from evidencebound import (
    ActionDecision,
    EvidenceBound,
    EvidenceRecord,
    PolicyBinding,
    ProvenanceRecord,
)
from evidencebound.adapters import run_guarded


def test_plain_adapter():
    eb = EvidenceBound(policy=PolicyBinding("p", "1"))
    evidence = [EvidenceRecord("e", {"x": 1}, ProvenanceRecord("s", "urn:s"))]
    run = run_guarded(eb, agent="worker", evidence=evidence, worker=lambda: {"answer": 42})
    assert run.value == {"answer": 42}
    assert run.verification.action is ActionDecision.ALLOW


def test_google_adk_callback_seam_matches_single_context_contract():
    from evidencebound.adapters.google_adk import (
        AdkCallbackAdapter,
        adk_consequential_action_allowed,
    )

    class FakeCallbackContext:
        def __init__(self):
            self.state = {"agent_output": {"answer": 7}}

    eb = EvidenceBound(policy=PolicyBinding("p", "1"))
    adapter = AdkCallbackAdapter(
        evidencebound=eb,
        evidence_factory=lambda _ctx: [
            EvidenceRecord("e", {"x": 1}, ProvenanceRecord("s", "urn:s"))
        ],
        output_factory=lambda ctx: ctx.state["agent_output"],
        agent_name="adk-worker",
    )
    context = FakeCallbackContext()
    assert not adk_consequential_action_allowed(context.state)
    assert adapter.after_agent(context) is None
    assert adapter.last_verification is not None
    assert adapter.last_verification.action is ActionDecision.ALLOW
    assert context.state["evidencebound.verification"]["action"] == "ALLOW"
    assert adk_consequential_action_allowed(context.state)


def test_google_adk_gate_blocks_missing_or_malformed_state():
    from evidencebound.adapters.google_adk import adk_consequential_action_allowed

    assert not adk_consequential_action_allowed(None)
    assert not adk_consequential_action_allowed({})
    assert not adk_consequential_action_allowed(
        {"evidencebound.verification": "not-a-result"}
    )
    assert not adk_consequential_action_allowed(
        {"evidencebound.verification": {"action": "REVIEW_REQUIRED"}}
    )
    assert not adk_consequential_action_allowed(
        {"evidencebound.verification": {"action": "BLOCK"}}
    )
