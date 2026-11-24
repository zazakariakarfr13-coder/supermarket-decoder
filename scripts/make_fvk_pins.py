"""Factory vs. Kitchen Pinterest pins (1000x1500), in the risograph style of the Keep or Toss pins:
a food character with a face, a factory on one side and a frying pan on the other, the question,
a slammed verdict stamp, the kitchen score and one surprising factory secret.

Usage: py -3 scripts/make_fvk_pins.py            (renders all 15 into pins/fvk/)
       py -3 scripts/make_fvk_pins.py pringles   (only those slugs)
Each pin links to its own Factory vs. Kitchen page with UTM tags. Rendered with headless Edge.
"""
from __future__ import annotations

import csv
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from fvk_data import BY_SLUG, PRODUCTS  # noqa: E402

SITE = "https://zazakariakarfr13-coder.github.io/supermarket-decoder"
OUT = ROOT / "pins" / "fvk"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
W, H = 1000, 1500

INK, CREAM, PAPER = "#1d1a2f", "#f6eedd", "#fffaf0"
RED, MUSTARD, CORAL, GREEN = "#d83a2e", "#f3b33d", "#ef6a4c", "#2f8f5b"
S = f'stroke="{INK}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"'
STAMP = {"NO WAY": (RED, CREAM, "NO WAY"), "SORT OF": (MUSTARD, INK, "SORT OF"), "YES": (GREEN, CREAM, "YES!")}


def link(slug: str) -> str:
    return (f"{SITE}/factory-vs-kitchen/{slug}.html?utm_source=pinterest&utm_medium=social"
            f"&utm_campaign=factory_vs_kitchen&utm_content={slug}")


# ---------------------------------------------------------------- SVG helpers (same look as Keep or Toss)
def defs(shadow: str) -> str:
    return f"""<defs>
<pattern id="hatch" width="11" height="11" patternUnits="userSpaceOnUse" patternTransform="rotate(38)">
  <line x1="0" y1="0" x2="0" y2="11" stroke="{INK}" stroke-width="2.6" opacity=".5"/></pattern>
<pattern id="dots" width="13" height="13" patternUnits="userSpaceOnUse">
  <circle cx="6.5" cy="6.5" r="2.4" fill="{INK}" opacity=".32"/></pattern>
<filter id="rough"><feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="7"/>
  <feDisplacementMap in="SourceGraphic" scale="6"/></filter>
<filter id="riso" x="-15%" y="-15%" width="140%" height="140%">
  <feOffset in="SourceAlpha" dx="13" dy="13" result="o"/><feFlood style="flood-color:{shadow}"/>
  <feComposite in2="o" operator="in" result="s"/>
  <feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>"""


def face(x, y, mood="happy", s=1.0, color=INK):
    e, dx = 13 * s, 34 * s
    if mood == "sleep":
        eyes = (f'<path d="M{x-dx-e} {y} q{e} {e} {2*e} 0" fill="none" stroke="{color}" stroke-width="{6*s}" stroke-linecap="round"/>'
                f'<path d="M{x+dx-e} {y} q{e} {e} {2*e} 0" fill="none" stroke="{color}" stroke-width="{6*s}" stroke-linecap="round"/>')
        mouth = f'<ellipse cx="{x}" cy="{y+34*s}" rx="{9*s}" ry="{11*s}" fill="{color}"/>'
    elif mood == "shock":
        eyes = (f'<circle cx="{x-dx}" cy="{y}" r="{e*1.35}" fill="#fff" stroke="{color}" stroke-width="{5*s}"/><circle cx="{x-dx}" cy="{y+3*s}" r="{e*.6}" fill="{color}"/>'
                f'<circle cx="{x+dx}" cy="{y}" r="{e*1.35}" fill="#fff" stroke="{color}" stroke-width="{5*s}"/><circle cx="{x+dx}" cy="{y+3*s}" r="{e*.6}" fill="{color}"/>')
        mouth = f'<ellipse cx="{x}" cy="{y+42*s}" rx="{12*s}" ry="{16*s}" fill="{color}"/>'
    elif mood == "cool":
        eyes = (f'<path d="M{x-dx-24*s} {y-10*s} h{48*s} v{12*s} q{-24*s} {22*s} {-48*s} 0 z M{x+dx-24*s} {y-10*s} h{48*s} v{12*s} q{-24*s} {22*s} {-48*s} 0 z" fill="{color}"/>'
                f'<path d="M{x-dx+24*s} {y-6*s} h{2*dx-48*s}" stroke="{color}" stroke-width="{5*s}"/>')
        mouth = f'<path d="M{x-24*s} {y+34*s} q{24*s} {20*s} {48*s} -4" fill="none" stroke="{color}" stroke-width="{6*s}" stroke-linecap="round"/>'
    elif mood == "smug":
        eyes = (f'<path d="M{x-dx-e} {y+2*s} h{2*e}" stroke="{color}" stroke-width="{7*s}" stroke-linecap="round"/>'
                f'<path d="M{x+dx-e} {y+2*s} h{2*e}" stroke="{color}" stroke-width="{7*s}" stroke-linecap="round"/>')
        mouth = f'<path d="M{x-18*s} {y+34*s} q{26*s} {14*s} {44*s} -10" fill="none" stroke="{color}" stroke-width="{6*s}" stroke-linecap="round"/>'
    else:
        eyes = f'<circle cx="{x-dx}" cy="{y}" r="{e}" fill="{color}"/><circle cx="{x+dx}" cy="{y}" r="{e}" fill="{color}"/>'
        mouth = f'<path d="M{x-24*s} {y+28*s} q{24*s} {26*s} {48*s} 0" fill="none" stroke="{color}" stroke-width="{6*s}" stroke-linecap="round"/>'
    cheeks = (f'<circle cx="{x-dx-22*s}" cy="{y+22*s}" r="{10*s}" fill="{CORAL}" opacity=".55"/>'
              f'<circle cx="{x+dx+22*s}" cy="{y+22*s}" r="{10*s}" fill="{CORAL}" opacity=".55"/>')
    return eyes + mouth + (cheeks if mood in ("happy", "cool", "smug") else "")


def star(x, y, r, color):
    return (f'<path d="M{x} {y-r} Q{x+r*.18} {y-r*.18} {x+r} {y} Q{x+r*.18} {y+r*.18} {x} {y+r} '
            f'Q{x-r*.18} {y+r*.18} {x-r} {y} Q{x-r*.18} {y-r*.18} {x} {y-r}Z" fill="{color}"/>')


def factory(x=40, y=60):
    """Small factory with smoke, top-left of the art."""
    return (f'<g transform="translate({x} {y})">'
            f'<circle cx="150" cy="8" r="20" fill="{PAPER}" {S}/><circle cx="182" cy="-18" r="15" fill="{PAPER}" {S}/>'
            f'<rect x="132" y="22" width="34" height="80" fill="{RED}" {S}/>'
            f'<path d="M0 200 V96 l48 30 V96 l48 30 V96 l48 30 V70 h40 V200 Z" fill="{PAPER}" {S}/>'
            f'<rect x="20" y="150" width="26" height="26" fill="{MUSTARD}" stroke="{INK}" stroke-width="5"/>'
            f'<rect x="70" y="150" width="26" height="26" fill="{MUSTARD}" stroke="{INK}" stroke-width="5"/>'
            f'<rect x="120" y="150" width="26" height="26" fill="{MUSTARD}" stroke="{INK}" stroke-width="5"/>'
            f'<path d="M0 200 h184" {S}/></g>')


def pan(x=750, y=110):
    """Small frying pan with an egg-yolk sparkle, top-right of the art."""
    return (f'<g transform="translate({x} {y}) rotate(-10)">'
            f'<path d="M150 60 L235 30" stroke="{INK}" stroke-width="26" stroke-linecap="round"/>'
            f'<path d="M150 60 L235 30" stroke="#8b5a3c" stroke-width="12" stroke-linecap="round"/>'
            f'<ellipse cx="80" cy="70" rx="95" ry="50" fill="#3b3550" {S}/>'
            f'<ellipse cx="80" cy="62" rx="72" ry="32" fill="#57506e"/>'
            f'<path d="M30 120 q50 26 100 0" stroke="{INK}" stroke-width="7" fill="none" stroke-linecap="round"/></g>')


def vs_badge(x=500, y=84):
    return (f'<circle cx="{x}" cy="{y}" r="54" fill="{MUSTARD}" {S}/>'
            f'<text x="{x}" y="{y+22}" text-anchor="middle" font-family="Anton" font-size="62" fill="{INK}">VS</text>')


def art(shadow: str, body: str, back: str = "") -> str:
    top = factory() + pan() + vs_badge()
    return (f'<svg viewBox="0 0 1000 800" width="1000" height="800" xmlns="http://www.w3.org/2000/svg">{defs(shadow)}'
            f'{back}<g filter="url(#rough)"><g filter="url(#riso)">{top}<g transform="translate(0 -40)">{body}</g></g></g></svg>')


def bowl(color, y=520):
    return (f'<path d="M240 {y} L760 {y} Q750 {y+190} 590 {y+235} L410 {y+235} Q250 {y+190} 240 {y}Z" fill="{color}" {S}/>'
            f'<path d="M630 {y} L760 {y} Q750 {y+190} 590 {y+235} Q690 {y+150} 630 {y}Z" fill="url(#hatch)"/>'
            f'<path d="M435 {y+235} L565 {y+235} L552 {y+268} L448 {y+268}Z" fill="{color}" {S}/>')


# ---------------------------------------------------------------- the 15 characters (centre around x=500, y 260-780)
def pringles():
    chips = "".join(f'<path d="M{410+dx} {268-dy} Q500 {214-dy} {590+dx} {268-dy} Q500 {306-dy} {410+dx} {268-dy}Z" fill="#f5c04a" {S}/>'
                     for dx, dy in [(0, 0), (6, 30)])
    return (f'<rect x="395" y="280" width="210" height="470" rx="34" fill="{RED}" {S}/>'
            f'<path d="M560 290 L605 300 L605 730 Q600 750 560 750Z" fill="url(#hatch)"/>'
            f'<rect x="395" y="470" width="210" height="130" fill="{CREAM}" stroke="{INK}" stroke-width="6"/>'
            + chips + face(500, 375, "shock", 1.0, CREAM)
            + f'<path d="M430 520 q70 -40 140 0 q-70 40 -140 0Z" fill="#f5c04a" stroke="{INK}" stroke-width="5"/>')


def pop_rocks():
    zig = "M360 330 " + " ".join(f"l20 -26 l20 26" for _ in range(7)) + " L640 740 L360 740 Z"
    rocks = "".join(f'<path d="M{x} {y} l18 -10 l14 14 l-6 18 l-20 2Z" fill="{c}" stroke="{INK}" stroke-width="4"/>'
                    for x, y, c in [(250, 560, "#ef7fae"), (720, 520, "#7cc4f2"), (300, 690, MUSTARD), (700, 680, "#ef7fae"), (230, 420, "#7cc4f2")])
    bursts = star(250, 330, 34, CREAM) + star(760, 380, 26, CREAM) + star(800, 600, 18, MUSTARD) + star(200, 620, 20, MUSTARD)
    return (f'<path d="{zig}" fill="#ef7fae" {S}/>'
            f'<path d="M590 330 L640 330 L640 740 L600 740Z" fill="url(#hatch)"/>'
            f'<circle cx="500" cy="560" r="92" fill="{CREAM}" stroke="{INK}" stroke-width="6"/>'
            f'<path d="M455 520 l30 0 l-14 36 l36 0 l-52 66 l14 -48 l-30 0Z" fill="{MUSTARD}" stroke="{INK}" stroke-width="5"/>'
            + face(500, 410, "shock", 1.0) + rocks + bursts)


def nutella():
    return (f'<rect x="390" y="300" width="220" height="80" rx="16" fill="#5a3a22" {S}/>'
            f'<path d="M392 340 h216" stroke="{CREAM}" stroke-width="4" stroke-dasharray="4 14"/>'
            f'<rect x="372" y="370" width="256" height="380" rx="46" fill="{PAPER}" {S}/>'
            f'<path d="M570 380 Q628 400 628 470 L628 700 Q628 750 580 750Z" fill="url(#hatch)"/>'
            f'<rect x="372" y="460" width="256" height="190" fill="#8a5432" stroke="{INK}" stroke-width="6"/>'
            + face(500, 540, "happy", 1.0, CREAM)
            + f'<g transform="translate(720 400)"><ellipse cx="0" cy="40" rx="62" ry="70" fill="#b5713d" {S}/>'
              f'<path d="M-60 10 Q0 -60 60 10 Q0 -10 -60 10Z" fill="#6b4024" {S}/>'
            + face(0, 52, "sleep", .55) + "</g>")


def cheetos():
    bumps = ("M300 520 q-20 -70 50 -90 q20 -70 90 -50 q50 -60 110 -10 q70 -30 100 40 q80 10 60 90 "
             "q50 60 -20 110 q0 80 -90 70 q-50 60 -110 10 q-80 30 -100 -50 q-80 -20 -40 -90 q-50 -50 0 -80Z")
    crumbs = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#f39a2b" stroke="{INK}" stroke-width="4"/>'
                     for x, y, r in [(220, 700, 14), (780, 690, 18), (820, 520, 10), (190, 480, 12)])
    return (f'<path d="{bumps}" fill="#f39a2b" {S}/>'
            f'<path d="{bumps}" fill="url(#dots)"/>' + face(500, 500, "cool", 1.25) + crumbs)


def mms():
    out = ""
    for x, y, c, mood in [(360, 560, RED, "happy"), (640, 560, "#3d6fd6", "cool"), (500, 400, MUSTARD, "shock")]:
        out += (f'<ellipse cx="{x}" cy="{y}" rx="125" ry="112" fill="{c}" {S}/>'
                f'<ellipse cx="{x-45}" cy="{y-55}" rx="34" ry="16" fill="#fff" opacity=".55" transform="rotate(-25 {x-45} {y-55})"/>'
                + face(x, y + 5, mood, .85, CREAM if c != MUSTARD else INK))
    return out


def pop_tarts():
    sprinkles = "".join(f'<rect x="{x}" y="{y}" width="26" height="8" rx="4" fill="{c}" transform="rotate({r} {x} {y})"/>'
                        for x, y, c, r in [(410, 380, "#7cc4f2", 20), (560, 370, MUSTARD, -30), (430, 640, "#fff", 45),
                                           (580, 630, "#7cc4f2", -10), (590, 470, "#fff", 60), (400, 520, MUSTARD, -50)])
    crimp = "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="#c98a4b"/>' for x in range(355, 650, 32) for y in (300, 740))
    return (f'<rect x="335" y="285" width="330" height="470" rx="28" fill="#f0c58a" {S}/>'
            f'<rect x="372" y="330" width="256" height="380" rx="22" fill="#f4a3c4" {S}/>'
            f'<path d="M560 330 L628 340 L628 690 Q610 710 560 710Z" fill="url(#hatch)"/>'
            + crimp + sprinkles + face(500, 520, "happy", 1.05))


def oreos():
    ring = "".join(f'<circle cx="{480 + 150 * c}" cy="{520 + 150 * s}" r="9" fill="#5a5068"/>'
                   for c, s in [(1, 0), (.7, .7), (0, 1), (-.7, .7), (-1, 0), (-.7, -.7), (0, -1), (.7, -.7)])
    return (f'<g transform="translate(700 650) rotate(-12)"><ellipse cx="0" cy="30" rx="110" ry="34" fill="#2a2230" {S}/>'
            f'<rect x="-110" y="0" width="220" height="30" fill="{PAPER}" stroke="{INK}" stroke-width="6"/>'
            f'<ellipse cx="0" cy="0" rx="110" ry="34" fill="#2a2230" {S}/></g>'
            f'<circle cx="480" cy="520" r="200" fill="#2a2230" {S}/>'
            f'<circle cx="480" cy="520" r="160" fill="none" stroke="#4a4058" stroke-width="10"/>' + ring
            + face(480, 515, "smug", 1.2, CREAM))


def coca_cola():
    bubbles = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{CREAM}" stroke-width="5"/>'
                      for x, y, r in [(300, 600, 18), (270, 480, 12), (720, 560, 16), (750, 430, 10), (300, 360, 9)])
    return (f'<rect x="395" y="280" width="210" height="470" rx="40" fill="{RED}" {S}/>'
            f'<ellipse cx="500" cy="290" rx="100" ry="26" fill="#cfd6dd" {S}/>'
            f'<path d="M560 300 Q605 310 605 360 L605 700 Q600 750 560 745Z" fill="url(#hatch)"/>'
            f'<rect x="395" y="560" width="210" height="60" fill="{PAPER}" stroke="{INK}" stroke-width="5"/>'
            f'<path d="M420 590 h160" stroke="{INK}" stroke-width="5" stroke-dasharray="2 16" stroke-linecap="round"/>'
            + face(500, 420, "happy", 1.0, CREAM) + bubbles)


def ritz():
    import math
    pts = []
    for i in range(18):
        a0, a1 = math.radians(i * 20), math.radians(i * 20 + 20)
        am = (a0 + a1) / 2
        pts.append(f"Q{500 + 232 * math.cos(am):.0f} {520 + 232 * math.sin(am):.0f} {500 + 200 * math.cos(a1):.0f} {520 + 200 * math.sin(a1):.0f}")
    path = f"M700 520 " + " ".join(pts) + "Z"
    holes = "".join(f'<circle cx="{500 + 120 * math.cos(math.radians(a))}" cy="{520 + 120 * math.sin(math.radians(a))}" r="11" fill="#b8742a"/>'
                    for a in (200, 250, 290, 340)) + '<circle cx="500" cy="700" r="11" fill="#b8742a"/><circle cx="380" cy="640" r="11" fill="#b8742a"/><circle cx="620" cy="640" r="11" fill="#b8742a"/>'
    salt = "".join(f'<rect x="{x}" y="{y}" width="9" height="9" fill="#fff" transform="rotate(30 {x} {y})"/>' for x, y in [(430, 420), (600, 450), (560, 690), (420, 600)])
    return f'<path d="{path}" fill="#e9a849" {S}/><path d="{path}" fill="url(#dots)"/>' + holes + salt + face(500, 520, "happy", 1.15)


def ramen():
    noodles = "".join(f'<path d="M{x} 520 q20 -60 0 -120 q-20 -60 0 -110" fill="none" stroke="{MUSTARD}" stroke-width="16" stroke-linecap="round"/>'
                      for x in range(330, 680, 40))
    return (f'<path d="M560 230 L700 470 M610 220 L720 460" stroke="{INK}" stroke-width="16" stroke-linecap="round"/>'
            f'<path d="M560 230 L700 470 M610 220 L720 460" stroke="#d9a56a" stroke-width="8" stroke-linecap="round"/>'
            f'<path d="M300 520 Q500 330 700 520Z" fill="{MUSTARD}" {S}/>' + noodles
            + f'<ellipse cx="420" cy="480" rx="40" ry="22" fill="{PAPER}" {S}/><ellipse cx="420" cy="480" rx="16" ry="10" fill="{MUSTARD}"/>'
            + bowl(RED) + face(500, 630, "happy", 1.1, CREAM))


def froot_loops():
    rings = "".join(f'<circle cx="{x}" cy="{y}" r="34" fill="none" stroke="{INK}" stroke-width="30"/><circle cx="{x}" cy="{y}" r="34" fill="none" stroke="{c}" stroke-width="18"/>'
                    for x, y, c in [(330, 470, RED), (410, 420, MUSTARD), (500, 450, "#5bbf6a"), (590, 410, "#8a5bd6"),
                                    (670, 470, CORAL), (450, 500, "#7cc4f2"), (560, 500, RED)])
    flying = "".join(f'<circle cx="{x}" cy="{y}" r="26" fill="none" stroke="{INK}" stroke-width="24"/><circle cx="{x}" cy="{y}" r="26" fill="none" stroke="{c}" stroke-width="13"/>'
                     for x, y, c in [(250, 330, "#5bbf6a"), (760, 330, MUSTARD)])
    return rings + flying + bowl("#3d6fd6") + face(500, 630, "shock", 1.1, CREAM)


def bear(x, y, c, mood, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<circle cx="-62" cy="-118" r="30" fill="{c}" {S}/><circle cx="62" cy="-118" r="30" fill="{c}" {S}/>'
            f'<circle cx="0" cy="-70" r="86" fill="{c}" {S}/>'
            f'<path d="M-90 40 q-10 -90 90 -90 q100 0 90 90 q0 110 -90 110 q-90 0 -90 -110Z" fill="{c}" {S}/>'
            f'<ellipse cx="-104" cy="40" rx="30" ry="22" fill="{c}" {S}/><ellipse cx="104" cy="40" rx="30" ry="22" fill="{c}" {S}/>'
            f'<ellipse cx="-36" cy="-112" rx="22" ry="10" fill="#fff" opacity=".5"/>'
            + face(0, -76, mood, .7) + "</g>")


def gummy_bears():
    return bear(300, 610, "#e94b4b", "happy", .9) + bear(700, 610, "#5bbf6a", "cool", .9) + bear(500, 520, MUSTARD, "shock", 1.1)


def kit_kat():
    fingers = "".join(f'<rect x="{x}" y="330" width="88" height="330" rx="12" fill="#7a4a2a" {S}/>'
                      f'<rect x="{x+14}" y="350" width="60" height="290" rx="8" fill="#8f5a35"/>' for x in (318, 410, 502, 594))
    return (fingers + f'<path d="M300 520 L700 520 L700 700 Q690 720 670 720 L330 720 Q300 720 300 700Z" fill="{RED}" {S}/>'
            f'<path d="M300 520 l30 -24 l30 24 l30 -24 l30 24 l30 -24 l30 24 l30 -24 l30 24 l30 -24 l30 24 l30 -24 l30 24 l30 -24 l10 8" fill="none" stroke="{INK}" stroke-width="6"/>'
            f'<path d="M620 520 L700 520 L700 700 Q690 720 670 720 L640 720Z" fill="url(#hatch)"/>'
            + face(500, 610, "happy", 1.0, CREAM)
            + f'<path d="M640 330 l18 -40 l10 44Z" fill="#7a4a2a" stroke="{INK}" stroke-width="4"/>')


def ketchup():
    return (f'<rect x="458" y="240" width="84" height="70" rx="12" fill="{PAPER}" {S}/>'
            f'<path d="M490 240 l10 -36 l10 36" fill="{PAPER}" {S}/>'
            f'<path d="M420 310 h160 q40 0 40 50 v330 q0 60 -60 60 h-120 q-60 0 -60 -60 v-330 q0 -50 40 -50Z" fill="{RED}" {S}/>'
            f'<path d="M560 320 Q620 330 620 390 L620 690 Q615 745 570 748Z" fill="url(#hatch)"/>'
            f'<circle cx="500" cy="590" r="70" fill="{PAPER}" stroke="{INK}" stroke-width="6"/>'
            f'<circle cx="500" cy="600" r="42" fill="{RED}" stroke="{INK}" stroke-width="5"/><path d="M488 560 l12 10 l12 -10" stroke="#2f8f5b" stroke-width="7" fill="none"/>'
            + face(500, 430, "cool", .95, CREAM)
            + f'<g transform="translate(730 650)"><circle cx="0" cy="0" r="62" fill="{RED}" {S}/>'
              f'<path d="M-20 -60 l20 14 l20 -14 l-6 22 l-28 0Z" fill="#2f8f5b" stroke="{INK}" stroke-width="4"/>'
            + face(0, 6, "happy", .55, CREAM) + "</g>")


def twinkies():
    return (f'<rect x="260" y="400" width="480" height="250" rx="125" fill="#f3c25a" {S}/>'
            f'<path d="M640 410 Q740 440 740 525 Q740 640 630 648 Q700 560 640 410Z" fill="url(#hatch)"/>'
            f'<rect x="260" y="400" width="480" height="250" rx="125" fill="url(#dots)" opacity=".6"/>'
            + "".join(f'<circle cx="{x}" cy="648" r="13" fill="{PAPER}" stroke="{INK}" stroke-width="5"/>' for x in (400, 500, 600))
            + f'<path d="M500 690 q-30 40 0 70 q30 -30 0 -70Z" fill="{PAPER}" stroke="{INK}" stroke-width="5"/>'
            + face(500, 505, "happy", 1.15))


# ---------------------------------------------------------------- pin list
# slug: (art, bg, text colour, headline shadow, art shadow, sub line)
PINS = {
    "pringles": (pringles, "#22306b", CREAM, CORAL, "#0e1430", "They're a dough, fried on a saddle mold."),
    "pop-rocks": (pop_rocks, "#6a4bc4", CREAM, MUSTARD, "#3a2585", "Hot candy + gas at ~600 psi. Don't try it."),
    "nutella": (nutella, "#f4a7b9", INK, "#fff", "#c0607d", "Sugar is ingredient #1. Hazelnuts: 13%."),
    "cheetos": (cheetos, "#1f7a78", CREAM, MUSTARD, "#0b4a49", "The puff happens in a split second."),
    "mms": (mms, "#9cc9e8", INK, "#fff", "#2d5f86", "The shell is dozens of thin sugar layers."),
    "pop-tarts": (pop_tarts, "#a8dcc6", INK, CREAM, "#1f6b55", "Pie crust + jam + glaze. Done."),
    "oreos": (oreos, "#f7d4bd", INK, "#fff", "#b7774e", "The secret is black cocoa."),
    "coca-cola": (coca_cola, "#2f4bbf", CREAM, "#f29aa8", "#18287a", "The recipe is locked in a vault."),
    "ritz": (ritz, CORAL, INK, MUSTARD, "#8f2a17", "The holes stop it puffing up. Use a fork."),
    "instant-ramen": (ramen, "#efe1c6", INK, CORAL, "#b08e58", "Fried noodles = 3-minute dinner."),
    "froot-loops": (froot_loops, "#e0623c", CREAM, INK, "#8f2a17", "Every color reportedly tastes the same."),
    "gummy-bears": (gummy_bears, "#7b5cd6", CREAM, MUSTARD, "#3a2585", "The secret: a day of drying."),
    "kit-kat": (kit_kat, "#f3b33d", INK, "#fff", "#a86d0c", "UK filling: crushed broken Kit Kats."),
    "ketchup": (ketchup, "#9ac9b0", INK, CREAM, "#2f6b51", "Tomato paste + 15 minutes."),
    "twinkies": (twinkies, "#2b5fa8", CREAM, MUSTARD, "#12305e", "Shelf life: 45 days. Yours: about 3."),
}

COPY = {  # Pinterest title (<= 100 chars)
    "pringles": "Can you make Pringles at home? How the factory really makes them",
    "pop-rocks": "Can you make Pop Rocks at home? The 600 psi secret",
    "nutella": "Homemade Nutella vs the jar: easy recipe and what's really inside",
    "cheetos": "Can you make Cheetos at home? The extruder secret, explained",
    "mms": "Can you make M&M's at home? How the candy shell is made",
    "pop-tarts": "Homemade Pop-Tarts: easier than you think (and better)",
    "oreos": "Homemade Oreos: the one ingredient everyone gets wrong",
    "coca-cola": "Can you make Coca-Cola at home? The secret formula, explained",
    "ritz": "Homemade Ritz crackers: why they have holes (and real butter)",
    "instant-ramen": "Why instant ramen cooks in 3 minutes, and how to make it at home",
    "froot-loops": "Can you make Froot Loops at home? Plus: every color tastes the same",
    "gummy-bears": "Homemade gummy bears: the step everyone skips",
    "kit-kat": "What's inside a Kit Kat? Factory secret and homemade version",
    "ketchup": "Homemade ketchup in 15 minutes from tomato paste",
    "twinkies": "Homemade Twinkies: how the cream gets in, and the 45-day shelf life",
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Space+Grotesk:wght@500;700&display=block');
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1000px;height:1500px;overflow:hidden}
html:not(.ready) .pin{visibility:hidden}
.pin{width:1000px;height:1500px;position:relative;overflow:hidden;background:var(--bg);color:var(--text)}
.k{position:absolute;top:58px;left:66px;font-family:Anton,Impact,sans-serif;font-size:76px;line-height:1;text-transform:uppercase;
   letter-spacing:.5px;text-shadow:6px 6px 0 var(--shadow)}
.q{position:absolute;top:136px;left:62px;right:62px;white-space:nowrap;font-family:Anton,Impact,sans-serif;font-size:168px;line-height:1;
   text-transform:uppercase;letter-spacing:.5px;text-shadow:8px 8px 0 var(--shadow)}
.k2{position:absolute;top:318px;left:66px;font-family:Anton,Impact,sans-serif;font-size:76px;line-height:1;text-transform:uppercase;
   letter-spacing:.5px;text-shadow:6px 6px 0 var(--shadow)}
.art{position:absolute;left:0;top:380px;width:1000px;height:800px}
.stamp{position:absolute;left:62px;bottom:236px;transform:rotate(-4deg);background:var(--sbg);color:var(--sfg);
   font-family:Anton,Impact,sans-serif;font-size:150px;line-height:1;padding:18px 40px 8px;border:8px solid #1d1a2f;
   box-shadow:14px 14px 0 #1d1a2f;letter-spacing:1px}
.score{position:absolute;right:70px;bottom:246px;width:190px;height:190px;border-radius:50%;background:#fffaf0;color:#1d1a2f;
   border:8px solid #1d1a2f;box-shadow:10px 10px 0 #1d1a2f;transform:rotate(6deg);display:flex;flex-direction:column;
   align-items:center;justify-content:center;font-family:Anton,Impact,sans-serif}
.score b{font-size:84px;line-height:.9;font-weight:400}.score b small{font-size:44px}
.score span{white-space:nowrap;font:700 16px 'Space Grotesk',sans-serif;letter-spacing:1px;text-transform:uppercase;margin-top:4px}
.sub{position:absolute;left:68px;right:60px;bottom:126px;font:700 40px 'Space Grotesk',sans-serif;line-height:1.15}
.foot{position:absolute;left:0;right:0;bottom:0;height:96px;background:#1d1a2f;color:#f6eedd;display:flex;
   align-items:center;justify-content:space-between;padding:0 66px;font:700 30px 'Space Grotesk',sans-serif}
.foot b{font-family:Anton,Impact,sans-serif;font-weight:400;font-size:38px;letter-spacing:1px}
.foot b i{font-style:normal;color:#f3b33d}
.foot span{opacity:.85}
.grain{position:absolute;inset:0;pointer-events:none;mix-blend-mode:multiply;opacity:.42;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='400'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .55 0'/></filter><rect width='400' height='400' filter='url(%23n)'/></svg>")}
.speck{position:absolute;inset:0;pointer-events:none;opacity:.5;background-image:radial-gradient(rgba(255,255,255,.35) 1.2px,transparent 1.4px);background-size:23px 29px}
"""

FIT = """<script>
Promise.all([document.fonts.load("76px Anton"),document.fonts.load("700 40px 'Space Grotesk'")]).then(function(){return document.fonts.ready}).then(function(){
var q=document.querySelector('.q'),s=168;while(q.scrollWidth>q.clientWidth&&s>80){s-=4;q.style.fontSize=s+'px';}
document.documentElement.classList.add('ready');});
</script>"""


def html(slug: str) -> str:
    p = BY_SLUG[slug]
    draw, bg, text, shadow, art_shadow, sub = PINS[slug]
    sbg, sfg, word = STAMP[p["verdict"]]
    style = f"--bg:{bg};--text:{text};--shadow:{shadow};--sbg:{sbg};--sfg:{sfg}"
    name = p["name"].upper().replace("RITZ CRACKERS", "RITZ")
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>"
            f"<div class='pin' style='{style}'>"
            f"<div class='art'>{art(art_shadow, draw())}</div>"
            f"<div class='k'>Can you make</div><div class='q'>{name}</div><div class='k2'>at home?</div>"
            f"<div class='stamp'>{word}</div>"
            f"<div class='score'><b>{p['score']}<small>/10</small></b><span>Kitchen score</span></div>"
            f"<div class='sub'>{sub}</div>"
            f"<div class='foot'><b>FACTORY <i>VS</i> KITCHEN</b><span>Supermarket Decoder →</span></div>"
            f"<div class='speck'></div><div class='grain'></div></div>{FIT}</body></html>")


def render(doc: str, out_png: Path) -> None:
    tmp = Path(tempfile.mkdtemp())
    src = tmp / "pin.html"
    src.write_text(doc, encoding="utf-8")
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={tmp / 'p'}",
                    "--virtual-time-budget=15000", "--run-all-compositor-stages-before-draw",
                    "--force-device-scale-factor=1", f"--window-size={W},{H}", f"--screenshot={out_png}", src.as_uri()],
                   check=True, capture_output=True, timeout=180)
    shutil.rmtree(tmp, ignore_errors=True)


def description(p: dict) -> str:
    word = {"NO WAY": "No way", "SORT OF": "Sort of", "YES": "Yes"}[p["verdict"]]
    return (f"{p['answer']} Verdict: {word}, kitchen score {p['score']}/10. "
            f"See how the factory makes {p['name']}, the one secret you can't easily copy, and a simple home method.")


def main(argv: list[str]) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    wanted = set(argv[1:])
    for p in PRODUCTS:
        if wanted and p["slug"] not in wanted:
            continue
        render(html(p["slug"]), OUT / f"{p['slug']}.png")
        print(f"rendered pins/fvk/{p['slug']}.png")
    with open(OUT / "pins.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["file", "title", "description", "link", "alt_text"])
        for p in PRODUCTS:
            sub = PINS[p["slug"]][5]
            alt = (f"Illustrated pin: Can you make {p['name']} at home? Verdict: {p['verdict'].title()}, "
                   f"kitchen score {p['score']}/10. {sub}")
            w.writerow([f"{p['slug']}.png", COPY[p["slug"]], description(p), link(p["slug"]), alt])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
