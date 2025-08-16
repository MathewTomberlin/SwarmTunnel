import os
import platform
import subprocess
import shutil
import sys


def fix_windows_permissions(directory):
	"""Fix Windows permissions to ensure the directory can be deleted by the user"""
	if platform.system().lower() == "windows":
		try:
			# Get current user
			import getpass
			current_user = getpass.getuser()
            
			print(f"🔧 Fixing permissions for {directory}...")
            
			# Use icacls to grant full control to current user
			cmd = f'icacls "{directory}" /grant "{current_user}:(OI)(CI)F" /t'
			result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
			if result.returncode == 0:
				print(f"\u2705 Fixed permissions for {directory}")
				return True
			else:
				print(f"\u26a0\ufe0f  Warning: Could not fix permissions for {directory}")
				print(f"   Error: {result.stderr}")
				return False
                
		except Exception as e:
			print(f"\u26a0\ufe0f  Warning: Could not fix permissions: {e}")
			return False
	return True


def force_delete_windows(directory):
	"""Force delete directory on Windows using takeown and rmdir"""
	if platform.system().lower() == "windows":
		try:
			print(f"🔧 Force deleting {directory}...")
            
			# Take ownership
			takeown_cmd = f'takeown /f "{directory}" /r /d y'
			result = subprocess.run(takeown_cmd, shell=True, capture_output=True, text=True)
            
			if result.returncode != 0:
				print(f"\u26a0\ufe0f  Warning: Could not take ownership: {result.stderr}")
            
			# Grant full permissions
			icacls_cmd = f'icacls "{directory}" /grant administrators:F /t'
			result = subprocess.run(icacls_cmd, shell=True, capture_output=True, text=True)
            
			# Force delete
			rmdir_cmd = f'rmdir /s /q "{directory}"'
			result = subprocess.run(rmdir_cmd, shell=True, capture_output=True, text=True)
            
			if result.returncode == 0:
				print(f"\u2705 Force deleted {directory}")
				return True
			else:
				print(f"\u274c Could not force delete {directory}: {result.stderr}")
				return False
                
		except Exception as e:
			print(f"\u274c Error during force delete: {e}")
			return False
	return False


def cleanup_swarmui():
	"""Clean up SwarmUI directory"""
	if not os.path.exists("SwarmUI"):
		print("ℹ️  SwarmUI directory not found")
		return True
    
	print("🧪 Cleaning up SwarmUI directory...")
    
	try:
		# Try normal deletion first
		shutil.rmtree("SwarmUI")
		print("\u2705 Removed SwarmUI directory")
		return True
        
	except PermissionError:
		print("\u26a0\ufe0f  Permission denied. Attempting to fix permissions...")
        
		# Try to fix permissions
		if fix_windows_permissions("SwarmUI"):
			try:
				shutil.rmtree("SwarmUI")
				print("\u2705 Removed SwarmUI directory after fixing permissions")
				return True
			except Exception as e:
				print(f"\u274c Still cannot remove after fixing permissions: {e}")
        
		# Try force delete on Windows
		if platform.system().lower() == "windows":
			print("🔧 Attempting force delete...")
			if force_delete_windows("SwarmUI"):
				return True
        
		print("\u274c Could not remove SwarmUI directory")
		print("   Manual steps required:")
		print("   1. Right-click SwarmUI folder → Properties → Security → Advanced")
		print("   2. Click 'Change' next to Owner")
		print("   3. Enter your username and click 'Check Names'")
		print("   4. Check 'Replace owner on subcontainers and objects'")
		print("   5. Click OK, then delete the folder")
		return False
        
	except Exception as e:
		print(f"\u274c Error removing SwarmUI directory: {e}")
		return False


def cleanup_cloudflared():
	"""Clean up cloudflared files"""
	print("🧪 Cleaning up cloudflared files...")
    
	files_to_remove = ["cloudflared", "cloudflared.exe", "cloudflared.tgz"]
	removed_count = 0
    
	for file in files_to_remove:
		if os.path.exists(file):
			try:
				os.remove(file)
				print(f"\u2705 Removed {file}")
				removed_count += 1
			except Exception as e:
				print(f"\u274c Could not remove {file}: {e}")
    
	if removed_count == 0:
		print("ℹ️  No cloudflared files found")
    
	return True


def main():
	print("🧪 SwarmUI and Cloudflared Cleanup Tool")
	print("=" * 50)
    
	success = True
    
	# Clean up SwarmUI
	if not cleanup_swarmui():
		success = False
    
	# Clean up cloudflared
	if not cleanup_cloudflared():
		success = False
    
	print("=" * 50)
	if success:
		print("\u2705 Cleanup completed successfully!")
	else:
		print("\u26a0\ufe0f  Cleanup completed with some issues")
		print("   Check the messages above for manual steps required")
    
	return 0 if success else 1

if __name__ == "__main__":
	sys.exit(main())

