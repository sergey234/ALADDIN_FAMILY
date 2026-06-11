# SFM deploy runbook (B-OPS-04 / B-OPS-19)

## Blocked scripts (never run on prod)

- `deploy_optimized_sfm.sh`
- Any deploy that sets `ALADDIN_ALLOW_SFM_MOCK=1`

## Required pre-deploy

```bash
/opt/aladdin-backend/venv/bin/python3 /opt/aladdin-backend/docs/server/preflight_sfm.py
bash /opt/aladdin-backend/docs/server/sfm_truth_check.sh
```

Deploy **aborts** if either exits non-zero.

## Post-deploy

```bash
systemctl restart aladdin-sfm-core
systemctl restart aladdin-backend
bash /opt/aladdin-backend/docs/server/sfm_prod_smoke.sh
```
