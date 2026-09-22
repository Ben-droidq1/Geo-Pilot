# Voice Agent Server — Endpoints

> HTTP endpoints on port 8789 (`voice_agent_server.py`)

## Voice Agent Endpoints

### `GET /api/health`
Health check endpoint.
- Returns: `{"status": "ok"}`

### `GET /api/voice-token`
Mints an AssemblyAI v3 streaming token (300s TTL).
- Returns: `{"token": "...", "expires_in_seconds": 300}`
- Requires: `ASSEMBLYAI_API_KEY` env var
- Uses `GET https://streaming.assemblyai.com/v3/token` internally

### `GET /api/agent-id`
Returns the AssemblyAI agent ID.
- Returns: `{"agent_id": "agent_..."}`

### `GET /api/capture?url=<hls_url>`
Captures a single frame from an HLS stream.
- Tries OpenCV first, falls back to ffmpeg for HLS streams
- Returns: `{"success": true, "frame": "<base64_jpeg>"}`
- Cache: `FRAME_CACHE_TTL`-second TTL per URL (default 5s)
- Resizes to max 720p
- SSRF protection: blocks private/internal IPs

### `GET /api/tts?text=<text>`
Text-to-speech via edge-tts.
- Returns: `audio/mpeg` binary
- Voice: configurable via `TTS_VOICE` env var (default `en-US-GuyNeural`)
- Limit: 3000 characters

### `GET /api/search-cameras?q=<query>&lat=<lat>&lon=<lon>&limit=<n>`
Content-aware camera search.
- **Text search**: matches name, city, country, source type
- **Country mapping**: "United States" → "us", "South Korea" → "kr"
- **Content keywords**: "beach" → surf-cams, "mountain" → ski-cams, "airport" → airport-webcams
- **Proximity**: haversine distance within `radius_km` (default 50)
- Sorts: live cameras first, then by distance
- Returns: `{"cameras": [...], "total": N}`

### `GET /api/agent-events`
SSE (Server-Sent Events) stream for agent commands.
- Events: `agent_add_cameras`, `agent_jump_to`, `agent_thinking`, `agent_cameras_found`
- Keepalive: 30-second `: keepalive` comments
- Auto-cleanup on disconnect

### `GET /api/proxy?url=<target_url>`
CORS proxy for external APIs.
- SSRF protection: blocks private/internal IPs
- Forwards Range/Accept headers
- Returns: proxied response with CORS headers

## Voice Tool Endpoints (AssemblyAI calls these via GET)

### `GET /api/tool/search-cameras?q=<query>&lat=<lat>&lon=<lon>&limit=<n>`
Tool: Search cameras by location. Returns compact format for voice agent.
- Returns: `{"cameras": [{"name", "city", "country", "lat", "lon", "live", "stream"}], "total": N}`

### `GET /api/tool/analyze-cameras?camera_urls=<csv>&question=<text>`
Tool: Capture and analyze multiple cameras in one call.
- `camera_urls`: comma-separated HLS stream URLs
- `question`: what to analyze (default: "Describe what you see")
- Returns: `{"answer": "...", "camera_count": N}`
- Timeout: 45 seconds

### `GET /api/tool/capture-frame?url=<hls_url>`
Tool: Capture a single frame from a camera.
- Returns: `{"success": true, "frame": "<base64_jpeg>", "url": "..."}`

## Analytics Endpoints (voice agent tool calls)

### `GET /vehicle-count`
Returns unique vehicle counts by class.
- Returns: `{"count": N, "by_class": {"car": N, "truck": N, ...}}`

### `GET /speed-stats`
Returns average/min/max/median speed in km/h.
- Returns: `{"avg": N, "min": N, "max": N, "median": N}`

### `GET /summary`
Returns full scene summary.
- Returns: `{"location_code": "...", "frame_count": N, "total_vehicles": N, "classes": {...}, "avg_speed": N}`

### `GET /peak-hours?top_n=5`
Returns frames with highest vehicle density.
- Returns: `{"peaks": [{"frame": N, "count": N}, ...]}`

### `GET /turning-patterns`
Returns heading distribution in 4 cardinal directions.
- Returns: `{"north": N, "east": N, "south": N, "west": N}`

### `GET /flow-rate`
Returns vehicles per minute.
- Returns: `{"avg_per_minute": N, "peak_per_minute": N}`

### `GET /object/{frame_idx}`
Returns all objects at a specific frame index.
- Returns: `{"objects": [{"id", "tracked_id", "class", "confidence", "speed_kmh", "heading"}, ...]}`

### `POST /load`
Loads a replay `.json.gz` file into memory.
- Body: `{"path": "path/to/replay.json.gz"}`
- Returns: `{"frame_count": N, "total_objects": N}`

## POST Endpoints

### `POST /api/chat`
Smart chat with auto camera discovery and content-aware search.
- Body: `{"message": "...", "context": "...", "camera_ids": [...], "max_cameras": 5, "radius_km": 100}`
- Flow:
  1. If `camera_ids` provided → capture frames concurrently
  2. If camera-related keywords detected → auto-discover cameras via text search
  3. Location extraction via Qwen LLM + regex fallback
  4. Content-based search: "beach" finds surf-cams, "mountain" finds ski-cams
  5. Fast text-only path for greetings (no vision API)
  6. Concurrent frame capture from all discovered cameras
  7. Analyze with Qwen VL (with camera metadata context)
- Returns: `{"answer": "...", "camera_count": N, "camera_info": [...]}`

## CORS
All endpoints include `Access-Control-Allow-Origin: *`.

## Related
- [[Voice Agent Server]]
- [[REST API Endpoints]]
