# Data Flow Pipeline

## End-to-End Flow

```
MP4 Video / RTSP Stream
    │
    ▼
┌─────────────────────────────────────────┐
│  pipeline.py (InferencePipeline.run)     │
│                                         │
│  1. Load YAML config (multi-config)     │
│  2. Load G-Projection JSON (optional)   │
│  3. Load prior dimensions (JSON)        │
│  4. Init YOLO model (Ultralytics)       │
│  5. Init ROI mask (optional)            │
│  6. Frame loop:                         │
│     a. YOLO detect + ByteTrack         │
│     b. ROI filter (optional)            │
│     c. CCTV→SAT projection              │
│     d. Kinematics smoothing             │
│     e. 3D box lifting                   │
│     f. Append to output                 │
│  7. Write gzipped JSON                  │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  replay_writer.py                       │
│  Writes: output/<model>/<config>/       │
│          <location>/<video>.json.gz      │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  replay_loader.py                       │
│  Reads: .json.gz or .json               │
└─────────────────────────────────────────┘
    │
    ├──────────────────────┐
    ▼                      ▼
┌──────────────┐  ┌──────────────────┐
│ CCTV Renderer│  │  Sat Renderer    │
│ (2D/3D bbox) │  │ (floor/arrow/    │
│              │  │  speed/scale)    │
└──────────────┘  └──────────────────┘
    │                      │
    ▼                      ▼
┌─────────────────────────────────────────┐
│  tab_visualization.py                   │
│  Side-by-side CCTV + SAT playback       │
└─────────────────────────────────────────┘
```

## Sub-Pipelines

### Projection Pipeline (g_projection.py)
```
CCTV pixel (u, v)
  → undistortPoints (K, D) → undistorted pixel (u_u, v_u)
  → perspectiveTransform (H) → apparent satellite (x, y)
  → parallax_correct (z_cam, h) → real satellite (x_real, y_real)
```

### Inverse Projection
```
Satellite (x, y, h)
  → parallax_project (z_cam, h) → apparent ground (x_app, y_app)
  → perspectiveTransform (H⁻¹) → undistorted pixel (u_u, v_u)
  → projectPoints (K, D) → CCTV pixel (u, v)
```

### Kinematics Pipeline (kinematics.py)
```
sat_coords[t] + dt + px_per_m
  → physics speed gate (>200 km/h → reject)
  → jitter check (EMA of position variance)
  → regression heading (cv2.fitLine on pos history)
  → speed EMA smoothing
  → heading EMA smoothing (adaptive alpha based on speed)
  → SVG snapping (if enabled, 15° threshold)
```

## Key Connections Between Modules

| From | To | Data |
|---|---|---|
| `pipeline.py` | `g_projection.py` | `get_ground_contact_from_box()`, `sat_floor_to_cctv_3d()` |
| `pipeline.py` | `kinematics.py` | `TrackSmoother.update()` |
| `pipeline.py` | `replay_writer.py` | `ReplayWriter.write()` |
| `tab_inference.py` | `inference_session.py` | `InferenceSession` (QThread) |
| `inference_session.py` | `pipeline.py` | `InferencePipeline.run()` |
| `tab_visualization.py` | `replay_loader.py` | `ReplayLoader.load()` |
| `tab_visualization.py` | `cctv_renderer.py` | `CCTRenderer.render()` |
| `tab_visualization.py` | `sat_renderer.py` | `SatRenderer.render()` |
| `tab_visualization.py` | `video_player.py` | `VideoPlayer` |
| `analytics_server.py` | `analytics/api.py` | FastAPI `app` |
| `analytics/api.py` | `replay_loader.py` | `ReplayLoader.load()` |
| `voice_demo/server.py` | `analytics/api.py` | HTTP requests |
| `argus_bridge.py` | Argus SQLite DB | `sqlite3` queries |

## Critical Path: If You Change X, Update Y

| If you change... | You must also update... |
|---|---|
| JSON output format in `pipeline.py` | `replay_writer.py`, `replay_loader.py`, `tab_visualization.py`, `cctv_renderer.py`, `sat_renderer.py`, `analytics/api.py`, `analytics/engine.py` |
| `GProjection` class signature | `pipeline.py`, `tab_calibration.py` (all stages), `final_stage.py` |
| `TrackSmoother` class signature | `pipeline.py`, `tab_calibration.py` |
| `CCTRenderer.render()` params | `tab_visualization.py` |
| `SatRenderer.render()` params | `tab_visualization.py` |
| `default_config()` schema | `trafficlab_config.py`, `tab_calibration.py` (all stages) |
| `inference_config.yaml` schema | `tab_inference.py`, `pipeline.py` |
| `prior_dimensions.json` keys | `pipeline.py` |
