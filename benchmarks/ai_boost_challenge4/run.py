"""Reproducible SPARK benchmark for EvidenceBound ScenarioGraph.

All quality ratios are integers in [0, 1000]. The benchmark is deliberately small and
must not be represented as automotive production accuracy.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evidencebound import digest
from evidencebound_scenariograph import FieldDecision, load_fixture, run_pipeline

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
FIXTURE_NAMES = ("nhtsa_vicis_991.json", "nhtsa_vicis_1027.json")


def ratio_milli(numerator: int, denominator: int) -> int:
    if denominator == 0:
        return 1000
    return numerator * 1000 // denominator


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

    visibility_result = results[0]
    expected_recompute = {"catalog_match_top1", "obstruction_context"}
    observed_recompute = set(
        visibility_result.graph.plan_recovery({"visibility"}).recompute_fields
    )
    invalidation_true_positive = len(expected_recompute & observed_recompute)
    invalidation_precision = ratio_milli(
        invalidation_true_positive,
        len(observed_recompute),
    )
    invalidation_recall = ratio_milli(
        invalidation_true_positive,
        len(expected_recompute),
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
        "invalidation_precision_milli": invalidation_precision,
        "invalidation_recall_milli": invalidation_recall,
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
        }
        for fixture, result in zip(fixtures, results, strict=True)
    ]
    body: dict[str, Any] = {
        "schema": "evidencebound-ai-boost-challenge4-benchmark/0.1",
        "scope": {
            "public_cases": len(fixtures),
            "controlled_adversarial_mutations": 2,
            "claim_boundary": (
                "SPARK controlled-fixture baseline; not automotive production accuracy, "
                "homologation evidence, or full OpenSCENARIO XSD conformance"
            ),
        },
        "metrics": metrics,
        "cases": cases,
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
    assert metrics["invalidation_precision_milli"] == 1000
    assert metrics["invalidation_recall_milli"] == 1000
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
