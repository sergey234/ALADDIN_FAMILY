# F-07 — Antifake model version & rollback

## Version tag

- Env: `ANTIFAKE_MODEL_VERSION` (default `antifake-v1.0.0`)
- Exposed in API responses (`model_version`) and `GET /api/antifake/metrics`

## Rollback (ops)

1. Note current version: `curl -s …/api/antifake/metrics | jq .model_version`
2. Set previous on VPS `/opt/aladdin-backend/.env`:
   ```
   ANTIFAKE_MODEL_VERSION=antifake-v1.0.0-previous
   ```
3. Restart SFM + API + worker:
   ```bash
   systemctl restart aladdin-sfm-core.service aladdin-backend.service aladdin-antifake-worker.service
   ```
4. Smoke: golden text → `real_agent` or acceptable `local_ml`; media jobs must not return mock sources.
5. Revert env and restart when fixed forward.

## SFM / torch rollback

If BERT load fails after upgrade, see `RUNBOOK_SFM_ML_DEGRADED.md` — tier-2 `local_ml` remains honest fallback.
