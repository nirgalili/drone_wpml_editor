#!/usr/bin/env python3
"""
Script to add photo capture actions to all waypoints in a WPML file.
Currently only waypoints 0, 2, and 4 have photo capture actions.
This script will add photo capture actions to all other waypoints.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

def add_photo_actions_to_wpml(input_file, output_file=None):
    """
    Add photo capture actions to all waypoints that don't already have them.
    
    Args:
        input_file: Path to input WPML file
        output_file: Path to output WPML file (if None, overwrites input)
    """
    if output_file is None:
        output_file = input_file
    
    # Parse the XML file
    tree = ET.parse(input_file)
    root = tree.getroot()
    
    # Define the namespaces
    kml_ns = "http://www.opengis.net/kml/2.2"
    wpml_ns = "http://www.dji.com/wpmz/1.0.6"
    
    # Find all Placemark elements (waypoints) - they are in KML namespace
    placemarks = root.findall(f".//{{{kml_ns}}}Placemark")
    
    print(f"Found {len(placemarks)} waypoints")
    
    # Track which waypoints already have photo actions
    waypoints_with_photo_actions = set()
    
    # Check existing photo actions
    for placemark in placemarks:
        waypoint_index = placemark.find(f".//{{{wpml_ns}}}index")
        if waypoint_index is not None:
            index = int(waypoint_index.text)
            
            # Check if this waypoint has any takePhoto actions
            photo_actions = placemark.findall(f".//{{{wpml_ns}}}actionActuatorFunc[.='takePhoto']")
            if photo_actions:
                waypoints_with_photo_actions.add(index)
                print(f"Waypoint {index}: Already has photo action")
            else:
                print(f"Waypoint {index}: No photo action")
    
    print(f"\nWaypoints with photo actions: {sorted(waypoints_with_photo_actions)}")
    print(f"Waypoints needing photo actions: {len(placemarks) - len(waypoints_with_photo_actions)}")
    
    # Add photo actions to waypoints that don't have them
    next_action_group_id = 4  # Start after existing action group IDs (0, 1, 2, 3)
    
    for placemark in placemarks:
        waypoint_index = placemark.find(f".//{{{wpml_ns}}}index")
        if waypoint_index is not None:
            index = int(waypoint_index.text)
            
            if index not in waypoints_with_photo_actions:
                print(f"Adding photo action to waypoint {index}")
                
                # Create action group for photo capture
                action_group = ET.SubElement(placemark, f"{{{wpml_ns}}}actionGroup")
                
                # Action group ID
                action_group_id = ET.SubElement(action_group, f"{{{wpml_ns}}}actionGroupId")
                action_group_id.text = str(next_action_group_id)
                next_action_group_id += 1
                
                # Action group start and end index
                start_index = ET.SubElement(action_group, f"{{{wpml_ns}}}actionGroupStartIndex")
                start_index.text = str(index)
                end_index = ET.SubElement(action_group, f"{{{wpml_ns}}}actionGroupEndIndex")
                end_index.text = str(index)
                
                # Action group mode
                action_group_mode = ET.SubElement(action_group, f"{{{wpml_ns}}}actionGroupMode")
                action_group_mode.text = "sequence"
                
                # Action trigger
                action_trigger = ET.SubElement(action_group, f"{{{wpml_ns}}}actionTrigger")
                action_trigger_type = ET.SubElement(action_trigger, f"{{{wpml_ns}}}actionTriggerType")
                action_trigger_type.text = "reachPoint"
                
                # Action
                action = ET.SubElement(action_group, f"{{{wpml_ns}}}action")
                action_id = ET.SubElement(action, f"{{{wpml_ns}}}actionId")
                action_id.text = "0"
                
                action_actuator_func = ET.SubElement(action, f"{{{wpml_ns}}}actionActuatorFunc")
                action_actuator_func.text = "takePhoto"
                
                # Action parameters
                action_params = ET.SubElement(action, f"{{{wpml_ns}}}actionActuatorFuncParam")
                payload_position_index = ET.SubElement(action_params, f"{{{wpml_ns}}}payloadPositionIndex")
                payload_position_index.text = "0"
                
                file_suffix = ET.SubElement(action_params, f"{{{wpml_ns}}}fileSuffix")
                file_suffix.text = ""
                
                use_global_payload_lens_index = ET.SubElement(action_params, f"{{{wpml_ns}}}useGlobalPayloadLensIndex")
                use_global_payload_lens_index.text = "0"
    
    # Save the modified XML
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"\nModified WPML file saved to: {output_file}")
    
    # Verify the changes
    print("\nVerifying changes...")
    verify_photo_actions(output_file)

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
            
            photo_actions = placemark.findall(f".//{{{wpml_ns}}}actionActuatorFunc[.='takePhoto']")
            if photo_actions:
                waypoints_with_photo_actions.add(index)
    
    print(f"Total waypoints: {len(placemarks)}")
    print(f"Waypoints with photo actions: {len(waypoints_with_photo_actions)}")
    print(f"Missing photo actions: {len(placemarks) - len(waypoints_with_photo_actions)}")
    
    if len(waypoints_with_photo_actions) == len(placemarks):
        print("✅ SUCCESS: All waypoints now have photo capture actions!")
    else:
        missing = set(range(len(placemarks))) - waypoints_with_photo_actions
        print(f"❌ ERROR: Waypoints missing photo actions: {sorted(missing)}")

if __name__ == "__main__":
    input_file = "waylines.wpml"
    output_file = "waylines_with_photos.wpml"  # Create a backup first
    
    print("Adding photo capture actions to all waypoints...")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print("-" * 50)
    
    add_photo_actions_to_wpml(input_file, output_file)
