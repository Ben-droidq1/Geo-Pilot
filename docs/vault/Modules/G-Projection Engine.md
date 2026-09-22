# G-Projection Engine

> `trafficlab/projection/g_projection.py` (165 lines)

## Class: `GProjection`

The core coordinate transform engine. Converts between CCTV pixel space and satellite map space.

### Constructor
```python
GProjection(config_data: dict, base_dir: str = ".")
```
- `config_data`: The G_projection JSON (undistort, homography, parallax sections)
- `base_dir`: Base directory for resolving relative paths (SVG layout)

### Transform Chain

```
CCTV (u,v) → Undistorted (u_u,v_u) → Apparent SAT (x,y) → Real SAT (with parallax)
```

Inverse:
```
Real SAT (x,y) → Apparent SAT → Undistorted (u_u,v_u) → CCTV (u,v)
```

### Methods

| Method | Input | Output | Description |
|---|---|---|---|
| `cctv_to_undistorted(u, v)` | pixel | pixel | Remove lens distortion |
| `undistorted_to_flat_sat(u_u, v_u)` | pixel | sat | Apply homography |
| `flat_sat_to_undistorted(x, y)` | sat | pixel | Inverse homography |
| `undistorted_to_cctv(u_u, v_u)` | pixel | pixel | Re-apply distortion |
| `cctv_to_sat(u, v, h)` | pixel+height | sat | Full forward projection |
| `sat_to_cctv(x, y, h)` | sat+height | pixel | Full inverse projection |
| `parallax_correct_ground_to_real(pt, h)` | sat+height | sat | Parallax correction |
| `parallax_project_real_to_ground(pt, h)` | sat+height | sat | Inverse parallax |
| `get_ground_contact_from_box(rect, h_meters, ...)` | bbox+height | dict | Full projection from bbox |
| `sat_floor_to_cctv_3d(sat_poly, h)` | polygon+height | 8 points | 3D box lifting |

### `get_ground_contact_from_box` Parameters
- `rect`: Bounding box `(x, y, w, h)` or QRect
- `h_meters`: Object height for parallax
- `ref_method`: `"center_bottom_side"` or `"center_box"`
- `proj_method`: `"down_h"` (full height) or `"down_h_2"` (half height)

### Return Value
```python
{
    "sat_coords": (x, y),        # Final satellite coordinates
    "cctv_ref_point": (cx, cy),  # Reference point on CCTV
    "cctv_ground_point": (u, v)  # Ground contact point on CCTV
}
```

### `sat_floor_to_cctv_3d` Output
Returns 8 CCTV pixel points: [4 bottom, 4 top] for 3D wireframe rendering.

### Hardcoded Defaults
| Value | Purpose |
|---|---|
| `z_cam_meters = 10.0` | Camera height fallback |
| `px_per_meter = 1.0` | Scale fallback |
| `0.001` | Min px_per_m threshold |
| `0.01` | Parallax div-by-zero guard |

## Bugs in This File

| # | Severity | Issue |
|---|---|---|
| 1 | LOW | Duplicate `return` in `sat_floor_to_cctv_3d` (dead code) |
| 2 | MEDIUM | No validation of config data — cryptic numpy errors on missing keys |
| 3 | LOW | `undistorted_to_cctv` name misleading — it applies distortion, not 3D reprojection |

## Related
- [[Inference Pipeline]]
- [[Calibration Stages]]
- [[Tab Calibration]]
