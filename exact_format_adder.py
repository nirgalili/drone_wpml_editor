#!/usr/bin/env python3
"""
Script to add photo actions using the EXACT format specified by the user.
Adds properly formatted action blocks after each <wpml:useStraightLine>0</wpml:useStraightLine> line.
"""

def add_exact_format_photos(input_file, output_file=None):
    """
    Add photo actions using the exact format specified by the user.
    """
    if output_file is None:
        output_file = input_file
    
    # Read the file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all waypoints that don't already have photo actions
    lines = content.split('\n')
    new_lines = []
    action_group_id = 4  # Start after existing action group IDs (0, 1, 2, 3)
    
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Check if this line contains <wpml:useStraightLine>0</wpml:useStraightLine>
        if '<wpml:useStraightLine>0</wpml:useStraightLine>' in line:
            # Check if the next few lines already contain an actionGroup
            has_action_group = False
            for j in range(i+1, min(i+10, len(lines))):
                if '<wpml:actionGroup>' in lines[j] or '<ns1:actionGroup>' in lines[j]:
                    has_action_group = True
                    break
            
            # If no action group exists, add one using the EXACT format
            if not has_action_group:
                # Find the waypoint index for the comment
                waypoint_index = "Unknown"
                for k in range(max(0, i-20), i):
                    if '<wpml:index>' in lines[k]:
                        waypoint_index = lines[k].split('<wpml:index>')[1].split('</wpml:index>')[0]
                        break
                    elif '<ns1:index>' in lines[k]:
                        waypoint_index = lines[k].split('<ns1:index>')[1].split('</ns1:index>')[0]
                        break
                
                # Add the photo action block using the EXACT format provided by user
                photo_block = f"""        <!-- Action Group for Waypoint: {waypoint_index}'s Actions -->
        <wpml:actionGroup>
          <wpml:actionGroupId>{action_group_id}</wpml:actionGroupId>
          <wpml:actionGroupStartIndex>{waypoint_index}</wpml:actionGroupStartIndex>
          <wpml:actionGroupEndIndex>{waypoint_index}</wpml:actionGroupEndIndex>
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
        </wpml:actionGroup>"""
                
                new_lines.append(photo_block)
                action_group_id += 1
                print(f"Added properly formatted photo action for waypoint {waypoint_index}")
        
        i += 1
    
    # Write the modified content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print(f"\nModified WPML file saved to: {output_file}")

if __name__ == "__main__":
    # First, restore the original file from the old folder
    print("Restoring original file...")
    with open('old/waylines.wpml', 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    with open('waylines.wpml', 'w', encoding='utf-8') as f:
        f.write(original_content)
    
    print("Adding photo actions using EXACT format...")
    add_exact_format_photos('waylines.wpml', 'waylines_exact_format.wpml')
    
    # Replace the main file
    with open('waylines_exact_format.wpml', 'r', encoding='utf-8') as f:
        new_content = f.read()
    
    with open('waylines.wpml', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Done! waylines.wpml now has properly formatted photo actions for all waypoints.")
