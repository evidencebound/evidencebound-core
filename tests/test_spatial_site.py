"""Deterministic showroom structure, search preservation and buyer-scope gates.

No aesthetic similarity is asserted by these tests. Visual resemblance requires
separate retained browser screenshots and a human review.
"""
from __future__ import annotations

import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"
ORIGINAL_URLS = {
    "https://evidencebound.org/",
    "https://evidencebound.org/assessment/",
    "https://evidencebound.org/agent/",
    "https://evidencebound.org/technology/",
    "https://evidencebound.org/technology/google-adk-external-reproduction/",
    "https://evidencebound.org/rab1/",
    "https://evidencebound.org/partners/oem/",
    "https://evidencebound.org/research/",
    "https://evidencebound.org/research/deterministic-control-plane-for-ai-agents/",
    "https://evidencebound.org/research/audit-evidence-for-high-stakes-ai/",
    "https://evidencebound.org/research/verify-the-algorithm-not-the-outcome/",
    "https://evidencebound.org/assurance/",
    "https://evidencebound.org/privacy/",
    "https://evidencebound.org/case-studies/signalreview/",
    "https://evidencebound.org/papers/",
    "https://evidencebound.org/webmcp/",
}


def read(path: str) -> str:
    return (SITE / path).read_text(encoding="utf-8")


class Elements(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.displays: list[dict[str, str | None]] = []
        self.links: list[dict[str, str | None]] = []
        self.buttons: list[dict[str, str | None]] = []
        self.inline_styles: list[str] = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if d.get("style") is not None:
            self.inline_styles.append(tag)
        if tag == "a":
            self.links.append(d)
            if "eb-display" in (d.get("class") or "").split():
                self.displays.append(d)
        if tag == "button":
            self.buttons.append(d)


class SpatialSiteTests(unittest.TestCase):
    def test_thirty_screens_across_seven_aisles(self):
        parser = Elements()
        parser.feed(read("index.html"))
        self.assertEqual(len(parser.displays), 30)
        self.assertEqual(
            [sum(("eb-lane-" + str(lane)) in (screen.get("class") or "").split()
                 for screen in parser.displays) for lane in range(7)],
            [5, 5, 5, 4, 4, 4, 3],
        )
        self.assertEqual(len({
            d.get("aria-label") for d in parser.displays
        }), 30)

    def test_native_links_resolve_to_real_public_page(self):
        parser = Elements()
        parser.feed(read("index.html"))
        for display in parser.displays:
            url = display.get("href") or ""
            self.assertTrue(url.startswith("/") and url.endswith("/"), url)
            self.assertTrue((SITE / url.lstrip("/") / "index.html").is_file(), url)
            self.assertNotIn("xoyk", url)

    def test_theme_sidebar_and_fullscreen_floor(self):
        html, css = read("index.html"), read("showroom.css")
        for marker in (
            'class="eb-side"', 'id="eb-search"', 'id="eb-stage"',
            'class="eb-ground"', 'id="eb-displays"', 'class="eb-floor-labels"',
            'class="eb-intro"', 'class="eb-statusline"',
            'class="eb-mobile-tabs"', 'id="eb-mobile-list"',
        ):
            self.assertIn(marker, html)
        for pattern in ("perspective(930px)", "rotateX(68deg)", "--size:126px",
                        ".eb-display-foot", ".eb-stage-corner", ".eb-list-group"):
            self.assertIn(pattern, css)
        self.assertIn("@media(max-width:700px)", css)
        self.assertIn("@media(prefers-reduced-motion:reduce)", css)

    def test_search_filter_buttons_are_semantic_and_stateful(self):
        parser = Elements()
        parser.feed(read("index.html"))
        self.assertEqual([b.get("data-eb-status") for b in parser.buttons
                          if b.get("data-eb-status") is not None],
                         ["all", "public", "planned"])
        self.assertEqual([b.get("data-eb-group") for b in parser.buttons
                          if b.get("data-eb-group") is not None],
                         ["all", "0", "1", "2", "3", "4", "5", "6"])
        self.assertTrue(all(
            b.get("aria-pressed") in {"true", "false"} for b in parser.buttons
            if b.get("data-eb-group") is not None or b.get("data-eb-status") is not None
        ))

    def test_development_status_remains_explicit(self):
        home = read("index.html")
        agent = read("agent/index.html")
        self.assertIn("no live agent or set price", home.lower())
        self.assertIn("Agent", home)
        self.assertIn("In development", agent)
        self.assertIn("NOT YET AVAILABLE", agent)
        self.assertIn("Scope &amp; pricing TBD", agent)
        self.assertIn('href="/agent/"', home)

    def test_buyer_price_and_limits_remain_clear(self):
        home, scope = read("index.html"), read("assessment/index.html")
        self.assertIn("Request a check", home)
        self.assertIn("$1,000", home)
        self.assertIn("Authorized staging or synthetic only", home)
        self.assertIn("RAB-1 reproduced a duplicate-consequence failure", home)
        self.assertIn("one protected action", scope.lower())
        self.assertIn("two scenarios", scope.lower())

    def test_metadata_canonical_and_org_graph_unchanged(self):
        home = read("index.html")
        self.assertEqual(len(re.findall(r"<h1(?:\s|>)", home)), 1)
        self.assertIn('<link rel="canonical" href="https://evidencebound.org/">', home)
        self.assertIn('<meta name="description" content="', home)
        blocks = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', home, re.S
        )
        self.assertEqual(len(blocks), 1)
        graph = json.loads(blocks[0])["@graph"]
        self.assertEqual({x["@type"] for x in graph}, {"Organization", "WebSite"})
        logo = next(x for x in graph if x["@type"] == "Organization")["logo"]["url"]
        self.assertEqual(logo, "https://evidencebound.org/assets/evidencebound-icon-primary.png")

    def test_sitemap_robots_and_routing_untouched(self):
        tree = ET.fromstring(read("sitemap.xml"))
        urls = [loc.text for loc in tree.findall(
            ".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
        )]
        self.assertEqual(set(urls), ORIGINAL_URLS)
        self.assertEqual(len(urls), 16)
        self.assertEqual(read("robots.txt"),
                         "User-agent: *\nAllow: /\n\n"
                         "Sitemap: https://evidencebound.org/sitemap.xml\n")
        config = json.loads(read("vercel.json"))
        self.assertTrue(config["trailingSlash"])
        self.assertTrue(config["cleanUrls"])
        self.assertTrue(any(r.get("permanent") for r in config["redirects"]))

    def test_no_inline_style_or_external_script(self):
        parser = Elements()
        parser.feed(read("index.html"))
        self.assertEqual(parser.inline_styles, [])
        self.assertIn('<script type="module" src="/showroom.mjs"></script>', read("index.html"))
        self.assertNotIn("xoyk.dev", read("index.html"))
        js = read("showroom.mjs")
        for prohibited in ("fetch(", "XMLHttpRequest", "WebSocket", "eval(",
                           "localStorage", "innerHTML"):
            self.assertNotIn(prohibited, js)

    def test_fallback_indexable_beneath_spatial_stage(self):
        html = read("index.html")
        self.assertLess(html.index("eb-showroom"), html.index('id="pricing"'))
        self.assertIn("What we test", html)
        self.assertIn("Five steps from scope to evidence-backed findings.", html)
        self.assertIn("Prove your AI agent is still authorized", html)
        self.assertIn('href="/assessment/"', html)

    def test_unmodified_webmcp_and_agent_pages_still_exist(self):
        self.assertTrue((SITE / "webmcp/control-core.mjs").is_file())
        self.assertTrue((SITE / "agent/index.html").is_file())
        self.assertTrue((SITE / "technology/index.html").is_file())

    def test_light_branding_and_30_screen_inventory(self):
        css = read("showroom.css")
        self.assertIn("background:#f6faff", css)
        self.assertIn("background:#f7fbff", css)
        self.assertIn("30 screens", read("index.html"))
        self.assertIn("PUBLISHED 25", read("index.html"))
        self.assertIn("PLANNED 5", read("index.html"))


if __name__ == "__main__":
    unittest.main()
