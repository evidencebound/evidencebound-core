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


def test_control_center_surface_exists() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    assert missing == [], f"missing Control Center surface: {missing}"
