# Critical Bugs

> Runtime crashes and data corruption risks.

## 🔴 HIGH — Will crash or produce wrong results

### 1. `NameError: name 'i' is not defined`
**File**: `pipeline.py:270`
**Trigger**: YOLO returns 0 frames (empty video, corrupt file)
**Impact**: `out_data["animation_frame_count"] = i` crashes because `i` is never assigned
**Fix**: Initialize `i = -1` before the loop

### 2. `AttributeError: 'Val1Stage' has no attribute 'info'`
**File**: `val1_stage.py:92`
**Trigger**: No inspect object available (fresh calibration)
**Impact**: `showEvent` crashes silently (caught by bare except)
**Fix**: Remove the reference or create the label

### 3. Duplicate signal connections — duplicate markers
**File**: `val1_stage.py:186`
**Trigger**: Every time stage is shown via `showEvent`
**Impact**: `self.left_view.clicked` gets a new connection each time → slot fires 2x, 3x, etc.
**Fix**: Connect signal once in `__init__`, not in `showEvent`

### 4. ROI threshold inconsistency across stages
**Files**: `roi_stage.py:302` (`> 0`), `final_stage.py:630` (`> 128`), `roi_stage.py:247` (`< 10`)
**Trigger**: Any ROI mask with pixel values 1-127
**Impact**: Box passes validation in roi_stage but fails in final_stage. Inconsistent behavior.
**Fix**: Standardize to one threshold everywhere

### 5. `prior_dimensions.json` loaded via relative path
**File**: `pipeline.py:69`
**Trigger**: App launched from a different working directory
**Impact**: `FileNotFoundError` — inference fails completely
**Fix**: Use `Path(__file__).parent.parent.parent / "prior_dimensions.json"`

## 🟡 MEDIUM — May crash under certain conditions

### 6. `cap.release()` not in try/finally
**File**: `pipeline.py:265`
**Trigger**: Exception during YOLO tracking or projection
**Impact**: Video capture handle leaked — system resource leak

### 7. `K = np.array(und.get('K'))` crash when K is None
**Files**: `homf_stage.py:178`, `pars_stage.py:166`
**Trigger**: Config JSON missing `undistort.K` key
**Impact**: `TypeError: int() argument must be a string, a bytes-like object or a real number, not 'NoneType'`

### 8. `self._ranges` accessed before initialization
**File**: `undistort_stage.py:276`
**Trigger**: During `__init__` loop execution
**Impact**: `AttributeError` (caught by try/except, so Set Range buttons always initially disabled)

### 9. Variable `i` undefined after empty results
**File**: `pipeline.py:270`
**Impact**: Same as #1

### 10. `_H_inv = None` fallback causes downstream crash
**File**: `val3_stage.py:184`
**Trigger**: H matrix singular (can't invert)
**Impact**: `_on_sat_click` crashes with `NoneType not subscriptable`

## 🟠 LOW — Incorrect behavior but doesn't crash

### 11. `factor = 10.0` / `factor = 100.0` arbitrary fallbacks
**Files**: `val3_stage.py:282`, `final_stage.py:821`
**Trigger**: Camera height equals object height
**Impact**: Wildly incorrect projection positions

### 12. ~~`_apply_matrix_to_inspect` dead code~~ ✅ RESOLVED
**File**: `lens_stage.py`
**Impact**: Intrinsics matrix not written to inspect_obj via button (only via other paths)
**Status**: Method removed during dead code cleanup. No behavior change — `_apply_intrinsics_and_preview` was already the live path.

### 13. `track_ids` list comprehension may fail
**File**: `pipeline.py:160`
**Trigger**: Certain ultralytics versions where `r.boxes.id` is tensor of None
**Impact**: `AttributeError` during inference

### 14. `frames_to_process = 0` → division guard needed
**File**: `pipeline.py:264`
**Trigger**: Both `total_frames` and `max_frame` are 0
**Impact**: Guarded by `if frames_to_process > 0` but fragile

## Related
- [[Code Smells]]
- [[Performance Issues]]
- [[Calibration Stages]]
