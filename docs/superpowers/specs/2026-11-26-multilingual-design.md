# English, French and Arabic for both sites: design

Date: 2026-11-26. Covers **Keep or Toss** (`keep-or-toss/`) and **Supermarket Decoder** (`Zakaria/`).
The same document is kept in both repos under `docs/superpowers/specs/`.

## Intent

The owner is in Morocco, where French and Arabic are the everyday languages. Both sites are English only.
The goal is full French and Arabic versions of every public page on both sites, with a visible language
switcher, so Moroccan (and wider French- and Arabic-speaking) readers can use them in their own language.

## Goals

- Every public page on both sites exists in EN, FR and AR (owner chose "everything", not a core subset).
- A visible switcher on every page goes to the same page in the other language.
- Arabic pages are right to left and mirrored, with an Arabic-friendly font.
- Search engines see the three versions as translations of each other: `hreflang` tags and sitemap entries.
- Translations read as written by a careful person, not word-for-word machine output.

## Non-goals

- No auto-redirect by browser language. The English home stays at `/`; readers choose.
- No translated URL slugs (`/fr/food/eggs/`, not `/fr/aliments/oeufs/`).
- No Darija. Arabic is Modern Standard Arabic, written simply.
- No new pages, foods, additives or articles. Same content set in three languages.
- Pinterest pins, videos, the Etsy and Gumroad products, `marketing/` and `pins/` are not translated.
- The decoder does not learn to read Arabic-script ingredient lists in this round (see "Later").

## Anti-goals (would be a failure even if it "works")

- Any number, time, temperature, E-number, percentage or source that differs between languages.
- A translated page that softens or strengthens a food-safety or health claim (for example turning
  "throw it out" into "probably best to throw it out", or "may have an adverse effect" into "causes").
- Half-translated pages (English paragraphs inside a French page) going live.
- Thin or near-duplicate pages: each translated page is a full twin of a real English page, nothing more.
- The paid PDF ending up in the public repo.
- Breaking the live English site: its URLs, tests, checks and the decoder must keep working unchanged.

## Constraints

- Both sites are static GitHub Pages sites. Keep or Toss is built by CI from `kot/` + `data/`.
  Supermarket Decoder is served straight from the repo root (no build step).
- Python generators, no new dependencies. Plain JS, no bundler.
- CI already runs: Keep or Toss: unit tests, `node --test tests/js/`, build, `scripts/check_site.py _site`.
  Supermarket Decoder: `scripts/check_site.py` (links, fragments, sitemap, metadata).
- The privacy page says no tracking: fonts must not load from Google's servers.
- Ask before any `git push`. Owner is busy with exams: few, clear questions.

## Approaches considered

**Keep or Toss:** only one sensible way. The site is fully generated, so translations go in as data
next to the English data and the generator renders each language. Hand copies of generated pages
would fall out of date at once.

**Supermarket Decoder**, two options were weighed:

1. **Translated copies plus a helper script (chosen by the owner).** Hand-written pages get translated
   twins under `fr/` and `ar/`. Generated sections (additives, Factory vs. Kitchen) get translated data
   and their generators write all three languages. A helper script adds the switcher, hreflang tags
   and sitemap entries to every page and the check fails when any twin is missing.
   Trade-off: an edit to an English hand-written page needs the same edit in its two twins; the check
   catches missing twins, not stale ones.
2. **Rebuild every page through a generator, then translate.** Cleanest to maintain, but rewrites every
   hand-written page of a live site before any translation, with real risk to the decoder and the comic.
   Rejected for risk and size.

## Shared decisions (both sites)

- **URLs:** English stays where it is. French under `/fr/`, Arabic under `/ar/`, same paths below that.
  Example: `food/eggs/` → `fr/food/eggs/`, `ar/food/eggs/`; `articles/e-numbers-explained.html` →
  `fr/articles/e-numbers-explained.html`.
- **`<html lang>` and `dir`:** `lang="en"`, `lang="fr"`, `lang="ar" dir="rtl"`.
- **hreflang:** every page's `<head>` lists all three versions plus `x-default` → English:
  `<link rel="alternate" hreflang="fr" href="…/fr/…">`. Canonical points to the page's own language.
  `og:locale` is `en_US`, `fr_FR`, `ar_AR`.
- **Sitemap:** one sitemap per site, every URL in all three languages, each `<url>` carrying
  `xhtml:link rel="alternate"` entries for its two twins and `x-default`.
- **Switcher:** static HTML (works without JavaScript) in the header next to the ☰ menu:
  `EN · FR · عربي`. Each label is in its own language with `lang`/`hreflang` attributes; the current
  one is marked `aria-current="true"` and not a link. On narrow screens it stays visible (it is short).
  It links to the same page's twin, so a reader on the French eggs page lands on the Arabic eggs page.
- **Right to left:** CSS switches physical `left/right` to logical properties (`margin-inline-start`,
  `inset-inline-end`, `text-align: start`) so one stylesheet serves both directions. Directional arrows
  in text (`→`, `›`) are written per language (`←`, `‹` in Arabic). The side column, menu panel and
  breadcrumbs mirror automatically. Numbers, temperatures, E-codes and barcodes stay left-to-right
  inside Arabic text (wrapped in `<bdi>`/`dir="ltr"` where a run mixes digits and units).
- **Arabic font:** Noto Naskh Arabic (SIL Open Font License), self-hosted as woff2 in each site's static
  folder, used only on `lang="ar"` pages, with a system fallback (`"Noto Naskh Arabic", "Segoe UI",
  Tahoma, "Geeza Pro", sans-serif`). Slightly larger size and line height for Arabic. Downloading the
  font file needs the owner's OK at implementation time; if declined, the system fallback is used.
- **Digits:** Western digits (0–9) in all three languages, as is normal in Morocco. This also lets a
  check compare numbers between languages exactly.
- **Temperatures:** English shows `40°F (4°C)` as today. French and Arabic show `4 °C (40 °F)`.
- **Units and terms:** French uses `jours, semaines, mois, ans, heures`; Arabic uses correct dual and
  plural forms (يوم / يومان / أيام / يومًا) through a small plural helper, not string concatenation.
- **Sources:** source links, publishers and titles stay as published (mostly English), with a short
  note per language that the sources are in English. Source URLs never change.
- **Names that stay as they are:** brand and product names (Oreo, Nutella…), E-numbers, the character
  names Mina, Tariq and Uncle Kamil, the site names *Keep or Toss* and *Supermarket Decoder*
  (a translated tagline may sit beside them).
- **Number guard (both sites):** a test extracts every number, `{temp:N}` marker, E-code, `%` value and
  URL from each English string and its French and Arabic counterpart and fails if the sets differ.
  This is the main defence against the anti-goal above.
- **Completeness guard:** the build or check fails if any page, field, UI string or list item exists in
  English but not in French or Arabic (or has a different number of list items).
- **Translation standard:** written in natural, plain French and plain MSA at the same reading level as
  the English (short sentences, everyday words). Safety verbs keep their strength
  (toss = jetez / تخلّص منه; keep = gardez / احتفظ به). A glossary of fixed terms is kept per site
  (`i18n/glossary.md`) and used everywhere so the same English term is always translated the same way.
  Health and regulatory wording (Southampton warning, EFSA/FDA statements, allergen wording) is
  translated closely, keeping every qualifier ("may", "in the EU and UK", "best quality").

## Keep or Toss

### Storage of translations

- `data/i18n/fr.py` and `data/i18n/ar.py` (split into several files per category if large), each a dict
  keyed by slug holding **only text fields**: food `name`, `question`, `why`, `spoiled_signs`,
  `how_to_store`, `common_mistake`, `freezing`, `description`, span `note`s; left-out `question`,
  `verdict_line`, `risk`, `next_time`, `description`; guide `title`, `description`, `answer`, section
  `heading`/`paragraphs`/`bullets`; quick-food `name` and `source` note.
- Storage spans (`min`, `max`, `unit`), places, categories, related slugs and source URLs are **never**
  in translation files. The renderer reads them from the English data. A translated page cannot show a
  different time because it never had its own copy of the time.
- UI strings (header, menu, buttons, headings like "How can you tell it has gone bad?", verdict words,
  footer, disclaimer, about/sources/privacy/404 text, category names, place names, units) live in
  `kot/i18n.py` as one catalog per language.

### Generator changes

- `kot/build.py` loops over `("en", "fr", "ar")`. English output is unchanged (byte-for-byte except
  the new hreflang/switcher markup). FR/AR output goes under `fr/` and `ar/`.
- `kot/render.py`: `shell()` takes `lang`; writes `lang`/`dir`, hreflang, switcher, Arabic font link;
  every hard-coded English string goes through the catalog; `span_text` and `fmt_temp` become
  language-aware.
- `checker.json` gets per-language copies (`checker.json`, `fr/checker.json`, `ar/checker.json`) with
  translated names and notes but identical numbers. `static/checker.js` reads its UI strings from a
  small `data-i18n` JSON block on the page, so one script serves all three languages.
- The home search (`_search_items`) is generated per language; its matching handles accents and
  Arabic letters (Unicode-aware word splits; accent-insensitive in French so "oeuf" finds "œuf").
- Quality gates in `kot/quality.py` (reading grade, similarity, minimum words) stay English-only;
  translated pages are covered by the completeness and number guards instead.
- `scripts/check_site.py` additionally checks: every page has its two twins, hreflang links point to
  pages that exist, `lang`/`dir` are right, and pages under `fr/`/`ar/` link to pages in their own
  language (static assets excepted).

## Supermarket Decoder

### Hand-written pages

Home, about, sources, 404, free-resources (5), articles (4), story (3), stories (1): translated twins
written by hand as `fr/<same path>` and `ar/<same path>`. Inner links point to twins in the same
language; assets point back to the shared `assets/`. Gumroad buttons keep their URLs, add the
language to `utm_content` (for example `hero-fr`), and a line next to them says the guide is in English.

### Generated pages

- `scripts/additives_data.py` → text fields translated in `scripts/i18n/additives_fr.py` /
  `additives_ar.py` keyed by slug; codes, numbers and sources are read from the English data only.
  `make_additives.py pages` writes all three languages.
- `scripts/fvk_data.py` → same pattern (`scripts/i18n/fvk_fr.py`, `fvk_ar.py`); `make_fvk.py` writes
  all three and adds all of them to the sitemap.

### Decoder tool

`decoder/index.html` currently mixes logic and English text in one 115 KB page. The script moves to
`assets/decoder.js` (logic, unchanged behaviour) and the text to `assets/decoder-text.en.js`,
`.fr.js`, `.ar.js` (function names, E-number explanations, dictionary explanations, allergen labels,
messages, samples). Matching patterns (regexes) stay in `decoder.js` and keep working on French names
as they do today. Each language's `decoder/index.html` is a small page loading the shared logic plus
its text file. The English decoder must behave exactly as now (checked by running the same samples
before and after).

### Shared script and menu

- New `scripts/i18n_pages.py`: inserts/updates, between marker comments, the hreflang block and the
  switcher on every page in all three languages, and rewrites the sitemap with alternates. Idempotent;
  `check_site.py` fails if running it would change anything (same pattern as the search index today).
- `scripts/make_search_index.py` writes `assets/search-index.json`, `search-index.fr.json`,
  `search-index.ar.json`; `assets/nav.js` picks the file and its menu group labels from `<html lang>`
  and uses Unicode-aware matching.
- `assets/site.css` and `assets/nav.css` switch to logical properties for RTL; Arabic font rules apply
  under `:lang(ar)`.
- `check_site.py` gains the same twin, hreflang, `lang`/`dir` and same-language-link checks.

## Order of work

1. Keep or Toss: i18n plumbing, switcher, RTL, guards (tested with a couple of translated foods).
2. Keep or Toss: all translations, FR then AR; build, checks, browser preview.
3. Supermarket Decoder: plumbing (helper script, switcher, RTL, decoder split, generators).
4. Supermarket Decoder: all translations; checks, browser preview.
5. Owner review of each site in the browser, then a push only after the owner says yes.

Each site is shown to the owner when it is done; Keep or Toss can go live before Supermarket Decoder
is finished.

## Left to the builder

- Exact file split of translation data (one file per language or per category).
- Exact CSS changes for mirroring, as long as English renders the same.
- Switcher styling, within the site's existing look.
- Glossary contents, following the standard above.

## Calls made without asking (owner can overrule)

- Modern Standard Arabic, not Darija.
- English slugs in translated URLs.
- °C first on French and Arabic pages; Western digits in Arabic.
- No language auto-redirect.
- Self-hosted Noto Naskh Arabic (needs a one-time download OK), system fonts as fallback.
- Source titles stay in their original language.
- Quality reading-grade gates stay English-only.
- Pins, videos and marketing material stay English.

## Later (not this round)

- Decoder reading Arabic-script ingredient lists (common on Moroccan packaging).
- French/Arabic Pinterest pins.
- A French or Arabic edition of the paid guide.
