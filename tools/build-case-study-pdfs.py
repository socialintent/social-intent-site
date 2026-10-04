"""Build a branded A4 PDF for every case study in src/work/*.md.

Run:  python3 tools/build-case-study-pdfs.py
Needs: python3 with playwright + markdown (pip install playwright markdown), and Chromium for Playwright.
Output: src/assets/downloads/<slug>.pdf  (Eleventy copies assets/ through to the built site.)
"""
import re, json, pathlib, asyncio, base64, html
import markdown

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
OUT = SRC / "assets" / "downloads"
OUT.mkdir(parents=True, exist_ok=True)
site = json.loads((SRC / "_data" / "site.json").read_text())

def front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    fm, body = m.group(1), m.group(2)
    data = {}
    facts = []
    for line in fm.splitlines():
        if line.startswith("  - {"):
            n = re.search(r'n:\s*"([^"]*)"', line).group(1)
            label = re.search(r'label:\s*"([^"]*)"', line).group(1)
            facts.append((n, label))
        elif ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip().strip('"')
    data["facts"] = facts
    return data, body

def data_uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()

LOGO_WHITE = data_uri(SRC / "assets/img/si-logo-landscape-white-yellow.svg", "image/svg+xml")
LOGO_BLACK = data_uri(SRC / "assets/img/si-logo-landscape-black-yellow.svg", "image/svg+xml")
FONT_HAND = data_uri(SRC / "assets/fonts/pink-champagne-regular.woff2", "font/woff2")
ARROW = data_uri(SRC / "assets/img/hand-arrow3-black.svg", "image/svg+xml")

CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Josefin+Sans:wght@300;400;700&family=Source+Sans+3:wght@400;600&display=swap');
@font-face {{ font-family: 'Pink Champagne'; src: url('{FONT_HAND}') format('woff2'); }}
@page {{ size: A4; margin: 0; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
body {{ font-family: 'Source Sans 3', 'Source Sans Pro', Arial, sans-serif; font-size: 10.6pt; line-height: 1.5; color: #141414; }}
.page {{ width: 210mm; min-height: 297mm; padding: 0 18mm 22mm; position: relative; page-break-after: always; }}
.page:last-child {{ page-break-after: auto; }}
.band {{ background: #000; color: #fff; margin: 0 -18mm; padding: 14mm 18mm 12mm; border-bottom: 5px solid #FEDB00; }}
.band img {{ width: 62mm; display: block; margin-bottom: 10mm; }}
.band .eyebrow {{ font-family: 'Josefin Sans', sans-serif; font-size: 8.5pt; letter-spacing: .12em; text-transform: uppercase; color: #FEDB00; margin: 0 0 4mm; }}
.band h1 {{ font-family: 'Josefin Sans', sans-serif; font-weight: 700; font-size: 26pt; line-height: 1.05; margin: 0 0 4mm; max-width: 150mm; letter-spacing: -0.01em; }}
.band .lead {{ font-size: 12pt; color: #D9D9D9; max-width: 150mm; margin: 0; }}
.facts {{ display: flex; gap: 4mm; margin: 8mm 0 6mm; }}
.facts div {{ flex: 1; background: #F4F3EC; border-top: 4px solid #FEDB00; padding: 3mm 4mm 2.5mm; }}
.facts strong {{ display: block; font-family: 'Josefin Sans', sans-serif; font-size: 20pt; line-height: 1; }}
.facts span {{ font-size: 8.5pt; color: #5B5A54; }}
h2 {{ font-family: 'Josefin Sans', sans-serif; font-weight: 700; font-size: 14pt; margin: 7mm 0 2mm; letter-spacing: -0.01em; }}
p {{ margin: 0 0 3mm; }}
ul {{ margin: 0 0 3mm; padding-left: 5mm; }}
li {{ margin-bottom: 1mm; }}
.cols {{ column-count: 2; column-gap: 9mm; }}
.cols h2:first-child {{ margin-top: 0; }}
blockquote {{ break-inside: avoid; margin: 6mm 0; background: #000; color: #fff; padding: 6mm 7mm; border-left: 5px solid #FEDB00; font-family: 'Josefin Sans', sans-serif; font-weight: 300; font-size: 12pt; line-height: 1.35; }}
blockquote p {{ margin: 0 0 3mm; }}
blockquote p::before {{ content: '\\201C'; color: #FEDB00; font-weight: 700; }}
blockquote cite {{ display: block; font-style: normal; font-family: 'Source Sans 3', sans-serif; font-size: 9pt; color: #C9C8C0; }}
.hand {{ font-family: 'Pink Champagne', cursive; font-size: 22pt; color: #000; white-space: nowrap; }}
.footer {{ position: absolute; left: 18mm; right: 18mm; bottom: 10mm; border-top: 1px solid #E2E0D6; padding-top: 3mm; font-size: 8.5pt; color: #5B5A54; display: flex; justify-content: space-between; align-items: center; }}
.footer img {{ width: 36mm; }}
.cta {{ break-inside: avoid; margin-top: 8mm; background: #FEDB00; padding: 6mm 7mm; display: flex; justify-content: space-between; align-items: center; gap: 6mm; }}
.cta > div:first-child {{ flex: 1; }}
.cta h3 {{ font-family: 'Josefin Sans', sans-serif; font-weight: 700; font-size: 13pt; margin: 0 0 1.5mm; }}
.cta p {{ margin: 0; font-size: 10pt; }}
.cta .arrow {{ display: flex; align-items: center; gap: 3mm; }}
.cta .arrow img {{ width: 22mm; height: 8mm; display: block; }}
.glance {{ font-size: 9pt; color: #5B5A54; margin: 0 0 4mm; }}
.glance b {{ color: #141414; font-family: 'Josefin Sans', sans-serif; }}
"""

def build_html(data, body_md):
    body_html = markdown.markdown(body_md)
    facts = "".join(f"<div><strong>{html.escape(n)}</strong><span>{html.escape(l)}</span></div>" for n, l in data["facts"])
    quote = ""
    if data.get("quote"):
        who = data.get("quoteBy", "")
        if data.get("quoteRole"): who += ", " + data["quoteRole"]
        quote = f"<blockquote><p>{html.escape(data['quote'])}</p><cite>{html.escape(who)}</cite></blockquote>"
    glance = f"<p class='glance'><b>Client</b> {html.escape(data['client'])} &nbsp;·&nbsp; <b>What we did</b> {html.escape(data['services'])}" + (f" &nbsp;·&nbsp; <b>When</b> {html.escape(data['year'])}" if data.get("year") else "") + "</p>"
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="page">
  <div class="band">
    <img src="{LOGO_WHITE}" alt="Social Intent">
    <p class="eyebrow">Case study · {html.escape(data['client'])}</p>
    <h1>{html.escape(data['title'])}</h1>
    <p class="lead">{html.escape(data['summary'])}</p>
  </div>
  <div class="facts">{facts}</div>
  {glance}
  <div class="cols">{body_html}</div>
  {quote}
  <div class="cta">
    <div><h3>Could your board use a critical friend?</h3><p>Book a free 30-minute call: {site['calendly']} &nbsp;·&nbsp; {site['email']} &nbsp;·&nbsp; {site['phone']}</p></div>
    <div class="arrow"><span class="hand">no hard sell</span><img src="{ARROW}" alt=""></div>
  </div>
  <div class="footer"><img src="{LOGO_BLACK}" alt="Social Intent"><span>Social Intent Limited · {site['url'].replace('https://','')} · Published with the client's approval</span></div>
</div>
</body></html>"""

async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        for md in sorted((SRC / "work").glob("*.md")):
            data, body = front_matter(md.read_text())
            await pg.set_content(build_html(data, body), wait_until="load")
            await pg.wait_for_timeout(600)
            out = OUT / f"{md.stem}.pdf"
            await pg.pdf(path=str(out), format="A4", print_background=True, prefer_css_page_size=True)
            print("wrote", out.relative_to(ROOT), out.stat().st_size, "bytes")
        await b.close()

asyncio.run(main())
