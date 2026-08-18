"""Strict boundary for recorded/schema-constrained GenAI Functional Scenario candidates.

This module does not call a model provider. It defines the contract that any LLM/VLM
adapter must satisfy before a candidate enters ScenarioGraph trust evaluation. Invalid or
invented evidence references are preserved as candidate claims and are subsequently
blocked by the deterministic ScenarioGraph gate.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .fixture import CrashFixture
from .functional import FunctionalScenario
from .model import ScenarioField


class GenerativeCandidateError(ValueError):
    """Raised when a provider result violates the structural candidate contract."""


@dataclass(frozen=True)
class RecordedGenerativeExtractor:
    """Replay one retained LLM/VLM candidate through the deterministic trust boundary."""

    candidate: dict[str, Any]

    @property
    def extractor_id(self) -> str:
        provider = self._required_string("provider")
        model = self._required_string("model")
        prompt_version = self._required_string("prompt_version")
        return f"recorded-genai/{provider}/{model}/{prompt_version}"

    def _required_string(self, key: str) -> str:
        value = self.candidate.get(key)
        if not isinstance(value, str) or not value.strip():
            raise GenerativeCandidateError(f"{key} must be a non-empty string")
        return value

    def extract(self, fixture: CrashFixture) -> FunctionalScenario:
        source_case_id = self._required_string("source_case_id")
        if source_case_id != fixture.case_id:
            raise GenerativeCandidateError(
                f"candidate source_case_id {source_case_id!r} does not match {fixture.case_id!r}"
            )

        label = self._required_string("functional_label")
        raw_fields = self.candidate.get("fields")
        if not isinstance(raw_fields, list) or not raw_fields:
            raise GenerativeCandidateError("fields must be a non-empty list")

        fields: list[ScenarioField] = []
        seen: set[str] = set()
        for raw in raw_fields:
            if not isinstance(raw, dict):
                raise GenerativeCandidateError("each field must be an object")
            field_id = raw.get("field_id")
            if not isinstance(field_id, str) or not field_id:
                raise GenerativeCandidateError("field_id must be a non-empty string")
            if field_id in seen:
                raise GenerativeCandidateError(f"duplicate field_id: {field_id}")
            seen.add(field_id)

            raw_evidence_ids = raw.get("evidence_ids", [])
            if not isinstance(raw_evidence_ids, list) or not all(
                isinstance(item, str) for item in raw_evidence_ids
            ):
                raise GenerativeCandidateError(
                    f"evidence_ids for {field_id} must be a list of strings"
                )
            uncertainty = raw.get("uncertainty_milli", 1000)
            if not isinstance(uncertainty, int) or isinstance(uncertainty, bool):
                raise GenerativeCandidateError(
                    f"uncertainty_milli for {field_id} must be an integer"
                )
            fields.append(
                ScenarioField(
                    field_id=field_id,
                    value=raw.get("value"),
                    evidence_ids=tuple(raw_evidence_ids),
                    uncertainty_milli=uncertainty,
                    material=bool(raw.get("material", True)),
                )
            )

        if "functional_label" not in seen:
            fields.append(
                ScenarioField(
                    field_id="functional_label",
                    value=label,
                    evidence_ids=tuple(
                        str(item) for item in self.candidate.get("label_evidence_ids", [])
                    ),
                    uncertainty_milli=int(
                        self.candidate.get("label_uncertainty_milli", 1000)
                    ),
                )
            )

        return FunctionalScenario(
            label=label,
            fields=tuple(fields),
            extractor_id=self.extractor_id,
        )
