@echo off
color 0B
echo ==============================================================
echo Installing Microsoft C++ Build Tools (Required for Voice Cloning)
echo ==============================================================
echo.

:: Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [SUCCESS] Administrator privileges confirmed.
) else (
    color 0C
    echo [ERROR] You must run this script as an Administrator!
    echo Please right-click "Install_Compiler_Run_As_Admin.bat" and select "Run as administrator".
    echo.
    pause
    exit /b 1
)

echo Step 1/2: Downloading Microsoft Visual Studio Bootstrapper...
powershell -Command "Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vs_buildtools.exe' -OutFile '%TEMP%\vs_buildtools.exe'"

echo.
echo Step 2/2: Starting Installation...
echo A window will pop up showing the progress. Please wait for it to finish (usually 5-15 minutes).
echo.
"%TEMP%\vs_buildtools.exe" --passive --wait --norestart --nocache --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended

echo.
echo ==============================================================
echo [SUCCESS] Installation Completed!
echo You can now safely run: .\backend\scripts\setup_coqui_env.bat
echo ==============================================================
pause
