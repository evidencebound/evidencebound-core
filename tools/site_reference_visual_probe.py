"""Read-only browser capture of the xoyk public spatial scene.

For visual comparison only: no source assets are republished or copied.
"""
import asyncio
import json
import re
from pathlib import Path
from playwright.async_api import async_playwright

OUT = Path("reference-qa")
OUT.mkdir(exist_ok=True)


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            args=["--no-sandbox", "--enable-unsafe-swiftshader"],
        )
        for name, width, height in [
            ("desktop", 1440, 900),
            ("mobile", 390, 844),
        ]:
            page = await browser.new_page(viewport={"width": width, "height": height},
                                          device_scale_factor=1, reduced_motion="reduce")
            await page.goto("https://xoyk.dev/", wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)
            before = await page.locator("button").all_text_contents()
            print(name, "PRE_BUTTONS", before)
            print(name, "BODY_HEAD", (await page.locator("body").inner_text())[:1300])
            (OUT / f"xoyk-{name}-buttons.json").write_text(json.dumps(before))
            clicked = False
            for keyword in ("without sound", "no sound", "mute", "silent", "off", "continue", "enter"):
                candidate = page.get_by_role("button", name=re.compile(keyword, re.I))
                if await candidate.count():
                    try:
                        await candidate.first.click(timeout=3000)
                        clicked = True
                        print(name, "CLICKED", keyword)
                        break
                    except Exception as exc:
                        print("not-clicked", keyword, str(exc)[:100])
            if not clicked and len(before) >= 2:
                try:
                    await page.locator("button").nth(1).click(timeout=3000)
                    print(name, "CLICKED_SECOND_BUTTON")
                    clicked = True
                except Exception as exc:
                    print("SECOND_BUTTON_ERROR", str(exc)[:200])
            if not clicked:
                try:
                    await page.mouse.click(width * .55, height * .52)
                    print(name, "CLICKED_FALLBACK_POSITION")
                except Exception as exc:
                    print("FALLBACK_ERROR", str(exc)[:150])
            await page.wait_for_timeout(6000)
            print(name, "POST_BODY", (await page.locator("body").inner_text())[:2800])
            await page.screenshot(path=str(OUT / f"xoyk-{name}-entered.png"))
            (OUT / f"xoyk-{name}-dom.txt").write_text(
                (await page.locator("body").inner_text())[:6000], encoding="utf-8"
            )
            await page.close()
        await browser.close()


asyncio.run(main())
