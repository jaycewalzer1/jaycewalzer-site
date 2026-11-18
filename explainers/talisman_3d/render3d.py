# usage: render3d.py <url> <mode: stills t1,t2,.. | frames t0 t1 outdir>
import asyncio, sys, os
from playwright.async_api import async_playwright
async def main():
    url, mode = sys.argv[1], sys.argv[2]
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle","--use-angle=metal","--enable-gpu","--ignore-gpu-blocklist"])
        pg = await b.new_page(viewport={"width":1920,"height":1080})
        pg.on("console", lambda m: print("console:", m.text))
        pg.on("pageerror", lambda e: print("pageerror:", e))
        await pg.goto(url); await pg.wait_for_function("window.ready === true"); await pg.evaluate("document.fonts.ready")
        if mode == "stills":
            for t in sys.argv[3].split(","):
                await pg.evaluate(f"setTime({t})"); await pg.screenshot(path=f"still_{t}.jpg", type="jpeg", quality=85)
        else:
            t0, t1, out = float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]; os.makedirs(out, exist_ok=True)
            n = round((t1 - t0) * 30)
            for i in range(n):
                await pg.evaluate(f"setTime({t0 + i/30})")
                await pg.screenshot(path=f"{out}/f{i:05d}.jpg", type="jpeg", quality=92)
        await b.close()
asyncio.run(main())
