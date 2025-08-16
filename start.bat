@echo off
REM SwarmTunnel Starter Batch File
REM This batch file opens a separate terminal window to run the Python starter

REM Check for help flag
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help
if "%1"=="-?" goto :show_help

echo Starting SwarmTunnel...
echo.

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

REM Check if SwarmUI is installed in common locations
REM Check current directory
if exist "SwarmUI\SwarmUI.sln" (
    echo Found SwarmUI in current directory
    goto :start_swarmtunnel
)

REM Check parent directory
if exist "..\SwarmUI\SwarmUI.sln" (
    echo Found SwarmUI in parent directory
    goto :start_swarmtunnel
)

REM Check user's Documents directory
if exist "%USERPROFILE%\Documents\SwarmUI\SwarmUI.sln" (
    echo Found SwarmUI in Documents directory
    goto :start_swarmtunnel
)

REM Check user's home directory
if exist "%USERPROFILE%\SwarmUI\SwarmUI.sln" (
    echo Found SwarmUI in home directory
    goto :start_swarmtunnel
)

REM If not found, try Python detection as fallback
python -c "import sys; sys.path.insert(0, 'src'); from swarmtunnel.install import is_swarmui_installed; exit(0 if is_swarmui_installed() else 1)" >nul 2>&1
if %errorlevel% equ 0 (
    echo Found SwarmUI via Python detection
    goto :start_swarmtunnel
)

REM SwarmUI not found
echo ERROR: SwarmUI is not installed or not found
echo Please run install.bat or python install.py first
echo.
echo The installer will help you find or install SwarmUI.
pause
exit /b 1

:start_swarmtunnel
REM Build command line arguments
set "args="
:parse_args
if "%1"=="" goto :run_starter
set "args=%args% %1"
shift
goto :parse_args

:run_starter
REM Open a new terminal window and run the starter
echo.
echo Opening SwarmTunnel in new window...
start "SwarmTunnel - SwarmUI & Quick Tunnel" cmd /c "python src/swarmtunnel/start.py%args% && echo. && echo SwarmTunnel completed. && pause"

REM Wait a moment for the window to open
timeout /t 2 /nobreak >nul
exit 0

:show_help
echo SwarmTunnel Starter
echo ==================
echo.
echo Usage: start.bat [options]
echo.
echo Options:
echo   --help, -h, -?           Show this help message
echo   [other args]             Pass additional arguments to start.py
echo.
echo Examples:
echo   start.bat                                    Normal startup
echo   start.bat --debug                          Start with debug mode
echo.
echo This will start SwarmUI and create a Cloudflare Quick Tunnel.
echo SwarmUI will open in your default browser.
echo.
pause
exit /b 0
