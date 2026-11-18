#!/usr/bin/env python3
"""Render 1200x630 social share cards (og:image) to assets/share/*.png.

Usage: python scripts/make_share_cards.py
"""
import html, shutil, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_pins import browser

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "share"
E = html.escape

CARDS = {
    "site": ("Free food-label school", "The front sells.\nThe back tells.", "Checklists, explainers, a comic and a free Ingredient Decoder."),
    "decoder": ("Free tool", "Ingredient\nDecoder", "Paste any food label: sugar names, E-numbers, processing clues and a NOVA estimate."),
    "articles": ("Plain-language explainers", "Read the label,\nnot the hype.", "Sugar names, E-numbers, NOVA and the 30-second scan, explained calmly."),
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@700;800;900&family=Source+Serif+4&display=swap');
*{box-sizing:border-box;margin:0}html,body{width:1200px;height:630px;overflow:hidden}
body{background:#F4EFE4;color:#13321F;font-family:Archivo,Arial,sans-serif;display:flex}
.l{flex:1;padding:58px 64px;display:flex;flex-direction:column}
.brand{font-weight:800;letter-spacing:.16em;font-size:20px}
.k{margin-top:auto;color:#D9481C;font-weight:800;letter-spacing:.14em;text-transform:uppercase;font-size:24px}
h1{font-size:84px;line-height:.96;font-weight:900;text-transform:uppercase;letter-spacing:-.02em;white-space:pre-line;margin:12px 0 20px}
p{font-family:'Source Serif 4',Georgia,serif;font-size:29px;line-height:1.3;color:#2B4A37;max-width:640px}
.r{width:360px;background:#13321F;display:flex;flex-direction:column;justify-content:center;gap:16px;padding:36px}
.chip{border-radius:999px;padding:14px 20px;font-weight:900;font-size:19px;white-space:nowrap;text-transform:uppercase;letter-spacing:.05em}
.a{background:#E2F1E7;color:#24613D}.b{background:#FBEBD3;color:#8A520F}.c{background:#FCF0C8;color:#6E5408}.d{background:#FBE1D7;color:#9A3519}
"""


def page(k, t, p):
    chips = '<span class="chip a">Basic ingredient</span><span class="chip b">Sugar name</span><span class="chip c">Additive: its job</span><span class="chip d">Processing clue</span>'
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="l"><div class="brand">SUPERMARKET DECODER</div><div class="k">{E(k)}</div><h1>{E(t)}</h1><p>{E(p)}</p></div>
<div class="r">{chips}</div></body></html>"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    exe, tmp = browser(), Path(tempfile.mkdtemp())
    for slug, (k, t, p) in CARDS.items():
        src = tmp / f"{slug}.html"
        src.write_text(page(k, t, p), encoding="utf-8")
        dst = OUT / f"{slug}.png"
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--window-size=1200,630", "--virtual-time-budget=8000", f"--user-data-dir={tmp / 'profile'}",
                        f"--screenshot={dst}", src.as_uri()], check=True, capture_output=True, timeout=120)
        print("rendered", dst.relative_to(ROOT))
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
