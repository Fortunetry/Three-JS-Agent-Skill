"""Render check for a Three.js page using Playwright (headless Chromium).

Usage:
  python3 verify_render.py <url> <screenshot.png> [--no-webgl] [--reduce-motion] [--mobile]

Prints: canvas status, fallback status, console errors and warnings, and the canvas size.
Requires: pip install playwright && python -m playwright install chromium
"""
import asyncio
import json
import sys

from playwright.async_api import async_playwright


async def main(url, shot, flags):
    args = []
    if "--no-webgl" in flags:
        args += ["--disable-webgl", "--disable-3d-apis"]
    viewport = {"width": 390, "height": 844} if "--mobile" in flags else {"width": 1280, "height": 800}
    reduced = "reduce" if "--reduce-motion" in flags else "no-preference"

    logs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=args)
        ctx = await browser.new_context(viewport=viewport, reduced_motion=reduced)
        page = await ctx.new_page()
        page.on("console", lambda m: logs.append(f"{m.type}: {m.text}"))
        page.on("pageerror", lambda e: logs.append(f"PAGEERROR: {e}"))
        await page.goto(url, wait_until="load")
        await page.wait_for_timeout(1500)
        info = await page.evaluate("""() => {
          const c = document.querySelector('canvas');
          const f = document.querySelector('.fallback');
          return {
            canvas: !!c,
            canvasSize: c ? [c.width, c.height] : null,
            noWebglClass: document.body.classList.contains('no-webgl'),
            fallbackDisplay: f ? getComputedStyle(f).display : null
          };
        }""")
        await page.screenshot(path=shot)
        await browser.close()

    # Ignore internal GPU driver warnings (typical of the software renderer in headless mode)
    filtered = [m for m in logs if "GL Driver Message" not in m]
    print(json.dumps({"info": info, "console": filtered or "clean"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3:]))
