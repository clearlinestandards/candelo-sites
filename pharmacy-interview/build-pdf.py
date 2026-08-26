#!/usr/bin/env python3
"""Render index.html to Diablo_Interview_Brief.pdf.

Builds a print variant of the page (light theme, all answers expanded, blanks
ruled for handwriting, no interactive chrome), inlines the Google Fonts as
data URIs so the PDF embeds them, then prints it with headless Chromium.

    python3 build-pdf.py

Needs network access on first run to fetch the fonts (cached in .fonts/), and
a Chromium binary — set CHROME to override the search path.
"""

import base64
import os
import re
import shutil
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, ".fonts")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

CHROME_CANDIDATES = [
    os.environ.get("CHROME"),
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    shutil.which("chromium"),
    shutil.which("chromium-browser"),
    shutil.which("google-chrome"),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req) as r:
        return r.read()


def inline_fonts(css_url):
    """Download the latin subset of each face and return @font-face rules
    with the woff2 payload embedded, so Chromium can subset it into the PDF."""
    os.makedirs(FONT_DIR, exist_ok=True)
    css = fetch(css_url).decode()
    blocks = re.findall(r"/\*\s*([a-z\-]+)\s*\*/\s*(@font-face\s*\{.*?\})", css, re.S)
    out = []
    for subset, block in blocks:
        if subset != "latin":
            continue
        url = re.search(r"url\((https://[^)]+\.woff2)\)", block)
        cached = os.path.join(FONT_DIR, url.group(1).rsplit("/", 1)[-1])
        if not os.path.exists(cached):
            with open(cached, "wb") as fh:
                fh.write(fetch(url.group(1)))
        with open(cached, "rb") as fh:
            payload = base64.b64encode(fh.read()).decode()
        block = block.replace(url.group(0), "url(data:font/woff2;base64,%s)" % payload)
        out.append(re.sub(r"\s*unicode-range:[^;]+;", "", block))
    if not out:
        sys.exit("no latin @font-face blocks found at %s" % css_url)
    return "\n".join(out)


PRINT_CSS = """
<style>
  @page { size: Letter; margin: 0.72in 0.8in; }

  html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }

  :root {
    --step--1: 8.6pt;
    --step-0:  10pt;
    --step-1:  12pt;
    --step-2:  15pt;
    --paper:   #FFFFFF;
    --shadow:  none;
  }

  body { font-size: var(--step-0); line-height: 1.5; background: #FFFFFF; }

  .wrap { max-width: none; margin: 0; padding: 0; gap: 1.3rem; }

  h1 { font-size: 27pt; letter-spacing: -.03em; }
  .standfirst { font-size: 11.5pt; max-width: 46ch; }
  .masthead { gap: .55rem; padding-bottom: .5rem; border-bottom: 2px solid var(--accent); }
  .fillnote {
    font-family: var(--f-mono);
    font-size: 8pt;
    line-height: 1.5;
    color: var(--muted);
    margin: .35rem 0 0;
    max-width: 62ch;
  }

  section { gap: .8rem; }
  .thesis, .script, .card, .row, .qa { box-shadow: none; }
  .thesis { padding: .95rem 1.1rem; }
  .thesis blockquote { font-size: 13.5pt; line-height: 1.3; }
  .script { padding: .9rem 1.05rem; gap: .6rem; }
  .card { padding: .8rem .85rem; gap: .35rem; }
  .pillars { gap: .6rem; grid-template-columns: 1fr 1fr; }
  .worksheet { gap: .5rem; }
  .row { padding: .7rem .85rem; gap: .3rem; }
  ol.track li { padding-bottom: .8rem; }

  /* blanks read as ruled fields on paper, not as UI */
  .slot {
    background: none;
    border-bottom: 1px solid var(--signal);
    color: var(--signal);
    min-width: 6.5rem;
    padding: 0 .25em;
    font-size: .88em;
  }
  .slot:empty::before { content: attr(data-hint); opacity: .55; font-style: italic; }

  /* every answer visible; no disclosure affordances on paper */
  .qa summary { padding: .6rem .85rem .4rem; font-size: 10pt; }
  .qa summary::after { display: none; }
  .qa .inner { padding: .5rem .85rem .65rem; gap: .5rem; }
  .qa + .qa { margin-top: .4rem; }
  .star { grid-template-columns: 3.5rem 1fr; gap: .25rem .7rem; }
  .star dd { line-height: 1.42; }

  /* Chromium collapses grid tracks in list items that cross a page break —
     lay these out in normal flow instead. */
  ul.plain { gap: .5rem; }
  ul.plain li { display: block; position: relative; padding-left: 1.05rem; max-width: 66ch; }
  ul.plain li::before { position: absolute; left: .15rem; top: .52em; margin-top: 0; }

  footer { padding-top: .7rem; font-size: 8pt; }

  /* pagination */
  .thesis, .script, .card, .row, .qa, ol.track li, ul.plain li { break-inside: avoid; }
  h2, h3, .eyebrow { break-after: avoid; }
  .masthead { break-after: avoid; }
  section { break-inside: auto; }
  a { color: inherit; text-decoration: none; }
</style>
"""

FILL_NOTE = (
    '<p class="fillnote">The ruled blanks are the work that\'s left. '
    "Write your real before-and-after figures into them — an approximate number "
    "beats an unquantified claim every time.</p>\n  </header>"
)

PRINT_FOOTER = (
    "<p>Prepared as an interview value package. Fill the blanks, rehearse the opening "
    "and the closer out loud, and cap every behavioral answer at two minutes.</p>"
)


def main():
    src = open(os.path.join(HERE, "index.html")).read()
    head, body = src.split("</head>", 1)

    link = re.search(r'<link rel="stylesheet" href="(https://fonts\.googleapis\.com[^"]*)">', head)
    head = re.sub(r'<link rel="preconnect"[^>]*>\s*', "", head)
    head = head.replace(link.group(0), "<style>\n" + inline_fonts(link.group(1)) + "\n</style>")
    head = head.replace('<html lang="en">', '<html lang="en" data-theme="light">')

    # strip everything that only makes sense on a screen
    body = re.sub(r"<script>.*?</script>", "", body, flags=re.S)
    body = re.sub(r'<div class="counter".*?</div>', "", body, flags=re.S)
    body = re.sub(r'<button class="reset".*?</button>', "", body, flags=re.S)
    body = re.sub(r"<p><a href=\"\./Diablo_Interview_Brief\.pdf\">.*?</p>", "", body, flags=re.S)
    body = body.replace('<details class="qa">', '<details class="qa" open>')
    body = body.replace("</header>", FILL_NOTE)
    body = re.sub(
        r"<p>Fill the orange fields and this becomes your script\..*?</p>",
        PRINT_FOOTER,
        body,
        flags=re.S,
    )

    print_html = os.path.join(HERE, ".print.html")
    open(print_html, "w").write(head + PRINT_CSS + "\n</head>" + body)

    chrome = next((c for c in CHROME_CANDIDATES if c and os.path.exists(c)), None)
    if not chrome:
        sys.exit("no Chromium found — set CHROME to a Chrome/Chromium binary")

    pdf = os.path.join(HERE, "Diablo_Interview_Brief.pdf")
    subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            "--virtual-time-budget=8000",
            "--print-to-pdf=" + pdf,
            "file://" + print_html,
        ],
        check=True,
        stderr=subprocess.DEVNULL,
    )
    os.remove(print_html)
    print("wrote %s (%d KB)" % (pdf, os.path.getsize(pdf) // 1024))


if __name__ == "__main__":
    main()
