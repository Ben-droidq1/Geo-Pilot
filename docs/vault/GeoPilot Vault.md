# GeoPilot Vault

> Comprehensive codebase analysis of the GeoPilot traffic intelligence platform.

## Quick Navigation

### Architecture
- [[Repo Map]] — Full file tree, entry points, and how to run
- [[Data Flow Pipeline]] — How data moves through the system
- [[JSON Output Schema]] — The per-frame replay format
- [[Deployment Guide]] — OS-based setup, Docker, env vars, production deployment

### Module Analysis
- [[Inference Pipeline]] — YOLO detection + tracking + projection
- [[G-Projection Engine]] — CCTV ↔ satellite coordinate transforms
- [[Kinematics Smoother]] — Heading + speed EMA smoothing
- [[Replay Writer]] — Gzipped JSON output
- [[Replay Loader]] — Gzipped JSON input
- [[TrafficLab Config]] — G-Projection JSON schema
- [[CCTV Renderer]] — 2D/3D bounding box drawing
- [[Sat Renderer]] — Floor boxes + arrows + speed labels
- [[Video Player]] — cv2.VideoCapture wrapper
- [[SVG Parser (Projection)]] — Road orientation extraction
- [[SVG Layout Parser]] — SVG → Qt graphics items
- [[Analytics Engine]] — Pure-computation analytics
- [[Analytics API]] — FastAPI REST endpoints (legacy, now on voice server too)
- [[Voice Agent Config]] — AssemblyAI tool definitions
- [[Voice Agent Server]] — HLS capture + Qwen VL + TTS + analytics (port 8789)
- [[Argus Bridge]] — SQLite camera database bridge

### GUI Analysis (Legacy — PyQt5)
- [[Main Window]] — QMainWindow with 5 tabs
- [[Tab Welcome]] — Landing page
- [[Tab Location]] — Location management
- [[Tab Calibration]] — 14-stage wizard
- [[Tab Inference]] — Batch inference manager
- [[Tab Visualization]] — Digital twin viewer
- [[Calibration Stages]] — All 14 stages deep-dive

### Weaknesses & Bugs
- [[Critical Bugs]] — Runtime crashes and data corruption risks
- [[Code Smells]] — Design issues and anti-patterns
- [[Security Issues]] — Secrets, exposure, injection risks
- [[Voice Agent Weaknesses]] — Voice server security and quality issues
- [[Performance Issues]] — Inefficiencies and bottlenecks
- [[Dead Code]] — Unused imports, variables, functions

### Working Endpoints
- [[REST API Endpoints]] — All FastAPI routes (port 8787, now also on 8789)
- [[Voice Agent Endpoints]] — Voice server HTTP routes (port 8789) — includes analytics
- [[Qt Signals and Slots]] — All GUI connections
- [[File I/O Operations]] — Every read/write operation
