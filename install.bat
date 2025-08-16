@echo off
REM SwarmTunnel Installer Batch File
REM This batch file opens a separate terminal window to run the Python installer

REM Check for help flag
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help
if "%1"=="-?" goto :show_help

echo Starting SwarmTunnel Installer...
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

REM Check if install.py exists
if not exist "src\swarmtunnel\install.py" (
    echo ERROR: src\swarmtunnel\install.py not found in current directory
    echo Please run this batch file from the SwarmTunnel directory
    pause
    exit /b 1
)

REM Build command line arguments
set "args="
:parse_args
if "%1"=="" goto :run_installer
set "args=%args% %1"
shift
goto :parse_args

:run_installer
REM Open a new terminal window and run the installer
echo Opening installer in new window...
start "SwarmTunnel Installer" cmd /c "python src/swarmtunnel/install.py%args% && echo. && pause"

REM Wait a moment for the window to open
timeout /t 2 /nobreak >nul
exit 0

:show_help
echo SwarmTunnel Installer
echo ====================
echo.
echo Usage: install.bat [options]
echo.
echo Options:
echo   --skip-swarmui-check     Force SwarmUI installation even if detected elsewhere
echo   --force-cloudflared-install  Force cloudflared installation even if detected elsewhere
echo   --help, -h, -?           Show this help message
echo.
echo Examples:
echo   install.bat                                    Normal installation
echo   install.bat --skip-swarmui-check              Force SwarmUI install
echo   install.bat --force-cloudflared-install       Force cloudflared install
echo   install.bat --skip-swarmui-check --force-cloudflared-install  Force both
echo.
echo Testing Options:
echo   These flags are useful for testing installation even when components
echo   are already installed elsewhere on your system.
echo.
pause
exit /b 0
