from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for key, value in attrs:
            if key == "href" and value:
                self.hrefs.append(value)


def read(path: str) -> str:
    return (SITE / path).read_text(encoding="utf-8")


def test_required_routes_exist() -> None:
    required = [
        "index.html",
        "assurance/index.html",
        "research/index.html",
        "research/deterministic-control-plane-for-ai-agents/index.html",
        "research/audit-evidence-for-high-stakes-ai/index.html",
        "research/verify-the-algorithm-not-the-outcome/index.html",
        "case-studies/signalreview/index.html",
        "identity/ruslan-vrublevskyi.json",
        "styles.css",
        "vercel.json",
    ]
    missing = [path for path in required if not (SITE / path).is_file()]
    assert not missing, f"missing site files: {missing}"


def test_homepage_has_safe_ai_assurance_positioning() -> None:
    html = read("index.html")
    for phrase in [
        "AI Safety Assurance",
        "Human Control Plane",
        "EvidenceBound Core",
        "Early-stage research",
        "no production customers claimed",
        "not a certification",
    ]:
        assert phrase.lower() in html.lower(), phrase
    assert "guarantees compliance" not in html.lower()
    assert "guarantees safety" not in html.lower()


def test_assurance_page_has_framework_mappings_and_boundaries() -> None:
    html = read("assurance/index.html")
    for phrase in [
        "NIST AI RMF",
        "GOVERN",
        "MAP",
        "MEASURE",
        "MANAGE",
        "ISO/IEC 42001",
        "EU AI Act",
        "not ISO certification",
        "not legal advice",
        "not a conformity assessment",
    ]:
        assert phrase.lower() in html.lower(), phrase


def test_research_canonical_ownership_is_evidencebound() -> None:
    research_pages = [
        "research/index.html",
        "research/deterministic-control-plane-for-ai-agents/index.html",
        "research/audit-evidence-for-high-stakes-ai/index.html",
        "research/verify-the-algorithm-not-the-outcome/index.html",
    ]
    for page in research_pages:
        html = read(page)
        canonicals = re.findall(r'<link rel="canonical" href="([^"]+)"', html)
        assert len(canonicals) == 1, (page, canonicals)
        assert canonicals[0].startswith("https://evidencebound.org/"), (page, canonicals[0])
        assert "signalreview.co/research" not in html.lower()


def test_current_product_does_not_use_audit_compliance_platform_as_product_name() -> None:
    current = "\n".join(
        [
            read("index.html"),
            read("assurance/index.html"),
            read("research/index.html"),
        ]
    )
    assert "Audit Compliance Platform" not in current
    assert "AI Safety Assurance" in current


def test_signalreview_is_case_study_not_identity_home() -> None:
    html = read("case-studies/signalreview/index.html")
    assert "production sports-intelligence reference implementation" in html.lower()
    assert "separate product" in html.lower()
    assert "does not transfer ownership" in html.lower()
    assert "EvidenceBound Core" in html


def test_machine_identity_is_canonical_to_evidencebound() -> None:
    identity = json.loads(read("identity/ruslan-vrublevskyi.json"))
    assert identity["canonical_url"].startswith("https://evidencebound.org/")
    assert identity["evidencebound"]["research_library"] == "https://evidencebound.org/research/"
    assert identity["evidencebound"]["homepage"] == "https://evidencebound.org/"
    assert identity["signalreview"]["role"] == "Founder"
    assert "signalreview.co/research" not in json.dumps(identity).lower()


def test_internal_links_resolve() -> None:
    pages = list(SITE.rglob("*.html"))
    failures: list[tuple[str, str]] = []
    for page in pages:
        parser = LinkParser()
        parser.feed(page.read_text(encoding="utf-8"))
        for href in parser.hrefs:
            if not href.startswith("/") or href.startswith("//"):
                continue
            href = href.split("#", 1)[0].split("?", 1)[0]
            if not href:
                continue
            if href.endswith("/"):
                target = SITE / href.lstrip("/") / "index.html"
            else:
                target = SITE / href.lstrip("/")
            if not target.exists():
                failures.append((str(page.relative_to(SITE)), href))
    assert not failures, failures


def test_vercel_headers_and_clean_urls_are_declared() -> None:
    config = json.loads(read("vercel.json"))
    assert config.get("cleanUrls") is True
    headers = json.dumps(config.get("headers", []))
    assert "Content-Security-Policy" in headers
    assert "X-Content-Type-Options" in headers
    assert "Referrer-Policy" in headers
