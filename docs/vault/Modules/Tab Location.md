# Tab Location

> `trafficlab/gui/tabs/tab_location.py` (363 lines)

## Class: `LocationTab(QWidget)`

Creates and manages location folders with CCTV/satellite imagery.

### Workflow
1. Select or create a location code
2. Pick CCTV image (PNG/JPG)
3. Pick satellite image (PNG/JPG)
4. Pick layout SVG (optional)
5. Pick ROI mask (optional)
6. Click "Create" → creates `location/<code>/` with all files

### File Naming Convention
```
location/<code>/
  cctv_<code>.png
  sat_<code>.png
  layout_<code>.svg    (optional)
  roi_<code>.png       (optional)
```

### Qt Connections
| Signal | Slot |
|---|---|
| `btn_pick_cctv.clicked` | `pick_cctv()` |
| `btn_pick_sat.clicked` | `pick_sat()` |
| `btn_pick_layout.clicked` | `pick_layout()` |
| `btn_pick_roi.clicked` | `pick_roi()` |
| `btn_create.clicked` | `create_location()` |
| `btn_refresh_locations.clicked` | `_populate_location_combo()` |
| `btn_add_footage.clicked` | `add_footage()` |

### `add_footage()` Flow
1. Pick MP4 video file
2. Copy to `location/<code>/footage/` directory
3. Log success/failure to console

## Bugs
1. `os.getcwd()` used everywhere — breaks if CWD differs
2. Bare `except Exception: pass` on image loading — silent errors
3. `_ensure_png` has unused `kind` parameter
4. Variable `h4` shadowed/reused

## Related
- [[Main Window]]
- [[Argus Bridge]]
