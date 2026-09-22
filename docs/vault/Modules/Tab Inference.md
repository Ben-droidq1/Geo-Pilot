# Tab Inference

> `trafficlab/gui/tabs/tab_inference.py` (668 lines)

## Class: `InferenceTab(QWidget)`

Batch inference manager. Scans location folders for videos, runs YOLO detection.

### Key Components
- **Config picker**: Selects preset from `inference_config.yaml`
- **Config editor**: YAML editor with validation
- **Measurements editor**: Edit `prior_dimensions.json` entries
- **Task table**: Shows location/video/config/status per row
- **Progress bar**: Per-task progress
- **Log console**: Inference output

### Workflow
1. Click "Scan" → scans `location/` for MP4 files
2. Select/deselect tasks in table
3. Click "Lock" → validates config, saves edits
4. Click "Start" → runs inference on selected tasks sequentially
5. Each task: creates `InferenceSession` → `QThread` → `InferencePipeline`

### Batch Execution
```python
on_start_clicked()
  → run_next_task()
    → worker = InferenceSession(...)
    → worker_thread = QThread()
    → worker.moveToThread(worker_thread)
    → worker_thread.started.connect(worker.run)
    → worker.sig_finished.connect(on_session_finished)
    → worker_thread.start()
```

### Qt Connections
| Signal | Slot |
|---|---|
| `cfg_picker.currentIndexChanged` | `_on_config_selected()` |
| `btn_edit.clicked` | `_toggle_editor()` |
| `btn_edit_meas.clicked` | `_toggle_measurements_editor()` |
| `btn_lock.clicked` | `on_lock_clicked()` |
| `btn_wipe.clicked` | `on_wipe_clicked()` |
| `btn_start.clicked` | `on_start_clicked()` |
| `btn_stop.clicked` | `on_stop_clicked()` |
| `worker.sig_log` | `log()` |
| `worker.sig_progress` | `update_progress()` |
| `worker.sig_error` | `on_worker_error()` |
| `worker.sig_finished` | `on_session_finished()` |

## Bugs
1. Old `QThread` not explicitly cleaned up on rapid `run_next_task` calls
2. `on_lock_clicked` commented out in `finish_batch` — table not auto-refreshed
3. Wipe confirmation is case-sensitive (`"DELETE"` only)
4. `pyqtColor` imports `QColor` inside function body — import on every call

## Related
- [[Inference Session]]
- [[Inference Pipeline]]
- [[Main Window]]
