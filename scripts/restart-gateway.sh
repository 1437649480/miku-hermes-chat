#!/bin/bash
GATEWAY_PATTERN='hermes_cli.main gateway run'

echo "[gw] Stopping existing gateway..."
pkill -f "$GATEWAY_PATTERN" 2>/dev/null
sleep 2
echo "Old gateway stopped"

export HERMES_HOME='/mnt/d/桌面/opencil/hermes-agent/bit by bit'
cd /home/yaya/hermes-agent

echo "[gw] Starting Hermes Gateway..."
nohup python3 -m hermes_cli.main gateway run > /tmp/hermes-gateway.log 2>&1 &
echo "Gateway PID: $!"
sleep 8
echo "=== Last 30 lines of log ==="
tail -30 /tmp/hermes-gateway.log
