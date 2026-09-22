# Getting Started

## Prerequisites

- Python 3.9+
- pip or conda
- Modern web browser (Chrome/Edge recommended)
- AssemblyAI API key

## Installation

### 1. Clone Repository

```bash
cd /Users/s/Documents/GeoPilot
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
cd voice-traffic-surveillance
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
TRAFFIC_SERVER_URL=http://localhost:8000
DEFAULT_CAMERA_ID=cam_001
```

## Running the System

### Step 1: Start Traffic Analysis Server

```bash
python tools/traffic_server.py
```

Expected output:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Publish Voice Agent

```bash
python publish.py
```

Expected output:
```
Agent published successfully!
Agent ID: 7ad24396-b822-4dca-871a-be9cc4781cf9
Saved to: .agent_id
```

### Step 3: Start Browser Server

```bash
python deployment/browser/server.py
```

Expected output:
```
INFO:     Started server process [12346]
INFO:     Uvicorn running on http://0.0.0.0:3000
```

### Step 4: Open Browser

Navigate to: `http://localhost:3000`

## Verification

### Check Services

```bash
# Traffic Server
curl http://localhost:8000/health

# Browser Server
curl http://localhost:3000/health
```

Expected responses:

```json
{
  "status": "healthy",
  "service": "GeoPilot Traffic Surveillance",
  "cameras_online": 2
}
```

### Test Voice Agent

1. Open `http://localhost:3000`
2. Click "Connect Voice"
3. Say "What's the traffic status?"
4. Verify voice response

### Test API

```bash
curl -X POST http://localhost:8000/tools/get_traffic_stats \
  -H "Content-Type: application/json" \
  -d '{"camera_id": "cam_001"}'
```

## Configuration

### Camera Setup

Edit `config/inference_config.yaml`:

```yaml
cameras:
  default_fps: 30
  default_resolution: "1920x1080"
  network_timeout: 30
```

### Voice Agent Settings

Edit `agents/traffic-surveillance.jsonc`:

```json
{
  "name": "GeoPilot Traffic Surveillance Agent",
  "voice": { "voice_id": "anna" },
  "greeting": "GeoPilot traffic surveillance active..."
}
```

### Alert Thresholds

Configure via API:

```bash
curl -X POST http://localhost:8000/tools/set_alert_threshold \
  -H "Content-Type: application/json" \
  -d '{"metric": "speed", "threshold": 30}'
```

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

#### Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### API Key Error

```
Error: ASSEMBLYAI_API_KEY not set
```

Solution: Ensure `.env` file exists with valid API key.

#### Connection Refused

```
Error: Connection refused at localhost:8000
```

Solution: Verify traffic server is running.

### Logs

Check logs for errors:

```bash
# Traffic server logs
tail -f logs/traffic_surveillance.log

# Browser server logs
# Check terminal output
```

## Next Steps

- [[Voice Commands]] - Learn available commands
- [[API Reference]] - Explore API endpoints
- [[Configuration Guide]] - Advanced configuration
- [[Deployment Guide]] - Production deployment

## Related Pages

- [[Home]]
- [[Architecture Overview]]
- [[Troubleshooting]]

## Tags

#getting-started #installation #setup #quickstart

---

*Part of [[GeoPilot Traffic Surveillance]]*
