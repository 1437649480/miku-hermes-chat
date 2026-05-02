@echo off
chcp 65001 >nul
set "LOGDIR=%~dp0"
set "LOGFILE=%LOGDIR%kimi-token-refresh.log"
echo [%date% %time%] Starting Kimi token refresh... >> "%LOGFILE%"
wsl -d Ubuntu-24.04 -e python3 /mnt/d/桌面/opencil/refresh-kimi-token.py >> "%LOGFILE%" 2>&1
echo [%date% %time%] Exit code: %ERRORLEVEL% >> "%LOGFILE%"
echo. >> "%LOGFILE%"
