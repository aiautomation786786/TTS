@echo off
set "PY311=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"

if not exist "%PY311%" (
  echo Python 3.11 not found at: %PY311%
  exit /b 1
)

if /I "%~1"=="-0p" (
  echo -3.11-64        %PY311%
  exit /b 0
)

if /I "%~1"=="-3.11" goto skipver
if /I "%~1"=="-3.11-64" goto skipver
if /I "%~1"=="-3.10" goto skipver
if /I "%~1"=="-3.10-64" goto skipver
goto runall

:skipver
shift
set ARGS=
:build
if "%~1"=="" goto runbuilt
set ARGS=%ARGS% "%~1"
shift
goto build

:runbuilt
"%PY311%" %ARGS%
exit /b %ERRORLEVEL%

:runall
"%PY311%" %*
exit /b %ERRORLEVEL%
