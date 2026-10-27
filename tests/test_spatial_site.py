"""Bounded deterministic acceptance for the EvidenceBound spatial website.

Tests do not score aesthetic similarity to xoyk.dev. They verify executable
interactions and preservation of exact search, pricing and product boundaries.
"""
from __future__ import annotations

import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def read(path: str) -> str:
    return (SITE / path).read_text(encoding="utf-8")


class StageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.screens = []
        self.inline_styles = []
        self.links = []
        self.buttons = []

    def handle_starttag(self, tag, attributes):
        data = dict(attributes)
        if "style" in data:
            self.inline_styles.append(tag)
        if tag == "a":
            self.links.append(data.get("href", ""))
            if "spatial-monitor" in data.get("class", "").split():
                self.screens.append(data)
        if tag == "button":
            self.buttons.append(data)


class SpatialSiteTests(unittest.TestCase):
    def test_exact_nine_spatial_screens_with_real_canonical_routes(self):
        root = StageParser()
        root.feed(read("index.html"))
        self.assertEqual(len(root.screens), 9)
        self.assertEqual(len(set(s.get("href") for s in root.screens)), 9)
        for item in root.screens:
            url = item["href"]
            self.assertTrue(url.startswith("/") and url.endswith("/"))
            self.assertTrue((SITE / url.lstrip("/") / "index.html").is_file(), url)
            self.assertIn(item.get("data-spatial-category"), {"service", "evidence", "research"})
            self.assertNotIn("xoyk.dev", item.get("href"))

    def test_three_aisles_three_screens_each(self):
        root = StageParser()
        root.feed(read("index.html"))
        self.assertEqual(
            [x.get("data-spatial-category") for x in root.screens],
            ["service"] * 3 + ["evidence"] * 3 + ["research"] * 3,
        )

    def test_every_stage_screen_is_keyboard_accessible_native_link(self):
        root = StageParser()
        root.feed(read("index.html"))
        self.assertTrue(all(x.get("aria-label", "").strip() for x in root.screens))
        self.assertIn("spatial-monitor:focus-visible", read("spatial.css"))
        self.assertIn('aria-label="Filter and display EvidenceBound work"', read("index.html"))

    def test_controls_are_real_and_have_state(self):
        root = StageParser()
        root.feed(read("index.html"))
        filters = [b["data-spatial-filter"] for b in root.buttons
                   if "data-spatial-filter" in b]
        self.assertEqual(filters, ["all", "service", "evidence", "research"])
        self.assertTrue(all(
            "aria-pressed" in b for b in root.buttons if "data-spatial-filter" in b
        ))
        self.assertTrue(any(b.get("id") == "spatial-mode" for b in root.buttons))
        self.assertIn("src=\"/spatial.mjs\"", read("index.html"))
        self.assertIn('id="spatial-directory" hidden', read("index.html"))

    def test_price_and_future_product_status_were_not_conflated(self):
        html = read("index.html")
        self.assertIn("Action-Control Check", html)
        self.assertIn("Request the $1,000 check", html)
        self.assertIn('href="/assessment/"', html)
        self.assertIn("Evidence Agent", html)
        self.assertIn("in development", html)
        self.assertIn("no live automated agent service or fixed price", html)
        self.assertIn('href="/agent/"', html)

    def test_inbound_search_surface_and_org_jsonld_unmodified(self):
        html = read("index.html")
        self.assertEqual(html.count("<h1"), 1)
        self.assertIn('<link rel="canonical" href="https://evidencebound.org/">', html)
        self.assertIn('<meta name="description"', html)
        blocks = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.S
        )
        self.assertEqual(len(blocks), 1)
        graph = json.loads(blocks[0])["@graph"]
        self.assertEqual({x["@type"] for x in graph}, {"Organization", "WebSite"})
        self.assertEqual(
            next(x for x in graph if x["@type"] == "Organization")["logo"]["url"],
            "https://evidencebound.org/assets/evidencebound-icon-primary.png",
        )

    def test_sitemap_preserves_16_urls_no_redirect_changes(self):
        sitemap = ET.fromstring(read("sitemap.xml"))
        urls = [x.text for x in sitemap.findall(
            ".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
        )]
        self.assertEqual(len(urls), 16)
        self.assertEqual(len(set(urls)), 16)
        self.assertIn("https://evidencebound.org/agent/", urls)
        self.assertEqual(
            read("robots.txt"),
            "User-agent: *\nAllow: /\n\nSitemap: https://evidencebound.org/sitemap.xml\n",
        )
        self.assertTrue(json.loads(read("vercel.json"))["trailingSlash"])

    def test_no_inline_styles_or_network_scripting(self):
        parser = StageParser()
        parser.feed(read("index.html"))
        self.assertEqual(parser.inline_styles, [])
        script = read("spatial.mjs")
        self.assertNotIn("fetch(", script)
        self.assertNotIn("XMLHttpRequest", script)
        self.assertNotIn("WebSocket", script)
        self.assertNotIn("localStorage", script)
        self.assertNotIn("innerHTML", script)
        self.assertNotIn("style.", script)
        self.assertNotIn("eval(", script)

    def test_spatial_depth_and_2d_accessibility_fallback(self):
        css = read("spatial.css")
        self.assertIn("perspective:1300px", css)
        self.assertIn("rotateY(-12deg)", css)
        self.assertIn(".spatial-screen", css)
        self.assertIn(".spatial-floor-light", css)
        self.assertIn(".spatial-lane", css)
        self.assertIn("@media(max-width:640px)", css)
        self.assertIn("@media(prefers-reduced-motion:reduce)", css)

    def test_global_palette_is_brand_blue_and_light(self):
        css = read("styles.css")
        self.assertIn("2026-10-27 EvidenceBound Light Spatial Interface", css)
        self.assertIn("--bg:#f7fbff", css)
        self.assertIn("--text:#142f58", css)
        self.assertIn("body{background:linear-gradient(180deg,#fff", css)
        self.assertIn("/assets/evidencebound-icon-primary.png", css)

    def test_old_commercial_evidence_and_research_text_remain(self):
        home = read("index.html")
        for phrase in (
            "DevSecOps agents", "Cyber-remediation agents",
            "One workflow. Two control transitions.",
            "RAB-1 reproduced a duplicate-consequence failure",
            "Fixed scope", "Retained test artifacts",
            "Scope", "Challenge", "Observe", "Report", "Retest",
        ):
            self.assertIn(phrase, home)


if __name__ == "__main__":
    unittest.main()
