---
name: aladdin-no-mock-bypass
description: Parental bypass and sensitive API — never ship sfm_mock or mock_fallback. Use for bypass, parental-control, family API, analytics.
origin: ALADDIN
---

# ALADDIN — No Mock in Production

Canonical rule: `.cursor/rules/prod-no-mock-bypass.mdc`

## Block always

- `source: "sfm_mock"`, `sfm_fallback`, `mock_fallback`
- `200 OK` with mock envelope on parental/family/gamification/analytics paths

## Bypass apply

`POST /api/parental/bypass/apply` → real `APIResponse<Bool>` (`success`, `data`, `message`) or real HTTP error.

## iOS logs

- `BYPASS APPLY start` / `ok` / `failed`

## Server

`api_gateway.py` `should_block_mock_result` — keep in sync. Guide: `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md`
