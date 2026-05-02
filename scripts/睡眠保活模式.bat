@echo off
chcp 65001 >nul
echo ==========================================
echo   Hermes 睡眠保活模式
echo   屏幕会关闭，但服务持续运行
echo ==========================================
echo.
echo 按 Ctrl+C 可退出保活模式，恢复系统正常睡眠
echo.
python "%~dp0keep-awake.py"
pause
