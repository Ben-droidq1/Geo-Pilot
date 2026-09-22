# SVG Parser (Projection)

> `trafficlab/projection/svg_parser.py` (119 lines)

## Class: `SVGParser`

Parses SVG road orientation guidelines for heading snapping.

### `get_nearest_heading(pt)` → float | None
Finds the nearest SVG segment to a satellite point and returns its angle in degrees [0, 360).

### Supported SVG Elements
- `<line>` → line segment
- `<polygon>` / `<polyline>` → series of segments
- `<g>` with `id="Guidelines"` or `id="Physical"` → target groups

### Supported Transforms
- `translate(tx, ty)`
- `rotate(angle)` and `rotate(angle, cx, cy)`
- `matrix(a, b, c, d, e, f)`

### NOT Supported
- `scale()`, `skewX()`, `skewY()` — silently ignored

## Bugs
1. `get_nearest_heading` is O(n) per call — slow with many segments
2. Only finds `Guidelines` and `Physical` groups — other IDs ignored
3. Silent parse errors — `except Exception: print()`

## Related
- [[G-Projection Engine]]
- [[Inference Pipeline]]
