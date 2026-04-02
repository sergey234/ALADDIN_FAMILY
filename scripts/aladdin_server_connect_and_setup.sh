#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/aladdin_server_connect_and_setup.sh root 149.154.65.180 8002 /path/to/ssh_key
#
# This script prepares ALADDIN backend on a remote server:
# - Ensures repo is aligned with origin/master
# - Creates/updates Python venv and installs dependencies
# - Creates/enables systemd unit for gunicorn on :8002
# - Restarts service and performs health and anti-mock checks
#
# Requirements: ssh access, git, python3, systemd, postgres

SSH_USER="${1:-root}"
HOST="${2:-149.154.65.180}"
PORT="${3:-${PORT:-8002}}"
SSH_KEY_PATH="${4:-${SSH_KEY_PATH:-}}"
BASE="http://${HOST}:${PORT}"

SSH_ARGS=("-o" "BatchMode=yes" "-o" "StrictHostKeyChecking=no")
if [[ -n "${SSH_KEY_PATH}" ]]; then
  SSH_ARGS+=("-i" "${SSH_KEY_PATH}")
fi

remote_run() {
  # Robustly escape the whole command so nested quotes / heredocs work correctly over ssh.
  # shellcheck disable=SC2059
  local cmd="$1"
  ssh "${SSH_ARGS[@]}" "${SSH_USER}@${HOST}" "bash -lc $(printf '%q' "$cmd")"
}

echo ">>> [1/7] Auditing server ${HOST}"
remote_run "uname -a; ss -ltnp | head -n 50 || netstat -ltn | head -n 50 || true"
remote_run "mkdir -p /opt/aladdin-backend/logs"

echo ">>> [2/7] Aligning /opt/aladdin-backend with origin/master"
remote_run "
  set -e
  cd /opt/aladdin-backend || mkdir -p /opt/aladdin-backend && cd /opt/aladdin-backend
  git rev-parse --is-inside-work-tree || git init
  git remote -v | grep -q origin || git remote add origin https://github.com/sergey234/ALADDIN_FAMILY.git
  git fetch origin
  git checkout -B master origin/master
  git branch backup-\$(date +%Y%m%d_%H%M%S) || true
  git reset --hard origin/master
  git clean -fdX
"

echo ">>> [3/7] Ensuring Python venv and dependencies"
remote_run "
  set -e
  cd /opt/aladdin-backend
  python3 -m venv venv || true
  source venv/bin/activate
  pip install --upgrade pip
  pip install fastapi uvicorn gunicorn psycopg2-binary aiosqlite asyncpg PyJWT structlog sqlalchemy prometheus-client slowapi requests
"

echo ">>> [4/7] Writing systemd unit for gunicorn :${PORT}"
UNIT_PATH="/etc/systemd/system/aladdin-backend.service"
remote_run "
  set -e
  cat > ${UNIT_PATH} <<'UNIT'
[Unit]
Description=Aladdin Backend (gunicorn :8002)
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/aladdin-backend
Environment=DISABLE_SFM_MOCK=1
Environment=PYTHONPATH=/opt/aladdin-backend
ExecStart=/opt/aladdin-backend/venv/bin/gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app -b 0.0.0.0:${PORT}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
UNIT
  systemctl daemon-reload
  systemctl enable --now aladdin-backend.service
  systemctl status --no-pager aladdin-backend.service | head -n 50
"

echo ">>> [5/7] Basic health checks"
remote_run "curl -s -S -m 8 http://127.0.0.1:${PORT}/api/health || true"
curl -s -S -m 8 "${BASE}/api/health" || true

echo ">>> [6/7] Wildcard and anti-mock quick checks"
echo "--- /api/auth/register-device empty body (expect 422; no mock markers)"
curl -s -S -m 12 -i -X POST -H 'Content-Type: application/json' -d '{}' \
  "${BASE}/api/auth/register-device" | tee /tmp/register_device_empty_response.txt
if grep -E 'sfm_mock|mock_fallback|\"source\":\"sfm_' -n /tmp/register_device_empty_response.txt; then
  echo "[FAIL] mock markers detected in /api/auth/register-device response" >&2
  exit 1
else
  echo "[OK] No mock markers in /api/auth/register-device"
fi

echo "--- Intentional unknown critical path (expect 404)"
curl -s -S -m 8 -i -X POST -H 'Content-Type: application/json' -d '{}' \
  "${BASE}/api/auth/unknown" | head -n 20 || true

echo ">>> [7/7] OpenAPI sanity and tracker stats"
curl -s -S -m 15 "${BASE}/openapi.json" -o /tmp/openapi_now.json || true
python3 - <<'PY' || true
import json
try:
    j=json.load(open('/tmp/openapi_now.json','r',encoding='utf-8'))
    paths=j.get('paths',{})
    print('register-device in OpenAPI:', '/api/auth/register-device' in paths, list(paths.get('/api/auth/register-device',{}).keys()))
except Exception as e:
    print('openapi_read_failed', e)
PY

echo "--- /api/reports/privacy/tracker/stats (expect 200/204, not 404)"
curl -s -S -m 12 -i "${BASE}/api/reports/privacy/tracker/stats" | head -n 20 || true

echo ">>> DONE"

