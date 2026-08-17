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


@dataclass(frozen=True)
class CrashFixture:
    case_id: str
    dataset: str
    source_uri: str
    privacy: str
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
        content_sha256 = hashlib.sha256(canonical_bytes(item.payload)).hexdigest()
        return EvidenceItem(
            evidence_id=item.evidence_id,
            source_uri=f"{self.source_uri}#{item.evidence_id}",
            content_sha256=content_sha256,
            kind=item.kind,
        )

    def without_evidence(self, evidence_id: str) -> CrashFixture:
        """Return a controlled missing-evidence mutation."""

        return CrashFixture(
            case_id=f"{self.case_id}--without-{evidence_id}",
            dataset=self.dataset,
            source_uri=self.source_uri,
            privacy=self.privacy,
            evidence=tuple(item for item in self.evidence if item.evidence_id != evidence_id),
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
        evidence=evidence,
        expected_functional_label=str(expected["functional_label"]),
        expected_catalog_id=str(expected["catalog_id"]),
    )
