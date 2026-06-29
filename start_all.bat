@echo off
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
