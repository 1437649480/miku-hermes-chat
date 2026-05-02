#!/bin/bash
# Hermes Miku 全服务启动脚本 (WSL2)
set -e

echo "========================================"
echo "  Starting Miku Services"
echo "========================================"

HERMES_HOME="/mnt/d/桌面/opencil/hermes-agent/bit by bit"
export HERMES_HOME

# Kill old processes
echo "[1/4] Cleaning up old processes..."
pkill -f "uvicorn.*8000" 2>/dev/null || true
pkill -f "kimi-free-api" 2>/dev/null || true
pkill -f "node.*index.js" 2>/dev/null || true
pkill -f "gateway/run.py" 2>/dev/null || true
sleep 2

# Start deepseek-free-api
echo "[2/4] Starting deepseek-free-api (port 8000)..."
cd /home/yaya/deepseek-free-api
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/deepseek.log 2>&1 &
sleep 2

# Start kimi-free-api
echo "[3/4] Starting kimi-free-api (port 8002)..."
cd /home/yaya/kimi-free-api-new
nohup node index.js > /tmp/kimi.log 2>&1 &
sleep 2

# Start Hermes gateway
echo "[4/4] Starting Hermes Gateway (port 8765)..."
cd /home/yaya/hermes-agent
nohup python gateway/run.py > /tmp/hermes-gateway.log 2>&1 &
sleep 3

echo ""
echo "========================================"
echo "  All services started!"
echo "  deepseek: http://127.0.0.1:8000"
echo "  kimi:     http://127.0.0.1:8002"
echo "  gateway:  http://127.0.0.1:8765"
echo "  image gen: cf plugin (pollinations.ai)"
echo "========================================"
