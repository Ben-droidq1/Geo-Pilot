# API Reference

## Base URL

```
Development: http://localhost:8000
Production: https://api.geopilot.com
```

## Authentication

All requests require API key in header:

```javascript
headers: {
  'Authorization': 'Bearer YOUR_API_KEY',
  'Content-Type': 'application/json'
}
```

## Endpoints

### Traffic Statistics

#### `POST /tools/get_traffic_stats`

Get current traffic statistics for a camera.

**Request Body:**
```json
{
  "camera_id": "cam_001",
  "zone": "Main Street"
}
```

**Response:**
```json
{
  "camera_id": "cam_001",
  "camera_name": "Main Street & 1st Ave",
  "zone": "Main Street",
  "timestamp": "2026-09-10T12:00:00Z",
  "vehicle_count": 47,
  "avg_speed": 42.5,
  "congestion_level": 35.2,
  "active_incidents": 1,
  "vehicle_types": {
    "car": 32,
    "truck": 8,
    "bus": 4,
    "motorcycle": 3
  },
  "camera_status": "online",
  "summary": "Camera Main Street: 47 vehicles detected, average speed 43 km/h, congestion at 35%."
}
```

**Error Responses:**
- `404` - Camera not found
- `500` - Internal server error

---

### Incident Detection

#### `POST /tools/detect_incidents`

Check for traffic incidents in an area.

**Request Body:**
```json
{
  "area": "Main Street",
  "severity": "medium"
}
```

**Response:**
```json
{
  "area": "Main Street",
  "timestamp": "2026-09-10T12:00:00Z",
  "total_incidents": 2,
  "active_incidents": 1,
  "incidents": [
    {
      "id": "inc_001",
      "severity": "high",
      "description": "Multi-vehicle collision blocking left lane",
      "location": {
        "lat": 40.7128,
        "lng": -74.0060,
        "zone": "Main Street"
      },
      "status": "active",
      "time_ago": "0:15:30"
    }
  ],
  "alert": "ATTENTION: 1 active incident(s) in Main Street.",
  "summary": "Found 1 active incidents. Most severe: Multi-vehicle collision blocking left lane"
}
```

---

### Vehicle Count

#### `POST /tools/get_vehicle_count`

Get real-time vehicle count and classification.

**Request Body:**
```json
{
  "camera_id": "cam_001",
  "time_range": "1h"
}
```

**Time Range Formats:**
- `5m` - 5 minutes
- `1h` - 1 hour
- `24h` - 24 hours

**Response:**
```json
{
  "camera_id": "cam_001",
  "time_range": "1h",
  "timestamp": "2026-09-10T12:00:00Z",
  "total_count": 127,
  "classification": {
    "car": 89,
    "truck": 18,
    "bus": 12,
    "motorcycle": 8
  },
  "avg_confidence": 0.94,
  "summary": "Detected 127 vehicles in the last 1h. 89 cars, 18 trucks, 12 buses, 8 motorcycles"
}
```

---

### Traffic Flow Analysis

#### `POST /tools/analyze_traffic_flow`

Analyze traffic flow patterns and congestion.

**Request Body:**
```json
{
  "route": "Highway 101",
  "direction": "northbound"
}
```

**Directions:**
- `northbound`
- `southbound`
- `eastbound`
- `westbound`
- `all`

**Response:**
```json
{
  "route": "Highway 101",
  "direction": "northbound",
  "vehicle_count": 89,
  "avg_speed": 65.3,
  "congestion_level": 25.8,
  "status": "flowing",
  "timestamp": "2026-09-10T12:00:00Z",
  "summary": "Traffic flowing normally on Highway 101. Average speed: 65 km/h."
}
```

---

### Speed Data

#### `POST /tools/get_speed_data`

Get speed distribution for vehicles.

**Request Body:**
```json
{
  "camera_id": "cam_001",
  "vehicle_type": "car"
}
```

**Vehicle Types:**
- `all`
- `car`
- `truck`
- `bus`
- `motorcycle`
- `bicycle`

**Response:**
```json
{
  "camera_id": "cam_001",
  "vehicle_type": "car",
  "count": 89,
  "avg_speed": 48.2,
  "min_speed": 12.5,
  "max_speed": 98.7,
  "std_dev": 15.3,
  "timestamp": "2026-09-10T12:00:00Z",
  "summary": "Speed analysis for cam_001: Average 48.2 km/h, Range 12.5-98.7 km/h, Based on 89 vehicles."
}
```

---

### Report Generation

#### `POST /tools/generate_report`

Generate a traffic analysis report.

**Request Body:**
```json
{
  "time_period": "today",
  "metrics": ["volume", "speed", "incidents", "congestion"]
}
```

**Time Periods:**
- `today`
- `last_hour`
- `2024-01-15` (specific date)

**Metrics:**
- `volume` - Vehicle counts
- `speed` - Speed statistics
- `incidents` - Incident data
- `congestion` - Congestion levels
- `anomalies` - Anomaly detection

**Response:**
```json
{
  "time_period": "today",
  "generated_at": "2026-09-10T12:00:00Z",
  "metrics": {
    "volume": {
      "total_vehicles": 1247,
      "by_camera": {
        "cam_001": 456,
        "cam_002": 512,
        "cam_003": 279
      }
    },
    "speed": {
      "average": 45.2,
      "min": 5.3,
      "max": 120.8
    },
    "incidents": {
      "total": 5,
      "active": 1,
      "by_severity": {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 2
      }
    },
    "congestion": {
      "cam_001": 35.2,
      "cam_002": 28.7,
      "cam_003": 42.1
    }
  },
  "summary": "Traffic Report for today: 1247 vehicles tracked across 3 cameras. 1 active incident(s) require attention."
}
```

---

### Alert Thresholds

#### `POST /tools/set_alert_threshold`

Set alert thresholds for monitoring.

**Request Body:**
```json
{
  "metric": "speed",
  "threshold": 30,
  "camera_id": "cam_001"
}
```

**Metrics:**
- `speed` - Speed threshold
- `volume` - Volume threshold
- `congestion` - Congestion threshold
- `incident` - Incident threshold

**Response:**
```json
{
  "status": "success",
  "camera_id": "cam_001",
  "metric": "speed",
  "threshold": 30,
  "summary": "Alert threshold set: speed threshold now 30 for cam_001."
}
```

---

### Camera Status

#### `POST /tools/get_camera_status`

Get status of all cameras.

**Request Body:**
```json
{
  "status_filter": "online"
}
```

**Filters:**
- `all`
- `online`
- `offline`
- `maintenance`

**Response:**
```json
{
  "timestamp": "2026-09-10T12:00:00Z",
  "total_cameras": 3,
  "online": 2,
  "offline": 0,
  "maintenance": 1,
  "cameras": [
    {
      "id": "cam_001",
      "name": "Main Street & 1st Ave",
      "status": "online",
      "location": {
        "lat": 40.7128,
        "lng": -74.0060
      },
      "last_active": "2026-09-10T12:00:00Z"
    }
  ],
  "summary": "Camera Network Status: 2 online, 0 offline, 1 in maintenance."
}
```

---

### Health Check

#### `GET /health`

Check service health.

**Response:**
```json
{
  "status": "healthy",
  "service": "GeoPilot Traffic Surveillance",
  "timestamp": "2026-09-10T12:00:00Z",
  "cameras_online": 2
}
```

---

## WebSocket Protocol

### Connection

```
ws://localhost:8000/ws/traffic-updates
```

### Message Format

```typescript
interface TrafficUpdate {
  type: 'vehicle_detected' | 'incident' | 'congestion_change' | 'camera_status';
  timestamp: string;
  data: {
    camera_id: string;
    // Additional data based on type
  };
}
```

### Example Messages

**Vehicle Detected:**
```json
{
  "type": "vehicle_detected",
  "timestamp": "2026-09-10T12:00:00Z",
  "data": {
    "camera_id": "cam_001",
    "vehicle_id": "veh_0047",
    "vehicle_type": "car",
    "speed": 45.2,
    "confidence": 0.96
  }
}
```

**Incident Alert:**
```json
{
  "type": "incident",
  "timestamp": "2026-09-10T12:00:00Z",
  "data": {
    "camera_id": "cam_001",
    "incident_id": "inc_001",
    "severity": "high",
    "description": "Multi-vehicle collision"
  }
}
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Camera cam_999 not found",
  "status_code": 404
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid API key |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Invalid request body |
| 500 | Internal Server Error |

### Retry Strategy

```javascript
async function withRetry(fn, maxAttempts = 3) {
  for (let i = 0; i < maxAttempts; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxAttempts - 1) throw error;
      await new Promise(r => setTimeout(r, 1000 * (i + 1)));
    }
  }
}
```

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| `/tools/*` | 100 req/min |
| `/ws/*` | 10 connections |
| `/health` | Unlimited |

---

## Related Pages

- [[REST Endpoints]]
- [[WebSocket Protocol]]
- [[Error Handling]]
- [[TypeScript Types]]

## Tags

#api #endpoints #rest #websocket #reference

---

*Part of [[GeoPilot Traffic Surveillance]]*
