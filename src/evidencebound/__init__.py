"""EvidenceBound public API."""
from .api import EvidenceBound
from .canonical import CANONICALIZATION_VERSION, CanonicalizationError, canonical_bytes, digest
from .events import Event, EventSink, ListEventSink, NullEventSink
from .graph import DependencyGraph, GraphError
from .models import (
    ActionDecision,
    ApplicabilityStatus,
    Checkpoint,
    EvidenceAssessment,
    EvidenceRecord,
    EvidenceState,
    IntegrityStatus,
    InvalidationReason,
    PolicyBinding,
    ProofReceipt,
    ProvenanceRecord,
    VerificationResult,
)
from .recovery import RecoveryPlan, action_after_recovery, plan_recovery
from .replay import ReplayConflict, ReplayGuard, ReplayStatus
from .verification import checkpoint_digest, evidence_digest, verify_checkpoint, verify_receipt

__version__ = "0.3.0"

__all__ = [
    "ActionDecision", "ApplicabilityStatus", "CANONICALIZATION_VERSION", "CanonicalizationError",
    "Checkpoint", "DependencyGraph", "EvidenceAssessment", "EvidenceBound", "EvidenceRecord",
    "EvidenceState", "Event", "EventSink", "GraphError", "IntegrityStatus", "InvalidationReason",
    "ListEventSink", "NullEventSink", "PolicyBinding", "ProofReceipt", "ProvenanceRecord",
    "RecoveryPlan", "ReplayConflict", "ReplayGuard", "ReplayStatus", "VerificationResult",
    "canonical_bytes", "checkpoint_digest", "digest", "evidence_digest", "plan_recovery",
    "verify_checkpoint", "verify_receipt", "action_after_recovery",
]
