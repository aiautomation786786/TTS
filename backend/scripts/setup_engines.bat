@echo off
title VoxForge Engine Setup

echo =======================================
echo     VoxForge Complete Engine Setup
echo =======================================
echo.

echo [1/3] Checking Edge-TTS (Primary Engine)
python -c "import edge_tts" 2>nul
if errorlevel 1 (
    echo Installing Edge-TTS...
    pip install edge-tts
) else (
    echo Edge-TTS is already installed.
)
echo.

echo [2/3] Setting up Piper TTS (Local Offline Engine)
call setup_piper.bat
echo.

echo [3/3] Setting up Coqui XTTS (Voice Cloning)
echo Coqui XTTS is optional and experimental on some Windows machines.
echo Run setup_coqui.bat manually if you wish to attempt installation.
echo.

echo =======================================
echo Engine setup complete!
echo Please run validate_engines.py to verify operational status.
echo =======================================
