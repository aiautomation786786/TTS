@echo off
echo ==============================================================
echo Starting Coqui XTTS Voice Cloning Worker
echo ==============================================================

cd %~dp0\..
set "WORKER_DIR=voice_clone_worker"
set "COQUI_TOS_AGREED=1"

if not exist "%WORKER_DIR%\venv_clone\Scripts\python.exe" (
    echo ERROR: venv_clone python not found!
    echo Please run setup_coqui_env.bat first.
    pause
    exit /b 1
)

cd "%WORKER_DIR%"

echo Starting worker on port 8001...
"venv_clone\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8001
pause
