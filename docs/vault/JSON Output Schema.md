# JSON Output Schema

Every inference produces a `.json.gz` file with this structure:

```json
{
  "mp4_path": "string",
  "meta": {
    "resolution": [width, height],
    "fps": 30.0
  },
  "location_code": "string",
  "mp4_frame_count": 1234,
  "animation_frame_count": 500,
  "frames": [
    {
      "frame_index": 0,
      "objects": [
        {
          "id": 0,
          "tracked_id": 1,
          "class": "car",
          "confidence": 0.87,
          "bbox_2d": [x1, y1, x2, y2],
          "reference_point": [cx, cy],
          "sat_coords": [x, y],
          "have_heading": true,
          "have_measurements": true,
          "default_heading": false,
          "heading": 90.5,
          "speed_kmh": 42.3,
          "sat_floor_box": [[x,y], [x,y], [x,y], [x,y]],
          "bbox_3d": [[x,y] x8]
        }
      ]
    }
  ]
}
```

## Field Descriptions

### Top-level

| Field | Type | Description |
|---|---|---|
| `mp4_path` | `str` | Source video path |
| `meta.resolution` | `[int, int]` | Video width × height |
| `meta.fps` | `float` | Frames per second |
| `location_code` | `str` | Location identifier |
| `mp4_frame_count` | `int` | Total frames in source video |
| `animation_frame_count` | `int` | Last frame index processed |
| `frames` | `list` | Per-frame data |

### Per-frame

| Field | Type | Description |
|---|---|---|
| `frame_index` | `int` | Frame number (0-indexed) |
| `objects` | `list` | Detected objects in this frame |

### Per-object

| Field | Type | Description |
|---|---|---|
| `id` | `int` | Detection index within frame |
| `tracked_id` | `int?` | ByteTrack ID (null if untracked) |
| `class` | `str` | Class name (e.g., "car", "truck") |
| `confidence` | `float` | YOLO confidence [0, 1] |
| `bbox_2d` | `[x1,y1,x2,y2]` | 2D bounding box (CCTV pixels) |
| `reference_point` | `[x, y]` | Projection reference point on CCTV |
| `sat_coords` | `[x, y]?` | Satellite coordinates (null if no G-Projection) |
| `have_heading` | `bool` | Whether heading was computed |
| `have_measurements` | `bool` | Whether prior dimensions exist |
| `default_heading` | `bool` | Whether heading is SVG-derived (not motion) |
| `heading` | `float?` | Heading in degrees [0, 360) |
| `speed_kmh` | `float` | Speed in km/h |
| `sat_floor_box` | `[[x,y] x4]?` | Rotated floor polygon on satellite |
| `bbox_3d` | `[[x,y] x8]?` | 3D bounding box projected to CCTV |

## Who Reads/Writes This Format

| Module | Reads | Writes |
|---|---|---|
| `replay_writer.py` | — | Yes |
| `replay_loader.py` | Yes | — |
| `tab_visualization.py` | Yes | — |
| `cctv_renderer.py` | Yes (objects) | — |
| `sat_renderer.py` | Yes (objects) | — |
| `analytics/engine.py` | Yes | — |
| `analytics/api.py` | Yes | — |
