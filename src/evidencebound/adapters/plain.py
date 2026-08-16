"""Thin framework-neutral hook adapter."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

from ..api import EvidenceBound
from ..models import Checkpoint, EvidenceRecord, VerificationResult

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class GuardedRun(Generic[T]):
    value: T
    checkpoint: Checkpoint
    verification: VerificationResult


def run_guarded(
    eb: EvidenceBound,
    *,
    agent: str,
    evidence: list[EvidenceRecord],
    worker: Callable[[], T],
    depends_on: tuple[str, ...] = (),
) -> GuardedRun[T]:
    value = worker()
    checkpoint = eb.checkpoint(
        agent=agent,
        evidence=evidence,
        output=value,  # type: ignore[arg-type]
        depends_on=depends_on,
    )
    verification = eb.verify(checkpoint)
    return GuardedRun(value, checkpoint, verification)
