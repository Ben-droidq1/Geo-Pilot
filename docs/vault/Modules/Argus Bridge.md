# Argus Bridge

> `trafficlab/argus_bridge.py` (265 lines)

## Class: `ArgusBridge`

SQLite bridge to the Argus camera database.

### Constructor
```python
ArgusBridge(db_path=None)
```
Default DB: `../../Argus/scripts/data/cameras.db`

### Methods

| Method | Returns | Description |
|---|---|---|
| `search(source, country, has_stream, has_feed, bbox, limit)` | `list[dict]` | Filter cameras |
| `get_camera(camera_id)` | `dict?` | Single camera by ID |
| `get_sources()` | `list[str]` | All source values |
| `get_countries()` | `list[str]` | All country values |
| `get_stream_url(camera)` | `str?` | Extract stream URL from JSON |
| `create_location(camera, footage_url)` | `str` | Create location folder |
| `close()` | None | Close DB connection |

### `create_location` Flow
1. Extract location code from camera (truncated to 30 chars)
2. Create `location/<code>/` directory
3. Save `camera.json` with camera metadata
4. Optionally copy footage from `footage_url`
5. Return location code

## Bugs
1. `shutil` imported but never used
2. `_ARGUS_PUBLIC` defined but never used
3. `sys.path.insert` at module level — import side effect
4. `create_location` doesn't `makedirs` the parent directory

## Related
- [[Tab Location]]
