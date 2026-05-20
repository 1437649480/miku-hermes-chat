@echo off
chcp 65001 >nul 2>&1
title Miku Sticker Manager

echo ===========================================
echo   Hatsune Miku - Sticker Manager
echo   http://localhost:5100
echo ===========================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.8+
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing Flask...
    pip install flask
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install Flask
        pause
        exit /b 1
    )
)

echo [OK] Starting sticker manager...
echo [OK] Opening browser in 2 seconds...
start "" http://localhost:5100
python "%~dp0sticker_manager.py"
pause