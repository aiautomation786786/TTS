@echo off
title VoxForge - Stop Services
echo.
echo [*] Stopping VoxForge services...
echo.

:: Kill Python (backend) processes
echo [1/2] Stopping Backend (Python/Uvicorn)...
taskkill /f /im python.exe /fi "WINDOWTITLE eq VoxForge Backend*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq VoxForge Backend*" >nul 2>&1
echo       Backend stopped.

:: Kill Node (frontend) processes
echo [2/2] Stopping Frontend (Node/Vite)...
taskkill /f /im node.exe /fi "WINDOWTITLE eq VoxForge Frontend*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq VoxForge Frontend*" >nul 2>&1
echo       Frontend stopped.

echo.
echo [OK] All VoxForge services stopped.
echo.
pause
