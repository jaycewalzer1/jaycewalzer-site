import asyncio, sys, json, html
from playwright.async_api import async_playwright
# argv: outdir, json list of [name, text]
async def main():
    out, items = sys.argv[1], json.loads(sys.argv[2])
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width":1920,"height":1080})
        for name, text in items:
            await pg.set_content(f"""<html><head><style>@font-face{{font-family:G;src:url(file://{out}/EBGaramond.ttf)}}
            html,body{{margin:0;background:transparent}}
            #c{{position:absolute;left:0;right:0;bottom:70px;text-align:center;font:52px G,serif;color:#F1ECE2;text-shadow:0 2px 12px rgba(10,20,28,.75)}}</style></head>
            <body><div id=c>{html.escape(text)}</div></body></html>""")
            await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(150)
            await pg.screenshot(path=f"{out}/{name}.png", omit_background=True)
        await b.close()
asyncio.run(main())
