"""Deterministic browser checks and retained snapshots of the staged showroom."""
import asyncio
import os
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path("spatial-qa")
ROOT.mkdir(exist_ok=True)
BASE = "http://127.0.0.1:4173/"


async def main():
    async with async_playwright() as pw:
        chrome = os.environ.get("BROWSER", "/usr/bin/google-chrome")
        browser = await pw.chromium.launch(
            executable_path=chrome,
            headless=True,
            args=["--no-sandbox", "--enable-unsafe-swiftshader"],
        )
        desktop = await browser.new_page(viewport={"width": 1440, "height": 900},
                                         reduced_motion="reduce")
        await desktop.goto(BASE, wait_until="domcontentloaded")
        await desktop.locator(".eb-display").first.wait_for()
        assert await desktop.locator(".eb-display").count() == 30
        assert await desktop.locator(".eb-floor-label").count() == 7
        sidebar_width = await desktop.locator(".eb-side").evaluate(
            "(el) => Math.round(el.getBoundingClientRect().width)"
        )
        assert sidebar_width == 304, f"unexpected sidebar width: {sidebar_width}"
        await desktop.locator('[data-eb-night-toggle]:visible').first.click()
        assert await desktop.locator("body.eb-night").count() == 1
        assert await desktop.locator(
            '[data-eb-night-toggle][aria-pressed="true"]'
        ).count() == 2
        await desktop.screenshot(path=str(ROOT / "home-night-desktop.png"))
        await desktop.locator('[data-eb-status="planned"]').click()
        assert (await desktop.locator("#eb-total").inner_text()) == "5 / 30"
        await desktop.locator('[data-eb-status="public"]').click()
        assert (await desktop.locator("#eb-total").inner_text()) == "25 / 30"
        await desktop.locator('[data-eb-status="all"]').click()
        assert (await desktop.locator("#eb-total").inner_text()) == "30 / 30"
        await desktop.close()

        mobile = await browser.new_page(viewport={"width": 390, "height": 844},
                                        reduced_motion="reduce")
        await mobile.goto(BASE, wait_until="domcontentloaded")
        await mobile.locator("#eb-mobile-list").click()
        assert await mobile.locator(".eb-side.eb-open").count() == 1
        await mobile.screenshot(path=str(ROOT / "home-mobile-list.png"))
        await mobile.locator("#eb-close-list").click()
        assert await mobile.locator(".eb-side.eb-open").count() == 0
        await mobile.locator('[data-eb-night-toggle]:visible').first.click()
        assert await mobile.locator("body.eb-night").count() == 1
        await mobile.screenshot(path=str(ROOT / "home-night-mobile.png"))
        await browser.close()


asyncio.run(main())
