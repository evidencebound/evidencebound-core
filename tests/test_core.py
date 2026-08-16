import json
from dataclasses import replace
from datetime import datetime, timezone

import pytest

from evidencebound import (
    ActionDecision,
    ApplicabilityStatus,
    CanonicalizationError,
    Checkpoint,
    EvidenceBound,
    EvidenceRecord,
    EvidenceState,
    IntegrityStatus,
    PolicyBinding,
    ProvenanceRecord,
    canonical_bytes,
    verify_checkpoint,
    verify_receipt,
    verify_verification_receipt,
)


def prov() -> ProvenanceRecord:
    return ProvenanceRecord("source", "urn:test")


def ev(value=1, **kwargs) -> EvidenceRecord:
    return EvidenceRecord("e1", {"value": value}, prov(), **kwargs)


def policy(version="1") -> PolicyBinding:
    return PolicyBinding("p", version)


def test_canonicalization_is_deterministic_and_rejects_float():
    left = canonical_bytes({"b": 2, "a": [1, "x"]})
    right = canonical_bytes({"a": [1, "x"], "b": 2})
    assert left == right
    with pytest.raises(CanonicalizationError):
        canonical_bytes({"x": 1.1})


def test_serialization_round_trip_is_json_safe():
    eb = EvidenceBound(policy=policy())
    cp = eb.checkpoint(agent="a", evidence=[ev()], output={"ok": True}, checkpoint_id="cp")
    assert json.loads(json.dumps(cp.to_dict()))["checkpoint_id"] == "cp"
    assert json.loads(json.dumps(eb.verify(cp).to_dict()))["action"] == "ALLOW"


def test_tamper_fails_closed():
    eb = EvidenceBound(policy=policy())
    cp = eb.checkpoint(agent="a", evidence=[ev()], output={"ok": True}, checkpoint_id="cp")
    original = eb.verify(cp)
    tampered = replace(cp, output={"ok": False})
    result = eb.verify(tampered, prior_receipt=original.receipt)
    assert result.integrity is IntegrityStatus.FAILED
    assert result.action is ActionDecision.BLOCK
    assert not verify_receipt(original.receipt, tampered)


def test_receipt_metadata_and_verification_result_are_bound():
    cp = Checkpoint("cp", "a", (ev(),), {"ok": True}, policy())
    result = verify_checkpoint(cp)
    assert verify_receipt(result.receipt, cp)
    assert verify_verification_receipt(result, cp)

    wrong_policy = replace(result.receipt, policy_version="2")
    assert not verify_receipt(wrong_policy, cp)

    wrong_receipt_version = replace(result.receipt, receipt_version="2")
    assert not verify_receipt(wrong_receipt_version, cp)

    changed_result = replace(result, action=ActionDecision.BLOCK)
    assert not verify_verification_receipt(changed_result, cp)

    changed_digest = replace(result.receipt, verification_digest="0" * 64)
    assert not verify_verification_receipt(replace(result, receipt=changed_digest), cp)


def test_historical_integrity_can_coexist_with_review_required():
    eb = EvidenceBound(policy=policy())
    cp = eb.checkpoint(agent="a", evidence=[ev()], output={"ok": True}, checkpoint_id="cp")
    original = eb.verify(cp)
    current = ev(2)
    result = eb.verify(cp, current_evidence={"e1": current}, prior_receipt=original.receipt)
    assert result.integrity is IntegrityStatus.VERIFIED
    assert result.applicability is ApplicabilityStatus.REVIEW_REQUIRED
    assert result.evidence[0].state is EvidenceState.CHANGED
    assert result.evidence[0].state is not EvidenceState.REFUTED


def test_missing_provenance_and_missing_evidence_fail_closed():
    missing_prov = EvidenceRecord("e1", {"v": 1}, None)
    cp = Checkpoint("cp", "a", (missing_prov,), {"ok": True}, policy())
    assert verify_checkpoint(cp).action is ActionDecision.BLOCK
    cp2 = Checkpoint("cp2", "a", (ev(),), {"ok": True}, policy())
    assert verify_checkpoint(cp2).action is ActionDecision.ALLOW
    assert verify_checkpoint(cp2, current_evidence={}).action is ActionDecision.BLOCK
    assert verify_checkpoint(cp2, current_evidence={"other": ev()}).action is ActionDecision.BLOCK


def test_current_evidence_mapping_key_must_match_record_identity():
    cp = Checkpoint("cp-identity", "a", (ev(),), {"ok": True}, policy())
    mismatched = EvidenceRecord("other", {"value": 1}, prov())
    result = verify_checkpoint(cp, current_evidence={"e1": mismatched})
    assert result.action is ActionDecision.BLOCK
    assert result.evidence[0].state is EvidenceState.MISSING
    assert "current evidence mapping key does not match record evidence_id" in result.reasons


def test_stale_and_refuted_semantics():
    cp = Checkpoint("cp", "a", (ev(),), {"ok": True}, policy())
    stale = EvidenceRecord(
        "e1",
        {"value": 1},
        prov(),
        valid_until="2026-01-01T00:00:00Z",
    )
    now = datetime(2026, 2, 1, tzinfo=timezone.utc)
    stale_result = verify_checkpoint(cp, current_evidence={"e1": stale}, now=now)
    assert stale_result.evidence[0].state is EvidenceState.STALE
    refuted = EvidenceRecord("e1", {"value": 2}, prov(), explicitly_refuted=True)
    refuted_result = verify_checkpoint(cp, current_evidence={"e1": refuted})
    assert refuted_result.evidence[0].state is EvidenceState.REFUTED


def test_policy_version_change_requires_review_not_history_rewrite():
    cp = Checkpoint("cp", "a", (ev(),), {"ok": True}, policy("1"))
    result = verify_checkpoint(cp, expected_policy=policy("2"))
    assert result.integrity is IntegrityStatus.VERIFIED
    assert result.applicability is ApplicabilityStatus.REVIEW_REQUIRED
    assert result.action is ActionDecision.REVIEW_REQUIRED


def test_empty_evidence_fails_closed():
    cp = Checkpoint("cp-empty", "a", (), {"ok": True}, policy())
    result = verify_checkpoint(cp)
    assert result.action is ActionDecision.BLOCK
    assert not result.provenance_complete


def test_new_current_evidence_requires_review():
    cp = Checkpoint("cp-new", "a", (ev(),), {"ok": True}, policy())
    extra = EvidenceRecord("e2", {"value": 2}, prov())
    result = verify_checkpoint(cp, current_evidence={"e1": ev(), "e2": extra})
    states = {item.evidence_id: item.state for item in result.evidence}
    assert states["e1"] is EvidenceState.UNCHANGED
    assert states["e2"] is EvidenceState.NEW
    assert result.action is ActionDecision.REVIEW_REQUIRED


def test_duplicate_evidence_ids_fail_closed_and_high_level_rejects():
    duplicate = (ev(1), ev(2))
    cp = Checkpoint("cp-duplicate", "a", duplicate, {"ok": True}, policy())
    assert verify_checkpoint(cp).action is ActionDecision.BLOCK

    eb = EvidenceBound(policy=policy())
    with pytest.raises(ValueError, match="duplicate evidence ids"):
        eb.checkpoint(agent="a", evidence=list(duplicate), output={"ok": True})
