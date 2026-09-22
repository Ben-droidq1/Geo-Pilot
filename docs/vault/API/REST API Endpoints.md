# REST API Endpoints

> FastAPI server on port 8787 (`analytics_server.py` → `analytics/api.py`)
>
> **Note**: These analytics endpoints are now also available on the voice agent server (port 8789). The separate `analytics_server.py` is kept for backward compatibility but is no longer required.

## Base URL
```
http://localhost:8787  (legacy FastAPI)
http://localhost:8789  (voice agent server — same endpoints)
```

## Endpoints

### `GET /health`
Returns: `{"status": "ok"}`

### `POST /load`
Body: `{"path": "path/to/replay.json.gz"}`
Loads a replay file into memory. Must be called before other endpoints.

Returns: `{"status": "loaded", "meta": {...}, "frame_count": N}`

### `GET /summary`
Returns full analytics summary (speed stats, counts, heading distribution, flow rate).

### `GET /vehicle-count`
Returns unique vehicle counts by class.

### `GET /speed-stats`
Returns average/min/max/median speed.

### `GET /peak-hours`
Returns frames with highest vehicle density.

### `GET /turning-patterns`
Returns heading distribution in 4 cardinal directions.

### `GET /flow-rate`
Returns vehicles per time window.

### `GET /object/{frame_idx}`
Returns all objects at a specific frame index.

## Response Limit
All responses are truncated to 8 KiB (`MAX_RESPONSE_BYTES`) for AssemblyAI compatibility.

## Usage
The voice agent server (`voice_agent_server.py`) now includes a `TrafficAnalytics` class and serves all these endpoints directly. You no longer need to run `analytics_server.py` separately.

```bash
# One command — everything runs
python main.py
```

## Related
- [[Analytics API]]
- [[Analytics Engine]]
- [[Voice Agent Config]]
- [[Voice Agent Server]]
