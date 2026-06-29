@echo off
title Setup Piper TTS

echo =======================================
echo     Piper TTS Setup for Windows
echo =======================================
echo.

set MODEL_DIR=..\models\piper
if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"

echo [1/3] Downloading Piper Executable (AMD64)...
:: We will download the pre-compiled windows-amd64 binary for piper
set PIPER_URL=https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip
set ZIP_FILE=%MODEL_DIR%\piper.zip

powershell -Command "Invoke-WebRequest -Uri '%PIPER_URL%' -OutFile '%ZIP_FILE%'"

echo [2/3] Extracting Piper...
powershell -Command "Expand-Archive -Path '%ZIP_FILE%' -DestinationPath '%MODEL_DIR%' -Force"
:: XCOPY to move everything including subdirectories
if exist "%MODEL_DIR%\piper\piper.exe" (
    xcopy /E /Y "%MODEL_DIR%\piper\*" "%MODEL_DIR%\"
    rmdir /S /Q "%MODEL_DIR%\piper"
)
del "%ZIP_FILE%"

echo [3/3] Downloading Medium-Quality English Model (Lessac)...
set MODEL_URL=https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx
set JSON_URL=https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

powershell -Command "Invoke-WebRequest -Uri '%MODEL_URL%' -OutFile '%MODEL_DIR%\en_US-lessac-medium.onnx'"
powershell -Command "Invoke-WebRequest -Uri '%JSON_URL%' -OutFile '%MODEL_DIR%\en_US-lessac-medium.onnx.json'"

echo.
echo =======================================
echo Piper TTS Setup Complete!
echo You can now use Piper offline voices in VoxForge.
echo =======================================
