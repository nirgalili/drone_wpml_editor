#!/usr/bin/env python3
"""Verify that all waypoints have photo capture actions."""

import xml.etree.ElementTree as ET

def verify_photo_actions(wpml_file):
    """Verify that all waypoints now have photo capture actions."""
    tree = ET.parse(wpml_file)
    root = tree.getroot()
    
    kml_ns = "http://www.opengis.net/kml/2.2"
    wpml_ns = "http://www.dji.com/wpmz/1.0.6"
    placemarks = root.findall(f".//{{{kml_ns}}}Placemark")
    
    waypoints_with_photo_actions = set()
    
    for placemark in placemarks:
        waypoint_index = placemark.find(f".//{{{wpml_ns}}}index")
        if waypoint_index is not None:
            index = int(waypoint_index.text)
            
            # Find all actionActuatorFunc elements with takePhoto
            photo_actions = []
            for action_group in placemark.findall(f".//{{{wpml_ns}}}actionGroup"):
                for action in action_group.findall(f".//{{{wpml_ns}}}action"):
                    actuator_func = action.find(f"{{{wpml_ns}}}actionActuatorFunc")
                    if actuator_func is not None and actuator_func.text == "takePhoto":
                        photo_actions.append(action)
            
            if photo_actions:
                waypoints_with_photo_actions.add(index)
                print(f"Waypoint {index}: {len(photo_actions)} photo action(s)")
            else:
                print(f"Waypoint {index}: NO photo actions")
    
    print(f"\nTotal waypoints: {len(placemarks)}")
    print(f"Waypoints with photo actions: {len(waypoints_with_photo_actions)}")
    print(f"Missing photo actions: {len(placemarks) - len(waypoints_with_photo_actions)}")
    
    if len(waypoints_with_photo_actions) == len(placemarks):
        print("✅ SUCCESS: All waypoints now have photo capture actions!")
        return True
    else:
        missing = set(range(len(placemarks))) - waypoints_with_photo_actions
        print(f"❌ ERROR: Waypoints missing photo actions: {sorted(missing)}")
        return False

if __name__ == "__main__":
    print("Verifying waylines_with_photos.wpml...")
    verify_photo_actions("waylines_with_photos.wpml")
