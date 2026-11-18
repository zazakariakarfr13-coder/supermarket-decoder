#!/usr/bin/env python3
"""Render comic-style Pins for The Cart Chronicles to pins/epNN-*.png (2000x3000).

Reuses Episode 02's panel/bubble CSS and SVG symbols; Episode 01 Pins swap in
that episode's mint/pink/yellow palette. Usage: python scripts/make_comic_pins.py [slug ...]
Share images (1200x630 JPG, og:image) go to assets/share/: python scripts/make_comic_pins.py share
"""
import re, shutil, subprocess, sys, tempfile
from PIL import Image, ImageFilter
from pathlib import Path
from make_pins import browser

ROOT = Path(__file__).resolve().parents[1]
EP = (ROOT / "story" / "episode-02.html").read_text(encoding="utf-8")
CSS = re.search(r"<style>(.*?)</style>", EP, re.S).group(1)
DEFS = re.search(r'(<svg width="0" height="0".*?</svg>)', EP, re.S).group(1)
CAST_DIR = Path(tempfile.mkdtemp())
SCALE = 2  # render at 2x: 2000x3000 output, same 2:3 ratio Pinterest expects


def prepare_cast():
    """Upscale the small 160x145 portraits with Lanczos + light sharpening so the
    browser never has to stretch them (that is what made faces look soft)."""
    for src in (ROOT / "assets" / "cast").glob("*.webp"):
        im = Image.open(src).convert("RGB")
        im = im.resize((im.width * 4, im.height * 4), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=80, threshold=2))
        im.save(CAST_DIR / f"{src.stem}.png")


CAST = CAST_DIR.as_uri()

PIN_CSS = """
body{margin:0;width:1000px;height:1500px;overflow:hidden;background:#fffaf0}
.pin{box-sizing:border-box;width:1000px;height:1500px;padding:48px 52px;display:flex;flex-direction:column;gap:26px}
.pin-top{display:flex;justify-content:space-between;font:900 22px var(--body);letter-spacing:.16em;text-transform:uppercase}
.pin-top b{color:var(--coral)}
.pin h1{font-size:118px;margin:0;line-height:.9}
.pin .hook{font:700 38px/1.3 var(--letter);margin:0}
.pin .grid{flex:1;gap:18px}
.pin .p{min-height:0;padding:20px;gap:14px}
.pin .b{font-size:30px;border-width:3px;border-radius:26px;padding:14px 20px}
.pin .b i{font-size:16px}
.pin .grid{grid-template-rows:1fr 1fr}
.pin .face{width:300px;height:272px;border-width:4px;margin:0;align-self:auto}
.pin .face.sm{width:240px;height:217px}
.stage{margin-top:auto;display:flex;align-items:flex-end;justify-content:space-around;gap:24px}
.stage .sfx{position:static;font-size:84px;margin-bottom:40px}
.stage svg{height:300px;width:auto}
.pin .cap{font-size:24px}
.pin .sfx{font-size:64px}
.pin-foot{background:var(--ink);color:#fff;border-radius:10px;padding:26px 32px;font:900 30px var(--body);display:flex;justify-content:space-between;align-items:center}
.pin-foot span{color:#ffd84d}
/* Episode 01 palette (pop-art mint / pink / yellow) */
.ep01{--mint:#a8e0cc;--lemon:#f8cd63;--rose:#f6a5c2;--sky:#c9ece0;--coral:#ee4d87;--paper:#f5eddf}
body.ep01{background:#f5eddf}
.pack{width:300px;min-height:330px;background:#ee4d87;border:6px solid var(--ink);box-shadow:10px 10px 0 var(--ink);padding:18px;display:flex;flex-direction:column;justify-content:space-between;text-align:center;transform:rotate(-5deg)}
.pack .band{font:400 30px var(--sfx);letter-spacing:.08em;border-bottom:4px solid var(--ink);padding-bottom:8px}
.pack strong{font:400 74px/.9 var(--sfx);letter-spacing:.02em;color:#fff;-webkit-text-stroke:2px var(--ink);text-shadow:4px 4px 0 var(--ink)}
.pack em{white-space:nowrap;font:900 18px var(--body);font-style:normal;background:#f8cd63;border:3px solid var(--ink);padding:8px}
.chips{display:flex;flex-wrap:wrap;gap:10px;justify-content:center}
.chips span{background:#fff;border:3px solid var(--ink);border-radius:999px;padding:8px 16px;font:800 24px var(--body);box-shadow:3px 3px 0 var(--ink)}
.pin .cube{width:84px;height:84px;border-width:5px;box-shadow:4px 4px 0 var(--ink)}
.pin .cubes{margin:0 auto}
"""

def face(name, cls=""):
    return f'<img class="face {cls}" src="{CAST}/{name}.png" alt="">'

PINS = {
    "ep02-electrolytes": ("Liquid Alibis", "The drink aisle has trust issues.", f"""
<div class="p w6 lemon"><div class="b shout"><i>Tariq</i>It has ELECTROLYTES. That's science you can drink.</div>
<div class="stage">{face('tariq')}<svg viewBox="0 0 120 250"><use href="#sevenfalls"/></svg></div></div>
<div class="p w6 sky"><div class="b r"><i>Mina</i>So does the sea. You don't drink that either.</div>
<div class="stage"><span class="sfx">DEADPAN.</span>{face('mina')}</div></div>
""", "A free comic that teaches you to read drink labels"),
    "ep02-two-columns": ("90 Calories?", "Per serving. The bottle holds about three.", f"""
<div class="p w6 center sky"><div class="label-card" style="width:680px">
<h3 style="font-size:50px">Nutrition Facts</h3><div class="srv" style="font-size:24px">About 3 servings per container<br>Serving size 12 fl oz (360 mL)</div>
<table class="nf" style="font-size:24px"><thead><tr><th></th><th style="font-size:20px">Per serving</th><th style="font-size:20px">Per container</th></tr></thead>
<tbody><tr class="cal"><td style="font-size:38px">Calories</td><td style="font-size:38px">90</td><td style="font-size:38px">250</td></tr>
<tr class="ind hl"><td>Incl. Added Sugars</td><td>22 g</td><td>61 g</td></tr></tbody></table>
<p class="fine" style="font-size:17px">Simplified fictional teaching example.</p></div></div>
<div class="p w6 rose"><div class="b shout"><i>Tariq</i>It's ONE bottle! Who drinks a third and puts it back?!</div>
<div class="stage">{face('tariq')}<span class="sfx">WHAT?!</span></div></div>
""", "Drinking it all? Read the second column"),
    "ep02-five-percent": ("“Real Fruit”", "The flamingo said real fruit. The carton said 5%.", f"""
<div class="p w6 rose"><div class="b mascot shout"><i>Flamboyo</i>Real fruit, kid. Would I lie to you? I'm a flamingo in sunglasses.</div>
<div class="stage"><svg viewBox="0 0 150 230"><use href="#carton"/></svg><svg viewBox="0 0 120 170"><use href="#flamingo"/></svg></div></div>
<div class="p w6 mint"><div class="b"><i>Mina</i>Tiny print: “contains 5% juice.”</div>
<div class="b r"><i>Uncle Kamil</i>U.S. rule: claim juice, state the percent.</div>
<div class="stage">{face('mina','sm')}<span class="sfx blue">SQUINT</span></div></div>
""", "Read the free comic: Liquid Alibis"),
    "ep01-flirting": ("Turn It Around", "The front is advertising. The back is information.", f"""
<div class="p w6 center lemon"><div class="pack"><span class="band">SUPER CRUNCH</span><strong>MAX<br>ENERGY!</strong><em>NATURAL · MULTI-GRAIN</em></div>
<p class="cap" style="position:absolute;left:20px;bottom:20px;margin:0">Fictional package</p><span class="sfx" style="top:24px;right:28px">SPARKLE!</span></div>
<div class="p w6 rose"><div class="b shout"><i>Tariq</i>So the box is flirting with me?</div>
<div class="b r"><i>Mina</i>And you're falling for it. Turn it around, Romeo.</div>
<div class="stage">{face('tariq','sm')}{face('mina','sm')}</div></div>
""", "Read the free comic: The Cart Chronicles"),
    "ep01-book-club": ("Wait, 8?!", "The numbers on the label are per serving.", f"""
<div class="p w6 center sky"><div class="label-card" style="width:660px">
<h3 style="font-size:50px">Nutrition Facts</h3><div class="srv" style="font-size:24px">8 servings per container<br>Serving size 1 cup (40 g)</div>
<table class="nf" style="font-size:24px"><tbody><tr class="cal"><td style="font-size:38px">Calories</td><td style="font-size:38px">160</td></tr>
<tr><td>Total Sugars</td><td>12 g</td></tr><tr class="ind hl"><td>Includes Added Sugars</td><td>10 g · 20% DV</td></tr></tbody></table>
<p class="fine" style="font-size:17px">Fictional teaching example, not a real cereal.</p></div></div>
<div class="p w6 lemon"><div class="b shout"><i>Tariq</i>Eight servings in one box? Who is this cereal feeding, a book club?</div>
<div class="stage">{face('tariq')}<span class="sfx">WAIT, 8?!</span></div></div>
""", "Check servings per container first"),
    "ep01-witness-protection": ("Sugar's Aliases", "Same sugar, many names on the ingredient list.", f"""
<div class="p w6 mint"><div class="b shout"><i>Mina</i>Why does sugar have so many aliases? Is it in witness protection?</div>
<div class="stage">{face('mina')}<span class="sfx">PLINK!</span></div></div>
<div class="p w6 center lemon"><div class="cubes" style="max-width:none;gap:14px"><span class="cube"></span><span class="cube"></span><span class="cube"></span><span class="cube half" style="width:42px"></span></div>
<p class="cube-cap" style="font-size:56px;margin:22px 0 26px">10 g added sugar ≈ 2.5 teaspoons</p>
<div class="chips"><span>dextrose</span><span>glucose syrup</span><span>honey</span><span>malt syrup</span><span>cane sugar</span></div></div>
""", "Read the free comic: The Cart Chronicles"),
}


SHARE_CSS = """
body{margin:0;width:1200px;height:630px;overflow:hidden;background:#fffaf0}
.share{box-sizing:border-box;width:1200px;height:630px;padding:40px 44px;display:grid;grid-template-columns:520px 1fr;gap:32px}
.share .txt{display:flex;flex-direction:column;gap:18px}
.share .kick{font:900 18px var(--body);letter-spacing:.16em;text-transform:uppercase}
.share .kick b{color:var(--coral)}
.share h1{font-size:104px;margin:0;line-height:.9}
.share .hook{font:700 30px/1.3 var(--letter);margin:0}
.share .tag{margin-top:auto;background:var(--ink);color:#fff;border-radius:10px;padding:18px 22px;font:900 22px var(--body)}
.share .tag span{color:#ffd84d}
.share .p{padding:18px;gap:12px;height:100%;box-sizing:border-box}
.share .b{font-size:26px;border-width:3px;border-radius:24px;padding:12px 18px}
.share .b i{font-size:15px}
.share .face{width:230px;height:208px;border-width:4px;margin:0;align-self:auto}
.share .stage svg{height:250px}
"""

SHARE = {
    "episode-02": ("ep02", "Liquid Alibis", "A bottle claims the power of seven waterfalls. A flamingo lawyers up.", f"""
<div class="p lemon"><div class="b shout"><i>Tariq</i>It has ELECTROLYTES. That's science you can drink.</div>
<div class="b r"><i>Mina</i>So does the sea.</div>
<div class="stage">{face('tariq')}<svg viewBox="0 0 120 250"><use href="#sevenfalls"/></svg></div></div>"""),
    "episode-01": ("ep01", "The Cart Chronicles", "One family. One cart. One cereal box that is definitely flirting.", f"""
<div class="p rose"><div class="b shout"><i>Tariq</i>So the box is flirting with me?</div>
<div class="b r"><i>Mina</i>Turn it around, Romeo.</div>
<div class="stage">{face('tariq','sm')}<div class="pack" style="width:220px;min-height:250px"><span class="band" style="font-size:22px">SUPER CRUNCH</span><strong style="font-size:54px">MAX<br>ENERGY!</strong><em style="font-size:12px;padding:6px">NATURAL · MULTI-GRAIN</em></div></div></div>"""),
}


def share_page(ep, title, hook, panel):
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Bangers&family=Comic+Neue:wght@400;700&family=Nunito:wght@400;700;900&display=swap" rel="stylesheet">
<style>{CSS}{PIN_CSS}{SHARE_CSS}</style></head><body class="{ep}">{DEFS}
<div class="share"><div class="txt"><span class="kick">The Cart Chronicles · <b>Episode {ep[2:]}</b></span>
<h1>{title}</h1><p class="hook">{hook}</p><div class="tag">Free comic · learn to read food labels <span>→</span></div></div>
{panel}</div></body></html>"""


def shoot(exe, tmp, html, dst, size, scale):
    src = tmp / "shot.html"; src.write_text(html, encoding="utf-8")
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--force-device-scale-factor={scale}",
                    f"--window-size={size}", "--virtual-time-budget=10000", "--allow-file-access-from-files",
                    f"--user-data-dir={tmp / 'profile'}", f"--screenshot={dst}", src.as_uri()],
                   check=True, capture_output=True, timeout=120)


def page(ep, title, hook, panels, foot):
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Bangers&family=Comic+Neue:wght@400;700&family=Nunito:wght@400;700;900&display=swap" rel="stylesheet">
<style>{CSS}{PIN_CSS}</style></head><body class="{ep}">{DEFS}
<div class="pin"><div class="pin-top"><span>The Cart Chronicles · <b>Ep {ep[2:]}</b></span><span>Supermarket Decoder</span></div>
<h1>{title}</h1><p class="hook">{hook}</p><div class="grid">{panels}</div>
<div class="pin-foot">{foot} <span>→</span></div></div></body></html>"""

def main():
    prepare_cast()
    exe = browser(); tmp = Path(tempfile.mkdtemp())
    if sys.argv[1:] == ["share"]:
        out = ROOT / "assets" / "share"; out.mkdir(parents=True, exist_ok=True)
        for name, (ep, t, h, panel) in SHARE.items():
            png = tmp / f"{name}.png"; shoot(exe, tmp, share_page(ep, t, h, panel), png, "1200,630", 1)
            dst = out / f"{name}.jpg"; Image.open(png).convert("RGB").save(dst, quality=88, optimize=True)
            print("rendered", dst.relative_to(ROOT), Image.open(dst).size, dst.stat().st_size // 1024, "KB")
    else:
        for slug in sys.argv[1:] or PINS:
            t, h, p, f = PINS[slug]
            dst = ROOT / "pins" / f"{slug}.png"
            shoot(exe, tmp, page(slug[:4], t, h, p, f), dst, "1000,1500", SCALE)
            print("rendered", dst.relative_to(ROOT), Image.open(dst).size)
    shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(CAST_DIR, ignore_errors=True)

if __name__ == "__main__":
    main()
