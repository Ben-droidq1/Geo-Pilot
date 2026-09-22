"""GET /api/search-cameras?q=&lat=&lon=&limit= — stateless camera search.

Reads the camera database shipped with the frontend (frontend/public),
so it works on Vercel with no extra backend process.
"""
from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

try:
    from _common import search_cameras, get_stream_url
except ImportError:  # pragma: no cover — Vercel path quirk fallback
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _common import search_cameras, get_stream_url


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        q = params.get("q", [""])[0]
        try:
            lat = float(params["lat"][0]) if "lat" in params else None
            lon = float(params["lon"][0]) if "lon" in params else None
            limit = int(params.get("limit", ["10"])[0])
        except (ValueError, IndexError):
            return self._json(400, {"error": "Invalid lat/lon/limit parameter"})
        cameras = search_cameras(query=q, lat=lat, lon=lon, limit=limit)
        for cam in cameras:
            cam["stream"] = get_stream_url(cam["index"])
        return self._json(200, {"cameras": cameras, "total": len(cameras)})

    def _json(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
