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
    assert result.graph.assess_field("kinematic_coherence").decision is FieldDecision.VERIFIED


def test_baseline_kinematic_gate_is_float_free_and_reproducible() -> None:
    result = run_pipeline(_fixture("nhtsa_vicis_991.json"))

    gate = result.receipt["body"]["kinematic_gate"]
    details = gate["details"]

    assert gate["decision"] == "VERIFIED"
    assert details["expected_reveal_time_millis"] == 3240
    assert details["observed_reveal_time_millis"] == 3000
    assert details["deviation_milli"] == 74
    assert details["policy_id"] == "spark-kinematic-coherence/0.1"


def test_kinematic_review_zone_is_explicit() -> None:
    fixture = _fixture("nhtsa_vicis_991.json").with_value(
        "kinematics",
        "calculated_reveal_time_millis",
        4300,
        label="review-zone",
    )

    result = run_pipeline(fixture)
    assessment = result.graph.assess_field("kinematic_coherence")

    assert assessment.decision is FieldDecision.REVIEW_REQUIRED
    assert assessment.reasons == (
        "validation_warning=constant_speed_time_deviation_milli=327>250",
    )


def test_kinematic_incoherence_is_blocked_before_export_trust() -> None:
    fixture = _fixture("nhtsa_vicis_991.json").with_value(
        "kinematics",
        "calculated_reveal_time_millis",
        500,
        label="collapse",
    )

    result = run_pipeline(fixture)
    assessment = result.graph.assess_field("kinematic_coherence")

    assert assessment.decision is FieldDecision.BLOCKED
    assert assessment.reasons == (
        "validation_error=constant_speed_time_deviation_milli=845>500",
    )
    assert 'name="eb_verification" parameterType="string" value="BLOCKED"' in (
        result.openscenario.xml
    )


def test_non_positive_speed_is_blocked_by_kinematic_gate() -> None:
    fixture = _fixture("nhtsa_vicis_1027.json").with_value(
        "kinematics",
        "pre_event_speed_kph",
        0,
        label="zero-speed",
    )

    result = run_pipeline(fixture)

    assert (
        result.graph.assess_field("kinematic_coherence").decision
        is FieldDecision.BLOCKED
    )
    assert (
        "validation_error=non_positive_vehicle_speed_kph"
        in result.graph.assess_field("kinematic_coherence").reasons
    )


def test_missing_kinematics_requires_review_not_completion() -> None:
    fixture = _fixture("nhtsa_vicis_1027.json").without_evidence("kinematics")

    result = run_pipeline(fixture)

    assert result.graph.fields["vehicle_speed_kph"].value is None
    assert result.graph.fields["detection_distance_m"].value is None
    assert result.graph.fields["reveal_time_millis"].value is None
    assert (
        result.graph.assess_field("kinematic_coherence").decision
        is FieldDecision.REVIEW_REQUIRED
    )


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
    assert "kinematic_coherence" in recovery.preserve_fields


def test_kinematic_change_recomputes_coherence_gate_but_not_unrelated_fields() -> None:
    fixture = _fixture("nhtsa_vicis_991.json")
    result = run_pipeline(fixture)

    recovery = result.graph.plan_recovery({"kinematics"})

    assert recovery.recompute_fields == (
        "detection_distance_m",
        "kinematic_coherence",
        "reveal_time_millis",
        "vehicle_speed_kph",
    )
    assert "functional_label" in recovery.preserve_fields
    assert "obstruction_context" in recovery.preserve_fields


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
