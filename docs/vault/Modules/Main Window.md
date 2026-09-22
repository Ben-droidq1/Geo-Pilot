# Main Window

> `trafficlab/gui/main_window.py`

## Class: `MainWindow(QMainWindow)`

### Tab Structure

| Index | Tab | Class | Description |
|---|---|---|---|
| 0 | Welcome | `WelcomeTab` | Landing page with markdown |
| 1 | Location | `LocationTab` | Create/manage locations |
| 2 | Calibration | `CalibrationTab` | 14-stage calibration wizard |
| 3 | Inference | `InferenceTab` | Batch YOLO inference |
| 4 | Visualization | `VisualizationTab` | Digital twin viewer |

### Theme
- Dark theme via `qdarktheme`
- Window title: "TrafficLab 3D"
- Minimum size: 1280×720

## Related
- [[Tab Welcome]]
- [[Tab Location]]
- [[Tab Calibration]]
- [[Tab Inference]]
- [[Tab Visualization]]
