"""Build index.html from site.json and the per-entry write-ups in assets/content/.

    python3 tools/build.py

A write-up is assets/content/<slug>.md: paragraphs, then optional `stack: ...` and
`links: url, url` lines. Videos are picked up if they exist:
assets/video/<slug>-demo.mp4 (+ .jpg poster) and assets/video/<slug>-explainer.mp4 (+ .jpg).
"""
import html
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = json.loads((ROOT / "site.json").read_text())
VID = ROOT / "assets/video"


def read_content(slug):
    p = ROOT / "assets/content" / f"{slug}.md"
    if not p.exists():
        return [], "", []
    paras, stack, links = [], "", []
    for block in re.split(r"\n\s*\n", p.read_text().strip()):
        text, items = [], []
        for line in block.strip().splitlines():
            line = line.strip()
            low = line.lower()
            if line.startswith("#"):
                continue
            if low.startswith("stack:"):
                stack = line.split(":", 1)[1].strip()
            elif low.startswith("links:"):
                links = [u.strip() for u in line.split(":", 1)[1].split(",") if u.strip()]
            elif line.startswith("- "):
                items.append(line[2:])
            else:
                text.append(line)
        if text:
            paras.append(" ".join(text))
        if items:
            paras.append(items)
    return paras, stack, links


def inline(text):
    t = html.escape(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    t = re.sub(r"\*(.+?)\*", r"<i>\1</i>", t)
    t = re.sub(r"\[(.+?)\]\(((?:https?://|#)[^)]+)\)", r'<a href="\2">\1</a>', t)
    return t


def render_paras(paras):
    out = []
    for p in paras:
        if isinstance(p, list):
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in p) + "</ul>")
        else:
            out.append(f"<p>{inline(p)}</p>")
    return "".join(out)


def icon(name):
    """Inline SVG icon that inherits the text color."""
    paths = {
        "play": '<path d="M7 4.5v15l12.5-7.5z" fill="currentColor" stroke="none"/>',
        "external": '<path d="M7 17 17 7M9 7h8v8"/>',
        "up": '<path d="M12 19V5M6 11l6-6 6 6"/>',
        "close": '<path d="M6 6l12 12M18 6 6 18"/>',
    }
    return ('<svg class="ic" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{paths[name]}</svg>')


def link_label(url):
    u = re.sub(r"^https?://(www\.)?", "", url).rstrip("/")
    return "code" if u.startswith("github.com/") else u


def duration(f):
    try:
        s = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                                 capture_output=True, text=True).stdout)
        return f"{int(s // 60)}:{int(s % 60):02d}"
    except ValueError:
        return ""


def media(slug, kind):
    f = VID / f"{slug}-{kind}.mp4"
    if not f.exists():
        return None
    poster = VID / f"{slug}-{kind}.jpg"
    return {"src": f"assets/video/{f.name}", "poster": f"assets/video/{poster.name}" if poster.exists() else "",
            "dur": duration(f)}


def links_html(links, extra=""):
    items = [f'<a href="{html.escape(u)}">{html.escape(link_label(u))} {icon("external")}</a>' for u in links]
    return '<p class="links">' + extra + "".join(items) + "</p>" if (items or extra) else ""


def project(item):
    slug = item["slug"]
    paras, stack, links = read_content(slug)
    links = links or item.get("links", [])
    demo, expl = media(slug, "demo"), media(slug, "explainer")
    vid = ""
    if demo:
        vid = (f'<div class="demo"><video data-src="{demo["src"]}" poster="{demo["poster"]}" muted loop playsinline '
               f'preload="none" aria-label="{html.escape(item["name"])} demo"></video></div>')
    play = ""
    if expl:
        play = (f'<button class="explain" data-src="{expl["src"]}" data-poster="{expl["poster"]}" '
                f'data-title="{html.escape(item["name"])}">{icon("play")} how it works <span>{expl["dur"]}</span></button>')
    more = ""
    if paras:
        meta = f'<p class="stack">{html.escape(stack)}</p>' if stack else ""
        more = f'<details class="more"><summary>read more</summary>{render_paras(paras)}{meta}</details>'
    cls = "proj featured" if item.get("featured") else "proj"
    return f"""<article class="{cls}" id="{slug}">
  {vid}
  <div class="txt">
    <h3>{html.escape(item['name'])} <span class="when">{html.escape(item.get('when', ''))}</span></h3>
    <p class="hook">{inline(item.get('hook', ''))}</p>
    <div class="row">{play}{links_html(links)}</div>
    {more}
  </div>
</article>"""


def job(item):
    slug = item["slug"]
    paras, stack, links = read_content(slug)
    first = paras[0] if paras and isinstance(paras[0], str) else ""
    rest = paras[1:] if first else paras
    see = ""
    target = item.get("media")
    if target:
        name = next((p["name"] for p in SITE["projects"] if p["slug"] == target), target)
        see = f'<a class="see" href="#{target}">see {html.escape(name)} {icon("up")}</a>'
    body = f"<p>{inline(first)}</p>" if first else ""
    extra = ""
    if rest or stack:
        extra = (f'<details class="more"><summary>more</summary>{render_paras(rest)}'
                 + (f'<p class="stack">{html.escape(stack)}</p>' if stack else "") + "</details>")
    return f"""<li id="{slug}"><div class="jhead"><b>{html.escape(item['name'])}</b> <span>{html.escape(item['tag'])}</span><em>{html.escape(item.get('when', ''))}</em></div>
<div class="jbody">{body}{see}{extra}</div></li>"""


def photo(p, cls="band", eager=False):
    pos = f' style="object-position:{p["pos"]}"' if p.get("pos") else ""
    lazy = "" if eager else ' loading="lazy"'
    return f'<img class="photo {cls}" src="{p["src"]}" alt="{html.escape(p["alt"])}"{pos}{lazy} decoding="async">'


def build():
    s = SITE
    featured = "\n".join(project(p) for p in s["projects"] if p.get("featured"))
    others = "\n".join(project(p) for p in s["projects"] if not p.get("featured"))
    page = (ROOT / "tools/template.html").read_text()
    for k, v in {
        "{{HERO}}": photo(s["photos"][0], "hero", eager=True),
        "{{BAND1}}": photo(s["photos"][1]),
        "{{BAND2}}": photo(s["photos"][2]),
        "{{BAND3}}": photo(s["photos"][3]),
        "{{INTRO}}": "".join(f"<p class='lede'>{inline(p)}</p>" for p in s["intro"]),
        "{{PROOF}}": "".join(f"<li>{inline(x)}</li>" for x in s["proof"]),
        "{{FEATURED}}": featured,
        "{{OTHERS}}": others,
        "{{WORK}}": "\n".join(job(j) for j in s["work"]),
        "{{EDU}}": "".join(f"<li>{inline(x)}</li>" for x in s["education"]),
        "{{HONORS}}": "".join(f"<li>{inline(x)}</li>" for x in s["honors"]),
        "{{SKILLS}}": "".join(f"<li>{inline(x)}</li>" for x in s["skills"]),
        "{{CLOSE_ICON}}": icon("close"),
        "{{CREDITS}}": " ".join(inline(c) for c in s["credits"]),
    }.items():
        page = page.replace(k, v)
    (ROOT / "index.html").write_text(page)
    print("index.html:", len(s["projects"]), "projects,", len(s["work"]), "jobs")


if __name__ == "__main__":
    build()
