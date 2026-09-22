# Voice Agent Config

> `trafficlab/voice/agent_config.py` (229 lines)

## Functions

### `validate_api_base_url(url)` → bool
Checks: HTTPS, not localhost, not `REPLACE-WITH-NGROK-URL`.

### `resolve_api_base_url(api_base_url=None)` → str
Priority: argument → `GEOPILOT_API_URL` env var → raises error.

### `build_tools(api_base_url, frame_url_mode)` → list
Builds 7 AssemblyAI HTTP tool definitions:

| Tool | Endpoint | Timeout |
|---|---|---|
| `vehicle_count` | `GET /vehicle-count` | 15s |
| `speed_stats` | `GET /speed-stats` | 15s |
| `summary` | `GET /summary` | 20s |
| `peak_hours` | `GET /peak-hours` | 15s |
| `turning_patterns` | `GET /turning-patterns` | 15s |
| `flow_rate` | `GET /flow-rate` | 15s |
| `objects_at_frame` | `GET /object/{frame_idx}` | 15s |

### `build_agent_config(...)` → dict
Full AssemblyAI agent configuration with:
- Agent name: "GeoPilot Traffic Analyst"
- Voice: "alba"
- Greeting: "GeoPilot online. Ask me about the traffic scene."
- 8 keyterms for speech recognition

## Related
- [[Analytics API]]
- [[REST API Endpoints]]
