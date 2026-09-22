"""POST /api/chat — stateless chat via the Qwen-compatible vision/text API.

Body: {"message": str, "cameras": [...optional], "history": [...optional]}
Needs QWEN_API_KEY / QWEN_BASE_URL / QWEN_MODEL env vars.
Frame capture (OpenCV/HLS) is a local-backend feature — serverless answers
from text context and tells the user when a live view needs the local server.
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            length = 0
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            return self._json(400, {"error": "invalid JSON body"})

        message = str(payload.get("message", "")).strip()
        if not message:
            return self._json(400, {"error": "message required"})

        api_key = os.environ.get("QWEN_API_KEY", "")
        base_url = os.environ.get("QWEN_BASE_URL", "").rstrip("/")
        model = os.environ.get("QWEN_MODEL", "")
        if not (api_key and base_url and model):
            return self._json(500, {"error": "Qwen env vars missing (QWEN_API_KEY/BASE_URL/MODEL)"})

        cameras = payload.get("cameras") or []
        context = ""
        if cameras:
            names = [c.get("name", "camera") for c in cameras if isinstance(c, dict)][:5]
            if names:
                context = f"Relevant cameras: {', '.join(names)}. "

        body = json.dumps(
            {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are GeoPilot, a friendly traffic intelligence assistant. "
                            "Reply concisely in 1-2 sentences. "
                            + context
                            + "Note: live frame capture runs on the local backend; "
                              "if asked what a camera sees right now and no image was provided, "
                              "say the live view needs the local server."
                        ),
                    },
                    {"role": "user", "content": message},
                ],
                "max_tokens": 300,
                "temperature": 0.7,
            }
        ).encode()
        try:
            req = urllib.request.Request(
                f"{base_url}/chat/completions",
                data=body,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=25) as resp:
                answer = json.loads(resp.read())["choices"][0]["message"]["content"].strip()
        except Exception as exc:  # noqa: BLE001
            return self._json(502, {"error": f"chat backend failed: {exc}"})
        return self._json(200, {"answer": answer})

    def _json(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
