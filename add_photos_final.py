#!/usr/bin/env python3
"""
Add properly formatted photo actions to waylines.wpml using the exact format specified.
Works with the original file format and adds photo actions after each <wpml:useStraightLine>0</wpml:useStraightLine> line.
"""

def add_photos_final():
    """
    Add photo actions using the exact format specified by the user.
    """
    # Read the current waylines.wpml file (copied from original)
    with open('waylines.wpml', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    action_group_id = 4  # Start after existing action group IDs (0, 1, 2, 3)
    added_count = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Check if this line contains <wpml:useStraightLine>0</wpml:useStraightLine>
        if '<wpml:useStraightLine>0</wpml:useStraightLine>' in line:
            # Check if the next few lines already contain a properly formatted actionGroup
            has_proper_action_group = False
            for j in range(i+1, min(i+15, len(lines))):
                if '<wpml:actionGroup>' in lines[j] and 'actionGroupId>' in lines[j+1]:
                    has_proper_action_group = True
                    break
            
            # If no properly formatted action group exists, add one
            if not has_proper_action_group:
                # Find the waypoint index for the comment
                waypoint_index = "Unknown"
                for k in range(max(0, i-20), i):
                    if '<wpml:index>' in lines[k]:
                        waypoint_index = lines[k].split('<wpml:index>')[1].split('</wpml:index>')[0]
                        break
                
                # Add the photo action block using the EXACT format specified by user
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
                added_count += 1
                print(f"Added properly formatted photo action for waypoint {waypoint_index}")
        
        i += 1
    
    # Write the modified content back to waylines.wpml
    with open('waylines.wpml', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print(f"\n✅ Successfully added {added_count} photo actions!")
    print(f"Modified waylines.wpml with properly formatted photo actions.")
    print(f"Original file is safely preserved in original/waylines.wpml")

if __name__ == "__main__":
    print("Adding properly formatted photo actions to waylines.wpml...")
    print("Using the exact format you specified...")
    add_photos_final()
