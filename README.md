# SwarmTunnel

SwarmTunnel is a tool that automatically installs and configures SwarmUI with Cloudflare Tunnel for easy remote access to your SwarmUI instance. It provides a seamless way to get SwarmUI running with secure remote access via Cloudflare's Quick Tunnel service.

## 🚀 Quick Start

### Windows Users (Recommended)

1. **Download** the SwarmTunnel files to a directory
2. **Double-click** `install.bat` to start the installer
3. **Follow** the prompts in the new terminal window
4. **Double-click** `start.bat` to launch SwarmUI with Quick Tunnel

### Linux and macOS Users

1. **Open terminal** in the SwarmTunnel directory
2. **Run**: `python3 src/swarmtunnel/install.py`
3. **Follow** the installation prompts
4. **Run**: `python3 src/swarmtunnel/start.py` to launch

**Note**: Linux and macOS support is provided through Python scripts. Batch files are Windows-only.

## 📋 Prerequisites

- **Python 3.7+** installed and available in PATH
- **Git** installed and available in PATH
- **Internet connection** for downloading SwarmUI and cloudflared
- **Windows**: Administrator privileges may be required for permission fixes

## 🔧 Installation

### Method 1: Windows Batch File (Recommended for Windows)

Simply double-click `install.bat` or run it from Command Prompt:

```cmd
install.bat
```

**Features:**
- ✅ Opens in a separate terminal window
- ✅ Automatically closes when complete
- ✅ Passes through command line arguments
- ✅ Error handling and user-friendly messages

### Method 2: Python Script (Cross-Platform)

**Windows:**
```cmd
python src/swarmtunnel/install.py
```

**Linux/macOS:**
```bash
python3 src/swarmtunnel/install.py
```

### Method 3: With Force Flags

```bash
# Force reinstall SwarmUI (skip detection of existing installations)
python src/swarmtunnel/install.py --skip-swarmui-check

# Force reinstall cloudflared
python src/swarmtunnel/install.py --force-cloudflared-install

# Force both components
python src/swarmtunnel/install.py --skip-swarmui-check --force-cloudflared-install
```

### Installation Process

The installer will:

1. **Check dependencies** (Python, Git, .NET)
2. **Detect existing installations** (unless forced)
3. **Clone SwarmUI repository** (if needed)
4. **Download cloudflared** for your platform
5. **Fix Windows permissions** (if needed)
6. **Configure LAN access** (bind to 0.0.0.0:7801)
7. **Launch platform-specific installer** (Windows/macOS/Linux)
8. **Wait for web UI** to become available

## 🎯 Starting SwarmUI

### Method 1: Windows Batch File (Recommended for Windows)

Double-click `start.bat` or run:

```cmd
start.bat
```

**Features:**
- ✅ Opens SwarmUI in a separate PowerShell window
- ✅ Opens cloudflared tunnel in a separate PowerShell window
- ✅ Automatically detects existing SwarmUI installations
- ✅ Provides local and tunnel URLs
- ✅ Graceful shutdown with Ctrl+C

### Method 2: Python Script (Cross-Platform)

**Windows:**
```cmd
python src/swarmtunnel/start.py
```

**Linux/macOS:**
```bash
python3 src/swarmtunnel/start.py
```

### Method 3: With Force Flags

```bash
# Force use of local SwarmUI installation
python src/swarmtunnel/start.py --force-local-swarmui

# Force use of local cloudflared installation
python src/swarmtunnel/start.py --force-local-cloudflared

# Force both local components
python src/swarmtunnel/start.py --force-local-swarmui --force-local-cloudflared
```

## 🧪 Testing and Development

SwarmTunnel includes comprehensive testing tools and special batch files for development scenarios.

### Test Suite

**Windows Users:**
Use `run_tests.bat` to run the comprehensive test suite:

```cmd
run_tests.bat
```

**Linux/macOS Users:**
Use the Python test runner directly:

```bash
python3 src/tests/run_tests.py
```

**Test Categories:**
- ✅ **Unit Tests**: Fast tests for individual functions
- ✅ **Integration Tests**: Tests for complete workflows
- ✅ **Error Tests**: Tests for error handling and edge cases
- ✅ **System Tests**: Tests with real network dependencies
- ✅ **Environment Tests**: Tests for CLI arguments and environment variables

**Examples:**
```cmd
# Windows
run_tests.bat --type install-unit          # Fast install.py unit tests
run_tests.bat --type start-all             # All start.py tests
run_tests.bat --type all --verbose         # All tests with verbose output
run_tests.bat --help                       # Show all test options
```

```bash
# Linux/macOS
python3 src/tests/run_tests.py --type install-unit
python3 src/tests/run_tests.py --type start-all
python3 src/tests/run_tests.py --type all --verbose
python3 src/tests/run_tests.py --help
```

**Features:**
- ✅ Comprehensive coverage of both `install.py` and `start.py`
- ✅ Cross-platform testing support
- ✅ CI/CD ready test categories
- ✅ Detailed test documentation in `src/tests/TEST_README.md`

### Local Installation Testing

**Windows Users:**
Use `local-install.bat` to force installation of local components:

```cmd
local-install.bat
```

**Linux/macOS Users:**
Use Python script with force flags:

```bash
python3 src/swarmtunnel/install.py --skip-swarmui-check --force-cloudflared-install
```

**What it does:**
- ✅ Forces SwarmUI installation (skips detection)
- ✅ Forces cloudflared installation (skips detection)
- ✅ Useful when you have external installations
- ✅ Perfect for testing installation process

### Local Startup Testing

**Windows Users:**
Use `local-start.bat` to force use of local components:

```cmd
local-start.bat
```

**Linux/macOS Users:**
Use Python script with force flags:

```bash
python3 src/swarmtunnel/start.py --force-local-swarmui --force-local-cloudflared
```

**What it does:**
- ✅ Forces use of local SwarmUI installation
- ✅ Forces use of local cloudflared installation
- ✅ Skips external component detection
- ✅ Ideal for testing startup process

### Testing Scenarios

These tools are perfect for:

- **Development**: Testing when you have external installations
- **Debugging**: Isolating issues with local vs external components
- **CI/CD**: Automated testing scenarios
- **Documentation**: Creating reproducible test environments
- **Quality Assurance**: Comprehensive test coverage

## 🗑️ Uninstallation

### Method 1: Windows Batch File (Recommended for Windows)

```cmd
uninstall.bat
```

**Features:**
- ✅ Opens in a separate terminal window
- ✅ Safely removes all components
- ✅ Handles Windows permission issues
- ✅ Provides detailed progress information

### Method 2: Python Script (Cross-Platform)

**Windows:**
```cmd
python src/swarmtunnel/uninstall.py
```

**Linux/macOS:**
```bash
python3 src/swarmtunnel/uninstall.py
```

### What Gets Removed

- ✅ **SwarmUI directory** (including Git repository)
- ✅ **cloudflared directory** and executable files
- ✅ **logs directory** and log files
- ✅ **Installation markers** and temporary files
- ✅ **Permission fixes** (Windows)

### Windows Permission Handling

The uninstaller automatically handles Windows permission issues by:

1. **Killing processes** that might hold file handles
2. **Removing file attributes** (read-only, system, hidden)
3. **Taking ownership** of all files and folders
4. **Granting full control** to the current user
5. **Using elevated permissions** when necessary

## 📁 File Structure

```
SwarmTunnel/
├── install.bat              # Windows installer (Windows only)
├── local-install.bat        # Local installation testing (Windows only)
├── start.bat                # Windows launcher (Windows only)
├── local-start.bat          # Local startup testing (Windows only)
├── uninstall.bat            # Windows uninstaller (Windows only)
├── run_tests.bat            # Test runner (Windows only)
├── src/
│   └── swarmtunnel/
│       ├── install.py       # Core installation logic (cross-platform)
│       ├── start.py         # Core launcher logic (cross-platform)
│       ├── uninstall.py     # Uninstaller logic (cross-platform)
│       └── cleanup.py       # Cleanup utilities (cross-platform)
├── SwarmUI/                 # Installed SwarmUI (after installation)
├── cloudflared/             # Installed cloudflared (after installation)
├── logs/                    # Log files (created during operation)
└── README.md                # This file
```

## ⚙️ Configuration

### Environment Variables

You can customize installation paths using environment variables:

```bash
# SwarmUI installation directory
export SWARMUI_DIR="SwarmUI"

# cloudflared installation directory
export SWARMTUNNEL_CLOUDFLARED_DIR="cloudflared"

# Log directory
export SWARMTUNNEL_LOG_DIR="logs"

# Force local installations (for testing)
export SWARMTUNNEL_FORCE_LOCAL_SWARMUI=1
export SWARMTUNNEL_FORCE_LOCAL_CLOUDFLARED=1
```

### Command Line Options

#### Install Script Options

```bash
--skip-swarmui-check          # Force SwarmUI installation
--force-cloudflared-install   # Force cloudflared installation
--help                        # Show help message
```

#### Start Script Options

```bash
--force-local-swarmui         # Force use of local SwarmUI
--force-local-cloudflared     # Force use of local cloudflared
--help                        # Show help message
```

## 🔍 Troubleshooting

### Common Issues

#### Python Not Found
```
ERROR: Python is not installed or not found in PATH
```
**Solution:** Install Python from https://python.org/downloads/ and ensure "Add Python to PATH" is checked.

#### Git Not Found
```
'git' is not installed or not found in PATH
```
**Solution:** Install Git from https://git-scm.com/downloads

#### Permission Errors (Windows)
```
Could not automatically fix permissions for SwarmUI
```
**Solution:** 
1. Run Command Prompt as Administrator
2. Follow the manual commands provided by the script
3. Or use the uninstaller which handles permissions automatically

#### Network Issues
```
Network error downloading [URL]
```
**Solution:** Check your internet connection and firewall settings

### Getting Help

All batch files support help functionality:

```cmd
install.bat --help
start.bat --help
uninstall.bat --help
local-install.bat --help
local-start.bat --help
```

### Manual Cleanup

If automated uninstall fails:

1. **Close all applications** using SwarmUI files
2. **Open Command Prompt as Administrator**
3. **Run**: `rmdir /S /Q "SwarmUI"`
4. **Run**: `rmdir /S /Q "cloudflared"`
5. **Run**: `rmdir /S /Q "logs"`

## 🌐 What You Get

After successful installation and startup:

- **Local Access**: `http://localhost:7801`
- **Remote Access**: `https://[random-name].trycloudflare.com`
- **LAN Access**: `http://[your-ip]:7801` (if on same network)

### SwarmUI Features

- ✅ **Web-based UI** for Docker Swarm management
- ✅ **Real-time monitoring** of services and nodes
- ✅ **Service management** (deploy, scale, update)
- ✅ **Log viewing** and troubleshooting
- ✅ **Secure remote access** via Cloudflare Tunnel

### Cloudflare Tunnel Benefits

- ✅ **No port forwarding** required
- ✅ **SSL encryption** automatically
- ✅ **Works behind NAT/firewalls**
- ✅ **Temporary URLs** for quick sharing
- ✅ **No account required** for Quick Tunnel

## 🔒 Security Notes

- **Quick Tunnel URLs** are temporary and change each time
- **Local access** is available on your network
- **No persistent tunnel** - URLs expire when you stop the service
- **For production use**, consider setting up a permanent Cloudflare tunnel

## 🌐 Platform Support

- **Windows**: Full support with batch file launchers and Python scripts
- **Linux**: Python script support (batch files not available)
- **macOS**: Python script support (batch files not available)

**Note**: Linux and macOS users should use the Python scripts directly. The batch files are Windows-specific and will not work on other platforms.

## 📝 Logs and Debugging

Log files are created in the `logs/` directory:

- `swarmui.log` - SwarmUI application logs
- `cloudflared.log` - Cloudflare tunnel logs
- `swarmtunnel_install.log` - Installation tracking
- `tunnel_config.yml` - Cloudflare tunnel configuration file

## 🤝 Support

For issues:

1. **Check console output** for specific error messages
2. **Review log files** in the `logs/` directory
3. **Try the local batch files** for testing
4. **Ensure administrator privileges** on Windows
5. **Close conflicting applications** before installation/uninstall

## 📄 License

This project is open source. See the LICENSE file for details.
