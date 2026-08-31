import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
WEBMCP = SITE / "webmcp"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_webmcp_judge_surface_and_modules_exist() -> None:
    required = (
        "index.html",
        "styles.css",
        "control-core.mjs",
        "webmcp-adapter.mjs",
        "app.mjs",
    )
    for name in required:
        assert (WEBMCP / name).is_file(), name


def test_webmcp_page_uses_only_self_hosted_module_script() -> None:
    html = _read(WEBMCP / "index.html")
    scripts = re.findall(r'<script\b[^>]*src="([^"]+)"[^>]*>', html, flags=re.IGNORECASE)
    assert scripts == ["/webmcp/app.mjs"]
    assert all(not src.startswith(("http://", "https://", "//")) for src in scripts)
    assert '<script type="module" src="/webmcp/app.mjs"></script>' in html


def test_judge_surface_makes_control_states_and_demo_boundary_visible() -> None:
    html = _read(WEBMCP / "index.html")
    for state in ("AUTHORIZED", "HUMAN_REQUIRED", "STALE", "INVALIDATED", "BLOCKED"):
        assert state in html
    assert "Capability follows current authority." in html
    assert "controlled demo" in html.lower()
    assert "no external deployment" in html.lower()
    assert "WEBMCP_UNAVAILABLE" in html


def test_human_authority_mutations_are_ui_only_not_webmcp_tools() -> None:
    adapter = _read(WEBMCP / "webmcp-adapter.mjs")
    registered_names = re.findall(r"name:\s*'([^']+)'", adapter)
    assert set(registered_names) == {
        "inspect_release_control",
        "request_release_authority",
        "list_control_receipts",
        "execute_authorized_release",
    }
    forbidden = re.compile(r"grant|approve|revoke|correct|restore", re.IGNORECASE)
    assert not any(forbidden.search(name) for name in registered_names)


def test_vercel_csp_allows_only_self_hosted_scripts_and_preserves_fail_closed_headers() -> None:
    config = json.loads(_read(SITE / "vercel.json"))
    header_sets = config["headers"]
    global_headers = next(item["headers"] for item in header_sets if item["source"] == "/(.*)")
    headers = {item["key"].lower(): item["value"] for item in global_headers}
    csp = headers["content-security-policy"]
    assert "script-src 'self'" in csp
    assert "'unsafe-inline'" not in csp
    assert "'unsafe-eval'" not in csp
    assert "connect-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp
    assert "base-uri 'self'" in csp
    assert "form-action 'self'" in csp
    assert headers["x-content-type-options"] == "nosniff"
    assert headers["x-frame-options"] == "DENY"


def test_webmcp_app_has_no_network_or_secret_dependency() -> None:
    combined = "\n".join(
        _read(WEBMCP / name)
        for name in ("control-core.mjs", "webmcp-adapter.mjs", "app.mjs")
    )
    assert "fetch(" not in combined
    assert "XMLHttpRequest" not in combined
    assert "WebSocket" not in combined
    assert "Authorization" not in combined
    assert "Bearer " not in combined
    assert "process.env" not in combined
