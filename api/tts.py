"""GET /api/tts?text= — stub.

TTS uses edge-tts on the local backend, which isn't available serverless.
Returns 501 with guidance so the frontend can fall back to browser speech.
"""
from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({"error": "TTS needs the local backend with edge-tts installed."}).encode()
        self.send_response(501)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
