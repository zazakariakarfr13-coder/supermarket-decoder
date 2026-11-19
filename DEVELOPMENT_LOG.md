# Supermarket Decoder — development log

This log records meaningful product, website, content, marketing and reliability changes. It is a working project record, not a sales or traffic report.

## Product definition

Supermarket Decoder is an educational product and content funnel that helps everyday shoppers interpret packaged-food labels, ingredient lists, additive codes, nutrition panels and practical product comparisons.

The system has four connected parts:

1. **Paid product:** the 53-page PDF guide sold through Gumroad. Keep the paid PDF, customer data and order exports out of this public repository.
2. **Discovery website:** GitHub Pages landing page, free resources, articles and source references.
3. **Audience growth:** Pinterest and other channels direct people to useful free content before introducing the paid guide.
4. **Measurement and iteration:** validate the site, inspect deployment health, track channel-to-site-to-checkout outcomes, and improve based on evidence.

## 2026-11-16 — baseline review

### What is working

- Repository is public and GitHub Pages deployment is configured through GitHub Actions.
- Recent Pages build and deployment runs inspected during this review completed successfully.
- The deployment workflow runs `scripts/check_site.py` before publishing.
- The homepage includes a product explanation, interactive ingredient decoder, FAQ, free resources and multiple tracked Gumroad links.
- Educational coverage includes ingredient order, hidden sugars, E-numbers, NOVA, a US Nutrition Facts label guide and a public sources page.
- SEO foundations include page titles, descriptions, canonical links, structured data, `robots.txt` and `sitemap.xml`.
- The US Pinterest plan already defines a useful 5-Pin weekly mix, destinations, alt text and a measurement routine.
- README correctly says the complete paid PDF is not part of the public repository.

### Product and growth assessment

The product foundation is coherent: free, useful education earns attention before the checkout offer. The main weakness is not a lack of content ideas; it is the absence of a consolidated, repeatable evidence loop connecting content distribution, site engagement, outbound checkout clicks and Gumroad outcomes.

Gumroad analytics are available through the connected creator account, but the inspected repository does not establish a site-side analytics event system or a consolidated dashboard. Treat checkout-side views/referrers and sales as separate evidence from Pinterest impressions and website sessions.

### Risks and follow-up opportunities

1. **Measurement:** verify that analytics is installed and that outbound Gumroad clicks can be measured without collecting unnecessary personal data. Add a lightweight event plan before adding tracking scripts.
2. **Search performance:** monitor Google Search Console indexing, queries and page impressions. A sitemap file alone does not prove that pages are indexed.
3. **US-specific content:** preserve clear separation between US FDA label rules and EU/Moroccan requirements. Keep official source links close to claims.
4. **Content maintenance:** re-check regulatory and scientific references when revising pages; distinguish legal rules by country and avoid turning processing indicators into health verdicts.
5. **Accessibility and quality:** continue automated local-link checks and add focused checks for page metadata, missing image alternatives, and broken fragment links where useful.
6. **Marketing operations:** track which Pins actually generate outbound visits and Gumroad product-page traffic. Do not infer sales from impressions or saves.
7. **Offer accuracy:** check time-limited discounts and price copy against the live Gumroad offer before changing them.

### Baseline activity observed

The most recent inspected commits on 16 November 2026 refined the US Nutrition Facts guide and its internal homepage links. The latest inspected GitHub Pages deployments were successful. This is repository/deployment evidence only; it is not proof of traffic, sales or customer satisfaction.

### Operating rules for future reviews

- Inspect commits, changed files, open issues/PRs and recent deployment runs.
- Read enough surrounding code/content to understand the product impact before changing anything.
- Make small, reversible, evidence-backed improvements; avoid broad redesigns without a clear reason.
- Keep credentials, customer records, order exports and the paid guide private.
- Never publish Pins, posts, emails or other external marketing content without explicit approval.
- Record the review date, findings, changes, validation result and next priorities below.
- If no meaningful change occurred, say so rather than inventing progress.

---

## Daily review entries

### 2026-11-16

- **Repository:** `zazakariakarfr13-coder/Zakaria`, default branch `main`.
- **Review:** inspected repository structure, README, homepage, key resource page, sources page, marketing plans, validation script and Pages workflow.
- **Status:** earlier Pages deploys were successful. Several intermediate deployment runs triggered during this batch of rapid commits were cancelled by newer pushes under the existing `cancel-in-progress` rule. The latest run for commit `491780c7da7aa8166b08f1a8a7c86dd7b46fec27` passed site validation and was still uploading the Pages artifact at the time of final inspection.
- **New changes:** added this development log, updated the README, strengthened the site validator, and added a scheduled GitHub Actions quality-check workflow.
- **Validation:** local link/asset/fragment/sitemap validation passed on the latest inspected deployment run. The Pages artifact upload was still running, so the final public deployment result is not yet confirmed. The scheduled quality workflow is configured for daily 08:00 Africa/Casablanca.
- **Priority next:** confirm the latest Pages deployment completes successfully; verify analytics and checkout-click measurement; then audit SEO/indexing and landing-page accessibility.


## Daily review entries

### 2026-11-17

- **Repository baseline:** compared `main` from `d407f101` to `f41e416f`: 51 commits ahead, with 21 net changed paths in the comparison. The latest inspected commit applies a retro screen-print comic art direction.
- **Educational content changes:** three U.S.-focused drafts were added during the work sequence (ingredient-list reading, Nutrition Facts comparison, and Contains vs May Contain), then removed in commit `e7b9293` while gallery assets were added. They are absent from the current site and current sitemap; the remaining local-link validation reports no broken references. I did not restore them because the removal may have been intentional.
- **Comic/product work:** the home page links to `/story/`, and the sitemap includes both `/story/` and `/stories/the-natural-cereal-mystery.html`. The new reader contains six illustrated scenes, a keyboard-operable button quiz with a live feedback region, an archive of scene links, and a Gumroad CTA. The separate cereal story uses a different character set.
- **Creative alignment risk:** `/story/` is still titled “The Snack Aisle Plot Twist” and features Leo and Rami; the separate cereal story features Detective Dee and a cereal-box monster. This does not match the recent requested reset away from Leo/Rami and the earlier small plot twist toward a longer, character-led supermarket dialogue. I did not replace the story or cast in this maintenance pass because that is a consequential creative rewrite; the direction should be carried through as a dedicated story revision rather than another round of decorative CSS changes.
- **Accessibility fix:** corrected the scene-image accessible labels for scenes 03–06 so the descriptions match the sugar jars, Nutrition Facts panel, additive identifiers, and closing snack scene.
- **Asset integrity:** `assets/label-detective-cases.jpg` is 15,000 bytes but does not begin with a valid JPEG signature. Repository code search found no references to it, so it was left untouched. The site validator now warns when a raster file's extension does not match its file signature; this is a warning, not a deployment blocker. The five `gallery/*.jpg` preview images have valid JPEG signatures and appear to be prepared assets rather than embedded site images.
- **SEO/social preview:** `/story/` has a canonical URL and is in the sitemap, but its `og:image` still points to a Canva design URL rather than a verified direct public raster image. The standalone cereal story has no `og:image`. A dedicated, verified share image should be prepared before promoting either story broadly.
- **Marketing/measurement:** the Pinterest plan still describes a five-Pin weekly mix and separate impression, save, Pin-click, outbound-click and Gumroad conversion checks. Gumroad analytics were reviewed separately; detailed performance figures are not written to this public repository. Site-side analytics were not verified.
- **Issues and pull requests:** no open repository issues or pull requests were found.
- **Deployment:** the latest inspected Pages build/deployment for `0584fbd3` completed successfully. The corrected validator passed and reported three non-blocking warnings: the 404 page lacked a meta description, the legacy redirect lacked an H1, and the unused `assets/label-detective-cases.jpg` did not have a valid JPEG signature. The five gallery JPEGs passed after the signature matcher was corrected. The daily quality workflow file is present, but no run of that workflow appeared in the inspected Actions history yet.
- **Changes in this review:** updated the comic scene accessible labels and extended `scripts/check_site.py` with raster image-signature warnings. No social posts were published, no purchases were made, and the paid PDF/customer data remain outside the public repository.
- **Next priorities:** finish the approved creative reset in one focused story revision; decide whether the three removed U.S. guides should be restored; replace the unverified social preview image with a dedicated public raster; review the incomplete U.S. Nutrition Facts mock label in the standalone cereal story; verify analytics and Gumroad conversion tracking; decide whether the unreferenced malformed JPEG should be replaced or removed.


### 2026-11-17 — follow-up checks

- **Gumroad delivery check:** the Supermarket Decoder product remains published at $9. The listing has six cover images and one attached PDF delivery file (about 3.97 MB). The paid PDF remains in Gumroad delivery and is not in the public repository. No buyer-level or customer records were accessed.
- **Gumroad measurement:** the connected analytics were reviewed for the recent 7-day and 30-day periods. Detailed page-view and referrer counts are kept out of this public repository; see the daily review summary in the associated ChatGPT conversation.
- **Low-risk SEO/structure fixes:** added a meta description to `404.html`; marked the legacy `story/cases.html` instant-refresh page `noindex,follow` and gave it a clear H1 so it is treated as a redirect helper rather than a separate search result; updated this README to document the story and gallery directories and the raster-signature check.
- **Remaining warning:** `assets/label-detective-cases.jpg` is still an unreferenced malformed raster asset. It was not deleted or replaced because its intended source is unclear.
- **Next review:** confirm the first GitHub scheduled quality run; prioritise the coordinated comic story reset and corrected Pinterest destinations before promoting more cases; prepare a verified direct share image.

- **Promotion timing:** the homepage currently shows the `LAUNCH40` 40%-off message through 19 November 2026 at 23:59 Europe/Paris; the site-side timestamp matches that cutoff. The available read-only Gumroad tools do not expose discount-code lookup, so the code's live validity could not be independently confirmed. Recheck the code in Gumroad before extending or removing the message.
- **Public-repository check:** no PDF files are present in the repository tree. The paid PDF remains attached only to the Gumroad product delivery.

- **Nutrition-label accuracy:** clarified that both comic mock labels are simplified fictional examples, added Added Sugars grams and %DV to the examples, and linked directly to FDA guidance. For most U.S. packaged foods, Added Sugars is listed in grams and %DV; single-ingredient sugars and syrups have special labeling rules.

### 2026-11-17 — channel and schedule review

- **Metricool/Pinterest:** reviewed the connected Pinterest brand and its scheduled queue. There are 14 posts in the 17–30 November window: 3 already published and 11 pending; all pending posts are set to auto-publish. No posts were created, edited, paused or published during this review.
- **Scheduled-link alignment:** the 17 November 18:00 “Sugar Has a Whole Alias List” Pin links to `story/index.html`, but that scene lists honey, cane sugar, glucose syrup and dextrose—not every item named in the Pin copy (invert sugar, fruit-juice concentrate and maltodextrin). The 18 November 04:00 “Contains vs May Contain” Pin also links to `story/index.html`, which has no allergen case. The 18 November 07:00 “Two Packets” Pin points to the same story; the story gives a general comparison takeaway but does not show the side-by-side packet comparison described by the Pin image alt text. These pending posts should be reviewed before their automatic publication; no external schedule changes were made.
- **Pinterest performance:** Metricool analytics were checked for 10–17 November. Detailed account-performance figures are kept out of this public repository. Gumroad attribution and Metricool outbound-click totals do not line up exactly, likely because their reporting scopes differ; validate UTM/referrer definitions before using either as a single source of truth.
- **Site analytics:** repository search found UTM-tagged Gumroad links but no Google Analytics/gtag or Pinterest tag. Site-side sessions and outbound-click events are therefore not independently measured in the code.
- **Creative alignment remains:** the currently promoted `/story/` page is still the six-scene Leo/Rami “Snack Aisle Plot Twist” and is not the requested longer, reset supermarket dialogue. The separate cereal story uses Detective Dee. The scheduled Pins continue to promote the older story until the story and scheduled links are revised together.
- **Content accuracy:** both fictional Nutrition Facts examples now identify themselves as simplified and show Added Sugars grams plus %DV, with direct FDA guidance links. See the FDA's [Added Sugars explanation](https://www.fda.gov/food/nutrition-facts-label/added-sugars-nutrition-facts-label).
- **Next priority:** approve one coordinated story-and-Pinterest revision before changing scheduled posts; do not send visitors to topics the landing page does not actually cover.

- **GitHub Actions schedule reliability:** no execution of `.github/workflows/daily-site-check.yml` appeared in the Actions history by 17 November 08:11 UTC, despite the workflow file being present. Moved its daily cron off the top of the hour and set an explicit `Africa/Casablanca` timezone at 08:17 local, so the schedule follows Morocco time changes. It remains manually runnable through `workflow_dispatch`; confirm the first scheduled run in the next review. The ChatGPT daily repository review itself is running separately.

- **Final verification for this run:** Pages deployment for `16394c65` completed successfully. The site validator passed with only the single known warning for the unreferenced malformed JPEG. The daily quality workflow's next scheduled slot is 08:17 Africa/Casablanca on 18 November; the separate ChatGPT daily review is active.

- **Pages deployment incident:** the custom Pages workflow for `badfc2fa` failed at `deploy-pages` because GitHub reported another deployment was already in progress. The parallel GitHub Pages dynamic deployment for the same commit completed successfully, so the site artifact was deployed despite the custom workflow failure. The failed run also emitted Node.js 20 deprecation warnings for the older Pages actions.
- **Actions maintenance:** upgraded the Pages and daily-quality workflows to Node 24-compatible major releases (`checkout@v7`, `setup-python@v7`, `configure-pages@v6`, `upload-pages-artifact@v5`, `deploy-pages@v5`). Set Pages deployment concurrency to queue rather than cancel an in-flight deployment. The push run for `2a01eab3` verified the updated actions successfully; the Node.js 20 deprecation warnings are gone, although `deploy-pages@v5` still emits a separate `punycode` deprecation warning.

- **Actions verification result:** Pages deployment run `44045338043` for `2a01eab3` completed successfully with the Node 24-compatible action versions and `cancel-in-progress: false`. The validator passed; the only site warning remains the unused malformed JPEG. The first scheduled quality workflow run (`44045049625`) also completed successfully on the previous workflow revision; the next scheduled run will exercise the timezone-aware schedule and upgraded actions.

### 2026-11-18 — launch offer extended

- **Promotion:** `LAUNCH40` (40% off, Supermarket Decoder only) extended in Gumroad to 3 December 2026, 23:59 Europe/Paris (22:59 UTC); Gumroad confirms the code is active. Homepage message reworded from "Launch week" to "Launch offer" and its client-side cutoff moved to the same time.

### 2026-11-18 — Episode 02, content accuracy and channel review

- **Repository activity:** reviewed 10 new commits from 17 November 13:02 UTC through 18 November 01:02 UTC. The work added the Mina, Tariq and Uncle Kamil cast; rebuilt Episode 01 as an eight-scene interactive comic; added the allergen explainer and scene deep links; created 11 Pinterest artwork files plus `scripts/make_pins.py`; moved free resources and the comic ahead of the paid-guide pitch on the homepage; extended the `LAUNCH40` offer message to 3 December; and added Episode 02, “Liquid Alibis”. No open GitHub issues or pull requests were found.
- **Pages and quality:** the latest Pages workflow (run 115, commit `8eee0d5`) completed successfully. The site validator passed all 17 HTML pages, local links/assets/fragments, sitemap targets and available metadata. The previously malformed, unreferenced `assets/label-detective-cases.jpg` was removed; the current repository tree contains no such file and the validator emitted no site warnings. A non-blocking Node `punycode` deprecation warning remains in the deployment tooling.
- **Content accuracy updates in this review:** clarified that the first three ingredients are a starting point rather than necessarily most of a product; removed the claim that one unfamiliar ingredient alone proves a food is ultra-processed; and made the NOVA wording more careful. Episode 02 now distinguishes stand-alone added caffeine from caffeine supplied by another ingredient, avoids implying that every zero-sugar drink uses a sweetener, and links to FDA guidance. FDA guidance supports the distinction: stand-alone added caffeine must be listed, while caffeine amounts are often supplied voluntarily; the FDA cites about 400 mg/day as an amount not generally associated with negative effects for most adults.
- **Pinterest destination alignment:** expanded the existing `articles/hidden-sugars-five-names.html` route to cover the eight sweetening ingredients named in the 29 November Pin. The legacy URL was retained so the scheduled destination continues to resolve; maltodextrin is explained separately as a starch-derived carbohydrate rather than another name for sugar.
- **Gumroad product:** the product remains published at $9. Gumroad reports 55 product-page views and zero sales for 11–18 November (Gumroad reporting timezone: Pacific Time): Pinterest 18, direct 17, the website 15, Gumroad self-referrals 4 and Gumroad recommendations 1. The product delivery contains one PDF file of 3,970,813 bytes. This is still a small sample; no price change is recommended.
- **Launch offer:** the homepage displays the 40% `LAUNCH40` offer through 3 December 2026. The previous repository note records Gumroad confirmation that the code is active; the connected read-only tools do not expose a current discount-code lookup, so verify it at checkout before relying on it in new promotion.
- **Metricool/Pinterest queue:** the 18–30 November view contains 19 entries: 3 published and 16 pending. Every pending post is set to auto-publish. No scheduled posts were edited, paused or published during this review. The 18 November allergen Pin now points to its matching explainer; the sugar-names Pin's existing destination now covers all eight named ingredients. Remaining alignment risks: the 19 November kids-snacks Pin, 23 November four-claims Pin and 28 November seven-aisles Pin point to the homepage rather than a dedicated explainer; the 18 November “Two Packets” Pin points to a snack-choice scene but not a side-by-side nutrition-label example. Do not alter the external queue without approval.
- **Analytics caveat:** Metricool's daily Pinterest export had gaps in reach/click/save fields for 16–17 November. Treat the follower count (5 to 6) as directional only and do not use the incomplete daily series as a trend baseline.
- **Privacy and delivery:** the public repository tree contains 63 paths and no PDF files or obvious customer/order/credential-named files. Gumroad still holds the single paid PDF delivery file. No buyer records were accessed, no customer data was copied, and no external purchases or social publications were made.
- **Next priorities:** create or approve dedicated free destinations for the three remaining Pin topics; consider a share-card image for Episode 02; check the discount code directly in Gumroad; and monitor whether the free-first homepage produces more qualified visits before changing the price or moving the guide CTA.
- **Scheduled quality check:** the timezone-aware daily GitHub quality workflow is configured for 08:17 Africa/Casablanca. Its 18 November run had not yet occurred at the time of this review.

### 2026-11-19 — repository migration, Ingredient Decoder and additive-reference review

- **Repository layout:** `zazakariakarfr13-coder/Zakaria` is now a four-file redirect shell. Its latest commit (`a8519e92`, 18 November 15:19 UTC) redirects the former `/Zakaria/` path and nested paths to `/supermarket-decoder/`, preserving query strings and fragments. The active source repository is now `zazakariakarfr13-coder/supermarket-decoder`; no development changes were made to the redirect-only repository.
- **New development since the previous review:** 12 commits on 18 November added the Ingredient Decoder tool, recognition for 600+ ingredient names/aliases including typos and French labels, five decoder Pins, 12 additive reference pages plus an index, SEO/share metadata and internal links, Episode 02/character artwork, and Complete Kit/pocket-reference cross-sells. The latest site commit before this review was `5e36c428` at 23:57 UTC. The active repository contains 101 paths.
- **Product and offer:** Gumroad confirms the main 53-page PDF guide is published at $9. The Complete Kit is published at $13 and describes $18 of combined products (guide, 123-code A5 E-number reference and shelf printables); the standalone pocket reference is $5. For 12–19 November (Gumroad reporting timezone: Pacific), the main guide had 55 views, 0 sales and $0 revenue. Product-specific referrers: GitHub Pages 21, Pinterest 19, direct 10, Gumroad self-referrals 4 and Gumroad 1. The Complete Kit had 3 views, the pocket reference 2, and the shelf printables 0; no sales were recorded in the returned product report. This remains a small sample; do not change price on this evidence alone.
- **Pinterest/Metricool:** the 19 November–3 December queue contains 24 entries: 22 pending, 1 published and 1 error. The 19 November 02:30 Europe/Paris Pin “What's E471 Doing in My Bread? Additives Explained” failed with Metricool's HTTP 400 “invalid URL” message. Its destination is the decoder page with a long prefilled `#list=` fragment; the exact validation cause is not confirmed. Do not edit or republish the external queue without approval. A separate 08:30 Pin is published; the 12:30 Ingredient Decoder Pin and later entries remain pending at review time.
- **Content-accuracy correction:** the generic note on all 12 additive pages and the additive index said an E-number meant the substance had been assessed and approved in Europe. That wording is too broad and directly conflicts with the E171 page: the European Commission withdrew E171's food-use authorisation from 7 August 2022, while Great Britain still lists it as authorised and the US FDA currently allows it under specified conditions. The generic wording has been corrected in both generator templates, all 12 generated pages and the index to explain that an E-number is an identifier and does not establish current authorisation in every country or food category. Official references: European Commission <https://food.ec.europa.eu/food-safety/food-improvement-agents/additives/re-evaluation_en>, Great Britain register <https://data.food.gov.uk/regulated-products/food_authorisations/e-171>, and US FDA <https://www.fda.gov/industry/color-additives/titanium-dioxide-color-additive-foods>.
- **E171 jurisdiction precision:** corrected the page and source data to distinguish the EU/Northern Ireland prohibition from Great Britain authorisation and US FDA conditional permission; added official EU, UK Committee on Toxicity, Great Britain register and FDA links to the sources page.
- **SEO/accessibility and privacy:** the latest SEO work adds canonical and Open Graph/Twitter metadata and share cards; the additive pages include FAQ structured data. The Ingredient Decoder's page code contains no `fetch`, XMLHttpRequest, sendBeacon, WebSocket or form-submission path; pasted text appears to be processed in-browser, with the share action copying the current URL. The repository tree contains 101 paths, no PDF files and no paths with obvious customer/order/credential/private-data names. The paid PDF and customer data remain outside the public repository.
- **Issues and pull requests:** no open issues or pull requests were returned for the active repository or the redirect-only repository.
- **Deployment:** Pages deployment run #128 for `5e36c428` completed successfully. The latest daily site-quality run (#3, 18 November) also passed. The next scheduled quality check for 19 November had not yet run at 08:02 Africa/Casablanca; the workflow is scheduled for 08:17 local time. The direct browser check of the GitHub Pages host was unavailable in this review environment, so live delivery is verified through GitHub Actions rather than a separate browser render.
- **Next priorities:** create a short, stable bread-additives example URL for the failed E471 Pin and obtain approval before changing its external schedule; build dedicated free destinations for the kids-snacks, four-front-claims and seven-aisles Pins; complete a manual keyboard/contrast/screen-reader audit; continue measuring product-specific referrers and sales; and verify the `LAUNCH40` code in Gumroad before using it in new promotions. No social posts were published, no scheduled posts were changed, and no external purchases were made.
