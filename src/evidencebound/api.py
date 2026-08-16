"""High-level EvidenceBound facade."""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from .canonical import digest
from .events import Event, EventSink, NullEventSink
from .graph import DependencyGraph
from .models import (
    ActionDecision,
    Checkpoint,
    EvidenceRecord,
    InvalidationReason,
    PolicyBinding,
    ProofReceipt,
    VerificationResult,
)
from .recovery import RecoveryPlan, plan_recovery
from .verification import verify_checkpoint


class EvidenceBound:
    def __init__(self, *, policy: PolicyBinding, event_sink: EventSink | None = None) -> None:
        self.policy = policy
        self.events = event_sink or NullEventSink()
        self._checkpoints: dict[str, Checkpoint] = {}
        self._verification: dict[str, VerificationResult] = {}

    def checkpoint(
        self,
        *,
        agent: str,
        evidence: list[EvidenceRecord] | tuple[EvidenceRecord, ...],
        output: object,
        depends_on: list[str] | tuple[str, ...] = (),
        checkpoint_id: str | None = None,
        operation_id: str | None = None,
    ) -> Checkpoint:
        if checkpoint_id is None:
            checkpoint_id = digest(
                {
                    "agent": agent,
                    "evidence": [record.to_dict() for record in evidence],
                    "output": output,
                    "depends_on": list(depends_on),
                    "policy": self.policy.to_dict(),
                    "operation_id": operation_id,
                },
                domain="checkpoint-id",
            )[:24]
        if checkpoint_id in self._checkpoints:
            raise ValueError(f"duplicate checkpoint id: {checkpoint_id}")
        missing = sorted(set(depends_on) - set(self._checkpoints))
        if missing:
            raise ValueError(f"unknown dependencies: {missing}")
        checkpoint = Checkpoint(
            checkpoint_id,
            agent,
            tuple(evidence),
            output,  # type: ignore[arg-type]
            self.policy,
            tuple(depends_on),
            operation_id,
        )
        self._checkpoints[checkpoint_id] = checkpoint
        self.events.emit(
            Event("checkpoint_created", {"checkpoint_id": checkpoint_id, "agent": agent})
        )
        return checkpoint

    def verify(
        self,
        checkpoint: Checkpoint,
        *,
        current_evidence: Mapping[str, EvidenceRecord] | None = None,
        expected_policy: PolicyBinding | None = None,
        prior_receipt: ProofReceipt | None = None,
        now: datetime | None = None,
    ) -> VerificationResult:
        result = verify_checkpoint(
            checkpoint,
            current_evidence=current_evidence,
            expected_policy=expected_policy or self.policy,
            prior_receipt=prior_receipt,
            now=now,
        )
        self._verification[checkpoint.checkpoint_id] = result
        self.events.emit(Event("verification_completed", {
            "checkpoint_id": checkpoint.checkpoint_id,
            "action": result.action.value,
            "applicability": result.applicability.value,
        }))
        if result.integrity.value == "FAILED":
            self.events.emit(Event("integrity_failed", {"checkpoint_id": checkpoint.checkpoint_id}))
        if result.action is not ActionDecision.ALLOW:
            self.events.emit(Event("action_blocked", {
                "checkpoint_id": checkpoint.checkpoint_id,
                "decision": result.action.value,
            }))
        return result

    def graph(self) -> DependencyGraph:
        return DependencyGraph(self._checkpoints.values())

    def invalidate(
        self,
        *,
        checkpoint_id: str,
        reason: InvalidationReason,
        consequential: set[str] | None = None,
    ) -> RecoveryPlan:
        self.events.emit(Event("invalidation_started", {
            "checkpoint_id": checkpoint_id,
            "reason": reason.value,
        }))
        graph = self.graph()
        affected = graph.blast_radius([checkpoint_id])
        self.events.emit(Event("blast_radius_computed", {
            "checkpoint_id": checkpoint_id,
            "affected": list(affected),
        }))
        plan = plan_recovery(
            graph,
            {checkpoint_id: reason},
            verification=self._verification,
            consequential=consequential,
        )
        self.events.emit(Event("recovery_planned", {
            "recompute": list(plan.recompute),
            "reusable": list(plan.reusable),
            "blocked": list(plan.blocked),
        }))
        return plan
