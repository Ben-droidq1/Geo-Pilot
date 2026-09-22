# Security Issues

> Secrets, exposure, and injection risks.

## 🔴 HIGH

### 1. API Server Binds to 0.0.0.0
**File**: `analytics_server.py:27`
**Risk**: The FastAPI server binds to all network interfaces by default. If ngrok is not running, the analytics API is publicly accessible on the local network.
**Mitigation**: Bind to `127.0.0.1` by default, add `--host 0.0.0.0` flag.

### 2. Hardcoded Agent ID
**File**: `voice_demo/server.py:61`
**Risk**: `AGENT_ID = "agent_f0ebe1f5c40a40cf9341db3b95b56ee4"` is a real AssemblyAI agent ID committed to source.
**Mitigation**: Read from `.env` only.

### 3. `.env` File Not Gitignored Properly
**File**: `.gitignore`
**Risk**: `.env` is gitignored, but `.env.example` is not. If someone fills in `.env.example` and commits it, secrets are exposed.
**Mitigation**: Add comment in `.env.example` warning against committing filled-in values.

## 🟡 MEDIUM

### 4. Authorization Header Format
**Files**: `setup_voice_agent.py`, `voice_demo/server.py`
**Risk**: AssemblyAI API called with `"Authorization": key` instead of `"Authorization": Bearer <key>"`. May fail depending on API version.

### 5. No CORS Configuration on FastAPI
**File**: `analytics/api.py`
**Risk**: Default FastAPI has no CORS headers. Browser requests from other origins will be blocked. If a proxy is added later, it could expose the API.

### 6. `sys.path.insert` at Module Level
**File**: `argus_bridge.py:12`
**Risk**: Modifies global Python path on import. Could shadow other modules or cause unexpected import resolution.

### 7. SQL Injection Risk — Mitigated
**File**: `argus_bridge.py`
**Risk**: SQL queries use parameterized queries (`?` placeholders). This is correct and safe. However, the `source` and `country` parameters come from user input and are used in LIKE clauses.

## 🟢 LOW

### 8. No Input Validation on API Endpoints
**File**: `analytics/api.py`
**Risk**: The `/load` endpoint accepts arbitrary file paths. A malicious request could read any JSON file on the system.

### 9. No HTTPS on Voice Demo Server
**File**: `voice_demo/server.py`
**Risk**: Plain HTTP server on port 8788. Fine for local dev but tokens are sent in cleartext.

## 🔴 CRITICAL — Voice Agent Server (PR #8)

### 10. Hardcoded API Key in Source Code
**File**: `voice_agent_server.py:43`
**Risk**: Real Qwen VL API key `sk-bmfag2ajstlu73gsf6jin5khya177ce9` committed to git. Even with `.env` override, the key is in git history.
**Fix**: Remove the fallback string entirely.

### 11. Hardcoded Agent ID in Source Code
**File**: `voice_agent_server.py:46`
**Risk**: Real AssemblyAI agent ID committed to git.

### 12. Wildcard CORS on All Voice Endpoints
**File**: `voice_agent_server.py:486`
**Risk**: `Access-Control-Allow-Origin: *` on all endpoints. Any website can mint tokens, capture frames, and consume API credits.

### 13. No Authentication on Any Voice Endpoint
**File**: `voice_agent_server.py`
**Risk**: Anyone on the network can mint AssemblyAI tokens, capture HLS frames, run vision analysis (costing money), and generate TTS.

### 14. SSRF via Frame Capture
**Endpoint**: `GET /api/capture?url=<url>`
**Risk**: Attacker can capture frames from any URL reachable by the server (internal networks, localhost services).
**Mitigation**: Validate URL scheme, block internal IPs.

## Related
- [[REST API Endpoints]]
- [[Voice Agent Endpoints]]
- [[Voice Agent Server]]
- [[Analytics API]]
- [[Voice Agent Config]]
