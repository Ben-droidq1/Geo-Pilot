# Dead Code

> Unused imports, variables, functions, and unreachable code.

## ✅ Resolved (dead code cleanup)

| File | Item | Resolution |
|---|---|---|
| `tab_visualization.py` | `sys`, `hashlib`, `re`, `xml.etree.ElementTree`, `QLineF`, `QGraphicsLineItem`, `QGraphicsEllipseItem` | Removed |
| `main_window.py` | `os`, `sys`, `QTextBrowser`, `QHBoxLayout` | Removed |
| `tab_inference.py` | `QSize`, duplicate `QComboBox` import | Removed |
| `g_projection.py` | `import math` | Removed |
| `g_projection.py:163` | Duplicate `return` in `sat_floor_to_cctv_3d` | Removed — single return remains |
| `lens_stage.py` | `_apply_matrix_to_inspect` defined but never connected | Removed |
| `video_player.py` | `read_frame()`, `frame_count()`, `fps()`, `resolution()` | Removed; `release()` kept and now called in `tab_visualization.setup_video` |
| `voice_agent_server.py` | `frame_cache` referenced but never defined (NameError) | Fixed — added `frame_cache = {}` at module scope |

## Unused Imports

| File | Unused Imports |
|---|---|
| `argus_bridge.py` | `shutil` |
| `upgrade_g_projection.py` | `copy` |

## Unused Variables / Attributes

| File | Variable | Line |
|---|---|---|
| `kinematics.py` | `cosine_reject_counter` | 27 |
| `inference_session.py` | `sig_status` signal | 9 |
| `tab_location.py` | `kind` parameter in `_ensure_png` | 191 |
| `views.py` | `parent_inspector` attribute | 28 |
| `argus_bridge.py` | `_ARGUS_PUBLIC` | Module level |

## Unreachable Code

| File | Line | Description |
|---|---|---|
| `lens_stage.py` | N/A | ~~`_apply_matrix_to_inspect` defined but never connected~~ ✅ REMOVED |
| `tab_calibration.py` | 277-278 | `while len(stage_widgets) < len(STEPS)` always false |

## Dead State / Placeholders

| File | Item | Description |
|---|---|---|
| `kinematics.py:27` | `cosine_reject_counter` | Initialized to 0, never modified |
| `inference_session.py:9` | `sig_status` | Declared, never emitted |
| `views.py:28` | `parent_inspector` | Set to None, never read |
| `analytics/api.py` | `_meta` | Set but never read |

## Commented-Out Code

| File | Line | Description |
|---|---|---|
| `tab_visualization.py` | 443-448 | Debug print statements |
| `tab_inference.py` | 624 | `self.on_lock_clicked()` commented out in `finish_batch` |

## Duplicate Code

| Pattern | Files |
|---|---|
| `RightClickImageViewer` class | `homa_stage.py`, `val2_stage.py`, `pars_stage.py`, `val3_stage.py` |
| `_cv_to_qimage` / `_qimage_to_cv` helpers | 6+ calibration stages |
| `_draw_marker` helper | `val1_stage.py`, `val2_stage.py`, `val3_stage.py`, `final_stage.py` |
| `TrafficAnalytics` class | `analytics/engine.py`, `analytics/api.py` |

## Related
- [[Code Smells]]
- [[Critical Bugs]]
