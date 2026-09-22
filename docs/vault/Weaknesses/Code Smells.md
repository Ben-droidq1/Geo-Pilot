# Code Smells

> Design issues and anti-patterns.

## 1. `os.getcwd()` Used Everywhere
**Files**: `tab_location.py`, `tab_inference.py`, `tab_visualization.py`, `tab_welcome.py`

All relative paths resolve from the current working directory. If the app is launched from `~/Documents` instead of the project root, every path breaks.

**Fix**: Use a project root constant:
```python
PROJECT_ROOT = Path(__file__).parent.parent.parent
```

## 2. Bare `except:` / `except: pass` Everywhere
**Files**: ALL calibration stages, `tab_visualization.py`, `tab_location.py`, `cctv_renderer.py`

At least 50+ bare exception handlers across the codebase. These silently swallow errors, making debugging nearly impossible.

**Examples**:
- `tab_visualization.py:417` — `except: pass` on directory creation
- `tab_visualization.py:492` — `traceback.print_exc()` left in production
- `pick_stage.py` — 15+ bare excepts
- All calibration stage `showEvent` methods

## 3. Duplicate `TrafficAnalytics` Class
**Files**: `analytics/engine.py`, `analytics/api.py`

Two different implementations of the same class with different averaging logic. This produces different results for the same data (e.g., avg speed 21.1 vs 25.0).

## 4. `RightClickImageViewer` Duplicated 4 Times
**Files**: `homa_stage.py`, `val2_stage.py`, `pars_stage.py`, `val3_stage.py`

Identical class copy-pasted in each file. Should be in a shared `views.py` or `calibration_stage/views.py`.

## 5. Signal Connections in `showEvent`
**Files**: `val1_stage.py` (and potentially others)

Connecting Qt signals in `showEvent` means they accumulate every time the widget is shown. This causes the slot to fire multiple times per event.

## 6. Unused Imports
**File**: `tab_visualization.py`

~~`sys`, `hashlib`, `re`, `xml.etree.ElementTree`, `QLineF`, `QGraphicsLineItem`, `QGraphicsEllipseItem` — all imported but never used.~~ ✅ RESOLVED during dead code cleanup (see [[Dead Code]]).

## 7. Orphaned Stage Widgets
**File**: `tab_calibration.py`

All stages created with `project_root=None, parent=None`. Qt may not manage their lifecycle correctly without a parent.

## 8. `sig_status` Signal Never Emitted
**File**: `inference_session.py`

Declared but never emitted or connected. Dead code.

## 9. Zoom Factor Inconsistency
**File**: `views.py`

Module-level `_ZOOM_IN = 1.15` but `MediaViewer` uses `1.25`. Different zoom feel across views.

## 10. Tab Indentation in Python
**File**: `trafficlab_config.py`

Uses tabs while the rest of the project uses spaces. Mixing will cause `IndentationError` if ever combined.

## Related
- [[Critical Bugs]]
- [[Dead Code]]
- [[Performance Issues]]
