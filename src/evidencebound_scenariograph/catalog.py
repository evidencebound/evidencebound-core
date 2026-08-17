"""Small versioned validation catalog and deterministic matching baseline."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .model import ScenarioGraph


@dataclass(frozen=True)
class CatalogScenario:
    catalog_id: str
    functional_label: str
    expected_location: str | None = None
    obstruction_required: bool = False


@dataclass(frozen=True)
class CatalogMatch:
    catalog_id: str
    score_milli: int
    reasons: tuple[str, ...]


DEFAULT_CATALOG = (
    CatalogScenario(
        catalog_id="pedestrian_nearside_obstruction_intersection",
        functional_label="pedestrian_dart_out_visual_obstruction",
        expected_location="Intersection-Related",
        obstruction_required=True,
    ),
    CatalogScenario(
        catalog_id="pedestrian_midblock_crossing_nonturning",
        functional_label="pedestrian_crossing_vehicle_not_turning",
        expected_location="Not at Intersection",
    ),
    CatalogScenario(
        catalog_id="pedestrian_crossing_turning_vehicle",
        functional_label="pedestrian_crossing_vehicle_turning",
        expected_location="Intersection-Related",
    ),
)


def _value(graph: ScenarioGraph, field_id: str) -> Any:
    item = graph.fields.get(field_id)
    return None if item is None else item.value


def match_catalog(
    graph: ScenarioGraph,
    catalog: tuple[CatalogScenario, ...] = DEFAULT_CATALOG,
) -> tuple[CatalogMatch, ...]:
    """Rank catalog scenarios with an inspectable integer score, not opaque confidence."""

    functional_label = _value(graph, "functional_label")
    crash_location = _value(graph, "crash_location")
    obstruction = _value(graph, "obstruction_context")
    matches: list[CatalogMatch] = []

    for candidate in catalog:
        score = 0
        reasons: list[str] = []
        if functional_label == candidate.functional_label:
            score += 700
            reasons.append("functional_label_exact")
        if (
            candidate.expected_location is not None
            and crash_location == candidate.expected_location
        ):
            score += 180
            reasons.append("location_exact")
        if candidate.obstruction_required and obstruction is not None:
            score += 120
            reasons.append("obstruction_evidence_present")
        elif not candidate.obstruction_required:
            score += 60
            reasons.append("no_obstruction_requirement")

        matches.append(
            CatalogMatch(
                catalog_id=candidate.catalog_id,
                score_milli=min(score, 1000),
                reasons=tuple(reasons),
            )
        )

    return tuple(sorted(matches, key=lambda item: (-item.score_milli, item.catalog_id)))
