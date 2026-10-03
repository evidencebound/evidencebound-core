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
        "assessment/index.html",
        "partners/oem/index.html",
        "rab1/index.html",
        "assets/evidencebound-mark.png",
        "assets/evidencebound-social-card.png",
        "robots.txt",
        "sitemap.xml",
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


def test_homepage_has_commercial_control_assurance_positioning() -> None:
    html = read("index.html")
    for phrase in [
        "Prove your AI agent is still authorized when conditions change.",
        "DevSecOps agents",
        "Cyber-remediation agents",
        "Scope",
        "Challenge",
        "Observe",
        "Report",
        "Retest",
        "RAB-1 reproduced a duplicate-consequence failure",
    ]:
        assert phrase.lower() in html.lower(), phrase
    for forbidden in [
        "Commercial architecture",
        "payments / refunds",
        "vendor onboarding",
        "Operational agents",
    ]:
        assert forbidden.lower() not in html.lower(), forbidden
    assert "guarantees compliance" not in html.lower()
    assert "guarantees safety" not in html.lower()


def test_commercial_routes_and_disclosure_boundary() -> None:
    assessment = read("assessment/index.html")
    partner = read("partners/oem/index.html")
    assert (
        "Typical pilot: one consequential workflow, approximately 1\u20132 weeks, "
        "fixed scope, one retest."
        in assessment
    )
    assert "PASS / FAIL / BLOCKED / UNVERIFIED" in assessment
    assert "A commercially controlled specialist methodology." in partner
    for forbidden in [
        "Enough evidence to buy",
        "complete adversarial corpus",
        "Not transferred by default",
        "trade secret",
    ]:
        assert forbidden.lower() not in partner.lower(), forbidden


def test_primary_navigation_is_five_item_buyer_navigation() -> None:
    html = read("index.html")
    nav = re.search(r'<div class="navlinks">(.*?)</div>', html, re.S)
    assert nav
    labels = re.findall(r">([^<]+)</a>", nav.group(1))
    assert labels == ["Assessment", "Evidence", "Partners", "Research", "Contact"]


def test_corporate_descriptor_is_synchronized() -> None:
    descriptor = (
        "EvidenceBound is an independent technical assurance practice for "
        "consequential AI-agent control."
    )
    for page in ["assurance/index.html", "research/index.html", "privacy/index.html"]:
        assert descriptor in read(page)
    combined = "\n".join(p.read_text(encoding="utf-8") for p in SITE.rglob("*.html"))
    assert "early-stage open-source AI safety infrastructure" not in combined.lower()
    assert "open-core verification and human-control infrastructure" not in combined.lower()


def test_discovery_and_social_metadata_exist() -> None:
    assert "Sitemap: https://evidencebound.org/sitemap.xml" in read("robots.txt")
    sitemap = read("sitemap.xml")
    for url in [
        "https://evidencebound.org/",
        "https://evidencebound.org/assessment/",
        "https://evidencebound.org/rab1/",
        "https://evidencebound.org/partners/oem/",
    ]:
        assert url in sitemap
    social = SITE / "assets" / "evidencebound-social-card.png"
    assert social.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    for page in SITE.rglob("*.html"):
        html = page.read_text(encoding="utf-8")
        for marker in [
            'property="og:title"',
            'property="og:description"',
            'property="og:image"',
            'name="twitter:card"',
        ]:
            assert marker in html, (str(page.relative_to(SITE)), marker)
        for mojibake in ["â€”", "â€“", "Â·", "â€™"]:
            assert mojibake not in html, (str(page.relative_to(SITE)), mojibake)


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
    assert "independent technical assurance" in current.lower()


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
    assert "independent technical assurance" in identity["evidencebound"]["description"].lower()
    assert (
        "early-stage research and open-source infrastructure"
        not in identity["claim_boundary"].lower()
    )
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
