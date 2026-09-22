# Voice Agent Server — Weaknesses

> Security and code quality issues in `voice_agent_server.py`.

## 🔴 HIGH — Security

### 1. ~~Hardcoded API Key in Source Code~~ ✅ FIXED
**Line**: 43
**Status**: Fallback removed. Now requires `QWEN_API_KEY` env var. Startup validation fails if missing.

### 2. ~~Hardcoded Agent ID in Source Code~~ ✅ FIXED
**Line**: 46
**Status**: Fallback removed. Now requires `GEOPILOT_AGENT_ID` env var. Startup validation fails if missing.

### 3. Wildcard CORS on All Endpoints
**Line**: 486
**Risk**: `Access-Control-Allow-Origin: *` on all endpoints. Any website can mint tokens, capture frames, and consume API credits.
**Status**: NOT FIXED — acceptable for local dev, would need restriction for production.

### 4. No Authentication on Any Endpoint
**Risk**: Anyone on the network can:
- Mint AssemblyAI tokens
- Capture frames from HLS streams
- Run vision analysis (costing API credits)
- Search camera database
- Load replay data
**Status**: PARTIALLY FIXED — startup validation now requires all env vars. No runtime auth yet.

## 🟡 MEDIUM

### 5. ~~Arbitrary URL Frame Capture~~ ✅ FIXED
**Endpoint**: `GET /api/capture?url=<url>`
**Status**: SSRF protection added. Blocks private/internal IPs (10.x, 192.168.x, 172.16.x, 169.254.x, fc00::). Allows localhost for dev.

### 6. Arbitrary Camera Analysis
**Endpoint**: `POST /api/analyze`
**Risk**: Attacker can analyze any camera URL, consuming Qwen VL API credits.

### 7. ~~`time.sleep(1)` in Request Handler~~ ✅ FIXED
**Line**: 663
**Status**: Removed. No more blocking in the HTTP handler.

### 8. No Rate Limiting
**Risk**: No limits on:
- Token minting (AssemblyAI rate limits apply server-side)
- Frame capture (could flood HLS sources)
- Vision analysis (API credit drain)
- TTS generation (edge-tts abuse)

## 🟠 LOW

### 9. ~~`frame_cache` Never Evicts~~ ⚠️ PARTIALLY FIXED
**Line**: 58
**Status**: `frame_cache` was previously referenced but never defined (NameError) — ✅ FIXED, defined at line 58. TTL-based eviction added via `FRAME_CACHE_TTL`. But old entries are only evicted on access, not proactively.

### 10. Async Event Loop Created Per TTS Call
**Line**: 467
```python
loop = asyncio.new_event_loop()
```
**Risk**: Creates and destroys an event loop for every TTS request. Should use a persistent loop.

### 11. ~~No Input Validation on `search-cameras`~~ ✅ FIXED
**Line**: 548-550
**Status**: `lat`/`lon`/`limit` parsing now wrapped in try/except with 400 response on ValueError.

### 12. Thread Safety of `frame_cache`
**Risk**: `frame_cache` is a plain dict accessed from multiple threads (HTTP handler threads + concurrent frame capture). No locking — race conditions possible.

### 13. `capture_multiple_frames` Silently Drops Timeouts
**Line**: 410
**Risk**: `concurrent.futures.wait(futures, timeout=15)` returns even if futures aren't done. The results list may contain `None` entries for timed-out captures. Currently handled by filtering `None` at the end, but partial failures are invisible.

## Related
- [[Security Issues]]
- [[Voice Agent Server]]
