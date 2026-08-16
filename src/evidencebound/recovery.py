"""Pure selective recovery planning."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any

from .graph import DependencyGraph
from .models import ActionDecision, InvalidationReason, VerificationResult


@dataclass(frozen=True, slots=True)
class RecoveryPlan:
    invalidated: tuple[str, ...]
    recompute: tuple[str, ...]
    reusable: tuple[str, ...]
    blocked: tuple[str, ...]
    reasons: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def plan_recovery(
    graph: DependencyGraph,
    invalidations: Mapping[str, InvalidationReason],
    *,
    verification: Mapping[str, VerificationResult] | None = None,
    consequential: set[str] | None = None,
) -> RecoveryPlan:
    if not invalidations:
        return RecoveryPlan((), (), graph.topological_order(), (), {})
    affected = graph.blast_radius(invalidations)
    affected_set = set(affected)
    reusable = tuple(node for node in graph.topological_order() if node not in affected_set)
    reasons: dict[str, str] = {}
    for node in affected:
        if node in invalidations:
            reasons[node] = invalidations[node].value
        else:
            roots = [root for root in invalidations if node in graph.descendants(root)]
            reasons[node] = "depends_on_invalidated:" + ",".join(sorted(roots))

    consequential = consequential or set()
    blocked: list[str] = []
    for node in graph.topological_order():
        if node not in consequential:
            continue
        if node in affected_set:
            blocked.append(node)
            continue
        if verification is None or node not in verification:
            blocked.append(node)
            continue
        if verification[node].action is not ActionDecision.ALLOW:
            blocked.append(node)
    return RecoveryPlan(affected, affected, reusable, tuple(blocked), reasons)


def action_after_recovery(
    checkpoint_id: str,
    plan: RecoveryPlan,
    *,
    reverified: Mapping[str, VerificationResult],
) -> ActionDecision:
    """Fail closed until affected consequential work has been re-verified successfully."""
    if checkpoint_id not in plan.blocked:
        result = reverified.get(checkpoint_id)
        return result.action if result is not None else ActionDecision.BLOCK
    result = reverified.get(checkpoint_id)
    if result is None or result.action is not ActionDecision.ALLOW:
        return ActionDecision.BLOCK
    return ActionDecision.ALLOW
