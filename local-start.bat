@echo off
REM SwarmTunnel Local Start Batch File
REM This batch file is specifically for running start.py with SwarmTunnel installations of 
REM SwarmUI and cloudflared instead of any detected externally

echo Starting SwarmTunnel (LOCAL)...
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

REM Check if start.py exists
if not exist "src\swarmtunnel\start.py" (
    echo ERROR: src\swarmtunnel\start.py not found in current directory
    echo Please run this batch file from the SwarmTunnel directory
    pause
    exit /b 1
)

REM Default test start with both force flags
echo Local Configuration:
echo   - Force local SwarmUI: YES
echo   - Force local cloudflared: YES
echo.

REM Open a new terminal window and run start.py with test flags
echo Opening local start in new window...
start "SwarmTunnel Local Start" cmd /c "python src/swarmtunnel/start.py --force-local-swarmui --force-local-cloudflared && echo. && echo Start completed. Press any key to close... && pause"

REM Wait a moment for the window to open
timeout /t 2 /nobreak >nul
exit 0

:show_help
echo SwarmTunnel Test Starter
echo ========================
echo.
echo Usage: test-start.bat [option]
echo.
echo This batch file is specifically for testing start.py with local installations.
echo It forces start.py to use local SwarmUI and cloudflared instead of detecting external ones.
echo.
echo Options:
echo   --full-test              Run complete test cycle of install + start + cleanup
echo   --cleanup                Run cleanup only and remove test installations
echo   --help, -h, -?           Show this help message
echo   (no args)                Run test start with forced local flags
echo.
echo Examples:
echo   test-start.bat                    Test start and force local component usage
echo   test-start.bat --full-test        Complete test cycle
echo   test-start.bat --cleanup          Clean up test installations
echo.
echo Test Configuration:
echo   - Force local SwarmUI: YES
echo   - Force local cloudflared: YES
echo   - Skip external component detection: YES
echo.
echo This is useful for:
echo   - Testing start.py when you have SwarmUI/cloudflared elsewhere
echo   - Verifying local installations work correctly
echo   - Development and debugging of start scripts
echo.
pause
exit /b 0
