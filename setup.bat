@echo off
title VoxForge - Setup
color 0B

echo.
echo  ╔════════════════════════════════════════════╗
echo  ║     VoxForge - Initial Setup Script        ║
echo  ╚════════════════════════════════════════════╝
echo.

:: Check Python
echo [1/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed.
    echo Please install Python 3.10+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('python --version') do echo       Found: %%i
)

:: Check Node.js
echo [2/6] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed.
    echo Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('node --version') do echo       Found: Node.js %%i
)

:: Install Backend Dependencies
echo [3/6] Installing Backend Dependencies...
cd /d "%~dp0backend"
pip install -r requirements.txt
if errorlevel 1 (
    echo [WARNING] Some backend dependencies may have failed to install.
    echo Try running: pip install -r requirements.txt manually
)
echo       Backend dependencies installed.

:: Create data directories
echo [4/7] Creating data directories...
if not exist "data\db" mkdir "data\db"
if not exist "data\outputs" mkdir "data\outputs"
if not exist "data\uploads" mkdir "data\uploads"
if not exist "data\cloned_voices" mkdir "data\cloned_voices"
if not exist "data\previews" mkdir "data\previews"
if not exist "data\temp_chunks" mkdir "data\temp_chunks"
if not exist "data\outputs\long_form" mkdir "data\outputs\long_form"
echo       Data directories created.

:: Install Frontend Dependencies
echo [5/7] Installing Frontend Dependencies...
cd /d "%~dp0frontend"
call npm install
if errorlevel 1 (
    echo [WARNING] Some frontend dependencies may have failed to install.
    echo Try running: npm install manually in the frontend directory.
)
echo       Frontend dependencies installed.

:: Check FFmpeg
echo [6/7] Checking FFmpeg for Long Form Audio Merging...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FFmpeg is not installed or not in PATH.
    echo Long Form TTS Mode requires FFmpeg to merge audio chunks.
    echo Please install FFmpeg (e.g. winget install ffmpeg) and restart the console.
) else (
    echo       FFmpeg found. Long Form Mode is fully supported.
)

:: Check optional: Coqui TTS for voice cloning
echo [7/7] Checking optional dependencies...
python -c "import TTS" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [INFO] Coqui TTS is NOT installed (optional, for voice cloning).
    echo       To enable voice cloning, run:
    echo       pip install coqui-tts
    echo       Note: Requires NVIDIA GPU with 4+ GB VRAM for best performance.
) else (
    echo       Coqui TTS found (voice cloning available).
)

python -c "import torch; print(torch.cuda.is_available())" >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyTorch/CUDA not detected. Voice cloning will use CPU (slower).
) else (
    echo       GPU support available for voice cloning.
)

echo.
echo ══════════════════════════════════════════════════════
echo.
echo  Setup Complete!
echo.
echo  To start VoxForge, run: start.bat
echo.
echo  Or start manually:
echo    Backend:  cd backend ^& python run.py
echo    Frontend: cd frontend ^& npm run dev
echo.
echo  Default Accounts:
echo  ┌─────────────────────────────────────────────────┐
echo  │ Admin:  username=admin   password=admin123      │
echo  │ Demo:   username=demo    password=demo123       │
echo  └─────────────────────────────────────────────────┘
echo.
echo ══════════════════════════════════════════════════════
pause
