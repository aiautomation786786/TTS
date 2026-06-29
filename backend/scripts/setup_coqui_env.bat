@echo off
setlocal enabledelayedexpansion
echo ==============================================================
echo Setting up Coqui XTTS Voice Cloning Worker
echo ==============================================================

cd %~dp0\..
set "WORKER_DIR=voice_clone_worker"

if not exist "%WORKER_DIR%" mkdir "%WORKER_DIR%"
cd "%WORKER_DIR%"

set "DETECTED_PY="

echo Checking for Python 3.10 or 3.11...

:: Method A: py -0p
echo Trying Python launcher (py -0p)...
for /f "tokens=1,2*" %%A in ('py -0p 2^>nul') do (
    echo %%A | findstr "3.11 3.10" >nul
    if not errorlevel 1 (
        if exist "%%B" (
            set "DETECTED_PY=%%B"
            goto :found
        )
    )
)

:: Method B: python --version
echo Trying normal python command...
for /f "tokens=2" %%v in ('python --version 2^>nul') do (
    echo %%v | findstr "^3.11 ^3.10" >nul
    if not errorlevel 1 (
        set "DETECTED_PY=python"
        goto :found
    )
)

:: Method C: Common local paths
echo Trying common local installation paths...
set "LOCAL_PY311=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
set "LOCAL_PY310=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"

if exist "%LOCAL_PY311%" (
    set "DETECTED_PY=%LOCAL_PY311%"
    goto :found
)
if exist "%LOCAL_PY310%" (
    set "DETECTED_PY=%LOCAL_PY310%"
    goto :found
)

echo ERROR: Python 3.10 or 3.11 could not be found via any method.
echo Please install Python 3.10 or 3.11 from python.org
pause
exit /b 1

:found
echo.
echo Detected Python candidates:
if not "%DETECTED_PY%"=="python" (
    echo * Python 3.1x found at %DETECTED_PY%
) else (
    echo * Python 3.1x found in system PATH
)
echo.
echo Using Python executable:
echo %DETECTED_PY%
echo.

echo Creating isolated venv_clone...
if not exist "venv_clone" "%DETECTED_PY%" -m venv venv_clone

echo Upgrading pip...
"venv_clone\Scripts\python.exe" -m pip install --upgrade pip

echo Installing PyTorch CPU (CUDA fallback)...
"venv_clone\Scripts\python.exe" -m pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cpu

echo Installing TTS/Coqui dependencies...
"venv_clone\Scripts\python.exe" -m pip install fastapi uvicorn python-multipart pydantic
"venv_clone\Scripts\python.exe" -m pip install TTS
echo Downgrading transformers and numpy to fix Coqui compatibility...
"venv_clone\Scripts\python.exe" -m pip install transformers==4.36.2 numpy==1.26.4 torchcodec

echo Creating required folders...
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs
if not exist "models" mkdir models

echo Testing import TTS...
"venv_clone\Scripts\python.exe" -c "import TTS; print('TTS package successfully installed.')"
if %errorlevel% neq 0 (
    echo ERROR: TTS package failed to import.
    pause
    exit /b 1
)

echo Setup Complete!
echo Run 'run_coqui_worker.bat' to start the worker.
pause
