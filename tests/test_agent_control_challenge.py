from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHALLENGE = ROOT / "challenges" / "agent-control-v1"


def _load_validator():
    path = CHALLENGE / "validate_submission.py"
    spec = importlib.util.spec_from_file_location("agent_control_challenge_validator", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_agent_control_challenge_is_sanitized_and_self_consistent():
    scenarios = json.loads((CHALLENGE / "scenarios.json").read_text(encoding="utf-8"))
    baseline = json.loads(
        (CHALLENGE / "frozen-baseline.json").read_text(encoding="utf-8")
    )
    submission = json.loads(
        (CHALLENGE / "submission-template.json").read_text(encoding="utf-8")
    )
    receipts = json.loads(
        (CHALLENGE / "receipt-template.json").read_text(encoding="utf-8")
    )

    assert len(scenarios) == 10
    assert [scenario["scenario_id"] for scenario in scenarios] == [
        f"n1-{index:02d}-{suffix}"
        for index, suffix in enumerate(
            (
                "authorized-current",
                "no-initial-authority",
                "unsupported-evidence",
                "stale-evidence",
                "authority-revoked",
                "policy-change-deny",
                "human-correction",
                "recovery-required",
                "audit-challenge",
                "authority-ambiguous",
            ),
            start=1,
        )
    ]
    assert baseline["freeze_id"] == "AGENT-CONTROL-STUDY-v1-N12-2026-09-12"
    assert baseline["cohort_at_freeze"]["independent_external_submissions"] == 0
    assert submission["exact_source_identity"] == baseline["exact_source_identity"]
    assert len(receipts) == len(scenarios)
    assert {receipt["exact_source_identity"] for receipt in receipts} == {
        baseline["exact_source_identity"]
    }

    serialized = "\n".join(
        path.read_text(encoding="utf-8")
        for path in CHALLENGE.iterdir()
        if path.is_file()
    ).lower()
    for private_term in (
        "hard_failure_records",
        "hard_failure_count",
        "weighted_score",
        "calibration_threshold",
        "provider_api_key",
    ):
        assert private_term not in serialized


def test_public_validator_rejects_template_as_non_independent(tmp_path: Path):
    validator = _load_validator()
    submission = json.loads(
        (CHALLENGE / "submission-template.json").read_text(encoding="utf-8")
    )
    receipts = json.loads(
        (CHALLENGE / "receipt-template.json").read_text(encoding="utf-8")
    )
    (tmp_path / "submission.json").write_text(
        json.dumps(submission),
        encoding="utf-8",
    )
    (tmp_path / "receipts.json").write_text(
        json.dumps(receipts),
        encoding="utf-8",
    )

    try:
        validator.validate_submission_directory(tmp_path)
    except validator.SubmissionValidationError as exc:
        assert "independent_from_evidencebound" in str(exc)
    else:
        raise AssertionError("template must not pass independent submission validation")
