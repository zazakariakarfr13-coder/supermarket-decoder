# Supermarket Decoder

**The front sells. The back tells.**

A public educational website and marketing hub by Zakaria Froud. It helps everyday shoppers understand packaged-food labels, ingredient lists, additive codes, nutrition panels and practical supermarket swaps.

**Live website:** https://zazakariakarfr13-coder.github.io/supermarket-decoder/

## What is in this repository

- `index.html` — product landing page and interactive ingredient-decoder preview.
- `decoder/` — free browser-based ingredient decoder with barcode/QR scanning and Open Food Facts product lookups.
- `about.html` — author background, purpose and editorial principles.
- `sources.html` — linked public-health, regulatory and scientific references.
- `free-resources/` — checklist, glossary and an index of free learning resources.
- `articles/` — short explainers on food labels, hidden sugars, E-numbers and NOVA.
- `story/` and `stories/` — illustrated food-label stories and case-study pages; the main reader includes a short interactive quiz.
- `gallery/` — prepared product-preview images for the Gumroad listing.
- `assets/cast/` — character portraits (Mina, Tariq, Uncle Kamil) for *The Cart Chronicles* comic.
- `marketing/` — Pinterest, LinkedIn, Reddit and content-planning material.
- `assets/site.css` — shared styling for educational pages.
- `scripts/check_site.py` — dependency-free local link, fragment, sitemap, metadata and raster-image-signature validation.
- `DEVELOPMENT_LOG.md` — product definition, dated development reviews and next priorities.
- `favicon.svg` and `404.html` — site icon and custom not-found page.
- `robots.txt` and `sitemap.xml` — search-engine discovery files.
- `.github/workflows/` — automatic GitHub Pages deployment and scheduled site-quality checks.

## Paid product protection

The complete 53-page paid PDF is **not included** in this public repository. Do not upload the paid PDF, customer information, order exports, credentials, or private Gumroad files here.

The landing page checkout buttons link directly to the published Gumroad product. Each button has a distinct UTM content label so Gumroad analytics can distinguish the hero, guide-details, final-section and sticky-bar links.

**Product page:** https://zakarfr.gumroad.com/l/supermarket-decoder

## Deployment and quality checks

GitHub Pages is deployed through **GitHub Actions**. Keep the Pages source set to **GitHub Actions** in repository Settings → Pages. The deployment workflow runs:

```bash
python scripts/check_site.py
```

A successful workflow run confirms that GitHub accepted and deployed the static-site artifact. The separate daily quality workflow checks site structure and links; it does not claim to measure traffic, search ranking or sales.

## Marketing flow

Free checklist or explainer → relevant social/community post → free-resource library or landing page → Gumroad product page.

Use the free pages to earn attention and demonstrate the teaching style. Avoid repetitive link-only comments; follow each community's self-promotion rules and share a free resource only when it answers the discussion.

## Accuracy and scope

Food-label rules differ by country and can change. The EU sources on the website explain EU requirements only; they are not a substitute for current Moroccan, UK, US or other national rules. NOVA is a processing classification, not a complete nutritional or medical score. The Ingredient Decoder's NOVA output is a screening estimate based on ingredient names, not a formal classification; a single clue does not prove a food belongs to group 4. Ingredient signals and additive codes should be read in context, not treated as proof that a food is harmful.

The site is educational and does not provide medical, dietetic or personalised nutrition advice.

The barcode scanner processes camera previews and selected photos on the device; it does not upload them. A lookup sends the product barcode to Open Food Facts, which may receive standard connection metadata such as the requester's IP address; an optional product thumbnail may also load from Open Food Facts. The lookup request omits cookies and the HTTP referrer. Browsers without native barcode detection may download the ZXing library from jsDelivr. Product records are community-contributed and should be checked against the packaging. The decoder supports compact demo links such as `decoder/#sample=bar`; custom `#list=` links still place ingredient text in the URL fragment, visible to anyone who receives the link.

## Ownership

© 2026 Zakaria Froud. All rights reserved. No open-source licence is granted for original educational copy or design assets unless explicitly stated in a separate licence.
