# Analytics Engine

> `trafficlab/analytics/engine.py` (385 lines)

## Class: `TrafficAnalytics`

Pure-computation analytics engine. No I/O — operates on in-memory replay data.

### Constructor
```python
TrafficAnalytics(replay_data: dict)
```
Builds pre-computed indices on init.

### Methods

| Method | Returns | Description |
|---|---|---|
| `vehicle_count(class_filter)` | `int` | Unique tracked vehicles |
| `detection_count(class_filter)` | `int` | Total object appearances |
| `vehicle_count_by_class()` | `dict` | Class → count |
| `speed_stats(class_filter)` | `dict` | avg/min/max/median/p95 |
| `speed_distribution(buckets)` | `list` | Speed histogram buckets |
| `peak_frames(top_n)` | `list` | Frames with most objects |
| `heading_distribution()` | `dict` | 8-way compass distribution |
| `traffic_flow_rate()` | `dict` | Vehicles per time window |
| `full_summary()` | `dict` | Everything combined |
| `query(question_parsed)` | `dict` | Intent-routed query |

### Intent Routing
Maps natural-language-like intents to methods:
- `VEHICLE_COUNT`, `COUNT`, `HOW_MANY` → `vehicle_count`
- `SPEED`, `SPEED_STATS` → `speed_stats`
- `PEAK`, `BUSIEST` → `peak_frames`
- `HEADING`, `DIRECTION` → `heading_distribution`
- `FLOW`, `FLOW_RATE` → `traffic_flow_rate`
- `SUMMARY`, `ALL` → `full_summary`

### Compass Labels
- 8-way: N, NE, E, SE, S, SW, W, NW (22.5° segments)
- 4-way: N, E, S, W (quadrants)

## Potential Issues
1. `_match_class` uses substring match — "car" matches "scar"
2. `_is_valid` truthiness check excludes "false"/"False" strings
3. Operator precedence in heading availability check (intentional but confusing)

## Related
- [[Analytics API]]
- [[REST API Endpoints]]
