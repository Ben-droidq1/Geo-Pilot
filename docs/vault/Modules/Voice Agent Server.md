# Voice Agent Server

> `voice_agent_server.py` (~1250 lines) — Single backend for voice, chat, analytics, proxy, TTS, camera search

## Overview

Argus Voice Agent Server — a standalone HTTP server combining:
- **AssemblyAI v3** real-time transcription (PCM at system sample rate)
- **Qwen VL** (api.b.ai) for vision analysis of camera frames
- **Frame capture** via OpenCV + ffmpeg fallback for HLS streams
- **Content-based camera search** — matches by name, city, country, source type, and keywords
- **Analytics API** — vehicle count, speed stats, flow rate, etc.
- **CORS proxy** for external APIs
- **TTS** via edge-tts
- **Country code mapping** — "United States" → "us", "beach" → surf-cams, etc.

Runs on **port 8789**. Starts automatically when you run `python main.py`.

## Entry Point

```bash
# One command — GUI + voice agent
python main.py

# Or standalone (headless)
python voice_agent_server.py
```

Binds to `127.0.0.1:8789`.

## Architecture

```
main.py
  └─ starts voice_agent_server in daemon thread
       │
       ├── Voice Agent Endpoints (AssemblyAI + frontend)
       │   ├── GET  /api/health          → Health check
       │   ├── GET  /api/voice-token     → AssemblyAI v3 streaming token
       │   ├── GET  /api/agent-id        → Returns agent ID
       │   ├── GET  /api/capture         → Capture single frame (OpenCV + ffmpeg)
       │   ├── GET  /api/tts             → Text-to-speech (edge-tts)
       │   ├── GET  /api/search-cameras  → Content-aware camera search
       │   ├── GET  /api/agent-events    → SSE stream for agent commands
       │   ├── GET  /api/proxy           → CORS proxy for external APIs
       │   ├── GET  /api/tool/search-cameras   → Voice tool: search cameras
       │   ├── GET  /api/tool/analyze-cameras  → Voice tool: capture + analyze
       │   ├── GET  /api/tool/capture-frame    → Voice tool: single frame
       │   └── POST /api/chat            → Smart chat with auto camera discovery
       │
       └── Analytics Endpoints (voice agent tool calls)
           ├── GET  /vehicle-count       → Unique vehicle counts by class
           ├── GET  /speed-stats         → Avg/min/max/median speed
           ├── GET  /summary             → Full scene summary
           ├── GET  /peak-hours?top_n=5  → Busiest frames
           ├── GET  /turning-patterns    → Heading cardinal split
           ├── GET  /flow-rate           → Vehicles per minute
           ├── GET  /object/{frame_idx}  → Objects at specific frame
           └── POST /load                → Load replay .json.gz file
```

## Config (from `.env`)

| Variable | Default | Description |
|---|---|---|
| `ASSEMBLYAI_API_KEY` | `""` | AssemblyAI API key |
| `QWEN_API_KEY` | `""` | Qwen VL API key |
| `QWEN_BASE_URL` | `""` | Qwen API endpoint |
| `QWEN_MODEL` | `""` | Vision model |
| `GEOPILOT_AGENT_ID` | `""` | AssemblyAI agent ID |
| `TTS_VOICE` | `en-US-GuyNeural` | TTS voice |
| `FRAME_CACHE_TTL` | `5` | Frame cache TTL in seconds |
| `AGENT_PORT` | `8789` | Server port |

## Key Components

### 1. Camera Search (Content-Aware)
- Lazy-loads `Argus/public/cameras.core.json` + `cameras.labels.json`
- `search_cameras(query, lat, lon, radius_km, limit)` — text + proximity + content search
- **Country code mapping**: "United States" → "us", "South Korea" → "kr", etc.
- **Content keyword mapping**: "beach" → surf-cams, "mountain" → ski-cams, "airport" → airport-webcams
- `get_camera_stream_url(cam_index)` — fetches stream URL from chunked detail files
- Haversine distance calculation for proximity sorting

### 2. Frame Capture (OpenCV + ffmpeg Fallback)
- `capture_frame(url)` — tries OpenCV first, falls back to ffmpeg for HLS streams
- ffmpeg uses `-rw_timeout 5000000` (5s) and 8s subprocess timeout
- `FRAME_CACHE_TTL`-second TTL cache per URL
- `capture_multiple_frames(urls)` — concurrent capture using `ThreadPoolExecutor(max_workers=8)`
- SSRF protection: `_is_safe_url()` blocks private/internal IPs

### 3. Voice Input (AssemblyAI v3)
- Real-time PCM transcription at system sample rate (44.1/48kHz)
- `ScriptProcessorNode` streams raw PCM int16 to WebSocket
- `Turn` messages with `end_of_turn` flag for partial/final transcripts
- Auto-send after 2s silence gap
- Mini heads-up display shows live transcription

### 4. Smart Chat (`/api/chat`)
- Detects camera-related intent from keywords
- Location extraction via Qwen LLM + regex fallback
- Auto-discovers cameras via text search (broader fallback if no location match)
- Content-based search: "beach" finds surf-cams, "mountain" finds ski-cams
- Fast text-only path for greetings (no vision API)
- Concurrent frame capture from all discovered cameras
- Publishes `agent_cameras_found` events to frontend via SSE

### 5. Qwen Vision API
- `ask_qwen_vision(question, images_b64, context)` — OpenAI-compatible API call
- System prompt: multi-camera aware — counts vehicles, detects congestion
- Supports multi-image input

### 6. TTS
- `edge_tts` library with configurable voice (`TTS_VOICE` env var)
- `generate_tts(text)` — sync wrapper around async edge-tts
- 3000 char limit on input text

### 7. Analytics Engine (inline)
- `TrafficAnalytics` class — computed from loaded replay data
- `POST /load` loads a `.json.gz` replay file
- All analytics endpoints return responses under 8 KiB

## Security

- **Startup validation**: Fails fast if any required env vars missing
- **SSRF protection**: `_is_safe_url()` blocks private/internal IPs on frame capture
- **Input validation**: `lat`/`lon`/`limit` parsing catches ValueError
- **Agent ID masked**: Shows first 8 chars only in logs

## Related
- [[Voice Agent Config]]
- [[Voice Agent Endpoints]]
- [[Analytics API]]
- [[REST API Endpoints]]
