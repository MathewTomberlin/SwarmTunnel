@echo off
REM SwarmTunnel Local Installer Batch File
REM This batch file is specifically for running install.py to install
REM SwarmUI and cloudflared with SwarmTunnel instead of using installations detected externally

echo Starting SwarmTunnel Local Installer...
echo.

REM Check for help flag
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help
if "%1"=="-?" goto :show_help

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not found in PATH
    echo Please install Python from https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if install.py exists
if not exist "src\swarmtunnel\install.py" (
    echo ERROR: src\swarmtunnel\install.py not found in current directory
    echo Please run this batch file from the SwarmTunnel directory
    pause
    exit /b 1
)

REM Default test installation with both flags
echo Local Configuration:
echo   - Force SwarmUI installation: YES
echo   - Force cloudflared installation: YES
echo.

REM Open a new terminal window and run the installer with local flags
echo Opening local installer in new window...
start "SwarmTunnel Local Installer" cmd /c "python src/swarmtunnel/install.py --skip-swarmui-check --force-cloudflared-install && echo. && pause"

REM Wait a moment for the window to open
timeout /t 2 /nobreak >nul
exit 0

:show_help
echo SwarmTunnel Test Installer
echo =========================
echo.
echo Usage: test-install.bat [option]
echo.
echo This batch file is specifically for testing installation scenarios.
echo It forces installation of components even when they exist elsewhere.
echo.
echo Options:
echo   --full-test              Run complete test cycle of install + cleanup
echo   --cleanup                Run cleanup only and remove test installations
echo   --help, -h, -?           Show this help message
echo   (no args)                Run test installation with forced flags
echo.
echo Examples:
echo   test-install.bat                    Test installation and force both component installs
echo   test-install.bat --full-test        Complete test cycle
echo   test-install.bat --cleanup          Clean up test installations
echo.
echo Test Configuration:
echo   - Force SwarmUI installation: YES
echo   - Force cloudflared installation: YES
echo   - Skip existing component detection: YES
echo.
echo This is useful for:
echo   - Testing installation when you have SwarmUI/cloudflared elsewhere
echo   - Verifying installation process works correctly
echo   - Development and debugging of installation scripts
echo.
pause
exit /b 0
