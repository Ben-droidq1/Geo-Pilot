# Replay Loader

> `trafficlab/visualization/replay_loader.py` (14 lines)

## Class: `ReplayLoader`
Static method `load(path)`:
- `.gz` ending → `gzip.open(path, 'rt')` → `json.load()`
- Otherwise → `open(path, 'r')` → `json.load()`

## Bugs
1. Extension check `endswith(".gz")` doesn't handle `.GZ` (uppercase) or `.tar.gz`
2. No error handling for missing files or corrupt gzip
3. No type hints on return value

## Related
- [[Replay Writer]]
- [[JSON Output Schema]]
- [[Tab Visualization]]
- [[Analytics API]]
