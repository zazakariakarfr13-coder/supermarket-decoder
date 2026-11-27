# Supermarket Decoder in English, French and Arabic: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every public page of Supermarket Decoder exists in EN, FR (`fr/`) and AR (`ar/`, right to left), with a static switcher, hreflang, a multilingual sitemap, a working decoder in all three languages, and checks that keep numbers and E-codes identical across languages.

**Architecture:** The site is served from the repo root with no build step, so French and Arabic pages are committed files. Hand-written pages get hand-translated twins under `fr/` and `ar/` with the same path. Generated pages (additives, Factory vs. Kitchen) get text-only overlays (`scripts/i18n/{fr,ar}/*.py`) that their generators read. The decoder's logic moves to `assets/decoder.js`; its words move to `assets/decoder-text.{en,fr,ar}.js`. One script, `scripts/i18n_pages.py`, owns the shared markup on every page (hreflang block, switcher, Arabic stylesheet link) between marker comments, plus the sitemap; `check_site.py` fails if running it would change anything.

**Tech Stack:** Python 3.12 stdlib, `unittest`; plain browser JS + `node --test` for the decoder; static CSS.

**Spec:** `docs/superpowers/specs/2026-11-26-multilingual-design.md` (Shared and Supermarket Decoder sections). Keep or Toss (`../keep-or-toss`, already live in three languages) is the reference implementation for the shared decisions: reuse its glossary, number-guard rules, switcher look, RTL rules and font files.

## Global Constraints

- Languages `("en", "fr", "ar")`; English stays at its current paths; `fr/<path>`, `ar/<path>`; file names unchanged.
- `<html lang="fr">`, `<html lang="ar" dir="rtl">`; hreflang en/fr/ar + x-default (English) on every page; canonical = own language; `og:locale` en_US / fr_FR / ar_AR.
- Switcher labels `EN`, `FR`, `عربي`, static HTML in the header, current one `<span aria-current="true">`.
- Numbers, E-codes (`E471`, `E150d`), percentages, prices (`$9`), years and URLs identical in every language (checked).
- Western digits in Arabic; Modern Standard Arabic; French "vous". Character names Mina, Tariq, Uncle Kamil (Oncle Kamil / العم كامل), brand and product names unchanged.
- Gumroad links keep their URLs; `utm_content` gets a `-fr` / `-ar` suffix; next to each buy button on FR/AR pages: the guide is in English.
- Shared `assets/` (one copy); Noto Naskh Arabic woff2 + OFL copied from `../keep-or-toss/static/fonts/`.
- English pages change only by: the marker blocks (hreflang + switcher), and the decoder page loading its script from `assets/` (behaviour identical).
- No new dependencies; never put the paid PDF in the repo; commit locally per task; push only with the owner's yes.

## Review Focus

- A French or Arabic page linking to an English page (other than the switcher), or to a missing twin → `check_site` fails (Task 4 tests).
- The English decoder giving any different result after the split → Task 6 golden test compares decoded output of every sample before/after.
- A translated decoder explanation that changes an E-code, number or the Southampton warning's wording strength → Task 6 overlay guard.
- Arabic search typed without the article or hamza (`سكر` finds `السكر`) → Task 3 node test.
- `check_site.py`'s content requirements (decoder caveats, FvK verdict blocks) must hold on FR/AR twins too, in their language → Task 4 per-language required strings.

---

### Task 1: Shared page markup and sitemap (`scripts/i18n_pages.py`)

**Files:** Create `scripts/i18n_pages.py`, `tests/test_i18n_pages.py`, `tests/__init__.py`. Modify every `*.html` (marker blocks), `sitemap.xml`.

**Interfaces — produces:**
- `LANGS`, `PREFIX = {"en": "", "fr": "fr/", "ar": "ar/"}`, `SITE`, `public_pages() -> list[str]` (English paths, e.g. `"articles/e-numbers-explained.html"`, `"decoder/index.html"`; skips graphify-out, marketing, pins, gallery, scripts, docs).
- `twin(path, lang) -> str`, `lang_of(path) -> str`, `base_of(path) -> str`.
- `page_url(path) -> str` (folder `index.html` → trailing slash, as the sitemap writes today).
- `head_block(path) -> str`: between `<!--i18n:head-->` and `<!--/i18n:head-->`: the 4 hreflang links, `og:locale`, and for Arabic `<link rel="stylesheet" href="…/assets/lang-ar.css">`.
- `switcher(path) -> str`: between `<!--i18n:switch-->` markers, placed right after the opening `<header>` content (or `<body>` when a page has no `<header>`), relative links to twins that exist.
- `apply(text, path) -> str` (idempotent), `write_all() -> list[str]` changed files, `sitemap() -> str` (every page in every language, `xhtml:link` alternates), CLI `py -3 scripts/i18n_pages.py [--check]`.

- [ ] Tests first: idempotence (`apply(apply(x)) == apply(x)`), hreflang hrefs for `articles/x.html` in fr, switcher link from `fr/articles/x.html` to `../../ar/articles/x.html`, sitemap has alternates and `x-default`, missing twins are left out of the switcher and sitemap while translations are in progress.
- [ ] Implement; run `py -3 scripts/i18n_pages.py`; `python scripts/check_site.py` still passes on English.
- [ ] Commit "Add shared language markup and multilingual sitemap".

### Task 2: RTL, switcher style, Arabic font

**Files:** Modify `assets/site.css` (8 left/right rules), `assets/nav.css` (7). Create `assets/lang-ar.css`, `assets/fonts/NotoNaskhArabic-{400,700}.woff2`, `assets/fonts/OFL.txt` (copied from Keep or Toss).

- [ ] Logical properties (`inset-inline-*`, `margin-inline-*`, `padding-inline-*`, `text-align: start/end`, `border-inline-*`); the ☰ menu (fixed, top right) mirrors to top left in Arabic; `.lang-switch` styled like Keep or Toss (44 px targets).
- [ ] `lang-ar.css`: same rules as Keep or Toss (`letter-spacing: 0`, no `text-transform`, Naskh, line-height 1.75, `bdi`).
- [ ] Check: English pages pixel-compare unchanged in the preview (home, an article, decoder) before/after.
- [ ] Commit.

### Task 3: Menu and search in three languages (`assets/nav.js`, `scripts/make_search_index.py`)

**Interfaces — produces:** `assets/search-index.json` (English, unchanged format), `assets/search-index.fr.json`, `assets/search-index.ar.json` (entries `u` relative to the site root, e.g. `fr/articles/x.html`; groups translated). `nav.js` picks strings and index by `document.documentElement.lang`. It stays one plain script; its pure `match` and `fold` functions are tested by loading the file in node, behind a guard at the end (`if (typeof module !== "undefined") module.exports = {match, fold}`) and a guard at the top that skips the DOM work when there is no `document`.

- [ ] Node tests (`tests/js/nav.test.cjs`): French accent fold, Arabic article/hamza fold, English ranking unchanged.
- [ ] Strings for: Menu, Site contents, On this page, Verdict, Kitchen score, The guide, Read any label in 30 seconds, 53-page illustrated ebook…, Get it · $9 (+ "in English" note), Free tools and their 4 entries, More in {group}, search status/no-match lines.
- [ ] `check_site.py` already fails if the committed index is stale; extend that to the FR/AR files.
- [ ] Commit.

### Task 4: Language checks in `scripts/check_site.py`

- [ ] Tests (`tests/test_check_site_lang.py`, temp copies of 2-3 pages): missing twin (once a page has any twin, all languages are required), wrong `lang`/`dir`, hreflang to a missing page, FR page linking into English, markers stale (`i18n_pages.py --check`), required content strings per language (decoder caveats, FvK verdict pieces: the existing English list becomes a dict per language).
- [ ] Implement; commit.

### Task 5: Generated sections in three languages

**Files:** Modify `scripts/make_additives.py`, `scripts/make_fvk.py`; create `scripts/i18n/__init__.py` (loader), `scripts/i18n/guard.py` (port of Keep or Toss `number_tokens`, plus E-code tokens `E\d{3,4}[a-z]?`), `scripts/i18n/{fr,ar}/additives.py`, `scripts/i18n/{fr,ar}/fvk.py`, `scripts/i18n/{fr,ar}/ui.py` (page chrome words of both generators).

- [ ] Tests: overlay missing field fails; number/E-code mismatch fails; `make_additives.py pages` writes `additives/`, `fr/additives/`, `ar/additives/`; same for FvK; English output byte-identical to before (except marker blocks).
- [ ] Translate the 12 additive entries and index text, then the 15 FvK products and index text, FR and AR.
- [ ] Commit per section.

### Task 6: Decoder split and decoder text in three languages

**Files:** Create `assets/decoder.js` (both scripts from `decoder/index.html`, unchanged logic), `assets/decoder-text.en.js` (every user-facing string: UI labels, messages, `F` function names, `E` names, `E_MORE`, `DICT` `t`/`d`, `CLASSES` labels, `ALLERGENS`, `SAMPLES`, `SOUTHAMPTON`), `assets/decoder-text.fr.js`, `assets/decoder-text.ar.js`, `tests/js/decoder.test.cjs`, `tests/js/golden-en.json`.

**Interfaces:** text files set `window.SD_TEXT = {lang, ui:{…}, f:{…}, e:{code: name}, eMore:{code: text}, dict:{<English title>: {t, d}}, …}`; FR/AR files hold the same keys. `decoder.js` reads `window.SD_TEXT`; match patterns stay in `decoder.js` and keep reading French names as today (`norm()`).

- [ ] Before moving anything: write `golden-en.json` = decoded output (JSON of items: name, kind, title, text, E-code, link) for every sample plus 20 real ingredient lists (English and French labels), from the current page, using node + a tiny DOM-free harness.
- [ ] Move code; golden test must pass byte-for-byte in English.
- [ ] Overlay test: every key in EN exists in FR/AR, numbers/E-codes/percentages identical (same guard as Task 5), no empty strings.
- [ ] Translate (FR, then AR). The Southampton warning is quoted as the EU's official French/Arabic-equivalent wording, keeping "may".
- [ ] `fr/decoder/index.html`, `ar/decoder/index.html`: small pages loading `../../assets/decoder-text.fr.js` then `../../assets/decoder.js`; Open Food Facts lookup asks for `ingredients_text_fr` first on the French page (already in FIELDS); Arabic page keeps the same order as English.
- [ ] Commit.

### Task 7: Hand-written pages, French

Home, about, sources, 404 (shared root 404 gains FR/AR links, as in Keep or Toss), free-resources (5), articles (4), story (index, episode-02, cases), stories (1). Copy each page to `fr/…`, translate text, alt text, titles, descriptions (≤ 160 characters), keep markup, fix relative paths (`../` depth +1), link inner pages to French twins, Gumroad `utm_content` suffix `-fr` + "guide in English" line. Run `i18n_pages.py`, `check_site.py`. Commit in batches (resources+articles, home+about+sources, comic+stories).

### Task 8: Hand-written pages, Arabic

Same as Task 7 into `ar/…`, plus `dir="rtl"` checks of any inline styles with left/right in the comic pages (switch to logical properties inside the page). Commit in batches.

### Task 9: Cross-links and Keep or Toss

- [ ] Keep or Toss: `DECODER_URL` per language (`…/fr/decoder/`, `…/ar/decoder/`), drop the "Decoder in English" note; small change in `../keep-or-toss` on its own branch, owner approval before push.
- [ ] Decoder sidebar "Keep or Toss" link → the same language on Keep or Toss.

### Task 10: Verify and preview

- [ ] `python scripts/check_site.py` 0 errors; `py -3 scripts/i18n_pages.py --check` clean; `node --test tests/js/`; `py -3 -m unittest discover -s tests`.
- [ ] Browser: EN/FR/AR home, an article, an E-number page, an FvK page, comic episode, decoder (paste a sample, scan button present), phone width; no console errors.
- [ ] Update README and DEVELOPMENT_LOG; CI workflow unchanged (it runs `check_site.py`). Owner approval before push.
