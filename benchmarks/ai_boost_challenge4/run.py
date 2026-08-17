"""Reproducible SPARK benchmark for EvidenceBound ScenarioGraph.

All quality ratios are integers in [0, 1000]. The benchmark is deliberately small and
must not be represented as automotive production accuracy.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from evidencebound import digest
from evidencebound_scenariograph import CrashFixture, FieldDecision, load_fixture, run_pipeline

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
FIXTURE_NAMES = ("nhtsa_vicis_991.json", "nhtsa_vicis_1027.json")


@dataclass(frozen=True)
class MutationCase:
    label: str
    baseline: CrashFixture
    mutated: CrashFixture
    expected_changed_evidence: tuple[str, ...]
    expected_recompute_fields: tuple[str, ...]


def ratio_milli(numerator: int, denominator: int) -> int:
    if denominator == 0:
        return 1000
    return numerator * 1000 // denominator


def _mutation_cases(fixtures: list[CrashFixture]) -> tuple[MutationCase, ...]:
    case_991, case_1027 = fixtures
    visibility_recompute = ("catalog_match_top1", "obstruction_context")
    kinematics_recompute = (
        "detection_distance_m",
        "reveal_time_millis",
        "vehicle_speed_kph",
    )
    movement_recompute = ("pedestrian_direction", "vehicle_maneuver")
    environment_recompute = ("atmospheric_condition", "light_condition")
    roadway_recompute = ("crosswalk_context", "roadway_alignment", "surface_condition")

    return (
        MutationCase(
            "991_visibility_obstruction_removed",
            case_991,
            case_991.with_value(
                "visibility",
                "pedestrian_vision_obscured",
                "No obstruction noted",
                label="visibility-obstruction-removed",
            ),
            ("visibility",),
            visibility_recompute,
        ),
        MutationCase(
            "991_speed_increase",
            case_991,
            case_991.with_value(
                "kinematics",
                "vehicle_speed_kph",
                55,
                label="speed-increase",
            ),
            ("kinematics",),
            kinematics_recompute,
        ),
        MutationCase(
            "991_maneuver_change",
            case_991,
            case_991.with_value(
                "movement",
                "motorist_maneuver",
                "Turning right",
                label="maneuver-change",
            ),
            ("movement",),
            movement_recompute,
        ),
        MutationCase(
            "991_visibility_removed",
            case_991,
            case_991.without_evidence("visibility"),
            ("visibility",),
            visibility_recompute,
        ),
        MutationCase(
            "1027_day_to_night",
            case_1027,
            case_1027.with_value(
                "environment",
                "light",
                "Dark – Not Lighted",
                label="day-to-night",
            ),
            ("environment",),
            environment_recompute,
        ),
        MutationCase(
            "1027_clear_to_rain",
            case_1027,
            case_1027.with_value(
                "environment",
                "atmospheric",
                "Rain",
                label="clear-to-rain",
            ),
            ("environment",),
            environment_recompute,
        ),
        MutationCase(
            "1027_dry_to_wet",
            case_1027,
            case_1027.with_value(
                "roadway",
                "surface_condition",
                "Wet",
                label="dry-to-wet",
            ),
            ("roadway",),
            roadway_recompute,
        ),
        MutationCase(
            "1027_speed_increase",
            case_1027,
            case_1027.with_value(
                "kinematics",
                "pre_event_speed_kph",
                72,
                label="speed-increase",
            ),
            ("kinematics",),
            kinematics_recompute,
        ),
        MutationCase(
            "1027_environment_removed",
            case_1027,
            case_1027.without_evidence("environment"),
            ("environment",),
            environment_recompute,
        ),
    )


def build_report() -> dict[str, Any]:
    fixtures = [load_fixture(FIXTURES / name) for name in FIXTURE_NAMES]
    results = [run_pipeline(fixture) for fixture in fixtures]

    asserted_fields = [
        item
        for result in results
        for item in result.graph.fields.values()
        if item.material and item.value is not None
    ]
    evidence_bound = [
        item for item in asserted_fields if item.evidence_ids or item.depends_on_fields
    ]
    unsupported = [
        item
        for item in asserted_fields
        if not item.evidence_ids and not item.depends_on_fields
    ]
    unknown_fields = [
        item
        for result in results
        for item in result.graph.fields.values()
        if item.material and item.value is None
    ]
    explicit_uncertainty = [item for item in unknown_fields if item.uncertainty_milli > 0]

    functional_correct = sum(
        result.functional_label == fixture.expected_functional_label
        for fixture, result in zip(fixtures, results, strict=True)
    )
    top1_correct = sum(
        bool(result.matches)
        and result.matches[0].catalog_id == fixture.expected_catalog_id
        for fixture, result in zip(fixtures, results, strict=True)
    )
    reciprocal_rank_milli = []
    for fixture, result in zip(fixtures, results, strict=True):
        rank = next(
            (
                index
                for index, item in enumerate(result.matches, start=1)
                if item.catalog_id == fixture.expected_catalog_id
            ),
            None,
        )
        reciprocal_rank_milli.append(0 if rank is None else 1000 // rank)

    reproducible = sum(
        run_pipeline(fixture).receipt == result.receipt
        for fixture, result in zip(fixtures, results, strict=True)
    )

    mutation_cases = _mutation_cases(fixtures)
    detected_exact = 0
    recovery_true_positive = 0
    recovery_observed = 0
    recovery_expected = 0
    preservation_true_positive = 0
    preservation_expected = 0
    mutation_rows: list[dict[str, Any]] = []
    baseline_results = {result.fixture.case_id: result for result in results}

    for mutation in mutation_cases:
        detected = mutation.baseline.changed_evidence_ids(mutation.mutated)
        if detected == mutation.expected_changed_evidence:
            detected_exact += 1

        baseline_result = baseline_results[mutation.baseline.case_id]
        recovery = baseline_result.graph.plan_recovery(set(detected))
        observed_recompute = set(recovery.recompute_fields)
        expected_recompute = set(mutation.expected_recompute_fields)
        recovery_true_positive += len(observed_recompute & expected_recompute)
        recovery_observed += len(observed_recompute)
        recovery_expected += len(expected_recompute)

        expected_preserve = set(baseline_result.graph.fields) - expected_recompute
        observed_preserve = set(recovery.preserve_fields)
        preservation_true_positive += len(observed_preserve & expected_preserve)
        preservation_expected += len(expected_preserve)

        mutated_result = run_pipeline(mutation.mutated)
        mutation_rows.append(
            {
                "label": mutation.label,
                "expected_changed_evidence": list(mutation.expected_changed_evidence),
                "detected_changed_evidence": list(detected),
                "expected_recompute_fields": list(mutation.expected_recompute_fields),
                "observed_recompute_fields": list(recovery.recompute_fields),
                "mutated_pipeline_receipt_sha256": mutated_result.receipt["sha256"],
            }
        )

    missing_environment = run_pipeline(fixtures[1].without_evidence("environment"))
    missing_fields = (
        missing_environment.graph.fields["light_condition"],
        missing_environment.graph.fields["atmospheric_condition"],
    )
    no_hallucinated_completion = sum(item.value is None for item in missing_fields)
    review_required = sum(
        missing_environment.graph.assess_field(item.field_id).decision
        is FieldDecision.REVIEW_REQUIRED
        for item in missing_fields
    )

    metrics = {
        "evidence_coverage_milli": ratio_milli(len(evidence_bound), len(asserted_fields)),
        "unsupported_assertion_rate_milli": ratio_milli(len(unsupported), len(asserted_fields)),
        "unknown_fields_with_explicit_uncertainty_milli": ratio_milli(
            len(explicit_uncertainty),
            len(unknown_fields),
        ),
        "functional_label_accuracy_milli": ratio_milli(functional_correct, len(fixtures)),
        "catalog_recall_at_1_milli": ratio_milli(top1_correct, len(fixtures)),
        "catalog_mrr_milli": sum(reciprocal_rank_milli) // len(reciprocal_rank_milli),
        "receipt_reproduction_rate_milli": ratio_milli(reproducible, len(fixtures)),
        "mutation_change_detection_milli": ratio_milli(detected_exact, len(mutation_cases)),
        "mutation_recovery_precision_milli": ratio_milli(
            recovery_true_positive,
            recovery_observed,
        ),
        "mutation_recovery_recall_milli": ratio_milli(
            recovery_true_positive,
            recovery_expected,
        ),
        "mutation_unrelated_preservation_milli": ratio_milli(
            preservation_true_positive,
            preservation_expected,
        ),
        "missing_evidence_no_completion_milli": ratio_milli(
            no_hallucinated_completion,
            len(missing_fields),
        ),
        "missing_evidence_review_required_milli": ratio_milli(
            review_required,
            len(missing_fields),
        ),
    }
    cases = [
        {
            "case_id": fixture.case_id,
            "source_uri": fixture.source_uri,
            "expected_functional_label": fixture.expected_functional_label,
            "observed_functional_label": result.functional_label,
            "expected_catalog_id": fixture.expected_catalog_id,
            "observed_catalog_top1": result.matches[0].catalog_id,
            "pipeline_receipt_sha256": result.receipt["sha256"],
            "openscenario_conformance": result.openscenario.conformance,
            "excluded_data_categories": list(fixture.excluded_data_categories),
        }
        for fixture, result in zip(fixtures, results, strict=True)
    ]
    body: dict[str, Any] = {
        "schema": "evidencebound-ai-boost-challenge4-benchmark/0.2",
        "scope": {
            "public_cases": len(fixtures),
            "controlled_adversarial_mutations": len(mutation_cases),
            "claim_boundary": (
                "SPARK controlled-fixture baseline; not automotive production accuracy, "
                "homologation evidence, or full OpenSCENARIO XSD conformance"
            ),
        },
        "metrics": metrics,
        "cases": cases,
        "mutations": mutation_rows,
    }
    return {
        "body": body,
        "sha256": digest(body, domain="ai-boost-challenge4-benchmark"),
    }


def assert_targets(report: dict[str, Any]) -> None:
    metrics = report["body"]["metrics"]
    assert metrics["evidence_coverage_milli"] >= 950
    assert metrics["unsupported_assertion_rate_milli"] == 0
    assert metrics["unknown_fields_with_explicit_uncertainty_milli"] == 1000
    assert metrics["functional_label_accuracy_milli"] == 1000
    assert metrics["catalog_recall_at_1_milli"] == 1000
    assert metrics["receipt_reproduction_rate_milli"] == 1000
    assert metrics["mutation_change_detection_milli"] == 1000
    assert metrics["mutation_recovery_precision_milli"] == 1000
    assert metrics["mutation_recovery_recall_milli"] == 1000
    assert metrics["mutation_unrelated_preservation_milli"] == 1000
    assert metrics["missing_evidence_no_completion_milli"] == 1000
    assert metrics["missing_evidence_review_required_milli"] == 1000


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assert-targets", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.assert_targets:
        assert_targets(report)
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
