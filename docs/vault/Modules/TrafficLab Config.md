# TrafficLab Config

> `trafficlab/io/trafficlab_config.py` (72 lines)

## Functions

### `default_config(location_code, timestamp)` → dict
Returns a default G-Projection JSON structure with placeholder values.

Schema:
```
meta: { location_code, timestamp }
inputs: { cctv_path, sat_path, layout_path, roi_path }
undistort: { resolution, K, D, model }
homography: { H, fov_polygon, anchors_list }
parallax: { x_cam_coords_sat, y_cam_coords_sat, z_cam_meters, scale, px_per_meter }
use_svg: bool
layout_svg: { A, association_pairs }
use_roi: bool
roi_method: "partial" | "in"
ref_method: "center_box" | "center_bottom_side"
proj_method: "down_h" | "down_h_2"
```

### `to_pretty_json(obj)` → str
JSON dump with indent=4.

### `save_config(path, obj)` → None
Writes JSON to file.

### `load_config(path)` → dict
Reads JSON from file.

## Bugs
1. Uses TABS for indentation — rest of project uses spaces
2. Default K matrix hardcoded for 1280×720 resolution
3. `load_config` has no error handling — raw `FileNotFoundError`
4. Timestamp lacks timezone info

## Related
- [[Calibration Stages]]
- [[G-Projection Engine]]
