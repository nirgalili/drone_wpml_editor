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
        
    def process_kmz(self, input_kmz_path, output_dir=None, output_filename=None):
        """
        Complete KMZ processing workflow
        
        Args:
            input_kmz_path: Path to input KMZ file
            output_dir: Directory to save output (default: same as input)
            output_filename: Custom output filename (default: DJI RC format)
        
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
            if not self._process_wpml():
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
    
    def _process_wpml(self):
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
            
            # Process the file using our existing logic
            processed_content = self._add_hover_photo_actions(content)
            
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
    
    def _add_hover_photo_actions(self, content):
        """Add hover and photo actions to WPML content"""
        try:
            # This uses the same logic as our existing hover_add_actions.py
            lines = content.split('\n')
            new_lines = []
            action_group_id = 0
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                
                # Look for insertion point
                if '<wpml:useStraightLine>0</wpml:useStraightLine>' in line:
                    # Add the hover + photo action block
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
<wpml:hoverTime>2</wpml:hoverTime>
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
                    
                    new_lines.append(action_block)
                    action_group_id += 1
            
            return '\n'.join(new_lines)
            
        except Exception as e:
            print(f"❌ Error adding actions: {str(e)}")
            return None
    
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
                # Note: GUI will handle the confirmation dialog
            
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
