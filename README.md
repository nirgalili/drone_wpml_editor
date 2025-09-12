# 🚁 Drone KMZ Processor - Complete Workflow

**Transform any Dronelink KMZ file into a DJI RC-compatible mission with hover + photo actions on every waypoint.**

## 🎯 What It Does

Takes a KMZ file from Dronelink and automatically:
1. ✅ Extracts the WPML mission data
2. ✅ Adds hover (2s) + photo actions to ALL waypoints  
3. ✅ Creates a new KMZ file named `5336EE45-2941-4996-B7F1-22BAA25F2639.kmz`
4. ✅ Ready to load directly into your DJI Remote Controller

## 🚀 Quick Start (GUI - Recommended)

1. **Download** this repository
2. **Run** `kmz_gui.py` (double-click it)
3. **Browse** for your Dronelink KMZ file
4. **Customize output filename** (optional - for different DJI RC units)
5. **Choose hover options** (enable/disable hover, set hover time)
6. **Click** "Process KMZ File"
7. **Done!** Get your processed file ready for DJI RC

## 💻 Command Line Alternative

```bash
python kmz_processor.py your_mission.kmz
```

## 📁 What You Get

- **Input:** `mission.kmz` (from Dronelink)
- **Output:** `5336EE45-2941-4996-B7F1-22BAA25F2639.kmz` (default) or custom filename
- **Result:** Every waypoint now has hover + photo actions (or photo only)
- **Customizable:** 
  - Filename can be changed for different DJI RC units
  - Hover can be enabled/disabled
  - Hover time can be customized (1-60 seconds)

## 🛠️ Advanced Tools

### File Validators
- `simple_check.py` - Quick WPML compatibility check
- `wpml_validator.py` - Comprehensive validation

### Individual Scripts  
- `add_photos_final.py` - Add photo actions only
- `hover_add_actions.py` - Add hover + photo actions
- `final_check.py` - Verify all waypoints have actions

### Git Management
- `universal_git_tool.py` - Manage any Git repository
- `git_update.py` - Quick Git updates

## 📋 Requirements

- Python 3.6+
- No additional packages needed (uses only standard library)

## 🔧 How It Works

1. **Extracts** KMZ (treats as ZIP file)
2. **Finds** `wpmz/waylines.wpml` inside
3. **Processes** WPML to add hover + photo actions
4. **Recreates** KMZ with processed data
5. **Names** output file for DJI RC compatibility

## 📚 File Structure

```
drone_wpml_editor/
├── kmz_gui.py              # 🎯 MAIN GUI - Use this!
├── kmz_processor.py        # Core processing engine
├── simple_check.py         # Quick file validator
├── universal_git_tool.py   # Git management
└── original/               # Preserved original files
```

## ⚡ No More Manual Steps!

**Before:** Rename → Unzip → Edit → Rezip → Rename → Load to RC
**Now:** Drag & Drop → Click Process → Load to RC

## 🎉 Perfect for DJI Drones

- ✅ Compatible with DJI Remote Controllers
- ✅ Preserves all original mission data
- ✅ Adds professional hover + photo workflow
- ✅ Ready for immediate use
