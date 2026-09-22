# CCTV Renderer

> `trafficlab/visualization/cctv_renderer.py` (125 lines)

## Module-Level Function

### `get_color_from_string(s)` → QColor
MD5 hash of string → deterministic color. LRU-cached (512 entries).

## Class: `CCTRenderer`

### `render()` Method
```python
render(frame, objects, show_tracking=True, show_3d=True,
       box_thickness=2, face_opacity=50, show_label=True) → QPixmap
```

Renders detection overlays on a BGR frame:
1. Convert numpy BGR → QImage → QPixmap
2. For each object:
   - Deterministic color from class+track_id
   - **3D mode**: Draw 6-face wireframe polygon (if heading + measurements + valid 8-point bbox)
   - **2D mode**: Draw flat bbox rectangle + reference point dot + label
3. Return painted QPixmap

### 3D Face Indices
```python
faces = [
    [0, 1, 2, 3],  # Bottom
    [4, 5, 6, 7],  # Top
    [0, 1, 5, 4],  # Front
    [1, 2, 6, 5],  # Right
    [2, 3, 7, 6],  # Back
    [3, 0, 4, 7],  # Left
]
```

## Bugs
1. `fm.width(lbl)` deprecated in Qt6 — use `horizontalAdvance()`
2. `except Exception: pass` on 3D rendering — silent failure
3. `frame.data` lifetime issue — QImage wraps numpy buffer without copy (safe in practice but fragile)

## Related
- [[Tab Visualization]]
- [[Sat Renderer]]
