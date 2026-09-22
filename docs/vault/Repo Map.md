# Repo Map

## Entry Points

| File | Purpose | How to run |
|---|---|---|
| `frontend/` | React frontend (landing page + main UI) | `cd frontend && npm run dev` (port 5173) |
| `voice_agent_server.py` | Backend: camera search + voice + analytics | `python voice_agent_server.py` (port 8789) |
| `main.py` | PyQt5 calibration/inference UI (legacy) | `python main.py` |
| `analytics_server.py` | FastAPI analytics (legacy) | `python analytics_server.py --port 8787` |
| `setup_voice_agent.py` | AssemblyAI agent CLI | `python setup_voice_agent.py --create` |

## How to Run

```bash
# Terminal 1: Frontend (landing page + Argus)
cd frontend
npm run dev          # http://localhost:5173

# Terminal 2: Backend
python voice_agent_server.py   # http://localhost:8789
```

## Architecture

```
frontend/                       React frontend (landing page + Argus, port 5173)
  └── src/App.tsx               HUD, map, filters, feed panel, voice agent

voice_agent_server.py           Python backend (port 8789)
  ├── Camera search             Argus 229K+ camera database
  ├── Vision analysis           Qwen VL for frame analysis
  ├── Voice agent               AssemblyAI voice I/O
  ├── Analytics                 Vehicle count, speed, flow, turning patterns
  └── TTS                       edge-tts spoken responses

trafficlab/                     Python engine (used by Argus + voice agent)
  ├── gui/                      PyQt5 calibration/inference/visualization UI
  ├── inference/                YOLO detection + tracking
  ├── projection/               CCTV ↔ satellite transforms
  ├── motion/                   Heading + speed smoothing
  ├── io/                       Replay read/write
  ├── visualization/            CCTV + satellite renderers
  └── voice/                    AssemblyAI agent config
```

## Directory Structure

```
GeoPilot/
├── Argus/                              React frontend (Vite + TypeScript)
│   ├── src/
│   │   └── App.tsx                     Entire UI: HUD, settings, filters, feed panel, both map renderers
│   ├── public/
│   │   ├── cameras.core.json           229K+ camera positions (loaded first)
│   │   ├── cameras.labels.json         Camera names (loaded behind core)
│   │   └── cameras.detail/             Per-camera detail chunks
│   ├── scripts/
│   │   ├── scraper.py                  Python CLI scraper
│   │   ├── store.py                    SQLite + export to JSON payload
│   │   └── server.py                   Local dev control server (port 8787)
│   └── package.json
│
├── voice_agent_server.py               Backend: camera search + voice + analytics (port 8789)
├── main.py                             PyQt5 calibration/inference UI (legacy)
├── analytics_server.py                 Legacy FastAPI server (port 8787)
├── setup_voice_agent.py                AssemblyAI agent setup CLI
├── inference_config.yaml               Multi-config YAML (3 presets)
├── prior_dimensions.json               Vehicle dimension priors
├── .env / .env.example                 Environment secrets
│
├── trafficlab/
│   ├── __init__.py
│   ├── argus_bridge.py                 Argus camera DB bridge
│   │
│   ├── gui/
│   │   ├── main_window.py              QMainWindow (5 tabs)
│   │   ├── views.py                    Reusable QGraphicsView widgets
│   │   ├── inference_session.py         QThread wrapper for pipeline
│   │   ├── tabs/
│   │   │   ├── tab_welcome.py          Landing page (markdown)
│   │   │   ├── tab_location.py         Create location folders
│   │   │   ├── tab_calibration.py      14-stage calibration wizard
│   │   │   ├── tab_inference.py        Batch YOLO inference
│   │   │   └── tab_visualization.py    Digital twin viewer
│   │   └── tabs/calibration_stage/
│   │       ├── pick_stage.py           Stage 0: Location picker
│   │       ├── lens_stage.py           Stage 1: Camera intrinsics
│   │       ├── undistort_stage.py      Stage 2: Distortion coefficients
│   │       ├── val1_stage.py           Stage 3: Undistort validation
│   │       ├── homa_stage.py           Stage 4: Homography anchors
│   │       ├── homf_stage.py           Stage 5: Homography FOV
│   │       ├── val2_stage.py           Stage 6: Pipeline validation
│   │       ├── pars_stage.py           Stage 7: Parallax subjects
│   │       ├── dist_stage.py           Stage 8: Distance/scale
│   │       ├── val3_stage.py           Stage 9: Parallax validation
│   │       ├── svg_stage.py            Stage 10: SVG alignment
│   │       ├── roi_stage.py            Stage 11: ROI configuration
│   │       └── final_stage.py          Stage 12: Final validation
│   │
│   ├── inference/
│   │   └── pipeline.py                 Core: YOLO → tracking → projection
│   │
│   ├── projection/
│   │   ├── g_projection.py             CCTV ↔ satellite transforms
│   │   └── svg_parser.py               SVG road orientation extraction
│   │
│   ├── motion/
│   │   └── kinematics.py               TrackSmoother: heading + speed EMA
│   │
│   ├── io/
│   │   ├── replay_writer.py            Writes gzipped JSON
│   │   └── trafficlab_config.py        G-Projection JSON schema + I/O
│   │
│   ├── visualization/
│   │   ├── cctv_renderer.py            2D/3D bbox drawing on CCTV
│   │   ├── sat_renderer.py             Floor boxes + arrows on satellite
│   │   ├── replay_loader.py            Loads .json / .json.gz
│   │   ├── video_player.py             cv2.VideoCapture wrapper
│   │   └── svg_parser.py               SVG → Qt QGraphicsItems
│   │
│   ├── analytics/
│   │   ├── engine.py                   Pure-computation analytics
│   │   └── api.py                      FastAPI REST API (legacy)
│   │
│   └── voice/
│       └── agent_config.py             AssemblyAI agent + tools
│
├── voice-traffic-surveillance/
│   ├── agents/                         Voice agent config
│   ├── tools/                          Traffic analysis server
│   ├── deployment/browser/             Browser voice client
│   └── publish.py                      Agent publisher
│
├── scripts/
│   ├── test_end_to_end.py              E2E test
│   ├── make_sample_replay.py           Generate sample .json.gz
│   ├── cut_batch_clips.py              FFmpeg batch clip splitter
│   ├── upgrade_g_projection.py         Cal migration script
│   ├── upgrade_roi.py                  ROI mask upsizer
│   └── icon_ascii_art.py               ASCII art generator
│
├── tests/
│   └── test_analytics_engine.py        Unit tests for analytics
│
└── media/                              README images and demo
```

## File Counts

| Category | Count | Lines (approx) |
|---|---|---|
| Core (pipeline, projection, kinematics) | 4 | ~725 |
| GUI tabs | 5 | ~2,580 |
| Calibration stages | 13 | ~5,700 |
| Visualization | 5 | ~550 |
| IO | 2 | ~95 |
| Analytics | 2 | ~745 |
| Voice/Bridge | 2 | ~495 |
| Scripts/Tests | 8 | ~570 |
| Config/Data | 4 | ~300 |
| **Total** | **~50 files** | **~11,760 lines** |

## Dependencies

### Python Standard Library
`os`, `sys`, `json`, `gzip`, `math`, `re`, `time`, `hashlib`, `shutil`, `copy`, `pathlib`, `collections`, `statistics`, `xml.etree.ElementTree`, `urllib`, `http.server`, `sqlite3`, `argparse`, `subprocess`, `traceback`, `functools`, `typing`, `ipaddress`, `concurrent.futures`, `threading`

### Third-Party (Python)
| Package | Used by |
|---|---|
| `PyQt5` | All GUI code |
| `cv2` (OpenCV) | Pipeline, projection, renderers, calibration stages |
| `numpy` | Pipeline, projection, kinematics, renderers |
| `ultralytics` (YOLO) | `pipeline.py` |
| `PyYAML` | `pipeline.py`, `tab_inference.py` |
| `FastAPI` | `analytics/api.py` |
| `uvicorn` | `analytics_server.py` |
| `pydantic` | `analytics/api.py` |
| `PIL` (Pillow) | `scripts/upgrade_roi.py`, `scripts/icon_ascii_art.py` |
| `qdarktheme` | `main.py` (dark theme) |
| `edge_tts` | `voice_agent_server.py` (TTS) |

### Third-Party (JavaScript — Argus)
| Package | Used by |
|---|---|
| `react` | UI components |
| `react-dom` | React rendering |
| `maplibre-gl` | Map rendering |
| `@deck.gl/react` | GPU-accelerated camera dots |
| `hls.js` | HLS stream playback |
| `lucide-react` | Icons |
| `framer-motion` | Animations |
| `tailwindcss` | Styling |
| `vite` | Build tool |
| `typescript` | Type checking |
