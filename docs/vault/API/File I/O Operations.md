# File I/O Operations

> Every read and write operation across the codebase.

## Writes

| File | What it writes | Format |
|---|---|---|
| `replay_writer.py` | Inference output | `.json.gz` (gzipped JSON) |
| `trafficlab_config.py` | G-Projection config | `.json` |
| `tab_location.py` | Location folders + copied footage | Directories + PNG/SVG/MP4 |
| `argus_bridge.py` | Camera metadata | `camera.json` |
| `scripts/make_sample_replay.py` | Sample replay | `.json.gz` |
| `scripts/upgrade_g_projection.py` | Upgraded calibration | `.json` |
| `scripts/upgrade_roi.py` | Upscaled ROI mask | `.png` |
| `scripts/cut_batch_clips.py` | Split video clips | `.mp4` |

## Reads

| File | What it reads | Format |
|---|---|---|
| `pipeline.py` | `inference_config.yaml` | YAML |
| `pipeline.py` | `prior_dimensions.json` | JSON |
| `pipeline.py` | G-Projection JSON | `.json` |
| `pipeline.py` | ROI mask | `.png` (IMREAD_UNCHANGED) |
| `pipeline.py` | Video/streams | `.mp4` / RTSP / HLS |
| `replay_loader.py` | Replay files | `.json` or `.json.gz` |
| `tab_welcome.py` | `media/welcome-trafficlab.md` | Markdown |
| `tab_location.py` | CCTV/sat images | PNG/JPG |
| `tab_inference.py` | `inference_config.yaml` | YAML |
| `tab_inference.py` | `prior_dimensions.json` | JSON |
| `tab_visualization.py` | Replay + video | `.json.gz` + `.mp4` |
| `visualization/svg_parser.py` | SVG layout | `.svg` |
| `projection/svg_parser.py` | SVG orientation | `.svg` |
| `analytics/api.py` | Replay files (via `/load`) | `.json.gz` |
| `argus_bridge.py` | Argus SQLite DB | `.db` |
| `voice_demo/server.py` | `.env` file | Env vars |
| `setup_voice_agent.py` | `.env` file | Env vars |

## Critical I/O Paths

```
location/<code>/
  cctv_<code>.png        ← tab_location writes, calibration stages read
  sat_<code>.png         ← tab_location writes, calibration stages read
  layout_<code>.svg      ← tab_location writes, svg_parser reads
  roi_<code>.png         ← tab_location writes, pipeline reads
  footage/<video>.mp4    ← tab_location writes, pipeline reads
  G_projection_<code>.json ← calibration writes, pipeline reads

output/<model>/<config>/<code>/
  <video>.json.gz        ← pipeline writes, replay_loader reads
```

## Related
- [[Data Flow Pipeline]]
- [[JSON Output Schema]]
