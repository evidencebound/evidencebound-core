"""End-to-end EvidenceBound ScenarioGraph SPARK pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from evidencebound import digest

from .catalog import CatalogMatch, match_catalog
from .enrichment import enrich_logical_scenario
from .export import OpenScenarioArtifact, export_openscenario_14
from .fixture import CrashFixture
from .functional import (
    DeterministicCodedRecordExtractor,
    FunctionalScenarioExtractor,
)
from .model import ScenarioField, ScenarioGraph


@dataclass(frozen=True)
class PipelineResult:
    fixture: CrashFixture
    graph: ScenarioGraph
    functional_label: str
    extractor_id: str
    matches: tuple[CatalogMatch, ...]
    openscenario: OpenScenarioArtifact
    receipt: dict[str, Any]


def run_pipeline(
    fixture: CrashFixture,
    *,
    extractor: FunctionalScenarioExtractor | None = None,
) -> PipelineResult:
    """Run the full evidence → scenario → match → export → receipt path."""

    selected_extractor = extractor or DeterministicCodedRecordExtractor()
    functional = selected_extractor.extract(fixture)
    graph = ScenarioGraph()
    for item in fixture.evidence:
        graph.add_evidence(fixture.source_item(item.evidence_id))
    for item in functional.fields:
        graph.add_field(item)
    for item in enrich_logical_scenario(fixture):
        graph.add_field(item)

    matches = match_catalog(graph)
    top_match = matches[0] if matches else None
    graph.add_field(
        ScenarioField(
            "catalog_match_top1",
            None if top_match is None else top_match.catalog_id,
            uncertainty_milli=1000 if top_match is None else 120,
            depends_on_fields=(
                "functional_label",
                "crash_location",
                "obstruction_context",
            ),
        )
    )
    openscenario = export_openscenario_14(graph, case_id=fixture.case_id)
    graph_receipt = graph.receipt()
    body: dict[str, Any] = {
        "schema": "evidencebound-scenariograph-pipeline-receipt/0.2",
        "case_id": fixture.case_id,
        "source_uri": fixture.source_uri,
        "privacy": fixture.privacy,
        "extractor_id": functional.extractor_id,
        "functional_label": functional.label,
        "graph_receipt_sha256": graph_receipt["sha256"],
        "matches": [
            {
                "catalog_id": item.catalog_id,
                "score_milli": item.score_milli,
                "reasons": list(item.reasons),
            }
            for item in matches
        ],
        "openscenario": {
            "standard": openscenario.standard,
            "conformance": openscenario.conformance,
            "xml": openscenario.xml,
        },
    }
    receipt = {
        "body": body,
        "sha256": digest(body, domain="ai-boost-challenge4-pipeline-receipt"),
    }
    return PipelineResult(
        fixture=fixture,
        graph=graph,
        functional_label=functional.label,
        extractor_id=functional.extractor_id,
        matches=matches,
        openscenario=openscenario,
        receipt=receipt,
    )
