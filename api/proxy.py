"""GET /api/proxy?url= — minimal HLS/image proxy for browser playback.

Stdlib only. Blocks non-http(s) targets and caps the fetched size.
"""
from http.server import BaseHTTPRequestHandler
import urllib.parse
import urllib.request

MAX_BYTES = 8 * 1024 * 1024


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        url = params.get("url", [""])[0]
        if not url or not url.startswith(("http://", "https://")):
            return self._err(400, "url parameter required (http/https)")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "GeoPilot/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                ctype = resp.headers.get("Content-Type", "application/octet-stream")
                data = resp.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                return self._err(413, "upstream response too large")
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data)
        except Exception as exc:  # noqa: BLE001 — surfacing as 502 is the point
            return self._err(502, f"proxy fetch failed: {exc}")

    def _err(self, code, message):
        import json

        body = json.dumps({"error": message}).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
