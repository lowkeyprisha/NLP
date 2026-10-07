@echo off
REM Smart Downloads Organizer - Background Launcher
REM Double-click this to start the organizer in the background

echo Starting Smart Downloads Organizer...
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Checking dependencies...
pip install -r requirements.txt --quiet

REM Start the organizer
echo.
echo Organizer is starting...
echo Press Ctrl+C in this window to stop it.
echo.

python organizer.py

pause
