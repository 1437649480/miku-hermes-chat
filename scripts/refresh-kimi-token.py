import requests
import json
import base64
import yaml
import os
import sys
from datetime import datetime

HERMES_CONFIG = "/home/yaya/.hermes/config.yaml"
REFRESH_URL = "https://kimi.moonshot.cn/api/auth/token/refresh"
REFRESH_THRESHOLD_DAYS = 30

AUX_KEYS = [
    "vision", "compression", "web_extract", "title_generation",
    "approval", "mcp", "session_search", "skills_hub"
]


def decode_jwt(token):
    payload = token.split(".")[1]
    payload += "=" * (4 - len(payload) % 4)
    return json.loads(base64.urlsafe_b64decode(payload).decode())


def get_current_token(config):
    for key in AUX_KEYS:
        tk = config.get("auxiliary", {}).get(key, {}).get("api_key")
        if tk:
            return tk
    return None


def refresh_token(old_token):
    resp = requests.get(
        REFRESH_URL,
        headers={"Authorization": f"Bearer {old_token}"},
        timeout=15,
    )
    if resp.status_code != 200:
        print(f"[FAIL] HTTP {resp.status_code}: {resp.text[:200]}")
        return None
    data = resp.json()
    new_token = data.get("refresh_token")
    if not new_token:
        print(f"[FAIL] No refresh_token in response: {json.dumps(data)[:200]}")
        return None
    return new_token


def update_config(new_token):
    with open(HERMES_CONFIG, "r") as f:
        config = yaml.safe_load(f)

    for key in AUX_KEYS:
        if key in config.get("auxiliary", {}):
            config["auxiliary"][key]["api_key"] = new_token

    with open(HERMES_CONFIG, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print(f"[OK] Config updated: {HERMES_CONFIG}")


def restart_gateway():
    os.system("pkill -f 'hermes_cli.main gateway run' 2>/dev/null")
    os.system("sleep 2")
    os.system("setsid -f python3 -m hermes_cli.main gateway run > /tmp/hermes-gw.log 2>&1")
    print("[OK] Hermes gateway restarted")


def main():
    force = "--force" in sys.argv
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking Kimi token...")

    with open(HERMES_CONFIG, "r") as f:
        config = yaml.safe_load(f)

    old_token = get_current_token(config)
    if not old_token:
        print("[FAIL] No token found in config")
        sys.exit(1)

    try:
        data = decode_jwt(old_token)
        exp_ts = data["exp"]
        now_ts = int(datetime.now().timestamp())
        days_left = (exp_ts - now_ts) / 86400
        print(f"[INFO] Token expires in {days_left:.1f} days")
    except Exception as e:
        print(f"[WARN] Cannot decode old token: {e}")
        days_left = 0

    if not force and days_left > REFRESH_THRESHOLD_DAYS:
        print(f"[SKIP] Token still valid ({days_left:.1f}d > {REFRESH_THRESHOLD_DAYS}d threshold), skipping refresh")
        return

    new_token = refresh_token(old_token)
    if not new_token:
        print("[FAIL] Token refresh failed")
        sys.exit(1)

    if new_token == old_token:
        print("[INFO] Token unchanged, no update needed")
        return

    try:
        new_data = decode_jwt(new_token)
        exp_ts = new_data["exp"]
        now_ts = int(datetime.now().timestamp())
        days_left = (exp_ts - now_ts) / 86400
        print(f"[NEW]  Token expires in {days_left:.1f} days")
    except Exception:
        print(f"[NEW]  Raw token: {new_token[:50]}...")

    update_config(new_token)
    restart_gateway()

    print("[DONE] Token refresh complete!")


if __name__ == "__main__":
    main()
