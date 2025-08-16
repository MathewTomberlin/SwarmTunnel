@echo off
REM SwarmTunnel Test Runner Batch File
REM This batch file opens a separate terminal window to run the Python test suite

REM Check for help flag
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help
if "%1"=="-?" goto :show_help

echo Starting SwarmTunnel Test Suite...
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

REM Check if run_tests.py exists
if not exist "src\tests\run_tests.py" (
    echo ERROR: src\tests\run_tests.py not found in current directory
    echo Please run this batch file from the SwarmTunnel directory
    pause
    exit /b 1
)

REM Build command line arguments
set "args="
:parse_args
if "%1"=="" goto :run_tests
set "args=%args% %1"
shift
goto :parse_args

:run_tests
REM Open a new terminal window and run the test suite
echo Opening test suite in new window...
start "SwarmTunnel Test Suite" cmd /c "cd src\tests && python run_tests.py%args% && echo. && echo Test suite completed. && pause"

REM Wait a moment for the window to open
timeout /t 2 /nobreak >nul
exit 0

:show_help
echo SwarmTunnel Test Suite
echo =====================
echo.
echo Usage: run_tests.bat [options]
echo.
echo Options:
echo   --type TYPE              Type of tests to run (see types below)
echo   --verbose, -v            Verbose output
echo   --help, -h, -?           Show this help message
echo.
echo Test Types:
echo   all                      All tests from both install.py and start.py suites
echo.
echo   Install.py Tests:
echo     install-unit           Fast unit tests (no external dependencies)
echo     install-integration    Integration tests (mocked dependencies)
echo     install-error          Error handling and edge cases
echo     install-system         System tests (requires internet)
echo     install-env            Environment variables and CLI tests
echo     install-all            All install.py tests
echo.
echo   Start.py Tests:
echo     start-unit             Fast unit tests (no external dependencies)
echo     start-integration      Integration tests (mocked dependencies)
echo     start-error            Error handling and cleanup tests
echo     start-env              Environment variables and CLI tests
echo     start-all              All start.py tests
echo.
echo Examples:
echo   run_tests.bat                                    Run all tests
echo   run_tests.bat --type install-unit               Run only install unit tests
echo   run_tests.bat --type start-all                  Run all start.py tests
echo   run_tests.bat --type install-system --verbose   Run system tests with verbose output
echo.
echo Environment Variables:
echo   TEST_WITH_INTERNET=1     Enable internet-dependent tests
echo.
echo Examples with environment variables:
echo   set TEST_WITH_INTERNET=1
echo   run_tests.bat --type install-system
echo.
pause
exit /b 0
