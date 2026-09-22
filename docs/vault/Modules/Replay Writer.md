# Replay Writer

> `trafficlab/io/replay_writer.py` (23 lines)

## Classes

### `NumpyEncoder(json.JSONEncoder)`
Custom JSON encoder for numpy types:
- `np.int*` → `int`
- `np.float*` → `float`
- `np.ndarray` → `list`

### `ReplayWriter`
Static method `write(path, data)`:
- Opens `gzip.open(path, 'wt', encoding='utf-8')`
- Dumps JSON with `indent=2` and `NumpyEncoder`

## Bugs
1. No error handling — directory not found = unhandled exception
2. `NumpyEncoder` doesn't handle `np.bool_`, `np.str_`, structured arrays

## Related
- [[Inference Pipeline]]
- [[JSON Output Schema]]
- [[Replay Loader]]
