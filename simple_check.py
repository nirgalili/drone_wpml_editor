#!/usr/bin/env python3
"""
Simple WPML Checker - No terminal needed
Just run this file directly in your IDE or double-click it
"""

import os

def check_wpml_file(file_path):
    """Check if a WPML file is compatible - returns True/False"""
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, file_path)
    
    print(f"Checking: {file_path}")
    print(f"Full path: {full_path}")
    print("-" * 40)
    
    # Check 1: File exists
    if not os.path.exists(full_path):
        print("❌ File not found")
        return False
    
    # Check 2: File size
    size = os.path.getsize(full_path)
    if size == 0:
        print("❌ File is empty")
        return False
    print(f"✅ File size: {size:,} bytes")
    
    # Check 3: Quick content check
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Basic checks
        if '<?xml' not in content:
            print("❌ Not XML")
            return False
            
        if 'kml' not in content.lower():
            print("❌ Not KML")
            return False
            
        if 'wpml' not in content.lower():
            print("❌ Not WPML")
            return False
            
        print("✅ Valid XML/KML/WPML")
        
        # Count waypoints
        waypoints = content.count('<Placemark>')
        print(f"✅ Waypoints: {waypoints}")
        
        # Count insertion points
        insertion_points = content.count('<wpml:useStraightLine>0</wpml:useStraightLine>')
        print(f"✅ Insertion points: {insertion_points}")
        
        if insertion_points == 0:
            print("❌ No insertion points - not compatible")
            return False
            
        # Count existing actions
        actions = content.count('<wpml:action>')
        if actions > 0:
            print(f"⚠️  Existing actions: {actions}")
        
        print("✅ COMPATIBLE with Drone WPML Editor!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# Test with your files
if __name__ == "__main__":
    print("WPML File Compatibility Checker")
    print("=" * 40)
    
    # Check main waylines file
    print("\n1. Checking waylines.wpml:")
    result1 = check_wpml_file("waylines.wpml")
    
    # Check hover file
    print("\n2. Checking working_hover.wpml:")
    result2 = check_wpml_file("working_hover.wpml")
    
    # Check original file
    print("\n3. Checking original/hover/waylines.wpml:")
    result3 = check_wpml_file("original/hover/waylines.wpml")
    
    print("\n" + "=" * 40)
    print("SUMMARY:")
    print(f"waylines.wpml: {'✅ OK' if result1 else '❌ Issues'}")
    print(f"working_hover.wpml: {'✅ OK' if result2 else '❌ Issues'}")
    print(f"original/hover/waylines.wpml: {'✅ OK' if result3 else '❌ Issues'}")
    
    input("\nPress Enter to exit...")
