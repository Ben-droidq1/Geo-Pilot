# Kinematics Smoother

> `trafficlab/motion/kinematics.py` (167 lines)

## Class: `TrackSmoother`

Per-track stateful smoother for heading and speed using Exponential Moving Average (EMA).

### Constructor
```python
TrackSmoother(config: dict)
```
Config keys consumed:
- `heading_ema.alpha_min` (default 0.05)
- `heading_ema.alpha_max` (default 0.6)
- `heading_ema.speed_ref` (default 5.0 km/h)
- `heading_min_speed_for_update` (default 0.1 km/h)
- `heading_max_jump` (default 5°)
- `heading_sat_coords_jitter_radius` (default 0.6m)
- `heading_sat_coords_jitter_frames` (default 8)
- `speed_ema_alpha` (default 0.4)

### `update()` Method
```python
update(current_sat_pos, dt, px_per_m, svg_heading=None) -> dict
```

Returns:
```python
{
    "speed_kmh": float,
    "heading": float | None,
    "default_heading": bool
}
```

### Processing Pipeline
1. **Physics gate**: If instantaneous speed > 200 km/h → reject update
2. **Position history**: Append to deque (max 8)
3. **Jitter check**: If recent positions within radius → suppress heading update
4. **Raw speed**: `(distance_m / dt) * 3.6`
5. **Regression heading**: `cv2.fitLine` on position history (min 3 points, min 2px movement)
6. **Speed EMA**: `alpha * raw + (1-alpha) * prev`
7. **Heading EMA**: Adaptive alpha based on speed ratio
8. **SVG snapping**: If heading within 15° of SVG → blend toward SVG
9. **Max jump clamp**: Limit heading change to ±5° per update

### Adaptive Alpha Formula
```python
speed_ms = speed_kmh / 3.6
ratio = min(1.0, speed_ms / speed_ref)
alpha = alpha_min + (alpha_max - alpha_min) * ratio
```
Fast objects → higher alpha → more responsive heading. Slow objects → lower alpha → smoother heading.

## Bugs in This File

| # | Severity | Issue |
|---|---|---|
| 1 | LOW | `cosine_reject_counter` initialized but never used (dead state) |
| 2 | LOW | `reg_win = 8` hardcoded instead of read from config |
| 3 | LOW | `vel_alpha = 0.25` hardcoded and not configurable |
| 4 | LOW | Jitter check uses bounding box range, not path length |

## Related
- [[Inference Pipeline]]
- [[Calibration Stages]]
