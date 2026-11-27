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
from make_additives import head, SITE, PREFIX  # noqa: E402
from i18n.fvk_ui import UI  # noqa: E402

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

STYLE_INDEX = STYLE.replace("dl.gloss dt{", ".filter-status{margin:10px 0 0;color:var(--muted);font-size:14px}\ndl.gloss dt{", 1)

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
TEXT_FIELDS = ["cost", "gear", "answer", "factory", "steps", "secret", "home", "home_tip", "label", "faq"]


def foot(lang="en"):
    up = "../" if lang == "en" else "../../"
    return f"</main><footer>{UI[lang]['foot']}</footer>" + FOOT_JS + f"<script defer src=\"{up}assets/nav.js\"></script></body></html>\n"


FOOT = foot("en")


def localized(lang, overlay=None):
    """Products in `lang`: English entries with text from scripts/i18n/<lang>/fvk.py (numbers guarded)."""
    if lang == "en":
        return PRODUCTS
    if overlay is None:
        import importlib
        overlay = importlib.import_module(f"i18n.{lang}.fvk").TR
    from i18n import guard
    out = []
    for p in PRODUCTS:
        tr = overlay.get(p["slug"])
        if tr is None:
            raise ValueError(f"{lang}/{p['slug']}: missing translation")
        q = dict(p)
        for f in TEXT_FIELDS:
            where = f"{lang}/{p['slug']}.{f}"
            if f not in tr:
                raise ValueError(f"{where}: missing")
            if isinstance(p[f], (list, tuple)):
                guard.same_list(where, list(p[f]), list(tr[f]))
            else:
                guard.same(where, p[f], tr[f])
            q[f] = [tuple(x) for x in tr[f]] if f == "faq" else (tuple(tr[f]) if isinstance(p[f], tuple) else tr[f])
        q["name"] = tr.get("name", p["name"])
        out.append(q)
    return out


def gloss_for(lang):
    if lang == "en":
        return GLOSS
    import importlib
    return importlib.import_module(f"i18n.{lang}.fvk").GLOSS


class Terms:
    """Turns glossary words into clickable explanations, once per page."""
    def __init__(self, gloss=None, lang="en"):
        self.gloss, self.lang = (GLOSS if gloss is None else gloss), lang
        self.used, self.tokens = set(), []
        # Arabic glues "the", "and", "with" to the word (المِبثق، والمبثق، بالمبثق): allow those prefixes.
        pre = r"(?<![\w-])(?:و?[بلفك]?(?:ال)?)?" if lang == "ar" else r"(?<![\w-])"
        self.patterns = [(t, re.compile(pre + re.escape(t) + r"(?:s|es)?(?!\w)", re.I))
                         for t in sorted(self.gloss, key=len, reverse=True)]
        self.ids = {t: (re.sub(r"[^a-z]+", "-", t) if lang == "en" else str(i)) for i, t in enumerate(sorted(self.gloss))}

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
            tid = "t-" + self.ids[term]
            self.tokens.append(f'<button type="button" class="term" aria-expanded="false" aria-controls="{tid}">{out[s:e]}</button>')
            out = out[:s] + f"\x00{len(self.tokens) - 1}\x00" + out[e:]
            notes.insert(0, f'<span class="term-note" id="{tid}" role="note"><b>{E(term.capitalize())}{" :" if self.lang == "fr" else ":"}</b> {E(self.gloss[term])}</span>')
        if notes:  # explanations open after the sentence, so they never split it
            self.tokens.append("".join(notes))
            out += f"\x00{len(self.tokens) - 1}\x00"
        return out

    def finish(self, page):
        return re.sub(r"\x00(\d+)\x00", lambda m: self.tokens[int(m.group(1))], page)


def meta_desc(p, lang="en"):
    d = UI[lang]["meta"].format(answer=p["answer"], verdict=UI[lang]["vtext"][p["verdict"]].lower(), score=p["score"])
    return d if len(d) <= 160 else d[:157].rsplit(" ", 1)[0] + "…"


def product_page(p, i, lang="en", items=None, gloss=None):
    U = UI[lang]
    items = items or PRODUCTS
    T = Terms(gloss, lang) if lang != "en" or gloss is not None else Terms()
    v = VCLASS[p["verdict"]]
    cells = "".join(f'<i class="{"on" if k < p["score"] else ""}"></i>' for k in range(10))
    factory = T(p["factory"])  # page order: the first mention gets the explanation
    steps = "".join(f"<li>{T(s)}</li>" for s in p["steps"])
    secret = T(p["secret"])
    home = "".join(f"<li>{T(s)}</li>" for s in p["home"])
    faq = "".join(f"<h3>{E(q)}</h3><p>{E(a)}</p>" for q, a in p["faq"])
    sources = (f"<h2>{U['sources_h']}</h2><ul>" + "".join(
        f'<li><a href="{E(u)}" target="_blank" rel="noopener">{E(t)}</a></li>' for t, u in p["sources"]) + "</ul>") if p["sources"] else ""
    others = [items[(i + k) % len(items)] for k in (1, 2, 3)]
    more = "".join(card(o, lang=lang) for o in others)
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}
    extra = HEAD_JS + f'\n  <script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>'
    title = U["title"].format(name=p["name"])
    u = p["slug"] if lang == "en" else f"{p['slug']}-{lang}"
    stamp = U["stamp"][p["verdict"]]
    body = head(title, meta_desc(p, lang), f"factory-vs-kitchen/{p['slug']}.html", extra=extra, lang=lang).replace(
        "</head>", f"<style>{STYLE}</style></head>", 1) + f"""
<div class="kicker">{E(U['kicker'].format(name=p['name']))}</div>
<h1>{E(title)} {p['emoji']}</h1>
<p class="lead">{E(p['answer'])}</p>
<p style="font-size:14px;color:var(--muted)">{U['tip']}</p>
<div class="verdict {v}">
  <div class="stamp">{E(stamp)}</div>
  <div class="score"><b>{U['score']}</b><div class="cells">{cells}</div><span class="num">{p['score']}/10</span></div>
</div>
<div class="faceoff">
  <div class="f"><small>{U['factory_uses']}</small><strong>{E(p['gear'][0])}</strong></div>
  <div class="k"><small>{U['you_use']}</small><strong>{E(p['gear'][1])}</strong></div>
  <div><small>{U['store']}</small><strong>{E(p['cost'][0])}</strong></div>
  <div><small>{U['homemade']}</small><strong>{E(p['cost'][1])}</strong></div>
</div>
<h2>{E(U['how_factory'].format(name=p['name']))}</h2>
<p>{factory}</p>
<ol class="steps">{steps}</ol>
<h2>{U['secret_h']}</h2>
<div class="secret"><b>{U['secret_b']}</b>{secret}</div>
<h2>{E(U['how_home'].format(name=p['name']))}</h2>
<ol class="steps home">{home}</ol>
<p>{T(p['home_tip'])}</p>
<h2>{U['label_h']}</h2>
<p>{T(p['label'])}</p>
<div class="panel"><p>{U['decoder']}</p></div>
<h2>{U['faq_h']}</h2>
{faq}
{sources}
<p style="font-size:14px;color:var(--muted)">{U['estimates']}</p>
<div class="note" style="margin-top:22px">{U['guide'].format(guide=GUIDE.format(slug=u))}</div>
<h2>{U['more_h']}</h2>
<div class="grid">{more}</div>
<p><a class="back" href="index.html">{U['back']}</a></p>
""" + foot(lang)
    return T.finish(body)


def card(p, href=None, lang="en"):
    v = VCLASS[p["verdict"]]
    stamp = UI[lang]["stamp"][p["verdict"]]
    parts = p["answer"].split(". ")
    short = parts[0] if len(parts[0]) >= 25 or len(parts) == 1 else parts[0] + ". " + parts[1]
    short = short.rstrip(".") + "."
    return (f'<a class="card" data-v="{v}" href="{href or p["slug"] + ".html"}"><div class="e">{p["emoji"]}</div>'
            f'<div class="n">{E(p["name"])}</div><span class="badge {v}">{E(stamp)} · {p["score"]}/10</span>'
            f'<div class="j">{E(short)}</div></a>')



FILTER_JS_EN = '<script>\n(function () {\n  var buttons = Array.prototype.slice.call(document.querySelectorAll(".chips button"));\n  var cards = Array.prototype.slice.call(document.querySelectorAll("#food-grid .card"));\n  var status = document.getElementById("filter-status");\n\n  function applyFilter(button) {\n    var filter = button.getAttribute("data-f");\n    var visible = 0;\n\n    buttons.forEach(function (item) {\n      item.setAttribute("aria-pressed", item === button ? "true" : "false");\n    });\n\n    cards.forEach(function (card) {\n      var show = filter === "all" || card.getAttribute("data-v") === filter;\n      card.hidden = !show;\n      if (show) visible += 1;\n    });\n\n    status.textContent = filter === "all"\n      ? "Showing all " + visible + " foods."\n      : "Showing " + visible + (visible === 1 ? " food" : " foods") + " in this category.";\n  }\n\n  buttons.forEach(function (button) {\n    button.addEventListener("click", function () {\n      applyFilter(button);\n    });\n  });\n})();\n</script>'
_STATUS_EN = '      ? "Showing all " + visible + " foods."\n      : "Showing " + visible + (visible === 1 ? " food" : " foods") + " in this category.";'
_STATUS = {'fr': '      ? "Les " + visible + " produits sont affichés."\n      : (visible === 1 ? "1 produit affiché" : visible + " produits affichés") + " dans cette catégorie.";', 'ar': '      ? "تُعرض كل المنتجات: " + visible + "."\n      : "عدد المنتجات المعروضة في هذه الفئة: " + visible + ".";'}


def filter_js(lang="en"):
    return FILTER_JS_EN if lang == "en" else FILTER_JS_EN.replace(_STATUS_EN, _STATUS[lang])

def index_page(lang="en", items=None, gloss=None):
    U = UI[lang]
    items = items or PRODUCTS
    G = GLOSS if gloss is None else gloss
    cards = "".join(card(p, lang=lang) for p in items)
    gid = (lambda t, i: re.sub(r"[^a-z]+", "-", t)) if lang == "en" else (lambda t, i: str(i))
    gloss_html = "".join(f'<dt id="g-{gid(t, i)}">{E(t.capitalize())}</dt><dd>{E(G[t])}</dd>' for i, t in enumerate(sorted(G)))
    chips = "".join(f'<button type="button" data-f="{f}" aria-controls="food-grid" aria-pressed="{"true" if f == "all" else "false"}">{U["chips"][f]}</button>'
                    for f in ("all", "yes", "sortof", "noway"))
    js = """<script>
document.querySelectorAll(".chips button").forEach(function (b) {
  b.addEventListener("click", function () {
    var f = b.getAttribute("data-f");
    document.querySelectorAll(".chips button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
    document.querySelectorAll(".grid .card").forEach(function (c) { c.hidden = f !== "all" && c.getAttribute("data-v") !== f; });
  });
});
</script>"""
    return head(U["idx_title"], U["idx_desc"], "factory-vs-kitchen/", og_type="website", extra=HEAD_JS, lang=lang).replace(
        "</head>", f"<style>{STYLE_INDEX}</style></head>", 1) + f"""
<div class="kicker">{U['idx_kicker']}</div>
<h1>{U['idx_h1']}</h1>
<p class="lead">{U['idx_lead']}</p>
<div class="panel"><p>{U['idx_how']}</p></div>
<p class="method-note">{U['method']}</p>
<div class="chips" role="group" aria-label="{U['filter']}">{chips}</div>
<p class="filter-status" id="filter-status" role="status" aria-live="polite" aria-atomic="true">{U['status_all'].format(n=len(items))}</p>
<div class="grid" id="food-grid">{cards}</div>
<h2>{U['words_h']}</h2>
<p>{U['words_p']}</p>
<dl class="gloss">{gloss_html}</dl>
<div class="panel"><p>{U['idx_more']}</p></div>
<p><a class="back" href="../free-resources/">{U['idx_back']}</a></p>
""" + foot(lang).replace(FOOT_JS, FOOT_JS + filter_js(lang))


def update_sitemap():
    sm = ROOT / "sitemap.xml"
    text = sm.read_text(encoding="utf-8")
    urls = [f"{SITE}/factory-vs-kitchen/"] + [f"{SITE}/factory-vs-kitchen/{p['slug']}.html" for p in PRODUCTS]
    add = "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls if f"<loc>{u}</loc>" not in text)
    if add:
        sm.write_text(text.replace("</urlset>", add + "</urlset>"), encoding="utf-8", newline="\n")


def available_langs():
    import importlib.util
    return ["en"] + [l for l in ("fr", "ar") if importlib.util.find_spec(f"i18n.{l}.fvk")]


def main():
    import i18n_pages
    update_sitemap()
    for lang in available_langs():
        items, gloss = localized(lang), (None if lang == "en" else gloss_for(lang))
        out = ROOT / PREFIX[lang] / "factory-vs-kitchen"
        out.mkdir(parents=True, exist_ok=True)
        for i, p in enumerate(items):
            html_ = product_page(p, i) if lang == "en" else product_page(p, i, lang, items, gloss)
            (out / f"{p['slug']}.html").write_text(html_, encoding="utf-8", newline="\n")
        (out / "index.html").write_text(index_page() if lang == "en" else index_page(lang, items, gloss), encoding="utf-8", newline="\n")
        print(f"wrote {len(items) + 1} pages to {PREFIX[lang]}factory-vs-kitchen/")
    i18n_pages.main([])


if __name__ == "__main__":
    main()
