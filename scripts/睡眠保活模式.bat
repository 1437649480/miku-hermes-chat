@echo off
chcp 65001 >nul 2>&1
echo ==========================================
echo   Hermes - Keep Awake Mode
echo   Screen will sleep, services stay alive
echo ==========================================
echo.
echo Press Ctrl+C to exit keep-awake mode
echo.
python "%~dp0keep-awake.py"
pause