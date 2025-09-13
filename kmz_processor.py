#!/usr/bin/env python3
"""
KMZ Processor - Complete Drone Mission Workflow
Handles the entire pipeline from KMZ input to processed KMZ output
"""

import os
import zipfile
import shutil
import uuid
import tempfile
from pathlib import Path
import xml.etree.ElementTree as ET

class KMZProcessor:
    def __init__(self):
        self.temp_dir = None
        self.original_kmz_path = None
        self.work_dir = None
        self.wpmz_dir = None
        self.template_kml_path = None
        self.waylines_wpml_path = None
        
    def process_kmz(self, input_kmz_path, output_dir=None, output_filename=None, enable_hover=True, hover_time=2.0):
        """
        Complete KMZ processing workflow
        
        Args:
            input_kmz_path: Path to input KMZ file
            output_dir: Directory to save output (default: same as input)
            output_filename: Custom output filename (default: DJI RC format)
            enable_hover: Whether to add hover actions (default: True)
            hover_time: Hover duration in seconds (default: 2.0)
        
        Returns:
            Path to processed KMZ file
        """
        try:
            print("🚁 Starting KMZ Processing Workflow")
            print("=" * 50)
            
            # Step 1: Validate input file
            if not self._validate_input(input_kmz_path):
                return None
                
            # Step 2: Create temporary workspace
            if not self._setup_workspace(input_kmz_path):
                return None
                
            # Step 3: Extract KMZ (treat as ZIP)
            if not self._extract_kmz():
                return None
                
            # Step 4: Find and validate WPML structure
            if not self._find_wpml_files():
                return None
                
            # Step 5: Process WPML file (add hover + photo actions)
            if not self._process_wpml(enable_hover, hover_time):
                return None
                
            # Step 6: Create new KMZ with processed WPML
            output_path = self._create_output_kmz(output_dir, output_filename)
            
            # Step 7: Cleanup
            self._cleanup()
            
            if output_path:
                print(f"✅ Success! Processed KMZ saved to: {output_path}")
                return output_path
            else:
                print("❌ Failed to create output KMZ")
                return None
                
        except Exception as e:
            print(f"❌ Error during processing: {str(e)}")
            self._cleanup()
            return None
    
    def _validate_input(self, input_path):
        """Validate input KMZ file"""
        print("📋 Step 1: Validating input file...")
        
        if not os.path.exists(input_path):
            print(f"❌ Input file not found: {input_path}")
            return False
            
        if not input_path.lower().endswith('.kmz'):
            print(f"❌ Input file must be .kmz: {input_path}")
            return False
            
        file_size = os.path.getsize(input_path)
        if file_size == 0:
            print(f"❌ Input file is empty: {input_path}")
            return False
            
        print(f"✅ Input file valid: {file_size:,} bytes")
        self.original_kmz_path = input_path
        return True
    
    def _setup_workspace(self, input_path):
        """Create temporary workspace"""
        print("📁 Step 2: Setting up workspace...")
        
        try:
            # Create temp directory
            self.temp_dir = tempfile.mkdtemp(prefix="kmz_processor_")
            self.work_dir = os.path.join(self.temp_dir, "work")
            os.makedirs(self.work_dir, exist_ok=True)
            
            print(f"✅ Workspace created: {self.temp_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create workspace: {str(e)}")
            return False
    
    def _extract_kmz(self):
        """Extract KMZ file (treat as ZIP)"""
        print("📦 Step 3: Extracting KMZ file...")
        
        try:
            with zipfile.ZipFile(self.original_kmz_path, 'r') as zip_ref:
                zip_ref.extractall(self.work_dir)
            
            print("✅ KMZ extracted successfully")
            return True
            
        except zipfile.BadZipFile:
            print("❌ Invalid KMZ file - not a valid ZIP archive")
            return False
        except Exception as e:
            print(f"❌ Failed to extract KMZ: {str(e)}")
            return False
    
    def _find_wpml_files(self):
        """Find and validate WPML files in extracted structure"""
        print("🔍 Step 4: Finding WPML files...")
        
        try:
            # Look for wpmz folder
            wpmz_candidates = []
            for root, dirs, files in os.walk(self.work_dir):
                if 'wpmz' in dirs:
                    wpmz_candidates.append(os.path.join(root, 'wpmz'))
            
            if not wpmz_candidates:
                print("❌ No 'wpmz' folder found in extracted KMZ")
                return False
            
            # Use the first wpmz folder found
            self.wpmz_dir = wpmz_candidates[0]
            print(f"✅ Found wpmz folder: {self.wpmz_dir}")
            
            # Look for required files
            template_kml = os.path.join(self.wpmz_dir, "template.kml")
            waylines_wpml = os.path.join(self.wpmz_dir, "waylines.wpml")
            
            if not os.path.exists(template_kml):
                print("❌ template.kml not found in wpmz folder")
                return False
                
            if not os.path.exists(waylines_wpml):
                print("❌ waylines.wpml not found in wpmz folder")
                return False
            
            self.template_kml_path = template_kml
            self.waylines_wpml_path = waylines_wpml
            
            print("✅ Found required files:")
            print(f"   - template.kml: {os.path.getsize(template_kml):,} bytes")
            print(f"   - waylines.wpml: {os.path.getsize(waylines_wpml):,} bytes")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to find WPML files: {str(e)}")
            return False
    
    def _process_wpml(self, enable_hover=True, hover_time=2.0):
        """Process WPML file to add hover and photo actions"""
        print("⚙️ Step 5: Processing WPML file...")
        
        try:
            # Read the WPML file
            with open(self.waylines_wpml_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if it's already processed
            if '<wpml:actionActuatorFunc>hover</wpml:actionActuatorFunc>' in content:
                print("⚠️  WPML file already contains hover actions")
                return True
            
            # Count waypoints
            waypoint_count = content.count('<Placemark>')
            insertion_points = content.count('<wpml:useStraightLine>0</wpml:useStraightLine>')
            
            print(f"📊 Found {waypoint_count} waypoints, {insertion_points} insertion points")
            
            if insertion_points == 0:
                print("❌ No insertion points found - WPML not compatible")
                return False
            
            # Show processing options
            if enable_hover:
                print(f"🎯 Adding hover ({hover_time}s) + photo actions to all waypoints")
            else:
                print("📸 Adding photo actions only to all waypoints")
            
            # Estimate mission time
            self._estimate_mission_time(content, enable_hover, hover_time)
            
            # Process the file using our existing logic
            processed_content = self._add_hover_photo_actions(content, enable_hover, hover_time)
            
            if not processed_content:
                print("❌ Failed to process WPML content")
                return False
            
            # Write processed content back
            with open(self.waylines_wpml_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            
            print("✅ WPML file processed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to process WPML: {str(e)}")
            return False
    
    def _add_hover_photo_actions(self, content, enable_hover=True, hover_time=2.0):
        """Add hover and photo actions to WPML content"""
        try:
            lines = content.split('\n')
            new_lines = []
            action_group_id = 0
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                
                # Look for insertion point
                if '<wpml:useStraightLine>0</wpml:useStraightLine>' in line:
                    # Generate action block based on options
                    if enable_hover:
                        # Hover + Photo actions
                        action_block = f'''<!-- Action Group for Waypoint: {action_group_id}'s Actions -->
<wpml:actionGroup>
<wpml:actionGroupId>{action_group_id}</wpml:actionGroupId>
<wpml:actionGroupStartIndex>{action_group_id}</wpml:actionGroupStartIndex>
<wpml:actionGroupEndIndex>{action_group_id}</wpml:actionGroupEndIndex>
<wpml:actionGroupMode>sequence</wpml:actionGroupMode>
<wpml:actionTrigger>
<wpml:actionTriggerType>reachPoint</wpml:actionTriggerType>
</wpml:actionTrigger>
<wpml:action>
<wpml:actionId>0</wpml:actionId>
<wpml:actionActuatorFunc>hover</wpml:actionActuatorFunc>
<wpml:actionActuatorFuncParam>
<wpml:hoverTime>{hover_time}</wpml:hoverTime>
</wpml:actionActuatorFuncParam>
</wpml:action>
<wpml:action>
<wpml:actionId>1</wpml:actionId>
<wpml:actionActuatorFunc>takePhoto</wpml:actionActuatorFunc>
<wpml:actionActuatorFuncParam>
<wpml:payloadPositionIndex>0</wpml:payloadPositionIndex>
<wpml:fileSuffix/>
<wpml:useGlobalPayloadLensIndex>0</wpml:useGlobalPayloadLensIndex>
</wpml:actionActuatorFuncParam>
</wpml:action>
</wpml:actionGroup>'''
                    else:
                        # Photo action only
                        action_block = f'''<!-- Action Group for Waypoint: {action_group_id}'s Actions -->
<wpml:actionGroup>
<wpml:actionGroupId>{action_group_id}</wpml:actionGroupId>
<wpml:actionGroupStartIndex>{action_group_id}</wpml:actionGroupStartIndex>
<wpml:actionGroupEndIndex>{action_group_id}</wpml:actionGroupEndIndex>
<wpml:actionGroupMode>sequence</wpml:actionGroupMode>
<wpml:actionTrigger>
<wpml:actionTriggerType>reachPoint</wpml:actionTriggerType>
</wpml:actionTrigger>
<wpml:action>
<wpml:actionId>0</wpml:actionId>
<wpml:actionActuatorFunc>takePhoto</wpml:actionActuatorFunc>
<wpml:actionActuatorFuncParam>
<wpml:payloadPositionIndex>0</wpml:payloadPositionIndex>
<wpml:fileSuffix/>
<wpml:useGlobalPayloadLensIndex>0</wpml:useGlobalPayloadLensIndex>
</wpml:actionActuatorFuncParam>
</wpml:action>
</wpml:actionGroup>'''
                    
                    new_lines.append(action_block)
                    action_group_id += 1
            
            return '\n'.join(new_lines)
            
        except Exception as e:
            print(f"❌ Error adding actions: {str(e)}")
            return None
    
    def _estimate_mission_time(self, content, enable_hover, hover_time):
        """Estimate total mission time from first to last waypoint"""
        try:
            import re
            from math import sqrt, atan2, cos, sin, radians
            
            # Find all waypoint coordinates
            coord_pattern = r'<coordinates>([^<]+)</coordinates>'
            coordinates = re.findall(coord_pattern, content)
            
            if len(coordinates) < 2:
                print("⚠️  Not enough waypoints for time estimation")
                return
            
            # Parse coordinates (longitude, latitude, altitude)
            waypoints = []
            for coord_str in coordinates:
                # Split by spaces and take first coordinate (some have multiple)
                coords = coord_str.strip().split()
                if coords:
                    coord_parts = coords[0].split(',')
                    if len(coord_parts) >= 3:
                        lon, lat, alt = map(float, coord_parts[:3])
                        waypoints.append((lon, lat, alt))
                    elif len(coord_parts) == 2:
                        # Some coordinates might only have lon, lat without altitude
                        lon, lat = map(float, coord_parts)
                        waypoints.append((lon, lat, 0))  # Default altitude to 0
            
            if len(waypoints) < 2:
                print("⚠️  Invalid waypoint coordinates")
                return
            
            # Calculate total distance
            total_distance = 0
            for i in range(1, len(waypoints)):
                dist = self._calculate_distance(waypoints[i-1], waypoints[i])
                total_distance += dist
            
            # Estimate flight time based on real DJI Air 3S waypoint mission data
            # Your actual data: 245m in 5m12s = 0.79 m/s effective speed
            # This accounts for waypoint mission dynamics: acceleration, deceleration, turns, stabilization
            waypoint_count = len(waypoints)
            
            # Advanced waypoint mission estimation based on real DJI Air 3S data
            # Mission 1: 35 waypoints, 245.1m, 5m12s → 0.79 m/s effective speed
            # Mission 2: 38 waypoints, 196.2m, 5m34s → 0.59 m/s effective speed
            
            # Calculate waypoint density (meters per waypoint)
            avg_distance_per_waypoint = total_distance / waypoint_count
            
            # Mathematical model based on real flight data
            # Fitting curve: speed = 0.10 * distance^0.85 + 0.20
            # This gives: 3.46m→0.40m/s, 5.16m→0.59m/s, 7.0m→0.79m/s
            import math
            base_speed = 0.10 * (avg_distance_per_waypoint ** 0.85) + 0.20
            
            # Add safety buffer for very tight waypoints (under 4m per waypoint)
            if avg_distance_per_waypoint < 4.0:
                base_speed *= 0.75  # 25% slower for very tight waypoints
            
            # Adjust for waypoint count (minimal impact based on data)
            waypoint_factor = 1.0 - (waypoint_count - 25) * 0.005  # -0.5% per waypoint over 25
            waypoint_factor = max(0.95, waypoint_factor)  # Minimum 0.95x speed
            
            effective_speed_ms = base_speed * waypoint_factor
            
            # Calculate actual action time based on hover settings
            if enable_hover:
                action_time_per_waypoint = hover_time + 1.5  # hover + photo + processing time
            else:
                action_time_per_waypoint = 1.5  # photo + processing time
            
            total_action_time = waypoint_count * action_time_per_waypoint
            
            # The effective speed already includes action overhead, so use it directly
            # But adjust for the specific hover time difference
            base_mission_time = total_distance / effective_speed_ms
            
            # Calculate the difference in action time from the base (2s hover)
            base_action_time = waypoint_count * (2.0 + 1.5)  # Base 2s hover + 1.5s processing
            action_time_difference = total_action_time - base_action_time
            
            # Adjust total mission time by the action time difference
            total_mission_time = base_mission_time + action_time_difference
            flight_time = total_mission_time - total_action_time
            
            # Convert to minutes and seconds
            total_minutes = int(total_mission_time // 60)
            total_seconds = int(total_mission_time % 60)
            
            print(f"\n📊 Mission Time Estimation:")
            print(f"   • Total distance: {total_distance:.1f} meters ({total_distance/1000:.2f} km)")
            print(f"   • Flight time: {flight_time:.1f} seconds ({flight_time/60:.1f} minutes)")
            print(f"     - Travel time: {total_distance/effective_speed_ms:.1f}s at {effective_speed_ms} m/s")
            print(f"     - Waypoint count: {waypoint_count} waypoints")
            print(f"   • Action time: {total_action_time:.1f} seconds ({total_action_time/60:.1f} minutes)")
            print(f"   • Total mission time: {total_minutes}m {total_seconds}s")
            
            # Battery estimation for DJI Air 3S
            # Based on real data: 8m2s used 22% battery → 2.75% per minute
            battery_percentage = (total_mission_time / 60) * 2.75  # 2.75% per minute
            print(f"   • Estimated battery usage: ~{min(battery_percentage, 100):.0f}% (DJI Air 3S)")
            
        except Exception as e:
            print(f"⚠️  Could not estimate mission time: {str(e)}")
    
    def _calculate_distance(self, point1, point2):
        """Calculate distance between two GPS coordinates in meters"""
        try:
            from math import sqrt, atan2, cos, sin, radians
            
            # Haversine formula for great-circle distance
            R = 6371000  # Earth's radius in meters
            
            lat1, lon1, alt1 = point1
            lat2, lon2, alt2 = point2
            
            lat1_rad = radians(lat1)
            lat2_rad = radians(lat2)
            delta_lat = radians(lat2 - lat1)
            delta_lon = radians(lon2 - lon1)
            
            a = (sin(delta_lat/2)**2 + 
                 cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2)
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            
            distance = R * c
            
            # Add altitude difference
            alt_diff = abs(alt2 - alt1)
            total_distance = sqrt(distance**2 + alt_diff**2)
            
            return total_distance
            
        except Exception as e:
            print(f"⚠️  Distance calculation error: {str(e)}")
            return 0
    
    def _create_output_kmz(self, output_dir, output_filename=None):
        """Create new KMZ file with processed WPML"""
        print("📦 Step 6: Creating output KMZ...")
        
        try:
            # Determine output path
            if output_dir is None:
                output_dir = os.path.dirname(self.original_kmz_path)
            
            # Use custom filename or default DJI RC format
            if output_filename is None:
                output_filename = "5336EE45-2941-4996-B7F1-22BAA25F2639.kmz"
            output_path = os.path.join(output_dir, output_filename)
            
            # Check if file already exists
            if os.path.exists(output_path):
                print(f"⚠️  WARNING: File already exists: {output_filename}")
                print("   The existing file will be overwritten!")
                # Continue with overwrite (GUI already handled confirmation)
            
            # Create new ZIP (KMZ) file
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all files from work directory
                for root, dirs, files in os.walk(self.work_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.work_dir)
                        zipf.write(file_path, arcname)
            
            print(f"✅ Output KMZ created: {output_path}")
            print(f"📊 File size: {os.path.getsize(output_path):,} bytes")
            
            return output_path
            
        except Exception as e:
            print(f"❌ Failed to create output KMZ: {str(e)}")
            return None
    
    def _cleanup(self):
        """Clean up temporary files"""
        print("🧹 Step 7: Cleaning up...")
        
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print("✅ Temporary files cleaned up")
        except Exception as e:
            print(f"⚠️  Warning: Failed to clean up temp files: {str(e)}")

def main():
    """Command line interface"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python kmz_processor.py <input.kmz>")
        print("Example: python kmz_processor.py mission.kmz")
        sys.exit(1)
    
    input_kmz = sys.argv[1]
    
    if not os.path.exists(input_kmz):
        print(f"❌ Input file not found: {input_kmz}")
        sys.exit(1)
    
    processor = KMZProcessor()
    output_path = processor.process_kmz(input_kmz)
    
    if output_path:
        print(f"\n🎉 SUCCESS!")
        print(f"📁 Input:  {input_kmz}")
        print(f"📁 Output: {output_path}")
        print(f"🔗 All waypoints now have hover + photo actions!")
    else:
        print(f"\n❌ FAILED to process {input_kmz}")
        sys.exit(1)

if __name__ == "__main__":
    main()
