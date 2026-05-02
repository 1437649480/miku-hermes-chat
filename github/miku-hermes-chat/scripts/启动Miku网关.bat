@echo off
chcp 65001 >nul
echo ========================================
echo   重启 Miku Hermes 网关
echo ========================================
echo.
echo [1/2] 正在关闭旧网关...
wsl -d Ubuntu-24.04 bash -c "pkill -f 'hermes_cli.main gateway' 2>/dev/null; sleep 2; echo '已关闭'"
echo.
echo [2/2] 启动新网关 (含生图插件)...
start "Miku Gateway" wsl -d Ubuntu-24.04 bash /home/yaya/start-gw.sh
echo.
echo 网关正在新窗口中启动...
echo 等待约 20-30 秒后即可使用。
echo.
echo ========================================
echo   使用方法：
echo   微信发 "帮我画一个可爱的初音未来表情包"
echo   微信发 "生成一张猫猫表情包 meme风格"
echo ========================================
pause
