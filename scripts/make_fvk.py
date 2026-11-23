#!/usr/bin/env python3
"""Build the Factory vs. Kitchen pages (factory-vs-kitchen/*.html) from scripts/fvk_data.py.

Usage:  python scripts/make_fvk.py
Then:   python scripts/make_search_index.py && python scripts/check_site.py

Hard words listed in fvk_data.GLOSS become clickable: a tap opens a short plain-English
explanation right under the word (first time the word appears on a page).
"""
import html, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fvk_data import GLOSS, PRODUCTS  # noqa: E402
from make_additives import head, SITE  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "factory-vs-kitchen"
E = html.escape
GUIDE = ("https://zakarfr.gumroad.com/l/supermarket-decoder?utm_source=github_pages&utm_medium=fvk_page"
         "&utm_campaign=supermarket_decoder&utm_content={slug}")
VCLASS = {"YES": "yes", "SORT OF": "sortof", "NO WAY": "noway"}
VTEXT = {"YES": "Yes, you can", "SORT OF": "Sort of", "NO WAY": "No way"}

STYLE = """
.term{font:inherit;color:#9A3519;background:#FCF3DC;border:0;border-bottom:2px dotted #D9481C;padding:0 4px;border-radius:5px;cursor:pointer;line-height:inherit}
.term::after{content:"?";display:inline-block;margin-left:5px;width:17px;height:17px;line-height:17px;text-align:center;font-size:11px;font-weight:900;background:#D9481C;color:#fff;border-radius:50%;vertical-align:2px}
.term:hover,.term[aria-expanded=true]{background:#F7DFA0}
.term:focus-visible{outline:3px solid #13321F;outline-offset:2px}
.term-note{display:block;margin:8px 0 12px;padding:10px 14px 10px 40px;background:#fff;border:2px solid #F2B51C;border-radius:12px;font-size:15px;line-height:1.5;position:relative;color:#13321F}
.term-note::before{content:"💡";position:absolute;left:12px;top:9px}
.js .term-note{display:none}
.js .term-note.open{display:block;animation:pop .18s ease-out}
@keyframes pop{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}
.verdict{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:center;background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:22px;margin:24px 0}
.stamp{justify-self:center;font-weight:900;font-size:clamp(30px,6vw,46px);letter-spacing:.02em;text-transform:uppercase;border:6px solid currentColor;border-radius:14px;padding:6px 18px;transform:rotate(-6deg);line-height:1.1;text-align:center}
.yes{color:#22964F}.sortof{color:#C67A06}.noway{color:#D2372D}
.score b{display:block;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.cells{display:flex;gap:5px;margin:8px 0}.cells i{flex:1;height:22px;border-radius:5px;background:#E6DECC}
.cells i.on{background:currentColor}.score .num{font-size:34px;font-weight:900}
.faceoff{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:0 0 24px}
.faceoff div{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px 16px}
.faceoff small{display:block;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:800}
.faceoff strong{font-size:18px}
.faceoff .f{background:#2A3746;color:#fff;border-color:#2A3746}.faceoff .f small{color:#BFC8D2}
.faceoff .k{background:#FBE7D8;border-color:#F0C6A6}
ol.steps{counter-reset:s;list-style:none;padding:0}
ol.steps>li{counter-increment:s;position:relative;padding:12px 14px 12px 58px;background:#fff;border:1px solid var(--line);border-radius:12px}
ol.steps>li::before{content:counter(s);position:absolute;left:14px;top:12px;width:30px;height:30px;border-radius:50%;background:#F2B51C;color:#13321F;font-weight:900;text-align:center;line-height:30px}
ol.steps.home>li::before{background:#D9481C;color:#fff}
.secret{background:#FFE7A3;border:2px solid #13321F;border-radius:16px;padding:18px 20px;font-size:18px}
.secret b{display:block;font-size:12px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:4px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin:18px 0}
.card{display:block;background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:16px;text-decoration:none;color:inherit}
.card:hover{border-color:var(--ink)}.card[hidden]{display:none}
.card .e{font-size:36px;line-height:1}.card .n{font-weight:900;font-size:19px;margin:6px 0 2px}
.badge{display:inline-block;font-size:12px;font-weight:900;letter-spacing:.05em;text-transform:uppercase;border:2px solid currentColor;border-radius:999px;padding:1px 10px}
.card .j{font-size:14px;color:var(--muted);margin-top:6px;line-height:1.45}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 0}
.chips button{font:inherit;font-weight:800;font-size:14px;border:2px solid var(--line);background:#fff;border-radius:999px;padding:6px 14px;cursor:pointer;color:var(--ink)}
.chips button[aria-pressed=true]{background:var(--ink);color:#fff;border-color:var(--ink)}
dl.gloss dt{font-weight:900;margin-top:12px}dl.gloss dd{margin:2px 0 0}
@media (max-width:560px){.verdict,.faceoff{grid-template-columns:1fr}}
"""

HEAD_JS = '\n  <script>document.documentElement.classList.add("js")</script>'
FOOT_JS = """<script>
document.querySelectorAll(".term").forEach(function (b) {
  b.addEventListener("click", function () {
    var n = document.getElementById(b.getAttribute("aria-controls"));
    var open = b.getAttribute("aria-expanded") !== "true";
    b.setAttribute("aria-expanded", open ? "true" : "false");
    n.classList.toggle("open", open);
  });
});
</script>"""
FOOT = ("</main><footer>© 2026 Zakaria Froud · <a href=\"../about.html\">About</a> · <a href=\"../sources.html\">Sources and method</a> · "
        "Educational content only, not medical or personalised nutrition advice.</footer>" + FOOT_JS +
        "<script defer src=\"../assets/nav.js\"></script></body></html>\n")


class Terms:
    """Turns glossary words into clickable explanations, once per page."""
    def __init__(self):
        self.used, self.tokens = set(), []
        self.patterns = [(t, re.compile(r"(?<![\w-])" + re.escape(t) + r"(?:s|es)?(?!\w)", re.I))
                         for t in sorted(GLOSS, key=len, reverse=True)]

    def __call__(self, text):
        out = E(text)
        hits = []
        for term, pat in self.patterns:
            if term in self.used: continue
            m = pat.search(out)
            if m and not any(m.start() < e and s < m.end() for s, e, _ in hits):
                hits.append((m.start(), m.end(), term))
        notes = []
        for s, e, term in sorted(hits, reverse=True):
            self.used.add(term)
            tid = "t-" + re.sub(r"[^a-z]+", "-", term)
            self.tokens.append(f'<button type="button" class="term" aria-expanded="false" aria-controls="{tid}">{out[s:e]}</button>')
            out = out[:s] + f"\x00{len(self.tokens) - 1}\x00" + out[e:]
            notes.insert(0, f'<span class="term-note" id="{tid}" role="note"><b>{E(term.capitalize())}:</b> {E(GLOSS[term])}</span>')
        if notes:  # explanations open after the sentence, so they never split it
            self.tokens.append("".join(notes))
            out += f"\x00{len(self.tokens) - 1}\x00"
        return out

    def finish(self, page):
        return re.sub(r"\x00(\d+)\x00", lambda m: self.tokens[int(m.group(1))], page)


def meta_desc(p):
    d = f"{p['answer']} Verdict: {VTEXT[p['verdict']].lower()}, {p['score']}/10."
    return d if len(d) <= 160 else d[:157].rsplit(" ", 1)[0] + "…"


def product_page(p, i):
    T = Terms()
    v = VCLASS[p["verdict"]]
    cells = "".join(f'<i class="{"on" if k < p["score"] else ""}"></i>' for k in range(10))
    factory = T(p["factory"])  # page order: the first mention gets the explanation
    steps = "".join(f"<li>{T(s)}</li>" for s in p["steps"])
    secret = T(p["secret"])
    home = "".join(f"<li>{T(s)}</li>" for s in p["home"])
    faq = "".join(f"<h3>{E(q)}</h3><p>{E(a)}</p>" for q, a in p["faq"])
    sources = ("<h2>Sources</h2><ul>" + "".join(
        f'<li><a href="{E(u)}" target="_blank" rel="noopener">{E(t)}</a></li>' for t, u in p["sources"]) + "</ul>") if p["sources"] else ""
    others = [PRODUCTS[(i + k) % len(PRODUCTS)] for k in (1, 2, 3)]
    more = "".join(card(o) for o in others)
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}
    extra = HEAD_JS + f'\n  <script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>'
    title = f"Can You Make {p['name']} at Home?"
    body = head(title, meta_desc(p), f"factory-vs-kitchen/{p['slug']}.html", extra=extra).replace(
        "</head>", f"<style>{STYLE}</style></head>", 1) + f"""
<div class="kicker">Factory vs. Kitchen · {E(p['name'])}</div>
<h1>{E(title)} {p['emoji']}</h1>
<p class="lead">{E(p['answer'])}</p>
<p style="font-size:14px;color:var(--muted)">Tip: tap any <button type="button" class="term" tabindex="-1" aria-hidden="true">underlined word</button> for a quick explanation.</p>
<div class="verdict {v}">
  <div class="stamp">{E(p['verdict'])}</div>
  <div class="score"><b>Kitchen score</b><div class="cells">{cells}</div><span class="num">{p['score']}/10</span></div>
</div>
<div class="faceoff">
  <div class="f"><small>🏭 The factory uses</small><strong>{E(p['gear'][0])}</strong></div>
  <div class="k"><small>🍳 You use</small><strong>{E(p['gear'][1])}</strong></div>
  <div><small>Store price</small><strong>{E(p['cost'][0])}</strong></div>
  <div><small>Homemade cost</small><strong>{E(p['cost'][1])}</strong></div>
</div>
<h2>How the factory makes {E(p['name'])}</h2>
<p>{factory}</p>
<ol class="steps">{steps}</ol>
<h2>The factory secret</h2>
<div class="secret"><b>🔒 What you can't easily copy</b>{secret}</div>
<h2>How to make {E(p['name'])} at home</h2>
<ol class="steps home">{home}</ol>
<p>{T(p['home_tip'])}</p>
<h2>What the label tells you</h2>
<p>{T(p['label'])}</p>
<div class="panel"><p><strong>Read any ingredient list in seconds.</strong> Paste a label into the free <a href="../decoder/">Ingredient Decoder</a> and every ingredient gets explained in plain words.</p></div>
<h2>Questions people ask</h2>
{faq}
{sources}
<p style="font-size:14px;color:var(--muted)"><strong>How to read these estimates:</strong> The kitchen score is an editorial estimate of how closely a home version can match the packaged product; it is not a lab measurement or official rating. Store prices and homemade costs are rough US examples, not live quotes, and vary by retailer, location, date, portion size and pantry assumptions. Recipes and ingredients differ between countries, so check the package in your hand.</p>
<div class="note" style="margin-top:22px"><strong>Want to read labels like this in your head?</strong> Supermarket Decoder is a 53-page illustrated ebook (PDF) with a printable cheat-sheet and a 14-day tracker. <a href="../index.html#inside">See what's inside</a> or <a href="{GUIDE.format(slug=p['slug'])}" target="_blank" rel="noopener">get it on Gumroad ($9)</a>.</div>
<h2>More Factory vs. Kitchen</h2>
<div class="grid">{more}</div>
<p><a class="back" href="index.html">← All Factory vs. Kitchen foods</a></p>
""" + FOOT
    return T.finish(body)


def card(p, href=None):
    v = VCLASS[p["verdict"]]
    parts = p["answer"].split(". ")
    short = parts[0] if len(parts[0]) >= 25 or len(parts) == 1 else parts[0] + ". " + parts[1]
    short = short.rstrip(".") + "."
    return (f'<a class="card" data-v="{v}" href="{href or p["slug"] + ".html"}"><div class="e">{p["emoji"]}</div>'
            f'<div class="n">{E(p["name"])}</div><span class="badge {v}">{E(p["verdict"])} · {p["score"]}/10</span>'
            f'<div class="j">{E(short)}</div></a>')


def index_page():
    cards = "".join(card(p) for p in PRODUCTS)
    gloss = "".join(f'<dt id="g-{re.sub(r"[^a-z]+", "-", t)}">{E(t.capitalize())}</dt><dd>{E(GLOSS[t])}</dd>' for t in sorted(GLOSS))
    chips = "".join(f'<button type="button" data-f="{f}" aria-pressed="{"true" if f == "all" else "false"}">{lab}</button>'
                    for f, lab in (("all", "All"), ("yes", "✅ Yes"), ("sortof", "🟡 Sort of"), ("noway", "⛔ No way")))
    js = """<script>
document.querySelectorAll(".chips button").forEach(function (b) {
  b.addEventListener("click", function () {
    var f = b.getAttribute("data-f");
    document.querySelectorAll(".chips button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
    document.querySelectorAll(".grid .card").forEach(function (c) { c.hidden = f !== "all" && c.getAttribute("data-v") !== f; });
  });
});
</script>"""
    return head("Factory vs. Kitchen: Can You Make It at Home?",
                "How 15 famous packaged foods are really made in factories, the one secret you can't copy, and whether you can make each one at home, with a verdict and a score.",
                "factory-vs-kitchen/", og_type="website", extra=HEAD_JS).replace(
        "</head>", f"<style>{STYLE}</style></head>", 1) + f"""
<div class="kicker">Factory vs. Kitchen</div>
<h1>Can you make it at home?</h1>
<p class="lead">How famous packaged foods are really made, the one factory secret you can't easily copy, and an honest verdict on whether your kitchen can do it.</p>
<div class="panel"><p><strong>How the verdicts work.</strong> <span class="badge yes">Yes</span> means a homemade version is as good or better. <span class="badge sortof">Sort of</span> means you can get most of the way, but one factory trick is missing. <span class="badge noway">No way</span> means the machine or the secret recipe makes it impossible at home. The kitchen score (out of 10) is how close a careful home cook can get.</p></div>
<div class="chips" role="group" aria-label="Filter by verdict">{chips}</div>
<div class="grid">{cards}</div>
<h2>Factory words, explained</h2>
<p>The words you'll meet on these pages, in plain English.</p>
<dl class="gloss">{gloss}</dl>
<div class="panel"><p><strong>Curious what's in the pack itself?</strong> Paste any ingredient list into the free <a href="../decoder/">Ingredient Decoder</a>, or look up additive codes in the <a href="../additives/">E-number pages</a>.</p></div>
<p><a class="back" href="../free-resources/">← All free resources</a></p>
""" + FOOT.replace(FOOT_JS, FOOT_JS + js)


def update_sitemap():
    sm = ROOT / "sitemap.xml"
    text = sm.read_text(encoding="utf-8")
    urls = [f"{SITE}/factory-vs-kitchen/"] + [f"{SITE}/factory-vs-kitchen/{p['slug']}.html" for p in PRODUCTS]
    add = "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls if f"<loc>{u}</loc>" not in text)
    if add:
        sm.write_text(text.replace("</urlset>", add + "</urlset>"), encoding="utf-8", newline="\n")


def main():
    OUT.mkdir(exist_ok=True)
    for i, p in enumerate(PRODUCTS):
        (OUT / f"{p['slug']}.html").write_text(product_page(p, i), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(index_page(), encoding="utf-8", newline="\n")
    update_sitemap()
    print(f"wrote {len(PRODUCTS) + 1} pages to factory-vs-kitchen/")


if __name__ == "__main__":
    main()
