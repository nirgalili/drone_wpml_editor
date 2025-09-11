#!/usr/bin/env python3
"""Final verification of the waylines.wpml file."""

import xml.etree.ElementTree as ET

def check_final_file():
    """Check the final waylines.wpml file."""
    tree = ET.parse('waylines.wpml')
    root = tree.getroot()
    
    kml_ns = "http://www.opengis.net/kml/2.2"
    wpml_ns = "http://www.dji.com/wpmz/1.0.6"
    placemarks = root.findall(f".//{{{kml_ns}}}Placemark")
    
    print("Final verification of waylines.wpml:")
    print("-" * 40)
    
    photo_count = 0
    for placemark in placemarks:
        waypoint_index = placemark.find(f".//{{{wpml_ns}}}index")
        if waypoint_index is not None:
            index = int(waypoint_index.text)
            
            # Count photo actions for this waypoint
            photo_actions = placemark.findall(f".//{{{wpml_ns}}}actionActuatorFunc[.='takePhoto']")
            if photo_actions:
                photo_count += len(photo_actions)
                print(f"Waypoint {index}: {len(photo_actions)} photo action(s)")
    
    print(f"\nSummary:")
    print(f"Total waypoints: {len(placemarks)}")
    print(f"Total photo actions: {photo_count}")
    
    if photo_count == len(placemarks):
        print("✅ SUCCESS: All waypoints have exactly 1 photo action each!")
    else:
        print(f"❌ ERROR: Expected {len(placemarks)} photo actions, found {photo_count}")

if __name__ == "__main__":
    check_final_file()
