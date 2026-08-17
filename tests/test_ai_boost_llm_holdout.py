from benchmarks.ai_boost_challenge4.llm_holdout_gemini import (
    EVALUATED_FIELDS,
    score_candidate,
)
from evidencebound_scenariograph.adapters.ni_stats20 import normalize_ni_stats20_case


def _expected():
    collision = {
        "a_ref": 501,
        "a_type": 2,
        "a_ctype": 13,
        "a_speed": 30,
        "a_jdet": 12,
        "a_jcont": 7,
        "a_light": 4,
        "a_weat": 2,
        "a_roadsc": 2,
    }
    vehicle = {
        "a_ref": 501,
        "v_id": 1,
        "v_type": 8,
        "v_man": 18,
        "v_loc": 3,
    }
    casualty = {
        "a_ref": 501,
        "v_id": 1,
        "c_id": 1,
        "c_class": 5,
        "c_sever": 2,
        "c_loc": 6,
        "c_move": 3,
    }
    return normalize_ni_stats20_case(collision, vehicle, casualty)


def _perfect_candidate():
    expected = _expected()
    values = dict(expected.fields)
    sources = {
        "actor_class": ["casualty.c_class"],
        "harmonized_event_class": ["casualty.c_class", "casualty.c_move"],
        "collision_severity": ["collision.a_type"],
        "carriageway_type": ["collision.a_ctype"],
        "light_conditions": ["collision.a_light"],
        "weather_conditions": ["collision.a_weat"],
        "road_surface": ["collision.a_roadsc"],
        "vehicle_type": ["vehicle.v_type"],
        "vehicle_manoeuvre": ["vehicle.v_man"],
        "pedestrian_movement": ["casualty.c_move"],
    }
    return {
        "case_id": expected.case_id,
        "fields": [
            {
                "field_id": field_id,
                "value": values[field_id],
                "source_fields": sources[field_id],
                "uncertain": False,
                "uncertainty_reason": "",
            }
            for field_id in EVALUATED_FIELDS
        ],
    }


def test_llm_holdout_perfect_candidate_is_verified_against_comparator() -> None:
    score = score_candidate(_expected(), _perfect_candidate())
    assert score["exact_fields"] == len(EVALUATED_FIELDS)
    assert score["valid_ref_fields"] == len(EVALUATED_FIELDS)
    assert score["source_covered_fields"] == len(EVALUATED_FIELDS)
    assert score["semantic_errors"] == []
    assert score["structural_issues"] == []
    assert score["invalid_evidence_refs"] == []
    assert score["structural_trust_decision"] == "VERIFIED_CANDIDATE"
    assert score["benchmark_evaluation_decision"] == "VERIFIED_AGAINST_HELDOUT_COMPARATOR"


def test_llm_holdout_invented_source_reference_is_blocked() -> None:
    candidate = _perfect_candidate()
    candidate["fields"][0]["source_fields"] = ["invented.secret_source"]
    score = score_candidate(_expected(), candidate)
    assert score["invalid_evidence_refs"] == ["actor_class"]
    assert score["structural_trust_decision"] == "BLOCKED"
    assert score["benchmark_evaluation_decision"] == "BLOCKED"


def test_llm_holdout_semantic_error_is_not_misrepresented_as_provenance_failure() -> None:
    candidate = _perfect_candidate()
    candidate["fields"][0]["value"] = "pedal_cyclist"
    score = score_candidate(_expected(), candidate)
    assert score["invalid_evidence_refs"] == []
    assert score["structural_trust_decision"] == "VERIFIED_CANDIDATE"
    assert score["semantic_errors"]
    assert score["benchmark_evaluation_decision"] == "REVIEW_REQUIRED_COMPARATOR_MISMATCH"


def test_llm_holdout_missing_vehicle_can_abstain_without_completion() -> None:
    collision = {
        "a_ref": 502,
        "a_type": 3,
        "a_ctype": 13,
        "a_speed": 30,
        "a_jdet": "",
        "a_jcont": "",
        "a_light": "",
        "a_weat": "",
        "a_roadsc": "",
    }
    casualty = {
        "a_ref": 502,
        "v_id": 0,
        "c_id": 1,
        "c_class": 5,
        "c_sever": 3,
        "c_loc": "",
        "c_move": "",
    }
    expected = normalize_ni_stats20_case(collision, None, casualty)
    values = dict(expected.fields)
    source_map = {
        "actor_class": ["casualty.c_class"],
        "harmonized_event_class": [
            "casualty.c_move",
            "collision.a_type",
            "source_policy.conditional_recording",
        ],
        "collision_severity": ["collision.a_type"],
        "carriageway_type": ["collision.a_ctype"],
        "light_conditions": ["collision.a_type", "source_policy.conditional_recording"],
        "weather_conditions": ["collision.a_type", "source_policy.conditional_recording"],
        "road_surface": ["collision.a_type", "source_policy.conditional_recording"],
        "vehicle_type": ["casualty.v_id"],
        "vehicle_manoeuvre": ["casualty.v_id"],
        "pedestrian_movement": [
            "casualty.c_move",
            "collision.a_type",
            "source_policy.conditional_recording",
        ],
    }
    fields = []
    for field_id in EVALUATED_FIELDS:
        uncertain = field_id in expected.uncertain_fields
        fields.append(
            {
                "field_id": field_id,
                "value": values[field_id],
                "source_fields": source_map[field_id],
                "uncertain": uncertain,
                "uncertainty_reason": "source missingness" if uncertain else "",
            }
        )
    score = score_candidate(expected, {"case_id": expected.case_id, "fields": fields})
    assert score["semantic_errors"] == []
    assert score["missing_vehicle_expected"] == 2
    assert score["missing_vehicle_no_completion"] == 2
    assert score["source_policy_expected"] == 4
    assert score["source_policy_no_completion"] == 4
    assert score["structural_trust_decision"] == "REVIEW_REQUIRED"
