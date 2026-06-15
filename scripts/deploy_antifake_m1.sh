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

# B-07: timestamped backup before overwrite
BACKUP_TAG="$(date +%Y%m%d_%H%M%S)"
ssh_r "mkdir -p '${REMOTE_ROOT}/.deploy_backups/antifake_${BACKUP_TAG}/app/services' '${REMOTE_ROOT}/.deploy_backups/antifake_${BACKUP_TAG}/scripts'"
for rel in app/routers/antifake.py app/services/antifake_service.py app/services/antifake_jobs_store.py; do
  ssh_r "cp '${REMOTE_ROOT}/${rel}' '${REMOTE_ROOT}/.deploy_backups/antifake_${BACKUP_TAG}/${rel}' 2>/dev/null || true"
done

FILES=(
  "app/routers/antifake.py"
  "app/services/antifake_service.py"
  "app/services/antifake_jobs_store.py"
  "app/services/antifake_security.py"
  "app/services/antifake_call_directory_store.py"
  "app/services/antifake_fraud_ingest.py"
  "app/services/antifake_reports_store.py"
  "app/services/antifake_whitelist_store.py"
  "app/services/antifake_family_store.py"
  "app/services/antifake_family_notify.py"
  "app/services/antifake_premium.py"
  "app/services/antifake_rate_limit.py"
  "app/services/antifake_upload_store.py"
  "app/services/antifake_queue.py"
  "app/services/antifake_worker_tasks.py"
  "app/workers/antifake_ml_worker.py"
  "app/security/ml_lazy_loader.py"
  "app/security/safe_function_manager.py"
  "app/security/ai_agents/fake_news_detection_agent.py"
  "app/database/migrations/create_antifake_scam_numbers.sql"
  "app/database/migrations/create_antifake_reports.sql"
  "app/database/migrations/create_antifake_family.sql"
  "app/database/migrations/create_antifake_jobs.sql"
  "data/antifake/scam_numbers_ru_v1.csv"
  "scripts/antifake_import_scam_numbers_csv.py"
  "scripts/antifake_cleanup_uploads.py"
  "scripts/antifake_prod_gate_af11.py"
  "docs/server/test_antifake_prod_smoke.py"
  "docs/server/smoke_env.py"
  "backend_tests/test_antifake_security_m.py"
  "backend_tests/test_antifake_call_directory_store.py"
  "backend_tests/test_antifake_fraud_ingest.py"
  "backend_tests/test_antifake_call_spoof.py"
  "backend_tests/test_antifake_media_probes.py"
  "backend_tests/test_antifake_rate_limit.py"
  "docs/server/RUNBOOK_ANTIFAKE_MODEL_VERSION.md"
  "docs/server/RUNBOOK_ANTIFAKE_DEPLOY_ROLLBACK.md"
  "scripts/antifake_verify_worker.py"
  "scripts/antifake_ops_alerts.py"
  "scripts/antifake_scam_db_rollback.py"
  "scripts/antifake_post_deploy_check.sh"
  "docs/server/RUNBOOK_ANTIFAKE_WORKER_OOM.md"
  "docs/server/RUNBOOK_ANTIFAKE_SCAM_DB_ROLLBACK.md"
  "docs/server/ANTIFAKE_POST_DEPLOY_CHECKLIST.md"
  "backend_tests/test_antifake_call_directory_contract.py"
  "backend_tests/test_antifake_ops_alerts.py"
  "start_sfm_core_http.py"
  "backend/requirements-antifake-worker.txt"
  "backend/requirements-antifake-ml.txt"
  "docs/server/aladdin-sfm-core.service"
  "docs/server/aladdin-backend.service"
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

if [[ -f backend/requirements-antifake-ml.txt ]]; then
  echo ">>> F-13: installing torch+transformers (CPU) — may take several minutes..."
  ./venv/bin/pip install -r backend/requirements-antifake-ml.txt
  ./venv/bin/python3 -c "import torch; import transformers; print('ml ok', torch.__version__, transformers.__version__)"
fi

if [[ -f docs/server/aladdin-sfm-core.service ]]; then
  cp docs/server/aladdin-sfm-core.service /etc/systemd/system/aladdin-sfm-core.service
  systemctl daemon-reload
fi

if [[ -f docs/server/aladdin-backend.service ]]; then
  cp docs/server/aladdin-backend.service /etc/systemd/system/aladdin-backend.service
  systemctl daemon-reload
fi

mkdir -p /var/lib/aladdin/antifake/uploads
chown aladdin:aladdin /var/lib/aladdin/antifake/uploads 2>/dev/null || true

if [[ ! -f /etc/systemd/system/${WORKER_SERVICE} ]]; then
  cp "/tmp/aladdin-antifake-worker.service.${TS}" "/etc/systemd/system/${WORKER_SERVICE}"
  sed -i 's/User=aladdin/User=root/' "/etc/systemd/system/${WORKER_SERVICE}" 2>/dev/null || true
  systemctl daemon-reload
  systemctl enable "${WORKER_SERVICE}" || true
fi

# B-06: always sync nginx 25MB + 300s snippet, reload when nginx present
mkdir -p /etc/nginx/snippets
cp "/tmp/aladdin-antifake-nginx.${TS}" /etc/nginx/snippets/aladdin-antifake-upload.conf
if command -v nginx >/dev/null 2>&1; then
  nginx -t && systemctl reload nginx || echo "WARN: nginx reload failed — check include in server block"
else
  echo "NOTE: nginx not installed — copy snippet manually"
fi

if [[ -f app/database/migrations/create_antifake_jobs.sql ]]; then
  ./venv/bin/python3 - <<'PY' || echo "WARN: antifake_jobs migration failed"
from pathlib import Path
from sqlalchemy import text
from app.database.database import engine

sql = Path("app/database/migrations/create_antifake_jobs.sql").read_text()
with engine.begin() as conn:
    for stmt in sql.split(";"):
        line = stmt.strip()
        if line:
            conn.execute(text(line))
print("antifake_jobs tables ok")
PY
fi

if [[ -f app/database/migrations/create_antifake_scam_numbers.sql ]]; then
  ./venv/bin/python3 - <<'PY' || echo "WARN: antifake scam_numbers migration failed"
from pathlib import Path
from sqlalchemy import text
from app.database.database import engine

sql = Path("app/database/migrations/create_antifake_scam_numbers.sql").read_text()
with engine.begin() as conn:
    for stmt in sql.split(";"):
        line = stmt.strip()
        if line:
            conn.execute(text(line))
print("antifake_scam_numbers tables ok")
PY
fi

if [[ -f app/database/migrations/create_antifake_reports.sql ]]; then
  ./venv/bin/python3 - <<'PY' || echo "WARN: antifake reports migration failed"
from pathlib import Path
from sqlalchemy import text
from app.database.database import engine

sql = Path("app/database/migrations/create_antifake_reports.sql").read_text()
with engine.begin() as conn:
    for stmt in sql.split(";"):
        line = stmt.strip()
        if line:
            conn.execute(text(line))
print("antifake_reports tables ok")
PY
fi

if [[ -f app/database/migrations/create_antifake_family.sql ]]; then
  ./venv/bin/python3 - <<'PY' || echo "WARN: antifake family migration failed"
from pathlib import Path
from sqlalchemy import text
from app.database.database import engine

sql = Path("app/database/migrations/create_antifake_family.sql").read_text()
with engine.begin() as conn:
    for stmt in sql.split(";"):
        line = stmt.strip()
        if line:
            conn.execute(text(line))
print("antifake_family tables ok")
PY
fi

# B-10: enforce premium gate on prod (free users → 403; smoke uses X-Aladdin-Smoke)
ENV_FILE="${REMOTE_ROOT}/.env"
if [[ -f "\${ENV_FILE}" ]]; then
  if grep -q '^ANTIFAKE_ALLOW_FREE=' "\${ENV_FILE}"; then
    sed -i 's/^ANTIFAKE_ALLOW_FREE=.*/ANTIFAKE_ALLOW_FREE=0/' "\${ENV_FILE}"
  else
    echo 'ANTIFAKE_ALLOW_FREE=0' >> "\${ENV_FILE}"
  fi
  if ! grep -q '^ANTIFAKE_INTERNAL_SMOKE_SECRET=' "\${ENV_FILE}"; then
    echo "WARN: ANTIFAKE_INTERNAL_SMOKE_SECRET missing in \${ENV_FILE} — deploy smoke will fail premium checks"
  fi
fi

./venv/bin/python3 -m py_compile app/routers/antifake.py app/services/antifake_premium.py app/services/antifake_queue.py app/services/antifake_worker_tasks.py app/services/antifake_reports_store.py app/services/antifake_whitelist_store.py app/services/antifake_family_store.py app/services/antifake_family_notify.py app/services/antifake_security.py app/services/antifake_jobs_store.py

pkill -f start_sfm_core_http.py 2>/dev/null || true
sleep 1
if systemctl restart aladdin-sfm-core.service 2>/dev/null; then
  sleep 16
  systemctl is-active aladdin-sfm-core.service || echo "WARN: aladdin-sfm-core not active after restart"
else
  echo "WARN: aladdin-sfm-core restart skipped"
fi
systemctl restart "${BACKEND_SERVICE}"
systemctl restart "${WORKER_SERVICE}" 2>/dev/null || systemctl start "${WORKER_SERVICE}" 2>/dev/null || echo "WARN: worker service not started (install redis + rq)"

sleep 2
systemctl is-active "${BACKEND_SERVICE}" || (journalctl -u "${BACKEND_SERVICE}" -n 40 --no-pager; exit 1)

if [[ -f docs/server/test_antifake_prod_smoke.py ]]; then
  ANTIFAKE_SMOKE_BASE="http://127.0.0.1:8002" ANTIFAKE_SMOKE_POLL_JOB=1 ./venv/bin/python3 docs/server/test_antifake_prod_smoke.py || echo "WARN: smoke failed — check ANTIFAKE_INTERNAL_SMOKE_SECRET"
fi

if [[ -f scripts/antifake_verify_worker.py ]]; then
  ANTIFAKE_GATE_BASE="http://127.0.0.1:8002" ./venv/bin/python3 scripts/antifake_verify_worker.py || echo "WARN: worker verify failed"
fi

# B-08: cron cleanup uploads every 15 min
(crontab -l 2>/dev/null | grep -v aladdin-antifake-cleanup; echo "*/15 * * * * cd ${REMOTE_ROOT} && ./venv/bin/python3 scripts/antifake_cleanup_uploads.py >> /var/log/aladdin-antifake-cleanup.log 2>&1 # aladdin-antifake-cleanup") | crontab - || echo "WARN: crontab install failed"

# P-01/P-02: ops alerts every 15 min
(crontab -l 2>/dev/null | grep -v aladdin-antifake-ops; echo "*/15 * * * * cd ${REMOTE_ROOT} && ./venv/bin/python3 scripts/antifake_ops_alerts.py --check-all >> /var/log/aladdin-antifake-ops.log 2>&1 # aladdin-antifake-ops") | crontab - || echo "WARN: ops alerts crontab failed"

chmod +x scripts/antifake_post_deploy_check.sh 2>/dev/null || true

if [[ -f scripts/antifake_import_scam_numbers_csv.py && -f data/antifake/scam_numbers_ru_v1.csv ]]; then
  ./venv/bin/python3 scripts/antifake_import_scam_numbers_csv.py data/antifake/scam_numbers_ru_v1.csv || echo "WARN: scam CSV import failed"
fi
EOF

echo ">>> Antifake M1 deploy complete (${TS})"
echo ">>> Backup: ${REMOTE_ROOT}/.deploy_backups/antifake_${BACKUP_TAG}"
echo ">>> Rollback: docs/server/RUNBOOK_ANTIFAKE_DEPLOY_ROLLBACK.md"
