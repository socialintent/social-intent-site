"""Build the paid guides (the Payhip products) as branded A4 PDFs.

Run:    python3 tools/build-guides.py            # all guides
        python3 tools/build-guides.py sorp       # one guide (by file stem)
Needs:  python3 with playwright, markdown, pypdf (pip install playwright markdown pypdf) and Chromium for Playwright.
Input:  guides/<slug>.md   (front matter + Markdown; <!-- page --> starts a new page)
Output: guides-pdf/<slug>.pdf, guides-pdf/<slug>-cover.png (portrait) and guides-pdf/<slug>-cover-square.png (for Payhip)

The output folder is outside src/, so the PDFs are never published on the site. Upload them to Payhip only.
"""
import re, sys, json, pathlib, asyncio, base64, html, io, tempfile
import markdown
from pypdf import PdfReader, PdfWriter

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
IN = ROOT / "guides"
OUT = ROOT / "guides-pdf"
OUT.mkdir(parents=True, exist_ok=True)
site = json.loads((SRC / "_data" / "site.json").read_text())


def data_uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


LOGO_WHITE = data_uri(SRC / "assets/img/si-logo-landscape-white-yellow.svg", "image/svg+xml")
LOGO_BLACK = data_uri(SRC / "assets/img/si-logo-landscape-black-yellow.svg", "image/svg+xml")
LOGO_MAIN_BLACK = data_uri(SRC / "assets/img/si-logo-main-black-yellow.svg", "image/svg+xml")
CIRCLES = data_uri(SRC / "assets/img/si-3circles-yellow.svg", "image/svg+xml")
FONT_HAND = data_uri(SRC / "assets/fonts/pink-champagne-regular.woff2", "font/woff2")
ARROW = data_uri(SRC / "assets/img/hand-arrow3-black.svg", "image/svg+xml")
PATTERN = data_uri(SRC / "assets/img/data-pattern.jpg", "image/jpeg")

YELLOW = "#FEDB00"

BASE_CSS = f"""
@font-face {{ font-family: 'Pink Champagne'; src: url('{FONT_HAND}') format('woff2'); }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
body {{ font-family: 'Source Sans 3', 'Source Sans Pro', Arial, sans-serif; font-size: 9.8pt; line-height: 1.42; color: #141414; }}
h1, h2, h3, h4 {{ font-family: 'Josefin Sans', sans-serif; font-weight: 700; letter-spacing: -0.01em; line-height: 1.1; }}
.hand {{ font-family: 'Pink Champagne', cursive; color: #000; white-space: nowrap; }}
"""

BODY_CSS = BASE_CSS + f"""
@page {{ size: A4; margin: 18mm 18mm 20mm 18mm; }}
h2 {{ font-size: 21pt; margin: 10mm 0 4mm; break-after: avoid; }}
.eyebrow + h2, .pb + h2 {{ margin-top: 0; }}
h3 {{ break-after: avoid; }}
h3 {{ font-size: 13pt; margin: 6mm 0 2mm; }}
h4 {{ font-size: 10.5pt; margin: 4mm 0 1mm; text-transform: uppercase; letter-spacing: .08em; font-weight: 700; }}
p {{ margin: 0 0 3mm; }}
ul, ol {{ margin: 0 0 3mm; padding-left: 5mm; }}
li {{ margin-bottom: 1.2mm; }}
li > p {{ margin: 0; }}
strong {{ font-weight: 600; }}
a {{ color: inherit; }}
hr {{ border: 0; border-top: 1px solid #E2E0D6; margin: 5mm 0; }}
.pb {{ page-break-before: always; }}
.eyebrow {{ font-family: 'Josefin Sans', sans-serif; font-size: 8.5pt; letter-spacing: .14em; text-transform: uppercase; color: #5B5A54; margin: 0 0 3mm; }}
.eyebrow b {{ color: #000; background: {YELLOW}; padding: .5mm 2mm; margin-right: 2mm; font-weight: 700; }}
.lead {{ font-size: 12pt; line-height: 1.4; color: #2A2A2A; margin: 0 0 5mm; max-width: 150mm; }}
.key {{ break-inside: avoid; margin: 5mm 0; background: #000; color: #fff; padding: 5mm 6mm 4.5mm; border-left: 5px solid {YELLOW}; }}
.key .k {{ font-family: 'Josefin Sans', sans-serif; font-size: 8.5pt; letter-spacing: .14em; text-transform: uppercase; color: {YELLOW}; margin: 0 0 2mm; }}
.key p {{ margin: 0 0 2mm; font-family: 'Josefin Sans', sans-serif; font-weight: 300; font-size: 12pt; line-height: 1.35; }}
.key p:last-child {{ margin: 0; }}
.key ul {{ margin: 0; }}
.note {{ break-inside: avoid; margin: 5mm 0; background: {YELLOW}; padding: 4.5mm 6mm 4mm; }}
.note .k {{ font-family: 'Josefin Sans', sans-serif; font-size: 8.5pt; letter-spacing: .14em; text-transform: uppercase; margin: 0 0 1.5mm; }}
.note p:last-child {{ margin: 0; }}
.soft {{ break-inside: avoid; margin: 5mm 0; background: #F4F3EC; padding: 4.5mm 6mm 4mm; border-top: 4px solid {YELLOW}; }}
.soft .k {{ font-family: 'Josefin Sans', sans-serif; font-size: 8.5pt; letter-spacing: .14em; text-transform: uppercase; margin: 0 0 1.5mm; color: #5B5A54; }}
.soft p:last-child {{ margin: 0; }}
.label {{ display: inline-block; font-family: 'Josefin Sans', sans-serif; font-size: 7.5pt; letter-spacing: .1em; text-transform: uppercase; padding: .6mm 1.8mm .3mm; border: 1.5px solid #000; border-radius: 3px; margin-right: 1.5mm; vertical-align: middle; }}
.label.ev {{ background: #000; color: #fff; }}
.label.in {{ background: {YELLOW}; border-color: {YELLOW}; }}
.label.de {{ background: #fff; }}
table {{ width: 100%; border-collapse: collapse; margin: 3mm 0 5mm; font-size: 8.8pt; line-height: 1.3; break-inside: auto; }}
th, td {{ text-align: left; vertical-align: top; padding: 2.2mm 2.5mm; border-bottom: 1px solid #E2E0D6; }}
th {{ font-family: 'Josefin Sans', sans-serif; font-size: 8.2pt; letter-spacing: .08em; text-transform: uppercase; background: #000; color: #fff; border-bottom: 3px solid {YELLOW}; }}
tr {{ break-inside: avoid; }}
td:first-child {{ font-weight: 600; }}
table.score td:not(:first-child) {{ text-align: center; width: 15mm; }}
table.score th:not(:first-child) {{ text-align: center; }}
table.score td:not(:first-child)::before {{ content: ''; display: inline-block; width: 4mm; height: 4mm; border: 1.5px solid #000; border-radius: 50%; vertical-align: middle; }}
table.score tr:last-child td:not(:first-child)::before {{ border-radius: 2px; }}
.check {{ list-style: none; padding-left: 0; }}
.check li {{ position: relative; padding-left: 8mm; margin-bottom: 2mm; }}
.check li::before {{ content: ''; position: absolute; left: 0; top: 1mm; width: 4.2mm; height: 4.2mm; border: 1.8px solid #000; border-radius: 2px; }}
.steps {{ list-style: none; padding: 0; margin: 3mm 0 5mm; counter-reset: step; }}
.steps li {{ counter-increment: step; position: relative; padding: 2mm 0 2mm 13mm; border-top: 1px solid #E2E0D6; break-inside: avoid; }}
.steps li::before {{ content: counter(step); position: absolute; left: 0; top: 2.2mm; width: 8.5mm; height: 8.5mm; border-radius: 50%; background: {YELLOW}; font-family: 'Josefin Sans', sans-serif; font-weight: 700; display: flex; align-items: center; justify-content: center; padding-top: .8mm; }}
.steps li b:first-child {{ font-family: 'Josefin Sans', sans-serif; font-weight: 700; font-size: 10.5pt; margin-right: 1mm; }}
.flow {{ margin: 3mm 0 5mm; }}
.flow .q {{ break-inside: avoid; display: flex; gap: 4mm; align-items: stretch; margin-bottom: 2.5mm; }}
.flow .q > div:first-child {{ flex: 0 0 72mm; background: #000; color: #fff; padding: 3.5mm 4mm; font-family: 'Josefin Sans', sans-serif; font-weight: 700; font-size: 10.5pt; line-height: 1.25; }}
.flow .q > div:last-child {{ flex: 1; background: #F4F3EC; padding: 3.5mm 4mm; font-size: 9.6pt; }}
.flow .q b {{ background: {YELLOW}; padding: 0 1.5mm; font-family: 'Josefin Sans', sans-serif; font-size: 8.5pt; letter-spacing: .06em; text-transform: uppercase; }}
.two {{ display: flex; gap: 6mm; margin: 3mm 0 5mm; }}
.two > div {{ flex: 1; }}
.two h4 {{ margin-top: 0; }}
.two p.small {{ font-size: 8.8pt; line-height: 1.35; }}
.cards {{ display: flex; gap: 4mm; margin: 3mm 0 5mm; }}
.cards > div {{ flex: 1; background: #F4F3EC; border-top: 4px solid {YELLOW}; padding: 3.5mm 4mm 3mm; font-size: 9.4pt; break-inside: avoid; }}
.cards h4 {{ margin-top: 0; }}
.cards strong.big {{ display: block; font-family: 'Josefin Sans', sans-serif; font-size: 20pt; line-height: 1; margin-bottom: 1.5mm; }}
.quote {{ break-inside: avoid; margin: 6mm 0; font-family: 'Josefin Sans', sans-serif; font-weight: 300; font-size: 14pt; line-height: 1.35; padding-left: 6mm; border-left: 5px solid {YELLOW}; }}
.annot {{ break-inside: avoid; display: flex; align-items: center; gap: 3mm; margin: 2mm 0 5mm; }}
.annot img {{ width: 22mm; height: 8mm; }}
.annot .hand {{ font-size: 20pt; }}
.contents {{ list-style: none; padding: 0; margin: 3mm 0 5mm; column-count: 2; column-gap: 8mm; }}
.contents li {{ display: flex; align-items: baseline; gap: 3mm; padding: 1.8mm 0; border-bottom: 1px solid #E2E0D6; font-family: 'Josefin Sans', sans-serif; font-weight: 700; font-size: 9.6pt; break-inside: avoid; }}
.contents li span:first-child {{ flex: 1; }}
.contents li span:last-child {{ font-weight: 400; color: #5B5A54; }}
.contents li.sub {{ font-weight: 400; font-size: 9.8pt; padding-left: 6mm; }}
.contents li.sub span:first-child {{ font-family: 'Source Sans 3', sans-serif; }}
.small {{ font-size: 8.8pt; color: #5B5A54; }}
.cta {{ break-inside: avoid; margin: 6mm 0; background: {YELLOW}; padding: 6mm 7mm; display: flex; justify-content: space-between; align-items: center; gap: 6mm; }}
.cta > div:first-child {{ flex: 1; }}
.cta h3 {{ margin: 0 0 1.5mm; font-size: 14pt; }}
.cta p {{ margin: 0; }}
.cta .arrow {{ display: flex; align-items: center; gap: 3mm; }}
.cta .arrow img {{ width: 22mm; height: 8mm; display: block; }}
table.blank td {{ height: 11mm; }}
.ws {{ margin: 3mm 0 5mm; border-top: 2px solid #000; }}
.ws .wsrow {{ display: flex; border-bottom: 1px solid #000; min-height: 24mm; break-inside: avoid; }}
.ws .wsrow.tall {{ min-height: 40mm; }}
.ws .wsk {{ flex: 0 0 46mm; background: #F4F3EC; padding: 2.5mm 3mm; font-family: 'Josefin Sans', sans-serif; font-weight: 700; font-size: 9.5pt; line-height: 1.2; }}
.ws .wsv {{ flex: 1; padding: 2.5mm 3mm; font-size: 8.4pt; color: #5B5A54; }}
.back {{ font-size: 8.6pt; color: #5B5A54; line-height: 1.4; }}
.cols2 {{ column-count: 2; column-gap: 8mm; }}
.cols2 li {{ break-inside: avoid; }}
.cols2 h4:first-child {{ margin-top: 0; }}
.back h4 {{ color: #141414; }}
"""

COVER_CSS = BASE_CSS + f"""
@page {{ size: A4; margin: 0; }}
.cover {{ width: 210mm; height: 297mm; position: relative; overflow: hidden; background: {YELLOW}; }}
.cover .pattern {{ position: absolute; inset: 0; background: url('{PATTERN}') center/cover; opacity: .28; }}
.cover .top {{ position: absolute; left: 0; right: 0; top: 0; height: 58mm; background: #000; padding: 16mm 18mm 0; }}
.cover .top img {{ width: 66mm; display: block; }}
.cover .top .kind {{ position: absolute; right: 18mm; top: 19mm; font-family: 'Josefin Sans', sans-serif; font-size: 8.5pt; letter-spacing: .14em; text-transform: uppercase; color: {YELLOW}; text-align: right; line-height: 1.6; }}
.cover .title {{ position: absolute; left: 18mm; right: 18mm; top: 86mm; }}
.cover .title .eyebrow {{ font-family: 'Josefin Sans', sans-serif; font-size: 9.5pt; letter-spacing: .14em; text-transform: uppercase; margin: 0 0 6mm; }}
.cover h1 {{ font-size: 40pt; line-height: 1.02; margin: 0 0 7mm; max-width: 165mm; }}
.cover .sub {{ font-size: 15pt; line-height: 1.35; max-width: 150mm; margin: 0; color: #141414; }}
.cover .ring {{ position: absolute; right: -32mm; bottom: -28mm; width: 120mm; height: 120mm; border: 16mm solid #000; border-radius: 50%; opacity: .92; }}
.cover .ring2 {{ position: absolute; right: 26mm; bottom: 80mm; width: 30mm; height: 30mm; border: 7mm solid #000; border-radius: 50%; }}
.cover .annot {{ position: absolute; left: 18mm; bottom: 44mm; }}
.cover .annot .hand {{ font-size: 30pt; transform: rotate(-4deg); display: inline-block; }}
.cover .foot {{ position: absolute; left: 18mm; right: 18mm; bottom: 16mm; display: flex; justify-content: space-between; align-items: flex-end; font-family: 'Josefin Sans', sans-serif; font-size: 9pt; letter-spacing: .08em; text-transform: uppercase; }}
.cover .foot img {{ width: 44mm; display: block; }}
"""


def front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    data = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip().strip('"')
    return data, m.group(2)


def md_to_html(md_text):
    # <!-- page --> starts a new page; everything else is Markdown (with raw HTML allowed)
    md_text = md_text.replace("<!-- page -->", '\n<div class="pb"></div>\n')
    return markdown.markdown(md_text, extensions=["tables", "attr_list", "md_in_html", "sane_lists"])


def contents_html(items):
    lis = "".join(f'<li class="{cls}"><span>{html.escape(t)}</span><span>{p}</span></li>' for cls, t, p in items)
    return f'<ul class="contents">{lis}</ul>'


def body_html(data, body, toc):
    body = body.replace("{{CONTENTS}}", toc)
    body = body.replace("{{CALENDLY}}", site["calendly"]).replace("{{EMAIL}}", site["email"]).replace("{{PHONE}}", site["phone"]).replace("{{ARROW}}", ARROW)
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{BODY_CSS}</style></head><body>{md_to_html(body)}</body></html>"


def cover_html(data, pages):
    return f"""<!doctype html><html><head><meta charset='utf-8'><style>{COVER_CSS}</style></head><body>
<div class="cover">
  <div class="pattern"></div>
  <div class="top"><img src="{LOGO_WHITE}" alt="Social Intent"><div class="kind">{html.escape(data['kind'])}<br>{pages} pages</div></div>
  <div class="ring"></div><div class="ring2"></div>
  <div class="title">
    <p class="eyebrow">{html.escape(data['eyebrow'])}</p>
    <h1>{data['title']}</h1>
    <p class="sub">{html.escape(data['subtitle'])}</p>
  </div>
  <div class="annot"><span class="hand">{html.escape(data['hand'])}</span></div>
  <div class="foot"><span>For {html.escape(data['audience'])}</span><span>Edition {html.escape(data['edition'])}</span></div>
</div></body></html>"""


def footer_template(title):
    return f"""<div style="width:100%;font-family:'Josefin Sans',sans-serif;font-size:7.5pt;letter-spacing:.08em;text-transform:uppercase;color:#5B5A54;padding:0 18mm;display:flex;justify-content:space-between;align-items:center;">
<span>{html.escape(title)} &nbsp;·&nbsp; Social Intent</span><span>Page <span class="pageNumber"></span></span></div>"""


async def render_pdf(pg, html_src, path, footer=None):
    await pg.set_content(html_src, wait_until="load")
    await pg.wait_for_timeout(500)
    kw = dict(path=str(path), format="A4", print_background=True, prefer_css_page_size=True)
    if footer:
        kw.update(display_header_footer=True, header_template="<span></span>", footer_template=footer, margin=dict(top="18mm", right="18mm", bottom="20mm", left="18mm"))
    await pg.pdf(**kw)


def find_pages(pdf_path, headings):
    """Map each heading text to the first PDF page (1-based) whose text contains it."""
    r = PdfReader(str(pdf_path))
    texts = [" ".join((p.extract_text() or "").split()) for p in r.pages]
    found = {}
    for h in headings:
        key = " ".join(h.split())
        for i, t in enumerate(texts):
            if key in t:
                found[h] = i + 1
                break
    return found, len(r.pages)


async def build(pg, md_path):
    data, body = front_matter(md_path.read_text())
    # headings for the contents: ## (sections) and ### marked with {: .toc}
    secs = [(m.group(1).strip()) for m in re.finditer(r"^## (.+)$", body, re.M)]
    secs = [re.sub(r"\s*\{:.*\}\s*$", "", s) for s in secs]
    # pass 1: no contents, find pages
    tmp = pathlib.Path(tempfile.mkdtemp())
    await render_pdf(pg, body_html(data, body, ""), tmp / "p1.pdf", footer_template(data["title_plain"]))
    pages, n = find_pages(tmp / "p1.pdf", secs)
    toc = contents_html([("", s, pages.get(s, "")) for s in secs])
    await render_pdf(pg, body_html(data, body, toc), tmp / "body.pdf", footer_template(data["title_plain"]))
    total = len(PdfReader(str(tmp / "body.pdf")).pages) + 1
    await render_pdf(pg, cover_html(data, total), tmp / "cover.pdf")
    # cover image for Payhip
    await pg.set_content(cover_html(data, total), wait_until="load")
    await pg.wait_for_timeout(300)
    await pg.set_viewport_size({"width": 794, "height": 1123})
    await pg.screenshot(path=str(OUT / f"{md_path.stem}-cover.png"), clip={"x": 0, "y": 0, "width": 794, "height": 1123}, scale="device")
    # merge
    w = PdfWriter()
    for part in ("cover.pdf", "body.pdf"):
        for p in PdfReader(str(tmp / part)).pages:
            w.add_page(p)
    w.add_metadata({"/Title": data["title_plain"], "/Author": "Social Intent Limited", "/Subject": data["subtitle"]})
    out = OUT / f"{md_path.stem}.pdf"
    with open(out, "wb") as f:
        w.write(f)
    # square cover for Payhip: cover centred on black
    from PIL import Image
    cov = Image.open(OUT / f"{md_path.stem}-cover.png").convert("RGB")
    sq = Image.new("RGB", (1200, 1200), "#000000")
    h = 1080
    wdt = int(cov.width * h / cov.height)
    cov2 = cov.resize((wdt, h), Image.LANCZOS)
    sq.paste(cov2, ((1200 - wdt) // 2, (1200 - h) // 2))
    sq.save(OUT / f"{md_path.stem}-cover-square.png")
    print(f"wrote {out.relative_to(ROOT)}  ({total} pages, {out.stat().st_size // 1024} KB)  sections:", pages)
    return total


async def main(only=None):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(device_scale_factor=2)
        for md in sorted(IN.glob("*.md")):
            if only and md.stem != only:
                continue
            await build(pg, md)
        await b.close()


asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else None))
