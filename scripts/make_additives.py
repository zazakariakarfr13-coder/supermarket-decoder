#!/usr/bin/env python3
"""Build the E-number pages (additives/*.html) and, optionally, their Pinterest pins.

Usage:
  python scripts/make_additives.py pages            # writes additives/*.html
  python scripts/make_additives.py pins OUT_DIR     # renders 1000x1500 pins + captions.md into OUT_DIR

Content lives in scripts/additives_data.py.
"""
import html, json, shutil, subprocess, sys, tempfile
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from additives_data import ADDITIVES, BY_SLUG  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://zazakariakarfr13-coder.github.io/supermarket-decoder"
OUT = ROOT / "additives"
GUIDE = "https://zakarfr.gumroad.com/l/supermarket-decoder?utm_source=github_pages&utm_medium=additive_page&utm_campaign=supermarket_decoder&utm_content={slug}"
POCKET = "https://zakarfr.gumroad.com/l/e-number-pocket-reference?utm_source=github_pages&utm_medium=additive_page&utm_campaign=pocket_reference&utm_content={slug}"
KIT = "https://zakarfr.gumroad.com/l/complete-kit?utm_source=github_pages&utm_medium=additive_page&utm_campaign=complete_kit&utm_content={slug}"
E = html.escape

STYLE = """
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;margin:22px 0}
.fact{background:var(--paper,#FFFDF8);border:1px solid var(--line,#E2DCCF);border-radius:12px;padding:12px 14px}
.fact b{display:block;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted,#5A7363);margin-bottom:4px}
.fact span{font-size:15px;line-height:1.45}
.clue{display:inline-block;font-size:12px;font-weight:900;letter-spacing:.06em;text-transform:uppercase;border-radius:999px;padding:4px 10px;background:#FBE1D7;color:#9A3519}
.clue.no{background:#E2F1E7;color:#24613D}
.names{display:flex;flex-wrap:wrap;gap:8px;list-style:none;padding:0}
.names li{background:#fff;border:1px solid var(--line,#E2DCCF);border-radius:999px;padding:5px 12px;font-size:14px;font-weight:600}
.cta-row{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0 4px}
.pill{display:inline-block;background:var(--accent,#D9481C);color:#fff !important;text-decoration:none;font-weight:800;padding:12px 20px;border-radius:999px}
.pill.ghost{background:transparent;color:var(--ink,#13321F) !important;border:2px solid var(--line,#E2DCCF)}
.codes{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin:18px 0}
.code{display:block;background:var(--paper,#FFFDF8);border:1px solid var(--line,#E2DCCF);border-radius:14px;padding:16px 18px;text-decoration:none;color:inherit}
.code:hover{border-color:var(--ink,#13321F)}
.code .c{font-size:26px;font-weight:900;color:var(--accent,#D9481C);letter-spacing:-.02em}
.code .n{font-weight:800;margin:2px 0 4px}
.code .j{font-size:14px;color:var(--muted,#5A7363)}
"""


def head(title, desc, path, og_type="article", extra=""):
    url = f"{SITE}/{path}"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{E(title)} | Supermarket Decoder</title>
  <meta name="description" content="{E(desc)}">
  <link rel="canonical" href="{url}">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="Supermarket Decoder">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{E(title)}">
  <meta property="og:description" content="{E(desc)}">
  <meta property="og:image" content="{SITE}/assets/share/articles.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Supermarket Decoder: {E(title)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="{SITE}/assets/share/articles.png">
  <meta name="theme-color" content="#13321F">
  <link rel="stylesheet" href="../assets/site.css">
  <style>{STYLE}</style>{extra}
</head><body><header><a href="../index.html">Supermarket Decoder · Read · Decode · Swap</a></header><main>"""


FOOT = """</main><footer>© 2026 Zakaria Froud · <a href="../about.html">About</a> · <a href="../sources.html">Sources and method</a> · Educational content only, not medical or personalised nutrition advice.</footer></body></html>
"""


def additive_page(a):
    code, slug = a["code"], a["slug"]
    title = f"{code} ({a['short']}): What It Is, Uses and Safety"
    desc = a["answer"]
    if len(desc) > 158:
        desc = desc[:155].rsplit(" ", 1)[0] + "…"
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in a["faq"]]}
    extra = f'\n  <script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>'
    clue = ('<span class="clue">Yes: a NOVA processing clue</span>' if a["clue"]
            else '<span class="clue no">Not on its own</span>')
    where = "".join(f"<li>{E(w)}</li>" for w in a["where"])
    names = "".join(f"<li>{E(n)}</li>" for n in a["names"])
    faq = "".join(f"<h3>{E(q)}</h3><p>{E(ans)}</p>" for q, ans in a["faq"])
    related = "".join(
        f'<a class="code" href="{r}.html"><div class="c">{E(BY_SLUG[r]["code"])}</div><div class="n">{E(BY_SLUG[r]["short"])}</div><div class="j">{E(BY_SLUG[r]["job"])}</div></a>'
        for r in a["related"])
    decoder = "../decoder/#list=" + quote(a["sample"], safe="")
    return head(title, desc, f"additives/{slug}.html", extra=extra) + f"""
<div class="kicker">E-number lookup · {E(a['job'])}</div>
<h1>{E(code)}: {E(a['name'])}</h1>
<p class="lead">{E(a['answer'])}</p>
<div class="facts">
  <div class="fact"><b>Its job</b><span>{E(a['job'])}</span></div>
  <div class="fact"><b>Made from</b><span>{E(a['made_from'])}</span></div>
  <div class="fact"><b>On US labels</b><span>{E(a['us_name'])}</span></div>
  <div class="fact"><b>Vegan?</b><span>{E(a['vegan'])}</span></div>
  <div class="fact"><b>Ultra-processing clue?</b><span>{clue}</span></div>
</div>
<h2>Why is {E(code)} added to food?</h2>
<p>{E(a['why'])}</p>
<h2>Where you'll find it</h2>
<ul>{where}</ul>
<h2>Is {E(code)} safe? What the research says</h2>
<p>{E(a['safety'])}</p>
<div class="note">An E-number is an identifier used in the European food-additive numbering system. It does not mean the additive is currently authorised in every country or food category. Rules differ by region and can change, so check local rules. The code is not a danger rating.</div>
<h2>How it appears on labels</h2>
<ul class="names">{names}</ul>
<div class="panel">
  <p><strong>See it decoded.</strong> Open a typical label that contains {E(code)} in the free Ingredient Decoder, or paste your own.</p>
  <div class="cta-row"><a class="pill" href="{decoder}">Decode an example label →</a><a class="pill ghost" href="index.html">All E-numbers</a></div>
</div>
<h2>Questions people ask about {E(code)}</h2>
{faq}
<div class="panel" style="margin-top:22px;border:2px solid var(--gold,#F2B51C)"><p><strong>Keep every code in your pocket.</strong> The E-Number Pocket Reference covers 123 additive codes: what each one does, which are worth a second look, US label names and the clean-label names that hide an additive's job. A5 PDF for your phone or kitchen.</p><div class="cta-row"><a class="pill" href="{POCKET.format(slug=slug)}" target="_blank" rel="noopener">Get the pocket reference · $5</a><a class="pill ghost" href="{KIT.format(slug=slug)}" target="_blank" rel="noopener">Complete Kit · $13</a></div></div>
<div class="note" style="margin-top:22px"><strong>Want to read labels like this in your head?</strong> Supermarket Decoder is a 53-page illustrated ebook (PDF) with a printable cheat-sheet and a 14-day tracker. <a href="../index.html#inside">See what's inside</a> or <a href="{GUIDE.format(slug=slug)}" target="_blank" rel="noopener">get it on Gumroad ($9)</a>.</div>
<h2>Related E-numbers</h2>
<div class="codes">{related}</div>
<p><a class="back" href="index.html">← All E-numbers</a> · <a class="back" href="../articles/e-numbers-explained.html">E-numbers explained</a></p>
""" + FOOT


def index_page():
    cards = "".join(
        f'<a class="code" href="{a["slug"]}.html"><div class="c">{E(a["code"])}</div><div class="n">{E(a["name"])}</div><div class="j">{E(a["job"])}</div></a>'
        for a in ADDITIVES)
    return head("Common E-Numbers Explained: What Each Code Means",
                "Plain-language pages for the E-numbers people look up most: E471, E322, E330, E415, E407, E621, E951, E250, E171, E150d, E211 and E129 (Red 40).",
                "additives/", og_type="website") + f"""
<div class="kicker">E-number lookup</div>
<h1>Common E-numbers, explained one by one</h1>
<p class="lead">What each code is, why it's in your food, where you'll find it and what the research says, without the panic and without the marketing.</p>
<div class="codes">{cards}</div>
<div class="panel" style="border:2px solid var(--gold,#F2B51C)"><p><strong>Want all of them in your pocket?</strong> The E-Number Pocket Reference covers 123 codes on 16 phone-friendly pages, with traffic-light markers, US label names and the rules that differ between countries.</p><div class="cta-row"><a class="pill" href="{POCKET.format(slug='index')}" target="_blank" rel="noopener">Get the pocket reference · $5</a><a class="pill ghost" href="{KIT.format(slug='index')}" target="_blank" rel="noopener">Complete Kit · $13</a></div></div>
<div class="panel"><p><strong>Looking for a code that isn't here?</strong> The free <a href="../decoder/">Ingredient Decoder</a> knows more than 300 E-numbers. Paste a whole ingredient list and it explains every one.</p></div>
<div class="note">An E-number means an additive has been assessed and approved in Europe. It's an identifier, not a danger rating. <a href="../articles/e-numbers-explained.html">How to read E-numbers sensibly →</a></div>
<p><a class="back" href="../free-resources/">← All free resources</a></p>
""" + FOOT


def build_pages():
    OUT.mkdir(exist_ok=True)
    for a in ADDITIVES:
        (OUT / f"{a['slug']}.html").write_text(additive_page(a), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(index_page(), encoding="utf-8", newline="\n")
    print(f"wrote {len(ADDITIVES) + 1} pages to additives/")


def build_pins(out_dir):
    import make_pins
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    exe = make_pins.browser()
    tmp = Path(tempfile.mkdtemp())
    captions = ["# E-number pins: titles, descriptions and links\n",
                "Post one or two a day rather than all at once. Suggested board: **Ingredients & Hidden Sugars** "
                "(or create **E-Numbers & Food Additives Explained**).\n"]
    for i, a in enumerate(ADDITIVES, 1):
        p = a["pin"]
        spec = dict(tag=f"{a['code']} · {a['job'].split(' (')[0].split(' and ')[0].upper()}", big=True, ts=150,
                    kicker=p["kicker"], title=p["title"], lead=p["lead"],
                    rows=[(lab, txt, "") for lab, txt in p["rows"]], takeaway=p["takeaway"])
        src = tmp / f"{a['slug']}.html"
        src.write_text(make_pins.page(spec), encoding="utf-8")
        name = f"{i:02d}-{a['slug']}-pin.png"
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--window-size=1000,1500", "--virtual-time-budget=8000", f"--user-data-dir={tmp / 'profile'}",
                        f"--screenshot={out / name}", src.as_uri()], check=True, capture_output=True, timeout=120)
        link = f"{SITE}/additives/{a['slug']}.html?utm_source=pinterest&utm_medium=organic&utm_campaign=additive_pages&utm_content={a['slug']}"
        captions.append(f"""
## {i}. {a['code']} · {a['short']}

**Image:** {name}

**Title:** What Is {a['code']} ({a['short']})? What It Does and Is It Safe

**Description:** {a['answer']} See where it hides, how it appears on US labels and what the research says. Save it for your next grocery trip.

**Link:** {link}

**Alt text:** Vertical educational pin explaining {a['code']}, {a['name'].lower()}: its job ({a['job'].lower()}), what it's made from, where it's found and one key fact.
""")
        print("rendered", name)
    (out / "captions.md").write_text("".join(captions), encoding="utf-8")
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "pages":
        build_pages()
    elif len(sys.argv) >= 3 and sys.argv[1] == "pins":
        build_pins(sys.argv[2])
    else:
        sys.exit(__doc__)
