#!/usr/bin/env python3
"""
Git Update Script - Updates GitHub repository from Python
No terminal commands needed!
"""

import subprocess
import sys
import os

def run_git_command(command):
    """Run a git command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def update_git():
    """Update Git repository with new files"""
    print("🔄 Updating Git repository...")
    print("=" * 50)
    
    # Check if we're in a git repository
    success, stdout, stderr = run_git_command("git status --porcelain")
    if not success:
        print("❌ Not a Git repository or Git not available")
        print(f"Error: {stderr}")
        return False
    
    # Add all files
    print("📁 Adding files to Git...")
    success, stdout, stderr = run_git_command("git add .")
    if not success:
        print(f"❌ Failed to add files: {stderr}")
        return False
    print("✅ Files added successfully")
    
    # Check what files are staged
    success, stdout, stderr = run_git_command("git status --porcelain")
    if success and stdout.strip():
        print(f"📋 Files to commit:\n{stdout}")
    else:
        print("ℹ️  No changes to commit")
        return True
    
    # Commit changes
    print("\n💾 Committing changes...")
    commit_message = "Added WPML file validators for compatibility checking"
    success, stdout, stderr = run_git_command(f'git commit -m "{commit_message}"')
    if not success:
        print(f"❌ Failed to commit: {stderr}")
        return False
    print("✅ Changes committed successfully")
    
    # Push to GitHub
    print("\n🚀 Pushing to GitHub...")
    success, stdout, stderr = run_git_command("git push origin main")
    if not success:
        print(f"❌ Failed to push: {stderr}")
        print("💡 You may need to authenticate with GitHub")
        return False
    print("✅ Successfully pushed to GitHub!")
    
    return True

def main():
    print("GitHub Update Tool")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Not in the drone_wpml_editor directory")
        return
    
    if not os.path.exists(".git"):
        print("❌ Not a Git repository")
        return
    
    # Update Git
    success = update_git()
    
    if success:
        print("\n🎉 Repository updated successfully!")
        print("🔗 Check your repository: https://github.com/nirgalili/drone_wpml_editor")
    else:
        print("\n❌ Update failed - check the errors above")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
