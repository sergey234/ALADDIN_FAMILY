#!/usr/bin/env bash
# Antifake M1 — deploy API + worker artifacts to ALADDIN backend (:8002)
# af-10-04 / af-10-05
#
# Usage:
#   chmod +x scripts/deploy_antifake_m1.sh
#   ./scripts/deploy_antifake_m1.sh [ssh_user] [host] [ssh_key_path]
#
# Example:
#   ./scripts/deploy_antifake_m1.sh root 149.154.65.180 ~/.ssh/aladdin_server
#
# НЕ деплоить в telegram_stars_shop_bot — только /opt/aladdin-backend

set -euo pipefail

SSH_USER="${1:-root}"
HOST="${2:-149.154.65.180}"
SSH_KEY="${3:-${SSH_KEY_PATH:-}}"
REMOTE_ROOT="/opt/aladdin-backend"
BACKEND_SERVICE="aladdin-backend.service"
WORKER_SERVICE="aladdin-antifake-worker.service"
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

echo ">>> Antifake M1 deploy → ${SSH_USER}@${HOST}:${REMOTE_ROOT}"

FILES=(
  "app/routers/antifake.py"
  "app/services/antifake_service.py"
  "app/services/antifake_jobs_store.py"
  "app/services/antifake_premium.py"
  "app/services/antifake_rate_limit.py"
  "app/services/antifake_upload_store.py"
  "app/services/antifake_queue.py"
  "app/services/antifake_worker_tasks.py"
  "app/workers/antifake_ml_worker.py"
  "app/security/ml_lazy_loader.py"
  "docs/server/test_antifake_prod_smoke.py"
  "docs/server/smoke_env.py"
  "backend/requirements-antifake-worker.txt"
)

for rel in "${FILES[@]}"; do
  src="${LOCAL_ROOT}/${rel}"
  if [[ ! -f "${src}" ]]; then
    echo "WARN: missing ${src}, skip"
    continue
  fi
  remote_dir="${REMOTE_ROOT}/$(dirname "${rel}")"
  ssh_r "mkdir -p '${remote_dir}'"
  scp_f "${src}" "${remote_dir}/"
  echo "  ✓ ${rel}"
done

scp_f "${LOCAL_ROOT}/deploy/aladdin-antifake-worker.service.example" "/tmp/aladdin-antifake-worker.service.${TS}"
scp_f "${LOCAL_ROOT}/deploy/nginx/antifake-upload-limits.conf.example" "/tmp/aladdin-antifake-nginx.${TS}"

ssh_r bash -s <<EOF
set -euo pipefail
cd "${REMOTE_ROOT}"

if [[ -f backend/requirements-antifake-worker.txt ]]; then
  ./venv/bin/pip install -q -r backend/requirements-antifake-worker.txt || true
fi

mkdir -p /var/lib/aladdin/antifake/uploads
chown aladdin:aladdin /var/lib/aladdin/antifake/uploads 2>/dev/null || true

if [[ ! -f /etc/systemd/system/${WORKER_SERVICE} ]]; then
  cp "/tmp/aladdin-antifake-worker.service.${TS}" "/etc/systemd/system/${WORKER_SERVICE}"
  sed -i 's/User=aladdin/User=root/' "/etc/systemd/system/${WORKER_SERVICE}" 2>/dev/null || true
  systemctl daemon-reload
  systemctl enable "${WORKER_SERVICE}" || true
fi

if [[ ! -f /etc/nginx/snippets/aladdin-antifake-upload.conf ]]; then
  mkdir -p /etc/nginx/snippets
  cp "/tmp/aladdin-antifake-nginx.${TS}" /etc/nginx/snippets/aladdin-antifake-upload.conf
  echo "NOTE: add 'include /etc/nginx/snippets/aladdin-antifake-upload.conf;' to nginx server block if not present"
fi

./venv/bin/python3 -m py_compile app/routers/antifake.py app/services/antifake_queue.py app/services/antifake_worker_tasks.py

systemctl restart "${BACKEND_SERVICE}"
systemctl restart "${WORKER_SERVICE}" 2>/dev/null || systemctl start "${WORKER_SERVICE}" 2>/dev/null || echo "WARN: worker service not started (install redis + rq)"

sleep 2
systemctl is-active "${BACKEND_SERVICE}" || (journalctl -u "${BACKEND_SERVICE}" -n 40 --no-pager; exit 1)

if [[ -f docs/server/test_antifake_prod_smoke.py ]]; then
  ANTIFAKE_SMOKE_BASE="http://127.0.0.1:8002" ./venv/bin/python3 docs/server/test_antifake_prod_smoke.py || echo "WARN: smoke failed — check ANTIFAKE_INTERNAL_SMOKE_SECRET"
fi
EOF

echo ">>> Antifake M1 deploy complete (${TS})"
