# SEC-P2 — Legacy backend migration (R-14…18)

**Дата:** 2026-06-11 · **VPS:** `test_security_prod_smoke.py` → **pass:true 11/11**

| ID | Change | Evidence |
|----|--------|----------|
| SEC-P2-01 | `GET /api/darkweb/breaches` on explicit `app/routers/darkweb.py`; legacy route removed | explicit registered first |
| SEC-P2-02 | `POST /api/identity-theft/monitor-credit` alias → `/monitor/credit` | `identity_theft.py` |
| SEC-P2-03 | `GET /api/location/bubble/*` → **410** + canonical hint | `location_bubble_legacy_deprecation.py` |
| SEC-P2-04 | monitoring routes removed from `parental_control_router`; explicit `parental_monitoring.py` + bypass ingest | `ingest_parental_monitoring_events` |
| SEC-P2-05 | `/api/devices/*` → dedicated `app/routers/devices.py` | misc_other_compat quarantine-only |

**R-19 COPY post-L3:** ❌ skipped per product decision (onboarding frozen).
