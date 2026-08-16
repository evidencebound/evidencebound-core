"""In-memory idempotency guard primitives; no exactly-once claim."""
from __future__ import annotations

from enum import Enum
from typing import Any

from .canonical import digest


class ReplayStatus(str, Enum):
    APPLIED = "APPLIED"
    ALREADY_APPLIED = "ALREADY_APPLIED"


class ReplayConflict(ValueError):
    pass


class ReplayGuard:
    def __init__(self) -> None:
        self._operations: dict[str, str] = {}

    def apply(self, operation_id: str, payload: Any) -> ReplayStatus:
        payload_digest = digest(payload, domain="operation")
        previous = self._operations.get(operation_id)
        if previous is None:
            self._operations[operation_id] = payload_digest
            return ReplayStatus.APPLIED
        if previous == payload_digest:
            return ReplayStatus.ALREADY_APPLIED
        raise ReplayConflict(f"operation id {operation_id!r} was reused with a different payload")
