#!/usr/bin/env python3
"""
SwarmTunnel Uninstall Script

This script safely removes SwarmUI repository and cloudflared files that were installed
by the SwarmTunnel installer. It handles Windows permission issues that can prevent
normal deletion of Git repositories.
"""

import os
import sys
import platform
import subprocess
import shutil
import time

# Configuration - should match install.py
SWARMUI_DIR = os.environ.get("SWARMUI_DIR", "SwarmUI").strip()
CLOUD_DIR = os.environ.get("SWARMTUNNEL_CLOUDFLARED_DIR", "cloudflared")
LOG_DIR = os.environ.get("SWARMTUNNEL_LOG_DIR", "logs")


def fix_windows_permissions_aggressive(directory):
    """Aggressive Windows permission fixing specifically for Git repositories"""
    if platform.system().lower() != "windows":
        return True
    
    try:
        # Get current user
        import getpass
        target_user = os.environ.get('USERNAME', getpass.getuser())
        
        # Step 1: Kill any processes that might be holding handles
        try:
            subprocess.run(["taskkill", "/F", "/IM", "git.exe"], shell=True, capture_output=True, text=True)
            subprocess.run(["taskkill", "/F", "/IM", "cmd.exe"], shell=True, capture_output=True, text=True)
            time.sleep(1)  # Give processes time to terminate
        except Exception:
            pass

        # Step 2: Remove ALL attributes aggressively
        try:
            # Remove attributes from all files and directories
            subprocess.run(f'attrib -R -S -H -A "{directory}\\*.*" /S', shell=True, capture_output=True, text=True)
            subprocess.run(f'attrib -R -S -H -A "{directory}" /D', shell=True, capture_output=True, text=True)
            print("   ✓ Removed file attributes")
        except Exception:
            pass

        # Step 3: Take ownership with elevation
        try:
            temp_dir = os.environ.get('TEMP', os.environ.get('TMP', '/tmp'))
            batch_path = os.path.join(temp_dir, f"swarmtunnel_uninstall_{os.getpid()}.bat")
            
            with open(batch_path, 'w', encoding='utf-8') as bf:
                bf.write('@echo off\r\n')
                bf.write('echo Aggressive permission fix for uninstall...\r\n')
                
                # Kill any remaining processes
                bf.write('taskkill /F /IM git.exe 2>nul\r\n')
                bf.write('taskkill /F /IM cmd.exe 2>nul\r\n')
                bf.write('timeout /t 2 /nobreak >nul\r\n')
                
                # Remove all attributes
                bf.write(f'attrib -R -S -H -A "{directory}\\*.*" /S\r\n')
                bf.write(f'attrib -R -S -H -A "{directory}" /D\r\n')
                
                # Take ownership
                bf.write(f'takeown /F "{directory}" /R /D Y\r\n')
                
                # Grant full control to current user
                bf.write(f'icacls "{directory}" /grant "{target_user}:(OI)(CI)F" /T /C\r\n')
                
                # Grant Everyone full control as fallback
                bf.write(f'icacls "{directory}" /grant Everyone:(OI)(CI)F /T /C\r\n')
                
                bf.write('echo Permission fix completed.\r\n')
                bf.write('exit /b 0\r\n')

            # Run elevated
            ps_cmd = (
                'powershell -NoProfile -Command "Start-Process cmd.exe -ArgumentList \'/c \"' +
                batch_path.replace('"', '\\"') + '\"\' -Verb RunAs -Wait"'
            )
            
            proc = subprocess.run(ps_cmd, shell=True)
            
            # Cleanup batch file
            try:
                os.remove(batch_path)
            except Exception:
                pass
                
            if proc.returncode == 0:
                return True
                
        except Exception as e:
            print(f"   ⚠ Could not run elevated permission fix: {e}")
            
        return False
        
    except Exception as e:
        print(f"   ❌ Permission fix failed: {e}")
        return False


def remove_directory_safely(directory, name="directory"):
    """Safely remove a directory with comprehensive error handling"""
    if not os.path.exists(directory):
        print(f"✅ {name} does not exist, skipping...")
        return True
        
    print(f"🗑️ Removing {name} ({directory})...")
    
    # On Windows, try aggressive permission fixing first
    if platform.system().lower() == "windows":
        fix_windows_permissions_aggressive(directory)
    
    # Try multiple removal strategies
    strategies = [
        ("Standard shutil.rmtree", lambda: shutil.rmtree(directory)),
        ("Force removal with rmdir", lambda: subprocess.run(["rmdir", "/S", "/Q", directory], shell=True, check=True)),
    ]
    
    for strategy_name, strategy_func in strategies:
        try:
            print(f"   Trying {strategy_name}...")
            strategy_func()
            print(f"   ✅ {strategy_name} succeeded")
            return True
        except Exception as e:
            print(f"   ❌ {strategy_name} failed: {e}")
            continue
    
    # If all strategies failed, provide manual instructions
    print(f"   ❌ Could not remove {name} automatically")
    print(f"   📋 Manual removal instructions:")
    print(f"      1. Close all applications that might be using files in {directory}")
    print(f"      2. Open Command Prompt as Administrator")
    print(f"      3. Run: rmdir /S /Q \"{directory}\"")
    print(f"      4. If that fails, manually delete the .git folder first, then the rest")
    
    return False


def remove_file_safely(file_path, name="file"):
    """Safely remove a file with error handling"""
    if not os.path.exists(file_path):
        return True
        
    try:
        os.remove(file_path)
        print(f"✅ Removed {name}")
        return True
    except Exception as e:
        print(f"❌ Could not remove {name}: {e}")
        return False


def cleanup_swarmui():
    """Remove SwarmUI directory and related files"""
    print("\n🔧 Cleaning up SwarmUI...")
    
    # Remove main SwarmUI directory
    success = remove_directory_safely(SWARMUI_DIR, "SwarmUI directory")
    
    # Remove any related files
    related_files = [
        os.path.join(LOG_DIR, "swarmtunnel_install.log"),
    ]
    
    # Also clean up temp files
    import tempfile
    temp_files = [
        os.path.join(tempfile.gettempdir(), "swarmtunnel_last_clone.txt"),
        os.path.join(tempfile.gettempdir(), "swarmtunnel_fixperm_*.bat"),
        os.path.join(tempfile.gettempdir(), "swarmtunnel_fixperm_everyone_*.bat")
    ]
    
    for file_name in related_files:
        if os.path.exists(file_name):
            remove_file_safely(file_name, file_name)
    
    # Clean up temp files (handle wildcards)
    import glob
    for temp_pattern in temp_files:
        for temp_file in glob.glob(temp_pattern):
            if os.path.exists(temp_file):
                remove_file_safely(temp_file, f"temp file {os.path.basename(temp_file)}")
    
    return success


def cleanup_cloudflared():
    """Remove cloudflared files and directory"""
    print("\n🔧 Cleaning up cloudflared...")
    
    # Remove cloudflared directory
    if os.path.exists(CLOUD_DIR):
        success = remove_directory_safely(CLOUD_DIR, "cloudflared directory")
    else:
        print("✅ cloudflared directory does not exist, skipping...")
        success = True
    
    # Remove cloudflared files from current directory
    cloudflared_files = ["cloudflared", "cloudflared.exe", "cloudflared.tgz"]
    for file_name in cloudflared_files:
        if os.path.exists(file_name):
            remove_file_safely(file_name, file_name)
    
    return success


def cleanup_logs():
    """Remove log directory"""
    print("\n🔧 Cleaning up logs...")
    
    if os.path.exists(LOG_DIR):
        success = remove_directory_safely(LOG_DIR, "logs directory")
    else:
        print("✅ logs directory does not exist, skipping...")
        success = True
    
    return success


def main():
    """Main uninstall function"""
    print("=" * 60)
    print("🔄 SwarmTunnel Uninstall Script")
    print("=" * 60)
    
    # Check if running on Windows
    if platform.system().lower() == "windows":
        print("🪟 Detected Windows - will use aggressive permission fixing")
    else:
        print("🐧 Detected non-Windows system")
    
    # Confirm uninstall
    try:
        response = input("\n⚠️ This will remove all SwarmTunnel components. Continue? (y/N): ").strip().lower()
        if response not in ('y', 'yes'):
            print("❌ Uninstall cancelled")
            return
    except KeyboardInterrupt:
        print("\n❌ Uninstall cancelled")
        return
    except Exception:
        # Non-interactive mode, proceed
        pass
    
    print("\n🚀 Starting uninstall process...")
    
    # Track overall success
    all_success = True
    
    # Clean up components
    if not cleanup_swarmui():
        all_success = False
    
    if not cleanup_cloudflared():
        all_success = False
    
    if not cleanup_logs():
        all_success = False
    
    # Final status
    print("\n" + "=" * 60)
    if all_success:
        print("✅ Uninstall completed successfully!")
        print("   All SwarmTunnel components have been removed.")
    else:
        print("⚠️ Uninstall completed with some issues.")
        print("   Some components may need manual removal.")
        print("   Check the output above for specific instructions.")
    
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Uninstall interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Uninstall failed with error: {e}")
        sys.exit(1)
