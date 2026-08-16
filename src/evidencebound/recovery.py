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
    requires_verification: tuple[str, ...]
    blocked: tuple[str, ...]
    reasons: dict[str, str]
    reverification_requirements: dict[str, tuple[str, ...]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _is_allowed(
    verification: Mapping[str, VerificationResult] | None,
    checkpoint_id: str,
) -> bool:
    if verification is None:
        return False
    result = verification.get(checkpoint_id)
    return result is not None and result.action is ActionDecision.ALLOW


def plan_recovery(
    graph: DependencyGraph,
    invalidations: Mapping[str, InvalidationReason],
    *,
    verification: Mapping[str, VerificationResult] | None = None,
    consequential: set[str] | None = None,
) -> RecoveryPlan:
    """Return a deterministic fail-closed recovery plan.

    ``reusable`` means both unaffected by the invalidation blast radius and
    backed by a supplied ``ALLOW`` verification result. Unaffected checkpoints
    without such a result are separated into ``requires_verification`` rather
    than being silently promoted to reusable state.
    """
    order = graph.topological_order()
    affected = graph.blast_radius(invalidations) if invalidations else ()
    affected_set = set(affected)
    unaffected = tuple(node for node in order if node not in affected_set)

    reusable = tuple(node for node in unaffected if _is_allowed(verification, node))
    reusable_set = set(reusable)
    requires_verification = tuple(node for node in unaffected if node not in reusable_set)
    non_reusable = affected_set | set(requires_verification)

    reasons: dict[str, str] = {}
    for node in affected:
        if node in invalidations:
            reasons[node] = invalidations[node].value
        else:
            roots = [root for root in invalidations if node in graph.descendants(root)]
            reasons[node] = "depends_on_invalidated:" + ",".join(sorted(roots))

    for node in requires_verification:
        if verification is None or node not in verification:
            reasons[node] = "verification_missing"
        else:
            reasons[node] = f"verification_{verification[node].action.value.lower()}"

    reverification_requirements: dict[str, tuple[str, ...]] = {}
    for node in order:
        if node not in non_reusable:
            continue
        required = set(graph.ancestors(node)) | {node}
        reverification_requirements[node] = tuple(
            candidate for candidate in order if candidate in required and candidate in non_reusable
        )

    consequential = consequential or set()
    blocked = tuple(node for node in order if node in consequential and node not in reusable_set)

    return RecoveryPlan(
        invalidated=affected,
        recompute=affected,
        reusable=reusable,
        requires_verification=requires_verification,
        blocked=blocked,
        reasons=reasons,
        reverification_requirements=reverification_requirements,
    )


def action_after_recovery(
    checkpoint_id: str,
    plan: RecoveryPlan,
    *,
    reverified: Mapping[str, VerificationResult],
) -> ActionDecision:
    """Allow only trusted reusable state or successfully re-verified prerequisites."""
    if checkpoint_id in plan.reusable:
        return ActionDecision.ALLOW

    required = plan.reverification_requirements.get(checkpoint_id)
    if required is None:
        return ActionDecision.BLOCK

    for required_id in required:
        result = reverified.get(required_id)
        if result is None or result.action is not ActionDecision.ALLOW:
            return ActionDecision.BLOCK
    return ActionDecision.ALLOW
