"""GET /api/agent-events — stub.

The live SSE event stream needs the long-lived local backend
(python backend/voice_agent_server.py). Serverless functions can't hold
open SSE connections, so this tells the frontend explicitly (410 Gone).
"""
from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({"error": "Live agent events need the local backend (python backend/voice_agent_server.py)."}).encode()
        self.send_response(410)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
