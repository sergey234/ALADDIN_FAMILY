# SFM ML Dependencies Policy (B-SFM-W11)

**Canonical registry:** `app/data/sfm/function_registry.json`  
**Sync script:** `docs/server/sync_sfm_registry_from_manifest.sh`

## Rule

| Runtime | torch / cv2 / heavy ML | Why |
|---------|------------------------|-----|
| `:8003` SFM hot path (`aladdin-sfm-core`) | **Forbidden** | Fast execute; boot must not depend on GPU/CPU torch |
| `:8002` FastAPI gunicorn | **Forbidden** | API latency + import shadow risk |
| Worker units (`aladdin-antifake-worker`, `aladdin-ml-worker`) | **Allowed (lazy)** | Heavy agents load only when job runs |

## Current prod behavior

- `fake_news_detection_agent` without torch → explicit routers use **honest fallback** (`rule_engine` / `database`), not mock.
- Antifake media jobs: sync path today; worker lazy load in `app/workers/antifake_ml_worker.py` (B2-10 ✅).

## Deploy checklist

1. Never `pip install torch` into gunicorn venv without worker split.
2. Preflight: `sfm_truth_check.sh` must PASS before deploy.
3. ML smoke runs against worker endpoint or explicit router smoke scripts only.
