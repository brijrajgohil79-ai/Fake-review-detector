@echo off
setlocal
title Fake Review Trap - Authenticity Detector

echo ==============================================================
echo             🛡️ FAKE REVIEW TRAP - SERVER LAUNCHER
echo ==============================================================
echo.

:: Detect Python executable (.venv, D:\Python311, or system python)
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PY_EXE=%~dp0.venv\Scripts\python.exe"
) else if exist "D:\Python311\python.exe" (
    set "PY_EXE=D:\Python311\python.exe"
) else (
    set "PY_EXE=python"
)

echo [1/2] Verifying Python runtime...
"%PY_EXE%" --version
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python or ensure it is in your PATH.
    pause
    exit /b 1
)

echo.
echo [2/2] Launching Fake Review Trap server...
echo Server running at: http://127.0.0.1:5000
echo Opening web interface in your default browser...

:: Open browser after 1 second delay
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:5000"

:: Start Flask server
"%PY_EXE%" "%~dp0backend\app.py"

pause
