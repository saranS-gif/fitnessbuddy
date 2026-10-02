@echo off
echo ===================================================
echo [FitBuddy] Setting up FitBuddy Virtual Environment...
echo ===================================================

cd /d "%~dp0"

if not exist venv (
    echo [FitBuddy] Creating virtual environment 'venv'...
    python -m venv venv
) else (
    echo [FitBuddy] Virtual environment 'venv' already exists.
)

if not exist .env (
    if exist config\.env.example (
        echo [FitBuddy] Creating .env from config\.env.example...
        copy config\.env.example .env
    ) else if exist .env.example (
        echo [FitBuddy] Creating .env from .env.example...
        copy .env.example .env
    )
)

echo [FitBuddy] Installing dependencies from requirements.txt...
venv\Scripts\python.exe -m pip install -r requirements.txt

echo ===================================================
echo [FitBuddy] Setup complete! Starting FitBuddy...
echo ===================================================
set PYTHONPATH=%~dp0backend;%~dp0;%PYTHONPATH%
venv\Scripts\python.exe run.py
pause
