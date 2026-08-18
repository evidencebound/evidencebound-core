"""Write current SPARK OpenSCENARIO XML artifacts for schema validation."""
from __future__ import annotations

from pathlib import Path

from evidencebound_scenariograph import load_fixture, run_pipeline

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
OUTPUT = HERE / "generated_xosc"


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name in ("nhtsa_vicis_991.json", "nhtsa_vicis_1027.json"):
        fixture = load_fixture(FIXTURES / name)
        artifact = run_pipeline(fixture).openscenario
        target = OUTPUT / f"{fixture.case_id}.xosc"
        target.write_text(artifact.xml + "\n", encoding="utf-8")
        print(f"wrote {target}")


if __name__ == "__main__":
    main()
