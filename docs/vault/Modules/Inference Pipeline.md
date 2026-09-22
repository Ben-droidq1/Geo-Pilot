# Inference Pipeline

> `trafficlab/inference/pipeline.py` (275 lines)

## Class: `InferencePipeline`

### Constructor Parameters
| Param | Type | Description |
|---|---|---|
| `location_code` | `str` | Location identifier |
| `footage_path` | `str` | Path to MP4 or RTSP/HLS stream |
| `config_path` | `str` | Path to `inference_config.yaml` |
| `output_root` | `str` | Output directory root |
| `g_proj_path` | `str?` | Path to G_projection JSON (None for detection-only) |
| `config_name` | `str?` | Named config preset in YAML |
| `log_fn` | `callable` | Logging callback |
| `progress_fn` | `callable` | Progress callback (0-100 or -1 for indeterminate) |
| `stop_flag_fn` | `callable` | Returns True to stop processing |

### `run()` Method Flow
1. Load YAML config (supports multi-config `configs:` map)
2. Load G-Projection JSON (optional — skip for detection-only)
3. Load `prior_dimensions.json` (relative path — fragile)
4. Create output directory structure
5. Init `cv2.VideoCapture` (supports streams)
6. Load ROI mask if enabled
7. Init YOLO model from weights
8. Run `model.track()` with ByteTrack
9. Per-frame loop: detect → ROI filter → project → kinematics → 3D lift
10. Write output via `ReplayWriter.write()`

### Key Dependencies
- [[G-Projection Engine]] — `get_ground_contact_from_box()`, `sat_floor_to_cctv_3d()`
- [[Kinematics Smoother]] — `TrackSmoother.update()`
- [[Replay Writer]] — `ReplayWriter.write()`

### Config Selection Logic
```
YAML has 'configs' key?
  YES → use config_name if provided, else first key
  NO  → use entire YAML as config
```

### Stream Detection
- If `total_frames == 0` or `fps <= 0` → treated as stream
- Default stream: 24 FPS, process 10 seconds of frames
- Progress bar set to indeterminate (-1) for streams

## Bugs in This File

| # | Severity | Issue |
|---|---|---|
| 1 | HIGH | `prior_dimensions.json` loaded via relative path — breaks if CWD differs |
| 2 | HIGH | Variable `i` undefined if `results` is empty → `NameError` |
| 3 | MEDIUM | No `try/finally` for `cap.release()` — video handle leaked on exception |
| 4 | MEDIUM | `track_ids` list comprehension may fail with certain ultralytics versions |
| 5 | LOW | `frames_to_process` could be 0 → division by zero (guarded but fragile) |
| 6 | LOW | `is_stream` detection fragile — some files report 0 frames |

## Related
- [[Data Flow Pipeline]]
- [[JSON Output Schema]]
- [[Critical Bugs]]
