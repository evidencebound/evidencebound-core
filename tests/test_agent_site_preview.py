"""Deterministic public-site integrity contract for planned Evidence Agent preview.

Tests enforce accurate availability wording, existing route preservation and
pre-existing Action-Control Check distinction. No test asserts production
deployment or an implemented custom agent.
"""
from __future__ import annotations

import json
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"
BASELINE_URLS = {
    "https://evidencebound.org/",
    "https://evidencebound.org/assessment/",
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


class AgentSitePreviewTest(unittest.TestCase):
    def test_sitemap_preserves_all_15_existing_routes(self):
        root = ET.fromstring(read("sitemap.xml"))
        urls = [node.text for node in root.findall(
            ".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
        )]
        self.assertEqual(len(urls), len(set(urls)))
        self.assertEqual(set(urls), BASELINE_URLS | {"https://evidencebound.org/agent/"})

    def test_robots_txt_preserved_byte_for_byte(self):
        self.assertEqual(
            read("robots.txt"),
            "User-agent: *\nAllow: /\n\nSitemap: https://evidencebound.org/sitemap.xml\n",
        )

    def test_agent_has_one_canonical_h1_and_search_metadata(self):
        agent = read("agent/index.html")
        self.assertIn('<link rel="canonical" href="https://evidencebound.org/agent/">', agent)
        self.assertEqual(len(re.findall(r"<h1(?:\s|>)", agent)), 1)
        self.assertIn('<meta name="description" content="', agent)
        self.assertIn('<meta property="og:title"', agent)
        self.assertIn('<meta name="twitter:card"', agent)
        self.assertNotIn("noindex", agent.lower())
        self.assertLessEqual(len(re.search(r"<title>(.*?)</title>", agent).group(1)), 75)

    def test_existing_homepage_canonical_and_service_price_unchanged(self):
        home, assessment = read("index.html"), read("assessment/index.html")
        self.assertIn('<link rel="canonical" href="https://evidencebound.org/">', home)
        self.assertIn('<link rel="canonical" href="https://evidencebound.org/assessment/">', assessment)
        self.assertIn("$1,000", home)
        self.assertIn("$1,000", assessment)
        self.assertIn("one protected action", assessment.lower())
        self.assertIn('href="/assessment/"', home)

    def test_homepage_explicitly_labels_preview_as_unavailable(self):
        home = read("index.html")
        self.assertIn('id="evidence-agent"', home)
        self.assertIn('href="/agent/"', home)
        self.assertIn("In development", home)
        self.assertIn("No automated agent service is available yet", home)
        self.assertIn("pricing remain to be defined", home)

    def test_proposed_challenges_and_test_limits_are_explicit(self):
        agent = read("agent/index.html")
        for phrase in (
            "IN DEVELOPMENT",
            "NOT YET AVAILABLE",
            "Authority Drift Challenge",
            "Policy &amp; Evidence Change Challenge",
            "Retry, Replay &amp; Recovery Challenge",
            "Evidence &amp; CI Verification Challenge",
            "synthetic or authorized staging",
            "language model does not assign PASS or FAIL",
            "No agent service, pilot slot or price is currently guaranteed",
        ):
            self.assertIn(phrase, agent)

    def test_agent_price_is_undecided_not_confused_with_current_offer(self):
        agent = read("agent/index.html")
        self.assertIn("Scope &amp; pricing TBD", agent)
        self.assertIn("Action-Control Check", agent)
        self.assertIn("$1,000", agent)
        self.assertIn('href="/assessment/"', agent)
        self.assertNotIn('"@type":"Offer"', agent)
        self.assertNotIn('"@type":"SoftwareApplication"', agent)

    def test_jsonld_is_webpage_and_not_unbuilt_product_advert(self):
        agent = read("agent/index.html")
        scripts = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', agent, re.S
        )
        self.assertEqual(len(scripts), 1)
        record = json.loads(scripts[0])
        self.assertEqual(record["@type"], "WebPage")
        self.assertEqual(record["url"], "https://evidencebound.org/agent/")
        self.assertIn("in development", record["description"])

    def test_primary_navigation_is_unchanged_for_all_existing_pages(self):
        for path in ("index.html", "assessment/index.html", "agent/index.html"):
            html = read(path)
            nav = re.search(r'<div class="navlinks">(.*?)</div>', html, re.S)
            self.assertIsNotNone(nav)
            self.assertEqual(re.findall(r">([^<]+)</a>", nav.group(1)), [
                "Assessment", "Evidence", "Technology", "Partners", "Contact"
            ])

    def test_no_new_scripts_inline_styles_or_personal_data_capture(self):
        agent = read("agent/index.html")
        self.assertNotIn('style="', agent)
        self.assertNotIn("<form", agent.lower())
        self.assertNotIn("<script src=", agent.lower())
        self.assertNotIn("fetch(", agent)
        self.assertIn('href="mailto:', agent)
        self.assertIn('href="/styles.css"', agent)

    def test_light_spatial_design_is_scoped_and_responsive(self):
        css = read("styles.css")
        self.assertIn("--bg:#030a1d", css)  # Legacy design not silently rewritten.
        self.assertIn(".agent-page{background:#f7faff;color:#12274b}", css)
        self.assertIn(".agent-preview{background:linear-gradient(", css)
        self.assertIn(".agent-spatial-stage", css)
        self.assertIn("@media(max-width:700px)", css)
        self.assertIn("@media(prefers-reduced-motion:reduce)", css)

    def test_existing_seo_rules_and_redirects_preserved(self):
        config = json.loads(read("vercel.json"))
        self.assertTrue(config["trailingSlash"])
        self.assertTrue(config["cleanUrls"])
        redirects = config["redirects"]
        self.assertTrue(any(
            x["source"] == "/research/audit-compliance-platform-for-high-stakes-ai"
            and x["destination"] == "/research/audit-evidence-for-high-stakes-ai/"
            and x["permanent"] for x in redirects
        ))


if __name__ == "__main__":
    unittest.main()
