# Runbook: Family backend rollback

## When to use

- `deploy_family_backend.sh` failed after restart
- `test_family_prod_smoke.py` returns `"pass": false`
- Regressions in `POST /api/family/create` or `register-device`

## Rollback steps (on server)

```bash
BACKUP_DIR=/opt/aladdin-backend/.deploy_backups/family_YYYYMMDD_HHMMSS  # latest

cp "$BACKUP_DIR/app/routers/auth_router.py" /opt/aladdin-backend/app/routers/auth_router.py
cp "$BACKUP_DIR/app/routers/family.py" /opt/aladdin-backend/app/routers/family.py

cd /opt/aladdin-backend
./venv/bin/python3 -m py_compile app/routers/auth_router.py app/routers/family.py
systemctl restart aladdin-backend
sleep 2
systemctl is-active aladdin-backend

FAMILY_SMOKE_BASE=http://127.0.0.1:8002 ./venv/bin/python3 docs/server/test_family_prod_smoke.py
```

## Verify timer

```bash
systemctl list-timers | grep family
journalctl -u aladdin-family-prod-smoke.service -n 20 --no-pager
cat /var/lib/aladdin/family_smoke_last_success.timestamp
```

## Manual smoke (local operator)

```bash
ssh -i ~/.ssh/aladdin_server root@149.154.65.180 \
  'cd /opt/aladdin-backend && FAMILY_SMOKE_BASE=http://127.0.0.1:8002 ./venv/bin/python3 docs/server/test_family_prod_smoke.py'
```
