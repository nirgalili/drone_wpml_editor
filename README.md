# Drone WPML Editor

A small toolkit to edit DJI WPML mission files:
- Add photo actions to all waypoints
- Create a hover + takePhoto action group per waypoint
- Preserve original files in `original/`

## Files
- `waylines.wpml`: photo-at-each-waypoint mission (DJI-compatible formatting)
- `working_hover.wpml`: hover(2s)+photo at each waypoint
- `original/waylines.wpml`: preserved original
- `original/hover/waylines.wpml`: original hover baseline

## Scripts
- `add_photos_final.py`: adds properly formatted takePhoto actions to all waypoints
- `hover_add_actions.py`: creates `working_hover.wpml` with hover+photo groups
- `final_check.py`: verifies each waypoint has one photo action
- `check_current.py`: quick check of current `waylines.wpml`

## Quick start
```bash
# Create hover+photo mission
python hover_add_actions.py

# Verify photo actions in current mission
python final_check.py
```

## Notes
- The repository keeps originals under `original/` so you can always regenerate outputs.
- The scripts are text-based to preserve the DJI controller’s required formatting.
