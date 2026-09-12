from __future__ import annotations

import json
import sys
from pathlib import Path

CHALLENGE_ROOT = Path(__file__).resolve().parent
SCENARIOS_PATH = CHALLENGE_ROOT / "scenarios.json"
SOURCE_IDENTITY = (
    "source-set@sha256:14dc37a84feb225c6f80a675a778f44785c02a3f7b6ac8bc8a2206b4c26f266b"
)
CHALLENGE_VERSION = "AGENT-CONTROL-CHALLENGE-v1-development"
ALLOWED_DECISIONS = {"execute", "hold", "abstain", "error"}
ALLOWED_PUBLICATION = {"full", "aggregate_only", "redacted"}


class SubmissionValidationError(ValueError):
    pass


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SubmissionValidationError(f"cannot load {path}: {exc}") from exc


def validate_submission_directory(directory: Path) -> dict[str, object]:
    submission_path = directory / "submission.json"
    receipts_path = directory / "receipts.json"
    submission = _load_json(submission_path)
    receipts = _load_json(receipts_path)
    scenarios = _load_json(SCENARIOS_PATH)

    if not isinstance(submission, dict):
        raise SubmissionValidationError("submission.json must contain one JSON object")
    if not isinstance(receipts, list):
        raise SubmissionValidationError("receipts.json must contain one JSON array")
    if not isinstance(scenarios, list):
        raise SubmissionValidationError("challenge scenarios are invalid")

    if submission.get("challenge_version") != CHALLENGE_VERSION:
        raise SubmissionValidationError("challenge_version mismatch")
    if submission.get("exact_source_identity") != SOURCE_IDENTITY:
        raise SubmissionValidationError("exact_source_identity mismatch")

    submitter = submission.get("submitter")
    if not isinstance(submitter, dict):
        raise SubmissionValidationError("submitter must be an object")
    if submitter.get("independent_from_evidencebound") is not True:
        raise SubmissionValidationError("independent_from_evidencebound must be true")
    if not str(submitter.get("github_handle", "")).strip() or submitter.get(
        "github_handle"
    ) == "replace-me":
        raise SubmissionValidationError("github_handle is required")
    if not str(submitter.get("independence_attestation", "")).strip():
        raise SubmissionValidationError("independence_attestation is required")
    if submitter.get("permission_to_publish") not in ALLOWED_PUBLICATION:
        raise SubmissionValidationError("permission_to_publish is invalid")

    system = submission.get("system")
    if not isinstance(system, dict):
        raise SubmissionValidationError("system must be an object")
    system_id = str(system.get("system_id", "")).strip()
    if not system_id or system_id == "replace-me":
        raise SubmissionValidationError("system_id is required")

    implementation = submission.get("implementation")
    execution = submission.get("execution")
    if not isinstance(implementation, dict) or not isinstance(execution, dict):
        raise SubmissionValidationError("implementation and execution must be objects")
    for field in ("framework", "framework_version", "architecture_summary"):
        if not str(implementation.get(field, "")).strip():
            raise SubmissionValidationError(f"implementation.{field} is required")
    if not str(execution.get("run_identity", "")).strip():
        raise SubmissionValidationError("execution.run_identity is required")

    expected_ids = [scenario["scenario_id"] for scenario in scenarios]
    observed_ids = []
    for index, receipt in enumerate(receipts):
        if not isinstance(receipt, dict):
            raise SubmissionValidationError(f"receipt {index} must be an object")
        scenario_id = receipt.get("scenario_id")
        observed_ids.append(scenario_id)
        if receipt.get("exact_source_identity") != SOURCE_IDENTITY:
            raise SubmissionValidationError(
                f"receipt {scenario_id!r} has source identity mismatch"
            )
        current_state = receipt.get("current_state")
        system_output = receipt.get("system_output")
        if not isinstance(current_state, dict) or not isinstance(system_output, dict):
            raise SubmissionValidationError(
                f"receipt {scenario_id!r} requires current_state and system_output"
            )
        if system_output.get("decision") not in ALLOWED_DECISIONS:
            raise SubmissionValidationError(
                f"receipt {scenario_id!r} has invalid decision"
            )
        if not str(system_output.get("framework_native_runtime", "")).strip():
            raise SubmissionValidationError(
                f"receipt {scenario_id!r} requires framework_native_runtime"
            )

    if len(receipts) != len(expected_ids):
        raise SubmissionValidationError(
            f"expected {len(expected_ids)} receipts, got {len(receipts)}"
        )
    if observed_ids != expected_ids:
        raise SubmissionValidationError(
            "receipt scenario IDs must exactly match scenarios.json in order"
        )

    return {
        "system_id": system_id,
        "receipt_count": len(receipts),
        "source_identity": SOURCE_IDENTITY,
        "format_valid": True,
    }


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: python challenges/agent-control-v1/validate_submission.py <directory>")
        return 2
    try:
        result = validate_submission_directory(Path(args[0]))
    except SubmissionValidationError as exc:
        print(f"INVALID: {exc}")
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
