"""POST /api/scrape — stub.

Scraping runs a long-lived scraper subprocess with NDJSON progress
(frontend/scripts/server.py locally). Not feasible serverless — 410 Gone
with guidance instead of a bare 404.
"""
from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.dumps({"error": "Scraping needs the local control server (cd frontend && python scripts/server.py)."}).encode()
        self.send_response(410)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
