# Tab Calibration

> `trafficlab/gui/tabs/tab_calibration.py` (401 lines)

## Class: `CalibrationTab(QWidget)`

14-step camera calibration wizard with step buttons, progress bar, and inspect dialog.

### Steps

| Index | Name | Stage Class | Purpose |
|---|---|---|---|
| 0 | Pick | `PickStage` | Location selection |
| 1 | Lens | `LensStage` | Camera intrinsics (K matrix) |
| 2 | Undistort | `UndistortStage` | Distortion coefficients (D) |
| 3 | Val1 | `Val1Stage` | Undistort validation |
| 4 | HomA | `HomAStage` | Homography anchor points |
| 5 | HomF | `HomFStage` | Homography FOV visualization |
| 6 | Val2 | `Val2Stage` | Pipeline validation |
| 7 | Pars | `ParsStage` | Parallax camera position |
| 8 | Dist | `DistStage` | Distance/scale (px/m) |
| 9 | Val3 | `Val3Stage` | Parallax validation |
| 10 | SVG | `SVGStage` | SVG alignment |
| 11 | ROI | `ROIStage` | ROI configuration |
| 12 | Final | `FinalStage` | Final 3D validation |
| 13 | Save | `SaveStage` | Save G_projection JSON |

### Step Navigation
- Click step button → `_on_step_clicked(index)` → `_show_stage(index)`
- Each stage has a "Proceed" button → advances to next stage
- Disabled stages: SVG, ROI, Save (initially enabled after prerequisites)

### Progress Bar
- Animated width transition to active step
- Color: `#cef` (light blue)

### Inspect Dialog
- Shows raw JSON of current G-Projection config
- Editable text area

## Bugs
1. `index == 13` magic number for Save button enable
2. Stages created with `project_root=None, parent=None` — orphaned widgets
3. Dead code: `while len(self.stage_widgets) < len(self.STEPS)` loop

## Related
- [[Calibration Stages]]
- [[Main Window]]
