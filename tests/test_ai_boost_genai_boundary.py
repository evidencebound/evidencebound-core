from pathlib import Path

import pytest

from evidencebound_scenariograph import (
    FieldDecision,
    GenerativeCandidateError,
    RecordedGenerativeExtractor,
    load_fixture,
    run_pipeline,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    ROOT / "benchmarks" / "ai_boost_challenge4" / "fixtures" / "nhtsa_vicis_991.json"
)


def _candidate(*, obstruction_evidence: str = "visibility") -> dict[str, object]:
    return {
        "provider": "example-provider",
        "model": "example-model",
        "prompt_version": "functional-scenario-v1",
        "source_case_id": "NHTSA-VICIS-991",
        "functional_label": "pedestrian_dart_out_visual_obstruction",
        "fields": [
            {
                "field_id": "crash_type",
                "value": "Dart-Out – Visual Obstruction Noted",
                "evidence_ids": ["crash_classification"],
                "uncertainty_milli": 80,
            },
            {
                "field_id": "crash_group",
                "value": "Dash – Run / Dart-Out",
                "evidence_ids": ["crash_classification"],
                "uncertainty_milli": 120,
            },
            {
                "field_id": "crash_location",
                "value": "Intersection-Related",
                "evidence_ids": ["crash_classification"],
                "uncertainty_milli": 80,
            },
            {
                "field_id": "vehicle_maneuver",
                "value": "Straight through",
                "evidence_ids": ["movement"],
                "uncertainty_milli": 120,
            },
            {
                "field_id": "obstruction_context",
                "value": "View obstructed by non-contact vehicle",
                "evidence_ids": [obstruction_evidence],
                "uncertainty_milli": 160,
            },
            {
                "field_id": "functional_label",
                "value": "pedestrian_dart_out_visual_obstruction",
                "evidence_ids": ["crash_classification", "visibility"],
                "uncertainty_milli": 140,
            },
        ],
    }


def test_recorded_genai_candidate_runs_through_same_pipeline_contract() -> None:
    fixture = load_fixture(FIXTURE_PATH)
    extractor = RecordedGenerativeExtractor(_candidate())

    result = run_pipeline(fixture, extractor=extractor)

    assert result.functional_label == fixture.expected_functional_label
    assert result.matches[0].catalog_id == fixture.expected_catalog_id
    assert result.extractor_id == (
        "recorded-genai/example-provider/example-model/functional-scenario-v1"
    )
    assert result.graph.assess_field("functional_label").decision is FieldDecision.VERIFIED


def test_invented_evidence_reference_is_blocked_by_deterministic_gate() -> None:
    fixture = load_fixture(FIXTURE_PATH)
    extractor = RecordedGenerativeExtractor(
        _candidate(obstruction_evidence="invented_evidence_id")
    )

    result = run_pipeline(fixture, extractor=extractor)

    obstruction = result.graph.assess_field("obstruction_context")
    top_match = result.graph.assess_field("catalog_match_top1")
    assert obstruction.decision is FieldDecision.BLOCKED
    assert obstruction.reasons == ("missing_evidence=invented_evidence_id",)
    assert top_match.decision is FieldDecision.BLOCKED


def test_candidate_cannot_be_replayed_against_a_different_crash_case() -> None:
    fixture = load_fixture(FIXTURE_PATH)
    candidate = _candidate()
    candidate["source_case_id"] = "NHTSA-VICIS-OTHER"
    extractor = RecordedGenerativeExtractor(candidate)

    with pytest.raises(GenerativeCandidateError, match="does not match"):
        run_pipeline(fixture, extractor=extractor)
