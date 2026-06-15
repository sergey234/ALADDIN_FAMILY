# Prod smoke — Antifake VPS (R-03)

Run on server after deploy (`149.154.65.180:8002`).

```bash
cd /opt/aladdin-backend
export ANTIFAKE_INTERNAL_SMOKE_SECRET='…'
export ANTIFAKE_SMOKE_BASE='http://127.0.0.1:8002'
export ANTIFAKE_SMOKE_POLL_JOB=1
./venv/bin/python3 docs/server/test_antifake_prod_smoke.py
```

## Expected

- `pass: true` in JSON report
- OpenAPI includes `/api/antifake/check/{audio,video,document}` and `/call/analyze` (`B-03`)
- `call-directory` returns `total_count >= 100` after CSV import (`C-08`)
- Audio job poll completes with valid `verdict` (`B-04`)

## Worker verify (optional)

```bash
./venv/bin/python3 scripts/antifake_verify_worker.py
```

## Rollback

See footer of `scripts/deploy_antifake_m1.sh` — restore previous `app/services/*`, restart `aladdin-backend` + `aladdin-antifake-worker`.
