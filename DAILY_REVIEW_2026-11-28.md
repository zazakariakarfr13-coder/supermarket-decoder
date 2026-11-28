# Supermarket Decoder — Daily Development Review
## 2026-11-28

### Repository review
- Active repository: [supermarket-decoder](https://github.com/zazakariakarfr13-coder/supermarket-decoder).
- Requested original repository: [Zakaria](https://github.com/zazakariakarfr13-coder/Zakaria), still a redirect-only repository; its latest inspected commit remains `a8519e92`.
- Compared active `main` from `216842c1` to `ee5a07e3`: **25 commits ahead, 0 behind, 241 changed paths**. Most activity is the multilingual implementation landed on 27 November.
- Open issues: 0. Open PRs: 0 (GitHub repository-scoped searches).
- Latest inspected commit: [`ee5a07e3`](https://github.com/zazakariakarfr13-coder/supermarket-decoder/commit/ee5a07e3ef0b28107536576f566474c711d3a235) — fixes French/Arabic comic avatar CSS paths and the video poster path; validator now checks CSS `url()` and video `poster` targets.
- The comparison below is the exact machine-returned changed-path manifest for this review window.

### Product and site changes
1. **French and Arabic site versions:** home, about/sources, free resources, label articles, E-number pages, Factory vs. Kitchen, story pages and the Ingredient Decoder now have translated twins. Arabic pages set RTL and use a self-hosted Noto Naskh Arabic font under its SIL Open Font License.
2. **Decoder localization:** translated interface/results and ingredient/advisory text, language-specific search indexes, and language-aware navigation. English decoder output is guarded by a golden test.
3. **Barcode/QR scan feature:** new `assets/decoder-scan.js` handles supported UPC/EAN formats, UPC-E expansion, GS1 Digital Link/element-string extraction and check digits, then looks up a product through Open Food Facts. The source states camera frames are processed locally; the product number is sent to Open Food Facts. Privacy copy and actual network behavior should be confirmed in browser QA.
4. **Translation build/test system:** `scripts/i18n_pages.py`, twin generators, number/E-code/URL guards and new unit/browser tests help prevent missing or stale language twins.
5. **Marketing attribution:** French and Arabic Gumroad links append language-specific UTM content labels.

### Risks and opportunities
- **Translation accuracy:** regulatory language (especially FDA/U.S. Nutrition Facts, EU E-numbers and NOVA) needs a bilingual subject-matter review. The README intentionally keeps U.S. label examples and sources in English; make language/jurisdiction scope obvious.
- **Scanner privacy/reliability:** verify camera permission denial, stop-camera behavior, no image/frame upload, network request contents, supported UPC/EAN variants and empty/incorrect Open Food Facts results on real phones.
- **Accessibility:** test Arabic RTL layout, mixed-direction E-codes/URLs, focus order, scanner status announcements and video/quiz controls with keyboard and screen reader.
- **SEO:** verify canonical/hreflang reciprocity and sitemap alternates in a crawler/Search Console. Translation paths can broaden organic reach, but machine/build-generated text alone is not proof of indexing.
- **Campaign routing:** Metricool's 28 Nov “7 Supermarket Aisles” Pin still links to the homepage although `/articles/supermarket-swaps.html` exists; 1 Dec swaps Pin points to a general label article; 2 Dec ingredient challenge points to homepage although `/articles/ingredient-list-challenge.html` exists. No queue changes made.
- **Commercial:** main guide remains published at $9; Gumroad analytics for 21–28 Nov show 2 page views, 0 sales and $0 revenue. This is too small a sample for pricing conclusions. Correct the NOVA phrase “ultra-processed ingredients” and direct the free-tool CTA to `/decoder/` only after approval.
- Creator storefront also contains separate “First Screen” parent-focused products. Consider clear storefront/category separation so the food-label brand does not confuse visitors; no product was edited.
- **Deployment:** GitHub connector exposed commit/status data but not push-triggered Pages run history in this review; combined status returned no checks. Therefore deployment of `ee5a07e3` is **not independently confirmed here**. Check [GitHub Actions](https://github.com/zazakariakarfr13-coder/supermarket-decoder/actions) and [Pages](https://zazakariakarfr13-coder.github.io/supermarket-decoder/) before treating this batch as live.

### Privacy and boundaries
- Paid PDF and buyer/customer/order data remain outside the public repository.
- No buyer-level data was requested or copied.
- No social posts were published, no Metricool queue was changed, and no purchase was made.

### Changes made by this review
- No application code change was justified: the upstream commits already address the observed multilingual path issue and include regression tests. I added this dated review and linked it from the development log.

### Exact upstream changed paths (241)
```text
.gitignore
404.html
DEVELOPMENT_LOG.md
README.md
about.html
additives/e129.html
additives/e150d.html
additives/e171.html
additives/e211.html
additives/e250.html
additives/e322.html
additives/e330.html
additives/e407.html
additives/e415.html
additives/e471.html
additives/e621.html
additives/e951.html
additives/index.html
ar/about.html
ar/additives/e129.html
ar/additives/e150d.html
ar/additives/e171.html
ar/additives/e211.html
ar/additives/e250.html
ar/additives/e322.html
ar/additives/e330.html
ar/additives/e407.html
ar/additives/e415.html
ar/additives/e471.html
ar/additives/e621.html
ar/additives/e951.html
ar/additives/index.html
ar/articles/e-numbers-explained.html
ar/articles/hidden-sugars-five-names.html
ar/articles/ingredient-list-challenge.html
ar/articles/nova-food-processing-levels.html
ar/articles/read-food-labels-in-30-seconds.html
ar/articles/supermarket-swaps.html
ar/decoder/index.html
ar/factory-vs-kitchen/cheetos.html
ar/factory-vs-kitchen/coca-cola.html
ar/factory-vs-kitchen/froot-loops.html
ar/factory-vs-kitchen/gummy-bears.html
ar/factory-vs-kitchen/index.html
ar/factory-vs-kitchen/instant-ramen.html
ar/factory-vs-kitchen/ketchup.html
ar/factory-vs-kitchen/kit-kat.html
ar/factory-vs-kitchen/mms.html
ar/factory-vs-kitchen/nutella.html
ar/factory-vs-kitchen/oreos.html
ar/factory-vs-kitchen/pop-rocks.html
ar/factory-vs-kitchen/pop-tarts.html
ar/factory-vs-kitchen/pringles.html
ar/factory-vs-kitchen/ritz.html
ar/factory-vs-kitchen/twinkies.html
ar/free-resources/30-second-label-checklist.html
ar/free-resources/contains-vs-may-contain.html
ar/free-resources/food-label-glossary.html
ar/free-resources/index.html
ar/free-resources/us-nutrition-facts-label.html
ar/index.html
ar/sources.html
ar/stories/the-natural-cereal-mystery.html
ar/story/episode-02.html
ar/story/index.html
articles/e-numbers-explained.html
articles/hidden-sugars-five-names.html
articles/ingredient-list-challenge.html
articles/nova-food-processing-levels.html
articles/read-food-labels-in-30-seconds.html
articles/supermarket-swaps.html
assets/decoder-data.ar.js
assets/decoder-data.fr.js
assets/decoder-scan.js
assets/decoder-text.ar.js
assets/decoder-text.fr.js
assets/decoder.js
assets/fonts/NotoNaskhArabic-400.woff2
assets/fonts/NotoNaskhArabic-700.woff2
assets/fonts/OFL.txt
assets/i18n.css
assets/lang-ar.css
assets/nav.css
assets/nav.js
assets/search-index.ar.json
assets/search-index.fr.json
assets/site.css
decoder/index.html
docs/superpowers/plans/2026-11-27-decoder-multilingual.md
docs/superpowers/specs/2026-11-26-multilingual-design.md
factory-vs-kitchen/cheetos.html
factory-vs-kitchen/coca-cola.html
factory-vs-kitchen/froot-loops.html
factory-vs-kitchen/gummy-bears.html
factory-vs-kitchen/index.html
factory-vs-kitchen/instant-ramen.html
factory-vs-kitchen/ketchup.html
factory-vs-kitchen/kit-kat.html
factory-vs-kitchen/mms.html
factory-vs-kitchen/nutella.html
factory-vs-kitchen/oreos.html
factory-vs-kitchen/pop-rocks.html
factory-vs-kitchen/pop-tarts.html
factory-vs-kitchen/pringles.html
factory-vs-kitchen/ritz.html
factory-vs-kitchen/twinkies.html
fr/about.html
fr/additives/e129.html
fr/additives/e150d.html
fr/additives/e171.html
fr/additives/e211.html
fr/additives/e250.html
fr/additives/e322.html
fr/additives/e330.html
fr/additives/e407.html
fr/additives/e415.html
fr/additives/e471.html
fr/additives/e621.html
fr/additives/e951.html
fr/additives/index.html
fr/articles/e-numbers-explained.html
fr/articles/hidden-sugars-five-names.html
fr/articles/ingredient-list-challenge.html
fr/articles/nova-food-processing-levels.html
fr/articles/read-food-labels-in-30-seconds.html
fr/articles/supermarket-swaps.html
fr/decoder/index.html
fr/factory-vs-kitchen/cheetos.html
fr/factory-vs-kitchen/coca-cola.html
fr/factory-vs-kitchen/froot-loops.html
fr/factory-vs-kitchen/gummy-bears.html
fr/factory-vs-kitchen/index.html
fr/factory-vs-kitchen/instant-ramen.html
fr/factory-vs-kitchen/ketchup.html
fr/factory-vs-kitchen/kit-kat.html
fr/factory-vs-kitchen/mms.html
fr/factory-vs-kitchen/nutella.html
fr/factory-vs-kitchen/oreos.html
fr/factory-vs-kitchen/pop-rocks.html
fr/factory-vs-kitchen/pop-tarts.html
fr/factory-vs-kitchen/pringles.html
fr/factory-vs-kitchen/ritz.html
fr/factory-vs-kitchen/twinkies.html
fr/free-resources/30-second-label-checklist.html
fr/free-resources/contains-vs-may-contain.html
fr/free-resources/food-label-glossary.html
fr/free-resources/index.html
fr/free-resources/us-nutrition-facts-label.html
fr/index.html
fr/sources.html
fr/stories/the-natural-cereal-mystery.html
fr/story/episode-02.html
fr/story/index.html
free-resources/30-second-label-checklist.html
free-resources/contains-vs-may-contain.html
free-resources/food-label-glossary.html
free-resources/index.html
free-resources/us-nutrition-facts-label.html
index.html
scripts/build_decoder_text.py
scripts/check_site.py
scripts/decoder_strings.js
scripts/i18n/__init__.py
scripts/i18n/ar/__init__.py
scripts/i18n/ar/additives.py
scripts/i18n/ar/decoder_data_0_names.json
scripts/i18n/ar/decoder_data_1.json
scripts/i18n/ar/decoder_data_2.json
scripts/i18n/ar/decoder_data_3.json
scripts/i18n/ar/e_name_hashes.txt
scripts/i18n/ar/fvk.py
scripts/i18n/ar/fvk_more.py
scripts/i18n/ar/pages/__init__.py
scripts/i18n/ar/pages/about.py
scripts/i18n/ar/pages/art_30s.py
scripts/i18n/ar/pages/art_challenge.py
scripts/i18n/ar/pages/art_e_numbers.py
scripts/i18n/ar/pages/art_nova.py
scripts/i18n/ar/pages/art_sugars.py
scripts/i18n/ar/pages/art_swaps.py
scripts/i18n/ar/pages/decoder.py
scripts/i18n/ar/pages/home.py
scripts/i18n/ar/pages/res_allergens.py
scripts/i18n/ar/pages/res_checklist.py
scripts/i18n/ar/pages/res_glossary.py
scripts/i18n/ar/pages/res_index.py
scripts/i18n/ar/pages/res_nutrition.py
scripts/i18n/ar/pages/sources.py
scripts/i18n/ar/pages/story_cereal.py
scripts/i18n/ar/pages/story_ep1.py
scripts/i18n/ar/pages/story_ep2.py
scripts/i18n/fr/__init__.py
scripts/i18n/fr/additives.py
scripts/i18n/fr/decoder_data_1.json
scripts/i18n/fr/decoder_data_2.json
scripts/i18n/fr/decoder_data_3.json
scripts/i18n/fr/decoder_data_4.json
scripts/i18n/fr/decoder_data_5.json
scripts/i18n/fr/fvk.py
scripts/i18n/fr/pages/__init__.py
scripts/i18n/fr/pages/about.py
scripts/i18n/fr/pages/art_30s.py
scripts/i18n/fr/pages/art_challenge.py
scripts/i18n/fr/pages/art_e_numbers.py
scripts/i18n/fr/pages/art_nova.py
scripts/i18n/fr/pages/art_sugars.py
scripts/i18n/fr/pages/art_swaps.py
scripts/i18n/fr/pages/decoder.py
scripts/i18n/fr/pages/home.py
scripts/i18n/fr/pages/res_allergens.py
scripts/i18n/fr/pages/res_checklist.py
scripts/i18n/fr/pages/res_glossary.py
scripts/i18n/fr/pages/res_index.py
scripts/i18n/fr/pages/res_nutrition.py
scripts/i18n/fr/pages/sources.py
scripts/i18n/fr/pages/story_cereal.py
scripts/i18n/fr/pages/story_ep1.py
scripts/i18n/fr/pages/story_ep2.py
scripts/i18n/fvk_ui.py
scripts/i18n/guard.py
scripts/i18n_pages.py
scripts/make_additives.py
scripts/make_fvk.py
scripts/make_search_index.py
scripts/make_twins.py
scripts/segments.py
sitemap.xml
sources.html
stories/the-natural-cereal-mystery.html
story/episode-02.html
story/index.html
tests/__init__.py
tests/js/decoder-golden.browser.js
tests/js/nav.test.cjs
tests/test_check_site_lang.py
tests/test_guard.py
tests/test_i18n_pages.py
tests/test_make_additives_i18n.py
tests/test_make_fvk_i18n.py
tests/test_make_twins.py
tests/test_search_index.py
```

### Next priorities
1. Confirm the Pages run for the latest main commit.
2. Run full English/French/Arabic visual and link QA, especially RTL and media paths.
3. Test barcode scanning/privacy on actual devices.
4. Obtain a native/bilingual review of regulatory translations.
5. Request approval for the three scheduled Pin destination corrections and the Gumroad copy/link changes.
6. Measure language-specific outbound checkout traffic after the new pages have had time to index.
