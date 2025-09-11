#!/usr/bin/env python3
"""
Simple Git Tool - Guided Git Workflow
Walks you through each step automatically
"""

import subprocess
import os
import sys

def run_command(cmd):
    """Run a command safely"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return result.returncode == 0, result.stdout, result.stderr
    except:
        return False, "", "Command failed"

def print_step(step_num, title):
    """Print a step header"""
    print(f"\n{'='*50}")
    print(f"STEP {step_num}: {title}")
    print(f"{'='*50}")

def wait_for_user():
    """Wait for user to press Enter"""
    input("\nPress Enter to continue...")

def main():
    print("🚀 Simple Git Update Tool")
    print("This will guide you through updating your GitHub repository")
    print("\nWhat this tool will do:")
    print("1. Check current status")
    print("2. Add all files")
    print("3. Commit changes")
    print("4. Push to GitHub")
    
    wait_for_user()
    
    # Step 1: Check if Git repository
    print_step(1, "Checking Git Repository")
    
    success, stdout, stderr = run_command("git status --porcelain")
    if not success:
        print("❌ This is not a Git repository!")
        print("Make sure you're in the right folder.")
        wait_for_user()
        return
    
    print("✅ Git repository found")
    
    # Show current status
    success, stdout, stderr = run_command("git status --short")
    if success and stdout.strip():
        print(f"\n📋 Files to be updated:")
        print(stdout)
    else:
        print("\n✅ No changes to commit")
        wait_for_user()
        return
    
    wait_for_user()
    
    # Step 2: Add files
    print_step(2, "Adding Files to Git")
    
    success, stdout, stderr = run_command("git add .")
    if not success:
        print(f"❌ Failed to add files: {stderr}")
        wait_for_user()
        return
    
    print("✅ All files added successfully")
    wait_for_user()
    
    # Step 3: Commit
    print_step(3, "Committing Changes")
    
    commit_message = "Updated Drone KMZ Processor with complete workflow"
    print(f"Commit message: {commit_message}")
    
    success, stdout, stderr = run_command(f'git commit -m "{commit_message}"')
    if not success:
        print(f"❌ Failed to commit: {stderr}")
        wait_for_user()
        return
    
    print("✅ Changes committed successfully")
    wait_for_user()
    
    # Step 4: Push to GitHub
    print_step(4, "Pushing to GitHub")
    
    print("Pushing to GitHub...")
    success, stdout, stderr = run_command("git push origin main")
    if not success:
        print(f"❌ Failed to push: {stderr}")
        print("\n💡 This might be an authentication issue.")
        print("You may need to sign in to GitHub in your browser.")
        wait_for_user()
        return
    
    print("✅ Successfully pushed to GitHub!")
    
    # Success message
    print(f"\n{'='*50}")
    print("🎉 SUCCESS! Repository Updated!")
    print(f"{'='*50}")
    print("✅ All files added")
    print("✅ Changes committed")
    print("✅ Pushed to GitHub")
    print(f"\n🔗 Check your repository:")
    print("https://github.com/nirgalili/drone_wpml_editor")
    
    wait_for_user()

if __name__ == "__main__":
    main()
