# Sat Renderer

> `trafficlab/visualization/sat_renderer.py` (143 lines)

## Class: `SatRenderer`

Cached QImage buffer — reused across frames for performance.

### `render()` Method
```python
render(objects, scene_w, scene_h, *,
       show_tracking=True, sat_box_thick=2, show_sat_box=True,
       show_sat_arrow=False, show_sat_coords_dot=False,
       sat_use_svg=True, show_3d=True, show_sat_label=False,
       sat_label_size=12, text_color_mode="White",
       speed_display_cache=None, speed_update_delay_frames=30,
       current_frame_idx=0) → QPixmap
```

Renders per-frame satellite overlays:
1. **Floor box**: Rotated polygon (requires heading + measurements)
2. **Heading arrow**: 40px yellow line from center (if not default heading)
3. **Coordinate dot**: Colored circle at satellite coords
4. **Speed label**: "car 42.3km/h" text

### Speed Display Cache
Dict keyed by track_id with `{val, last_frame}`. Updates every `speed_update_delay_frames` frames for smooth display.

## Bugs
1. Heading arrow hardcoded 40px — doesn't scale with scene resolution
2. `coord` fallback to `"sat_coord"` (typo compat) — falsy values trigger fallback incorrectly
3. No `try/finally` around `QPainter` — exception leaks painter state
4. Speed label drawn at object coordinate — clips at scene edges

## Related
- [[CCTV Renderer]]
- [[Tab Visualization]]
