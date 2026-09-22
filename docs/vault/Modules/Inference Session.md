# Inference Session

> `trafficlab/gui/inference_session.py` (49 lines)

## Class: `InferenceSession(QObject)`

QThread-compatible wrapper for `InferencePipeline`.

### Signals
| Signal | Type | Description |
|---|---|---|
| `sig_log` | `str` | Log messages |
| `sig_progress` | `int` | Progress percentage |
| `sig_status` | `str` | Status updates (**never emitted**) |
| `sig_finished` | `()` | Pipeline complete |
| `sig_error` | `str` | Error messages |

### Methods
- `request_stop()` — sets `stop_requested = True`
- `run()` — creates and runs `InferencePipeline`

## Bugs
1. `sig_status` declared but never emitted — dead signal
2. `"Done."` log emitted after `sig_finished` — out-of-order signal delivery
3. `stop_requested` is plain bool, not `threading.Event` — technically not thread-safe
4. `import traceback` inside except block — unconventional

## Related
- [[Tab Inference]]
- [[Inference Pipeline]]
