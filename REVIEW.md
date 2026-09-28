# Debugging and verification record

Review date: 2026-09-27. The original 24 tests and lint check passed. Seventeen additional regression tests were then run against the original code; all seventeen failed before repair.

## Reproduced issues fixed

| Original behavior | Corrected behavior |
|---|---|
| Missing bath/area fields were not recovered when beds existed | Fallback runs independently for each missing field |
| Missing beds caused existing bath/area values to be overwritten | Existing values are preserved |
| Address line 2 alone produced a leading comma | Only nonempty address lines are joined |
| Protocol-relative listing URLs were malformed | URLs resolve using standard URL joining |
| Empty href became a fake root listing URL | Missing links remain blank |
| JavaScript href became a fabricated HTTPS URL | Unsupported URL schemes are rejected |
| A detached link could discard a valid property card | Link failure leaves other fields intact |
| Austin,TX was not slugified like Austin, TX | Whitespace and comma separators normalize consistently |
| Seven-bedroom demo generation crashed | Bedroom generation supports higher valid minima |
| Denver demos reused Austin ZIP codes | Supported cities get matching ZIP labels; unknown cities omit ZIPs |
| Fictional demo links looked like Realtor.com listings | Demo links use a reserved .example domain |
| Nested output folders caused export failure | Parent folders are created |
| Prices, bedroom counts, baths, and area were text cells | Recognized scalar values are numeric Excel cells |
| Formula-like addresses became Excel formulas | Scraped strings remain literal text |
| Illegal control characters crashed workbook creation | Unsupported Excel control characters are removed |
| Importing the module created a log file | CLI-only logging configuration avoids import side effects |
| Negative bedroom filters were accepted | Input validation rejects invalid filters before browser startup |

## Other improvements

- Shared parsing/collection path for local HTML, JavaScript-rendered fixtures, and live browser pages.
- Explicit empty-page markers distinguished from unknown/blocked pages.
- HTTP errors, navigation timeouts, and detached pagination retain a useful failure status.
- Partial results export with a warning and nonzero exit code.
- Same-host pagination, repeated-URL detection, record deduplication, and local numeric filter checks.
- Browser cleanup in a finally block and selector-based rendering waits.
- Numeric overflow handling, typed dates, frozen headers, worksheet filters, and atomic exports.
- A local dashboard with search, filters, sorting, comparisons, and processing activity.
- Removed the unused requests dependency.

## Verification evidence

- **82 tests passed** with the optional Chromium integration enabled on Windows / Python 3.12.
- Ruff lint and formatting checks passed; JavaScript passed the Node syntax check.
- CLI Chromium demo successfully produced 25 records over three asynchronously rendered pages, removing two duplicates. Its record values match the plain HTML-fixture path.
- API integration tests read actual workbook response bytes and verify filtered records, ordering, numeric values, headers, and source notes.
- Atomic-export regression verifies that a failed replacement preserves an existing output file.
- Browser walkthrough verified next/previous pages, price/bedroom/area filters, descending price sort, card/table switching, search empty states, unavailable metrics on empty results, and disabled empty export.
- Comparison controls were exercised: add three properties, reject a fourth, display side-by-side data, and clear the selection.
- Alternate dashboard run: 50 Denver properties, 6 pages, 5 duplicates removed. A 2,400-square-foot minimum leaves 21 properties.
- Desktop and mobile layouts were visually inspected. No page-level horizontal overflow at the mobile breakpoint; the data table scrolls inside its container.

## Limits and permissions

Live Realtor.com access and selector compatibility were not tested. Browser-based extraction was verified only against locally generated fixtures. No production-volume or real-market claims are established. Remote CI and Python 3.11 execution were not performed locally.

The user declined the in-app browser's download permission. The browser download was not retried or worked around. The export endpoint had already been checked through automated in-memory workbook tests. The included sample workbook was produced earlier by the CLI Chromium demo, independently of the declined browser download. Native Excel was not used to inspect it.

The Windows launcher is provided as a convenience; the program was launched directly using the isolated Python environment during this review. The screenshots are direct browser captures of the running dashboard, with synthetic records and schematic property art.
