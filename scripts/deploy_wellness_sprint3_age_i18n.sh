#!/usr/bin/env bash
# Sprint 3 — wellness age_band policy + reflective hints (no «столп» on API)
set -euo pipefail

SSH_USER="${1:-root}"
HOST="${2:-149.154.65.180}"
SSH_KEY="${3:-${SSH_KEY_PATH:-$HOME/.ssh/aladdin_server}}"
REMOTE_ROOT="/opt/aladdin-backend"
SERVICE="aladdin-backend.service"
TS="$(date +%Y%m%d_%H%M%S)"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SSH_OPTS=(-o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15)
SCP_OPTS=(-o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15)
if [[ -n "${SSH_KEY}" && -f "${SSH_KEY}" ]]; then
  SSH_OPTS+=(-i "${SSH_KEY}")
  SCP_OPTS+=(-i "${SSH_KEY}")
fi

ssh_r() { ssh "${SSH_OPTS[@]}" "${SSH_USER}@${HOST}" "$@"; }
scp_f() { scp "${SCP_OPTS[@]}" "$1" "${SSH_USER}@${HOST}:$2"; }

echo ">>> Wellness Sprint 3 (age + reflective i18n) → ${SSH_USER}@${HOST}"

FILES=(
  "security/api/routers/wellness_router.py"
  "security/services/ai_platform/wellness_age_policy.py"
  "security/services/ai_platform/wellness_reflective_modes.py"
  "security/services/ai_platform/wellness_i18n_loader.py"
  "security/services/ai_platform/jwt_claims.py"
  "security/services/ai_platform/wellness_i18n/reflective_modes_v1.json"
)

echo ">>> [1/4] Backup"
ssh_r "set -e
  cd ${REMOTE_ROOT}
  mkdir -p backups/wellness_s3_${TS}
  for f in ${FILES[*]}; do
    [ -f \"\$f\" ] && cp -a \"\$f\" \"backups/wellness_s3_${TS}/\" || true
  done
"

echo ">>> [2/4] Upload"
for rel in "${FILES[@]}"; do
  local_path="${LOCAL_ROOT}/${rel}"
  [[ -f "${local_path}" ]] || { echo "MISSING ${rel}" >&2; exit 1; }
  remote_path="${REMOTE_ROOT}/${rel}"
  ssh_r "mkdir -p \"\$(dirname '${remote_path}')\""
  scp_f "${local_path}" "${remote_path}"
  echo "  OK ${rel}"
done

echo ">>> [3/4] py_compile + restart"
ssh_r "set -e
  cd ${REMOTE_ROOT}
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_age_policy.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_reflective_modes.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_i18n_loader.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/jwt_claims.py
  ./venv/bin/python3 -m py_compile security/api/routers/wellness_router.py
  systemctl restart ${SERVICE}
  sleep 2
  systemctl is-active ${SERVICE}
"

echo ">>> [4/4] Smoke: reflective modes RU hint (no столп)"
ssh_r "set -e
  cd ${REMOTE_ROOT}
  ./venv/bin/python3 - <<'PY'
from security.services.ai_platform.wellness_i18n_loader import list_reflective_modes_from_i18n
ru = list_reflective_modes_from_i18n(locale=\"ru\")
presence = next(m for m in ru if m.get(\"id\") == \"presence\")
hint = presence.get(\"hint\") or \"\"
assert \"столп\" not in hint.lower(), hint
assert \"Принять себя\" in hint or \"герою\" in hint, hint
print(\"presence hint OK:\", hint[:80])
PY
"

echo ">>> Sprint 3 deploy done. Run: ./scripts/verify_wellness_reflective_prod.sh https://aladdin-ai.ru"
