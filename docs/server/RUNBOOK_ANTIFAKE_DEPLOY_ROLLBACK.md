# Runbook — Antifake deploy & rollback (B-07)

**Host:** `149.154.65.180` · **Backend:** `/opt/aladdin-backend` · **API:** `:8002`  
**Deploy:** `./scripts/deploy_antifake_m1.sh root 149.154.65.180 ~/.ssh/aladdin_server`  
**SSH:** `ssh -i ~/.ssh/aladdin_server root@149.154.65.180` (см. `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md`)

## Pre-deploy

```bash
curl -s http://149.154.65.180:8002/api/health
ssh root@149.154.65.180 'cd /opt/aladdin-backend && ANTIFAKE_SMOKE_BASE=http://127.0.0.1:8002 ./venv/bin/python3 docs/server/test_antifake_prod_smoke.py'
```

Deploy script creates timestamped backup:

`/opt/aladdin-backend/.deploy_backups/antifake_YYYYMMDD_HHMMSS/`

## Deploy

```bash
cd ALADDIN_iOS
./scripts/deploy_antifake_m1.sh root 149.154.65.180 ~/.ssh/aladdin_server
```

Post-deploy checks:

```bash
ssh root@149.154.65.180 'cd /opt/aladdin-backend && bash scripts/antifake_post_deploy_check.sh'
```

Or step-by-step (P-05): `docs/server/ANTIFAKE_POST_DEPLOY_CHECKLIST.md`

```bash
ssh root@149.154.65.180 'cd /opt/aladdin-backend && \
  ANTIFAKE_SMOKE_BASE=http://127.0.0.1:8002 ANTIFAKE_SMOKE_POLL_JOB=1 ./venv/bin/python3 docs/server/test_antifake_prod_smoke.py && \
  ANTIFAKE_GATE_BASE=http://127.0.0.1:8002 ./venv/bin/python3 scripts/antifake_prod_gate_af11.py && \
  ./venv/bin/python3 scripts/antifake_verify_worker.py'
```

## Rollback (last backup)

```bash
ssh root@149.154.65.180 <<'SSH'
set -euo pipefail
cd /opt/aladdin-backend
LATEST=$(ls -1dt .deploy_backups/antifake_* 2>/dev/null | head -1)
if [[ -z "${LATEST}" ]]; then echo "no backup"; exit 1; fi
echo "Restoring from ${LATEST}"
rsync -a "${LATEST}/app/" ./app/
rsync -a "${LATEST}/scripts/" ./scripts/ 2>/dev/null || true
systemctl restart aladdin-backend.service aladdin-antifake-worker.service aladdin-sfm-core.service
sleep 3
systemctl is-active aladdin-backend.service
SSH
```

Re-run smoke after rollback.

## nginx 25MB (B-06)

Snippet: `/etc/nginx/snippets/aladdin-antifake-upload.conf`  
Must include `client_max_body_size 25m` and `proxy_read_timeout 300s`.

```bash
ssh root@149.154.65.180 'nginx -t && systemctl reload nginx'
grep client_max_body_size /etc/nginx/snippets/aladdin-antifake-upload.conf
```

## Media TTL cron (B-08)

```bash
ssh root@149.154.65.180 'crontab -l | grep antifake_cleanup || echo "missing cron"'
```

Expected: `*/15 * * * *` → `scripts/antifake_cleanup_uploads.py`
