#!/usr/bin/env python3
"""
Copy original/hover/waylines.wpml to working_hover.wpml and add a combined
hover+takePhoto action group after each <wpml:useStraightLine>0</wpml:useStraightLine>
block that does not already have a wpml:actionGroup immediately following.

This is text-based to preserve existing formatting and namespaces exactly.
"""
import sys
from pathlib import Path

def main():
    project_root = Path(__file__).resolve().parent
    src = project_root / "original" / "hover" / "waylines.wpml"
    dst = project_root / "working_hover.wpml"

    if not src.exists():
        print(f"❌ Source not found: {src}")
        sys.exit(1)

    content = src.read_text(encoding="utf-8")
    lines = content.split("\n")
    new_lines = []

    # Determine next actionGroupId by scanning existing IDs
    import re
    id_pattern = re.compile(r"<wpml:actionGroupId>(\d+)</wpml:actionGroupId>")
    existing_ids = [int(m.group(1)) for m in id_pattern.finditer(content)]
    next_id = (max(existing_ids) + 1) if existing_ids else 0

    added = 0

    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)

        if "<wpml:useStraightLine>0</wpml:useStraightLine>" in line:
            # Peek ahead a handful of lines to see if an actionGroup already follows
            has_group = False
            for j in range(i + 1, min(i + 12, len(lines))):
                scan = lines[j].strip()
                if scan.startswith("<wpml:actionGroup>") or scan.startswith("<ns1:actionGroup>"):
                    has_group = True
                    break
                # stop if we hit end of Placemark
                if scan.startswith("</Placemark>") or scan.startswith("</ns0:Placemark>"):
                    break

            if not has_group:
                # Find waypoint index for the comment (backwards search up to 30 lines)
                waypoint_index = None
                for k in range(max(0, i - 30), i + 1):
                    if "<wpml:index>" in lines[k]:
                        try:
                            waypoint_index = lines[k].split("<wpml:index>")[1].split("</wpml:index>")[0].strip()
                        except Exception:
                            waypoint_index = None
                        # don't break; prefer the closest one below
                if waypoint_index is None:
                    waypoint_index = "0"

                # Build block with exact formatting per user's spec
                block = [
                    f"        <!-- Action Group for Waypoint: {waypoint_index}'s Actions -->",
                    f"        <wpml:actionGroup>",
                    f"          <wpml:actionGroupId>{next_id}</wpml:actionGroupId>",
                    f"          <wpml:actionGroupStartIndex>{waypoint_index}</wpml:actionGroupStartIndex>",
                    f"          <wpml:actionGroupEndIndex>{waypoint_index}</wpml:actionGroupEndIndex>",
                    f"          <wpml:actionGroupMode>sequence</wpml:actionGroupMode>",
                    f"          <wpml:actionTrigger>",
                    f"            <wpml:actionTriggerType>reachPoint</wpml:actionTriggerType>",
                    f"          </wpml:actionTrigger>",
                    f"          <wpml:action>",
                    f"            <wpml:actionId>0</wpml:actionId>",
                    f"            <wpml:actionActuatorFunc>hover</wpml:actionActuatorFunc>",
                    f"            <wpml:actionActuatorFuncParam>",
                    f"              <wpml:hoverTime>2</wpml:hoverTime>",
                    f"            </wpml:actionActuatorFuncParam>",
                    f"          </wpml:action>",
                    f"          <wpml:action>",
                    f"            <wpml:actionId>1</wpml:actionId>",
                    f"            <wpml:actionActuatorFunc>takePhoto</wpml:actionActuatorFunc>",
                    f"            <wpml:actionActuatorFuncParam>",
                    f"              <wpml:payloadPositionIndex>0</wpml:payloadPositionIndex>",
                    f"              <wpml:fileSuffix/>",
                    f"              <wpml:useGlobalPayloadLensIndex>0</wpml:useGlobalPayloadLensIndex>",
                    f"            </wpml:actionActuatorFuncParam>",
                    f"          </wpml:action>",
                    f"        </wpml:actionGroup>",
                ]
                new_lines.extend(block)
                added += 1
                next_id += 1
        i += 1

    (project_root / "working_hover.wpml").write_text("\n".join(new_lines), encoding="utf-8")
    print(f"✅ Updated working file: {dst}")
    print(f"Added {added} combined hover+takePhoto action groups.")

if __name__ == "__main__":
    main()
