"""Evidence-bound ScenarioGraph model for AI-BOOST Challenge 4.

This package is challenge-specific foreground work. It depends on the pre-existing
EvidenceBound Core only for deterministic, domain-separated receipts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from evidencebound import digest


class FieldDecision(str, Enum):
    """Trust decision for one generated scenario field."""

    VERIFIED = "VERIFIED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class EvidenceItem:
    """A source-addressed crash/standards evidence item."""

    evidence_id: str
    source_uri: str
    content_sha256: str
    kind: str = "source"

    def __post_init__(self) -> None:
        if not self.evidence_id:
            raise ValueError("evidence_id must not be empty")
        if not self.source_uri:
            raise ValueError("source_uri must not be empty")
        if len(self.content_sha256) != 64:
            raise ValueError("content_sha256 must be a 64-character SHA-256 hex digest")
        try:
            int(self.content_sha256, 16)
        except ValueError as exc:
            raise ValueError("content_sha256 must be hexadecimal") from exc


@dataclass(frozen=True)
class ScenarioField:
    """A generated/derived scenario claim with explicit evidence bindings.

    ``uncertainty_milli`` is an integer in [0, 1000]. This keeps receipts inside
    EvidenceBound EBCJ-1's intentionally float-free deterministic domain.
    """

    field_id: str
    value: Any
    evidence_ids: tuple[str, ...] = ()
    uncertainty_milli: int = 0
    material: bool = True
    depends_on_fields: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.field_id:
            raise ValueError("field_id must not be empty")
        if not 0 <= self.uncertainty_milli <= 1000:
            raise ValueError("uncertainty_milli must be between 0 and 1000")


@dataclass(frozen=True)
class FieldAssessment:
    field_id: str
    decision: FieldDecision
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ScenarioRecoveryPlan:
    changed_evidence_ids: tuple[str, ...]
    preserve_fields: tuple[str, ...]
    recompute_fields: tuple[str, ...]


@dataclass
class ScenarioGraph:
    """Evidence-linked fields plus deterministic trust and recovery semantics."""

    evidence: dict[str, EvidenceItem] = field(default_factory=dict)
    fields: dict[str, ScenarioField] = field(default_factory=dict)
    review_threshold_milli: int = 350

    def __post_init__(self) -> None:
        if not 0 <= self.review_threshold_milli <= 1000:
            raise ValueError("review_threshold_milli must be between 0 and 1000")

    def add_evidence(self, item: EvidenceItem) -> None:
        if item.evidence_id in self.evidence:
            raise ValueError(f"duplicate evidence_id: {item.evidence_id}")
        self.evidence[item.evidence_id] = item

    def add_field(self, scenario_field: ScenarioField) -> None:
        if scenario_field.field_id in self.fields:
            raise ValueError(f"duplicate field_id: {scenario_field.field_id}")
        self.fields[scenario_field.field_id] = scenario_field

    def assess_field(self, field_id: str) -> FieldAssessment:
        return self._assess_field(field_id, active=())

    def _assess_field(self, field_id: str, *, active: tuple[str, ...]) -> FieldAssessment:
        if field_id in active:
            return FieldAssessment(
                field_id=field_id,
                decision=FieldDecision.BLOCKED,
                reasons=("dependency_cycle",),
            )

        scenario_field = self.fields[field_id]
        reasons: list[str] = []
        missing_evidence = sorted(
            evidence_id
            for evidence_id in scenario_field.evidence_ids
            if evidence_id not in self.evidence
        )
        missing_dependencies = sorted(
            dependency
            for dependency in scenario_field.depends_on_fields
            if dependency not in self.fields
        )

        if missing_dependencies:
            reasons.append("missing_field_dependencies=" + ",".join(missing_dependencies))
        if missing_evidence:
            reasons.append("missing_evidence=" + ",".join(missing_evidence))
        if (
            scenario_field.material
            and scenario_field.value is not None
            and not scenario_field.evidence_ids
            and not scenario_field.depends_on_fields
        ):
            reasons.append("material_claim_has_no_evidence")

        if reasons:
            return FieldAssessment(
                field_id=field_id,
                decision=FieldDecision.BLOCKED,
                reasons=tuple(reasons),
            )

        if scenario_field.value is None:
            return FieldAssessment(
                field_id=field_id,
                decision=FieldDecision.REVIEW_REQUIRED,
                reasons=("value_unknown",),
            )

        if scenario_field.uncertainty_milli >= self.review_threshold_milli:
            return FieldAssessment(
                field_id=field_id,
                decision=FieldDecision.REVIEW_REQUIRED,
                reasons=(f"uncertainty_milli={scenario_field.uncertainty_milli}",),
            )

        dependency_assessments = [
            self._assess_field(dependency, active=(*active, field_id))
            for dependency in scenario_field.depends_on_fields
        ]
        if any(item.decision is FieldDecision.BLOCKED for item in dependency_assessments):
            return FieldAssessment(
                field_id=field_id,
                decision=FieldDecision.BLOCKED,
                reasons=("blocked_dependency",),
            )
        if any(
            item.decision is FieldDecision.REVIEW_REQUIRED
            for item in dependency_assessments
        ):
            return FieldAssessment(
                field_id=field_id,
                decision=FieldDecision.REVIEW_REQUIRED,
                reasons=("dependency_requires_review",),
            )

        return FieldAssessment(
            field_id=field_id,
            decision=FieldDecision.VERIFIED,
            reasons=("evidence_bound_or_derived",),
        )

    def assessments(self) -> dict[str, FieldAssessment]:
        return {field_id: self.assess_field(field_id) for field_id in sorted(self.fields)}

    def affected_fields(self, changed_evidence_ids: set[str]) -> tuple[str, ...]:
        """Return the exact transitive field blast radius for changed evidence."""

        affected = {
            field_id
            for field_id, scenario_field in self.fields.items()
            if changed_evidence_ids.intersection(scenario_field.evidence_ids)
        }
        changed = True
        while changed:
            changed = False
            for field_id, scenario_field in self.fields.items():
                if field_id in affected:
                    continue
                if affected.intersection(scenario_field.depends_on_fields):
                    affected.add(field_id)
                    changed = True
        return tuple(sorted(affected))

    def plan_recovery(self, changed_evidence_ids: set[str]) -> ScenarioRecoveryPlan:
        """Preserve unaffected fields and recompute only the transitive blast radius."""

        recompute = self.affected_fields(changed_evidence_ids)
        recompute_set = set(recompute)
        preserve = tuple(sorted(set(self.fields) - recompute_set))
        return ScenarioRecoveryPlan(
            changed_evidence_ids=tuple(sorted(changed_evidence_ids)),
            preserve_fields=preserve,
            recompute_fields=recompute,
        )

    def receipt(self, *, changed_evidence_ids: set[str] | None = None) -> dict[str, Any]:
        """Return a deterministic, content-addressed verification receipt."""

        changed = changed_evidence_ids or set()
        assessments = self.assessments()
        recovery = self.plan_recovery(changed)
        body: dict[str, Any] = {
            "schema": "evidencebound-scenariograph-receipt/0.2",
            "review_threshold_milli": self.review_threshold_milli,
            "evidence": [
                {
                    "evidence_id": item.evidence_id,
                    "source_uri": item.source_uri,
                    "content_sha256": item.content_sha256,
                    "kind": item.kind,
                }
                for item in sorted(self.evidence.values(), key=lambda item: item.evidence_id)
            ],
            "fields": [
                {
                    "field_id": item.field_id,
                    "value": item.value,
                    "evidence_ids": list(item.evidence_ids),
                    "uncertainty_milli": item.uncertainty_milli,
                    "material": item.material,
                    "depends_on_fields": list(item.depends_on_fields),
                    "decision": assessments[item.field_id].decision.value,
                    "reasons": list(assessments[item.field_id].reasons),
                }
                for item in sorted(self.fields.values(), key=lambda item: item.field_id)
            ],
            "recovery": {
                "changed_evidence_ids": list(recovery.changed_evidence_ids),
                "preserve_fields": list(recovery.preserve_fields),
                "recompute_fields": list(recovery.recompute_fields),
            },
        }
        return {
            "body": body,
            "sha256": digest(body, domain="ai-boost-challenge4-scenario-receipt"),
        }
