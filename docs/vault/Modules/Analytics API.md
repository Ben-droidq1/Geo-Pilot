# Analytics API

> `trafficlab/analytics/api.py` (360 lines)

## FastAPI REST API

Runs on port 8787 via `analytics_server.py`.

### Global State
- `_analytics`: Currently loaded `TrafficAnalytics` instance (single-tenant)
- `_meta`: Metadata dict (set but never read)
- `MAX_RESPONSE_BYTES = 8192` — AssemblyAI response ceiling

### Duplicate `TrafficAnalytics` Class
**This file defines its own `TrafficAnalytics` class** separate from `engine.py`. They differ:
- `api.py`: Averages ALL speed samples directly
- `engine.py`: Averages per-vehicle means
- Result: Different avg speed values (e.g., 21.1 vs 25.0)

## Related
- [[Analytics Engine]]
- [[REST API Endpoints]]
- [[Voice Agent Config]]
