"""Commercial-site claim constraints for the November 2026 gateway research preview."""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.ids: set[str] = set()
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        p = dict(attrs)
        if tag == "a" and p.get("href"):
            self.hrefs.append(p["href"])
        if p.get("id"):
            self.ids.add(p["id"])


def page(path: str) -> str:
    return (SITE / path).read_text(encoding="utf-8")


def test_existing_offer_price_scope_and_cta_unchanged() -> None:
    assessment = page("assessment/index.html")
    assert '"name":"EvidenceBound Action-Control Check"' in assessment
    assert '"price":"1000"' in assessment
    assert '"priceCurrency":"USD"' in assessment
    assert "one protected action" in assessment.lower()
    assert "two scenarios" in assessment.lower()
    assert "mailto:ruslan@evidencebound.org?subject=EvidenceBound%20%241000%20Action-Control%20Check" in assessment
    assert "No payment is taken on this website." in assessment


def test_cost_exposure_is_measurable_not_guaranteed() -> None:
    assessment = page("assessment/index.html")
    home = page("index.html")
    assert 'id="operational-exposure"' in assessment
    assert "actual downstream boundary" in assessment
    assert "cost savings require a customer-specific baseline" in home
    assert "Actual minutes are measured only where source records exist." in assessment
    assert "No universal token or labor savings are claimed." in assessment
    assert "Google Agent Gateway Extension" not in home


def test_protocol_evidence_is_explicitly_local_and_bounded() -> None:
    tech = page("technology/index.html")
    partner = page("partners/oem/index.html")
    note = (ROOT / "docs/research/2026-11-03-envoy-extproc-local-acceptance.md").read_text(encoding="utf-8")
    assert 'id="gateway-research"' in tech
    assert "19/19" in tech and "400 sequential localhost" in tech
    assert "GOOGLE-MANAGED COMPATIBILITY · NOT VERIFIED" in tech
    assert "not been tested against the managed Google service" in tech
    assert "separately priced pilot" in partner
    assert "Pricing, connectivity and acceptance criteria" in partner or "price and acceptance criteria" in partner
    assert "8073a818fe1ccfa417544e7db6d492c9926077295bf1bc74d920ff3c9ec0ab97" in note
    assert "not a downloadable public reproduction bundle" in note
    assert "not third-party verification" in note
    assert "0.95 s" in note


def test_local_navigation_and_anchors() -> None:
    for path in ("index.html", "assessment/index.html", "partners/oem/index.html", "technology/index.html"):
        html = page(path)
        parse = Links()
        parse.feed(html)
        assert parse.ids
        assert "/assessment/" in parse.hrefs
        assert "<h1" in html
        for href in parse.hrefs:
            if not href.startswith("/") or href.startswith("//"):
                continue
            local, _, fragment = href.partition("#")
            target = SITE / local.lstrip("/")
            if local.endswith("/"):
                target = target / "index.html"
            assert target.is_file(), (path, href)
            if fragment and target.suffix == ".html":
                parser = Links()
                parser.feed(target.read_text(encoding="utf-8"))
                assert fragment in parser.ids, (path, href)


def test_metadata_and_single_h1_preserved() -> None:
    for path in ("index.html", "assessment/index.html", "partners/oem/index.html", "technology/index.html"):
        html = page(path)
        assert len(re.findall(r"<h1(?:\s|>)", html)) == 1, path
        assert html.count('rel="canonical"') == 1, path
        for key in ('name="description"', 'property="og:description"', 'name="twitter:description"'):
            assert key in html, (path, key)
        for js in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, flags=re.S):
            assert json.loads(js)["@context"] == "https://schema.org"
