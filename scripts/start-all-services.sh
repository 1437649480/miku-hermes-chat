#!/bin/bash
# Hermes Miku 全服务启动脚本 (WSL2) - 后台保活版
set -e

echo "========================================"
echo "  Starting Miku Services (Auto-Restart)"
echo "========================================"

HERMES_HOME="/mnt/d/桌面/opencil/mikuchat/hermes-agent"
export HERMES_HOME

# Kill old processes
echo "[1/4] Cleaning up old processes..."
pkill -f "uvicorn.*8000" 2>/dev/null || true
pkill -f "kimi-free-api" 2>/dev/null || true
pkill -f "node.*index.js" 2>/dev/null || true
pkill -f "gateway/run.py" 2>/dev/null || true
pkill -f "hermes gateway" 2>/dev/null || true
sleep 2

# Start deepseek-free-api
echo "[2/4] Starting deepseek-free-api (port 8000)..."
cd /home/yaya/deepseek-free-api
nohup bash -c 'while true; do uvicorn main:app --host 0.0.0.0 --port 8000; sleep 5; done' > /tmp/deepseek.log 2>&1 &
sleep 2

# Start kimi-free-api
echo "[3/4] Starting kimi-free-api (port 8002)..."
cd /home/yaya/kimi-free-api
nohup bash -c 'while true; do node index.js; sleep 5; done' > /tmp/kimi.log 2>&1 &
sleep 2

# Start Hermes gateway with auto-restart
echo "[4/4] Starting Hermes Gateway (auto-restart)..."
export PATH="$HOME/.local/bin:$PATH"
nohup bash -c '
  while true; do
    echo "[$(date)] Starting Hermes Gateway..."
    hermes gateway run --replace
    echo "[$(date)] Gateway exited, restarting in 5s..."
    sleep 5
  done
' > /tmp/hermes-gateway.log 2>&1 &
sleep 3

echo ""
echo "========================================"
echo "  All services started with auto-restart!"
echo "  deepseek: http://127.0.0.1:8000"
echo "  kimi:     http://127.0.0.1:8002"
echo "  gateway:  hermes gateway run (auto-restart)"
echo "========================================"
echo ""
echo "  Voice mode: /voice tts (default: all)"
echo "========================================"