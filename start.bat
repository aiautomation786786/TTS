@echo off
title VoxForge - Premium TTS Platform
color 0B

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║                                                      ║
echo  ║   ██╗   ██╗ ██████╗ ██╗  ██╗███████╗ ██████╗ ██████╗ ██████╗ ███████╗  ║
echo  ║   ██║   ██║██╔═══██╗╚██╗██╔╝██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝  ║
echo  ║   ██║   ██║██║   ██║ ╚███╔╝ █████╗  ██║   ██║██████╔╝██║  ███╗█████╗    ║
echo  ║   ╚██╗ ██╔╝██║   ██║ ██╔██╗ ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝    ║
echo  ║    ╚████╔╝ ╚██████╔╝██╔╝ ██╗██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗  ║
echo  ║     ╚═══╝   ╚═════╝ ╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝  ║
echo  ║                                                      ║
echo  ║          Premium AI Text-to-Speech Platform           ║
echo  ║                                                      ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

echo [*] Starting VoxForge...
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)

:: Start Backend
echo [1/2] Starting Backend Server (FastAPI)...
cd /d "%~dp0backend"
start "VoxForge Backend" cmd /k "python run.py"
echo       Backend starting on http://localhost:8000
echo       API Docs: http://localhost:8000/docs
echo.

:: Wait for backend to initialize
timeout /t 3 /nobreak >nul

:: Start Frontend
echo [2/2] Starting Frontend Dev Server (Vite)...
cd /d "%~dp0frontend"
start "VoxForge Frontend" cmd /k "npm run dev"
echo       Frontend starting on http://localhost:5173
echo.

:: Wait for frontend to start
timeout /t 3 /nobreak >nul

echo ══════════════════════════════════════════════════════
echo.
echo  VoxForge is starting up!
echo.
echo  Frontend:  http://localhost:5173
echo  Backend:   http://localhost:8000
echo  API Docs:  http://localhost:8000/docs
echo.
echo  Default Accounts:
echo  ┌─────────────────────────────────────────────────┐
echo  │ Admin:  username=admin   password=admin123      │
echo  │ Demo:   username=demo    password=demo123       │
echo  └─────────────────────────────────────────────────┘
echo.
echo  Press any key to open in browser...
echo ══════════════════════════════════════════════════════

pause >nul
start http://localhost:5173
