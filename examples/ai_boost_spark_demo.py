"""One-command judge-visible demo for AI-BOOST Challenge 4 SPARK evidence."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from evidencebound import digest
from evidencebound_scenariograph import load_fixture, run_pipeline

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = (
    ROOT
    / "benchmarks"
    / "ai_boost_challenge4"
    / "fixtures"
    / "nhtsa_vicis_991.json"
)


def build_demo() -> dict[str, Any]:
    fixture = load_fixture(FIXTURE)
    baseline = run_pipeline(fixture)
    mutated_fixture = fixture.with_value(
        "visibility",
        "pedestrian_vision_obscured",
        "No obstruction noted",
        label="judge-demo-visibility-change",
    )
    changed_evidence = fixture.changed_evidence_ids(mutated_fixture)
    recovery = baseline.graph.plan_recovery(set(changed_evidence))
    mutated = run_pipeline(mutated_fixture)

    body: dict[str, Any] = {
        "demo": "EvidenceBound ScenarioGraph selective recovery",
        "case_id": fixture.case_id,
        "baseline": {
            "functional_label": baseline.functional_label,
            "catalog_match_top1": baseline.matches[0].catalog_id,
            "pipeline_receipt_sha256": baseline.receipt["sha256"],
            "openscenario_conformance": baseline.openscenario.conformance,
        },
        "controlled_change": {
            "changed_evidence_ids": list(changed_evidence),
            "preserve_fields": list(recovery.preserve_fields),
            "recompute_fields": list(recovery.recompute_fields),
        },
        "after_change": {
            "pipeline_receipt_sha256": mutated.receipt["sha256"],
        },
        "claim_boundary": (
            "TRL-3 controlled-fixture demonstration; not automotive production accuracy"
        ),
    }
    return {
        "body": body,
        "sha256": digest(body, domain="ai-boost-challenge4-judge-demo"),
    }


def main() -> None:
    print(json.dumps(build_demo(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
