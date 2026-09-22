# Calibration Stages

> 13 stages in `trafficlab/gui/tabs/calibration_stage/`

## Stage Overview

```
Pick (0) → Lens (1) → Undistort (2) → Val1 (3) → HomA (4) → HomF (5)
  → Val2 (6) → Pars (7) → Dist (8) → Val3 (9) → SVG (10) → ROI (11) → Final (12) → Save (13)
```

| Stage | File | Lines | Purpose |
|---|---|---|---|
| 0 | `pick_stage.py` | 615 | Location selection, construct/reconstruct config |
| 1 | `lens_stage.py` | 444 | Camera intrinsic matrix K editor |
| 2 | `undistort_stage.py` | 800 | Distortion coefficients D (k1,k2,k3,p1,p2) |
| 3 | `val1_stage.py` | 287 | Side-by-side original vs undistorted |
| 4 | `homa_stage.py` | 397 | Homography anchor point pairs |
| 5 | `homf_stage.py` | 306 | Homography FOV polygon visualization |
| 6 | `val2_stage.py` | 278 | CCTV click → satellite projection test |
| 7 | `pars_stage.py` | 366 | Camera position via parallax triangulation |
| 8 | `dist_stage.py` | 259 | Pixel-to-meter scale from anchor distance |
| 9 | `val3_stage.py` | 364 | Full parallax + projection verification |
| 10 | `svg_stage.py` | 466 | SVG road alignment to satellite points |
| 11 | `roi_stage.py` | 334 | ROI mask configuration and validation |
| 12 | `final_stage.py` | 926 | 3D box reconstruction with all params |
| 13 | (in `tab_calibration.py`) | — | Save G_projection JSON |

## Common Patterns

### Inspect Object Pattern
All stages access a shared `inspect_obj` dict through the host `CalibrationTab`:
```python
host = self.parent()  # CalibrationTab
obj = host.inspect_obj  # Shared state dict
```

### QImage/OpenCV Conversion
Most stages have these helper methods:
```python
def _cv_to_qimage(self, cv_bgr):
    # OpenCV BGR → QImage RGB

def _qimage_to_cv(self, qimg):
    # QImage → OpenCV BGR
```

### RightClickImageViewer
Duplicated in 4 files (`homa_stage.py`, `val2_stage.py`, `pars_stage.py`, `val3_stage.py`):
- Right-click emits `clicked(x, y)` signal
- Left-click pans

## Bugs Across All Stages

| # | Severity | Stage | Issue |
|---|---|---|---|
| 1 | HIGH | val1 | `self.info` attribute referenced but not defined |
| 2 | HIGH | val1 | `left_view.clicked` reconnected every `showEvent` — duplicate markers |
| 3 | HIGH | roi/final | ROI threshold inconsistency: `> 0` vs `> 128` vs `< 10` |
| 4 | MEDIUM | undistort | `self._ranges` accessed before initialization |
| 5 | MEDIUM | homf/pars | `K = np.array(None)` crash when config missing |
| 6 | MEDIUM | val3 | `factor = 10.0` arbitrary fallback when z_cam = h_obj |
| 7 | MEDIUM | final | `factor = 100.0` arbitrary fallback when z_cam = h_obj |
| 8 | LOW | lens | `_apply_matrix_to_inspect` dead code — ✅ REMOVED |
| 9 | LOW | homa | `QMessageBox.msgbox` as class attribute |
| 10 | ALL | ALL | Bare `except:` / `except: pass` everywhere |

## Related
- [[Tab Calibration]]
- [[G-Projection Engine]]
- [[TrafficLab Config]]
- [[Critical Bugs]]
