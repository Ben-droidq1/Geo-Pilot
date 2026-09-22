# Configuration Guide

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ASSEMBLYAI_API_KEY` | AssemblyAI API key | `sk_abc123...` |
| `TRAFFIC_SERVER_URL` | Traffic server URL | `http://localhost:8000` |
| `DEFAULT_CAMERA_ID` | Default camera ID | `cam_001` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CAMERA_NETWORK_URL` | Camera network URL | `http://localhost:8000/cameras` |
| `ALERT_WEBHOOK_URL` | Alert webhook URL | - |
| `ENABLE_VOICE_ALERTS` | Enable voice alerts | `true` |
| `EXA_API_KEY` | EXA Search API key | - |

### Twilio Variables (Phone Integration)

| Variable | Description |
|----------|-------------|
| `TWILIO_ACCOUNT_SID` | Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token |
| `TWILIO_PHONE_NUMBER` | Twilio Phone Number |
| `TWILIO_TRUNK_DOMAIN` | SIP Trunk Domain |

## Environment File

### Development (.env)

```env
ASSEMBLYAI_API_KEY=your_key_here
TRAFFIC_SERVER_URL=http://localhost:8000
DEFAULT_CAMERA_ID=cam_001
ENABLE_VOICE_ALERTS=true
```

### Production (.env.production)

```env
ASSEMBLYAI_API_KEY=your_production_key
TRAFFIC_SERVER_URL=https://api.geopilot.com
DEFAULT_CAMERA_ID=cam_001
ENABLE_VOICE_ALERTS=true
ALERT_WEBHOOK_URL=https://alerts.geopilot.com/webhook
```

## Inference Configuration

Location: `config/inference_config.yaml`

### Detection Settings

```yaml
detection:
  model_path: "models/yolov8s.pt"
  confidence_threshold: 0.5
  nms_threshold: 0.4
  input_size: [640, 640]
  classes:
    - car
    - truck
    - bus
    - motorcycle
    - bicycle
    - pedestrian
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `model_path` | YOLO model path | `models/yolov8s.pt` |
| `confidence_threshold` | Detection confidence | `0.5` |
| `nms_threshold` | Non-max suppression | `0.4` |
| `input_size` | Input resolution | `[640, 640]` |

### Tracking Settings

```yaml
tracking:
  tracker: "bytetrack"
  max_age: 30
  min_hits: 3
  iou_threshold: 0.3
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `tracker` | Tracker algorithm | `bytetrack` |
| `max_age` | Max frames to keep | `30` |
| `min_hits` | Min hits to confirm | `3` |
| `iou_threshold` | IoU threshold | `0.3` |

### Analysis Settings

```yaml
analysis:
  free_flow_speed: 60
  congestion_thresholds:
    low: 25
    medium: 50
    high: 75
  incident_detection:
    enabled: true
    min_confidence: 0.8
    alert_cooldown: 300
```

### Kinematics Settings

```yaml
kinematics:
  speed_smoothing:
    method: "exponential_moving_average"
    alpha: 0.3
  position_smoothing:
    method: "kalman_filter"
    process_noise: 0.01
    measurement_noise: 0.1
```

## Voice Agent Configuration

Location: `agents/traffic-surveillance.jsonc`

### Agent Settings

```json
{
  "name": "GeoPilot Traffic Surveillance Agent",
  "system_prompt": "You are GeoPilot...",
  "voice": { "voice_id": "anna" },
  "greeting": "GeoPilot traffic surveillance active..."
}
```

### Voice Options

| Voice ID | Gender | Style |
|----------|--------|-------|
| `anna` | Female | Professional |
| `james` | Male | Authoritative |
| `sarah` | Female | Friendly |
| `michael` | Male | Calm |

### Keyterms

Improve transcription accuracy:

```json
"keyterms": [
  "GeoPilot",
  "TrafficLab",
  "incident detection",
  "vehicle count",
  "traffic flow",
  "congestion",
  "anomaly detection"
]
```

## Alert Configuration

### Alert Thresholds

Set via API:

```bash
# Speed alert
curl -X POST http://localhost:8000/tools/set_alert_threshold \
  -H "Content-Type: application/json" \
  -d '{"metric": "speed", "threshold": 30}'

# Congestion alert
curl -X POST http://localhost:8000/tools/set_alert_threshold \
  -H "Content-Type: application/json" \
  -d '{"metric": "congestion", "threshold": 75}'
```

### Alert Channels

| Channel | Description |
|---------|-------------|
| `voice` | Voice alerts via agent |
| `websocket` | Real-time dashboard updates |
| `webhook` | HTTP webhook notifications |

## Camera Configuration

### Camera Registration

Cameras are registered in the data store:

```python
CameraInfo(
    camera_id="cam_001",
    name="Main Street & 1st Ave",
    location={"lat": 40.7128, "lng": -74.0060},
    status=CameraStatus.ONLINE,
    resolution="1920x1080",
    fps=30,
    last_active=datetime.now()
)
```

### Camera Status

| Status | Description |
|--------|-------------|
| `online` | Camera active and streaming |
| `offline` | Camera disconnected |
| `maintenance` | Camera under maintenance |

## Performance Configuration

### Server Settings

```yaml
performance:
  max_concurrent_streams: 10
  queue_size: 100
  batch_size: 16
  gpu_enabled: true
```

### Logging

```yaml
logging:
  level: "INFO"
  file: "logs/traffic_surveillance.log"
  max_size: "100MB"
  backup_count: 5
```

## Related Pages

- [[Getting Started]]
- [[Deployment Guide]]
- [[Troubleshooting]]

## Tags

#configuration #settings #environment #setup

---

*Part of [[GeoPilot Traffic Surveillance]]*
