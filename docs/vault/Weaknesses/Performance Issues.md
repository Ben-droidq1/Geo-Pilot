# Performance Issues

> Inefficiencies and bottlenecks.

## 1. `get_nearest_heading` is O(n) Per Call
**File**: `projection/svg_parser.py:101`
**Impact**: Called once per detected object per frame. With 100 SVG segments and 50 objects/frame at 30fps = 150,000 calls/second.
**Fix**: Build a spatial index (KD-tree) on init.

## 2. `SVGLayoutParser` Parses CSS on Every Init
**File**: `visualization/svg_parser.py:47`
**Impact**: Regex-based CSS parsing runs every time a visualization tab is opened.
**Fix**: Cache parsed CSS per SVG path.

## 3. QImage Created Without `.copy()` in Some Paths
**File**: `cctv_renderer.py:72`
**Impact**: `QImage(frame.data, ...)` wraps numpy buffer. If frame is modified before `QPixmap.fromImage()`, undefined behavior. The renderer is safe (consecutive calls), but other code paths may not be.

## 4. Speed Display Cache Not Shared Across Frames
**File**: `sat_renderer.py:49-50`
**Impact**: If caller passes new dict each frame, speed smoothing is lost. The caller must pass the same dict reference.

## 5. `cv2.fitLine` Called Per-Track Per-Frame
**File**: `kinematics.py:117`
**Impact**: With 50 tracked objects, this is 50 `cv2.fitLine` calls per frame. Each operates on a deque of max 8 points — relatively cheap but adds up.

## 6. No Frame Caching in Visualization
**File**: `tab_visualization.py`
**Impact**: Every frame seek reads from disk via `VideoPlayer.read()` (`cv2.VideoCapture` seek). No LRU cache for recently accessed frames.

## 7. GZipped JSON Decompression on Load
**File**: `replay_loader.py:9`
**Impact**: Large replay files (>100MB) take several seconds to decompress. No streaming/incremental loading.

## 8. `model.track()` Runs Full Pipeline
**File**: `pipeline.py:145`
**Impact**: YOLO model is loaded once but `model.track()` runs the full detect+track pipeline per frame. No early termination for frames with no detections.

## 9. Multiple `scene.clear()` Calls in Calibration
**Files**: Various calibration stages
**Impact**: `scene.clear()` destroys all QGraphicsItems and rebuilds. For complex scenes, this causes visible flicker.

## 10. `get_color_from_string` Uses MD5
**File**: `cctv_renderer.py:13`
**Impact**: MD5 is cryptographic overkill. A simpler hash (e.g., `hash()`) would be faster. LRU cache mitigates this.

## Related
- [[Code Smells]]
- [[Critical Bugs]]
