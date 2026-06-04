# Real Estate Listings Scraper

A Python web scraper that pulls real estate listings from Realtor.com using Playwright (handles JavaScript-rendered pages). Filter by city, maximum price, and minimum bedrooms. Outputs a clean, formatted Excel file.

## Features

- Uses **Playwright + Chromium** to render JavaScript-heavy listing pages
- Filters by city, maximum price, and minimum bedrooms
- Handles **pagination** automatically — scrapes until no more results
- Polite scraping: randomized delays between pages (4–8 seconds)
- Outputs a formatted **Excel file** with auto-fitted columns and a styled header
- **Demo mode** generates 25 realistic sample listings without making any live requests

## Project Structure

```
realestate-scraper/
├── realestate_scraper.py    # Main scraper
├── requirements.txt         # Python dependencies
├── sample_listings.xlsx     # Sample output (25 demo listings)
└── scraper.log              # Application log (created on run)
```

## Setup

### 1. Install dependencies

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Run the scraper

```bash
# Live scraping
python realestate_scraper.py --city "Austin, TX" --max-price 500000 --min-beds 3

# Demo mode (no live requests — great for testing)
python realestate_scraper.py --demo

# Custom output filename
python realestate_scraper.py --city "Denver, CO" --max-price 600000 --min-beds 2 --output denver_listings.xlsx

# Show the browser window (useful for debugging)
python realestate_scraper.py --no-headless
```

## Command-Line Options

| Option | Default | Description |
|---|---|---|
| `--city` | `"Austin, TX"` | City and state to search |
| `--max-price` | `500000` | Maximum listing price |
| `--min-beds` | `3` | Minimum bedrooms |
| `--max-pages` | `3` | Maximum result pages to scrape |
| `--output` | `listings.xlsx` | Output Excel filename |
| `--demo` | off | Use generated sample data |
| `--no-headless` | off | Show browser window |

## Sample Output (`sample_listings.xlsx`)

| Address | Price | Beds | Baths | Sq Ft | Listing URL | Date Scraped |
|---|---|---|---|---|---|---|
| 4823 Oak Ridge Dr, Austin, TX 78704 | $342,500 | 3 | 2.0 | 1,847 | https://realtor.com/... | 2024-05-10 |
| 1156 Sunset Blvd, Austin, TX 78702 | $489,000 | 4 | 2.5 | 2,314 | https://realtor.com/... | 2024-05-10 |
| ... | ... | ... | ... | ... | ... | ... |

## Notes

- Realtor.com's layout changes periodically — if selectors stop working, check the browser dev tools for updated CSS selectors in `_parse_card()`.
- For large-scale scraping (100+ pages), add proxy rotation via a service like Bright Data or Oxylabs to avoid IP-based rate limiting.
- The `--no-headless` flag lets you watch the browser scrape in real time, which is helpful for debugging.
