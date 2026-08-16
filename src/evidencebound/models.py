"""Public typed contracts for EvidenceBound."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

JsonValue = None | bool | int | str | list["JsonValue"] | dict[str, "JsonValue"]


class EvidenceState(str, Enum):
    UNCHANGED = "UNCHANGED"
    NEW = "NEW"
    CHANGED = "CHANGED"
    STALE = "STALE"
    MISSING = "MISSING"
    REFUTED = "REFUTED"


class IntegrityStatus(str, Enum):
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    UNVERIFIED = "UNVERIFIED"


class ApplicabilityStatus(str, Enum):
    VERIFIED = "VERIFIED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


class ActionDecision(str, Enum):
    ALLOW = "ALLOW"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"


class InvalidationReason(str, Enum):
    EVIDENCE_CHANGED = "evidence_changed"
    EVIDENCE_STALE = "evidence_stale"
    EVIDENCE_MISSING = "evidence_missing"
    EVIDENCE_REFUTED = "evidence_refuted"
    POLICY_CHANGED = "policy_changed"
    PROVENANCE_FAILED = "provenance_failed"
    INTEGRITY_FAILED = "integrity_failed"
    WORKER_FAILED = "worker_failed"
    EXPLICIT_MANUAL_INVALIDATION = "explicit_manual_invalidation"


@dataclass(frozen=True, slots=True)
class ProvenanceRecord:
    source: str | None
    locator: str | None = None
    retrieved_at: str | None = None
    content_type: str | None = None
    metadata: dict[str, JsonValue] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    evidence_id: str
    payload: JsonValue | None
    provenance: ProvenanceRecord | None
    observed_at: str | None = None
    valid_until: str | None = None
    explicitly_refuted: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PolicyBinding:
    policy_id: str
    version: str
    require_provenance: bool = True
    consequential: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Checkpoint:
    checkpoint_id: str
    agent: str
    evidence: tuple[EvidenceRecord, ...]
    output: JsonValue
    policy: PolicyBinding
    depends_on: tuple[str, ...] = ()
    operation_id: str | None = None
    schema_version: str = "1"

    def protected_payload(self) -> dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "agent": self.agent,
            "evidence": [item.to_dict() for item in self.evidence],
            "output": self.output,
            "policy": self.policy.to_dict(),
            "depends_on": list(self.depends_on),
            "operation_id": self.operation_id,
            "schema_version": self.schema_version,
        }

    def to_dict(self) -> dict[str, Any]:
        return self.protected_payload()


@dataclass(frozen=True, slots=True)
class EvidenceAssessment:
    evidence_id: str
    state: EvidenceState
    snapshot_digest: str | None
    current_digest: str | None
    reason: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["state"] = self.state.value
        return data


@dataclass(frozen=True, slots=True)
class ProofReceipt:
    checkpoint_id: str
    checkpoint_digest: str
    verification_digest: str
    policy_id: str
    policy_version: str
    canonicalization_version: str
    receipt_version: str = "1"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class VerificationResult:
    checkpoint_id: str
    integrity: IntegrityStatus
    applicability: ApplicabilityStatus
    action: ActionDecision
    provenance_complete: bool
    policy_compatible: bool
    evidence: tuple[EvidenceAssessment, ...]
    reasons: tuple[str, ...]
    receipt: ProofReceipt

    def to_dict(self) -> dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "integrity": self.integrity.value,
            "applicability": self.applicability.value,
            "action": self.action.value,
            "provenance_complete": self.provenance_complete,
            "policy_compatible": self.policy_compatible,
            "evidence": [item.to_dict() for item in self.evidence],
            "reasons": list(self.reasons),
            "receipt": self.receipt.to_dict(),
        }
