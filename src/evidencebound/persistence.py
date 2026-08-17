"""Provider-neutral durable-state contracts for EvidenceBound."""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from .graph import DependencyGraph
from .models import Checkpoint, VerificationResult
from .replay import ReplayStatus

PERSISTENCE_SCHEMA_VERSION = "1"
PERSISTED_RECORD_VERSION = "1"


class PersistenceError(RuntimeError):
    """Base error for durable-state failures."""


class PersistenceIntegrityError(PersistenceError):
    """Persisted state is incomplete, malformed, or no longer integrity-bound."""


class UnsupportedPersistenceSchema(PersistenceError):
    """The durable store or a stored record uses an unsupported schema version."""


@runtime_checkable
class PersistenceStore(Protocol):
    """Minimal persistence boundary required by EvidenceBound recovery."""

    def commit_bundle(
        self,
        checkpoint: Checkpoint,
        verification: VerificationResult,
        *,
        operation_id: str | None = None,
        operation_payload: Any | None = None,
    ) -> ReplayStatus | None:
        """Atomically persist checkpoint, receipt, verification state and optional replay state."""
        ...

    def load_checkpoint(self, checkpoint_id: str) -> Checkpoint | None:
        """Load a checkpoint record without implying that it is trusted or reusable."""
        ...

    def load_verification(self, checkpoint_id: str) -> VerificationResult | None:
        """Load verification state only after re-checking its receipt/checkpoint binding."""
        ...

    def load_graph(self) -> DependencyGraph:
        """Reconstruct the dependency graph deterministically from persisted checkpoints."""
        ...

    def load_recovery_state(self) -> tuple[DependencyGraph, dict[str, VerificationResult]]:
        """Load a graph plus only verification state that still passes deterministic binding."""
        ...

    def apply_operation(self, operation_id: str, payload: Any) -> ReplayStatus:
        """Persist idempotency state so duplicate/conflict semantics survive restart."""
        ...
