# Video Player

> `trafficlab/visualization/video_player.py` (31 lines)

## Class: `VideoPlayer`

Wraps `cv2.VideoCapture` with a cleaner API.

> Note: `read_frame()`, `frame_count()`, `fps()`, `resolution()` were removed during dead code cleanup. Only the used surface is kept.

| Method | Description |
|---|---|
| `__init__(path)` | Opens video file |
| `is_opened()` | Returns `bool` |
| `seek(index)` | Seeks to frame |
| `read()` | Returns `(ret, frame)` |
| `release()` | Releases capture |
| `__del__` | Auto-releases capture |

## Bugs
1. `seek()` doesn't verify success — some codecs fail silently
2. Not thread-safe — `cv2.VideoCapture` must be single-threaded
3. No type hints

## Related
- [[Tab Visualization]]
