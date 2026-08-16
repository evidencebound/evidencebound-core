from dataclasses import replace
from datetime import datetime, timezone
import pytest
from evidencebound import *

P = PolicyBinding("policy", "1")
PROV = ProvenanceRecord("trusted-adapter", "urn:source:1")

def record(evidence_id="e1", value=1, provenance=PROV, **kw):
    return EvidenceRecord(evidence_id, {"value": value}, provenance, **kw)


def test_provenance_deletion_blocks_current_applicability():
    cp = Checkpoint("c", "a", (record(),), {"ok": True}, P)
    prior = verify_checkpoint(cp)
    current = EvidenceRecord("e1", {"value": 1}, None)
    result = verify_checkpoint(cp, current_evidence={"e1": current}, prior_receipt=prior.receipt)
    assert result.integrity is IntegrityStatus.VERIFIED
    assert result.action is ActionDecision.BLOCK


def test_partial_current_state_loss_blocks():
    cp = Checkpoint("c", "a", (record("e1"), record("e2")), {"ok": True}, P)
    result = verify_checkpoint(cp, current_evidence={"e1": record("e1")})
    assert result.action is ActionDecision.BLOCK
    states = {x.evidence_id: x.state for x in result.evidence}
    assert states["e2"] is EvidenceState.MISSING


def test_output_only_tamper_is_detected():
    cp = Checkpoint("c", "a", (record(),), {"answer": 1}, P)
    receipt = verify_checkpoint(cp).receipt
    changed = replace(cp, output={"answer": 2})
    assert verify_checkpoint(changed, prior_receipt=receipt).action is ActionDecision.BLOCK


def test_policy_binding_tamper_is_detected_by_prior_receipt():
    cp = Checkpoint("c", "a", (record(),), {"answer": 1}, P)
    receipt = verify_checkpoint(cp).receipt
    changed = replace(cp, policy=PolicyBinding("policy", "2"))
    result = verify_checkpoint(changed, prior_receipt=receipt, expected_policy=P)
    assert result.integrity is IntegrityStatus.FAILED
    assert result.action is ActionDecision.BLOCK


def test_refutation_is_explicit_not_inferred_from_hash_change():
    cp = Checkpoint("c", "a", (record(),), {"answer": 1}, P)
    changed = record(value=99)
    result = verify_checkpoint(cp, current_evidence={"e1": changed})
    assert result.evidence[0].state is EvidenceState.CHANGED
    assert result.action is ActionDecision.REVIEW_REQUIRED
    refuted = record(value=99, explicitly_refuted=True)
    blocked = verify_checkpoint(cp, current_evidence={"e1": refuted})
    assert blocked.evidence[0].state is EvidenceState.REFUTED
    assert blocked.action is ActionDecision.BLOCK


def test_staleness_requires_explicit_time_input():
    cp = Checkpoint("c", "a", (record(),), {"answer": 1}, P)
    current = EvidenceRecord("e1", {"value": 1}, PROV, valid_until="2026-08-15T00:00:00Z")
    no_clock = verify_checkpoint(cp, current_evidence={"e1": current})
    assert no_clock.evidence[0].state is EvidenceState.UNCHANGED
    with_clock = verify_checkpoint(
        cp,
        current_evidence={"e1": current},
        now=datetime(2026, 8, 16, tzinfo=timezone.utc),
    )
    assert with_clock.evidence[0].state is EvidenceState.STALE
    assert with_clock.action is ActionDecision.REVIEW_REQUIRED


def test_naive_time_rejected():
    cp = Checkpoint("c", "a", (record(),), {"answer": 1}, P)
    with pytest.raises(ValueError):
        verify_checkpoint(cp, now=datetime(2026, 8, 16))


def test_replay_domain_is_deterministic_for_key_order():
    guard = ReplayGuard()
    assert guard.apply("x", {"a": 1, "b": 2}) is ReplayStatus.APPLIED
    assert guard.apply("x", {"b": 2, "a": 1}) is ReplayStatus.ALREADY_APPLIED
