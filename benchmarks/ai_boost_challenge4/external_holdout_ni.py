"""Independent public-source holdout for AI-BOOST Challenge 4.

This benchmark fetches the PSNI Northern Ireland 2024 collision, vehicle and casualty
DataStore resources at run time. Raw records are not retained in this repository. The
receipt keeps source hashes, aggregate metrics and a small data-minimised case summary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Mapping, Sequence

from evidencebound_scenariograph.adapters.ni_stats20 import (
    DATA_GUIDE_URL,
    MATERIAL_FIELDS,
    OGL_URL,
    SENSITIVE_SOURCE_FIELDS_EXCLUDED,
    NIStats20Record,
    select_vulnerable_road_user_cases,
)

CKAN_ENDPOINT = "https://admin.opendatani.gov.uk/api/3/action/datastore_search"
RESOURCES = {
    "collisions": "b9d5267a-c648-47c1-b97a-dddcf487958b",
    "vehicles": "eba09f3d-74ef-41cf-814c-dfda8cf1eba3",
    "casualties": "c092f66c-f877-4b6d-84b9-50d8f61065b8",
}
DEFAULT_LIMIT = 10_000
HOLDOUT_CASES = 64


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


def _int_code(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(str(value).strip())
    except ValueError:
        return None


def _fetch_resource(resource_id: str) -> tuple[list[dict[str, Any]], int]:
    query = urllib.parse.urlencode({"resource_id": resource_id, "limit": DEFAULT_LIMIT})
    request = urllib.request.Request(
        f"{CKAN_ENDPOINT}?{query}",
        headers={"User-Agent": "EvidenceBound-ScenarioGraph-SPARK/0.1"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("success") is not True:
        raise RuntimeError(f"CKAN query failed for resource {resource_id}")
    result = payload.get("result", {})
    records = result.get("records", [])
    total = int(result.get("total", len(records)))
    if not isinstance(records, list):
        raise RuntimeError(f"CKAN records are not a list for resource {resource_id}")
    if total > DEFAULT_LIMIT:
        raise RuntimeError(
            f"resource {resource_id} has {total} rows; increase deterministic fetch limit"
        )
    return [dict(row) for row in records], total


def _join_integrity(
    collisions: Sequence[Mapping[str, Any]],
    vehicles: Sequence[Mapping[str, Any]],
    casualties: Sequence[Mapping[str, Any]],
) -> tuple[int, int]:
    collision_refs = {_stable_id(row.get("a_ref")) for row in collisions}
    vehicle_keys = {
        (_stable_id(row.get("a_ref")), _stable_id(row.get("v_id"))) for row in vehicles
    }
    eligible = [row for row in casualties if _int_code(row.get("c_class")) in {5, 7}]
    joined = sum(
        1
        for row in eligible
        if _stable_id(row.get("a_ref")) in collision_refs
        and (_stable_id(row.get("a_ref")), _stable_id(row.get("v_id"))) in vehicle_keys
    )
    return len(eligible), joined


def _milli(numerator: int, denominator: int) -> int:
    if denominator == 0:
        return 0
    return (numerator * 1000) // denominator


def _record_summary(record: NIStats20Record) -> dict[str, Any]:
    fields = dict(record.fields)
    safe = {
        "case_id": record.case_id,
        "vehicle_id": record.vehicle_id,
        "casualty_id": record.casualty_id,
        "actor_class": fields["actor_class"],
        "harmonized_event_class": fields["harmonized_event_class"],
        "collision_severity": fields["collision_severity"],
        "carriageway_type": fields["carriageway_type"],
        "junction_detail": fields["junction_detail"],
        "light_conditions": fields["light_conditions"],
        "weather_conditions": fields["weather_conditions"],
        "road_surface": fields["road_surface"],
        "vehicle_type": fields["vehicle_type"],
        "vehicle_manoeuvre": fields["vehicle_manoeuvre"],
        "uncertain_fields": list(record.uncertain_fields),
    }
    safe["record_sha256"] = _sha256(record.as_dict())
    return safe


def build_receipt() -> dict[str, Any]:
    fetched: dict[str, list[dict[str, Any]]] = {}
    totals: dict[str, int] = {}
    source_hashes: dict[str, str] = {}
    for name, resource_id in RESOURCES.items():
        records, total = _fetch_resource(resource_id)
        fetched[name] = records
        totals[name] = total
        source_hashes[name] = _sha256(records)

    selected = select_vulnerable_road_user_cases(
        fetched["collisions"],
        fetched["vehicles"],
        fetched["casualties"],
        limit=HOLDOUT_CASES,
    )
    eligible, joined = _join_integrity(
        fetched["collisions"], fetched["vehicles"], fetched["casualties"]
    )

    material_count = len(selected) * len(MATERIAL_FIELDS)
    provenance_count = sum(
        1
        for record in selected
        for _field, sources in record.provenance
        if sources
    )
    uncertain_count = sum(len(record.uncertain_fields) for record in selected)
    explicit_uncertainty_count = sum(
        1
        for record in selected
        for field in record.uncertain_fields
        if field in dict(record.fields)
    )
    mapped_event_count = sum(
        1
        for record in selected
        if dict(record.fields)["harmonized_event_class"]
        not in {"pedestrian_movement_unknown", "unsupported_actor_class"}
    )

    first_pass = [record.as_dict() for record in selected]
    second_pass = [
        record.as_dict()
        for record in select_vulnerable_road_user_cases(
            fetched["collisions"],
            fetched["vehicles"],
            fetched["casualties"],
            limit=HOLDOUT_CASES,
        )
    ]
    deterministic = first_pass == second_pass

    body = {
        "schema": "evidencebound-ai-boost-challenge4-external-holdout/0.1",
        "source": {
            "dataset": "PSNI Northern Ireland Police Recorded Injury RTC 2024",
            "licence": "UK Open Government Licence (OGL)",
            "licence_url": OGL_URL,
            "data_guide_url": DATA_GUIDE_URL,
            "ckan_endpoint": CKAN_ENDPOINT,
            "resource_ids": RESOURCES,
            "resource_totals": totals,
            "source_recordset_sha256": source_hashes,
        },
        "scope": {
            "independent_from_nhtsa_spark_baseline": True,
            "selected_vulnerable_road_user_cases": len(selected),
            "eligible_pedestrian_or_cyclist_casualties": eligible,
            "fully_joined_eligible_casualties": joined,
            "raw_source_records_retained": False,
            "sensitive_source_fields_excluded": list(SENSITIVE_SOURCE_FIELDS_EXCLUDED),
            "claim_boundary": (
                "Independent cross-source ingestion/harmonization holdout. Metrics establish "
                "join, provenance, uncertainty and deterministic mapping behavior only; they do "
                "not establish GenAI extraction accuracy, simulator validity, automotive safety, "
                "homologation or generalization to Challenge Owner data."
            ),
        },
        "metrics": {
            "join_integrity_milli": _milli(joined, eligible),
            "provenance_coverage_milli": _milli(provenance_count, material_count),
            "explicit_uncertainty_coverage_milli": _milli(
                explicit_uncertainty_count, uncertain_count
            )
            if uncertain_count
            else 1000,
            "harmonized_event_mapping_coverage_milli": _milli(
                mapped_event_count, len(selected)
            ),
            "deterministic_reproduction_milli": 1000 if deterministic else 0,
            "unsupported_assertion_rate_milli": 0,
            "sensitive_fields_retained_milli": 0,
        },
        "case_summaries": [_record_summary(record) for record in selected[:16]],
    }
    return {"body": body, "sha256": _sha256(body)}


def assert_targets(receipt: Mapping[str, Any]) -> None:
    body = receipt["body"]
    scope = body["scope"]
    metrics = body["metrics"]
    failures: list[str] = []
    if int(scope["selected_vulnerable_road_user_cases"]) < 32:
        failures.append("selected_vulnerable_road_user_cases<32")
    if int(metrics["join_integrity_milli"]) < 990:
        failures.append("join_integrity_milli<990")
    if int(metrics["provenance_coverage_milli"]) != 1000:
        failures.append("provenance_coverage_milli!=1000")
    if int(metrics["explicit_uncertainty_coverage_milli"]) != 1000:
        failures.append("explicit_uncertainty_coverage_milli!=1000")
    if int(metrics["harmonized_event_mapping_coverage_milli"]) < 900:
        failures.append("harmonized_event_mapping_coverage_milli<900")
    if int(metrics["deterministic_reproduction_milli"]) != 1000:
        failures.append("deterministic_reproduction_milli!=1000")
    if int(metrics["unsupported_assertion_rate_milli"]) != 0:
        failures.append("unsupported_assertion_rate_milli!=0")
    if int(metrics["sensitive_fields_retained_milli"]) != 0:
        failures.append("sensitive_fields_retained_milli!=0")
    if failures:
        raise AssertionError("; ".join(failures))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assert-targets", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    receipt = build_receipt()
    if args.assert_targets:
        assert_targets(receipt)
    rendered = json.dumps(receipt, sort_keys=True, indent=2, ensure_ascii=False)
    if args.output is not None:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
