#!/usr/bin/env bash
# Smoke @AladdinchatAI_bot proxy path (tg-hermes-wire) на VPS.
# Usage: ./telegram_support_bot_smoke.sh [base_url]
set -euo pipefail

BASE="${1:-http://127.0.0.1:8002}"
SSH_HOST="${SSH_HOST:-root@149.154.65.180}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/aladdin_server}"

ssh -o IdentitiesOnly=yes -o BatchMode=yes -i "$SSH_KEY" "$SSH_HOST" bash -s -- "$BASE" <<'REMOTE'
set -euo pipefail
BASE="$1"
cd /opt/aladdin-backend
set -a
# shellcheck disable=SC1091
source .env
set +a

[[ -n "${TG_BOT_INTERNAL_SECRET:-}" ]] || { echo "FAIL: TG_BOT_INTERNAL_SECRET missing"; exit 1; }

TG_ID="999000$(date +%s | tail -c 6)"
ALADDIN_UID="tg-smoke-$(date +%s)"

python3 - <<PY
import os, time, sqlite3
db = os.getenv("TELEGRAM_LINK_DB", "/opt/aladdin-backend/data/telegram_links.db")
os.makedirs(os.path.dirname(db), exist_ok=True)
with sqlite3.connect(db) as c:
    c.execute("""CREATE TABLE IF NOT EXISTS links (
        telegram_user_id INTEGER PRIMARY KEY,
        aladdin_user_id TEXT NOT NULL,
        telegram_username TEXT,
        ai_opt_in INTEGER NOT NULL DEFAULT 0,
        linked_at REAL NOT NULL)""")
    c.execute("DELETE FROM links WHERE telegram_user_id = ?", (${TG_ID},))
    c.execute(
        "INSERT INTO links VALUES (?,?,?,?,?)",
        (${TG_ID}, "${ALADDIN_UID}", "smoke_bot", 1, time.time()),
    )
    c.commit()
print("OK: temp link", ${TG_ID})
PY

BODY=$(curl -sS -m 90 -X POST "${BASE}/api/telegram/bot/chat" \
  -H "Content-Type: application/json" \
  -H "X-TG-Bot-Secret: ${TG_BOT_INTERNAL_SECRET}" \
  -d "{\"telegram_user_id\":${TG_ID},\"message\":\"Какие тарифы ALADDIN?\"}")

echo "$BODY" | python3 -c "
import json, sys
d = json.load(sys.stdin)
text = (d.get('response') or '')[:200]
tools = d.get('tools_used', [])
forbidden = ('187 функций', '1074 функций', 'Я отвечаю по базе знаний')
for f in forbidden:
    if f in text:
        raise SystemExit(f'FAIL: SFM template: {f}')
if not text.strip():
    raise SystemExit('FAIL: empty response')
print('OK: response:', text[:120], '...')
print('OK: tools_used:', tools)
"

python3 - <<PY
import os, sqlite3
db = os.getenv("TELEGRAM_LINK_DB", "/opt/aladdin-backend/data/telegram_links.db")
with sqlite3.connect(db) as c:
    c.execute("DELETE FROM links WHERE telegram_user_id = ?", (${TG_ID},))
    c.commit()
PY

echo "=== TELEGRAM SUPPORT BOT SMOKE PASS ==="
REMOTE
