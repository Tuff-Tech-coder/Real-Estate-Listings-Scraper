# Real Estate Listings Scraper

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Chromium-2EAD33?logo=playwright&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

A JavaScript-aware web scraper that pulls real estate listings from Realtor.com and exports them to a clean, formatted Excel workbook. Because Realtor.com renders its listings client-side, this uses **Playwright + Chromium** rather than plain HTTP requests — the same approach needed for any modern, JS-heavy site.

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
realestate-scraper/
├── realestate_scraper.py   # Main scraper
├── requirements.txt        # Python dependencies
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

## Possible extensions

Add geocoding for map plotting, push results to Google Sheets or a database, schedule recurring runs to track new listings, or extend the parser to additional portals.
