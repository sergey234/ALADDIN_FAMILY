#!/usr/bin/env bash
# Family backend deploy — auth_router + family routers + prod smoke gate (blocking).
#
# Usage:
#   chmod +x scripts/deploy_family_backend.sh
#   ./scripts/deploy_family_backend.sh [ssh_user] [host] [ssh_key_path]
#
# Example:
#   ./scripts/deploy_family_backend.sh root 149.154.65.180 ~/.ssh/aladdin_server

set -euo pipefail

SSH_USER="${1:-root}"
HOST="${2:-149.154.65.180}"
SSH_KEY="${3:-${SSH_KEY_PATH:-}}"
REMOTE_ROOT="/opt/aladdin-backend"
BACKEND_SERVICE="aladdin-backend.service"
TS="$(date +%Y%m%d_%H%M%S)"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SSH_OPTS=(-o BatchMode=yes -o StrictHostKeyChecking=no)
SCP_OPTS=(-o BatchMode=yes -o StrictHostKeyChecking=no)
if [[ -n "${SSH_KEY}" ]]; then
  SSH_OPTS+=(-i "${SSH_KEY}")
  SCP_OPTS+=(-i "${SSH_KEY}")
fi

ssh_r() { ssh "${SSH_OPTS[@]}" "${SSH_USER}@${HOST}" "$@"; }
scp_f() { scp "${SCP_OPTS[@]}" "$1" "${SSH_USER}@${HOST}:$2"; }

echo ">>> Family backend deploy → ${SSH_USER}@${HOST}:${REMOTE_ROOT}"

cd "${LOCAL_ROOT}"
echo ">>> Local static gates"
bash scripts/verify_family_static_gates.sh

python3 -m py_compile \
  app/routers/auth_router.py \
  app/routers/family.py \
  docs/server/test_family_prod_smoke.py \
  scripts/family_ops_alerts.py \
  scripts/family_auth_static_guard_smoke.py

BACKUP_TAG="${TS}"
ssh_r "mkdir -p '${REMOTE_ROOT}/.deploy_backups/family_${BACKUP_TAG}/app/routers' '${REMOTE_ROOT}/.deploy_backups/family_${BACKUP_TAG}/docs/server' '${REMOTE_ROOT}/.deploy_backups/family_${BACKUP_TAG}/scripts'"
for rel in \
  app/routers/auth_router.py \
  app/routers/family.py \
  docs/server/test_family_prod_smoke.py \
  scripts/family_ops_alerts.py \
  scripts/family_auth_static_guard_smoke.py; do
  ssh_r "cp '${REMOTE_ROOT}/${rel}' '${REMOTE_ROOT}/.deploy_backups/family_${BACKUP_TAG}/${rel}' 2>/dev/null || true"
done

scp_f "${LOCAL_ROOT}/app/routers/auth_router.py" "${REMOTE_ROOT}/app/routers/auth_router.py"
scp_f "${LOCAL_ROOT}/app/routers/family.py" "${REMOTE_ROOT}/app/routers/family.py"
scp_f "${LOCAL_ROOT}/docs/server/test_family_prod_smoke.py" "${REMOTE_ROOT}/docs/server/test_family_prod_smoke.py"
scp_f "${LOCAL_ROOT}/scripts/family_ops_alerts.py" "${REMOTE_ROOT}/scripts/family_ops_alerts.py"
scp_f "${LOCAL_ROOT}/scripts/family_auth_static_guard_smoke.py" "${REMOTE_ROOT}/scripts/family_auth_static_guard_smoke.py"
scp_f "${LOCAL_ROOT}/scripts/family_auto_remediate.sh" "${REMOTE_ROOT}/scripts/family_auto_remediate.sh"
scp_f "${LOCAL_ROOT}/scripts/family_smoke_with_remediate.sh" "${REMOTE_ROOT}/scripts/family_smoke_with_remediate.sh"
scp_f "${LOCAL_ROOT}/scripts/family_telegram_notify.sh" "${REMOTE_ROOT}/scripts/family_telegram_notify.sh"
scp_f "${LOCAL_ROOT}/docs/server/aladdin-family-prod-smoke.service" "/etc/systemd/system/aladdin-family-prod-smoke.service"
scp_f "${LOCAL_ROOT}/docs/server/aladdin-family-prod-smoke.timer" "/etc/systemd/system/aladdin-family-prod-smoke.timer"

ssh_r bash -s <<EOF
set -euo pipefail
cd "${REMOTE_ROOT}"
mkdir -p /var/lib/aladdin
chmod +x scripts/family_auto_remediate.sh scripts/family_smoke_with_remediate.sh scripts/family_telegram_notify.sh
./venv/bin/python3 -m py_compile app/routers/auth_router.py app/routers/family.py docs/server/test_family_prod_smoke.py scripts/family_ops_alerts.py scripts/family_auth_static_guard_smoke.py
systemctl restart "${BACKEND_SERVICE}"
sleep 2
systemctl is-active "${BACKEND_SERVICE}"

FAMILY_SMOKE_BASE=http://127.0.0.1:8002 FAMILY_SMOKE_TIMESTAMP_FILE=/var/lib/aladdin/family_smoke_last_success.timestamp FAMILY_REMEDIATE_NOTIFY=1 \\
  ./scripts/family_smoke_with_remediate.sh

systemctl daemon-reload
systemctl enable aladdin-family-prod-smoke.timer
systemctl start aladdin-family-prod-smoke.timer
systemctl start aladdin-family-prod-smoke.service

# P2: family ops alerts every 15 min (journal + smoke freshness)
(crontab -l 2>/dev/null | grep -v aladdin-family-ops; \\
 echo "*/15 * * * * cd ${REMOTE_ROOT} && ./venv/bin/python3 scripts/family_ops_alerts.py --check-all --notify >> /var/log/aladdin-family-ops.log 2>&1 # aladdin-family-ops") | crontab - || echo "WARN: family ops crontab failed"

echo ">>> family deploy smoke PASS"
EOF

echo ">>> Family backend deploy complete (${TS})"
echo ">>> Backup: ${REMOTE_ROOT}/.deploy_backups/family_${BACKUP_TAG}"
echo ">>> Rollback: docs/server/RUNBOOK_FAMILY_DEPLOY_ROLLBACK.md"
