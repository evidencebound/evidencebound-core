"""Deterministic kinematic coherence gate for the SPARK vertical slice.

This is a deliberately narrow sanity check, not a vehicle-dynamics simulator. It
compares reported reveal time with the constant-speed traversal time implied by
reported detection distance and pre-event speed. Thresholds are versioned prototype
policy, not homologation limits.
"""
from __future__ import annotations

from .fixture import CrashFixture
from .model import ScenarioField

KINEMATIC_POLICY_ID = "spark-kinematic-coherence/0.1"
REVIEW_DEVIATION_MILLI = 250
BLOCK_DEVIATION_MILLI = 500


def _is_integer_measurement(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def build_kinematic_coherence_field(fixture: CrashFixture) -> ScenarioField:
    """Build a float-free, judge-visible kinematic sanity-check field."""

    speed = fixture.value("kinematics", "pre_event_speed_kph")
    if speed is None:
        speed = fixture.value("kinematics", "vehicle_speed_kph")
    distance = fixture.value("kinematics", "detection_distance_m")
    observed_time = fixture.value("kinematics", "calculated_reveal_time_millis")

    value = {
        "policy_id": KINEMATIC_POLICY_ID,
        "assumption": "constant_speed_traversal_sanity_check",
        "expected_reveal_time_millis": None,
        "observed_reveal_time_millis": observed_time,
        "deviation_milli": None,
        "review_deviation_milli": REVIEW_DEVIATION_MILLI,
        "block_deviation_milli": BLOCK_DEVIATION_MILLI,
    }
    errors: list[str] = []
    warnings: list[str] = []

    measurements = {
        "vehicle_speed_kph": speed,
        "detection_distance_m": distance,
        "reveal_time_millis": observed_time,
    }
    missing = tuple(sorted(name for name, item in measurements.items() if item is None))
    if missing:
        warnings.append("insufficient_kinematic_evidence=" + ",".join(missing))
        return ScenarioField(
            "kinematic_coherence",
            value,
            uncertainty_milli=1000,
            depends_on_fields=(
                "vehicle_speed_kph",
                "detection_distance_m",
                "reveal_time_millis",
            ),
            validation_warnings=tuple(warnings),
        )

    non_integer = tuple(
        sorted(name for name, item in measurements.items() if not _is_integer_measurement(item))
    )
    if non_integer:
        errors.append("non_integer_measurement=" + ",".join(non_integer))
        return ScenarioField(
            "kinematic_coherence",
            value,
            uncertainty_milli=1000,
            depends_on_fields=(
                "vehicle_speed_kph",
                "detection_distance_m",
                "reveal_time_millis",
            ),
            validation_errors=tuple(errors),
        )

    assert isinstance(speed, int)
    assert isinstance(distance, int)
    assert isinstance(observed_time, int)

    if speed <= 0:
        errors.append("non_positive_vehicle_speed_kph")
    if distance <= 0:
        errors.append("non_positive_detection_distance_m")
    if observed_time <= 0:
        errors.append("non_positive_reveal_time_millis")

    if errors:
        return ScenarioField(
            "kinematic_coherence",
            value,
            uncertainty_milli=1000,
            depends_on_fields=(
                "vehicle_speed_kph",
                "detection_distance_m",
                "reveal_time_millis",
            ),
            validation_errors=tuple(errors),
        )

    expected_time = (distance * 3600 + speed // 2) // speed
    deviation_milli = abs(observed_time - expected_time) * 1000 // expected_time
    value["expected_reveal_time_millis"] = expected_time
    value["deviation_milli"] = deviation_milli

    if deviation_milli > BLOCK_DEVIATION_MILLI:
        errors.append(
            "constant_speed_time_deviation_milli="
            f"{deviation_milli}>{BLOCK_DEVIATION_MILLI}"
        )
    elif deviation_milli > REVIEW_DEVIATION_MILLI:
        warnings.append(
            "constant_speed_time_deviation_milli="
            f"{deviation_milli}>{REVIEW_DEVIATION_MILLI}"
        )

    return ScenarioField(
        "kinematic_coherence",
        value,
        uncertainty_milli=80 if not errors and not warnings else 500,
        depends_on_fields=(
            "vehicle_speed_kph",
            "detection_distance_m",
            "reveal_time_millis",
        ),
        validation_errors=tuple(errors),
        validation_warnings=tuple(warnings),
    )
