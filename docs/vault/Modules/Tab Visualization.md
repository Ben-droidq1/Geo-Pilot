# Tab Visualization

> `trafficlab/gui/tabs/tab_visualization.py` (1049 lines)

## Class: `VisualizationTab(QWidget)`

The main playback viewer — side-by-side CCTV + satellite digital twin.

### Components
- **Sidebar**: File picker, layer controls, rendering options
- **CCTV View**: `CCTVGraphicsView` with video frames + overlays
- **Satellite View**: `SatGraphicsView` with map + floor boxes + arrows
- **Playback controls**: Play/pause, frame seek, FPS slider
- **Keyboard shortcuts**: 15 shortcuts for common operations

### Layout
```
┌─────────────────────────────────────────┐
│ Sidebar (340px)  │  CCTV View           │
│                  │                      │
│ File picker      │──────────────────────│
│ Layer controls   │  Satellite View      │
│ Render options   │                      │
│ Playback         │                      │
└─────────────────────────────────────────┘
```

### Key Features
- SVG overlay toggle with opacity slider
- ROI mask toggle
- FOV polygon display
- 3D bounding box toggle
- Coordinate dot toggle
- Speed label display with configurable delay
- Text color modes (White/Black/Yellow)
- Adaptive playback loop

### Playback Engine
```python
adaptive_loop():
    if playing:
        update_frame(advance=True)
        QTimer.singleShot(delay_ms, adaptive_loop)
```

### Frame Update Flow
```python
update_frame(advance):
    frame = video_player.read_frame(frame_idx)
    objects = current_json_data['frames'][frame_idx]['objects']
    draw_cctv(frame, objects)
    draw_sat(objects)
```

### Qt Connections (30+)
- File combo → load file
- Layer checkboxes → toggle SVG layers
- Opacity slider → update layer alpha
- Render checkboxes → update UI state
- FPS slider → update playback speed
- Keyboard shortcuts → various actions

## Bugs
1. ~~Unused imports: `sys`, `hashlib`, `re`, `ET`, `QLineF`, `QGraphicsLineItem`, `QGraphicsEllipseItem`~~ ✅ RESOLVED
2. Debug `traceback.print_exc()` left in production code
3. `mp4_frame_count` vs `animation_frame_count` inconsistency
4. Bare `except: pass` in multiple locations
5. File ends abruptly without blank line

## Related
- [[CCTV Renderer]]
- [[Sat Renderer]]
- [[Video Player]]
- [[Replay Loader]]
- [[Main Window]]
