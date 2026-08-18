"""Functional Scenario extraction with a deterministic benchmark baseline."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .fixture import CrashFixture
from .model import ScenarioField


@dataclass(frozen=True)
class FunctionalScenario:
    label: str
    fields: tuple[ScenarioField, ...]
    extractor_id: str


class FunctionalScenarioExtractor(Protocol):
    """Provider seam for schema-constrained LLM/VLM or deterministic extractors."""

    extractor_id: str

    def extract(self, fixture: CrashFixture) -> FunctionalScenario: ...


class DeterministicCodedRecordExtractor:
    """Reproducible comparator over already-coded public crash-record fields.

    This is intentionally not represented as a generative model. A future LLM/VLM
    extractor must produce the same evidence-linked contract before trust evaluation.
    """

    extractor_id = "coded-record-baseline/0.1"

    def extract(self, fixture: CrashFixture) -> FunctionalScenario:
        crash_type = fixture.value("crash_classification", "crash_type")
        crash_group = fixture.value("crash_classification", "crash_group")
        crash_location = fixture.value("crash_classification", "crash_location")

        if isinstance(crash_type, str) and "Dart-Out" in crash_type:
            label = "pedestrian_dart_out_visual_obstruction"
        elif isinstance(crash_group, str) and "Vehicle Not Turning" in crash_group:
            label = "pedestrian_crossing_vehicle_not_turning"
        else:
            label = "unclassified"

        maneuver = fixture.value("movement", "motorist_maneuver")
        if maneuver is None:
            maneuver = fixture.value("movement", "vehicle_pre_event_movement")

        obstruction = fixture.value("visibility", "pedestrian_vision_obscured")
        if obstruction is None:
            obstruction = fixture.value("visibility", "reported_obstruction")

        fields = (
            ScenarioField(
                "crash_type",
                crash_type,
                evidence_ids=("crash_classification",) if crash_type is not None else (),
                uncertainty_milli=0 if crash_type is not None else 1000,
            ),
            ScenarioField(
                "crash_group",
                crash_group,
                evidence_ids=("crash_classification",) if crash_group is not None else (),
                uncertainty_milli=0 if crash_group is not None else 1000,
            ),
            ScenarioField(
                "crash_location",
                crash_location,
                evidence_ids=("crash_classification",) if crash_location is not None else (),
                uncertainty_milli=0 if crash_location is not None else 1000,
            ),
            ScenarioField(
                "vehicle_maneuver",
                maneuver,
                evidence_ids=("movement",) if maneuver is not None else (),
                uncertainty_milli=80 if maneuver is not None else 1000,
            ),
            ScenarioField(
                "obstruction_context",
                obstruction,
                evidence_ids=("visibility",) if obstruction is not None else (),
                uncertainty_milli=120 if obstruction is not None else 1000,
            ),
            ScenarioField(
                "functional_label",
                label,
                evidence_ids=("crash_classification",),
                uncertainty_milli=40 if label != "unclassified" else 700,
                depends_on_fields=("crash_type", "crash_group"),
            ),
        )
        return FunctionalScenario(label=label, fields=fields, extractor_id=self.extractor_id)
