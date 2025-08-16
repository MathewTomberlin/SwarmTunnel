import os
import sys
import subprocess
import time
import threading
import queue
import signal
import platform
import json
import re
import argparse
from urllib.request import urlopen
from urllib.error import URLError

# Try to import psutil for process monitoring (optional)
try:
	import psutil
except ImportError:
	psutil = None

# Configuration
SWARMUI_PORT = 7801
SWARMUI_URL = f"http://localhost:{SWARMUI_PORT}"

# Allow overriding the SwarmUI install directory via environment variable (used by install.py)
SWARMUI_DIR = os.environ.get("SWARMUI_DIR", "SwarmUI")

# Directories for cloudflared binary and logs
CLOUD_DIR = os.environ.get("SWARMTUNNEL_CLOUDFLARED_DIR", "cloudflared")
LOG_DIR = os.environ.get("SWARMTUNNEL_LOG_DIR", "logs")

# Tunnel configuration file (defined after LOG_DIR)
TUNNEL_CONFIG_FILE = os.path.join(LOG_DIR, "tunnel_config.yml")

# Test flags to force use of local installations (similar to install.py)
FORCE_LOCAL_SWARMUI = os.environ.get('SWARMTUNNEL_FORCE_LOCAL_SWARMUI', '0') != '0'
FORCE_LOCAL_CLOUDFLARED = os.environ.get('SWARMTUNNEL_FORCE_LOCAL_CLOUDFLARED', '0') != '0'

# Installed marker file created by install.py when installation completed
SWARMUI_INSTALLED_MARKER = os.path.join(SWARMUI_DIR, ".installed")

# Ensure we're using absolute paths for better reliability
if not os.path.isabs(SWARMUI_DIR):
    SWARMUI_DIR = os.path.abspath(SWARMUI_DIR)
if not os.path.isabs(CLOUD_DIR):
    CLOUD_DIR = os.path.abspath(CLOUD_DIR)
if not os.path.isabs(LOG_DIR):
    LOG_DIR = os.path.abspath(LOG_DIR)

# Module-level cleanup guard to avoid duplicate cleanup prints/actions
_cleanup_done = False

def parse_arguments():
	"""Parse command line arguments and update global flags"""
	global FORCE_LOCAL_SWARMUI, FORCE_LOCAL_CLOUDFLARED
	
	parser = argparse.ArgumentParser(description='Start SwarmUI with Cloudflare tunnel')
	parser.add_argument('--force-local-swarmui', action='store_true',
						help='Force use of local SwarmUI installation (ignore external installations)')
	parser.add_argument('--force-local-cloudflared', action='store_true',
						help='Force use of local cloudflared installation (ignore external installations)')
	
	args = parser.parse_args()
	
	# Update global flags based on command line arguments
	if args.force_local_swarmui:
		FORCE_LOCAL_SWARMUI = True
	if args.force_local_cloudflared:
		FORCE_LOCAL_CLOUDFLARED = True
	
	return args

def _check_local_swarmui():
	"""Check if local SwarmUI installation exists (ignores external installations)"""
	global SWARMUI_DIR, SWARMUI_INSTALLED_MARKER
	
	# Check if the configured SWARMUI_DIR exists and has installation markers
	installed_marker = os.path.join(SWARMUI_DIR, ".installed")
	sln_file = os.path.join(SWARMUI_DIR, "SwarmUI.sln")
	
	if os.path.exists(installed_marker) or os.path.exists(sln_file):
		print(f"✅ Local SwarmUI found at: {SWARMUI_DIR}")
		return True
	
	print(f"❌ Local SwarmUI not found at: {SWARMUI_DIR}")
	return False

def _check_local_cloudflared():
	"""Check if local cloudflared installation exists (ignores external installations)"""
	cloudflared_name = "cloudflared.exe" if platform.system().lower() == "windows" else "cloudflared"
	local_path = os.path.join(CLOUD_DIR, cloudflared_name)
	
	if os.path.exists(local_path):
		print(f"✅ Local cloudflared found at: {local_path}")
		return True
	
	print(f"❌ Local cloudflared not found at: {local_path}")
	return False

def check_dependencies(verbose=True):
	"""Check if required dependencies are installed.

	When verbose=False, only prints error messages; success messages are suppressed.
	"""
	if verbose:
		print("🔍 Checking dependencies...")

	global SWARMUI_DIR, SWARMUI_INSTALLED_MARKER

	# Simplified import strategy - try to import install module
	install_module = None
	try:
		import swarmtunnel.install as install_module
	except ImportError:
		try:
			import sys
			import os
			parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
			if parent_dir not in sys.path:
				sys.path.insert(0, parent_dir)
			import swarmtunnel.install as install_module
		except ImportError:
			print("❌ Could not import install module. Please ensure you're running from the correct directory.")
			return False

	# Check SwarmUI installation
	if FORCE_LOCAL_SWARMUI:
		# Force use of local SwarmUI installation
		print("🔧 Force local SwarmUI mode: checking local installation only")
		if not _check_local_swarmui():
			print("❌ Local SwarmUI not found. Please run 'python install.py' first.")
			return False
	else:
		# Use normal detection (may find external installations)
		if not install_module.is_swarmui_installed():
			print("❌ SwarmUI not found. Offering to run installer...")
			try:
				install_module.install_swarmui()
			except Exception as e:
				print(f"❌ Installer failed or was cancelled: {e}")
				print("Please run 'python install.py' manually.")
				return False
			# Re-check and fail if still not found
			if not install_module.is_swarmui_installed():
				print("❌ SwarmUI still not found after installer. Aborting.")
				return False

	# Update module-level SWARMUI_DIR and marker from environment if installer/discovery changed it
	SWARMUI_DIR = os.environ.get('SWARMUI_DIR', SWARMUI_DIR)
	SWARMUI_INSTALLED_MARKER = os.path.join(SWARMUI_DIR, '.installed')

	# Check cloudflared installation
	if FORCE_LOCAL_CLOUDFLARED:
		# Force use of local cloudflared installation
		print("🔧 Force local cloudflared mode: checking local installation only")
		if not _check_local_cloudflared():
			print("❌ Local cloudflared not found. Please run 'python install.py' first.")
			return False
	else:
		# Use normal detection (may find external installations)
		if not install_module.is_cloudflared_installed():
			print("❌ cloudflared not found. Please run 'python install.py' first.")
			return False

	# Check if .NET is available
	try:
		result = subprocess.run(["dotnet", "--version"], capture_output=True, text=True)
		if result.returncode != 0:
			print("❌ .NET not found. Please install .NET 8 SDK.")
			return False
		if verbose:
			print(f"✅ .NET {result.stdout.strip()} found")
	except FileNotFoundError:
		print("❌ .NET not found. Please install .NET 8 SDK.")
		return False

	if verbose:
		print("✅ All dependencies found")
	return True


def build_swarmui():
	"""Build SwarmUI if needed"""
	# Consider platform-specific launcher scripts as valid "built" artifacts
	# since some installations run via the provided launch scripts instead of a packaged exe.
	os_name = platform.system().lower()
	
	# First try to find any launcher script anywhere under SWARMUI_DIR
	try:
		launcher = _find_launch_script(SWARMUI_DIR)
		if launcher:
			print(f"ℹ️ Found launcher script: {launcher}")
			return True
	except Exception as e:
		print(f"ℹ️ Error searching for launcher scripts: {e}")

	# Fall back to checking the expected binary locations
	if os_name == 'windows':
		exe_path = os.path.join(SWARMUI_DIR, "src", "bin", "live_release", "SwarmUI.exe")
		if os.path.exists(exe_path):
			print(f"ℹ️ Found SwarmUI executable: {exe_path}")
			return True
	elif os_name == 'darwin':
		exe_path = os.path.join(SWARMUI_DIR, "src", "bin", "live_release", "SwarmUI")
		if os.path.exists(exe_path):
			print(f"ℹ️ Found SwarmUI executable: {exe_path}")
			return True
	else:
		exe_path = os.path.join(SWARMUI_DIR, "src", "bin", "live_release", "SwarmUI")
		if os.path.exists(exe_path):
			print(f"ℹ️ Found SwarmUI executable: {exe_path}")
			return True

	# Check if SwarmUI.sln exists (indicates source installation)
	sln_path = os.path.join(SWARMUI_DIR, "SwarmUI.sln")
	if os.path.exists(sln_path):
		print(f"ℹ️ Found SwarmUI solution file: {sln_path}")
		print("ℹ️ SwarmUI appears to be installed but may need to be built.")
		print("ℹ️ Attempting to start with available launcher scripts...")
		return True

	# If neither a launcher nor an expected binary exists, ask the user to run installer
	print("❌ SwarmUI is not built or no launch script found. Please run 'python install.py' to install and/or build SwarmUI.")
	return False


def _find_launch_script(root_dir):
	"""Search root_dir for known launch scripts up to a limited depth.
	Returns path to script or None.
	"""
	candidates = [
		'launch-windows.bat', 'launch_windows.bat',
		'launch-linux.sh', 'launch_linux.sh',
		'launch-macos.sh', 'launch_macos.sh'
	]

	# First check the root directory directly
	for name in candidates:
		script_path = os.path.join(root_dir, name)
		if os.path.exists(script_path):
			return script_path

	# Walk the tree but limit depth to avoid long scans
	max_depth = 3
	root_dir = os.path.abspath(root_dir)
	for dirpath, dirnames, filenames in os.walk(root_dir):
		# compute depth relative to root_dir
		rel = os.path.relpath(dirpath, root_dir)
		if rel == '.':
			depth = 0
		else:
			depth = rel.count(os.sep) + 1
		if depth > max_depth:
			# don't descend further
			dirnames[:] = []
			continue

		for name in candidates:
			if name in filenames:
				return os.path.join(dirpath, name)

	return None


def is_swarmui_built():
	"""Return True if SwarmUI executable exists"""
	exe_path = os.path.join(SWARMUI_DIR, "src", "bin", "live_release", "SwarmUI.exe")
	if platform.system().lower() != "windows":
		exe_path = os.path.join(SWARMUI_DIR, "src", "bin", "live_release", "SwarmUI")
	return os.path.exists(exe_path)

def wait_for_service(url, timeout=60, check_interval=2):
	"""Wait for a service to become available"""
	print(f"🔍 Checking if {url} is available...")
	start_time = time.time()

	while time.time() - start_time < timeout:
		try:
			response = urlopen(url, timeout=5)
			if response.getcode() == 200:
				print(f"✅ {url} is available")
				return True
		except (URLError, Exception):
			pass

		time.sleep(check_interval)

	if timeout <= 10:
		print(f"ℹ️ Service not available at {url} (not started yet)")
	else:
		print(f"⏰ Service not available at {url} (timeout after {timeout}s)")
	return False

def start_swarmui():
	"""Start SwarmUI in the background"""
	print("🚀 Starting SwarmUI...")
	print(f"📍 Working directory: {SWARMUI_DIR}")

	# Set environment variables
	env = os.environ.copy()
	env["ASPNETCORE_ENVIRONMENT"] = "Production"
	env["ASPNETCORE_URLS"] = f"http://*:{SWARMUI_PORT}"
	env["DOTNET_CLI_TELEMETRY_OPTOUT"] = "1"

	# Prefer launcher scripts if present (they may perform setup/build and start the app)
	os_name = platform.system().lower()
	launcher_cmd = None
	if os_name == 'windows':
		launcher = _find_launch_script(SWARMUI_DIR)
		if launcher and launcher.lower().endswith('.bat'):
			# Run the batch file but capture its output so we can write logs and tail them
			cmd = f'"{launcher}"'
			use_shell = True
		else:
			exe_path = os.path.join(SWARMUI_DIR, "src", "bin", "live_release", "SwarmUI.exe")
			cmd = [exe_path]
			use_shell = False
	elif os_name == 'darwin':
		launcher = os.path.join(SWARMUI_DIR, 'launch-macos.sh')
		if os.path.exists(launcher):
			cmd = ["/bin/bash", launcher]
			use_shell = False
		else:
			exe_path = os.path.join(SWARMUI_DIR, "src", "bin", "live_release", "SwarmUI")
			cmd = [exe_path]
			use_shell = False
	else:
		launcher = os.path.join(SWARMUI_DIR, 'launch-linux.sh')
		if os.path.exists(launcher):
			cmd = ["/bin/bash", launcher]
			use_shell = False
		else:
			exe_path = os.path.join(SWARMUI_DIR, "src", "bin", "live_release", "SwarmUI")
			cmd = [exe_path]
			use_shell = False

	try:
		# On Windows, start SwarmUI directly in a new PowerShell window
		# This ensures the process is tied to the window that shows the logs
		if platform.system().lower() == 'windows':
			print(f"ℹ️ Starting SwarmUI in new PowerShell window...")
			
			# Build the PowerShell command to run SwarmUI
			if use_shell and isinstance(cmd, str):
				# For batch files, we need to run them in cmd
				powershell_cmd = f'cmd /c "cd /d "{SWARMUI_DIR}" && {cmd}"'
			else:
				# For executables, we can run them directly
				if isinstance(cmd, list):
					cmd_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in cmd)
				else:
					cmd_str = cmd
				# Use & operator to execute the command properly in PowerShell
				powershell_cmd = f'cd "{SWARMUI_DIR}"; & {cmd_str}'
			
			# Create the PowerShell command
			full_cmd = powershell_cmd
			
			# Start PowerShell with the command and pass environment variables directly
			creationflags = getattr(subprocess, 'CREATE_NEW_CONSOLE', 0)
			si = subprocess.STARTUPINFO()
			si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
			si.wShowWindow = 1  # SW_SHOWNORMAL
			
			process = subprocess.Popen([
				'powershell', '-NoExit', '-Command', full_cmd
			], env=env, creationflags=creationflags, startupinfo=si)
			
			# Create a dummy process object that we can monitor
			# The actual SwarmUI process will be in the PowerShell window
			class DummyProcess:
				def __init__(self, pid):
					self.pid = pid
					self._log_queue = queue.Queue()
				
				def poll(self):
					# Check if the PowerShell process is still running
					if psutil:
						return None if psutil.pid_exists(self.pid) else 1
					else:
						# Fallback: assume it's still running
						return None
				
				def terminate(self):
					if psutil:
						try:
							proc = psutil.Process(self.pid)
							proc.terminate()
						except:
							pass
				
				def kill(self):
					if psutil:
						try:
							proc = psutil.Process(self.pid)
							proc.kill()
						except:
							pass
			
			dummy_process = DummyProcess(process.pid)
			
			# Wait briefly to allow process to initialize
			time.sleep(3)
			
			print("✅ SwarmUI started successfully in PowerShell window")
			return dummy_process
		
		else:
			# For non-Windows platforms, use the original approach
			print(f"ℹ️ Executing command: {cmd}")
			process = subprocess.Popen(
				cmd,
				env=env,
				cwd=SWARMUI_DIR,
				shell=use_shell,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT,
				text=True
			)

			# Create a log file and start a thread to stream process output into it and into a queue
			# Ensure log dir exists for logs
			os.makedirs(LOG_DIR, exist_ok=True)
			log_path = os.path.join(LOG_DIR, "swarmui.log")
			def _stream_output(proc, path, q):
				try:
					with open(path, 'a', encoding='utf-8') as lf:
						while True:
							line = proc.stdout.readline()
							if line == '' and proc.poll() is not None:
								break
							if not line:
								time.sleep(0.1)
								continue
							lf.write(line)
							lf.flush()
							q.put(line)
				except Exception:
					pass

			log_queue = queue.Queue()
			t = threading.Thread(target=_stream_output, args=(process, log_path, log_queue), daemon=True)
			t.start()

			# Wait briefly to allow process to initialize
			time.sleep(3)

			# Attach the queue so other functions can read lines (extract_tunnel_url)
			process._log_queue = log_queue

			# Check if process is still running
			if process.poll() is None:
				print("✅ SwarmUI started successfully")
				return process
			else:
				# Try to drain any captured output
				try:
					out_lines = []
					while not log_queue.empty():
						out_lines.append(log_queue.get_nowait())
					print(f"❌ SwarmUI failed to start")
					if out_lines:
						print("".join(out_lines))
				except Exception:
					pass
				return None

	except Exception as e:
		print(f"❌ Error starting SwarmUI: {e}")
		return None

def create_tunnel_config():
	"""Create tunnel configuration file"""
	# Ensure logs directory exists
	os.makedirs(LOG_DIR, exist_ok=True)
	
	config = f"""
	tunnel: swarmui-tunnel

	ingress:
	  - service: http://localhost:{SWARMUI_PORT}
	"""

	with open(TUNNEL_CONFIG_FILE, 'w') as f:
		f.write(config.strip())

	print(f"✅ Created tunnel config: {TUNNEL_CONFIG_FILE}")

def start_tunnel():
	"""Start Cloudflare tunnel"""
	print("🌐 Starting Cloudflare tunnel...")

	# Start tunnel using the tunnel command (creates a quick tunnel)
	cloudflared_name = "cloudflared.exe" if platform.system().lower() == "windows" else "cloudflared"
	
	if FORCE_LOCAL_CLOUDFLARED:
		# Force use of local cloudflared installation
		print("🔧 Force local cloudflared mode: using local installation only")
		cloudflared_path = os.path.join(CLOUD_DIR, cloudflared_name)
		if not os.path.exists(cloudflared_path):
			print(f"❌ Local cloudflared not found at: {cloudflared_path}")
			return None
		print(f"ℹ️ Using local cloudflared: {cloudflared_path}")
	else:
		# Use the same detection logic as install.py: prefer system PATH, then CWD, then CLOUD_DIR
		from shutil import which
		which_path = which(cloudflared_name)
		if which_path is not None:
			cloudflared_path = which_path
			print(f"ℹ️ Using cloudflared from system PATH: {cloudflared_path}")
		else:
			# Check current working directory
			cwd_path = os.path.join(os.getcwd(), cloudflared_name)
			if os.path.exists(cwd_path):
				cloudflared_path = cwd_path
				print(f"ℹ️ Using cloudflared from current directory: {cloudflared_path}")
			else:
				# Check the local cloudflared directory
				local_path = os.path.join(CLOUD_DIR, cloudflared_name)
				if os.path.exists(local_path):
					cloudflared_path = local_path
					print(f"ℹ️ Using cloudflared from local directory: {cloudflared_path}")
				else:
					# Fallback to just the name (will fail if not in PATH)
					cloudflared_path = cloudflared_name
					print(f"ℹ️ Using cloudflared from PATH: {cloudflared_path}")

	try:
		# On Windows, start cloudflared directly in a new PowerShell window
		# This ensures the process is tied to the window that shows the logs
		if platform.system().lower() == 'windows':
			print(f"ℹ️ Starting cloudflared in new PowerShell window...")
			
			# Build the PowerShell command to run cloudflared
			# Use & operator to execute the command properly in PowerShell
			cloudflared_cmd = f'& "{cloudflared_path}" tunnel --url http://localhost:{SWARMUI_PORT}'
			powershell_cmd = cloudflared_cmd
			
			# Start PowerShell with the command
			creationflags = getattr(subprocess, 'CREATE_NEW_CONSOLE', 0)
			si = subprocess.STARTUPINFO()
			si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
			si.wShowWindow = 1  # SW_SHOWNORMAL
			
			process = subprocess.Popen([
				'powershell', '-NoExit', '-Command', powershell_cmd
			], creationflags=creationflags, startupinfo=si)
			
			# Create a dummy process object that we can monitor
			# The actual cloudflared process will be in the PowerShell window
			class DummyProcess:
				def __init__(self, pid):
					self.pid = pid
					self._log_queue = queue.Queue()
				
				def poll(self):
					# Check if the PowerShell process is still running
					if psutil:
						return None if psutil.pid_exists(self.pid) else 1
					else:
						# Fallback: assume it's still running
						return None
				
				def terminate(self):
					if psutil:
						try:
							proc = psutil.Process(self.pid)
							proc.terminate()
						except:
							pass
				
				def kill(self):
					if psutil:
						try:
							proc = psutil.Process(self.pid)
							proc.kill()
						except:
							pass
			
			dummy_process = DummyProcess(process.pid)
			
			# Allow a short time for cloudflared to initialize
			time.sleep(2)
			
			print("✅ Cloudflare tunnel started in PowerShell window")
			return dummy_process
		
		else:
			# For non-Windows platforms, use the original approach
			process = subprocess.Popen([
				cloudflared_path, "tunnel", "--url", f"http://localhost:{SWARMUI_PORT}"
			], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

			# Create log file and streamer thread
			# Ensure log dir exists for logs
			os.makedirs(LOG_DIR, exist_ok=True)
			log_path = os.path.join(LOG_DIR, "cloudflared.log")
			def _stream_output(proc, path, q):
				try:
					with open(path, 'a', encoding='utf-8') as lf:
						while True:
							line = proc.stdout.readline()
							if line == '' and proc.poll() is not None:
								break
							if not line:
								time.sleep(0.1)
								continue
							lf.write(line)
							lf.flush()
							q.put(line)
				except Exception:
					pass

			log_queue = queue.Queue()
			t = threading.Thread(target=_stream_output, args=(process, log_path, log_queue), daemon=True)
			t.start()

			# Allow a short time for cloudflared to initialize
			time.sleep(2)

			# Attach queue for extract_tunnel_url to use
			process._log_queue = log_queue

			if process.poll() is None:
				print("✅ Cloudflare tunnel started")
				return process
			else:
				# Drain any captured output
				try:
					out_lines = []
					while not log_queue.empty():
						out_lines.append(log_queue.get_nowait())
					print(f"❌ Tunnel failed to start")
					if out_lines:
						print("".join(out_lines))
				except Exception:
					pass
				return None

	except Exception as e:
		print(f"❌ Error starting tunnel: {e}")
		return None

def extract_tunnel_url(tunnel_process, timeout=30):
	"""Extract the tunnel URL from the tunnel process output"""
	print("🔍 Extracting tunnel URL...")

	# Check if this is a DummyProcess (Windows PowerShell window)
	if hasattr(tunnel_process, 'pid') and not hasattr(tunnel_process, 'stdout'):
		# This is a DummyProcess running in PowerShell window
		# We can't capture output, so we'll use a different approach
		print("ℹ️ Tunnel running in PowerShell window - checking for tunnel URL...")
		
		# For Windows with DummyProcess, we'll try to detect the tunnel URL
		# by checking if the tunnel is working by testing connectivity
		start_time = time.time()
		while time.time() - start_time < timeout:
			if tunnel_process.poll() is not None:
				print("❌ Tunnel process terminated")
				return None
			
			# Give cloudflared time to establish the tunnel
			time.sleep(2)
			
			# For now, we'll return a placeholder URL since we can't extract it
			# The user will see the actual URL in the PowerShell window
			print("ℹ️ Tunnel is running in PowerShell window")
			print("ℹ️ Check the PowerShell window for the tunnel URL")
			print("ℹ️ The URL will be in the format: https://[random-name].trycloudflare.com")
			return "https://tunnel-url-in-powershell-window.trycloudflare.com"
		
		print("❌ Could not extract tunnel URL")
		return None
	
	# Original approach for non-Windows or when we can capture output
	start_time = time.time()
	# Prefer reading from the attached log queue if present (we started a streamer)
	log_queue = getattr(tunnel_process, '_log_queue', None)
	while time.time() - start_time < timeout:
		if tunnel_process.poll() is not None:
			print("❌ Tunnel process terminated")
			return None

		try:
			if log_queue is not None:
				try:
					# Wait up to a short interval for a line
					line = log_queue.get(timeout=1)
				except Exception:
					line = None
			else:
				line = tunnel_process.stdout.readline()

			if line:
				match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
				if match:
					tunnel_url = match.group(0)
					print(f"✅ Found tunnel URL: {tunnel_url}")
					return tunnel_url
		except Exception:
			pass

		time.sleep(0.1)

	print("❌ Could not extract tunnel URL")
	return None

def cleanup(swarmui_process, tunnel_process):
	"""Clean up processes and files"""
	global _cleanup_done
	if _cleanup_done:
		return
	_cleanup_done = True
	print("\n🧹 Cleaning up...")

	# Terminate processes
	if swarmui_process:
		try:
			swarmui_process.terminate()
			swarmui_process.wait(timeout=5)
		except:
			swarmui_process.kill()
	else:
		print("ℹ️ SwarmUI was already running, not stopping it")

	if tunnel_process:
		try:
			tunnel_process.terminate()
			tunnel_process.wait(timeout=5)
		except:
			tunnel_process.kill()

	# Remove config file if it exists
	if os.path.exists(TUNNEL_CONFIG_FILE):
		os.remove(TUNNEL_CONFIG_FILE)

	print("✅ Cleanup complete")

def signal_handler(signum, frame):
	"""Handle interrupt signals"""
	print("\n🛑 Received interrupt signal")
	cleanup(swarmui_process, tunnel_process)
	sys.exit(0)


def main():
	"""Main function"""
	global swarmui_process, tunnel_process, FORCE_LOCAL_SWARMUI, FORCE_LOCAL_CLOUDFLARED
	swarmui_process = None
	tunnel_process = None

	# Parse command line arguments
	args = parse_arguments()

	# Set up signal handlers
	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.SIGTERM, signal_handler)

	print("=== SwarmUI with Cloudflare Tunnel ===")
	print(f"📍 SwarmUI Directory: {SWARMUI_DIR}")
	print(f"🌐 Cloudflared Directory: {CLOUD_DIR}")
	print(f"📝 Log Directory: {LOG_DIR}")
	
	# Show test mode information if force flags are set
	if FORCE_LOCAL_SWARMUI or FORCE_LOCAL_CLOUDFLARED:
		print("🔧 Test Mode Active:")
		if FORCE_LOCAL_SWARMUI:
			print("  - Force local SwarmUI: YES")
		if FORCE_LOCAL_CLOUDFLARED:
			print("  - Force local cloudflared: YES")

	try:
		# Check dependencies (quiet on success)
		if not check_dependencies(verbose=False):
			sys.exit(1)

		# Build SwarmUI
		if not build_swarmui():
			sys.exit(1)

		# Check if SwarmUI is already running
		print("🔍 Checking if SwarmUI is already running...")
		if wait_for_service(SWARMUI_URL, timeout=5, check_interval=1):
			print("✅ SwarmUI is already running, connecting to existing instance")
			swarmui_process = None  # No need to start a new process
		else:
			print("ℹ️ SwarmUI not running, starting new instance...")
			# Start SwarmUI
			swarmui_process = start_swarmui()
			if not swarmui_process:
				print("❌ Failed to start SwarmUI process")
				sys.exit(1)

			# Wait for SwarmUI to be ready
			print("⏳ Waiting for SwarmUI to become available...")
			if not wait_for_service(SWARMUI_URL, timeout=120):  # Give more time for first startup
				print("❌ SwarmUI failed to start properly")
				cleanup(swarmui_process, None)
				sys.exit(1)

		# Start tunnel
		tunnel_process = start_tunnel()
		if not tunnel_process:
			print("❌ Failed to start tunnel")
			cleanup(swarmui_process, None)
			sys.exit(1)

		# Extract tunnel URL
		tunnel_url = extract_tunnel_url(tunnel_process)
		if not tunnel_url:
			print("❌ Failed to get tunnel URL")
			cleanup(swarmui_process, tunnel_process)
			sys.exit(1)

		print("\n" + "="*60)
		print("🎉 SwarmUI is now running!")
		print(f"📍 Local URL: {SWARMUI_URL}")
		
		# Check if we got a placeholder URL (Windows PowerShell window case)
		if tunnel_url == "https://tunnel-url-in-powershell-window.trycloudflare.com":
			print("🌐 Tunnel URL: Check the PowerShell window for the tunnel URL")
			print("   (The URL will be in the format: https://[random-name].trycloudflare.com)")
		else:
			print(f"🌐 Tunnel URL: {tunnel_url}")
		
		print("="*60)

	except Exception as e:
		print(f"\n❌ Error: {e}")
		import traceback
		traceback.print_exc()
	finally:
		cleanup(swarmui_process, tunnel_process)

if __name__ == "__main__":
	main()

