#!/usr/bin/env python3
"""Check the current waylines.wpml file for photo actions."""

import xml.etree.ElementTree as ET

def check_waylines_file():
    """Check which waypoints have photo actions in waylines.wpml."""
    tree = ET.parse('waylines.wpml')
    root = tree.getroot()
    
    kml_ns = "http://www.opengis.net/kml/2.2"
    wpml_ns = "http://www.dji.com/wpmz/1.0.6"
    placemarks = root.findall(f".//{{{kml_ns}}}Placemark")
    
    print("Checking waylines.wpml file:")
    print("-" * 40)
    
    waypoints_with_photos = []
    waypoints_without_photos = []
    
    for placemark in placemarks:
        waypoint_index = placemark.find(f".//{{{wpml_ns}}}index")
        if waypoint_index is not None:
            index = int(waypoint_index.text)
            
            # Check if this waypoint has takePhoto actions
            has_photo = False
            for action_group in placemark.findall(f".//{{{wpml_ns}}}actionGroup"):
                for action in action_group.findall(f".//{{{wpml_ns}}}action"):
                    actuator_func = action.find(f"{{{wpml_ns}}}actionActuatorFunc")
                    if actuator_func is not None and actuator_func.text == "takePhoto":
                        has_photo = True
                        break
                if has_photo:
                    break
            
            if has_photo:
                waypoints_with_photos.append(index)
                print(f"Waypoint {index}: ✅ HAS photo action")
            else:
                waypoints_without_photos.append(index)
                print(f"Waypoint {index}: ❌ NO photo action")
    
    print(f"\nSummary:")
    print(f"Total waypoints: {len(placemarks)}")
    print(f"With photo actions: {len(waypoints_with_photos)}")
    print(f"Without photo actions: {len(waypoints_without_photos)}")
    
    if waypoints_without_photos:
        print(f"Missing photos at waypoints: {waypoints_without_photos}")
    else:
        print("✅ All waypoints have photo actions!")

if __name__ == "__main__":
    check_waylines_file()
