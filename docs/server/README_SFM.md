# SFM canonical paths (production)

| Resource | Path |
|----------|------|
| SFM code | `/opt/aladdin-backend/app/security/safe_function_manager.py` |
| Registry (canonical) | `/opt/aladdin-backend/app/data/sfm/function_registry.json` |
| Registry (legacy sync) | `/opt/aladdin-backend/data/sfm/function_registry.json` |
| HTTP API | `http://127.0.0.1:8003` |
| Truth check | `docs/server/sfm_truth_check.sh` |
| Pre-deploy | `docs/server/preflight_sfm.py` |

**PYTHONPATH:** `/opt/aladdin-backend/app` **before** `/opt/aladdin-backend` (shadow `security/` package).

**Forbidden in prod:** `deploy_optimized_sfm.sh`, `OptimizedSFM`, `mock-real-protection`.
