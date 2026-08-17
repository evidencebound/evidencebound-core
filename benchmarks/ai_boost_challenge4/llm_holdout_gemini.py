"""Live schema-constrained Gemini extraction benchmark for AI-BOOST Challenge 4.

The benchmark is intentionally separate from deterministic ScenarioGraph trust metrics.
It fetches the independent PSNI Northern Ireland 2024 public dataset, selects a fixed
vulnerable-road-user holdout, sends data-minimised coded evidence packets to Gemini,
and compares structured model output with the deterministic source-code comparator.

No API key is read from command-line arguments. Set GEMINI_API_KEY in the environment.
Do not commit generated model outputs or credentials.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import sys
import urllib.parse
import urllib.request
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from evidencebound_scenariograph.adapters.ni_stats20 import (
    CARRIAGEWAY_TYPE,
    CASUALTY_CLASS,
    COLLISION_SEVERITY,
    JUNCTION_CONTROL,
    JUNCTION_DETAIL,
    LIGHT_CONDITIONS,
    PEDESTRIAN_LOCATION,
    PEDESTRIAN_MOVEMENT,
    ROAD_SURFACE,
    VEHICLE_LOCATION,
    VEHICLE_MANOEUVRE,
    VEHICLE_TYPE,
    WEATHER_CONDITIONS,
    NIStats20Record,
    normalize_ni_stats20_case,
)

CKAN_ENDPOINT = "https://admin.opendatani.gov.uk/api/3/action/datastore_search"
RESOURCES = {
    "collisions": "b9d5267a-c648-47c1-b97a-dddcf487958b",
    "vehicles": "eba09f3d-74ef-41cf-814c-dfda8cf1eba3",
    "casualties": "c092f66c-f877-4b6d-84b9-50d8f61065b8",
}
MODEL_DEFAULT = "gemini-3.6-flash"
PROMPT_VERSION = "psni-codebook-extraction/0.1"
DEFAULT_CASES = 16
MAX_SOURCE_ROWS = 10_000

EVALUATED_FIELDS = (
    "actor_class",
    "harmonized_event_class",
    "collision_severity",
    "carriageway_type",
    "light_conditions",
    "weather_conditions",
    "road_surface",
    "vehicle_type",
    "vehicle_manoeuvre",
    "pedestrian_movement",
)

SOURCE_KEYS_BY_FIELD = {
    "actor_class": {"casualty.c_class"},
    "harmonized_event_class": {"casualty.c_class", "casualty.c_move", "collision.a_type"},
    "collision_severity": {"collision.a_type"},
    "carriageway_type": {"collision.a_ctype"},
    "light_conditions": {"collision.a_light", "collision.a_type"},
    "weather_conditions": {"collision.a_weat", "collision.a_type"},
    "road_surface": {"collision.a_roadsc", "collision.a_type"},
    "vehicle_type": {"vehicle.v_type", "casualty.v_id"},
    "vehicle_manoeuvre": {"vehicle.v_man", "casualty.v_id"},
    "pedestrian_movement": {"casualty.c_move", "collision.a_type"},
}

ALLOWED_SOURCE_FIELDS = {
    "collision.a_type",
    "collision.a_ctype",
    "collision.a_speed",
    "collision.a_jdet",
    "collision.a_jcont",
    "collision.a_light",
    "collision.a_weat",
    "collision.a_roadsc",
    "casualty.c_class",
    "casualty.c_sever",
    "casualty.c_loc",
    "casualty.c_move",
    "casualty.v_id",
    "vehicle.v_type",
    "vehicle.v_man",
    "vehicle.v_loc",
    "source_policy.conditional_recording",
}


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _stable_id(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.isdigit():
        return str(int(text))
    return text


def _code(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(str(value).strip())
    except ValueError:
        return None


def _fetch_resource(resource_id: str) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode({"resource_id": resource_id, "limit": MAX_SOURCE_ROWS})
    request = urllib.request.Request(
        f"{CKAN_ENDPOINT}?{query}",
        headers={"User-Agent": "EvidenceBound-ScenarioGraph-LLM-Holdout/0.1"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("success") is not True:
        raise RuntimeError(f"CKAN query failed for {resource_id}")
    result = payload.get("result", {})
    records = result.get("records", [])
    total = int(result.get("total", len(records)))
    if not isinstance(records, list):
        raise RuntimeError(f"CKAN records are not a list for {resource_id}")
    if total > MAX_SOURCE_ROWS:
        raise RuntimeError(f"resource {resource_id} exceeds deterministic fetch limit")
    return [dict(row) for row in records]


def _selected_packets(case_count: int) -> list[dict[str, Any]]:
    collisions = _fetch_resource(RESOURCES["collisions"])
    vehicles = _fetch_resource(RESOURCES["vehicles"])
    casualties = _fetch_resource(RESOURCES["casualties"])

    collision_by_ref = {_stable_id(row.get("a_ref")): row for row in collisions}
    vehicle_by_key = {
        (_stable_id(row.get("a_ref")), _stable_id(row.get("v_id"))): row for row in vehicles
    }
    eligible = [row for row in casualties if _code(row.get("c_class")) in {5, 7}]
    eligible.sort(
        key=lambda row: (
            _stable_id(row.get("a_ref")).zfill(12),
            _stable_id(row.get("v_id")).zfill(6),
            _stable_id(row.get("c_id")).zfill(6),
        )
    )

    packets: list[dict[str, Any]] = []
    for casualty in eligible:
        ref = _stable_id(casualty.get("a_ref"))
        collision = collision_by_ref.get(ref)
        if collision is None:
            continue
        vehicle_id = _stable_id(casualty.get("v_id"))
        vehicle = vehicle_by_key.get((ref, vehicle_id))
        expected = normalize_ni_stats20_case(collision, vehicle, casualty)
        packet = {
            "case_id": expected.case_id,
            "collision": {
                key: collision.get(key)
                for key in (
                    "a_type",
                    "a_ctype",
                    "a_speed",
                    "a_jdet",
                    "a_jcont",
                    "a_light",
                    "a_weat",
                    "a_roadsc",
                )
            },
            "casualty": {
                key: casualty.get(key)
                for key in ("c_class", "c_sever", "c_loc", "c_move", "v_id")
            },
            "vehicle": None
            if vehicle is None
            else {key: vehicle.get(key) for key in ("v_type", "v_man", "v_loc")},
            "expected": expected,
        }
        packets.append(packet)
        if len(packets) >= case_count:
            break
    if len(packets) != case_count:
        raise RuntimeError(f"requested {case_count} cases but selected {len(packets)}")
    return packets


def _string_codebook(mapping: Mapping[int, str]) -> dict[str, str]:
    return {str(key): value for key, value in sorted(mapping.items())}


def _prompt(packet: Mapping[str, Any]) -> str:
    codebook = {
        "collision.a_type": _string_codebook(COLLISION_SEVERITY),
        "collision.a_ctype": _string_codebook(CARRIAGEWAY_TYPE),
        "collision.a_jdet": _string_codebook(JUNCTION_DETAIL),
        "collision.a_jcont": _string_codebook(JUNCTION_CONTROL),
        "collision.a_light": _string_codebook(LIGHT_CONDITIONS),
        "collision.a_weat": _string_codebook(WEATHER_CONDITIONS),
        "collision.a_roadsc": _string_codebook(ROAD_SURFACE),
        "casualty.c_class": _string_codebook(CASUALTY_CLASS),
        "casualty.c_loc": _string_codebook(PEDESTRIAN_LOCATION),
        "casualty.c_move": _string_codebook(PEDESTRIAN_MOVEMENT),
        "vehicle.v_type": _string_codebook(VEHICLE_TYPE),
        "vehicle.v_man": _string_codebook(VEHICLE_MANOEUVRE),
        "vehicle.v_loc": _string_codebook(VEHICLE_LOCATION),
    }
    evidence = {
        "case_id": packet["case_id"],
        "collision": packet["collision"],
        "casualty": packet["casualty"],
        "vehicle": packet["vehicle"],
    }
    return (
        "You are extracting a validation-scenario record from coded public crash evidence. "
        "Use ONLY the supplied evidence and codebook. Never infer a missing value. "
        "For a slight-injury collision (collision.a_type=3), if junction/light/weather/"
        "road-surface or pedestrian location/movement is missing, use the exact value "
        "not_recorded_for_slight_collision and mark the field uncertain. If the associated "
        "vehicle object is null, use unknown_missing_associated_vehicle_row for vehicle fields "
        "and mark them uncertain. For harmonized_event_class use: pedal cyclist -> "
        "pedal_cyclist_casualty; pedestrian c_move 3 or 5 -> "
        "pedestrian_crossing_masked_by_static_vehicle; c_move 2 or 4 -> pedestrian_crossing; "
        "c_move 6,7,8,9 -> pedestrian_in_carriageway; missing c_move in a slight collision -> "
        "pedestrian_movement_not_recorded_for_slight_collision; otherwise -> "
        "pedestrian_movement_unknown. Return exactly one entry for every requested field. "
        "Each source_fields item must be one of the literal source names used below or "
        "source_policy.conditional_recording. Do not cite URLs, prose, hidden knowledge or "
        "fields that are not present in the packet.\n\n"
        f"REQUESTED_FIELDS={json.dumps(EVALUATED_FIELDS)}\n"
        f"ALLOWED_SOURCE_FIELDS={json.dumps(sorted(ALLOWED_SOURCE_FIELDS))}\n"
        f"CODEBOOK={json.dumps(codebook, sort_keys=True)}\n"
        f"EVIDENCE={json.dumps(evidence, sort_keys=True)}"
    )


def _response_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "case_id": {"type": "string"},
            "fields": {
                "type": "array",
                "minItems": len(EVALUATED_FIELDS),
                "maxItems": len(EVALUATED_FIELDS),
                "items": {
                    "type": "object",
                    "properties": {
                        "field_id": {"type": "string", "enum": list(EVALUATED_FIELDS)},
                        "value": {"type": "string"},
                        "source_fields": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 1,
                        },
                        "uncertain": {"type": "boolean"},
                        "uncertainty_reason": {"type": "string"},
                    },
                    "required": [
                        "field_id",
                        "value",
                        "source_fields",
                        "uncertain",
                        "uncertainty_reason",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["case_id", "fields"],
        "additionalProperties": False,
    }


def _extract_output_text(interaction: Any) -> str:
    output_text = getattr(interaction, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text
    for step in getattr(interaction, "steps", []):
        if getattr(step, "type", None) != "model_output":
            continue
        texts = [
            getattr(item, "text", "")
            for item in getattr(step, "content", [])
            if getattr(item, "type", None) == "text"
        ]
        if texts:
            return "".join(texts)
    raise RuntimeError("Gemini interaction returned no model text")


def _candidate_fields(candidate: Mapping[str, Any]) -> tuple[dict[str, Mapping[str, Any]], list[str]]:
    raw_fields = candidate.get("fields")
    issues: list[str] = []
    if not isinstance(raw_fields, list):
        return {}, ["fields_not_array"]
    mapped: dict[str, Mapping[str, Any]] = {}
    for raw in raw_fields:
        if not isinstance(raw, dict):
            issues.append("field_not_object")
            continue
        field_id = raw.get("field_id")
        if not isinstance(field_id, str) or field_id not in EVALUATED_FIELDS:
            issues.append(f"invalid_field_id:{field_id}")
            continue
        if field_id in mapped:
            issues.append(f"duplicate_field:{field_id}")
            continue
        mapped[field_id] = raw
    for field_id in EVALUATED_FIELDS:
        if field_id not in mapped:
            issues.append(f"missing_field:{field_id}")
    return mapped, issues


def score_candidate(expected: NIStats20Record, candidate: Mapping[str, Any]) -> dict[str, Any]:
    expected_values = dict(expected.fields)
    predicted, structural_issues = _candidate_fields(candidate)
    if candidate.get("case_id") != expected.case_id:
        structural_issues.append("case_id_mismatch")

    exact_fields = 0
    valid_ref_fields = 0
    source_covered_fields = 0
    expected_uncertain = 0
    expected_uncertain_correct = 0
    definite_fields = 0
    false_uncertain = 0
    semantic_errors: list[str] = []
    invalid_evidence_refs: list[str] = []
    source_policy_expected = 0
    source_policy_no_completion = 0
    missing_vehicle_expected = 0
    missing_vehicle_no_completion = 0

    for field_id in EVALUATED_FIELDS:
        raw = predicted.get(field_id)
        if raw is None:
            semantic_errors.append(f"{field_id}:missing")
            continue
        predicted_value = raw.get("value")
        expected_value = expected_values[field_id]
        if predicted_value == expected_value:
            exact_fields += 1
        else:
            semantic_errors.append(
                f"{field_id}:expected={expected_value!r}:observed={predicted_value!r}"
            )

        refs = raw.get("source_fields")
        refs_valid = isinstance(refs, list) and bool(refs) and all(
            isinstance(ref, str) and ref in ALLOWED_SOURCE_FIELDS for ref in refs
        )
        if refs_valid:
            valid_ref_fields += 1
            expected_sources = SOURCE_KEYS_BY_FIELD[field_id]
            if any(ref in expected_sources for ref in refs):
                source_covered_fields += 1
        else:
            invalid_evidence_refs.append(field_id)

        is_expected_uncertain = field_id in expected.uncertain_fields
        model_uncertain = raw.get("uncertain") is True
        if is_expected_uncertain:
            expected_uncertain += 1
            if model_uncertain:
                expected_uncertain_correct += 1
        else:
            definite_fields += 1
            if model_uncertain:
                false_uncertain += 1

        if expected_value == "not_recorded_for_slight_collision":
            source_policy_expected += 1
            if predicted_value == expected_value and model_uncertain:
                source_policy_no_completion += 1
        if expected_value == "unknown_missing_associated_vehicle_row":
            missing_vehicle_expected += 1
            if predicted_value == expected_value and model_uncertain:
                missing_vehicle_no_completion += 1

    structural_decision = "VERIFIED_CANDIDATE"
    if structural_issues or invalid_evidence_refs:
        structural_decision = "BLOCKED"
    elif any(raw.get("uncertain") is True for raw in predicted.values()):
        structural_decision = "REVIEW_REQUIRED"

    benchmark_decision = structural_decision
    if benchmark_decision != "BLOCKED" and semantic_errors:
        benchmark_decision = "REVIEW_REQUIRED_COMPARATOR_MISMATCH"
    elif benchmark_decision == "VERIFIED_CANDIDATE" and not semantic_errors:
        benchmark_decision = "VERIFIED_AGAINST_HELDOUT_COMPARATOR"

    return {
        "case_id": expected.case_id,
        "candidate_sha256": _sha256(candidate),
        "exact_fields": exact_fields,
        "total_fields": len(EVALUATED_FIELDS),
        "valid_ref_fields": valid_ref_fields,
        "source_covered_fields": source_covered_fields,
        "expected_uncertain": expected_uncertain,
        "expected_uncertain_correct": expected_uncertain_correct,
        "definite_fields": definite_fields,
        "false_uncertain": false_uncertain,
        "source_policy_expected": source_policy_expected,
        "source_policy_no_completion": source_policy_no_completion,
        "missing_vehicle_expected": missing_vehicle_expected,
        "missing_vehicle_no_completion": missing_vehicle_no_completion,
        "semantic_errors": semantic_errors,
        "structural_issues": structural_issues,
        "invalid_evidence_refs": invalid_evidence_refs,
        "structural_trust_decision": structural_decision,
        "benchmark_evaluation_decision": benchmark_decision,
    }


def _milli(numerator: int, denominator: int) -> int:
    if denominator == 0:
        return 1000
    return (numerator * 1000) // denominator


def _aggregate(scores: list[Mapping[str, Any]]) -> dict[str, int]:
    total_fields = sum(int(score["total_fields"]) for score in scores)
    exact_fields = sum(int(score["exact_fields"]) for score in scores)
    valid_ref_fields = sum(int(score["valid_ref_fields"]) for score in scores)
    source_covered_fields = sum(int(score["source_covered_fields"]) for score in scores)
    expected_uncertain = sum(int(score["expected_uncertain"]) for score in scores)
    expected_uncertain_correct = sum(
        int(score["expected_uncertain_correct"]) for score in scores
    )
    definite_fields = sum(int(score["definite_fields"]) for score in scores)
    false_uncertain = sum(int(score["false_uncertain"]) for score in scores)
    source_policy_expected = sum(int(score["source_policy_expected"]) for score in scores)
    source_policy_no_completion = sum(
        int(score["source_policy_no_completion"]) for score in scores
    )
    missing_vehicle_expected = sum(int(score["missing_vehicle_expected"]) for score in scores)
    missing_vehicle_no_completion = sum(
        int(score["missing_vehicle_no_completion"]) for score in scores
    )
    exact_cases = sum(1 for score in scores if not score["semantic_errors"])
    structurally_blocked = sum(
        1 for score in scores if score["structural_trust_decision"] == "BLOCKED"
    )
    return {
        "field_exact_accuracy_milli": _milli(exact_fields, total_fields),
        "case_exact_match_milli": _milli(exact_cases, len(scores)),
        "evidence_reference_validity_milli": _milli(valid_ref_fields, total_fields),
        "expected_source_coverage_milli": _milli(source_covered_fields, total_fields),
        "expected_uncertainty_recall_milli": _milli(
            expected_uncertain_correct, expected_uncertain
        ),
        "false_uncertainty_rate_milli": _milli(false_uncertain, definite_fields),
        "source_policy_no_completion_milli": _milli(
            source_policy_no_completion, source_policy_expected
        ),
        "missing_vehicle_no_completion_milli": _milli(
            missing_vehicle_no_completion, missing_vehicle_expected
        ),
        "structurally_blocked_case_rate_milli": _milli(structurally_blocked, len(scores)),
    }


def run_benchmark(*, model: str, case_count: int) -> dict[str, Any]:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    from google import genai  # type: ignore[import-not-found]

    client = genai.Client(api_key=api_key)
    packets = _selected_packets(case_count)
    schema = _response_schema()
    scores: list[dict[str, Any]] = []
    total_input_tokens = 0
    total_output_tokens = 0
    total_thought_tokens = 0

    for packet in packets:
        interaction = client.interactions.create(
            model=model,
            input=_prompt(packet),
            store=False,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": schema,
            },
        )
        candidate = json.loads(_extract_output_text(interaction))
        if not isinstance(candidate, dict):
            raise RuntimeError("Gemini structured output is not an object")
        expected = packet["expected"]
        if not isinstance(expected, NIStats20Record):
            raise RuntimeError("internal expected comparator type mismatch")
        score = score_candidate(expected, candidate)
        scores.append(score)
        usage = getattr(interaction, "usage", None)
        if usage is not None:
            total_input_tokens += int(getattr(usage, "total_input_tokens", 0) or 0)
            total_output_tokens += int(getattr(usage, "total_output_tokens", 0) or 0)
            total_thought_tokens += int(getattr(usage, "total_thought_tokens", 0) or 0)

    body = {
        "schema": "evidencebound-ai-boost-challenge4-live-llm-holdout/0.1",
        "provider": "google-gemini-api",
        "model": model,
        "sdk": f"google-genai/{importlib.metadata.version('google-genai')}",
        "prompt_version": PROMPT_VERSION,
        "source": "PSNI Northern Ireland Police Recorded Injury RTC 2024",
        "cases": case_count,
        "evaluated_fields": list(EVALUATED_FIELDS),
        "metrics": _aggregate(scores),
        "usage": {
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_thought_tokens": total_thought_tokens,
        },
        "case_scores": scores,
        "claim_boundary": (
            "Live schema-constrained model extraction benchmark on an independent public coded-"
            "evidence holdout. Semantic mismatches are identified with a held-out deterministic "
            "comparator for evaluation only; the production trust gate cannot infer semantic "
            "truth merely from valid provenance. Results do not establish simulator validity, "
            "automotive production safety, homologation or Challenge Owner data performance."
        ),
    }
    return {"body": body, "sha256": _sha256(body)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=MODEL_DEFAULT)
    parser.add_argument("--cases", type=int, default=DEFAULT_CASES)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.cases < 1 or args.cases > 64:
        raise SystemExit("--cases must be between 1 and 64")

    receipt = run_benchmark(model=args.model, case_count=args.cases)
    rendered = json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False)
    if args.output is not None:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
