"""Sanitized public crash-fixture ingestion for ScenarioGraph."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from evidencebound import canonical_bytes

from .model import EvidenceItem


@dataclass(frozen=True)
class FixtureEvidence:
    evidence_id: str
    kind: str
    payload: dict[str, Any]

    @property
    def content_sha256(self) -> str:
        return hashlib.sha256(canonical_bytes(self.payload)).hexdigest()


@dataclass(frozen=True)
class CrashFixture:
    case_id: str
    dataset: str
    source_uri: str
    privacy: str
    excluded_data_categories: tuple[str, ...]
    evidence: tuple[FixtureEvidence, ...]
    expected_functional_label: str
    expected_catalog_id: str

    def evidence_by_id(self, evidence_id: str) -> FixtureEvidence | None:
        return next((item for item in self.evidence if item.evidence_id == evidence_id), None)

    def value(self, evidence_id: str, key: str) -> Any:
        item = self.evidence_by_id(evidence_id)
        if item is None:
            return None
        return item.payload.get(key)

    def source_item(self, evidence_id: str) -> EvidenceItem:
        item = self.evidence_by_id(evidence_id)
        if item is None:
            raise KeyError(evidence_id)
        return EvidenceItem(
            evidence_id=item.evidence_id,
            source_uri=f"{self.source_uri}#{item.evidence_id}",
            content_sha256=item.content_sha256,
            kind=item.kind,
        )

    def without_evidence(self, evidence_id: str) -> CrashFixture:
        """Return a controlled missing-evidence mutation."""

        return self._replace(
            case_id=f"{self.case_id}--without-{evidence_id}",
            evidence=tuple(item for item in self.evidence if item.evidence_id != evidence_id),
        )

    def with_value(self, evidence_id: str, key: str, value: Any, *, label: str) -> CrashFixture:
        """Return a controlled one-field mutation inside one evidence object."""

        found = False
        mutated: list[FixtureEvidence] = []
        for item in self.evidence:
            if item.evidence_id != evidence_id:
                mutated.append(item)
                continue
            if key not in item.payload:
                raise KeyError(f"{evidence_id}.{key}")
            payload = dict(item.payload)
            payload[key] = value
            mutated.append(
                FixtureEvidence(
                    evidence_id=item.evidence_id,
                    kind=item.kind,
                    payload=payload,
                )
            )
            found = True
        if not found:
            raise KeyError(evidence_id)
        return self._replace(
            case_id=f"{self.case_id}--mutation-{label}",
            evidence=tuple(mutated),
        )

    def changed_evidence_ids(self, other: CrashFixture) -> tuple[str, ...]:
        """Detect exact evidence blocks whose content changed, appeared or disappeared."""

        before = {item.evidence_id: item.content_sha256 for item in self.evidence}
        after = {item.evidence_id: item.content_sha256 for item in other.evidence}
        return tuple(
            sorted(
                evidence_id
                for evidence_id in set(before) | set(after)
                if before.get(evidence_id) != after.get(evidence_id)
            )
        )

    def _replace(
        self,
        *,
        case_id: str,
        evidence: tuple[FixtureEvidence, ...],
    ) -> CrashFixture:
        return CrashFixture(
            case_id=case_id,
            dataset=self.dataset,
            source_uri=self.source_uri,
            privacy=self.privacy,
            excluded_data_categories=self.excluded_data_categories,
            evidence=evidence,
            expected_functional_label=self.expected_functional_label,
            expected_catalog_id=self.expected_catalog_id,
        )


def load_fixture(path: str | Path) -> CrashFixture:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    evidence = tuple(
        FixtureEvidence(
            evidence_id=str(item["id"]),
            kind=str(item["kind"]),
            payload=dict(item["payload"]),
        )
        for item in raw["evidence"]
    )
    expected = raw["expected"]
    return CrashFixture(
        case_id=str(raw["case_id"]),
        dataset=str(raw["dataset"]),
        source_uri=str(raw["source_uri"]),
        privacy=str(raw["privacy"]),
        excluded_data_categories=tuple(
            str(item) for item in raw.get("excluded_data_categories", [])
        ),
        evidence=evidence,
        expected_functional_label=str(expected["functional_label"]),
        expected_catalog_id=str(expected["catalog_id"]),
    )
