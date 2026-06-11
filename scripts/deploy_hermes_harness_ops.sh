#!/usr/bin/env bash
# Ops-скрипты Hermes harness + logrotate + cron на VPS.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SSH_HOST="${SSH_HOST:-root@149.154.65.180}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/aladdin_server}"
REMOTE_SCRIPTS="/opt/aladdin-backend/scripts"
REMOTE_ROOT="/opt/aladdin-backend"

RSYNC_SSH="ssh -o IdentitiesOnly=yes -o BatchMode=yes -i ${SSH_KEY}"

OPS_SCRIPTS=(
  hermes_deploy_guardrails.sh
  hermes_harness_smoke_api.sh
  hermes_openrouter_key_check.sh
  hermes_openrouter_key_update.sh
  companion_llm_cost_alert.sh
  companion_llm_metrics_report.py
  companion_llm_latency_baseline.sh
  telegram_support_bot_smoke.sh
  deploy_hermes_kb.sh
)

for s in "${OPS_SCRIPTS[@]}"; do
  rsync -az -e "$RSYNC_SSH" "${ROOT}/scripts/${s}" "${SSH_HOST}:${REMOTE_SCRIPTS}/"
done

rsync -az -e "$RSYNC_SSH" \
  "${ROOT}/scripts/logrotate-companion-llm.example" \
  "${SSH_HOST}:/etc/logrotate.d/companion-llm"

ssh -o IdentitiesOnly=yes -o BatchMode=yes -i "$SSH_KEY" "$SSH_HOST" bash -s <<'REMOTE'
set -euo pipefail
chmod +x /opt/aladdin-backend/scripts/hermes_*.sh
chmod +x /opt/aladdin-backend/scripts/companion_llm_cost_alert.sh
chmod +x /opt/aladdin-backend/scripts/deploy_hermes_kb.sh
chmod +x /opt/aladdin-backend/scripts/companion_llm_metrics_report.py

mkdir -p /var/log/aladdin-backend
touch /var/log/aladdin-backend/companion_llm.log
chown root:root /var/log/aladdin-backend/companion_llm.log

CRON_MARKER="# aladdin-companion-llm-ops"
CRON_FILE=/etc/cron.d/aladdin-companion-llm
if ! grep -q "$CRON_MARKER" "$CRON_FILE" 2>/dev/null; then
  cat > "$CRON_FILE" <<'CRON'
# aladdin-companion-llm-ops
15 * * * * root /opt/aladdin-backend/scripts/companion_llm_cost_alert.sh >> /var/log/aladdin-backend/companion_llm_alert.log 2>&1
0 9 * * 1 root /opt/aladdin-backend/venv/bin/python3 /opt/aladdin-backend/scripts/companion_llm_metrics_report.py --days 7 --out /var/log/aladdin-backend/companion_llm_weekly.csv >> /var/log/aladdin-backend/companion_llm_report.log 2>&1
CRON
  chmod 644 "$CRON_FILE"
  echo "cron installed: $CRON_FILE"
else
  echo "cron already present"
fi

/opt/aladdin-backend/scripts/hermes_deploy_guardrails.sh
REMOTE

echo "Harness ops deployed."
