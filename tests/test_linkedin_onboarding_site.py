from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def _read(relative: str) -> str:
    return (SITE / relative).read_text(encoding="utf-8")


def test_privacy_policy_is_canonical_and_contactable() -> None:
    path = SITE / "privacy" / "index.html"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "EvidenceBound Privacy Policy" in text
    assert "ruslan@evidencebound.org" in text
    assert "LinkedIn" in text
    assert "GitHub Actions" in text
    assert "Vercel" in text
    assert "access token" in text.lower()
    assert "private messages" in text.lower()


def test_callback_surface_exists_and_never_reflects_query_parameters() -> None:
    path = SITE / "linkedin" / "oauth" / "callback" / "index.html"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "LinkedIn OAuth Callback" in text
    assert "ruslan@evidencebound.org" in text
    lowered = text.lower()
    assert "<script" not in lowered
    assert "location.search" not in lowered
    assert "urlsearchparams" not in lowered
    assert "document.location" not in lowered
    assert "window.location" not in lowered


def test_home_footer_links_to_privacy_and_linkedin_callback_surface() -> None:
    text = _read("index.html")
    assert 'href="/privacy/"' in text
    assert 'href="/linkedin/oauth/callback/"' in text


def test_public_onboarding_pages_contain_no_secret_values() -> None:
    combined = "\n".join(
        [
            _read("privacy/index.html"),
            _read("linkedin/oauth/callback/index.html"),
        ]
    )
    forbidden = (
        "LINKEDIN_CLIENT_SECRET=",
        "LINKEDIN_ACCESS_TOKEN=",
        "LINKEDIN_REFRESH_TOKEN=",
        "Authorization: Bearer ",
        "AQV",
    )
    for marker in forbidden:
        assert marker not in combined
