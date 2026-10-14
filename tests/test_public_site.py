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
    assert "$1,000" in assessment
    assert "one protected action" in assessment.lower()
    assert "two scenarios" in assessment.lower()
    assert "retest" in assessment.lower()
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
    assert labels == ["Assessment", "Evidence", "Technology", "Partners", "Contact"]


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


def test_stage1_commercial_offer_and_brand_assets() -> None:
    home = read("index.html")
    assessment = read("assessment/index.html")
    for content in (home, assessment):
        assert "$1,000" in content
        assert "mailto:ruslan@evidencebound.org" in content
        assert "evidencebound-icon-primary.png" in content
        assert "certification" in content.lower() or "no certification" in content.lower()
        for forbidden in ("OntoGuard", "EMILIA", "guaranteed safe", "certified compliant"):
            assert forbidden.lower() not in content.lower(), forbidden
    for name in ("evidencebound-icon-primary.png", "evidencebound-logo-primary.png"):
        raw = (SITE / "assets" / name).read_bytes()
        assert raw.startswith(bytes.fromhex("89504e470d0a1a0a"))
    for marker in ("Scope", "Challenge", "Observe", "Report", "Retest"):
        assert marker in home
    for marker in ("staging or synthetic", "two agreed transitions", "Not included"):
        assert marker.lower() in assessment.lower(), marker


def test_stage2_technology_route_and_claim_boundaries() -> None:
    technology = read("technology/index.html")
    assert "https://evidencebound.org/technology/" in read("sitemap.xml")
    assert 'rel="canonical" href="https://evidencebound.org/technology/"' in technology
    assert "RELEASED OPEN REFERENCE" in technology
    assert "FROZEN CONTROLLED BENCHMARK" in technology
    assert "externalSideEffect=false" in technology
    assert "12/12 hard gates" in technology
    assert "8/8 frozen scenarios" in technology
    assert "Not NVIDIA validation" in technology
    assert "NOT A PUBLIC PRODUCT" in technology
    assert "not proof of client adoption" in technology.lower()
    assert "$1,000" in technology
    partner = read("partners/oem/index.html")
    assert "not signed partners or customer references" in partner.lower()
    assert "not an assumed partnership" in partner.lower()
    for page in SITE.rglob("*.html"):
        html = page.read_text(encoding="utf-8").lower()
        for forbidden in ("ontoguard", "emilia"):
            assert forbidden not in html, (str(page.relative_to(SITE)), forbidden)


def test_stage2_navigation_and_favicon_are_consistent() -> None:
    branded_routes = [
        "index.html", "assessment/index.html", "partners/oem/index.html",
        "technology/index.html", "rab1/index.html", "assurance/index.html",
        "research/index.html", "papers/index.html", "privacy/index.html",
    ]
    for route in branded_routes:
        html = read(route)
        for path in ("/assessment/", "/technology/", "/partners/oem/", "/rab1/"):
            assert 'href="' + path + '"' in html, (route, path)
        assert "evidencebound-icon-primary.png" in html, route


def test_visual_qa_fixes_keep_strict_csp() -> None:
    import json
    for page in SITE.rglob("*.html"):
        html = page.read_text(encoding="utf-8")
        assert 'style="' not in html, page.relative_to(SITE)
    assert ".boundary-spaced{margin-top:24px}" in read("styles.css")
    for route in ("rab1/index.html", "assurance/index.html"):
        html = read(route)
        assert '<p class="table-scroll-hint">' in html
        assert 'role="region" aria-label="Scrollable technical evidence table"' in html
    for route in ("linkedin/oauth/callback/index.html", "webmcp/index.html"):
        assert 'href="/assets/evidencebound-icon-primary.png"' in read(route)
    callback = read("linkedin/oauth/callback/index.html")
    assert '<a href="/technology/">Technology</a>' in callback
    assert '<a href="/research/">Research</a>' not in callback
    config = json.loads(read("vercel.json"))
    values = [
        h["value"]
        for group in config["headers"]
        for h in group["headers"]
        if h["key"] == "Content-Security-Policy"
    ]
    assert len(values) == 1
    assert "style-src 'self'" in values[0]
    assert "'unsafe-inline'" not in values[0]


def test_seo_aeo_discovery_and_buyer_answers() -> None:
    import xml.etree.ElementTree as ET

    sitemap = ET.fromstring(read("sitemap.xml"))
    locs = {
        node.text for node in sitemap.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    }
    callback = "linkedin/oauth/callback/index.html"
    for page in SITE.rglob("*.html"):
        path = str(page.relative_to(SITE)).replace("\\", "/")
        html = page.read_text(encoding="utf-8")
        canonical = re.findall(r'<link rel="canonical" href="([^"]+)"', html)
        assert len(canonical) == 1, path
        assert '<meta name="description" content="' in html, path
        assert len(re.findall(r"<h1(?:\s|>)", html)) == 1, path
        title = re.findall(r"<title>([^<]+)</title>", html)
        assert len(title) == 1 and len(title[0]) <= 75, path
        if path == callback:
            assert '<meta name="robots" content="noindex,follow">' in html
            assert canonical[0] not in locs
        else:
            assert canonical[0] in locs, path

    home = read("index.html")
    assessment = read("assessment/index.html")
    for page in (home, assessment):
        blocks = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', page, re.S
        )
        assert len(blocks) == 1
        assert json.loads(blocks[0])["@context"] == "https://schema.org"
    graph = json.loads(re.search(
        r'<script type="application/ld\+json">(.*?)</script>', home, re.S
    ).group(1))["@graph"]
    org = next(item for item in graph if item["@type"] == "Organization")
    assert org["logo"]["url"].endswith("evidencebound-icon-primary.png")
    assert org["url"] == "https://evidencebound.org/"
    offer = json.loads(re.search(
        r'<script type="application/ld\+json">(.*?)</script>', assessment, re.S
    ).group(1))["offers"]
    assert offer["price"] == "1000" and offer["priceCurrency"] == "USD"
    assert "What is included in the $1,000 price?" in assessment
    assert "Do you need access to production?" in assessment
    assert "Does a PASS prove my agent is safe?" in assessment
    assert 'id="verify-claims"' in read("technology/index.html")
    for forbidden in ("guaranteed safe", "ontoguard", "emilia"):
        assert forbidden not in assessment.lower() and forbidden not in home.lower()
