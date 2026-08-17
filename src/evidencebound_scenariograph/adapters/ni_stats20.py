"""Northern Ireland 2024 STATS20-compatible public-data adapter.

The adapter intentionally retains scenario-relevant coded fields only. Driver/casualty
sex, age-group and exact OSGR coordinates are excluded from the normalized record.
Code semantics and conditional recording rules are taken from the PSNI 2024 public
Data Guide; no missing code or missing associated-vehicle row is silently completed.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

DATASET_ID = "psni-ni-injury-rtc-2024"
DATA_GUIDE_URL = (
    "https://admin.opendatani.gov.uk/dataset/bba6af11-b283-432e-8155-c6af9e0da461/"
    "resource/08dac536-5d3c-413f-9fcc-040a3b228a42/download/data-guide_2024.pdf"
)
OGL_URL = "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"

COLLISION_SEVERITY = {
    1: "fatal_injury_collision",
    2: "serious_injury_collision",
    3: "slight_injury_collision",
}
CARRIAGEWAY_TYPE = {
    1: "roundabout",
    2: "one_way_street",
    10: "other_or_unknown",
    11: "dual_carriageway",
    12: "motorway",
    13: "single_carriageway",
    14: "slip_road",
}
JUNCTION_DETAIL = {
    1: "not_at_or_within_20m_of_junction",
    2: "roundabout",
    3: "mini_roundabout",
    6: "crossroads",
    8: "multiple_junction",
    9: "slip_road",
    10: "private_drive_or_entrance",
    11: "other_junction",
    12: "t_or_staggered_junction",
}
JUNCTION_CONTROL = {
    1: "not_at_junction",
    2: "authorised_person",
    3: "automatic_traffic_signal",
    4: "stop_sign",
    7: "give_way_or_uncontrolled",
}
LIGHT_CONDITIONS = {
    1: "daylight_street_lights_present",
    2: "daylight_no_street_lighting",
    3: "daylight_street_lighting_unknown",
    4: "darkness_street_lights_lit",
    5: "darkness_street_lights_unlit",
    6: "darkness_no_street_lighting",
    7: "darkness_street_lighting_unknown",
}
WEATHER_CONDITIONS = {
    1: "fine_without_high_winds",
    2: "raining_without_high_winds",
    3: "snowing_without_high_winds",
    4: "fine_with_high_winds",
    5: "raining_with_high_winds",
    6: "snowing_with_high_winds",
    7: "fog_or_mist_if_hazard",
    8: "strong_sun_glaring",
    9: "other",
    10: "unknown",
}
ROAD_SURFACE = {
    1: "dry",
    2: "wet_or_damp",
    3: "snow",
    4: "frost_or_ice",
    5: "flood",
    6: "oil",
    7: "mud",
    8: "leaves",
    9: "slippery_after_dry_spell",
    10: "other",
}
VEHICLE_TYPE = {
    0: "unknown",
    1: "pedal_cycle",
    2: "motorcycle_moped",
    4: "motorcycle_under_125cc",
    5: "motorcycle_125cc_and_above",
    7: "car_taxi_hackney",
    8: "car",
    9: "motor_caravan",
    14: "other_motor_vehicle",
    15: "goods_3_5t_or_less",
    16: "goods_over_3_5t_under_7_5t",
    17: "goods_7_5t_or_over",
    18: "car_used_as_taxi",
    19: "minibus",
    20: "bus_or_coach",
    21: "ridden_horse",
    22: "other_non_motor_vehicle",
    23: "motorcycle_engine_size_unknown",
    24: "goods_vehicle_weight_unknown",
    25: "agricultural_vehicle",
}
VEHICLE_MANOEUVRE = {
    1: "reversing",
    2: "parked",
    3: "about_to_go_ahead_held_up",
    4: "slowing_or_stopping",
    5: "moving_off",
    6: "u_turn",
    7: "turning_left",
    8: "waiting_to_turn_left",
    9: "turning_right",
    10: "waiting_to_turn_right",
    11: "changing_lane_left",
    12: "changing_lane_right",
    13: "overtaking_moving_vehicle_offside",
    14: "overtaking_stationary_vehicle_offside",
    15: "overtaking_nearside",
    16: "going_ahead_left_bend",
    17: "going_ahead_right_bend",
    18: "going_ahead_other",
    19: "other_or_not_known",
}
VEHICLE_LOCATION = {
    1: "leaving_main_road",
    2: "entering_main_road",
    3: "on_main_road",
    4: "on_minor_road",
    6: "on_layby_or_hard_shoulder",
    7: "entering_layby_or_hard_shoulder",
    8: "leaving_layby_or_hard_shoulder",
    9: "on_cycle_lane_or_cycle_way",
    10: "pedestrian_vehicle_shared_precinct",
    11: "other_public_place",
    12: "bus_lane_or_busway",
    13: "footpath_pavement",
}
CASUALTY_CLASS = {
    1: "driver",
    2: "pillion_passenger",
    3: "vehicle_passenger_front",
    4: "vehicle_passenger_rear",
    5: "pedestrian",
    6: "motorcyclist",
    7: "pedal_cyclist",
}
CASUALTY_SEVERITY = {1: "fatal", 2: "seriously_injured", 3: "slightly_injured"}
PEDESTRIAN_LOCATION = {
    1: "not_a_pedestrian",
    2: "crossing_on_pedestrian_crossing",
    3: "crossing_within_zigzag_at_approach",
    4: "crossing_within_zigzag_at_exit",
    5: "crossing_elsewhere_within_50m_of_crossing",
    6: "crossing_elsewhere",
    7: "on_footway_or_verge",
    8: "on_refuge_central_island_or_reservation",
    9: "in_centre_of_carriageway",
    10: "in_carriageway_not_crossing",
    11: "unknown_or_other",
}
PEDESTRIAN_MOVEMENT = {
    1: "not_a_pedestrian",
    2: "crossing_from_driver_nearside",
    3: "crossing_from_driver_nearside_masked_by_static_vehicle",
    4: "crossing_from_driver_offside",
    5: "crossing_from_driver_offside_masked_by_static_vehicle",
    6: "stationary_in_carriageway_not_crossing",
    7: "stationary_in_carriageway_masked_by_vehicle",
    8: "walking_in_carriageway_facing_traffic",
    9: "walking_in_carriageway_back_to_traffic",
    10: "unknown_or_other",
}

MATERIAL_FIELDS = (
    "actor_class",
    "harmonized_event_class",
    "collision_severity",
    "carriageway_type",
    "speed_limit_recorded",
    "junction_detail",
    "junction_control",
    "light_conditions",
    "weather_conditions",
    "road_surface",
    "vehicle_type",
    "vehicle_manoeuvre",
    "vehicle_location",
    "casualty_severity",
    "pedestrian_location",
    "pedestrian_movement",
)
VEHICLE_FIELDS = ("vehicle_type", "vehicle_manoeuvre", "vehicle_location")
SENSITIVE_SOURCE_FIELDS_EXCLUDED = (
    "collision.a_gd1",
    "collision.a_gd2",
    "vehicle.v_sex",
    "vehicle.v_agegroup",
    "casualty.c_sex",
    "casualty.c_agegroup",
)


def _code(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(str(value).strip())
    except ValueError:
        return None


def _stable_id(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.isdigit():
        return str(int(text))
    return text


def _mapped(value: Any, mapping: Mapping[int, str]) -> tuple[str, bool]:
    code = _code(value)
    if code is None:
        return "unknown_missing", True
    label = mapping.get(code)
    if label is None:
        return f"unknown_code_{code}", True
    return label, label in {
        "unknown",
        "unknown_or_other",
        "other_or_unknown",
        "other_or_not_known",
    }


def _event_class(
    casualty_class: int | None,
    pedestrian_move: int | None,
    *,
    slight_collision: bool,
) -> tuple[str, bool]:
    if casualty_class == 7:
        return "pedal_cyclist_casualty", False
    if casualty_class != 5:
        return "unsupported_actor_class", True
    if pedestrian_move in {3, 5}:
        return "pedestrian_crossing_masked_by_static_vehicle", False
    if pedestrian_move in {2, 4}:
        return "pedestrian_crossing", False
    if pedestrian_move in {6, 7, 8, 9}:
        return "pedestrian_in_carriageway", False
    if pedestrian_move is None and slight_collision:
        return "pedestrian_movement_not_recorded_for_slight_collision", True
    return "pedestrian_movement_unknown", True


@dataclass(frozen=True)
class NIStats20Record:
    """Data-minimised canonical record for independent holdout evaluation."""

    case_id: str
    vehicle_id: str
    casualty_id: str
    vehicle_joined: bool
    fields: tuple[tuple[str, Any], ...]
    provenance: tuple[tuple[str, tuple[str, ...]], ...]
    uncertain_fields: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "vehicle_id": self.vehicle_id,
            "casualty_id": self.casualty_id,
            "vehicle_joined": self.vehicle_joined,
            "fields": dict(self.fields),
            "provenance": {key: list(value) for key, value in self.provenance},
            "uncertain_fields": list(self.uncertain_fields),
        }


def normalize_ni_stats20_case(
    collision: Mapping[str, Any],
    vehicle: Mapping[str, Any] | None,
    casualty: Mapping[str, Any],
) -> NIStats20Record:
    """Normalize one PSNI collision/casualty case with an optional vehicle row."""

    collision_ref = _stable_id(collision.get("a_ref"))
    vehicle_joined = vehicle is not None
    vehicle_id = _stable_id((vehicle or casualty).get("v_id"))
    casualty_id = _stable_id(casualty.get("c_id"))
    collision_type_code = _code(collision.get("a_type"))
    slight_collision = collision_type_code == 3
    casualty_class_code = _code(casualty.get("c_class"))
    pedestrian_move_code = _code(casualty.get("c_move"))

    values: dict[str, Any] = {}
    uncertain: set[str] = set()
    provenance: dict[str, tuple[str, ...]] = {}

    def add_mapped(
        name: str,
        raw: Any,
        mapping: Mapping[int, str],
        source: str,
        *,
        conditional_slight: bool = False,
    ) -> None:
        if conditional_slight and slight_collision and _code(raw) is None:
            values[name] = "not_recorded_for_slight_collision"
            provenance[name] = (source, "collision.a_type", DATA_GUIDE_URL)
            uncertain.add(name)
            return
        value, is_uncertain = _mapped(raw, mapping)
        values[name] = value
        provenance[name] = (source, DATA_GUIDE_URL)
        if is_uncertain:
            uncertain.add(name)

    add_mapped("actor_class", casualty.get("c_class"), CASUALTY_CLASS, "casualty.c_class")
    event_class, event_uncertain = _event_class(
        casualty_class_code,
        pedestrian_move_code,
        slight_collision=slight_collision,
    )
    values["harmonized_event_class"] = event_class
    provenance["harmonized_event_class"] = (
        "casualty.c_class",
        "casualty.c_move",
        "collision.a_type",
        DATA_GUIDE_URL,
    )
    if event_uncertain:
        uncertain.add("harmonized_event_class")

    add_mapped(
        "collision_severity", collision.get("a_type"), COLLISION_SEVERITY, "collision.a_type"
    )
    add_mapped(
        "carriageway_type", collision.get("a_ctype"), CARRIAGEWAY_TYPE, "collision.a_ctype"
    )
    speed = _code(collision.get("a_speed"))
    values["speed_limit_recorded"] = speed if speed is not None else "unknown_missing"
    provenance["speed_limit_recorded"] = ("collision.a_speed", DATA_GUIDE_URL)
    if speed is None:
        uncertain.add("speed_limit_recorded")

    add_mapped(
        "junction_detail",
        collision.get("a_jdet"),
        JUNCTION_DETAIL,
        "collision.a_jdet",
        conditional_slight=True,
    )
    add_mapped(
        "junction_control",
        collision.get("a_jcont"),
        JUNCTION_CONTROL,
        "collision.a_jcont",
        conditional_slight=True,
    )
    add_mapped(
        "light_conditions",
        collision.get("a_light"),
        LIGHT_CONDITIONS,
        "collision.a_light",
        conditional_slight=True,
    )
    add_mapped(
        "weather_conditions",
        collision.get("a_weat"),
        WEATHER_CONDITIONS,
        "collision.a_weat",
        conditional_slight=True,
    )
    add_mapped(
        "road_surface",
        collision.get("a_roadsc"),
        ROAD_SURFACE,
        "collision.a_roadsc",
        conditional_slight=True,
    )

    if vehicle is None:
        for name in VEHICLE_FIELDS:
            values[name] = "unknown_missing_associated_vehicle_row"
            provenance[name] = ("casualty.v_id", DATA_GUIDE_URL)
            uncertain.add(name)
    else:
        add_mapped("vehicle_type", vehicle.get("v_type"), VEHICLE_TYPE, "vehicle.v_type")
        add_mapped(
            "vehicle_manoeuvre", vehicle.get("v_man"), VEHICLE_MANOEUVRE, "vehicle.v_man"
        )
        add_mapped(
            "vehicle_location", vehicle.get("v_loc"), VEHICLE_LOCATION, "vehicle.v_loc"
        )

    add_mapped(
        "casualty_severity", casualty.get("c_sever"), CASUALTY_SEVERITY, "casualty.c_sever"
    )
    add_mapped(
        "pedestrian_location",
        casualty.get("c_loc"),
        PEDESTRIAN_LOCATION,
        "casualty.c_loc",
        conditional_slight=True,
    )
    add_mapped(
        "pedestrian_movement",
        casualty.get("c_move"),
        PEDESTRIAN_MOVEMENT,
        "casualty.c_move",
        conditional_slight=True,
    )

    return NIStats20Record(
        case_id=f"NI-2024-{collision_ref}",
        vehicle_id=vehicle_id,
        casualty_id=casualty_id,
        vehicle_joined=vehicle_joined,
        fields=tuple((name, values[name]) for name in MATERIAL_FIELDS),
        provenance=tuple((name, provenance[name]) for name in MATERIAL_FIELDS),
        uncertain_fields=tuple(sorted(uncertain)),
    )


def select_vulnerable_road_user_cases(
    collisions: Sequence[Mapping[str, Any]],
    vehicles: Sequence[Mapping[str, Any]],
    casualties: Sequence[Mapping[str, Any]],
    *,
    limit: int = 64,
) -> tuple[NIStats20Record, ...]:
    """Select pedestrian/cyclist casualties without dropping missing vehicle joins."""

    collision_by_ref = {_stable_id(row.get("a_ref")): row for row in collisions}
    vehicle_by_key = {
        (_stable_id(row.get("a_ref")), _stable_id(row.get("v_id"))): row for row in vehicles
    }
    eligible = [row for row in casualties if _code(row.get("c_class")) in {5, 7}]
    eligible.sort(
        key=lambda row: (
            _stable_id(row.get("a_ref")).zfill(12),
            _stable_id(row.get("v_id")).zfill(6),
            _stable_id(row.get("c_id")).zfill(6),
        )
    )

    result: list[NIStats20Record] = []
    for casualty in eligible:
        ref = _stable_id(casualty.get("a_ref"))
        vehicle_id = _stable_id(casualty.get("v_id"))
        collision = collision_by_ref.get(ref)
        if collision is None:
            continue
        vehicle = vehicle_by_key.get((ref, vehicle_id))
        result.append(normalize_ni_stats20_case(collision, vehicle, casualty))
        if len(result) >= limit:
            break
    return tuple(result)
