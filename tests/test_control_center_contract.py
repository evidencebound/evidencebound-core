import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "control/CONTROL.yaml",
    "control/ACCEPTANCE.md",
    "control/AUTHORITY.md",
    "control/knowledge_delta.schema.json",
    "tools/validate_control_center.py",
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


def _control() -> dict[str, object]:
    return json.loads((ROOT / "control/CONTROL.yaml").read_text(encoding="utf-8"))


def test_control_center_surface_exists() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    assert missing == [], f"missing Control Center surface: {missing}"


def test_control_center_selects_one_progressive_route() -> None:
    control = _control()
    assert control["project"] == "EvidenceBound Core"
    assert control["visibility"] == "public"
    context = control["context_selection"]
    assert context["mode"] == "progressive_disclosure"
    assert context["primary_route_count"] == 1
    assert context["cross_route_requires_recorded_dependency"] is True
    assert set(control["routes"]) == REQUIRED_ROUTES


def test_route_sources_are_existing_local_paths() -> None:
    control = _control()
    for route in control["routes"].values():
        for path in route["read_first"]:
            assert "://" not in path
            assert ".." not in Path(path).parts
            assert (ROOT / path).is_file(), path


def test_consequential_effects_are_deny_by_default() -> None:
    gates = _control()["authority"]["external_effects"]
    assert set(gates) == REQUIRED_GATES
    assert all(gate["default"] == "DENY" for gate in gates.values())


def test_public_control_artifacts_do_not_identify_external_private_repositories() -> None:
    paths = [
        ROOT / "control/CONTROL.yaml",
        ROOT / "control/ACCEPTANCE.md",
        ROOT / "control/AUTHORITY.md",
        ROOT / "evidence/control-center/INDEX.md",
    ]
    delta_dir = ROOT / "evidence/control-center/knowledge_deltas"
    paths.extend(sorted(delta_dir.glob("*.json")))
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths).lower()
    forbidden = ("github.com/", "api.github.com/", "raw.githubusercontent.com/")
    assert all(token not in text for token in forbidden)


def test_bootstrap_knowledge_delta_is_machine_readable() -> None:
    deltas = sorted((ROOT / "evidence/control-center/knowledge_deltas").glob("*.json"))
    assert deltas
    payload = json.loads(deltas[0].read_text(encoding="utf-8"))
    assert payload["project"] == "EvidenceBound Core"
    assert payload["result"] in {"PASS", "BLOCKED", "FAIL"}
    assert payload["verification"]


def test_validator_reports_pass() -> None:
    result = subprocess.run(
        [sys.executable, "tools/validate_control_center.py"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["status"] == "PASS"
    assert report["routes_checked"] == len(REQUIRED_ROUTES)
    assert report["approval_gates_checked"] == len(REQUIRED_GATES)
    assert report["knowledge_deltas_checked"] >= 1
    assert report["errors"] == []
