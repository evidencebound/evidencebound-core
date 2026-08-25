from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_current_public_branding_uses_evidencebound_org() -> None:
    paths = [ROOT / "README.md", ROOT / "pyproject.toml"]
    paths.extend((ROOT / "site").rglob("*.html"))
    paths.extend((ROOT / "site").rglob("*.json"))

    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)

    assert "https://github.com/moneyparking" not in combined
    assert "https://github.com/evidencebound/evidencebound-core" in combined
