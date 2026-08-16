"""Deterministic integrity, evidence, policy, and applicability verification."""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone

from .canonical import CANONICALIZATION_VERSION, digest
from .models import (
    ActionDecision,
    ApplicabilityStatus,
    Checkpoint,
    EvidenceAssessment,
    EvidenceRecord,
    EvidenceState,
    IntegrityStatus,
    PolicyBinding,
    ProofReceipt,
    VerificationResult,
)


def _parse_time(value: str | None) -> datetime | None:
    if value is None:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def evidence_digest(record: EvidenceRecord) -> str | None:
    if record.payload is None:
        return None
    return digest(record.payload, domain="evidence")


def assess_evidence(
    snapshot: EvidenceRecord,
    current: EvidenceRecord | None,
    *,
    now: datetime | None,
) -> EvidenceAssessment:
    snapshot_hash = evidence_digest(snapshot)
    if current is None or current.payload is None:
        return EvidenceAssessment(
            snapshot.evidence_id,
            EvidenceState.MISSING,
            snapshot_hash,
            None,
            "current evidence is missing",
        )
    current_hash = evidence_digest(current)
    valid_until = _parse_time(current.valid_until)
    if current.explicitly_refuted:
        state = EvidenceState.REFUTED
        reason = "current evidence explicitly refutes the snapshot"
    elif now is not None and valid_until is not None and valid_until < now:
        state = EvidenceState.STALE
        reason = "current evidence is past valid_until"
    elif current_hash == snapshot_hash:
        state = EvidenceState.UNCHANGED
        reason = "current evidence matches the protected snapshot"
    else:
        state = EvidenceState.CHANGED
        reason = "current evidence digest differs from the protected snapshot"
    return EvidenceAssessment(snapshot.evidence_id, state, snapshot_hash, current_hash, reason)


def checkpoint_digest(checkpoint: Checkpoint) -> str:
    return digest(checkpoint.protected_payload(), domain="checkpoint")


def _verification_payload(
    checkpoint: Checkpoint,
    integrity: IntegrityStatus,
    applicability: ApplicabilityStatus,
    action: ActionDecision,
    provenance_complete: bool,
    policy_compatible: bool,
    evidence: tuple[EvidenceAssessment, ...],
    reasons: tuple[str, ...],
) -> dict[str, object]:
    return {
        "checkpoint_id": checkpoint.checkpoint_id,
        "checkpoint_digest": checkpoint_digest(checkpoint),
        "integrity": integrity.value,
        "applicability": applicability.value,
        "action": action.value,
        "provenance_complete": provenance_complete,
        "policy_compatible": policy_compatible,
        "evidence": [item.to_dict() for item in evidence],
        "reasons": list(reasons),
    }


def verify_checkpoint(
    checkpoint: Checkpoint,
    *,
    current_evidence: Mapping[str, EvidenceRecord] | None = None,
    expected_policy: PolicyBinding | None = None,
    prior_receipt: ProofReceipt | None = None,
    now: datetime | None = None,
) -> VerificationResult:
    if now is not None:
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")
        now = now.astimezone(timezone.utc)

    computed_checkpoint_digest = checkpoint_digest(checkpoint)
    integrity = IntegrityStatus.VERIFIED
    reasons: list[str] = []
    if prior_receipt is not None and prior_receipt.checkpoint_digest != computed_checkpoint_digest:
        integrity = IntegrityStatus.FAILED
        reasons.append("protected checkpoint payload does not match prior receipt")

    current = (
        {record.evidence_id: record for record in checkpoint.evidence}
        if current_evidence is None
        else current_evidence
    )
    if not checkpoint.evidence:
        provenance_complete = False
        reasons.append("checkpoint has no evidence")
    else:
        snapshot_provenance_complete = all(
            record.provenance is not None
            and bool(record.provenance.source)
            and bool(record.provenance.locator)
            for record in checkpoint.evidence
        )
        current_provenance_complete = bool(current) and all(
            record.provenance is not None
            and bool(record.provenance.source)
            and bool(record.provenance.locator)
            for record in current.values()
        )
        provenance_complete = snapshot_provenance_complete and current_provenance_complete
    if checkpoint.policy.require_provenance and not provenance_complete:
        reasons.append("required provenance is incomplete")

    policy_compatible = expected_policy is None or (
        checkpoint.policy.policy_id == expected_policy.policy_id
        and checkpoint.policy.version == expected_policy.version
    )
    if not policy_compatible:
        reasons.append("checkpoint policy binding does not match expected policy")

    assessments = tuple(
        assess_evidence(record, current.get(record.evidence_id), now=now)
        for record in checkpoint.evidence
    )
    states = {item.state for item in assessments}

    blocked_evidence = bool(states & {EvidenceState.MISSING, EvidenceState.REFUTED})
    review_evidence = bool(states & {EvidenceState.CHANGED, EvidenceState.STALE, EvidenceState.NEW})

    if integrity is IntegrityStatus.FAILED or blocked_evidence or (
        checkpoint.policy.require_provenance and not provenance_complete
    ):
        applicability = ApplicabilityStatus.BLOCKED
        action = ActionDecision.BLOCK
    elif not policy_compatible or review_evidence:
        applicability = ApplicabilityStatus.REVIEW_REQUIRED
        action = ActionDecision.REVIEW_REQUIRED
    else:
        applicability = ApplicabilityStatus.VERIFIED
        action = ActionDecision.ALLOW

    for assessment in assessments:
        if assessment.state is not EvidenceState.UNCHANGED:
            reasons.append(f"{assessment.evidence_id}: {assessment.state.value}")

    reason_tuple = tuple(sorted(set(reasons)))
    payload = _verification_payload(
        checkpoint,
        integrity,
        applicability,
        action,
        provenance_complete,
        policy_compatible,
        assessments,
        reason_tuple,
    )
    receipt = ProofReceipt(
        checkpoint_id=checkpoint.checkpoint_id,
        checkpoint_digest=computed_checkpoint_digest,
        verification_digest=digest(payload, domain="verification"),
        policy_id=checkpoint.policy.policy_id,
        policy_version=checkpoint.policy.version,
        canonicalization_version=CANONICALIZATION_VERSION,
    )
    return VerificationResult(
        checkpoint.checkpoint_id,
        integrity,
        applicability,
        action,
        provenance_complete,
        policy_compatible,
        assessments,
        reason_tuple,
        receipt,
    )


def verify_receipt(receipt: ProofReceipt, checkpoint: Checkpoint) -> bool:
    """Verify the receipt-to-checkpoint integrity binding; not source authenticity."""
    return (
        receipt.checkpoint_id == checkpoint.checkpoint_id
        and receipt.checkpoint_digest == checkpoint_digest(checkpoint)
        and receipt.canonicalization_version == CANONICALIZATION_VERSION
    )
