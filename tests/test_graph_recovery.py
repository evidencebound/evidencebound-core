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
    action_after_recovery,
    plan_recovery,
    verify_checkpoint,
)

P = PolicyBinding("p", "1")
E = (EvidenceRecord("e", {"v": 1}, ProvenanceRecord("s", "u")),)


def cp(name, deps=()) -> Checkpoint:
    return Checkpoint(name, "a", E, {"n": name}, P, tuple(deps))


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


def test_recovery_reusable_recompute_and_blocked():
    graph = DependencyGraph([cp("A"), cp("B", ["A"]), cp("C", ["B"]), cp("X", ["A"])])
    plan = plan_recovery(
        graph,
        {"B": InvalidationReason.EVIDENCE_CHANGED},
        consequential={"C"},
    )
    assert plan.invalidated == ("B", "C")
    assert plan.recompute == ("B", "C")
    assert plan.reusable == ("A", "X")
    assert plan.blocked == ("C",)


def test_consequential_action_blocked_until_reverification_succeeds():
    graph = DependencyGraph([cp("A"), cp("B", ["A"])])
    plan = plan_recovery(
        graph,
        {"A": InvalidationReason.EVIDENCE_CHANGED},
        consequential={"B"},
    )
    assert action_after_recovery("B", plan, reverified={}) is ActionDecision.BLOCK
    blocked_result = verify_checkpoint(cp("B", ["A"]), current_evidence={})
    assert (
        action_after_recovery("B", plan, reverified={"B": blocked_result})
        is ActionDecision.BLOCK
    )
    allowed_result = verify_checkpoint(cp("B", ["A"]))
    assert (
        action_after_recovery("B", plan, reverified={"B": allowed_result})
        is ActionDecision.ALLOW
    )
