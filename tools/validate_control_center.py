from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "control/CONTROL.yaml",
    "control/ACCEPTANCE.md",
    "control/AUTHORITY.md",
    "control/knowledge_delta.schema.json",
    "evidence/control-center/INDEX.md",
)
REQUIRED_ROUTES = {
    "core_runtime_and_invariants",
    "release_and_supply_chain",
    "adoption_and_security",
    "webmcp_public_surface",
    "public_benchmark_interface",
}
REQUIRED_GATES = {
    "publication",
    "deployment",
    "registry_publication",
    "external_message",
    "spend_or_procurement",
    "destructive_or_irreversible",
}
DELTA_FIELDS = {
    "session_id",
    "at_utc",
    "project",
    "objective",
    "result",
    "new_facts",
    "corrected_assumptions",
    "decisions",
    "failed_approaches",
    "verification",
    "authoritative_updates",
}
ACCEPTANCE_MARKERS = (
    "Scenario A — Route-safe progressive disclosure",
    "Scenario B — No unverified completion",
    "Scenario C — Public/private isolation",
    "Scenario D — Authority-gated external effects",
    "Scenario E — Verified knowledge promotion",
)
PUBLIC_SCAN_PATHS = (
    "control/CONTROL.yaml",
    "control/ACCEPTANCE.md",
    "control/AUTHORITY.md",
    "evidence/control-center/INDEX.md",
)
FORBIDDEN_EXTERNAL_LOCATORS = (
    "github.com/",
    "api.github.com/",
    "raw.githubusercontent.com/",
)


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON-compatible document {path.relative_to(ROOT)}: {exc}")
        return None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _local_file(path_value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(path_value, str) or not path_value:
        errors.append(f"{label} must be a non-empty local path")
        return
    path = Path(path_value)
    if path.is_absolute() or "://" in path_value or ".." in path.parts:
        errors.append(f"{label} is not a safe local path: {path_value}")
        return
    if not (ROOT / path).is_file():
        errors.append(f"{label} does not exist: {path_value}")


def _validate_delta(payload: Any, path: Path, errors: list[str]) -> None:
    label = str(path.relative_to(ROOT))
    if not isinstance(payload, dict):
        errors.append(f"{label} must contain an object")
        return
    keys = set(payload)
    if keys != DELTA_FIELDS:
        errors.append(f"{label} fields mismatch: {sorted(keys ^ DELTA_FIELDS)}")
    if payload.get("project") != "EvidenceBound Core":
        errors.append(f"{label} project must be EvidenceBound Core")
    if payload.get("result") not in {"PASS", "BLOCKED", "FAIL"}:
        errors.append(f"{label} has invalid result")
    for key in ("session_id", "at_utc", "objective"):
        if not isinstance(payload.get(key), str) or not payload.get(key):
            errors.append(f"{label} {key} must be a non-empty string")
    for key in (
        "new_facts",
        "corrected_assumptions",
        "decisions",
        "failed_approaches",
        "verification",
        "authoritative_updates",
    ):
        if not isinstance(payload.get(key), list):
            errors.append(f"{label} {key} must be an array")
    verification = payload.get("verification")
    if isinstance(verification, list):
        for index, item in enumerate(verification):
            if not isinstance(item, dict):
                errors.append(f"{label} verification[{index}] must be an object")
                continue
            for field in ("kind", "source_or_command", "status"):
                if not isinstance(item.get(field), str) or not item.get(field):
                    errors.append(
                        f"{label} verification[{index}].{field} must be a non-empty string"
                    )


def validate() -> dict[str, Any]:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    control_path = ROOT / "control/CONTROL.yaml"
    schema_path = ROOT / "control/knowledge_delta.schema.json"
    control = _load_json(control_path, errors) if control_path.is_file() else None
    schema = _load_json(schema_path, errors) if schema_path.is_file() else None

    routes_checked = 0
    gates_checked = 0
    if isinstance(control, dict):
        if control.get("project") != "EvidenceBound Core":
            errors.append("control project must be EvidenceBound Core")
        if control.get("visibility") != "public":
            errors.append("control visibility must be public")
        if control.get("bootstrap") != [
            "control/CONTROL.yaml",
            "control/ACCEPTANCE.md",
        ]:
            errors.append("bootstrap must start with Control Center then executable acceptance")
        context = control.get("context_selection")
        if not isinstance(context, dict):
            errors.append("context_selection must be an object")
        else:
            if context.get("mode") != "progressive_disclosure":
                errors.append("context selection must use progressive_disclosure")
            if context.get("primary_route_count") != 1:
                errors.append("exactly one primary context route is required")
            if context.get("cross_route_requires_recorded_dependency") is not True:
                errors.append("cross-route reads must require a recorded dependency")
        routes = control.get("routes")
        if not isinstance(routes, dict) or set(routes) != REQUIRED_ROUTES:
            errors.append("Control Center routes do not match required public routes")
        else:
            routes_checked = len(routes)
            for route_name, route in routes.items():
                if not isinstance(route, dict):
                    errors.append(f"route {route_name} must be an object")
                    continue
                read_first = route.get("read_first")
                if not isinstance(read_first, list) or not read_first:
                    errors.append(f"route {route_name} requires read_first paths")
                    continue
                for index, source in enumerate(read_first):
                    _local_file(source, f"routes.{route_name}.read_first[{index}]", errors)
        authority = control.get("authority")
        gates = authority.get("external_effects") if isinstance(authority, dict) else None
        if not isinstance(gates, dict) or set(gates) != REQUIRED_GATES:
            errors.append("external-effect gates do not match the required deny-by-default set")
        else:
            gates_checked = len(gates)
            for gate_name, gate in gates.items():
                if not isinstance(gate, dict) or gate.get("default") != "DENY":
                    errors.append(f"authority gate {gate_name} must default to DENY")
        objective = control.get("current_objective")
        if isinstance(objective, dict):
            _local_file(objective.get("canonical_owner"), "current objective owner", errors)
        else:
            errors.append("current_objective must be an object")

    if isinstance(schema, dict):
        if schema.get("type") != "object":
            errors.append("knowledge delta schema must describe an object")
        if set(schema.get("required", [])) != DELTA_FIELDS:
            errors.append("knowledge delta schema required fields do not match the contract")
        properties = schema.get("properties")
        project_schema = properties.get("project") if isinstance(properties, dict) else None
        if not isinstance(project_schema, dict) or project_schema.get("const") != "EvidenceBound Core":
            errors.append("knowledge delta schema must bind project identity")
    elif schema_path.is_file():
        errors.append("knowledge delta schema must contain an object")

    acceptance_path = ROOT / "control/ACCEPTANCE.md"
    if acceptance_path.is_file():
        acceptance = acceptance_path.read_text(encoding="utf-8")
        for marker in ACCEPTANCE_MARKERS:
            if marker not in acceptance:
                errors.append(f"acceptance marker missing: {marker}")

    scan_paths = [ROOT / relative for relative in PUBLIC_SCAN_PATHS]
    delta_dir = ROOT / "evidence/control-center/knowledge_deltas"
    delta_paths = sorted(delta_dir.glob("*.json")) if delta_dir.is_dir() else []
    scan_paths.extend(delta_paths)
    for path in scan_paths:
        if not path.is_file():
            continue
        lowered = path.read_text(encoding="utf-8").lower()
        for token in FORBIDDEN_EXTERNAL_LOCATORS:
            if token in lowered:
                errors.append(
                    f"public Control Center artifact contains external repository locator: "
                    f"{path.relative_to(ROOT)}"
                )
                break

    for path in delta_paths:
        payload = _load_json(path, errors)
        _validate_delta(payload, path, errors)
    if not delta_paths:
        errors.append("at least one persisted knowledge delta is required")

    hashes = {}
    for relative in (
        "control/CONTROL.yaml",
        "control/ACCEPTANCE.md",
        "control/knowledge_delta.schema.json",
    ):
        path = ROOT / relative
        if path.is_file():
            hashes[relative] = _sha256(path)

    return {
        "status": "PASS" if not errors else "FAIL",
        "project": "EvidenceBound Core",
        "routes_checked": routes_checked,
        "approval_gates_checked": gates_checked,
        "knowledge_deltas_checked": len(delta_paths),
        "hashes": hashes,
        "errors": errors,
    }


def main() -> int:
    report = validate()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
