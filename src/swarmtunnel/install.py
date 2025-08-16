import os
import platform
import subprocess
import sys
import urllib.request
import zipfile
import tarfile
import shutil

CLOUDFLARED_BASE = "https://github.com/cloudflare/cloudflared/releases/latest/download"
SWARMUI_REPO = "https://github.com/mcmonkeyprojects/SwarmUI.git"

# Allow overriding the install directory via environment variable for flexibility and tests
SWARMUI_DIR = os.environ.get("SWARMUI_DIR", "SwarmUI")
# Normalize whitespace to avoid accidental trailing spaces from external launchers
SWARMUI_DIR = SWARMUI_DIR.strip()
# Directories: where to place cloudflared binary and where to write logs
# CLOUD_DIR defaults to `cloudflared/`; LOG_DIR defaults to `logs/`.
CLOUD_DIR = os.environ.get("SWARMTUNNEL_CLOUDFLARED_DIR", "cloudflared")
LOG_DIR = os.environ.get("SWARMTUNNEL_LOG_DIR", "logs")

# Allow skipping the initial SwarmUI detection check via environment variable
# or command-line flag. Default: do not skip.
SKIP_SWARMUI_CHECK = os.environ.get('SWARMTUNNEL_SKIP_SWARMUI_CHECK', '0') != '0'
# Allow forcing cloudflared installation even if detection thinks it's present
FORCE_CLOUDFLARED_INSTALL = os.environ.get('SWARMTUNNEL_FORCE_CLOUDFLARED_INSTALL', '0') != '0'


def download_file(url, dest):
	print(f"Downloading {url}...")
	try:
		# Ensure destination directory exists
		dirname = os.path.dirname(dest)
		if dirname:
			os.makedirs(dirname, exist_ok=True)
		urllib.request.urlretrieve(url, dest)
		print(f"\u2705 Downloaded {dest}")
	except urllib.error.URLError as e:
		print(f"\u274c Network error downloading {url}: {e}")
		raise
	except Exception as e:
		print(f"\u274c Unexpected error downloading {url}: {e}")
		raise


def extract_zip(zip_path, dest):
	try:
		with zipfile.ZipFile(zip_path, 'r') as zip_ref:
			zip_ref.extractall(dest)
		print(f"\u2705 Extracted {zip_path}")
	except zipfile.BadZipFile:
		print(f"\u274c Error: {zip_path} is not a valid ZIP file")
		raise
	except Exception as e:
		print(f"\u274c Error extracting {zip_path}: {e}")
		raise


def extract_tar_gz(tar_path, dest):
	try:
		with tarfile.open(tar_path, 'r:gz') as tar_ref:
			tar_ref.extractall(dest)
		print(f"\u2705 Extracted {tar_path}")
	except tarfile.ReadError:
		print(f"\u274c Error: {tar_path} is not a valid tar.gz file")
		raise
	except Exception as e:
		print(f"\u274c Error extracting {tar_path}: {e}")
		raise


def fix_windows_permissions(directory):
	"""Fix Windows permissions to ensure the directory can be deleted by the user"""
	if platform.system().lower() != "windows":
		return

	# Try conservative non-elevated fixes first
	try:
		import getpass, tempfile, time
		# If the caller provided an explicit interactive user (from the non-elevated
		# launcher), prefer that. It should be in DOMAIN\User format.
		target_user = os.environ.get('SWARMTUNNEL_INTERACTIVE_USER')
		if target_user:
			# trim and use as-is
			target_user = target_user.strip()
		else:
			# Fallback: attempt to determine an appropriate account name
			try:
				who = subprocess.run(["whoami"], capture_output=True, text=True, shell=True)
				if who.returncode == 0 and who.stdout:
					target_user = who.stdout.strip()
				else:
					import getpass
					target_user = os.environ.get('USERNAME', getpass.getuser())
			except Exception:
				target_user = os.environ.get('USERNAME', getpass.getuser())

		# Step 1: Remove ALL attributes from all files (Git creates files with system, hidden, read-only attributes)
		try:
			# Remove read-only, system, and hidden attributes from all files
			attrib_cmd = f'attrib -R -S -H "{directory}\\*.*" /S'
			subprocess.run(attrib_cmd, shell=True, capture_output=True, text=True)
		except Exception:
			pass

		# Step 2: Specifically handle .git folder permissions (Git creates problematic permissions)
		git_dir = os.path.join(directory, ".git")
		if os.path.exists(git_dir):
			try:
				# Remove ALL attributes from .git folder specifically (including system and hidden)
				git_attrib_cmd = f'attrib -R -S -H "{git_dir}\\*.*" /S'
				subprocess.run(git_attrib_cmd, shell=True, capture_output=True, text=True)
				
				# Also remove attributes from the .git folder itself
				git_folder_attrib_cmd = f'attrib -R -S -H "{git_dir}"'
				subprocess.run(git_folder_attrib_cmd, shell=True, capture_output=True, text=True)
				
				# Grant full control to current user on .git folder
				git_grant_cmd = f'icacls "{git_dir}" /grant "{target_user}:(OI)(CI)F" /T /C'
				subprocess.run(git_grant_cmd, shell=True, capture_output=True, text=True)
			except Exception:
				pass

		# Step 3: Take ownership of all files and folders
		try:
			takeown_cmd = f'takeown /F "{directory}" /R /D Y'
			subprocess.run(takeown_cmd, shell=True, capture_output=True, text=True)
		except Exception:
			pass

		# Step 4: Grant full control to the target user
		try:
			grant_cmd = f'icacls "{directory}" /grant "{target_user}:(OI)(CI)F" /T /C'
			res = subprocess.run(grant_cmd, shell=True, capture_output=True, text=True)
			if res.returncode == 0:
				return
		except Exception:
			pass

		# Step 5: If non-elevated attempts didn't work, try elevated approach
		try:
			temp_dir = tempfile.gettempdir()
			batch_path = os.path.join(temp_dir, f"swarmtunnel_fixperm_{os.getpid()}.bat")
			with open(batch_path, 'w', encoding='utf-8') as bf:
				bf.write('@echo off\r\n')
				bf.write('echo Fixing permissions for Git repository...\r\n')
				# %1 = directory, %2 = target_user
				
				# Remove ALL attributes from all files (including system and hidden)
				bf.write('attrib -R -S -H "%~1\\*.*" /S\r\n')
				bf.write('attrib -R -S -H "%~1" /D\r\n')  # Also remove from directories
				
				# Take ownership
				bf.write('takeown /F "%~1" /R /D Y\r\n')
				
				# Set ownership to target user
				bf.write('icacls "%~1" /setowner "%~2" /T /C\r\n')
				
				# Grant full control
				bf.write('icacls "%~1" /grant "%~2:(OI)(CI)F" /T /C\r\n')
				
				# Specifically handle .git folder if it exists
				bf.write('if exist "%~1\\.git" (\r\n')
				bf.write('  echo Fixing .git folder permissions...\r\n')
				bf.write('  attrib -R -S -H "%~1\\.git\\*.*" /S\r\n')
				bf.write('  attrib -R -S -H "%~1\\.git" /D\r\n')
				bf.write('  takeown /F "%~1\\.git" /R /D Y\r\n')
				bf.write('  icacls "%~1\\.git" /setowner "%~2" /T /C\r\n')
				bf.write('  icacls "%~1\\.git" /grant "%~2:(OI)(CI)F" /T /C\r\n')
				bf.write(')\r\n')
				
				bf.write('echo Permission fix completed.\r\n')
				bf.write('exit /b %ERRORLEVEL%\r\n')

			# Build PowerShell Start-Process command to run the batch elevated and wait
			ps_cmd = (
				'powershell -NoProfile -Command "Start-Process cmd.exe -ArgumentList \'/c \"' +
				batch_path.replace('"', '\\"') + '\" \"' + directory.replace('"', '\\"') + '\" \"' +
				target_user.replace('"', '\\"') + '\"\' -Verb RunAs -Wait"'
			)

			proc = subprocess.run(ps_cmd, shell=True)
			# Best-effort cleanup of the batch file
			try:
				os.remove(batch_path)
			except Exception:
				pass

			if proc.returncode == 0:
				return
			else:
				print(f"\u26a0\ufe0f  Warning: Elevated permission fix did not complete successfully (returncode={proc.returncode})")
		except Exception as e:
			print(f"\u26a0\ufe0f  Warning: Could not elevate to fix permissions: {e}")

		# Step 6: As a final elevated fallback, try to grant the well-known 'Everyone' group
		# full control recursively. This is less strict but ensures the folder can be
		# deleted by the interactive user.
		try:
			temp_dir2 = tempfile.gettempdir()
			batch_path2 = os.path.join(temp_dir2, f"swarmtunnel_fixperm_everyone_{os.getpid()}.bat")
			with open(batch_path2, 'w', encoding='utf-8') as bf2:
				bf2.write('@echo off\r\n')
				bf2.write('echo Granting Everyone full control...\r\n')
				
				# Remove ALL attributes
				bf2.write('attrib -R -S -H "%~1\\*.*" /S\r\n')
				bf2.write('attrib -R -S -H "%~1" /D\r\n')
				
				# Grant Everyone full control
				bf2.write('icacls "%~1" /grant Everyone:(OI)(CI)F /T /C\r\n')
				
				# Specifically handle .git folder if it exists
				bf2.write('if exist "%~1\\.git" (\r\n')
				bf2.write('  attrib -R -S -H "%~1\\.git\\*.*" /S\r\n')
				bf2.write('  attrib -R -S -H "%~1\\.git" /D\r\n')
				bf2.write('  icacls "%~1\\.git" /grant Everyone:(OI)(CI)F /T /C\r\n')
				bf2.write(')\r\n')
				
				bf2.write('echo Everyone grant completed.\r\n')
				bf2.write('exit /b %ERRORLEVEL%\r\n')

			ps_cmd2 = (
				'powershell -NoProfile -Command "Start-Process cmd.exe -ArgumentList \'/c "' +
				batch_path2.replace('"', '\\"') + '\" \"' + directory.replace('"', '\\"') + '\"\' -Verb RunAs -Wait"'
			)

			proc2 = subprocess.run(ps_cmd2, shell=True)
			try:
				os.remove(batch_path2)
			except Exception:
				pass

			if proc2.returncode == 0:
				print(f"\u2705 Granted Everyone full control on {directory} (elevated)")
				return
			else:
				print(f"\u26a0\ufe0f  Warning: Elevated Everyone grant did not complete successfully (returncode={proc2.returncode})")
		except Exception as e:
			print(f"\u26a0\ufe0f  Warning: Could not elevate to grant Everyone ACLs: {e}")

		# Final fallback: instruct the user what to run as Administrator
		print(f"\u26a0\ufe0f  Warning: Could not automatically fix permissions for {directory}.")
		print("   Please run an elevated Command Prompt (Run as Administrator) and execute:")
		print(f"     attrib -R -S -H \"{directory}\\*.*\" /S")
		print(f"     attrib -R -S -H \"{directory}\" /D")
		print(f"     takeown /F \"{directory}\" /R /D Y")
		print(f"     icacls \"{directory}\" /setowner \"{target_user}\" /T /C")
		print(f"     icacls \"{directory}\" /grant \"{target_user}:(OI)(CI)F\" /T /C")
		if os.path.exists(os.path.join(directory, ".git")):
			print(f"     attrib -R -S -H \"{directory}\\.git\\*.*\" /S")
			print(f"     attrib -R -S -H \"{directory}\\.git\" /D")
			print(f"     takeown /F \"{directory}\\.git\" /R /D Y")
			print(f"     icacls \"{directory}\\.git\" /setowner \"{target_user}\" /T /C")
			print(f"     icacls \"{directory}\\.git\" /grant \"{target_user}:(OI)(CI)F\" /T /C")

	except Exception as e:
		print(f"\u26a0\ufe0f  Warning: Could not fix permissions: {e}")


def enable_lan_for_swarmui(swarmui_dir):
	"""Ensure SwarmUI launchers or an env file set ASPNETCORE_URLS to bind on all interfaces.

	This function is conservative: it prepends an export/set line only if ASPNETCORE_URLS
	is not already present. It also writes a fallback `.env.swarmtunnel` file when no
	launcher is present.
	"""
	try:
		# Look for common launcher names
		win_launch_candidates = ['launch-windows.bat', 'launch_windows.bat']
		sh_launch_candidates = ['launch-linux.sh', 'launch_linux.sh', 'launch-macos.sh', 'launch_macos.sh']

		# Windows batch: prepend set ASPNETCORE_URLS=... if not present
		for name in win_launch_candidates:
			path = os.path.join(swarmui_dir, name)
			if os.path.exists(path):
				with open(path, 'r', encoding='utf-8', errors='ignore') as f:
					content = f.read()
				if 'ASPNETCORE_URLS' not in content:
					new = 'set ASPNETCORE_URLS=http://0.0.0.0:7801\r\n' + content
					with open(path, 'w', encoding='utf-8') as f:
						f.write(new)

		# POSIX shells: prepend export line
		for name in sh_launch_candidates:
			path = os.path.join(swarmui_dir, name)
			if os.path.exists(path):
				with open(path, 'r', encoding='utf-8', errors='ignore') as f:
					content = f.read()
				if 'ASPNETCORE_URLS' not in content:
					new = 'export ASPNETCORE_URLS="http://0.0.0.0:7801"\n' + content
					with open(path, 'w', encoding='utf-8') as f:
						f.write(new)
					# try to make it executable
					try:
						os.chmod(path, 0o755)
					except Exception:
						pass

		# If no launchers were modified/created, write a fallback .env.swarmtunnel
		# This is a visible, reversible artifact indicating the desired binding.
		fallback = os.path.join(swarmui_dir, '.env.swarmtunnel')
		if not os.path.exists(fallback):
			try:
				with open(fallback, 'w', encoding='utf-8') as f:
					f.write('ASPNETCORE_URLS=http://0.0.0.0:7801\n')
			except Exception:
				# Non-fatal
				pass

		print('\u2705 Configured SwarmUI launchers to bind on 0.0.0.0 (LAN enabled)')
	except Exception as e:
		# Don't raise — installer should continue even if this tweak fails
		print(f"\u26a0\ufe0f  Warning: could not enable LAN binding: {e}")


def is_cloudflared_installed():
	"""Check if cloudflared is already installed and executable"""
	os_name = platform.system().lower()
	cloudflared_path = "cloudflared"
	if os_name == "windows":
		cloudflared_path = "cloudflared.exe"

	# Prefer system/user PATH (system-wide or user-wide installation) unless tests ask us not to
	if not os.environ.get('SWARMTUNNEL_IGNORE_SYSTEM_CLOUDFLARED'):
		from shutil import which
		which_path = which(cloudflared_path)
		if which_path is not None:
			return True

	# Next, check current working directory (tests place files here)
	cwd_path = os.path.join(os.getcwd(), cloudflared_path)
	if os.path.exists(cwd_path):
		if os_name != "windows":
			return os.access(cwd_path, os.X_OK)
		else:
			return True

	# Finally, check the cloudflared dir managed by this project
	local_path = os.path.join(CLOUD_DIR, cloudflared_path)
	if os.path.exists(local_path):
		if os_name != "windows":
			return os.access(local_path, os.X_OK)
		else:
			return True

	return False


def is_swarmui_installed():
	"""Check if SwarmUI is already installed (directory exists and has been initialized).

	We use a marker file `.installed` inside the SwarmUI directory to indicate that
	the initial installer/setup step has completed. This keeps `start.py` from
	accidentally launching first-run installer UI.
	"""
	global SWARMUI_DIR

	# First, check the configured SWARMUI_DIR (may be relative to cwd)
	installed_marker = os.path.join(SWARMUI_DIR, ".installed")
	sln_file = os.path.join(SWARMUI_DIR, "SwarmUI.sln")
	# Consider either the marker or the solution file as evidence of an existing install
	if os.path.exists(installed_marker) or os.path.exists(sln_file):
		return True

	# If not found, attempt to discover an existing SwarmUI by searching
	# upward from the current working directory. If found, set the
	# SWARMUI_DIR environment variable so subsequent runs use it.
	cwd = os.getcwd()
	p = cwd
	while True:
		candidate = os.path.join(p, "SwarmUI")
		marker = os.path.join(candidate, ".installed")
		sln_candidate = os.path.join(candidate, "SwarmUI.sln")
		if os.path.exists(marker) or os.path.exists(sln_candidate):
			# update environment and module-level variable so other modules pick this up
			os.environ["SWARMUI_DIR"] = candidate
			SWARMUI_DIR = candidate
			print(f"ℹ️ Detected existing SwarmUI at {candidate}")
			return True

		newp = os.path.dirname(p)
		if newp == p:
			break
		p = newp

	# Not found by walking upward: check a few common alternative locations where
	# a user might have SwarmUI installed (sibling directories, repo root, home).
	possible_locations = []
	# sibling to current working directory: ../SwarmUI
	possible_locations.append(os.path.abspath(os.path.join(cwd, '..', 'SwarmUI')))
	# relative to this package's repo layout: go up from this file to repository root
	package_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
	possible_locations.append(os.path.join(package_root, 'SwarmUI'))
	# user's home directory
	possible_locations.append(os.path.join(os.path.expanduser('~'), 'SwarmUI'))

	for candidate in possible_locations:
		# Avoid detecting the repository's own SwarmUI copy (if present)
		# when tests or runs are executed from a temp directory. Only accept
		# external installations that are not inside the package root.
		try:
			common = os.path.commonpath([os.path.abspath(candidate), package_root])
		except Exception:
			common = None
		if common == package_root:
			# candidate is inside the repository; skip to avoid false positives
			continue

		marker = os.path.join(candidate, '.installed')
		sln_candidate = os.path.join(candidate, 'SwarmUI.sln')
		if os.path.exists(marker) or os.path.exists(sln_candidate):
			os.environ['SWARMUI_DIR'] = candidate
			SWARMUI_DIR = candidate
			print(f"ℹ️ Detected existing SwarmUI at {candidate}; using it as SWARMUI_DIR")
			return True

	return False


def get_cloudflared_url_and_dest():
	"""Get the appropriate cloudflared URL and destination filename for the current platform"""
	os_name = platform.system().lower()
	arch = platform.machine().lower()

	# Map common architecture names to cloudflared naming convention
	arch_mapping = {
		'x86_64': 'amd64',
		'amd64': 'amd64',
		'aarch64': 'arm64',
		'arm64': 'arm64',
		'armv7l': 'arm',
		'armv8l': 'arm64',
		'i386': '386',
		'i686': '386'
	}

	# Get the mapped architecture or default to amd64
	mapped_arch = arch_mapping.get(arch, 'amd64')

	if os_name == "windows":
		# Windows: Use amd64 for x86_64 systems, arm64 for ARM systems
		if mapped_arch == "arm64":
			url = f"{CLOUDFLARED_BASE}/cloudflared-windows-arm64.exe"
		else:
			url = f"{CLOUDFLARED_BASE}/cloudflared-windows-amd64.exe"
		dest = "cloudflared.exe"
	elif os_name == "darwin":
		# macOS: Use arm64 for Apple Silicon, amd64 for Intel
		if mapped_arch == "arm64":
			url = f"{CLOUDFLARED_BASE}/cloudflared-darwin-arm64.tgz"
		else:
			url = f"{CLOUDFLARED_BASE}/cloudflared-darwin-amd64.tgz"
		dest = "cloudflared.tgz"
	else:
		# Linux: Support multiple architectures
		if mapped_arch == "arm64":
			url = f"{CLOUDFLARED_BASE}/cloudflared-linux-arm64"
		elif mapped_arch == "arm":
			url = f"{CLOUDFLARED_BASE}/cloudflared-linux-arm"
		elif mapped_arch == "386":
			url = f"{CLOUDFLARED_BASE}/cloudflared-linux-386"
		else:
			url = f"{CLOUDFLARED_BASE}/cloudflared-linux-amd64"
		dest = "cloudflared"

	return url, dest, mapped_arch


def install_cloudflared(force_install=None):
	"""Install cloudflared unless detection finds it and force_install is False.

	If force_install is True, proceed to download/install regardless of detection.
	If force_install is None, fall back to module-level FORCE_CLOUDFLARED_INSTALL.
	"""
	if force_install is None:
		force_install = FORCE_CLOUDFLARED_INSTALL

	if not force_install and is_cloudflared_installed():
		print("\u2705 cloudflared already installed.")
		return

	try:
		os_name = platform.system().lower()
		arch = platform.machine().lower()

		url, dest, mapped_arch = get_cloudflared_url_and_dest()
		print(f"Detected platform: {os_name} {arch} -> {mapped_arch}")

		# Download to the current working directory (tests expect this)
		download_file(url, dest)

		# If we downloaded a tarball, extract it into EXTERNAL_DIR
		if dest.endswith(".tgz"):
			os.makedirs(CLOUD_DIR, exist_ok=True)
			extract_tar_gz(dest, CLOUD_DIR)
			try:
				os.remove(dest)
			except Exception:
				pass
		else:
			# For plain binaries, set executable perms in CWD then move to EXTERNAL_DIR
			if os_name != "windows":
				try:
					os.chmod(dest, 0o755)
				except OSError as e:
					print(f"\u26a0\ufe0f  Warning: Could not set executable permissions on {dest}: {e}")
					print("   You may need to run: chmod +x cloudflared")

			# Move binary into EXTERNAL_DIR for repository cleanliness
			try:
				os.makedirs(CLOUD_DIR, exist_ok=True)
				shutil.move(dest, os.path.join(CLOUD_DIR, dest))
			except Exception:
				# If move fails, leave it in place; tests look for the chmod/prints
				pass

		# Keep the original print used by tests
		print("\u2705 cloudflared installed.")

	except Exception as e:
		print(f"\u274c Failed to install cloudflared: {e}")
		# Clean up any partial downloads
		# Clean up any partial downloads in EXTERNAL_DIR
		for cleanup_file in [os.path.join(CLOUD_DIR, f) for f in ["cloudflared", "cloudflared.exe", "cloudflared.tgz"]]:
			if os.path.exists(cleanup_file):
				try:
					os.remove(cleanup_file)
				except:
					pass
		raise


def install_swarmui(skip_swarmui_check=None):
	"""Install or attach to SwarmUI.

	If skip_swarmui_check is None, fall back to module-level SKIP_SWARMUI_CHECK.
	If True, do not call is_swarmui_installed() and proceed to install.
	"""
	if skip_swarmui_check is None:
		skip_swarmui_check = SKIP_SWARMUI_CHECK

	# Respect the skip flag: if skip_swarmui_check is True, do not auto-detect
	# an existing SwarmUI installation and proceed with clone/installation.
	if not skip_swarmui_check and is_swarmui_installed():
		print("\u2705 SwarmUI already installed.")
		return

	# If we reach here, we couldn't auto-detect an existing SwarmUI install.
	# If skip_swarmui_check is True, skip the user prompt and proceed directly to installation
	if skip_swarmui_check:
		print("Skipping SwarmUI detection check - proceeding with installation...")
		use_existing = False
	else:
		# Prompt the user to see if they want to use an existing installation elsewhere.
		use_existing = None
		try:
			# Prompt in console first
			choice = input("Use existing SwarmUI installation? (Y/N): ").strip().lower()
			if choice in ('y', 'yes'):
				use_existing = True
			else:
				use_existing = False
		except Exception:
			# Non-interactive environment: treat as No
			use_existing = False

	if use_existing:
		# Try to open a folder selection dialog (cross-platform) to let the user pick
		# the SwarmUI folder. Use tkinter if available; if not, ask for a path.
		selected = None
		try:
			import tkinter as tk
			from tkinter import filedialog
			root = tk.Tk()
			root.withdraw()
			selected = filedialog.askdirectory(title='Select existing SwarmUI directory')
		except Exception:
			# Fallback to console prompt
			try:
				selected = input('Enter path to existing SwarmUI directory (or blank to cancel): ').strip()
			except Exception:
				selected = None

		if selected:
			# Validate the selection: must be a directory and contain expected structure
			if os.path.isdir(selected) and os.path.exists(os.path.join(selected, 'SwarmUI.sln')):
				os.environ['SWARMUI_DIR'] = selected
				global SWARMUI_DIR
				SWARMUI_DIR = selected
				print(f"\u2705 Using existing SwarmUI at {selected}")
				return
			else:
				print("\u26a0\ufe0f Selected folder doesn't look like a SwarmUI installation or selection cancelled. Proceeding to install in project.")

	try:
		# Ensure git is available
		print("Checking for git...")
		result = subprocess.run(["git", "--version"], capture_output=True, text=True)
		if result.returncode != 0:
			raise FileNotFoundError("git is not available")
		print(f"Cloning SwarmUI repository into '{SWARMUI_DIR}'...")
		subprocess.run(["git", "clone", "--depth", "1", SWARMUI_REPO, SWARMUI_DIR], check=True)
		
		# Small delay to ensure all file handles are released
		import time
		time.sleep(2)  # Increased delay to ensure Git processes complete

		# Basic validation that clone succeeded
		if not os.path.exists(os.path.join(SWARMUI_DIR, ".git")):
			raise Exception("SwarmUI clone appears incomplete")

		# Record where the clone was performed for diagnostics. Write both a temp file
		# and a repo-root log so the user can find the clone even if consoles close.
		try:
			import tempfile, datetime
			abs_clone = os.path.abspath(SWARMUI_DIR)
			cwd_now = os.path.abspath(os.getcwd())
			stamp = datetime.datetime.utcnow().isoformat() + 'Z'
			# temp file
			tmpfile = os.path.join(tempfile.gettempdir(), 'swarmtunnel_last_clone.txt')
			with open(tmpfile, 'w', encoding='utf-8') as tf:
				tf.write(f"timestamp={stamp}\nclone_path={abs_clone}\ncwd={cwd_now}\n")
			# repo-root log (if we can find package root)
			try:
				# Ensure logs directory exists
				os.makedirs(LOG_DIR, exist_ok=True)
				logpath = os.path.join(LOG_DIR, 'swarmtunnel_install.log')
				with open(logpath, 'a', encoding='utf-8') as lf:
					lf.write(f"[{stamp}] clone_path={abs_clone} cwd={cwd_now}\n")
			except Exception:
				# non-fatal
				pass
		except Exception:
			# non-fatal; don't block install on logging failure
			pass

		# Fix Windows permissions to ensure the directory can be deleted
		fix_windows_permissions(SWARMUI_DIR)
		
		# Additional step: Force close any handles that might be held by Git processes
		try:
			# Kill any git processes that might be holding file handles
			subprocess.run(["taskkill", "/F", "/IM", "git.exe"], shell=True, capture_output=True, text=True)
		except Exception:
			pass

		# Decide whether to write the installed marker now or wait for the
		# platform-specific launcher/installer to complete. If there is no
		# launcher present in the cloned repo, treat clone-as-install and write
		# the marker immediately. Otherwise, defer marker creation until the
		# launcher brings up the web UI (below).
		launcher_files = [
			'launch-windows.bat', 'launch_windows.bat',
			'launch-linux.sh', 'launch_linux.sh',
			'launch-macos.sh', 'launch_macos.sh'
		]
		try:
			found_launcher = any(os.path.exists(os.path.join(SWARMUI_DIR, f)) for f in launcher_files)
		except Exception:
			found_launcher = False

		if not found_launcher:
			# No launcher script found: consider this clone sufficient for start.py
			# and mark installation complete.
			try:
				marker_path = os.path.join(SWARMUI_DIR, ".installed")
				with open(marker_path, "w") as mf:
					mf.write("installed")
				print("\u2705 SwarmUI installed.")
			except Exception:
				print("\u26a0\ufe0f  Warning: Could not write installed marker file")

		# Attempt to enable LAN binding by editing launch scripts or writing a fallback env file.
		# This can be disabled by setting SWARMTUNNEL_ENABLE_LAN=0 in the environment.
		try:
			enable_lan = os.environ.get('SWARMTUNNEL_ENABLE_LAN', '1') != '0'
			if enable_lan:
				enable_lan_for_swarmui(SWARMUI_DIR)
		except Exception:
			# Non-fatal
			pass

		# Attempt to run the bundled launcher/installer to complete platform-specific setup.
		try:
			os_name = platform.system().lower()
			# Choose the launcher/installer script depending on platform
			launcher_cmd = None
			if os_name == "windows":
				launcher = os.path.join(SWARMUI_DIR, "launch-windows.bat")
				if os.path.exists(launcher):
					# Run the batch file via cmd.exe in a new console so the window is visible
					# and we keep a handle to the process. Avoid shell=True to ensure
					# creationflags and startupinfo are respected.
					launcher_cmd = ["cmd.exe", "/c", launcher]
					creationflags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
					print(f"\u27a1\ufe0f Launching Windows installer in a new console: {launcher}")
					try:
						si = subprocess.STARTUPINFO()
						si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
						si.wShowWindow = 1  # SW_SHOWNORMAL
						proc = subprocess.Popen(launcher_cmd, creationflags=creationflags, startupinfo=si)
					except Exception:
						# Fallback to a basic launch if STARTUPINFO is unavailable
						proc = subprocess.Popen(launcher_cmd, creationflags=creationflags)
			elif os_name == "darwin":
				launcher = os.path.join(SWARMUI_DIR, "launch-macos.sh")
				if os.path.exists(launcher):
					launcher_cmd = ["/bin/bash", launcher]
					print(f"\u27a1\ufe0f Launching macOS installer in background: {launcher}")
					proc = subprocess.Popen(launcher_cmd, start_new_session=True)
			else:
				# Linux / others
				installer = os.path.join(SWARMUI_DIR, "launch-linux.sh")
				if os.path.exists(installer):
					launcher_cmd = ["/bin/bash", installer]
					print(f"\u27a1\ufe0f Launching Linux installer in background: {installer}")
					proc = subprocess.Popen(launcher_cmd, start_new_session=True)

			# If we launched an installer, wait for the web service to become available
			if launcher_cmd is not None:
				# Wait for the SwarmUI web service to come up (user may need to click through installer)
				print("\u23f3 Waiting for SwarmUI web UI to become available on http://localhost:7801 ...")
				# Poll for service up to a long timeout (default 1 hour)
				wait_for_service_url = "http://localhost:7801"
				total_wait = 60 * 60  # 1 hour
				interval = 5
				import time
				from urllib.request import urlopen
				from urllib.error import URLError

				start_time = time.time()
				service_ready = False
				while time.time() - start_time < total_wait:
					try:
						resp = urlopen(wait_for_service_url, timeout=5)
						if getattr(resp, 'getcode', lambda: None)() == 200:
							service_ready = True
							print("\u2705 SwarmUI web UI appears to be available")
							break
					except (URLError, Exception):
						pass
					time.sleep(interval)

				if not service_ready:
					print("\u26a0\ufe0f  Timeout waiting for SwarmUI web UI. You may need to finish installer manually before cloudflared is installed.")
				else:
					# Optionally create installed marker to indicate install completed
					try:
						marker_path = os.path.join(SWARMUI_DIR, ".installed")
						with open(marker_path, "w") as mf:
							mf.write("installed")
					except Exception:
						print("\u26a0\ufe0f  Warning: Could not write installed marker file")
		except Exception as e:
			# Non-fatal: warn but continue
			print(f"\u26a0\ufe0f  Warning: launching platform installer failed: {e}")

		print("\u2705 SwarmUI installation step completed (launcher started or skipped).")

	except FileNotFoundError:
		print("\u274c 'git' is not installed or not found in PATH. Please install git from https://git-scm.com/downloads and try again.")
		raise
	except subprocess.CalledProcessError as e:
		print(f"\u274c Failed to clone SwarmUI: {e}")
		# Clean up partial directory if present
		if os.path.exists(SWARMUI_DIR):
			try:
				shutil.rmtree(SWARMUI_DIR)
			except Exception:
				pass
		raise
	except Exception as e:
		print(f"\u274c Failed to install SwarmUI: {e}")
		# Clean up partial directory if present
		if os.path.exists(SWARMUI_DIR):
			try:
				shutil.rmtree(SWARMUI_DIR)
			except Exception:
				pass
		raise


def cleanup_for_testing():
	"""Clean up installed components for testing purposes"""
	print("\ud83e\uddf9 Cleaning up for testing...")

	# Remove SwarmUI directory
	if os.path.exists(SWARMUI_DIR):
		try:
			if platform.system().lower() == "windows":
				# On Windows, try to fix permissions first
				fix_windows_permissions(SWARMUI_DIR)
			shutil.rmtree(SWARMUI_DIR)
			print("\u2705 Removed SwarmUI directory")
		except Exception as e:
			print(f"\u274c Could not remove SwarmUI directory: {e}")
			print("   You may need to manually delete it or run as administrator")

	# Remove cloudflared files from both CWD and CLOUD_DIR
	for fname in ["cloudflared", "cloudflared.exe", "cloudflared.tgz"]:
		# cwd
		path_cwd = os.path.join(os.getcwd(), fname)
		if os.path.exists(path_cwd):
			try:
				os.remove(path_cwd)
				print(f"\u2705 Removed {path_cwd}")
			except Exception as e:
				print(f"\u274c Could not remove {path_cwd}: {e}")

		# cloudflared dir
		path_ext = os.path.join(CLOUD_DIR, fname)
		if os.path.exists(path_ext):
			try:
				os.remove(path_ext)
				print(f"\u2705 Removed {path_ext}")
			except Exception as e:
				print(f"\u274c Could not remove {path_ext}: {e}")

	# Optionally remove EXTERNAL_DIR if empty
	try:
		if os.path.isdir(CLOUD_DIR) and not os.listdir(CLOUD_DIR):
			os.rmdir(CLOUD_DIR)
	except Exception:
		pass


if __name__ == "__main__":
	print("=== Installing SwarmUI and Cloudflare Tunnel ===")
	try:
		# Simple CLI: support --skip-swarmui-check to force clone/install without
		# detecting an existing SwarmUI installation.
		# Determine flags from CLI
		skip_flag = ('--skip-swarmui-check' in sys.argv) or ('--no-swarmui-check' in sys.argv)
		force_cloudflared = ('--force-cloudflared-install' in sys.argv) or ('--force-cloudflared' in sys.argv)

		install_swarmui(skip_swarmui_check=skip_flag)
		install_cloudflared(force_install=force_cloudflared)
		print("\nInstallation complete. Run 'start.py' to launch SwarmUI with a Quick Tunnel.")

		# Add cleanup option for testing
		if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
			cleanup_for_testing()

	except Exception as e:
		print(f"\n\u274c Installation failed: {e}")
		print("Please check your internet connection and try again.")
		sys.exit(1)

