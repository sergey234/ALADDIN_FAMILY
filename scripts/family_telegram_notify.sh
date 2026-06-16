#!/usr/bin/env bash
# Send ops Telegram message (optional). Args: message text
set -euo pipefail
TEXT="${1:-}"
[[ -n "${TEXT}" ]] || exit 0
[[ "${FAMILY_REMEDIATE_NOTIFY:-}" == "1" ]] || exit 0
ENV_FILE="${ALADDIN_ENV:-/opt/aladdin-telegram-shop-bot/shared/.env}"
[[ -f "${ENV_FILE}" ]] || exit 0
python3 - "${ENV_FILE}" "${TEXT}" <<'PY'
import sys, urllib.parse, urllib.request
from pathlib import Path

env_path, text = sys.argv[1], sys.argv[2]
env = {}
for line in Path(env_path).read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, _, v = line.partition("=")
    env[k.strip()] = v.strip().strip('"').strip("'")
token = env.get("ALERT_TELEGRAM_BOT_TOKEN") or env.get("BOT_TOKEN")
chat = env.get("ALERT_TELEGRAM_CHAT_ID")
if not token or not chat:
    raise SystemExit(0)
body = urllib.parse.urlencode({
    "chat_id": chat,
    "text": text[:4000],
    "disable_web_page_preview": "true",
}).encode()
urllib.request.urlopen(
    urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=body,
        method="POST",
    ),
    timeout=15,
)
PY
