@echo off
setlocal EnableDelayedExpansion
title Auto-Installer

echo =======================================================
echo          AI Voice Cloning - Automated Installer
echo =======================================================
echo.
echo This script will automatically check for and install all
echo required dependencies to run the Voice Cloning AI on Windows.
echo.

:: 1. Check for Python
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python 3.10+ is missing!
    echo [i] Downloading and installing Python via winget...
    winget install -e --id Python.Python.3.10 --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo [X] Failed to install Python. Please install Python 3.10 manually from python.org
        pause
        exit /b 1
    )
    echo [i] Python installed successfully.
) else (
    echo [OK] Python is already installed.
)

:: 2. Check for Node.js
echo.
echo [2/4] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Node.js is missing!
    echo [i] Downloading and installing Node.js via winget...
    winget install -e --id OpenJS.NodeJS --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo [X] Failed to install Node.js. Please install manually from nodejs.org
        pause
        exit /b 1
    )
    echo [i] Node.js installed successfully.
) else (
    echo [OK] Node.js is already installed.
)

:: 3. Backend Setup
echo.
echo [3/4] Setting up the AI Engine (Backend)...
cd backend
if not exist "venv" (
    echo [i] Creating Python Virtual Environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

echo [i] Installing AI Libraries...
:: A simple progress visualization via pip's native progress bar
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r voice_clone_worker\requirements.txt

:: Check if Coqui is installed, if not run the setup scripts
if not exist "venv_clone" (
    echo [i] Installing Voice Cloning Sub-Engine...
    call scripts\setup_coqui_env.bat
)
cd ..

:: 4. Frontend Setup
echo.
echo [4/4] Setting up the User Interface (Frontend)...
cd frontend
echo [i] Installing UI dependencies (this may take a minute)...
call npm install --no-fund --no-audit
cd ..

echo.
echo =======================================================
echo                 INSTALLATION COMPLETE!
echo =======================================================
echo.
echo All requirements have been successfully installed.
echo.
echo Starting the App...
echo.
call start_all.bat
