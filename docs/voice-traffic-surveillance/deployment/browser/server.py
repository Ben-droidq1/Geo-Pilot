#!/usr/bin/env python3
"""
GeoPilot Voice Agent Browser Server
Serves the browser interface for the voice agent.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="GeoPilot Voice Agent Browser")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Serve static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main voice agent interface."""
    index_file = Path(__file__).parent / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>GeoPilot Voice Agent</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
            .connected { background: #d4edda; color: #155724; }
            .disconnected { background: #f8d7da; color: #721c24; }
            #transcript { background: #f5f5f5; padding: 15px; border-radius: 5px; min-height: 200px; }
            .controls { margin: 20px 0; }
            button { padding: 10px 20px; margin: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>GeoPilot Traffic Surveillance Voice Agent</h1>
        <div id="status" class="status disconnected">Disconnected</div>
        <div class="controls">
            <button onclick="connect()">Connect</button>
            <button onclick="disconnect()">Disconnect</button>
        </div>
        <div id="transcript"></div>
        <script>
            let ws = null;
            const statusEl = document.getElementById('status');
            const transcriptEl = document.getElementById('transcript');

            function connect() {
                ws = new WebSocket('ws://localhost:3000/ws');
                ws.onopen = () => {
                    statusEl.textContent = 'Connected';
                    statusEl.className = 'status connected';
                };
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    transcriptEl.innerHTML += '<p><strong>Agent:</strong> ' + data.text + '</p>';
                };
                ws.onclose = () => {
                    statusEl.textContent = 'Disconnected';
                    statusEl.className = 'status disconnected';
                };
            }

            function disconnect() {
                if (ws) ws.close();
            }
        </script>
    </body>
    </html>
    """)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "GeoPilot Voice Agent Browser"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000, log_level="info")
