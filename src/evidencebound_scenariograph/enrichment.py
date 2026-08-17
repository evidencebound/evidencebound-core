"""Evidence-linked Logical Scenario enrichment."""
from __future__ import annotations

from .fixture import CrashFixture
from .model import ScenarioField


def _field(
    fixture: CrashFixture,
    field_id: str,
    evidence_id: str,
    key: str,
    *,
    uncertainty_milli: int = 80,
) -> ScenarioField:
    value = fixture.value(evidence_id, key)
    return ScenarioField(
        field_id,
        value,
        evidence_ids=(evidence_id,) if value is not None else (),
        uncertainty_milli=uncertainty_milli if value is not None else 1000,
    )


def enrich_logical_scenario(fixture: CrashFixture) -> tuple[ScenarioField, ...]:
    """Return explicit Logical Scenario attributes; missing values remain unknown."""

    speed = fixture.value("kinematics", "pre_event_speed_kph")
    if speed is None:
        speed = fixture.value("kinematics", "vehicle_speed_kph")
    speed_field = ScenarioField(
        "vehicle_speed_kph",
        speed,
        evidence_ids=("kinematics",) if speed is not None else (),
        uncertainty_milli=100 if speed is not None else 1000,
    )

    return (
        _field(fixture, "light_condition", "environment", "light"),
        _field(fixture, "atmospheric_condition", "environment", "atmospheric"),
        _field(fixture, "roadway_alignment", "roadway", "roadway_alignment"),
        _field(fixture, "surface_condition", "roadway", "surface_condition"),
        _field(fixture, "crosswalk_context", "roadway", "crosswalk"),
        _field(fixture, "pedestrian_direction", "movement", "pedestrian_direction", uncertainty_milli=100),
        speed_field,
        _field(
            fixture,
            "detection_distance_m",
            "kinematics",
            "detection_distance_m",
            uncertainty_milli=180,
        ),
        _field(
            fixture,
            "reveal_time_millis",
            "kinematics",
            "calculated_reveal_time_millis",
            uncertainty_milli=180,
        ),
    )
