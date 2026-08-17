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

    visibility_fixture = fixture.with_value(
        "visibility",
        "pedestrian_vision_obscured",
        "No obstruction noted",
        label="judge-demo-visibility-change",
    )
    visibility_changed = fixture.changed_evidence_ids(visibility_fixture)
    visibility_recovery = baseline.graph.plan_recovery(set(visibility_changed))
    visibility_result = run_pipeline(visibility_fixture)

    kinematic_fixture = fixture.with_value(
        "kinematics",
        "calculated_reveal_time_millis",
        500,
        label="judge-demo-kinematic-inconsistency",
    )
    kinematic_changed = fixture.changed_evidence_ids(kinematic_fixture)
    kinematic_recovery = baseline.graph.plan_recovery(set(kinematic_changed))
    kinematic_result = run_pipeline(kinematic_fixture)
    kinematic_gate = kinematic_result.receipt["body"]["kinematic_gate"]

    body: dict[str, Any] = {
        "demo": "EvidenceBound ScenarioGraph deterministic trust + selective recovery",
        "case_id": fixture.case_id,
        "baseline": {
            "functional_label": baseline.functional_label,
            "catalog_match_top1": baseline.matches[0].catalog_id,
            "pipeline_receipt_sha256": baseline.receipt["sha256"],
            "openscenario_conformance": baseline.openscenario.conformance,
            "kinematic_gate": baseline.receipt["body"]["kinematic_gate"],
        },
        "selective_recovery_demo": {
            "change": "visibility evidence changed",
            "changed_evidence_ids": list(visibility_changed),
            "preserve_fields": list(visibility_recovery.preserve_fields),
            "recompute_fields": list(visibility_recovery.recompute_fields),
            "after_change_pipeline_receipt_sha256": visibility_result.receipt["sha256"],
        },
        "kinematic_fail_closed_demo": {
            "change": "reported reveal time changed from 3000 ms to 500 ms",
            "changed_evidence_ids": list(kinematic_changed),
            "preserve_fields": list(kinematic_recovery.preserve_fields),
            "recompute_fields": list(kinematic_recovery.recompute_fields),
            "gate_decision": kinematic_gate["decision"],
            "gate_reasons": kinematic_gate["reasons"],
            "gate_details": kinematic_gate["details"],
            "openscenario_embeds_blocked_verification": (
                'name="eb_verification" parameterType="string" value="BLOCKED"'
                in kinematic_result.openscenario.xml
            ),
            "after_change_pipeline_receipt_sha256": kinematic_result.receipt["sha256"],
        },
        "claim_boundary": (
            "TRL-3 controlled-fixture demonstration; kinematic gate is a versioned "
            "sanity check, not automotive production accuracy or simulator validation"
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
