@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo   Miku Hermes Gateway - Restart
echo ========================================
echo.
echo [1/2] Stopping old gateway...
wsl -d Ubuntu-24.04 bash -c "pkill -f 'hermes_cli.main gateway' 2>/dev/null; sleep 2; echo done"
echo.
echo [2/2] Starting new gateway...
start "HermesGW" wsl -d Ubuntu-24.04 bash /home/yaya/start-gw.sh
echo.
echo Gateway starting in new window...
echo Wait 20-30 seconds, then ready.
echo.
echo ========================================
echo   Usage: send "miku" in WeChat to start
echo ========================================
pause