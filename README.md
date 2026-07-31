# Real Estate Listings Scraper

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Chromium-2EAD33?logo=playwright&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-3.x-150458?logo=pandas&logoColor=white)
![Tests](https://img.shields.io/badge/tests-24%20passing-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)

A browser-driven extraction pipeline that turns paginated, client-rendered property listings into a clean Excel workbook. Listings that a plain HTTP client never sees — because the markup arrives empty and the content is assembled in JavaScript — are captured by driving a real headless browser and waiting for the render.

```bash
pip install -r requirements.txt
python realestate_scraper.py --demo      # 25 listings, no browser, no network
```

---

## ⚖️ Responsible use

Automated collection from any site is governed by that site's Terms of Service and `robots.txt`, and property listing data is frequently licensed rather than public domain.

**Before pointing this at a live site:**

1. Read that site's Terms of Service and `robots.txt`, and honour them.
2. Prefer an official feed where one exists — most MLS data is available through licensed IDX/RETS/RESO Web API providers, which is the sanctioned route for listing data.
3. Keep the built-in delays and the `--max-pages` cap on.

`--demo` generates 25 realistic listings locally and is the intended path for evaluating this project. The parsing and export layers are source-agnostic and unit-tested against stubs, so the pipeline is useful independently of where the HTML comes from.

---

## Why it's useful

Most listing portals load their data with JavaScript, so a standard `requests` scraper comes back empty. This project demonstrates the real-world fix: drive a headless browser, wait for the dynamic content, and extract structured records — then deliver them in a format a non-technical client can open immediately.

---

## Features

- **Renders JavaScript** with Playwright/Chromium so dynamically loaded listings are actually captured.
- **Filterable search** — city, maximum price, and minimum bedrooms, mapped into Realtor.com's URL filter scheme.
- **Automatic pagination** — walks through result pages until listings run out or a page limit is hit.
- **Resilient parsing** — primary `data-testid` selectors with regex fallbacks for beds/baths/sqft when the markup varies.
- **Polite scraping** — randomized 3–6s render waits and 4–8s delays between pages, plus a realistic browser context (User-Agent + viewport).
- **Formatted Excel output** via `openpyxl` — auto-fit columns and a styled header row (address, price, beds, baths, sq ft, listing URL, date scraped).
- **Demo mode** generates 25 realistic sample listings with no live requests — perfect for reviewing the output instantly.
- **Headless or visible** browser (`--no-headless`) for easy debugging.

---

## Tech stack

`Python` · `Playwright (Chromium)` · `BeautifulSoup` · `pandas` · `openpyxl` · `dataclasses` · `argparse` · `logging`

---

## Project structure

```
├── realestate_scraper.py   # Main scraper
├── requirements.txt        # Python dependencies
├── tests/                  # 24 unit tests
├── sample_listings.xlsx    # Sample output (25 demo listings)
└── scraper.log             # Generated: application log
```

---

## Setup

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium       # one-time browser download
```

`playwright install chromium` is only needed for live scraping. `--demo` and the
test suite both run without it.

---

## Usage

```bash
# Live scrape with filters
python realestate_scraper.py --city "Austin, TX" --max-price 500000 --min-beds 3

# Generate sample data, no network
python realestate_scraper.py --demo

# Watch the browser work (debugging)
python realestate_scraper.py --city "Austin, TX" --no-headless
```

**Options:** `--city` · `--max-price` · `--min-beds` · `--max-pages` · `--output` · `--demo` · `--no-headless`

---

## How it works

1. Builds a filtered Realtor.com search URL from the CLI arguments.
2. Launches Chromium with a realistic browser context and navigates page by page.
3. Waits for listing cards to render, then extracts each into a typed `Listing` dataclass (with regex fallbacks for missing fields).
4. Stops on the last page or when `--max-pages` is reached.
5. Writes everything to a styled Excel workbook.

---

## Development

```bash
pip install -r requirements.txt
pip install pytest ruff

pytest -q          # 24 tests
ruff check .
```

The suite launches no browser and makes no request. Playwright's element API is
small enough to stub directly — `query_selector`, `inner_text`, `get_attribute` —
which is what makes card parsing testable without downloading Chromium.

It covers URL construction from the filter arguments (including city
slugification and the page-1 suffix rule), defensive card parsing (the regex
fallback used when the `data-testid` attributes are absent, relative-to-absolute
listing URLs, cards that must be rejected, and a detached element that must not
kill the whole card), and the Excel export.

One assertion worth calling out: demo listings must genuinely satisfy the
`--max-price` and `--min-beds` filters they claim to match. Demo data that
violates its own filters would misrepresent what the tool does.

---

## Possible extensions

Add geocoding for map plotting, push results to Google Sheets or a database, schedule recurring runs to track new listings, or extend the parser to additional portals.
