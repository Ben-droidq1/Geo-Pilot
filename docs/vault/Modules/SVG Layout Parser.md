# SVG Layout Parser

> `trafficlab/visualization/svg_parser.py` (215 lines)

## Class: `SVGLayoutParser`

Parses SVG layout files into Qt graphics items for satellite view rendering.

### Layers Parsed
| Layer | Contents |
|---|---|
| `Background` | Background shapes |
| `Aesthetic` | Decorative elements |
| `Guidelines` | Road orientation lines |
| `Physical` | Road/pavement polygons |
| `Anchors` | Reference markers |

### Output
`layer_items` dict: `{layer_name: [QGraphicsLineItem, QGraphicsPolygonItem, ...]}`

### CSS Handling
- Reads `<style>` element from SVG
- Merges with hardcoded `cls-1` through `cls-7` defaults
- Inline `style=""` overrides class, direct attributes override both

## Bugs
1. `<path>` elements NOT supported — most common SVG element silently ignored
2. `<circle>`, `<ellipse>` NOT supported
3. No `<g>` recursion — nested groups within layers are missed
4. Multiple `except Exception: pass` — silent failure
5. Operator precedence ambiguity in `_parse_transform_str` translate

## Related
- [[Tab Visualization]]
- [[Calibration Stages]]
