# Endpoint Contract and Server Access

## Canonical Content Contract

- `GET /api/content/manifest`
- `GET /api/content/delta?fromVersion=<int>`

Required response envelopes:

- `manifest` object for `/api/content/manifest`
- `delta` object for `/api/content/delta`

## Smoke Validation Script

- Script: `scripts/content_contract_smoke.py`
- Default target: `http://149.154.65.180:8002`
- Override with env:
  - `ALADDIN_API_BASE=http://149.154.65.180:8002`

Run:

```bash
python3 scripts/content_contract_smoke.py
```

**Детский контент — сверка прода, разделение API, что добавить в план (2026-04-27):** `docs/CHILD_CONTENT_PROD_CHECK_AND_ROADMAP.md`

## Production Server Access and Runbook

- Primary connection guide:
  - `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md`
- Mandatory production policy:
  - No mock/fallback responses for production APIs.
- Canonical deployment paths:
  - Backend root: `/opt/aladdin-backend`
  - Routers: `/opt/aladdin-backend/app/routers/`

## JWT/API Architecture Reference

- Architecture reference:
  - `ALADDIN_JWT_API_ARCHITECTURE_COMPLETE.md` (including **§6.3** — `smart_api_tester.py`, `register-device` body `device_id`, response `access_token`, and how to interpret the smoke run vs `full_system_endpoint_audit.py`).
- **OpenAPI-конформный прогон (правильные HTTP-методы + полный список операций с бэка):**
  - объяснение простым языком: `docs/OPENAPI_HTTP_CHECKS_EXPLAINED_RU.md`
  - скрипт: `scripts/openapi_conformant_audit.py` (по умолчанию `ALADDIN_BASE_URL=http://149.154.65.180:8002`, т.к. `/openapi.json` отдаётся там)
  - последний отчёт: `docs/OPENAPI_CONFORMANT_AUDIT_LATEST.md`
- Quick device registration contract (prod, 2026-04-25):
  - `POST /api/auth/register-device` with JSON `{"device_id":"<string>","deviceType":"ios"}` → `200` and `access_token` / `refresh_token`.

Use this file together with the server connection guide when validating or rolling out endpoint changes.

