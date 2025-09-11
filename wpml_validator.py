#!/usr/bin/env python3
"""
WPML File Validator
Checks if a WPML file is compatible with the Drone WPML Editor software.
"""

import xml.etree.ElementTree as ET
import os
import sys
from typing import List, Tuple, Dict, Any

class WPMLValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.waypoint_count = 0
        self.action_count = 0
        
    def validate_file(self, file_path: str) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a WPML file for compatibility.
        
        Returns:
            (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        self.waypoint_count = 0
        self.action_count = 0
        
        # Check if file exists
        if not self._check_file_exists(file_path):
            return False, self.errors, self.warnings
            
        # Check if file is readable
        if not self._check_file_readable(file_path):
            return False, self.errors, self.warnings
            
        # Check if file is valid XML
        if not self._check_xml_valid(file_path):
            return False, self.errors, self.warnings
            
        # Check WPML structure
        if not self._check_wpml_structure(file_path):
            return False, self.errors, self.warnings
            
        # Check waypoint compatibility
        self._check_waypoint_compatibility(file_path)
        
        # Check action compatibility
        self._check_action_compatibility(file_path)
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def _check_file_exists(self, file_path: str) -> bool:
        """Check if file exists."""
        if not os.path.exists(file_path):
            self.errors.append(f"File does not exist: {file_path}")
            return False
        return True
    
    def _check_file_readable(self, file_path: str) -> bool:
        """Check if file is readable."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1)  # Try to read first character
            return True
        except PermissionError:
            self.errors.append(f"Permission denied: Cannot read {file_path}")
            return False
        except UnicodeDecodeError:
            self.errors.append(f"File encoding error: {file_path} is not valid UTF-8")
            return False
        except Exception as e:
            self.errors.append(f"File read error: {str(e)}")
            return False
    
    def _check_xml_valid(self, file_path: str) -> bool:
        """Check if file is valid XML."""
        try:
            ET.parse(file_path)
            return True
        except ET.ParseError as e:
            self.errors.append(f"Invalid XML: {str(e)}")
            return False
        except Exception as e:
            self.errors.append(f"XML parsing error: {str(e)}")
            return False
    
    def _check_wpml_structure(self, file_path: str) -> bool:
        """Check if file has proper WPML structure."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Check for KML namespace
            if not root.tag.startswith('{http://www.opengis.net/kml/2.2}'):
                self.errors.append("Missing or invalid KML namespace")
                return False
            
            # Check for WPML namespace in document
            wpml_ns = "http://www.dji.com/wpmz/1.0.6"
            wpml_elements = root.findall(f".//{{{wpml_ns}}}*")
            if not wpml_elements:
                self.errors.append("No WPML elements found - not a valid WPML file")
                return False
                
            return True
            
        except Exception as e:
            self.errors.append(f"Structure validation error: {str(e)}")
            return False
    
    def _check_waypoint_compatibility(self, file_path: str):
        """Check if waypoints are compatible with our scripts."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            kml_ns = "http://www.opengis.net/kml/2.2"
            wpml_ns = "http://www.dji.com/wpmz/1.0.6"
            
            # Find all waypoints (Placemark elements)
            placemarks = root.findall(f".//{{{kml_ns}}}Placemark")
            self.waypoint_count = len(placemarks)
            
            if self.waypoint_count == 0:
                self.errors.append("No waypoints found in file")
                return
            
            # Check for required waypoint structure
            compatible_waypoints = 0
            for i, placemark in enumerate(placemarks):
                if self._is_waypoint_compatible(placemark, wpml_ns):
                    compatible_waypoints += 1
                else:
                    self.warnings.append(f"Waypoint {i} may not be compatible with action scripts")
            
            if compatible_waypoints == 0:
                self.errors.append("No compatible waypoints found")
            elif compatible_waypoints < self.waypoint_count:
                self.warnings.append(f"Only {compatible_waypoints}/{self.waypoint_count} waypoints are compatible")
                
        except Exception as e:
            self.errors.append(f"Waypoint validation error: {str(e)}")
    
    def _is_waypoint_compatible(self, placemark, wpml_ns: str) -> bool:
        """Check if a single waypoint is compatible with our action scripts."""
        # Look for the insertion point our scripts use
        use_straight_line = placemark.find(f".//{{{wpml_ns}}}useStraightLine")
        if use_straight_line is None:
            return False
            
        # Check if it has the expected value
        if use_straight_line.text != "0":
            return False
            
        return True
    
    def _check_action_compatibility(self, file_path: str):
        """Check if existing actions are compatible."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            wpml_ns = "http://www.dji.com/wpmz/1.0.6"
            
            # Count existing actions
            actions = root.findall(f".//{{{wpml_ns}}}action")
            self.action_count = len(actions)
            
            if self.action_count > 0:
                self.warnings.append(f"File already contains {self.action_count} actions")
                
                # Check for action ID conflicts
                action_ids = []
                for action in actions:
                    action_id_elem = action.find(f"{{{wpml_ns}}}actionId")
                    if action_id_elem is not None:
                        try:
                            action_id = int(action_id_elem.text)
                            if action_id in action_ids:
                                self.warnings.append(f"Duplicate action ID found: {action_id}")
                            action_ids.append(action_id)
                        except ValueError:
                            self.warnings.append("Invalid action ID found")
                            
        except Exception as e:
            self.errors.append(f"Action validation error: {str(e)}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the validation results."""
        return {
            'waypoint_count': self.waypoint_count,
            'action_count': self.action_count,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'is_valid': len(self.errors) == 0
        }

def main():
    """Command line interface for the validator."""
    if len(sys.argv) != 2:
        print("Usage: python wpml_validator.py <wpml_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    validator = WPMLValidator()
    
    print(f"Validating WPML file: {file_path}")
    print("=" * 50)
    
    is_valid, errors, warnings = validator.validate_file(file_path)
    summary = validator.get_summary()
    
    # Print results
    if is_valid:
        print("✅ VALID: File is compatible with Drone WPML Editor")
    else:
        print("❌ INVALID: File has compatibility issues")
    
    print(f"\n📊 Summary:")
    print(f"   Waypoints: {summary['waypoint_count']}")
    print(f"   Existing actions: {summary['action_count']}")
    print(f"   Errors: {summary['error_count']}")
    print(f"   Warnings: {summary['warning_count']}")
    
    if errors:
        print(f"\n❌ Errors:")
        for error in errors:
            print(f"   • {error}")
    
    if warnings:
        print(f"\n⚠️  Warnings:")
        for warning in warnings:
            print(f"   • {warning}")
    
    if is_valid:
        print(f"\n🎉 File is ready to use with the Drone WPML Editor!")
    else:
        print(f"\n🔧 Please fix the errors before using this file.")
    
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
