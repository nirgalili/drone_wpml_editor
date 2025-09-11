#!/usr/bin/env python3
"""
Quick WPML File Checker
Fast validation for WPML file compatibility.
"""

import os
import sys

def quick_check(file_path):
    """Quick check if WPML file is compatible."""
    print(f"Checking: {file_path}")
    
    # Check 1: File exists
    if not os.path.exists(file_path):
        print("❌ File not found")
        return False
    
    # Check 2: File size (not empty)
    size = os.path.getsize(file_path)
    if size == 0:
        print("❌ File is empty")
        return False
    print(f"✅ File size: {size:,} bytes")
    
    # Check 3: Quick XML check (first 1000 chars)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(1000)
            
        # Look for key WPML elements
        if '<?xml' not in content:
            print("❌ Not a valid XML file")
            return False
            
        if 'kml' not in content.lower():
            print("❌ Not a KML file")
            return False
            
        if 'wpml' not in content.lower():
            print("❌ Not a WPML file")
            return False
            
        print("✅ Valid XML/KML/WPML structure")
        
    except Exception as e:
        print(f"❌ File read error: {e}")
        return False
    
    # Check 4: Look for waypoints and insertion points
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            full_content = f.read()
            
        # Count waypoints
        waypoint_count = full_content.count('<Placemark>')
        print(f"✅ Found {waypoint_count} waypoints")
        
        # Count insertion points
        insertion_points = full_content.count('<wpml:useStraightLine>0</wpml:useStraightLine>')
        print(f"✅ Found {insertion_points} insertion points")
        
        if insertion_points == 0:
            print("❌ No insertion points found - file not compatible")
            return False
            
        if waypoint_count == 0:
            print("❌ No waypoints found")
            return False
            
        # Check for existing actions
        action_count = full_content.count('<wpml:action>')
        if action_count > 0:
            print(f"⚠️  File already has {action_count} actions")
        
        print("✅ File is compatible with Drone WPML Editor!")
        return True
        
    except Exception as e:
        print(f"❌ Content check error: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python quick_wpml_check.py <wpml_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    is_valid = quick_check(file_path)
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
