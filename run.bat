@echo off
cd /d "%~dp0"
echo ===================================================
echo [FitBuddy] Starting FitBuddy Application...
echo [FitBuddy] Open in your browser: http://localhost:8000
echo ===================================================
if not exist venv\Scripts\python.exe (
    echo [FitBuddy] Error: Virtual environment not found in .\venv!
    echo [FitBuddy] Please double click setup.bat first to install.
    pause
    exit /b 1
)
venv\Scripts\python.exe run.py
pause
