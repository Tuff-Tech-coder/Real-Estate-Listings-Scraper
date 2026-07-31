"""
Real Estate Scraper
===================
Scrapes real estate listings from Realtor.com using Playwright (handles
JavaScript-rendered content). Filters by city, maximum price, and minimum
bedrooms. Outputs results to a formatted Excel file.

Usage:
    python realestate_scraper.py --city "Austin, TX" --max-price 500000 --min-beds 3
    python realestate_scraper.py --demo    # Generate sample data without live requests

Requirements:
    pip install -r requirements.txt
    playwright install chromium
"""

import argparse
import datetime
import logging
import random
import re
import time
from dataclasses import asdict, dataclass, field

import pandas as pd
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("scraper.log", encoding="utf-8")],
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
@dataclass
class Listing:
    address: str = ""
    price: str = ""
    beds: str = ""
    baths: str = ""
    sqft: str = ""
    listing_url: str = ""
    date_scraped: str = field(default_factory=lambda: datetime.date.today().isoformat())


# ---------------------------------------------------------------------------
# Scraper
# ---------------------------------------------------------------------------
class RealEstateScraper:
    BASE_URL = "https://www.realtor.com/realestateandhomes-search"

    def __init__(self, city: str, max_price: int, min_beds: int, headless: bool = True):
        self.city = city
        self.max_price = max_price
        self.min_beds = min_beds
        self.headless = headless

    def _build_url(self, page_num: int = 1) -> str:
        """Build a Realtor.com search URL with filters applied."""
        # Convert city name to URL slug format: "Austin, TX" → "Austin_TX"
        city_slug = self.city.replace(", ", "_").replace(" ", "_")
        base = f"{self.BASE_URL}/{city_slug}"
        params = (
            f"/price-na-{self.max_price}"
            f"/beds-{self.min_beds}-na"
        )
        page_suffix = f"/pg-{page_num}" if page_num > 1 else ""
        return f"{base}{params}{page_suffix}"

    def _parse_listings(self, page) -> list[Listing]:
        """Extract all listing cards from the current page."""
        listings = []

        # Wait for listing cards to appear
        try:
            page.wait_for_selector('[data-testid="card-content"]', timeout=15000)
        except PlaywrightTimeout:
            logger.warning("Listing cards did not appear - page may be empty or still rendering")
            return listings

        cards = page.query_selector_all('[data-testid="card-content"]')
        logger.info(f"Found {len(cards)} listing cards on page")

        for card in cards:
            try:
                listing = self._parse_card(card, page)
                if listing:
                    listings.append(listing)
            except Exception as e:
                logger.debug(f"Error parsing card: {e}")

        return listings

    def _parse_card(self, card, page) -> Listing | None:
        """Parse a single listing card element into a Listing object."""

        def safe_text(selector: str, element=None) -> str:
            """Return inner text of a selector or empty string on miss."""
            try:
                el = (element or card).query_selector(selector)
                return el.inner_text().strip() if el else ""
            except Exception:
                return ""

        # --- Price ---
        price_raw = safe_text('[data-testid="card-price"]')
        if not price_raw:
            price_raw = safe_text(".Pricestyles__Component-rui__sc-rmiu7q-0")

        # --- Address ---
        address = safe_text('[data-testid="card-address-1"]')
        address2 = safe_text('[data-testid="card-address-2"]')
        if address2:
            address = f"{address}, {address2}"

        # --- Beds / Baths / Sqft ---
        beds = safe_text('[data-testid="property-meta-beds"]')
        baths = safe_text('[data-testid="property-meta-baths"]')
        sqft = safe_text('[data-testid="property-meta-sqft"]')

        # Fallback: scrape from combined meta string
        if not beds:
            meta = safe_text(".property-meta")
            beds_match = re.search(r"(\d+)\s*(?:bed|bd)", meta, re.I)
            baths_match = re.search(r"([\d.]+)\s*(?:bath|ba)", meta, re.I)
            sqft_match = re.search(r"([\d,]+)\s*sq\s*ft", meta, re.I)
            beds = beds_match.group(1) if beds_match else ""
            baths = baths_match.group(1) if baths_match else ""
            sqft = sqft_match.group(1) if sqft_match else ""

        # --- Listing URL ---
        url = ""
        link = card.query_selector("a")
        if link:
            href = link.get_attribute("href") or ""
            url = href if href.startswith("http") else f"https://www.realtor.com{href}"

        if not address and not price_raw:
            return None

        return Listing(
            address=address,
            price=price_raw,
            beds=beds,
            baths=baths,
            sqft=sqft,
            listing_url=url,
        )

    def scrape(self, max_pages: int = 5) -> list[Listing]:
        """
        Scrape listings across multiple pages.
        Stops early if fewer listings are found than expected (last page).
        """
        all_listings: list[Listing] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 900},
            )
            page = context.new_page()

            for page_num in range(1, max_pages + 1):
                url = self._build_url(page_num)
                logger.info(f"Scraping page {page_num}: {url}")

                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    # Extra wait for JS rendering
                    time.sleep(random.uniform(3, 6))
                except PlaywrightTimeout:
                    logger.warning(f"Page {page_num} timed out - stopping pagination")
                    break
                except Exception as e:
                    logger.error(f"Failed to load page {page_num}: {e}")
                    break

                page_listings = self._parse_listings(page)
                all_listings.extend(page_listings)

                logger.info(f"Page {page_num}: scraped {len(page_listings)} listings")

                # If no listings on this page, we've hit the end
                if not page_listings:
                    logger.info("No listings found - reached last page")
                    break

                # Polite delay between pages
                if page_num < max_pages:
                    delay = random.uniform(4, 8)
                    logger.info(f"Waiting {delay:.1f}s before next page...")
                    time.sleep(delay)

            browser.close()

        logger.info(f"Total listings scraped: {len(all_listings)}")
        return all_listings


# ---------------------------------------------------------------------------
# Demo data generator (20+ realistic listings)
# ---------------------------------------------------------------------------
def generate_demo_listings(city: str, max_price: int, min_beds: int) -> list[Listing]:
    """Generate realistic-looking demo listings matching the filter criteria."""
    streets = [
        "Oak Ridge Dr", "Maple Ave", "Sunset Blvd", "Elm St", "Cedar Ln",
        "Pine Tree Rd", "Willow Creek Way", "Riverstone Pkwy", "Hillcrest Dr",
        "Magnolia Ct", "Bluebonnet Trl", "Pecan Grove Dr", "Lake View Ln",
        "Canyon Rd", "Meadowbrook Dr", "Springdale Ave", "Westover Hills Blvd",
        "Rolling Hills Rd", "Barton Creek Blvd", "Congress Ave", "Lamar Blvd",
        "South Lamar", "Research Blvd", "Burnet Rd", "Slaughter Ln",
    ]
    city_state = city.split(",")[0].strip()
    state = city.split(",")[1].strip() if "," in city else "TX"
    zip_codes = ["78701", "78702", "78703", "78704", "78705", "78741", "78745", "78748", "78749"]

    listings = []
    for i, street in enumerate(streets):
        beds = random.randint(max(min_beds, 2), min(min_beds + 2, 6))
        baths = round(random.choice([1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]), 1)
        sqft = random.randint(1000, 3800)
        price = random.randint(
            int(max_price * 0.55),
            int(max_price * 0.97),
        )
        house_num = random.randint(100, 9999)
        zipcode = random.choice(zip_codes)

        listings.append(Listing(
            address=f"{house_num} {street}, {city_state}, {state} {zipcode}",
            price=f"${price:,}",
            beds=str(beds),
            baths=str(baths),
            sqft=f"{sqft:,}",
            listing_url=f"https://www.realtor.com/realestateandhomes-detail/sample-listing-{i+1}",
        ))

    return listings


# ---------------------------------------------------------------------------
# Excel export
# ---------------------------------------------------------------------------
def export_to_excel(listings: list[Listing], output_path: str) -> None:
    """Write listings to a formatted Excel file."""
    if not listings:
        logger.warning("No listings to export")
        return

    rows = [asdict(listing) for listing in listings]
    df = pd.DataFrame(rows)

    # Rename columns to be client-friendly
    df.columns = ["Address", "Price", "Beds", "Baths", "Sq Ft", "Listing URL", "Date Scraped"]

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Listings")

        # Auto-fit column widths
        ws = writer.sheets["Listings"]
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col) + 2
            ws.column_dimensions[col[0].column_letter].width = min(max_len, 60)

        # Bold header row
        from openpyxl.styles import Alignment, Font, PatternFill
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="2D6A4F", end_color="2D6A4F", fill_type="solid")
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")

    logger.info(f"Exported {len(listings)} listings to {output_path}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Real Estate Listings Scraper")
    parser.add_argument("--city", default="Austin, TX", help="City to search (e.g. 'Austin, TX')")
    parser.add_argument("--max-price", type=int, default=500000, help="Maximum listing price")
    parser.add_argument("--min-beds", type=int, default=3, help="Minimum number of bedrooms")
    parser.add_argument("--max-pages", type=int, default=3, help="Max result pages to scrape")
    parser.add_argument("--output", default="listings.xlsx", help="Output Excel filename")
    parser.add_argument("--demo", action="store_true", help="Generate demo data (no live requests)")
    parser.add_argument("--no-headless", action="store_true", help="Show browser window (for debugging)")
    args = parser.parse_args()

    logger.info("Real Estate Scraper starting")
    logger.info(f"City: {args.city} | Max Price: ${args.max_price:,} | Min Beds: {args.min_beds}")

    if args.demo:
        logger.info("Demo mode: generating sample listings...")
        listings = generate_demo_listings(args.city, args.max_price, args.min_beds)
    else:
        scraper = RealEstateScraper(
            city=args.city,
            max_price=args.max_price,
            min_beds=args.min_beds,
            headless=not args.no_headless,
        )
        listings = scraper.scrape(max_pages=args.max_pages)

    if listings:
        export_to_excel(listings, args.output)
        print(f"\n[OK] Done! {len(listings)} listings saved to: {args.output}")
    else:
        print("No listings found. Try different search parameters or check the log.")


if __name__ == "__main__":
    main()
