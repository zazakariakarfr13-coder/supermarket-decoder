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


LANGS = ("en", "fr", "ar")
PREFIX = {"en": "", "fr": "fr/", "ar": "ar/"}
TEXT_FIELDS = ["name", "short", "job", "answer", "us_name", "made_from", "vegan", "why", "where", "safety", "faq"]
FREE_FIELDS = ["names", "sample"]  # label names and the decoder example are written for local labels, not guarded

UI = {
    "en": {
        "title": "{code} ({short}): What It Is, Uses and Safety", "kicker": "E-number lookup · {job}",
        "job": "Its job", "made": "Made from", "us": "On US labels", "vegan": "Vegan?", "clue_q": "Ultra-processing clue?",
        "clue_yes": "Yes: a NOVA processing clue", "clue_no": "Not on its own",
        "why_h": "Why is {code} added to food?", "where_h": "Where you'll find it", "safe_h": "Is {code} safe? What the research says",
        "note": "An E-number is an identifier used in the European food-additive numbering system. It does not mean the additive is currently authorised in every country or food category. Rules differ by region and can change, so check local rules. The code is not a danger rating.",
        "labels_h": "How it appears on labels",
        "see": "<strong>See it decoded.</strong> Open a typical label that contains {code} in the free Ingredient Decoder, or paste your own.",
        "decode_btn": "Decode an example label →", "all_btn": "All E-numbers", "faq_h": "Questions people ask about {code}",
        "pocket": "<strong>Keep every code in your pocket.</strong> The E-Number Pocket Reference covers 123 additive codes: what each one does, which are worth a second look, US label names and the clean-label names that hide an additive's job. A5 PDF for your phone or kitchen.",
        "pocket_btn": "Get the pocket reference · $5", "kit_btn": "Complete Kit · $13",
        "guide": "<strong>Want to read labels like this in your head?</strong> Supermarket Decoder is a 53-page illustrated ebook (PDF) with a printable cheat-sheet and a 14-day tracker. <a href=\"../index.html#inside\">See what's inside</a> or <a href=\"{guide}\" target=\"_blank\" rel=\"noopener\">get it on Gumroad ($9)</a>.",
        "related_h": "Related E-numbers", "back_all": "← All E-numbers", "back_expl": "E-numbers explained",
        "idx_title": "Common E-Numbers Explained: What Each Code Means",
        "idx_desc": "Plain-language pages for the E-numbers people look up most: E471, E322, E330, E415, E407, E621, E951, E250, E171, E150d, E211 and E129 (Red 40).",
        "idx_kicker": "E-number lookup", "idx_h1": "Common E-numbers, explained one by one",
        "idx_lead": "What each code is, why it's in your food, where you'll find it and what the research says, without the panic and without the marketing.",
        "idx_pocket": "<strong>Want all of them in your pocket?</strong> The E-Number Pocket Reference covers 123 codes on 16 phone-friendly pages, with traffic-light markers, US label names and the rules that differ between countries.",
        "idx_more": "<strong>Looking for a code that isn't here?</strong> The free <a href=\"../decoder/\">Ingredient Decoder</a> knows more than 300 E-numbers. Paste a whole ingredient list and it explains every one.",
        "idx_note": "An E-number is an identifier used in the European food-additive numbering system. It does not mean the additive is currently authorised in every country or food category. Rules differ by region and can change; check local rules. The code is not a danger rating. <a href=\"../articles/e-numbers-explained.html\">How to read E-numbers sensibly →</a>",
        "idx_back": "← All free resources",
        "header": "Supermarket Decoder · Read · Decode · Swap",
        "foot": "© 2026 Zakaria Froud · <a href=\"../about.html\">About</a> · <a href=\"../sources.html\">Sources and method</a> · Educational content only, not medical or personalised nutrition advice.",
        "english_only": "",
    },
    "fr": {
        "title": "{code} ({short}) : ce que c’est, à quoi ça sert, est-ce sûr ?", "kicker": "Fiche additif · {job}",
        "job": "Son rôle", "made": "Fabriqué à partir de", "us": "Sur les étiquettes américaines", "vegan": "Végan ?",
        "clue_q": "Indice d’ultra-transformation ?", "clue_yes": "Oui : un indice NOVA", "clue_no": "Pas à lui seul",
        "why_h": "Pourquoi ajoute-t-on {code} aux aliments ?", "where_h": "Où le trouve-t-on", "safe_h": "{code} est-il sûr ? Ce que dit la recherche",
        "note": "Un numéro E est un identifiant du système européen de numérotation des additifs. Il ne veut pas dire que l’additif est autorisé aujourd’hui dans tous les pays ou toutes les catégories d’aliments. Les règles varient selon les régions et peuvent changer : vérifiez la réglementation locale. Le code n’est pas une note de danger.",
        "labels_h": "Comment il apparaît sur les étiquettes",
        "see": "<strong>Voyez-le décodé.</strong> Ouvrez une étiquette typique contenant {code} dans le Décodeur d’ingrédients gratuit, ou collez la vôtre.",
        "decode_btn": "Décoder un exemple d’étiquette →", "all_btn": "Tous les additifs", "faq_h": "Questions fréquentes sur {code}",
        "pocket": "<strong>Gardez tous les codes dans votre poche.</strong> L’E-Number Pocket Reference couvre 123 codes d’additifs : le rôle de chacun, ceux qui méritent un second regard, les noms sur les étiquettes américaines et les noms « clean label » qui cachent le rôle d’un additif. PDF A5 pour le téléphone ou la cuisine (en anglais).",
        "pocket_btn": "Le guide de poche · 5 $", "kit_btn": "Kit complet · 13 $",
        "guide": "<strong>Envie de lire les étiquettes comme ça de tête ?</strong> Supermarket Decoder est un ebook illustré de 53 pages (PDF, en anglais) avec une fiche mémo à imprimer et un suivi sur 14 jours. <a href=\"../index.html#inside\">Voir le contenu</a> ou <a href=\"{guide}\" target=\"_blank\" rel=\"noopener\">le prendre sur Gumroad (9 $)</a>.",
        "related_h": "Additifs proches", "back_all": "← Tous les additifs", "back_expl": "Les numéros E expliqués",
        "idx_title": "Les additifs (E) les plus courants : ce que veut dire chaque code",
        "idx_desc": "Des fiches simples pour les additifs les plus recherchés : E471, E322, E330, E415, E407, E621, E951, E250, E171, E150d, E211 et E129 (Red 40).",
        "idx_kicker": "Fiches additifs", "idx_h1": "Les additifs courants, expliqués un par un",
        "idx_lead": "Ce qu’est chaque code, pourquoi il est dans votre assiette, où on le trouve et ce que dit la recherche, sans panique et sans marketing.",
        "idx_pocket": "<strong>Envie de les avoir tous dans la poche ?</strong> L’E-Number Pocket Reference couvre 123 codes sur 16 pages adaptées au téléphone (en anglais), avec des repères couleur, les noms américains et les règles qui diffèrent selon les pays.",
        "idx_more": "<strong>Vous cherchez un code absent d’ici ?</strong> Le <a href=\"../decoder/\">Décodeur d’ingrédients</a> gratuit connaît plus de 300 numéros E. Collez une liste d’ingrédients entière et il les explique tous.",
        "idx_note": "Un numéro E est un identifiant du système européen de numérotation des additifs. Il ne veut pas dire que l’additif est autorisé aujourd’hui dans tous les pays ou toutes les catégories d’aliments. Les règles varient selon les régions et peuvent changer : vérifiez la réglementation locale. Le code n’est pas une note de danger. <a href=\"../articles/e-numbers-explained.html\">Comment lire les numéros E sans s’affoler →</a>",
        "idx_back": "← Toutes les ressources gratuites",
        "header": "Supermarket Decoder · Lire · Décoder · Remplacer",
        "foot": "© 2026 Zakaria Froud · <a href=\"../about.html\">À propos</a> · <a href=\"../sources.html\">Sources et méthode</a> · Contenu éducatif, pas un avis médical ni nutritionnel personnalisé.",
        "english_only": "",
    },
    "ar": {
        "title": "{code} ({short}): ما هو، وفيمَ يُستعمل، وهل هو آمن؟", "kicker": "دليل الإضافات · {job}",
        "job": "وظيفته", "made": "مصنوع من", "us": "على الملصقات الأمريكية", "vegan": "نباتي صرف؟",
        "clue_q": "علامة على المعالجة الفائقة؟", "clue_yes": "نعم: علامة في تصنيف NOVA", "clue_no": "ليس وحده",
        "why_h": "لماذا يُضاف {code} إلى الطعام؟", "where_h": "أين تجده", "safe_h": "هل {code} آمن؟ ماذا تقول الأبحاث",
        "note": "رقم E معرّف في نظام الترقيم الأوروبي للإضافات الغذائية. ولا يعني أن الإضافة مسموح بها حاليًا في كل البلدان أو في كل فئات الطعام. فالقواعد تختلف من منطقة إلى أخرى وقد تتغيّر، لذا راجع القواعد المحلية. والرمز ليس درجة خطورة.",
        "labels_h": "كيف يظهر على الملصقات",
        "see": "<strong>شاهده مفكّكًا.</strong> افتح ملصقًا نموذجيًّا يحتوي على {code} في مفكّك المكوّنات المجاني، أو الصق ملصقك.",
        "decode_btn": "فكّك ملصقًا نموذجيًّا ←", "all_btn": "كل الإضافات", "faq_h": "أسئلة شائعة عن {code}",
        "pocket": "<strong>احمل كل الرموز في جيبك.</strong> يغطّي دليل الجيب لأرقام E (بالإنجليزية) 123 رمزًا: وظيفة كل واحد، وأيّها يستحق نظرة ثانية، وأسماؤها على الملصقات الأمريكية، والأسماء «النظيفة» التي تُخفي وظيفة الإضافة. ملف PDF بحجم A5 للهاتف أو المطبخ.",
        "pocket_btn": "دليل الجيب · 5 $", "kit_btn": "المجموعة الكاملة · 13 $",
        "guide": "<strong>تريد أن تقرأ الملصقات هكذا في ذهنك؟</strong> Supermarket Decoder كتاب إلكتروني مصوّر من 53 صفحة (PDF، بالإنجليزية) مع ورقة ملخّص للطباعة ومتابعة لمدة 14 يومًا. <a href=\"../index.html#inside\">اطّلع على محتواه</a> أو <a href=\"{guide}\" target=\"_blank\" rel=\"noopener\">احصل عليه من Gumroad (9 $)</a>.",
        "related_h": "إضافات ذات صلة", "back_all": "→ كل الإضافات", "back_expl": "أرقام E بشرح مبسّط",
        "idx_title": "أشهر أرقام E بشرح مبسّط: ماذا يعني كل رمز",
        "idx_desc": "صفحات بلغة بسيطة لأكثر أرقام E بحثًا: E471 وE322 وE330 وE415 وE407 وE621 وE951 وE250 وE171 وE150d وE211 وE129 (Red 40).",
        "idx_kicker": "دليل الإضافات", "idx_h1": "أشهر أرقام E، واحدًا واحدًا",
        "idx_lead": "ما هو كل رمز، ولماذا هو في طعامك، وأين تجده، وماذا تقول الأبحاث، دون هلع ودون تسويق.",
        "idx_pocket": "<strong>تريدها كلها في جيبك؟</strong> يغطّي دليل الجيب لأرقام E (بالإنجليزية) 123 رمزًا في 16 صفحة تناسب الهاتف، مع علامات ملوّنة، والأسماء الأمريكية، والقواعد التي تختلف بين البلدان.",
        "idx_more": "<strong>تبحث عن رمز غير موجود هنا؟</strong> <a href=\"../decoder/\">مفكّك المكوّنات</a> المجاني يعرف أكثر من 300 رقم E. الصق قائمة مكوّنات كاملة وسيشرحها كلها.",
        "idx_note": "رقم E معرّف في نظام الترقيم الأوروبي للإضافات الغذائية. ولا يعني أن الإضافة مسموح بها حاليًا في كل البلدان أو في كل فئات الطعام. فالقواعد تختلف من منطقة إلى أخرى وقد تتغيّر، لذا راجع القواعد المحلية. والرمز ليس درجة خطورة. <a href=\"../articles/e-numbers-explained.html\">كيف تقرأ أرقام E بهدوء ←</a>",
        "idx_back": "→ كل الموارد المجانية",
        "header": "Supermarket Decoder · اقرأ · فكّك · استبدل",
        "foot": "© 2026 Zakaria Froud · <a href=\"../about.html\">من نحن</a> · <a href=\"../sources.html\">المصادر والمنهج</a> · محتوى تعليمي، وليس نصيحة طبية أو غذائية شخصية.",
        "english_only": "",
    },
}


def localized(lang, overlay=None):
    """The additives in `lang`: English entries with text fields from scripts/i18n/<lang>/additives.py."""
    if lang == "en":
        return ADDITIVES
    if overlay is None:
        import importlib
        overlay = importlib.import_module(f"i18n.{lang}.additives").TR
    from i18n import guard
    unknown = set(overlay) - set(BY_SLUG)
    if unknown:
        raise ValueError(f"{lang}: unknown additive slugs {sorted(unknown)}")
    out = []
    for a in ADDITIVES:
        tr = overlay.get(a["slug"])
        if tr is None:
            raise ValueError(f"{lang}/{a['slug']}: missing translation")
        b = dict(a)
        for f in TEXT_FIELDS:
            where = f"{lang}/{a['slug']}.{f}"
            if f not in tr:
                raise ValueError(f"{where}: missing")
            (guard.same_list if isinstance(a[f], list) else guard.same)(where, a[f], tr[f])
            b[f] = [tuple(x) for x in tr[f]] if f == "faq" else tr[f]
        for f in FREE_FIELDS:
            if not tr.get(f):
                raise ValueError(f"{lang}/{a['slug']}.{f}: missing")
            b[f] = tr[f]
        out.append(b)
    return out


def _utm(slug, lang):
    return slug if lang == "en" else f"{slug}-{lang}"


def head(title, desc, path, og_type="article", extra="", lang="en"):
    url = f"{SITE}/{PREFIX[lang]}{path}"
    up = "../" if lang == "en" else "../../"
    html_tag = '<html lang="en">' if lang == "en" else (f'<html lang="{lang}" dir="rtl">' if lang == "ar" else f'<html lang="{lang}">')
    title_full = f"{E(title)} | Supermarket Decoder"
    return f"""<!doctype html>
{html_tag}<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title_full}</title>
  <meta name="description" content="{E(desc)}">
  <link rel="canonical" href="{url}">
  <link rel="icon" href="{up}favicon.svg" type="image/svg+xml">
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
  <link rel="stylesheet" href="{up}assets/site.css">
  <style>{STYLE}</style>{extra}
</head><body class="with-side"><header><a href="../index.html">{UI[lang]['header']}</a></header><main>"""


def foot(lang="en"):
    up = "../" if lang == "en" else "../../"
    return f"""</main><footer>{UI[lang]['foot']}</footer><script defer src="{up}assets/nav.js"></script></body></html>
"""


FOOT = foot("en")


def _desc(text):
    return text if len(text) <= 158 else text[:155].rsplit(" ", 1)[0] + "…"


def additive_page(a, lang="en"):
    T = UI[lang]
    code, slug = a["code"], a["slug"]
    items = a.get("_by") or BY_SLUG
    title = T["title"].format(code=code, short=a["short"])
    desc = _desc(a["answer"])
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in a["faq"]]}
    extra = f'\n  <script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>'
    clue = (f'<span class="clue">{T["clue_yes"]}</span>' if a["clue"]
            else f'<span class="clue no">{T["clue_no"]}</span>')
    where = "".join(f"<li>{E(w)}</li>" for w in a["where"])
    names = "".join(f"<li>{E(n)}</li>" for n in a["names"])
    faq = "".join(f"<h3>{E(q)}</h3><p>{E(ans)}</p>" for q, ans in a["faq"])
    related = "".join(
        f'<a class="code" href="{r}.html"><div class="c">{E(items[r]["code"])}</div><div class="n">{E(items[r]["short"])}</div><div class="j">{E(items[r]["job"])}</div></a>'
        for r in a["related"])
    decoder = "../decoder/#list=" + quote(a["sample"], safe="")
    u = _utm(slug, lang)
    return head(title, desc, f"additives/{slug}.html", extra=extra, lang=lang) + f"""
<div class="kicker">{T['kicker'].format(job=E(a['job']))}</div>
<h1>{E(code)}: {E(a['name'])}</h1>
<p class="lead">{E(a['answer'])}</p>
<div class="facts">
  <div class="fact"><b>{T['job']}</b><span>{E(a['job'])}</span></div>
  <div class="fact"><b>{T['made']}</b><span>{E(a['made_from'])}</span></div>
  <div class="fact"><b>{T['us']}</b><span>{E(a['us_name'])}</span></div>
  <div class="fact"><b>{T['vegan']}</b><span>{E(a['vegan'])}</span></div>
  <div class="fact"><b>{T['clue_q']}</b><span>{clue}</span></div>
</div>
<h2>{T['why_h'].format(code=E(code))}</h2>
<p>{E(a['why'])}</p>
<h2>{T['where_h']}</h2>
<ul>{where}</ul>
<h2>{T['safe_h'].format(code=E(code))}</h2>
<p>{E(a['safety'])}</p>
<div class="note">{T['note']}</div>
<h2>{T['labels_h']}</h2>
<ul class="names">{names}</ul>
<div class="panel">
  <p>{T['see'].format(code=E(code))}</p>
  <div class="cta-row"><a class="pill" href="{decoder}">{T['decode_btn']}</a><a class="pill ghost" href="index.html">{T['all_btn']}</a></div>
</div>
<h2>{T['faq_h'].format(code=E(code))}</h2>
{faq}
<div class="panel" style="margin-top:22px;border:2px solid var(--gold,#F2B51C)"><p>{T['pocket']}</p><div class="cta-row"><a class="pill" href="{POCKET.format(slug=u)}" target="_blank" rel="noopener">{T['pocket_btn']}</a><a class="pill ghost" href="{KIT.format(slug=u)}" target="_blank" rel="noopener">{T['kit_btn']}</a></div></div>
<div class="note" style="margin-top:22px">{T['guide'].format(guide=GUIDE.format(slug=u))}</div>
<h2>{T['related_h']}</h2>
<div class="codes">{related}</div>
<p><a class="back" href="index.html">{T['back_all']}</a> · <a class="back" href="../articles/e-numbers-explained.html">{T['back_expl']}</a></p>
""" + foot(lang)


def index_page(lang="en", items=None):
    T = UI[lang]
    items = items or ADDITIVES
    cards = "".join(
        f'<a class="code" href="{a["slug"]}.html"><div class="c">{E(a["code"])}</div><div class="n">{E(a["name"])}</div><div class="j">{E(a["job"])}</div></a>'
        for a in items)
    u = _utm("index", lang)
    return head(T["idx_title"], T["idx_desc"], "additives/", og_type="website", lang=lang) + f"""
<div class="kicker">{T['idx_kicker']}</div>
<h1>{T['idx_h1']}</h1>
<p class="lead">{T['idx_lead']}</p>
<div class="codes">{cards}</div>
<div class="panel" style="border:2px solid var(--gold,#F2B51C)"><p>{T['idx_pocket']}</p><div class="cta-row"><a class="pill" href="{POCKET.format(slug=u)}" target="_blank" rel="noopener">{T['pocket_btn']}</a><a class="pill ghost" href="{KIT.format(slug=u)}" target="_blank" rel="noopener">{T['kit_btn']}</a></div></div>
<div class="panel"><p>{T['idx_more']}</p></div>
<div class="note">{T['idx_note']}</div>
<p><a class="back" href="../free-resources/">{T['idx_back']}</a></p>
""" + foot(lang)


def available_langs():
    import importlib.util
    return ["en"] + [l for l in ("fr", "ar") if importlib.util.find_spec(f"i18n.{l}.additives")]


def build_pages():
    import i18n_pages
    written = 0
    for lang in available_langs():
        items = localized(lang)
        by = {a["slug"]: a for a in items}
        out = ROOT / PREFIX[lang] / "additives"
        out.mkdir(parents=True, exist_ok=True)
        for a in items:
            a = dict(a, _by=by)
            (out / f"{a['slug']}.html").write_text(additive_page(a, lang), encoding="utf-8", newline="\n")
        (out / "index.html").write_text(index_page(lang, items), encoding="utf-8", newline="\n")
        written += len(items) + 1
    i18n_pages.main([])
    print(f"wrote {written} additive pages")


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
