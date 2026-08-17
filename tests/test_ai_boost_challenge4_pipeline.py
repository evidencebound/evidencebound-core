from pathlib import Path

from evidencebound_scenariograph import FieldDecision, load_fixture, run_pipeline

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "benchmarks" / "ai_boost_challenge4" / "fixtures"


def _fixture(name: str):  # type: ignore[no-untyped-def]
    return load_fixture(FIXTURES / name)


def test_nhtsa_991_end_to_end_is_evidence_grounded_and_reproducible() -> None:
    fixture = _fixture("nhtsa_vicis_991.json")

    first = run_pipeline(fixture)
    second = run_pipeline(fixture)

    assert first.functional_label == fixture.expected_functional_label
    assert first.matches[0].catalog_id == fixture.expected_catalog_id
    assert first.receipt == second.receipt
    assert first.openscenario.standard == "ASAM OpenSCENARIO XML 1.4"
    assert (
        first.openscenario.conformance
        == "ASAM_OPENSCENARIO_XML_1_4_XSD_VALIDATED_IN_CI"
    )
    assert 'revMinor="4"' in first.openscenario.xml
    assert "<Init><Actions /></Init>" in first.openscenario.xml
    assert "<StopTrigger />" in first.openscenario.xml


def test_nhtsa_1027_end_to_end_matches_expected_catalog_scenario() -> None:
    fixture = _fixture("nhtsa_vicis_1027.json")

    result = run_pipeline(fixture)

    assert result.functional_label == fixture.expected_functional_label
    assert result.matches[0].catalog_id == fixture.expected_catalog_id
    assert result.graph.assess_field("light_condition").decision is FieldDecision.VERIFIED
    assert result.graph.assess_field("vehicle_speed_kph").decision is FieldDecision.VERIFIED


def test_missing_environment_is_explicit_not_hallucinated() -> None:
    fixture = _fixture("nhtsa_vicis_1027.json").without_evidence("environment")

    result = run_pipeline(fixture)

    light = result.graph.fields["light_condition"]
    atmosphere = result.graph.fields["atmospheric_condition"]
    assert light.value is None
    assert atmosphere.value is None
    assert light.uncertainty_milli == 1000
    assert atmosphere.uncertainty_milli == 1000
    assert result.graph.assess_field("light_condition").decision is FieldDecision.REVIEW_REQUIRED
    assert (
        result.graph.assess_field("atmospheric_condition").decision
        is FieldDecision.REVIEW_REQUIRED
    )


def test_visibility_change_recomputes_only_dependent_branch() -> None:
    fixture = _fixture("nhtsa_vicis_991.json")
    result = run_pipeline(fixture)

    recovery = result.graph.plan_recovery({"visibility"})

    assert recovery.recompute_fields == ("catalog_match_top1", "obstruction_context")
    assert "functional_label" in recovery.preserve_fields
    assert "vehicle_speed_kph" in recovery.preserve_fields


def test_public_fixture_payloads_exclude_sensitive_person_fields() -> None:
    prohibited = {
        "age",
        "sex",
        "race",
        "ethnicity",
        "injury",
        "alcohol",
        "drug",
        "medical",
        "height",
        "weight",
    }
    for name in ("nhtsa_vicis_991.json", "nhtsa_vicis_1027.json"):
        fixture = _fixture(name)
        keys = {
            str(key).lower()
            for item in fixture.evidence
            for key in item.payload
        }
        assert prohibited.isdisjoint(keys)
