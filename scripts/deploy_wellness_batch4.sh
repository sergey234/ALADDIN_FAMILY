#!/usr/bin/env bash
# Wellness batch 4 — packs (hero_flavor + exercise instructions), drift log, outcome fatigue JSON.
# Usage: ./scripts/deploy_wellness_batch4.sh [user] [host] [ssh_key]

set -euo pipefail

SSH_USER="${1:-root}"
HOST="${2:-149.154.65.180}"
SSH_KEY="${3:-${SSH_KEY_PATH:-}}"
REMOTE_ROOT="/opt/aladdin-backend"
SERVICE="aladdin-backend.service"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SSH_OPTS=(-o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15)
SCP_OPTS=(-o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15)
if [[ -n "${SSH_KEY}" ]]; then
  SSH_OPTS+=(-i "${SSH_KEY}")
  SCP_OPTS+=(-i "${SSH_KEY}")
fi

ssh_r() { ssh "${SSH_OPTS[@]}" "${SSH_USER}@${HOST}" "$@"; }
scp_f() { scp "${SCP_OPTS[@]}" "$1" "${SSH_USER}@${HOST}:$2"; }
scp_r() { scp -r "${SCP_OPTS[@]}" "$1" "${SSH_USER}@${HOST}:$2"; }

echo ">>> Wellness batch 4 deploy → ${SSH_USER}@${HOST}"

FILES=(
  "security/api/routers/wellness_router.py"
  "security/api/routers/ai_companion_router.py"
)

for f in "${FILES[@]}"; do
  scp_f "${LOCAL_ROOT}/${f}" "${REMOTE_ROOT}/${f}"
  echo "  OK ${f}"
done

for sub in cognitive behavioral humanistic jung; do
  scp_r "${LOCAL_ROOT}/security/services/ai_platform/wellness_knowledge/${sub}" \
    "${REMOTE_ROOT}/security/services/ai_platform/wellness_knowledge/"
  echo "  OK wellness_knowledge/${sub}/"
done

ssh_r "systemctl restart ${SERVICE}"
echo ">>> Restarted ${SERVICE}"
echo ">>> iOS: rebuild for recap + memory chips + outcome follow-up (local Xcode)"
echo ">>> Verify: ./scripts/verify_wellness_prod.sh https://aladdin-ai.ru"
