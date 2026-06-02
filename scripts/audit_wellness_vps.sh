#!/usr/bin/env bash
# Read-only аудит wellness на VPS: пути, флаги, OpenAPI, smoke.
# Usage: ./scripts/audit_wellness_vps.sh [ssh_key]
set -euo pipefail

HOST="${HOST:-149.154.65.180}"
SSH_KEY="${1:-${SSH_KEY_PATH:-$HOME/.ssh/aladdin_server}}"
REMOTE="/opt/aladdin-backend"
SSH_OPTS=(-o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15)
[[ -n "${SSH_KEY}" ]] && SSH_OPTS+=(-i "${SSH_KEY}")

ssh_r() { ssh "${SSH_OPTS[@]}" "root@${HOST}" "$@"; }

echo ">>> Audit wellness @ root@${HOST}:${REMOTE}"
ssh_r "bash -s" <<REMOTE
set -e
ROOT=${REMOTE}
echo "=== Must NOT be telegram bot tree ==="
test ! -f "\$ROOT/telegram_stars_shop_bot/bot.py"
echo "OK: not telegram-shop-bot root"

echo "=== Required files under \${ROOT} ==="
for f in \\
  main.py \\
  security/api/routers/wellness_router.py \\
  security/services/ai_platform/feature_flags.py \\
  security/services/ai_platform/wellness_four_pillars.py \\
  security/services/ai_platform/wellness_escalation.py \\
  security/services/ai_platform/wellness_referral.py \\
  security/services/ai_platform/wellness_prompt_builder.py \\
  security/services/ai_platform/companion_store.py \\
  scripts/vps_smoke_wellness.py; do
  test -f "\$ROOT/\$f" && echo "OK \$f" || { echo "MISSING \$f"; exit 1; }
done

echo "=== Knowledge pack ==="
test -f "\$ROOT/security/services/ai_platform/wellness_knowledge/cognitive/v1/pack.yaml"

echo "=== .env ==="
grep '^FEATURE_WELLNESS_' "\$ROOT/.env" || exit 1

echo "=== main.py router ==="
grep -q wellness_router "\$ROOT/main.py"

echo "=== Service ==="
systemctl is-active aladdin-backend.service

echo "=== Smoke (localhost) ==="
cd "\$ROOT" && PYTHONPATH="\$ROOT" ./venv/bin/python3 scripts/vps_smoke_wellness.py
REMOTE

echo ">>> External (Mac): ./scripts/verify_wellness_prod.sh https://aladdin-ai.ru"
