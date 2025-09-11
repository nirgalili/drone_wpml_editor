#!/usr/bin/env python3
"""
Simple Git Update - Updates repository with new files
"""

import subprocess
import os
import sys

def run_command(cmd):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout, result.stderr
    except:
        return False, "", "Command failed"

def main():
    print("🔄 Updating Git Repository...")
    print("=" * 40)
    
    # Check if we're in a git repo
    success, _, _ = run_command("git status --porcelain")
    if not success:
        print("❌ Not a Git repository")
        return
    
    # Add all files
    print("📁 Adding files...")
    success, stdout, stderr = run_command("git add .")
    if not success:
        print(f"❌ Failed to add files: {stderr}")
        return
    print("✅ Files added")
    
    # Commit
    print("💾 Committing...")
    commit_msg = "Added complete KMZ processing workflow with GUI"
    success, stdout, stderr = run_command(f'git commit -m "{commit_msg}"')
    if not success:
        print(f"❌ Failed to commit: {stderr}")
        return
    print("✅ Committed")
    
    # Push
    print("🚀 Pushing to GitHub...")
    success, stdout, stderr = run_command("git push origin main")
    if not success:
        print(f"❌ Failed to push: {stderr}")
        print("💡 You may need to authenticate")
        return
    print("✅ Pushed to GitHub")
    
    print("\n🎉 Repository updated successfully!")
    print("🔗 Check: https://github.com/nirgalili/drone_wpml_editor")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
