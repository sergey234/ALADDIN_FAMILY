# Runbook — SFM / torch degraded (af-P-06)

**Prod:** `149.154.65.180` · API `:8002` · SFM `:8003` · `/opt/aladdin-backend`

## Quick triage

```bash
curl -s http://127.0.0.1:8003/api/sfm/status | jq .
curl -s http://127.0.0.1:8002/api/health
cd /opt/aladdin-backend && ANTIFAKE_SMOKE_BASE=http://127.0.0.1:8002 ./venv/bin/python3 docs/server/test_antifake_prod_smoke.py
```

| Symptom | Likely cause | Action |
|---------|--------------|--------|
| `sfm_loaded: false`, `load_error` syntax/import | Bad deploy / SFM file | Fix `safe_function_manager.py`, `py_compile`, restart SFM |
| `sfm_loaded: true`, text `source: local_ml` | SFM execute fail, tier-2 OK | Check `:8003/api/execute`, journalctl SFM |
| torch import fail | ML deps missing | `pip install -r backend/requirements-antifake-ml.txt` |
| OOM / killed during BERT | 3.7GB RAM VPS | Restart SFM; reduce concurrency; keep `local_ml` fallback |
| 422 active_executions | Slot leak | F-01 purge in SFM; restart `aladdin-sfm-core` |
| Smoke B-11 fail | SFM not healthy | See rows above |
| Smoke Q-07 fail | SFM up but not real_agent | Verify fake_news handler + torch |

## Restart sequence

```bash
systemctl restart aladdin-sfm-core.service
sleep 16
systemctl is-active aladdin-sfm-core.service
curl -s http://127.0.0.1:8003/api/sfm/status | jq .sfm_loaded
systemctl restart aladdin-backend.service
```

## Fallback policy (prod)

- **Never** enable mock / `sfm_mock` — 503 + iOS `validateForProduction()`.
- If SFM down: `local_ml` + heuristic (F-12) — honest badge, not `real_agent`.
- If torch OOM: fix infra or accept `local_ml` until RAM upgraded; do **not** fake `real_agent`.

## Deploy ML stack (F-13)

```bash
./scripts/deploy_antifake_m1.sh root 149.154.65.180 ~/.ssh/aladdin_server
```

Requires `backend/requirements-antifake-ml.txt` (CPU torch). First BERT inference may take 30–90s; smoke uses 90s timeout for golden text.

## Logs

```bash
journalctl -u aladdin-sfm-core -n 80 --no-pager
journalctl -u aladdin-backend -n 40 --no-pager
```
