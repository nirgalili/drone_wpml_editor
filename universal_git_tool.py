#!/usr/bin/env python3
"""
Universal Git Tool - Works with any Git repository
Copy this file to any project folder to manage Git operations
"""

import subprocess
import sys
import os
import json
from datetime import datetime

def run_git_command(command, timeout=30):
    """Run a git command safely"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_git_repo():
    """Check if current directory is a Git repository"""
    success, _, _ = run_git_command("git status --porcelain")
    return success

def get_repo_info():
    """Get repository information"""
    info = {}
    
    # Get remote URL
    success, stdout, _ = run_git_command("git remote get-url origin")
    if success:
        info['remote_url'] = stdout.strip()
    else:
        info['remote_url'] = "No remote configured"
    
    # Get current branch
    success, stdout, _ = run_git_command("git branch --show-current")
    if success:
        info['current_branch'] = stdout.strip()
    else:
        info['current_branch'] = "Unknown"
    
    # Get last commit
    success, stdout, _ = run_git_command("git log -1 --oneline")
    if success:
        info['last_commit'] = stdout.strip()
    else:
        info['last_commit'] = "No commits"
    
    return info

def show_status():
    """Show current Git status"""
    print("📊 Git Repository Status")
    print("=" * 40)
    
    if not check_git_repo():
        print("❌ Not a Git repository")
        return False
    
    info = get_repo_info()
    print(f"🌐 Remote: {info['remote_url']}")
    print(f"🌿 Branch: {info['current_branch']}")
    print(f"📝 Last commit: {info['last_commit']}")
    
    # Show changes
    success, stdout, stderr = run_git_command("git status --porcelain")
    if success:
        if stdout.strip():
            print(f"\n📋 Changes:\n{stdout}")
        else:
            print("\n✅ Working directory clean")
    
    return True

def add_and_commit(message=None):
    """Add all files and commit"""
    if not message:
        message = f"Update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    print(f"📁 Adding files...")
    success, stdout, stderr = run_git_command("git add .")
    if not success:
        print(f"❌ Failed to add files: {stderr}")
        return False
    
    print(f"💾 Committing: {message}")
    success, stdout, stderr = run_git_command(f'git commit -m "{message}"')
    if not success:
        print(f"❌ Failed to commit: {stderr}")
        return False
    
    print("✅ Committed successfully")
    return True

def push_to_github():
    """Push to GitHub"""
    print("🚀 Pushing to GitHub...")
    success, stdout, stderr = run_git_command("git push origin main")
    if not success:
        # Try master branch if main fails
        success, stdout, stderr = run_git_command("git push origin master")
        if not success:
            print(f"❌ Failed to push: {stderr}")
            return False
    
    print("✅ Successfully pushed to GitHub!")
    return True

def quick_update():
    """Quick update: add, commit, push"""
    print("🔄 Quick Git Update")
    print("=" * 30)
    
    if not check_git_repo():
        print("❌ Not a Git repository")
        return False
    
    # Get commit message from user
    message = input("Enter commit message (or press Enter for auto): ").strip()
    if not message:
        message = f"Update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Add and commit
    if not add_and_commit(message):
        return False
    
    # Push
    if not push_to_github():
        return False
    
    print("\n🎉 Repository updated successfully!")
    return True

def main():
    print("Universal Git Tool")
    print("=" * 30)
    print("1. Show status")
    print("2. Quick update (add + commit + push)")
    print("3. Add and commit only")
    print("4. Push only")
    print("5. Exit")
    
    while True:
        choice = input("\nChoose option (1-5): ").strip()
        
        if choice == "1":
            show_status()
        elif choice == "2":
            quick_update()
        elif choice == "3":
            message = input("Enter commit message: ").strip()
            if message:
                add_and_commit(message)
        elif choice == "4":
            push_to_github()
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
