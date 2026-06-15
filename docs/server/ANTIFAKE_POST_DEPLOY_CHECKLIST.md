# Post-deploy checklist — Antifake (P-05)

Run on VPS **after** `./scripts/deploy_antifake_m1.sh` or manual rsync.

## One command

```bash
ssh -i ~/.ssh/aladdin_server root@149.154.65.180 \
  'cd /opt/aladdin-backend && bash scripts/antifake_post_deploy_check.sh'
```

Or locally on server:

```bash
cd /opt/aladdin-backend
bash scripts/antifake_post_deploy_check.sh
```

## Steps (manual)

| # | Check | Command | Pass |
|---|-------|---------|------|
| 1 | API health | `curl -sf http://127.0.0.1:8002/api/health` | 200 |
| 2 | Prod smoke + job poll | `ANTIFAKE_SMOKE_POLL_JOB=1 python3 docs/server/test_antifake_prod_smoke.py` | exit 0 |
| 3 | Gate af-11 (6 checks) | `python3 scripts/antifake_prod_gate_af11.py` | exit 0 |
| 4 | Worker audio/video | `python3 scripts/antifake_verify_worker.py` | exit 0 |
| 5 | nginx 25MB | `grep client_max_body_size /etc/nginx/snippets/aladdin-antifake-upload.conf` | `25m` |
| 6 | Cron cleanup | `crontab -l \| grep antifake_cleanup` | `*/15` |
| 7 | Cron ops alerts | `crontab -l \| grep antifake_ops_alerts` | `*/15` |
| 8 | Ops alerts dry-run | `python3 scripts/antifake_ops_alerts.py --check-all` | no ALERT (or investigate) |

## On failure

- **Smoke / gate:** `RUNBOOK_ANTIFAKE_DEPLOY_ROLLBACK.md`
- **Worker OOM / 422:** `RUNBOOK_ANTIFAKE_WORKER_OOM.md` (P-03)
- **SFM / torch:** `RUNBOOK_SFM_ML_DEGRADED.md` (P-06)
- **Bad fraud DB:** `RUNBOOK_ANTIFAKE_SCAM_DB_ROLLBACK.md` (P-04)

## Related

- R-01 TestFlight code gate: `scripts/verify_antifake_release_readiness.py` (iOS tree, no VPS)
- B-07 deploy: `scripts/deploy_antifake_m1.sh`
