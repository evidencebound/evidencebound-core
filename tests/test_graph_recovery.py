import pytest

from evidencebound import (
    ActionDecision,
    Checkpoint,
    DependencyGraph,
    EvidenceRecord,
    GraphError,
    InvalidationReason,
    PolicyBinding,
    ProvenanceRecord,
    VerificationResult,
    action_after_recovery,
    plan_recovery,
    verify_checkpoint,
)

P = PolicyBinding("p", "1")
E = (EvidenceRecord("e", {"v": 1}, ProvenanceRecord("s", "u")),)


def cp(name, deps=()) -> Checkpoint:
    return Checkpoint(name, "a", E, {"n": name}, P, tuple(deps))


def allowed(graph: DependencyGraph, *nodes: str) -> dict[str, VerificationResult]:
    return {node: verify_checkpoint(graph.get(node)) for node in nodes}


def test_exact_blast_radius_branch_case():
    graph = DependencyGraph(
        [cp("A"), cp("B", ["A"]), cp("C", ["B"]), cp("D", ["C"]), cp("X", ["A"])]
    )
    assert graph.blast_radius(["C"]) == ("C", "D")
    assert graph.ancestors("C") == ("A", "B")
    assert graph.descendants("A") == ("B", "C", "D", "X")


def test_diamond_and_deterministic_order():
    graph = DependencyGraph(
        [cp("A"), cp("B", ["A"]), cp("C", ["A"]), cp("D", ["B", "C"])]
    )
    assert graph.topological_order() == ("A", "B", "C", "D")
    assert graph.blast_radius(["B"]) == ("B", "D")


def test_cycle_missing_dependency_and_duplicate_rejected():
    with pytest.raises(GraphError):
        DependencyGraph([cp("A", ["B"]), cp("B", ["A"])])
    with pytest.raises(GraphError):
        DependencyGraph([cp("A", ["Z"])])
    with pytest.raises(GraphError):
        DependencyGraph([cp("A"), cp("A")])


def test_recovery_reusable_means_verified_and_unaffected():
    graph = DependencyGraph([cp("A"), cp("B", ["A"]), cp("C", ["B"]), cp("X", ["A"])])
    plan = plan_recovery(
        graph,
        {"B": InvalidationReason.EVIDENCE_CHANGED},
        verification=allowed(graph, "A", "X"),
        consequential={"C"},
    )
    assert plan.invalidated == ("B", "C")
    assert plan.recompute == ("B", "C")
    assert plan.reusable == ("A", "X")
    assert plan.requires_verification == ()
    assert plan.blocked == ("C",)


def test_unverified_unaffected_state_is_not_reusable():
    graph = DependencyGraph([cp("A"), cp("B", ["A"]), cp("C", ["B"]), cp("X", ["A"])])
    plan = plan_recovery(
        graph,
        {"B": InvalidationReason.EVIDENCE_CHANGED},
    )
    assert plan.reusable == ()
    assert plan.requires_verification == ("A", "X")
    assert plan.recompute == ("B", "C")


def test_mismatched_allow_result_cannot_make_graph_checkpoint_reusable():
    graph = DependencyGraph([cp("A"), cp("B", ["A"])])
    forged_same_id = Checkpoint("A", "a", E, {"n": "different"}, P)
    forged_result = verify_checkpoint(forged_same_id)
    plan = plan_recovery(
        graph,
        {"B": InvalidationReason.WORKER_FAILED},
        verification={"A": forged_result},
    )
    assert plan.reusable == ()
    assert plan.requires_verification == ("A",)
    assert plan.reasons["A"] == "verification_binding_invalid"


def test_consequential_action_blocked_until_path_reverification_succeeds():
    graph = DependencyGraph([cp("A"), cp("B", ["A"])])
    plan = plan_recovery(
        graph,
        {"A": InvalidationReason.EVIDENCE_CHANGED},
        consequential={"B"},
    )
    assert plan.reverification_requirements["B"] == ("A", "B")
    assert action_after_recovery("B", plan, reverified={}) is ActionDecision.BLOCK
    allowed_a = verify_checkpoint(graph.get("A"))
    allowed_b = verify_checkpoint(graph.get("B"))
    assert (
        action_after_recovery("B", plan, reverified={"B": allowed_b})
        is ActionDecision.BLOCK
    )
    wrong_id = verify_checkpoint(cp("wrong"))
    assert (
        action_after_recovery(
            "B",
            plan,
            reverified={"A": allowed_a, "B": wrong_id},
        )
        is ActionDecision.BLOCK
    )
    assert (
        action_after_recovery(
            "B",
            plan,
            reverified={"A": allowed_a, "B": allowed_b},
        )
        is ActionDecision.ALLOW
    )


def test_unrelated_invalidation_does_not_block_verified_other_branch():
    graph = DependencyGraph([cp("A"), cp("B", ["A"]), cp("X"), cp("Y", ["X"])])
    plan = plan_recovery(
        graph,
        {"A": InvalidationReason.WORKER_FAILED},
        verification=allowed(graph, "X"),
        consequential={"Y"},
    )
    assert plan.recompute == ("A", "B")
    assert plan.reusable == ("X",)
    assert plan.requires_verification == ("Y",)
    assert plan.reverification_requirements["Y"] == ("Y",)
    allowed_y = verify_checkpoint(graph.get("Y"))
    assert action_after_recovery("Y", plan, reverified={"Y": allowed_y}) is ActionDecision.ALLOW
