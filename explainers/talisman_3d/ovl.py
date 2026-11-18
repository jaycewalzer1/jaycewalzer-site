import asyncio, sys, json
from playwright.async_api import async_playwright
CSS = """@font-face{font-family:G;src:url(file://%s/EBGaramond.ttf)}@font-face{font-family:G;font-style:italic;src:url(file://%s/EBGaramond-Italic.ttf)}
html,body{margin:0;background:transparent;width:1920px;height:1080px;position:relative}
.c{position:absolute;left:0;right:0;bottom:70px;text-align:center;font:52px G,serif;color:#F1ECE2;text-shadow:0 2px 12px rgba(10,20,28,.85)}
.l{position:absolute;font:italic 40px G,serif;color:#F1ECE2;text-shadow:0 2px 10px rgba(10,20,28,.9)}"""
async def main():
    out, items = sys.argv[1], json.loads(open(sys.argv[2]).read())
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width":1920,"height":1080})
        for name, body in items:
            await pg.set_content(f"<html><head><style>{CSS % (out, out)}</style></head><body>{body}</body></html>")
            await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(150)
            await pg.screenshot(path=f"{out}/{name}.png", omit_background=True)
        await b.close()
asyncio.run(main())
