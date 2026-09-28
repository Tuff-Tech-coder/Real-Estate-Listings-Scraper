# Portfolio materials

## Project title

**Habitat — Real Estate Listings Scraper and Property Data Explorer**

## Short description

A Python extraction pipeline with a local property dashboard. It handles rendered listing cards, normalizes prices and property details, removes duplicate records, and produces formatted Excel workbooks. The interface supports price/bedroom/area filters, sorting, and side-by-side comparison. A reproducible local demo exercises the parser, and an additional Chromium test verifies JavaScript-rendered content.

## LinkedIn post draft

Project spotlight: Habitat, a real estate listing extraction and exploration project built with Python.

The goal was to make the output useful and the behavior easy to inspect. The pipeline extracts property details, handles missing fields, checks numeric filters, removes repeated listings, and exports prices and room counts as actual Excel numbers.

The local dashboard adds search, property filters, sorting, comparison of up to three homes, and page-by-page processing activity.

One useful engineering detail: the demonstration can insert property cards asynchronously with JavaScript and use Playwright to wait for and parse the rendered content. A browser integration test checks those records against the ordinary HTML-fixture results.

The reviewed build passes 82 tests, including that Chromium check. The screenshots use fictional properties and labeled schematic illustrations; they do not represent live market data.

Stack: Python, Playwright, BeautifulSoup, pandas, openpyxl, and vanilla JavaScript.

#Python #DataEngineering #SoftwareDevelopment #Portfolio

## Resume bullet

Developed a Python property-data pipeline with dynamic-page extraction, defensive parsing, pagination safeguards, deduplication, and typed Excel exports; added a local filtering/comparison dashboard and validated the project with 82 automated tests, including a real Chromium fixture test.

## Screenshot captions

1. **Property overview** — Explore 25 synthetic properties, with asking-price and floor-area metrics calculated from the parsed records.
2. **Filtered table** — A $600,000 budget and three-bedroom minimum narrow the collection to 10 properties, sorted by asking price from high to low.
3. **Property comparison** — Compare three selected homes using price, room counts, floor area, collection date, and asking price per square foot.
4. **Extraction pipeline** — See the three-page run, record counts, and two repeated listings removed.
5. **Denver collection** — Switch the source location and sample size to process 50 fictional Denver properties across six pages.
6. **Mobile layout** — Filter the Denver dataset by a minimum 2,400 square feet; the table scrolls within its container on a narrow screen.

Lead with the property overview, then comparison and pipeline screenshots. Use the filtered table when highlighting data-handling skills. Every illustration is schematic, and every listing is synthetic.

## Interview walkthrough (about 90 seconds)

1. Explain how the demo separates generated source data from the real parser and collector.
2. Show the 25-property overview, then apply the $600,000 and three-bedroom filters.
3. Switch to the table and show the descending price order.
4. Select three homes and compare price, room counts, and floor area.
5. Open Pipeline to explain duplicate detection, page boundaries, and explicit failure reporting.
6. Show a regression test for partial metadata, typed Excel prices, or a failed later page preserving earlier results.

The export endpoint is covered by automated workbook checks. During this review, browser download permission was declined, so test that specific browser action yourself before presenting it live.

Avoid claims about scraping live Realtor.com successfully, production scale, real property valuation, or time savings unless separately verified. The demonstrated strengths are code quality, data integrity, reproducibility, and an inspectable user experience.
