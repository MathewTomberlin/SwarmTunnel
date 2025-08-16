@echo off
REM SwarmTunnel Uninstaller Batch File
REM This batch file opens a separate terminal window to run the Python uninstaller

REM Check for help flag
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help
if "%1"=="-?" goto :show_help

echo Starting SwarmTunnel Uninstaller...
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

REM Check if uninstall.py exists
if not exist "src\swarmtunnel\uninstall.py" (
    echo ERROR: src\swarmtunnel\uninstall.py not found in current directory
    echo Please run this batch file from the SwarmTunnel directory
    pause
    exit /b 1
)

REM Build command line arguments
set "args="
:parse_args
if "%1"=="" goto :run_uninstaller
set "args=%args% %1"
shift
goto :parse_args

:run_uninstaller
REM Open a new terminal window and run the uninstaller
echo Opening uninstaller in new window...
start "SwarmTunnel Uninstaller" cmd /c "python src/swarmtunnel/uninstall.py%args% && echo. && echo Uninstallation completed. && pause"

REM Wait a moment for the window to open
timeout /t 2 /nobreak >nul

echo.
echo Uninstaller window opened. You can close this window.
echo The uninstallation will continue in the new terminal window.
echo.
echo If the uninstallation fails, the terminal window will stay open
echo so you can see the error messages.
echo.
pause
exit /b 0

:show_help
echo SwarmTunnel Uninstaller
echo ======================
echo.
echo Usage: uninstall.bat [options]
echo.
echo Options:
echo   --help, -h, -?           Show this help message
echo   [other args]             Pass additional arguments to uninstall.py
echo.
echo Examples:
echo   uninstall.bat                                    Normal uninstallation
echo   uninstall.bat --force                           Force uninstallation
echo.
echo This will safely remove all SwarmTunnel components including:
echo   - SwarmUI directory and Git repository
echo   - cloudflared files and directories
echo   - Log files and temporary files
echo.
pause
exit /b 0
