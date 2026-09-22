# Qt Signals and Slots

> Complete map of all Qt signal-slot connections across the GUI.

## Main Window
- Tab widget index change → tab-specific refresh logic

## Tab Welcome
- None (passive display)

## Tab Location
| Signal | Slot |
|---|---|
| `btn_pick_cctv.clicked` | `pick_cctv()` |
| `btn_pick_sat.clicked` | `pick_sat()` |
| `btn_pick_layout.clicked` | `pick_layout()` |
| `btn_pick_roi.clicked` | `pick_roi()` |
| `btn_create.clicked` | `create_location()` |
| `media_cctv_fit.clicked` | `media_cctv.fit_view()` |
| `media_sat_fit.clicked` | `media_sat.fit_view()` |
| `btn_refresh_locations.clicked` | `_populate_location_combo()` |
| `btn_add_footage.clicked` | `add_footage()` |

## Tab Calibration
| Signal | Slot |
|---|---|
| `btn_save.clicked` | `_on_save()` |
| Each step button `.clicked` | `_on_step_clicked(index)` |
| `inspect_btn.clicked` | `_on_inspect()` |

### Per-Stage Connections
**PickStage**: refresh, combo, construct, validate, reconstruct, fit views, SVG/ROI toggles, proceed
**LensStage**: fit, proceed, use_default, apply_intrinsics
**UndistortStage**: pen_mode, activate_pen, new_arc, clear_arcs, proceed, sliders, set/reset buttons
**Val1Stage**: marker_button, clear_markers, proceed, left_view.clicked
**HomAStage**: list_widget, name_input, btn_add/del/compute/proceed, view_cctv/sat.clicked
**HomFStage**: slider_alpha, btn_compute/proceed
**Val2Stage**: view_cctv.clicked, btn_proceed
**ParsStage**: view_cctv.clicked, btn_reset/compute/proceed
**DistStage**: combo_start/end, btn_compute/proceed
**Val3Stage**: view_cctv/sat.clicked, btn_clear/proceed
**SVGStage**: slider_alpha, btn_back_edit/compute/proceed
**ROIStage**: viewer.boxChanged, bg_method, cb_show_mask, btn_proceed
**FinalStage**: view_cctv.boxDrawn, btn_reset_box, spin_w/l/h, cb_ref/proj, btn_confirm_pts, chk_auto_head, slider_head, btn_show_3d, chk_roi, slider_alpha, btn_proceed

## Tab Inference
| Signal | Slot |
|---|---|
| `btn_reload.clicked` | `_load_defaults()` |
| `cfg_picker.currentIndexChanged` | `_on_config_selected()` |
| `btn_edit.clicked` | `_toggle_editor()` |
| `btn_edit_meas.clicked` | `_toggle_measurements_editor()` |
| `btn_lock.clicked` | `on_lock_clicked()` |
| `btn_wipe.clicked` | `on_wipe_clicked()` |
| `btn_start.clicked` | `on_start_clicked()` |
| `btn_stop.clicked` | `on_stop_clicked()` |
| `btn_select_all.clicked` | `on_select_all_clicked()` |
| `btn_unselect_all.clicked` | `on_unselect_all_clicked()` |
| `worker.sig_log` | `log()` |
| `worker.sig_progress` | `update_progress()` |
| `worker.sig_error` | `on_worker_error()` |
| `worker.sig_finished` | `on_session_finished()` |

## Tab Visualization
| Signal | Slot |
|---|---|
| `file_combo.currentIndexChanged` | `load_selected_file()` |
| `btn_load_selected.clicked` | `load_selected_file()` |
| `btn_list_files.clicked` | `show_file_list_dialog()` |
| `btn_refresh.clicked` | `load_file_list()` |
| `slider_opacity.valueChanged` | `update_sat_layers()` |
| `layer_checks[name].toggled` | `toggle_svg_layer()` |
| `chk_sat_box/coords/arrow/label.toggled` | `update_ui_state()` |
| `slider_sat_thick/text.valueChanged` | `update_ui_state()` |
| `combo_text_color.currentIndexChanged` | `update_text_controls()` |
| `chk_fov.toggled` | `set_fov_visible()` |
| `slider_fov_opacity.valueChanged` | `update_fov_opacity()` |
| `slider_speed_delay.valueChanged` | `update_ui_state()` |
| `chk_tracking/3d_box/cctv_label/roi.toggled` | `update_ui_state()` |
| `slider_3d_alpha.valueChanged` | `update_ui_state()` |
| `slider_fps.valueChanged` | `update_fps_target()` |
| `btn_help.clicked` | `QMessageBox.information()` |
| `btn_toggle_sidebar.toggled` | `_toggle_sidebar()` |
| 15 keyboard shortcuts | various lambdas |

## Related
- [[Main Window]]
- [[Tab Calibration]]
- [[Tab Inference]]
- [[Tab Visualization]]
