#!/usr/bin/env python3
"""Render 1000x1500 Pinterest Pins for the Ingredient Decoder tool to pins/decoder-*.png.

The decoded rows mirror what decoder/index.html actually outputs for each example.
Usage: python scripts/make_decoder_pins.py [slug ...]
"""
import html, shutil, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_pins import browser  # reuse Chrome/Edge discovery

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pins"
E = html.escape

# tag classes: ok, kit, sug, add, sig
PINS = {
    "decoder-hero": dict(
        tag="FREE TOOL", kicker="Paste it. Decode it. Done.",
        title="What's really in\nyour snack bar?",
        lead="Paste any ingredient list. Every ingredient gets explained.",
        label="Ingredients · chocolate cereal bar",
        rows=[("Oat flakes · 25%", [("ok", "Basic ingredient")]),
              ("Glucose syrup", [("sug", "Sugar name"), ("sig", "Processing clue")]),
              ("Milk chocolate · 12%", [("add", "Compound ingredient")]),
              ("Palm fat", [("kit", "Kitchen staple")]),
              ("Glycerol", [("add", "Humectant · E422")]),
              ("Dextrose", [("sug", "Sugar name")]),
              ("Flavouring", [("sig", "Processing clue")])],
        stats=[("12", "ingredients"), ("3", "sugar names"), ("5", "processing clues")],
        nova=4, cta="Try it free: paste any label", dense=True),
    "decoder-sugars": dict(
        tag="SUGAR NAMES", kicker="One bar. Three sugars.",
        title="3 sugar names\nin one snack bar",
        lead="Splitting sugar into several names keeps each one lower in the list. The Decoder counts them for you.",
        listing=[("Oat flakes (25%), ", ""), ("glucose syrup", "s"), (", milk chocolate (", ""), ("sugar", "s"),
                 (", cocoa butter, whole milk powder, cocoa mass, soy lecithin), palm fat, glycerol, ", ""),
                 ("dextrose", "s"), (", flavouring.", "")],
        cards=[("1", "Glucose syrup", "Starch turned into a sweet syrup"),
               ("2", "Sugar", "Hidden inside the chocolate's brackets"),
               ("3", "Dextrose", "Another name for glucose")],
        cta="Count the sugars on your label"),
    "decoder-bread": dict(
        tag="E-NUMBERS", kicker="Sliced white bread, decoded",
        title="What's E471 doing\nin my bread?",
        lead="An E-number is an ID, not a verdict. The Decoder tells you each additive's job.",
        label="Ingredients · sliced white bread",
        rows=[("E471", [("add", "Emulsifier")], "Mono- and diglycerides: keeps the crumb soft"),
              ("E472e", [("add", "Emulsifier")], "DATEM: strengthens dough for a taller loaf"),
              ("Calcium propionate", [("add", "Preservative · E282")], "Slows mould on packaged bread"),
              ("Ascorbic acid", [("add", "Flour treatment · E300")], "Vitamin C, helps dough strength")],
        nova=4, cta="Decode your bread's label free"),
    "decoder-nova": dict(
        tag="NOVA SCALE", kicker="Processed or ultra-processed?",
        title="Paste the label.\nGet a NOVA estimate.",
        lead="The Decoder looks for ingredients rarely used in a home kitchen and estimates the processing group.",
        compare=[("Plain yoghurt", "Milk, live cultures", 1, "Minimally processed"),
                 ("Salted peanuts", "Peanuts, sunflower oil, salt", 3, "Processed"),
                 ("Strawberry yoghurt", "…modified maize starch, flavourings, carmine", 4, "Ultra-processed")],
        cta="Check any food free",
        note="An estimate about processing, not a health score."),
    "decoder-cola": dict(
        tag="DRINK LABELS", kicker="5 ingredients, decoded",
        title="A can of cola,\nline by line",
        lead="Caramel colour E150d, phosphoric acid, “natural flavourings”: here's what each one does.",
        label="Ingredients · cola",
        rows=[("Carbonated water", [("ok", "Basic ingredient")], "Water with carbon dioxide"),
              ("Sugar", [("sug", "Sugar name")], "Second ingredient: there's a lot of it"),
              ("Caramel E150d", [("sig", "Colour · E150d")], "Sulphite ammonia caramel, for colour"),
              ("Phosphoric acid", [("add", "Acidity regulator")], "E338: adds the sharp tang"),
              ("Natural flavourings", [("sig", "Processing clue")], "Includes caffeine, a stimulant")],
        stats=[("5", "ingredients"), ("1", "sugar name"), ("2", "processing clues")],
        cta="Decode your drink free"),
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;800;900&family=Source+Serif+4:ital,wght@0,400;1,400&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1000px;height:1500px;overflow:hidden}
body{background:#F4EFE4;color:#13321F;font-family:Archivo,Arial,sans-serif;display:flex;flex-direction:column}
.top{background:#13321F;color:#F4EFE4;display:flex;justify-content:space-between;align-items:center;padding:30px 64px;font-weight:800;letter-spacing:.14em;font-size:22px}
.top .t{background:#F2B51C;color:#13321F;border-radius:999px;padding:8px 18px;font-size:19px}
main{flex:1;padding:46px 64px 0;display:flex;flex-direction:column}
.k{color:#D9481C;font-weight:800;text-transform:uppercase;letter-spacing:.12em;font-size:25px}
h1{font-size:86px;line-height:.98;font-weight:900;letter-spacing:-.02em;text-transform:uppercase;margin:16px 0 22px;white-space:pre-line}
.lead{font-family:'Source Serif 4',Georgia,serif;font-size:32px;line-height:1.32;color:#2B4A37;margin-bottom:30px}
.panel{background:#FFFDF8;border:3px solid #E2DCCF;border-radius:28px;padding:28px 30px;box-shadow:0 14px 40px rgba(19,50,31,.10)}
.lbl{font-size:19px;font-weight:900;letter-spacing:.16em;text-transform:uppercase;color:#5A7363;margin-bottom:14px}
.row{display:flex;align-items:center;justify-content:space-between;gap:16px;background:#fff;border:2px solid #E2DCCF;border-left:12px solid #B9B2A3;border-radius:14px;padding:13px 18px;margin:10px 0}
.row .nm{font-weight:800;font-size:30px}
.row .sub{font-size:21px;color:#3F5B49;margin-top:2px}
.row.ok,.row.kit{border-left-color:#3E8E5E}.row.sug{border-left-color:#D58A1E}.row.add{border-left-color:#F2B51C}.row.sig{border-left-color:#D9481C}
.tags{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
.tag{font-size:17px;font-weight:900;letter-spacing:.05em;text-transform:uppercase;border-radius:999px;padding:7px 13px;white-space:nowrap}
.tag.ok,.tag.kit{background:#E2F1E7;color:#24613D}.tag.sug{background:#FBEBD3;color:#8A520F}.tag.add{background:#FCF0C8;color:#6E5408}.tag.sig{background:#FBE1D7;color:#9A3519}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px}
.stat{background:#F4EFE4;border-radius:14px;padding:12px 16px}
.stat b{display:block;font-size:50px;line-height:1;font-weight:900}.stat span{font-size:20px;color:#5A7363;font-weight:700}
.stat:nth-child(2) b{color:#A0611A}.stat:nth-child(3) b{color:#D9481C}
.nova{margin-top:16px;border-radius:16px;padding:16px 20px;color:#fff;display:flex;align-items:center;justify-content:space-between;gap:16px}
.nova b{font-size:28px}.nova .bar{display:flex;gap:6px;width:220px}.nova .bar i{flex:1;height:12px;border-radius:6px;background:rgba(255,255,255,.28)}.nova .bar i.on{background:#F2B51C}
.g1{background:#13321F}.g2{background:#2F5A41}.g3{background:#7A5A12}.g4{background:#8E2F12}
.dense .row{padding:9px 18px;margin:7px 0}.dense .row .nm{font-size:28px}.dense .stat b{font-size:42px}
.listing{font-size:38px;line-height:1.6;background:#FFFDF8;border:3px solid #E2DCCF;border-radius:24px;padding:26px 30px}
.listing .s{background:#FBEBD3;color:#8A520F;font-weight:900;border-radius:8px;padding:0 8px;box-shadow:inset 0 -4px 0 #D58A1E}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:30px}
.card{background:#FFFDF8;border:2px solid #E2DCCF;border-top:10px solid #D58A1E;border-radius:18px;padding:26px 22px;min-height:290px}
.card .c{color:#D58A1E;font-weight:900;font-size:60px;line-height:1}.card .h{font-weight:900;font-size:32px;margin-top:14px}.card .d{font-size:25px;color:#3F5B49;margin-top:6px;line-height:1.3}
.cmp{display:flex;flex-direction:column;gap:14px}
.cmp .item{background:#FFFDF8;border:3px solid #E2DCCF;border-radius:20px;padding:20px 24px}
.cmp .item .h{font-weight:900;font-size:34px}.cmp .item .d{font-size:23px;color:#3F5B49;margin:2px 0 12px}
.cmp .nova{margin-top:0;padding:12px 18px}.cmp .nova b{font-size:24px}
.note{margin-top:14px;font-size:22px;color:#5A7363;font-weight:700;text-align:center}
.spacer{flex:1}
.cta{margin:26px 0 34px;background:#D9481C;color:#fff;border-radius:24px;padding:26px 34px;display:flex;justify-content:space-between;align-items:center;font-weight:900;font-size:36px}
.cta small{display:block;font-size:20px;font-weight:700;opacity:.9;margin-top:4px;letter-spacing:.02em}
.cta .arr{font-size:54px}
.foot{display:flex;justify-content:space-between;align-items:center;padding:24px 64px;border-top:2px solid #E2DCCF;font-weight:800;font-size:21px;letter-spacing:.1em}
"""

NOVA_TXT = {1: "NOVA 1 · Minimally processed", 2: "NOVA 2 · Kitchen ingredient", 3: "NOVA 3 · Processed", 4: "NOVA 4 · Likely ultra-processed"}


def nova_bar(g, label=None):
    bars = "".join(f'<i class="{"on" if i <= g else ""}"></i>' for i in range(1, 5))
    return f'<div class="nova g{g}"><b>{E(label or NOVA_TXT[g])}</b><div class="bar">{bars}</div></div>'


def body(p):
    out = []
    if "rows" in p:
        rows = []
        for r in p["rows"]:
            name, tags = r[0], r[1]
            sub = f'<div class="sub">{E(r[2])}</div>' if len(r) > 2 else ""
            tg = "".join(f'<span class="tag {c}">{E(t)}</span>' for c, t in tags)
            rows.append(f'<div class="row {tags[0][0]}"><div><div class="nm">{E(name)}</div>{sub}</div><div class="tags">{tg}</div></div>')
        stats = ""
        if p.get("stats"):
            stats = '<div class="stats">' + "".join(f'<div class="stat"><b>{E(a)}</b><span>{E(b)}</span></div>' for a, b in p["stats"]) + "</div>"
        nova = nova_bar(p["nova"]) if p.get("nova") else ""
        out.append(f'<div class="panel{" dense" if p.get("dense") else ""}"><div class="lbl">{E(p["label"])}</div>{"".join(rows)}{stats}{nova}</div>')
    if "listing" in p:
        out.append('<div class="listing">' + "".join(f'<span class="s">{E(t)}</span>' if c else E(t) for t, c in p["listing"]) + "</div>")
        out.append('<div class="cards">' + "".join(f'<div class="card"><div class="c">{E(a)}</div><div class="h">{E(b)}</div><div class="d">{E(c)}</div></div>' for a, b, c in p["cards"]) + "</div>")
    if "compare" in p:
        items = "".join(f'<div class="item"><div class="h">{E(n)}</div><div class="d">{E(d)}</div>{nova_bar(g, f"NOVA {g} · {lab}")}</div>' for n, d, g, lab in p["compare"])
        out.append(f'<div class="cmp">{items}</div>')
        if p.get("note"):
            out.append(f'<div class="note">{E(p["note"])}</div>')
    return "".join(out)


def page(p):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="top"><span>SUPERMARKET DECODER</span><span class="t">{E(p['tag'])}</span></div>
<main><div class="k">{E(p['kicker'])}</div><h1>{E(p['title'])}</h1><p class="lead">{E(p['lead'])}</p>
{body(p)}<div class="spacer"></div>
<div class="cta"><div>{E(p['cta'])}<small>Free · no sign-up · runs in your browser</small></div><span class="arr">→</span></div></main>
<div class="foot"><span>INGREDIENT DECODER</span><span>SAVE FOR YOUR NEXT SHOP</span></div>
</body></html>"""


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
