#!/usr/bin/env bash
# Проверка split: Shop → AiMonkeyStars, ALADDIN gateway → AladdinChatAI_bot
set -euo pipefail

fail() { echo "FAIL: $*" >&2; exit 1; }
ok() { echo "OK: $*"; }

python3 - <<'PY'
import re, sys, urllib.request, json
from pathlib import Path

def load(p):
    env = {}
    if not p.is_file():
        return env
    for line in p.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

def me(token):
    r = urllib.request.urlopen(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
    return json.loads(r.read()).get("result", {}).get("username", "")

shop = load(Path("/opt/aladdin-telegram-shop-bot/shared/.env"))
ald = load(Path("/etc/aladdin-backend/feedback-telegram.env"))
am = Path("/etc/prometheus/alertmanager.yml").read_text()

st = shop.get("ALERT_TELEGRAM_BOT_TOKEN") or shop.get("BOT_TOKEN", "")
at = ald.get("ALADDIN_FEEDBACK_TELEGRAM_BOT_TOKEN", "")
if not st or not at:
    raise SystemExit("FAIL: missing shop or aladdin token")

su, au = me(st), me(at)
if su != "AiMonkeyStars_bot":
    raise SystemExit(f"FAIL: shop bot @{su}")
if au.lower() != "aladdinchatai_bot":
    raise SystemExit(f"FAIL: aladdin bot @{au}")

if st not in am or at not in am:
    raise SystemExit("FAIL: alertmanager.yml missing one of the tokens")
if "telegram-shop" not in am or "telegram-aladdin" not in am:
    raise SystemExit("FAIL: split receivers missing")

print(f"OK: shop receiver -> @{su}")
print(f"OK: aladdin receiver -> @{au}")
PY

systemctl is-active prometheus-alertmanager.service >/dev/null || fail "alertmanager down"
systemctl is-active ops-watchdog.timer >/dev/null || fail "ops-watchdog.timer down"

systemctl start ops-watchdog.service
ok "ops_watchdog triggered (shop heartbeat via ALERT_TELEGRAM_*)"

echo "Prometheus routes:"
grep -A2 "receiver:" /etc/prometheus/alertmanager.yml | head -20
