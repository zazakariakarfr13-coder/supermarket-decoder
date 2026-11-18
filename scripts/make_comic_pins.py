#!/usr/bin/env python3
"""Render 1000x1500 comic-style Pins for The Cart Chronicles Episode 02 to pins/ep02-*.png.

Reuses the episode page's CSS and SVG symbols so the Pins match the comic.
Usage: python scripts/make_comic_pins.py
"""
import re, shutil, subprocess, tempfile
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
}

def page(title, hook, panels, foot):
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Bangers&family=Comic+Neue:wght@400;700&family=Nunito:wght@400;700;900&display=swap" rel="stylesheet">
<style>{CSS}{PIN_CSS}</style></head><body>{DEFS}
<div class="pin"><div class="pin-top"><span>The Cart Chronicles · <b>Ep 02</b></span><span>Supermarket Decoder</span></div>
<h1>{title}</h1><p class="hook">{hook}</p><div class="grid">{panels}</div>
<div class="pin-foot">{foot} <span>→</span></div></div></body></html>"""

def main():
    prepare_cast()
    exe = browser(); tmp = Path(tempfile.mkdtemp())
    for slug, (t, h, p, f) in PINS.items():
        src = tmp / f"{slug}.html"; src.write_text(page(t, h, p, f), encoding="utf-8")
        dst = ROOT / "pins" / f"{slug}.png"
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--force-device-scale-factor={SCALE}",
                        "--window-size=1000,1500", "--virtual-time-budget=10000", "--allow-file-access-from-files",
                        f"--user-data-dir={tmp / 'profile'}", f"--screenshot={dst}", src.as_uri()],
                       check=True, capture_output=True, timeout=120)
        print("rendered", dst.relative_to(ROOT), Image.open(dst).size)
    shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(CAST_DIR, ignore_errors=True)

if __name__ == "__main__":
    main()
