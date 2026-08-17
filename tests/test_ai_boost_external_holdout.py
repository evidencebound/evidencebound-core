from evidencebound_scenariograph.adapters.ni_stats20 import (
    MATERIAL_FIELDS,
    SENSITIVE_SOURCE_FIELDS_EXCLUDED,
    VEHICLE_FIELDS,
    normalize_ni_stats20_case,
    select_vulnerable_road_user_cases,
)


def _collision() -> dict[str, object]:
    return {
        "a_ref": 42,
        "a_type": 2,
        "a_ctype": 13,
        "a_speed": 30,
        "a_jdet": 12,
        "a_jcont": 7,
        "a_light": 4,
        "a_weat": 2,
        "a_roadsc": 2,
        "a_gd1": 123456,
        "a_gd2": 654321,
    }


def _vehicle() -> dict[str, object]:
    return {
        "a_ref": 42,
        "v_id": 1,
        "v_type": 8,
        "v_man": 18,
        "v_loc": 3,
        "v_sex": 1,
        "v_agegroup": 4,
    }


def _casualty() -> dict[str, object]:
    return {
        "a_ref": 42,
        "v_id": 1,
        "c_id": 1,
        "c_class": 5,
        "c_sever": 2,
        "c_loc": 6,
        "c_move": 3,
        "c_sex": 2,
        "c_agegroup": 3,
    }


def test_ni_stats20_adapter_maps_masked_pedestrian_without_sensitive_fields() -> None:
    record = normalize_ni_stats20_case(_collision(), _vehicle(), _casualty())
    fields = dict(record.fields)
    provenance = dict(record.provenance)

    assert record.case_id == "NI-2024-42"
    assert record.vehicle_joined is True
    assert fields["actor_class"] == "pedestrian"
    assert fields["harmonized_event_class"] == "pedestrian_crossing_masked_by_static_vehicle"
    assert fields["vehicle_manoeuvre"] == "going_ahead_other"
    assert fields["light_conditions"] == "darkness_street_lights_lit"
    assert fields["weather_conditions"] == "raining_without_high_winds"
    assert fields["road_surface"] == "wet_or_damp"
    assert len(record.fields) == len(MATERIAL_FIELDS)
    assert all(provenance[field] for field in MATERIAL_FIELDS)

    serialized = str(record.as_dict())
    for source_field in SENSITIVE_SOURCE_FIELDS_EXCLUDED:
        assert source_field not in serialized
    assert "123456" not in serialized
    assert "654321" not in serialized


def test_ni_stats20_adapter_keeps_missing_codes_explicitly_uncertain() -> None:
    collision = _collision()
    collision["a_light"] = ""
    collision["a_weat"] = None
    casualty = _casualty()
    casualty["c_move"] = 10

    record = normalize_ni_stats20_case(collision, _vehicle(), casualty)
    fields = dict(record.fields)

    assert fields["light_conditions"] == "unknown_missing"
    assert fields["weather_conditions"] == "unknown_missing"
    assert fields["harmonized_event_class"] == "pedestrian_movement_unknown"
    assert "light_conditions" in record.uncertain_fields
    assert "weather_conditions" in record.uncertain_fields
    assert "harmonized_event_class" in record.uncertain_fields


def test_ni_stats20_missing_vehicle_is_retained_as_explicit_uncertainty() -> None:
    casualty = _casualty()
    casualty["v_id"] = 0

    record = normalize_ni_stats20_case(_collision(), None, casualty)
    fields = dict(record.fields)

    assert record.vehicle_joined is False
    assert record.vehicle_id == "0"
    for field in VEHICLE_FIELDS:
        assert fields[field] == "unknown_missing_associated_vehicle_row"
        assert field in record.uncertain_fields


def test_ni_stats20_slight_collision_uses_source_policy_missingness() -> None:
    collision = _collision()
    collision["a_type"] = 3
    for field in ("a_jdet", "a_jcont", "a_light", "a_weat", "a_roadsc"):
        collision[field] = ""
    casualty = _casualty()
    casualty["c_sever"] = 3
    casualty["c_loc"] = ""
    casualty["c_move"] = ""

    record = normalize_ni_stats20_case(collision, None, casualty)
    fields = dict(record.fields)

    for field in (
        "junction_detail",
        "junction_control",
        "light_conditions",
        "weather_conditions",
        "road_surface",
        "pedestrian_location",
        "pedestrian_movement",
    ):
        assert fields[field] == "not_recorded_for_slight_collision"
        assert field in record.uncertain_fields
    assert (
        fields["harmonized_event_class"]
        == "pedestrian_movement_not_recorded_for_slight_collision"
    )
    assert "harmonized_event_class" in record.uncertain_fields


def test_ni_stats20_selection_keeps_missing_vehicle_and_is_deterministic() -> None:
    missing_vehicle = _casualty()
    missing_vehicle["v_id"] = 0
    missing_vehicle["c_id"] = 2
    collisions = [_collision()]
    vehicles = [_vehicle()]
    casualties = [_casualty(), missing_vehicle]

    first = select_vulnerable_road_user_cases(collisions, vehicles, casualties)
    second = select_vulnerable_road_user_cases(collisions, vehicles, casualties)

    assert len(first) == 2
    assert first == second
    assert first[0].as_dict() == second[0].as_dict()
    assert {record.vehicle_joined for record in first} == {True, False}
