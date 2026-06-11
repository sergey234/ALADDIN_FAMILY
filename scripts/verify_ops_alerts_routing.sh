#!/usr/bin/env bash
# Проверка: алерты идут через @AiMonkeyStars_bot (BOT_TOKEN = ALERT_TELEGRAM).
set -euo pipefail

ENV_FILE="${ENV_FILE:-/opt/aladdin-telegram-shop-bot/shared/.env}"
AM_FILE="${AM_FILE:-/etc/prometheus/alertmanager.yml}"

fail() { echo "FAIL: $*" >&2; exit 1; }
ok() { echo "OK: $*"; }

python3 - "$ENV_FILE" "$AM_FILE" <<'PY'
import re, sys, urllib.request, json
from pathlib import Path

env_path, am_path = Path(sys.argv[1]), Path(sys.argv[2])
env = {}
for line in env_path.read_text().splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

shop = env.get("BOT_TOKEN", "")
alert = env.get("ALERT_TELEGRAM_BOT_TOKEN", "")
chat = env.get("ALERT_TELEGRAM_CHAT_ID", "")
if not shop or not alert or not chat:
    raise SystemExit("FAIL: BOT_TOKEN / ALERT_TELEGRAM_* missing")
if shop != alert:
    raise SystemExit("FAIL: ALERT_TELEGRAM_BOT_TOKEN != BOT_TOKEN")

am = am_path.read_text()
if shop not in am:
    raise SystemExit("FAIL: BOT_TOKEN not in alertmanager.yml")
if f"chat_id: {chat}" not in am.replace("'", ""):
    raise SystemExit(f"FAIL: chat_id {chat} not in alertmanager.yml")

r = urllib.request.urlopen(f"https://api.telegram.org/bot{shop}/getMe", timeout=10)
u = json.loads(r.read()).get("result", {}).get("username")
if u != "AiMonkeyStars_bot":
    raise SystemExit(f"FAIL: expected AiMonkeyStars_bot, got @{u}")
print(f"OK: alerts route to @{u} chat_id={chat}")
PY

systemctl is-active prometheus-alertmanager.service >/dev/null || fail "prometheus-alertmanager not active"
systemctl is-active prometheus.service >/dev/null || fail "prometheus not active"
systemctl is-active ops-watchdog.timer >/dev/null || fail "ops-watchdog.timer not active"

ok "prometheus + alertmanager + ops-watchdog.timer active"

echo "=== trigger ops_watchdog once (systemd + shared/.env) ==="
systemctl start ops-watchdog.service
ok "ops_watchdog.service finished (check Telegram: [INFO] OK: ops heartbeat from @AiMonkeyStars_bot)"
