"""Loopback-only property exploration dashboard using synthetic HTML fixtures."""

import io
import json
import logging
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from realestate_scraper import export_to_excel, number, run_demo

STATIC = Path(__file__).parent / "web"
CITIES = {"Austin, TX", "Denver, CO", "Raleigh, NC"}


def dataset(query):
    params = parse_qs(query, keep_blank_values=True)
    city = params.get("city", ["Austin, TX"])[0]
    count = int(params.get("count", ["25"])[0])
    if city not in CITIES or count not in {25, 50, 100}:
        raise ValueError("Choose a supported city and sample size")
    records, stats = run_demo(city, 800000, 2, count=count)
    return records, stats, params


def filter_records(records, params):
    search = params.get("search", [""])[0].strip().casefold()
    budget = int(params.get("budget", ["800000"])[0])
    beds = int(params.get("beds", ["0"])[0])
    area = int(params.get("area", ["0"])[0])
    sort = params.get("sort", ["price-asc"])[0]
    if not 1 <= budget <= 10000000 or not 0 <= beds <= 12 or not 0 <= area <= 10000:
        raise ValueError("Invalid property filters")
    orders = {
        "price-asc": ("price", False),
        "price-desc": ("price", True),
        "area-desc": ("sqft", True),
    }
    if sort not in orders:
        raise ValueError("Invalid sort order")
    results = [
        r
        for r in records
        if (not search or search in r.address.casefold())
        and number(r.price, "price") is not None
        and number(r.price, "price") <= budget
        and number(r.beds, "beds") is not None
        and number(r.beds, "beds") >= beds
        and (not area or (number(r.sqft, "sqft") or 0) >= area)
    ]
    field, descending = orders[sort]
    return sorted(results, key=lambda r: number(getattr(r, field), field) or 0, reverse=descending)


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, body, mime, filename=None):
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'",
        )
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.headers.get("Host", "").split(":")[0] not in {"127.0.0.1", "localhost"}:
            self.reply(403, b"Local access only", "text/plain")
            return
        parsed = urlsplit(self.path)
        static = {
            "/": ("index.html", "text/html; charset=utf-8"),
            "/app.css": ("app.css", "text/css"),
            "/app.js": ("app.js", "text/javascript"),
        }
        if parsed.path in static:
            filename, mime = static[parsed.path]
            self.reply(200, (STATIC / filename).read_bytes(), mime)
            return
        if parsed.path == "/favicon.ico":
            self.reply(204, b"", "image/x-icon")
            return
        if parsed.path not in {"/api/demo", "/api/export"}:
            self.reply(404, b"Not found", "text/plain")
            return
        try:
            records, stats, params = dataset(parsed.query)
            if parsed.path == "/api/demo":
                rows = []
                for record in records:
                    row = asdict(record)
                    row["id"] = record.listing_url.rsplit("/", 1)[-1]
                    row["values"] = {
                        k: number(getattr(record, k), k) for k in ("price", "beds", "baths", "sqft")
                    }
                    rows.append(row)
                self.reply(
                    200,
                    json.dumps(
                        {
                            "listings": rows,
                            "stats": stats,
                            "city": params.get("city", ["Austin, TX"])[0],
                        }
                    ).encode(),
                    "application/json",
                )
            else:
                records = filter_records(records, params)
                if not records:
                    raise ValueError("No matching listings to export")
                buffer = io.BytesIO()
                export_to_excel(records, buffer, source=stats["source"])
                self.reply(
                    200,
                    buffer.getvalue(),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "habitat_listings_demo.xlsx",
                )
        except (ValueError, OverflowError) as exc:
            self.reply(400, json.dumps({"error": str(exc)}).encode(), "application/json")
        except Exception:
            logging.exception("Dashboard request failed")
            self.reply(
                500,
                b'{"error":"Unable to complete the request. Check the server log."}',
                "application/json",
            )

    def log_message(self, format, *args):
        logging.getLogger(__name__).info(format, *args)


def serve(port=8766):
    with ThreadingHTTPServer(("127.0.0.1", port), Handler) as server:
        print(f"Habitat dashboard: http://127.0.0.1:{server.server_port}", flush=True)
        print("Offline demo. Press Ctrl+C to stop.", flush=True)
        server.serve_forever()
