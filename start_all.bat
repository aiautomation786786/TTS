@echo off
title AI Platform
echo ==============================================================
echo [1/3] Checking for application updates from Git...
echo ==============================================================
git fetch origin >nul 2>&1
git status -uno | findstr "behind" >nul
if %ERRORLEVEL% EQU 0 (
    echo [i] Updates found! Downloading the latest version...
    git pull origin main
    echo [OK] Update applied successfully!
) else (
    echo [OK] Application is already up to date.
)
echo.
echo ==============================================================
echo Cleaning up previous application sessions...
echo ==============================================================
powershell -Command "$ports = @(8000, 8001, 5173); foreach ($p in $ports) { $procs = Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; foreach ($proc in $procs) { if ($proc) { Stop-Process -Id $proc -Force -ErrorAction SilentlyContinue } } }"
echo Cleanup complete.
echo.
title AI Platform
echo Starting AI Platform...
echo.

npx concurrently --kill-others -n "BACKEND,FRONTEND,WORKER" -c "bgBlue.bold,bgMagenta.bold,bgGreen.bold" "cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000" "cd frontend && npm run dev" "cd backend\scripts && run_coqui_worker.bat"
