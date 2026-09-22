# Deployment Guide

How to run GeoPilot (Argus frontend + voice agent backend) on any OS.

---

## Prerequisites

| Tool | Version | Check |
|---|---|---|
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Git | any | `git --version` |

Optional: Docker (for containerized deployment).

---

## Quick Start (All Platforms)

```bash
# 1. Clone the repo
git clone https://github.com/your-org/geopilot.git
cd geopilot

# 2. Run the setup script
make setup
# or manually:
cp -n .env.example .env        # fill in your API keys
cd Argus && cp -n .env.example .env && cd ..

# 3. Start everything
make dev
# or manually:
# Terminal 1 — backend
source venv/bin/activate        # or .venv on Windows
python voice_agent_server.py

# Terminal 2 — frontend
cd Argus
npm install --legacy-peer-deps
npm run dev
```

Open http://localhost:5173

---

## macOS

### Install dependencies

```bash
# Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python
brew install python@3.13

# Node.js
brew install node@20

# OpenCV system deps (usually not needed on macOS)
# If cv2 fails: brew install opencv
```

### Setup

```bash
cd geopilot

# Python venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .  # install TrafficLab as editable package

# Frontend
cd Argus
npm install --legacy-peer-deps
cd ..

# Config
cp -n .env.example .env
cd Argus && cp -n .env.example .env && cd ..
# Edit .env with your API keys (ASSEMBLYAI_API_KEY, QWEN_API_KEY, etc.)
```

### Run

```bash
# Terminal 1 — Backend (port 8789)
source venv/bin/activate
python voice_agent_server.py

# Terminal 2 — Frontend (port 5173)
cd Argus
npm run dev
```

---

## Windows

### Install dependencies

```powershell
# Python — download from https://www.python.org/downloads/
# Check "Add Python to PATH" during install

# Node.js — download from https://nodejs.org/
# LTS version recommended

# Verify
python --version
node --version
```

### Setup

```powershell
cd geopilot

# Python venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -e .

# Frontend
cd Argus
npm install --legacy-peer-deps
cd ..

# Config
copy .env.example .env
cd Argus
copy .env.example .env
cd ..
# Edit .env with your API keys
```

### Run

```powershell
# Terminal 1 — Backend
venv\Scripts\activate
python voice_agent_server.py

# Terminal 2 — Frontend
cd Argus
npm run dev
```

---

## Linux (Ubuntu/Debian)

### Install dependencies

```bash
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3-pip nodejs npm git

# OpenCV system deps
sudo apt install -y libgl1 libglib2.0-0

# If Node.js version is too old, use nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20
```

### Setup

```bash
cd geopilot

# Python venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Frontend
cd Argus
npm install --legacy-peer-deps
cd ..

# Config
cp -n .env.example .env
cd Argus && cp -n .env.example .env && cd ..
# Edit .env with your API keys
```

### Run

```bash
# Terminal 1 — Backend
source venv/bin/activate
python voice_agent_server.py

# Terminal 2 — Frontend
cd Argus
npm run dev
```

---

## Docker (All Platforms)

### Prerequisites

- Docker Desktop (macOS/Windows) or Docker Engine (Linux)
- Docker Compose v2+

### Build & Run

```bash
cd geopilot

# Copy and fill in config
cp -n .env.example .env

# Build and start
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

Frontend is served at http://localhost:8789 (the backend serves the built React app).

---

## Environment Variables

### Root `.env` (Backend)

| Variable | Required | Description |
|---|---|---|
| `ASSEMBLYAI_API_KEY` | Yes | AssemblyAI API key for voice recognition |
| `QWEN_API_KEY` | Yes | Qwen VL API key for camera frame analysis |
| `QWEN_BASE_URL` | Yes | Qwen API endpoint (e.g. `https://api.b.ai/v1`) |
| `QWEN_MODEL` | Yes | Model name (e.g. `qwen3.8-flash`) |
| `GEOPILOT_AGENT_ID` | Yes | AssemblyAI agent ID (from `setup_voice_agent.py`) |
| `AGENT_PORT` | No | Backend port (default: `8789`) |
| `TTS_VOICE` | No | TTS voice (default: `en-US-GuyNeural`) |
| `FRAME_CACHE_TTL` | No | Frame cache TTL in seconds (default: `5`) |
| `GEOPILOT_API_URL` | No | Public URL for AssemblyAI callbacks (via ngrok) |

### Argus `.env` (Frontend)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_URL` | No | Backend URL (default: `http://localhost:8789`) |

---

## Production Deployment

### Option 1: Docker (recommended)

```bash
docker compose -f docker-compose.yml up -d
```

### Option 2: Manual

```bash
# Build frontend
cd Argus
VITE_API_URL=https://api.geopilot.ai npm run build
cd ..

# Serve frontend with a static file server (nginx, Caddy, etc.)
# Point API proxy to the Python backend on port 8789

# Run backend
source venv/bin/activate
AGENT_PORT=8789 python voice_agent_server.py
```

### Option 3: Platform-as-a-Service

- **Frontend**: Deploy `Argus/dist/` to Vercel, Netlify, or Cloudflare Pages
- **Backend**: Deploy to Railway, Fly.io, or a VPS
- Set `VITE_API_URL` to the backend's public URL before building

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `cv2` import error | `pip install opencv-python` + install system deps (`libgl1` on Linux) |
| `npm install` fails | Use `--legacy-peer-deps` flag |
| Port 8789 in use | Set `AGENT_PORT=8790` in `.env` |
| CORS errors | Ensure backend is running and `VITE_API_URL` matches |
| Map tiles not loading | Check internet connection (CartoDB tiles required) |
| Voice not working | Ensure `ASSEMBLYAI_API_KEY` is set and valid |
