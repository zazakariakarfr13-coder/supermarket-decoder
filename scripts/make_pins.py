#!/usr/bin/env python3
"""Render branded 1000x1500 Pinterest Pins to pins/*.png using headless Edge/Chrome.

Usage: python scripts/make_pins.py [slug ...]
"""
import html, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pins"
BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "google-chrome", "chromium", "msedge",
]

TINTS = ["#DDEBDD", "#F9E4DC", "#FBEFC6", "#FFFDF8"]

# Each pin: kicker, title (use \n for line breaks), lead, body (rows or cards), takeaway, tag
PINS = {
    "kids-snacks": dict(
        tag="KIDS' SNACKS", ts=80, kicker="A calm checklist for parents",
        title="Check the label\non kids' snacks",
        lead="Bright packaging is not the full story. Turn the pack over.",
        rows=[("1", "First ingredients", "What makes up most of the snack?"),
              ("2", "Added Sugars", "Check grams and %DV per serving, not the badge."),
              ("3", "Serving size", "Is it the amount your child actually eats?"),
              ("4", "Fruit claims", "“Made with real fruit” can mean a little. Find it in the list.")],
        takeaway="No food rules, no panic: one quick check before it goes in the cart."),
    "processed-vs-ultra": dict(
        tag="NOVA SCALE", ts=92, kicker="Processing is a scale, not a yes / no",
        title="Processed ≠\nultra-processed",
        lead="The NOVA system sorts foods into four groups by how they are processed.",
        rows=[("1", "Unprocessed / minimally processed", "Fresh fruit · eggs · plain milk · rice"),
              ("2", "Culinary ingredients", "Olive oil · butter · sugar · salt"),
              ("3", "Processed foods", "Canned beans · cheese · simple bakery bread"),
              ("4", "Ultra-processed foods", "Soft drinks · many packaged snacks · many sweetened cereals")],
        takeaway="NOVA describes processing. It is not a complete health score."),
    "first-three": dict(
        tag="INGREDIENT ORDER", big=True, kicker="A 5-second habit",
        title="Read the first\n3 ingredients",
        lead="Ingredients are listed in descending order by weight.",
        rows=[("1", "Whole wheat flour", "Listed first: there is more of it than anything else"),
              ("2", "Water", "Second by weight"),
              ("3", "Yeast", "Third by weight"),
              ("4", "Salt", "Smaller amount, but still worth noticing")],
        takeaway="The first three give a quick snapshot of the recipe. Then read the full list."),
    "front-claims": dict(
        tag="FRONT-OF-PACK", ts=84, kicker="The front sells. The back tells.",
        title="4 front-of-pack\nwords, decoded",
        lead="A claim tells you one thing. The back label tells you the rest.",
        rows=[("“Natural”", "No formal FDA definition for most foods", "Read the ingredient list"),
              ("“Multigrain”", "More than one grain, not always whole grain", "Look for “whole” grains first"),
              ("“Made with real fruit”", "Some fruit is in there, the amount varies", "Find the fruit in the list"),
              ("“Good source of fiber”", "10–19% Daily Value per serving", "Check the serving size")],
        takeaway="Use the claim as a clue, then check the label before deciding."),
    "fourteen-days": dict(
        tag="14-DAY PLAN", kicker="Start small. Keep what works.",
        title="14 days.\nOne small swap.",
        lead="Build a label-reading habit without overhauling your whole cart.",
        grid=True,
        takeaway="Supermarket Decoder includes a printable 14-day tracker and cheat-sheet.",
        cta="53-page PDF guide · $9"),
    "e-numbers": dict(
        tag="E-NUMBERS", big=True, ts=92, kicker="Additives, without the panic",
        title="E-number ≠\nautomatically bad",
        lead="The code identifies an additive. Learn its job before judging it.",
        cards=[("E300", "Vitamin C", "Antioxidant"),
               ("E330", "Citric acid", "Acidity regulator"),
               ("E440", "Pectin", "Thickener / gelling agent"),
               ("E500", "Sodium carbonates", "Raising agent (incl. baking soda)")],
        takeaway="E-numbers are used in Europe. U.S. labels list additives by name instead."),
    "contains-may-contain": dict(
        tag="ALLERGENS", big=True, kicker="Two phrases, two different messages",
        title="“Contains” vs\n“May contain”",
        lead="One is about the recipe. The other is about possible cross-contact.",
        cards=[("CONTAINS", "It is an ingredient", "Major allergens used in the recipe must be declared."),
               ("MAY CONTAIN", "A precaution", "Voluntary advisory wording about possible cross-contact.")],
        takeaway="No “Contains” line? Allergens can also appear inside the ingredient list. Always read it all.",
        two=True),
    "seven-aisles": dict(
        tag="SHOPPING SWAPS", kicker="Simple ideas, aisle by aisle",
        title="7 aisles.\nSmarter swaps.",
        lead="Look for a simpler option that does the same job.",
        rows=[("Bread", "Loaf with a short ingredient list", ""),
              ("Cereals", "Plain oats instead of a sweet cereal", ""),
              ("Dairy", "Plain yogurt + fresh fruit", ""),
              ("Drinks", "Sparkling water + lemon", ""),
              ("Snacks", "Plain nuts or homemade popcorn", ""),
              ("Sauces", "Simple tomato sauce or homemade dressing", ""),
              ("Ready meals", "Frozen vegetables + rice + egg", "")],
        takeaway="Same moment, same job. One level simpler can be enough.", compact=True),
    "sugar-names": dict(
        tag="HIDDEN SUGARS", big=True, kicker="Check the full ingredient list",
        title="Sugar has\nmany names",
        lead="Added sugar is not always called “sugar”. Look for these too:",
        chips=["Cane sugar", "Corn syrup", "Glucose syrup", "Dextrose", "Invert sugar",
               "Honey", "Fruit juice concentrate", "Brown rice syrup"],
        takeaway="On U.S. labels, the Added Sugars line shows the total added sugar per serving."),
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800;900&family=Source+Serif+4:ital,wght@0,400;1,400&display=swap');
*{box-sizing:border-box;margin:0}
html,body{width:1000px;height:1500px}
body{background:#F4EFE4;color:#13321F;font-family:Archivo,Arial,sans-serif;display:flex;flex-direction:column}
.top{background:#13321F;color:#F4EFE4;display:flex;justify-content:space-between;align-items:center;padding:30px 64px;font-weight:800;letter-spacing:.14em;font-size:22px}
.top .t{color:#F2B51C}
main{flex:1;padding:58px 64px 0;display:flex;flex-direction:column}
.k{color:#D9481C;font-weight:800;text-transform:uppercase;letter-spacing:.12em;font-size:25px}
h1{font-size:100px;line-height:.95;font-weight:900;letter-spacing:-.02em;text-transform:uppercase;margin:18px 0 26px;white-space:pre-line}
.lead{font-family:'Source Serif 4',Georgia,serif;font-size:34px;line-height:1.3;color:#2B4A37;margin-bottom:34px}
.rows{display:flex;flex-direction:column;gap:18px}
.row{display:grid;grid-template-columns:86px 1fr;gap:24px;align-items:center;border-radius:22px;padding:24px 28px}
.row .n{width:70px;height:70px;border-radius:50%;background:#13321F;color:#F4EFE4;display:grid;place-items:center;font-weight:900;font-size:32px}
.row .h{font-weight:800;font-size:33px;line-height:1.15}
.row .d{font-size:26px;color:#3F5B49;margin-top:6px;line-height:1.3}
.row.wide{grid-template-columns:330px 1fr}
.row.wide .lab{font-weight:900;font-size:31px;color:#D9481C}
.row.claim{grid-template-columns:1fr;gap:4px}
.row.claim .lab{font-weight:900;font-size:34px}
.row.claim .d b{color:#D9481C}
.compact .row{padding:15px 26px}
.compact .row .h{font-size:28px;font-weight:600}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:22px}
.card{border-radius:24px;padding:30px;min-height:220px}
.card .c{color:#D9481C;font-weight:900;font-size:56px}
.card .h{font-weight:800;font-size:32px;text-transform:uppercase;margin-top:10px}
.card .d{font-size:25px;color:#3F5B49;margin-top:8px;line-height:1.3}
.two .card{min-height:520px;padding:40px 34px}.two .card .c{font-size:48px}.big.mid .two .card .h{font-size:40px;margin-top:22px}.big.mid .two .card .d{font-size:33px;margin-top:22px}
.chips{display:flex;flex-wrap:wrap;gap:16px}
.chip{background:#FFFDF8;border:3px solid #F2B51C;border-radius:999px;padding:16px 28px;font-weight:800;font-size:33px}
.grid{display:grid;grid-template-columns:repeat(7,1fr);gap:14px}
.day{aspect-ratio:1/1.15;border-radius:18px;background:#DDEBDD;display:flex;flex-direction:column;justify-content:center;align-items:center;font-weight:900;font-size:36px}
.day:nth-child(n+8){background:#F9E4DC}.day span{font-size:16px;font-weight:700;letter-spacing:.1em;color:#5A7363}
.day.on{background:#F2B51C}
.mid{flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:30px}
.big .card .d{font-size:30px}.big .card .h{font-size:36px}.big .row .d{font-size:29px}.big .row .h{font-size:36px}
.big .chip{font-size:40px;padding:20px 34px}.big .chips{gap:20px}
.take{margin-bottom:40px;background:#13321F;color:#F4EFE4;border-radius:24px;padding:34px 38px;font-size:31px;line-height:1.35;font-weight:600}
.cta{display:inline-block;margin-top:18px;background:#D9481C;color:#fff;border-radius:999px;padding:14px 28px;font-weight:900;font-size:28px}
.foot{display:flex;justify-content:space-between;align-items:center;padding:26px 64px;border-top:2px solid #E2DCCF;font-weight:800;font-size:22px;letter-spacing:.1em}
.foot .s{color:#D9481C}
"""


def esc(s):
    return html.escape(s)


def body_for(p):
    if "rows" in p:
        out = []
        for i, (a, b, c) in enumerate(p["rows"]):
            tint = TINTS[i % 3] if not p.get("compact") else ("#FFFDF8" if i % 2 == 0 else "#DDEBDD")
            if a.isdigit():
                out.append(f'<div class="row" style="background:{tint}"><div class="n">{a}</div><div><div class="h">{esc(b)}</div><div class="d">{esc(c)}</div></div></div>')
            elif c and a.startswith("“"):
                out.append(f'<div class="row claim" style="background:{tint}"><div class="lab">{esc(a)}</div><div class="d">{esc(b)} · <b>{esc(c)}</b></div></div>')
            else:
                out.append(f'<div class="row wide" style="background:{tint}"><div class="lab">{esc(a)}</div><div class="h">{esc(b)}</div></div>')
        cls = "rows compact" if p.get("compact") else "rows"
        return f'<div class="{cls}">' + "".join(out) + "</div>"
    if "cards" in p:
        cards = "".join(
            f'<div class="card" style="background:{TINTS[i % 4]};border:2px solid #E2DCCF"><div class="c">{esc(a)}</div><div class="h">{esc(b)}</div><div class="d">{esc(c)}</div></div>'
            for i, (a, b, c) in enumerate(p["cards"]))
        return f'<div class="cards{" two" if p.get("two") else ""}">{cards}</div>'
    if "chips" in p:
        return '<div class="chips">' + "".join(f'<span class="chip">{esc(c)}</span>' for c in p["chips"]) + "</div>"
    if p.get("grid"):
        days = "".join(f'<div class="day{" on" if d in (1, 2, 3) else ""}">{d:02d}<span>DAY</span></div>' for d in range(1, 15))
        return f'<div class="grid">{days}</div>'
    return ""


def page(p):
    cta = f'<div class="cta">{esc(p["cta"])}</div>' if p.get("cta") else ""
    ts = p.get("ts", 100)
    big = " big" if p.get("big") else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="top"><span>SUPERMARKET DECODER</span><span class="t">{esc(p['tag'])}</span></div>
<main><div class="k">{esc(p['kicker'])}</div><h1 style="font-size:{ts}px">{esc(p['title'])}</h1><p class="lead">{esc(p['lead'])}</p>
<div class="mid{big}">{body_for(p)}</div>
<div class="take">{esc(p['takeaway'])}{('<br>' + cta) if cta else ''}</div></main>
<div class="foot"><span>READ · DECODE · SWAP</span><span class="s">SAVE FOR YOUR NEXT SHOP</span></div>
</body></html>"""


def browser():
    for b in BROWSERS:
        if Path(b).exists() or shutil.which(b):
            return b
    sys.exit("No Chrome/Edge found.")


def main(slugs):
    OUT.mkdir(exist_ok=True)
    exe = browser()
    tmp = Path(tempfile.mkdtemp())
    for slug in slugs or PINS:
        src = tmp / f"{slug}.html"
        src.write_text(page(PINS[slug]), encoding="utf-8")
        dst = OUT / f"{slug}.png"
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", "--window-size=1000,1500",
                        "--virtual-time-budget=8000", f"--user-data-dir={tmp / 'profile'}",
                        f"--screenshot={dst}", src.as_uri()],
                       check=True, capture_output=True, timeout=120)
        print("rendered", dst.relative_to(ROOT))
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main(sys.argv[1:])
