@echo off
title Setup Coqui XTTS

echo =======================================
echo     Coqui XTTS Setup for Windows
echo =======================================
echo.

echo WARNING: Coqui XTTS has heavy dependencies and may not install natively on Python 3.12+.
echo The system detected Python:
python --version
echo.
echo WARNING: If you do not have a dedicated NVIDIA GPU and CUDA installed, Voice Cloning will run on CPU and be EXTREMELY SLOW.
echo.

set /p CONTINUE="Do you want to attempt installation anyway? (Y/N): "
if /I "%CONTINUE%" neq "Y" (
    echo Installation aborted.
    exit /b 0
)

echo.
echo [1/2] Installing PyTorch (CPU fallback)...
:: We install the CPU version by default to maximize compatibility if CUDA is absent.
:: Users with CUDA should run the specific PyTorch index URL manually.
pip install torch torchvision torchaudio

echo.
echo [2/2] Installing Coqui TTS...
pip install TTS

echo.
echo =======================================
echo Coqui TTS Installation Attempt Complete!
echo Please check the Admin Engine Status page to see if it is operational.
echo If it failed, please refer to the README for advanced Python environment setup.
echo =======================================
