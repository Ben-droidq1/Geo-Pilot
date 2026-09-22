"""GET /api/voice-token — mint a short-lived AssemblyAI streaming token.

Needs ASSEMBLYAI_API_KEY env var (set in Vercel dashboard, never committed).
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.parse
import urllib.request


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        key = os.environ.get("ASSEMBLYAI_API_KEY", "")
        if not key:
            return self._json(500, {"error": "ASSEMBLYAI_API_KEY missing"})
        url = "https://streaming.assemblyai.com/v3/token?" + urllib.parse.urlencode(
            {"expires_in_seconds": 300}
        )
        try:
            req = urllib.request.Request(url, headers={"Authorization": key})
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = json.loads(resp.read())
            return self._json(200, payload)
        except Exception as exc:  # noqa: BLE001
            return self._json(502, {"error": f"token mint failed: {exc}"})

    def _json(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
