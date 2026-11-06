# L-W1-AF-SMOKE — 2026-11-06

Target: 🇷🇺 MAIN — FirstVDS / Аладдин · запас · Россия (`…180`), iOS API `:8002`.
No secrets in this file.

## Stage 1 — outside, no SSH (done)

| Check | Result |
|-------|--------|
| `GET /api/health` | 200 `{"status":"ok"}` · 0.43s |
| `GET /openapi.json` | 200 |
| `/api/antifake/check/text` · `/check/url` | present · 200/422 |
| `/api/antifake/check/audio` · `/check/video` · `/check/document` · `/call/analyze` | present · 202/200/400/403/413/429/503 |
| `/api/antifake/jobs/{job_id}` · `/call-directory` · `/metrics` | present |
| Unauth POST text/audio/video/document/call | 403 on all five (gate works, no job created) |

Client finding fixed: HTTP 413 → `badRequest("File too large")` did not match the `file_too_large` check, so users saw a generic error. `AntifakeCheckFailureHandler.isFileTooLarge` now matches both forms.

## Stage 1b — on server, read-only (owner GO 2026-11-06)

Root cause of Q27–Q29, Q32–Q33 found.

- Nightly `aladdin-antifake-prod-smoke.service` = **failed**: text OK, `audio/video/document/call job poll timeout`, still failing after 2 auto-restarts.
- `aladdin-antifake-worker.service` crashes on every media job:
  `RuntimeError: DATABASE_URL environment variable is required` (import of `app.services.antifake_jobs_store` → `app.database.database`).
- Worker unit has **no** `EnvironmentFile=/opt/aladdin-backend/.env` (only `ANTIFAKE_*` vars + `onnx.conf` drop-in). `aladdin-backend.service` has it; `.env` contains `DATABASE_URL`.
- First crash in journal: 2026-10-16 15:50 (journal horizon). Successful media jobs in 21 days: **0**. Failed in last 24h: 355.
- `fail_job` lives in the same crashing module, so jobs never become `failed` → stay `queued` → client polls to SLA → user sees timeout. This is exactly the device symptom.

Proposed fix (needs separate owner GO — systemd + restart on prod):
drop-in `/etc/systemd/system/aladdin-antifake-worker.service.d/env.conf` with `EnvironmentFile=-/opt/aladdin-backend/.env` → `daemon-reload` → restart worker → rerun smoke.

## Fix applied (owner GO 2026-11-06 15:32 MSK)

- Backup: `/root/backups/antifake-worker-unit-20261106_153248`
- Added `/etc/systemd/system/aladdin-antifake-worker.service.d/env.conf` → `EnvironmentFile=-/opt/aladdin-backend/.env`
- `daemon-reload` + restart **worker only**. Worker `active`, listening on `aladdin-antifake`; `aladdin-backend` untouched, health 200.
- Rollback: `rm …/env.conf && systemctl daemon-reload && systemctl restart aladdin-antifake-worker`

## Stage 2 — smoke on server ✅ 5/5

Canonical `test_antifake_prod_smoke.py` (`ANTIFAKE_SMOKE_POLL_JOB=1`): text, SMS, short text, URL phishing + bank allowlist, metrics, web trial, call-directory — **no failures**. Media part hit 429 (`media` bucket 10/h on the fixed device id `antifake-smoke-free`, used up by earlier runs) → rerun media with a fresh device id and real ffmpeg fixtures:

| Kind | File | HTTP | job_id | status | verdict | time |
|------|------|------|--------|--------|---------|------|
| text | canonical golden scam | 200 | sync | completed | likely_fake (golden) | — |
| voice | wav 5s 16 kHz, 160 KB | 202 | c464d84c | completed | uncertain | 4.1s |
| video | mp4 2s 320×240, 30 KB | 202 | 93888916 | completed | likely_real | 10.1s |
| document | jpg 800×1000, 10 KB | 202 | cae7b798 | completed | uncertain | 4.1s |
| call | wav 5s + caller_id QA number | 202 | cccaec5e | completed | likely_fake | 2.0s |

**L-W1-AF-SMOKE: PASS 5/5.** Fixtures deleted from server `/tmp` after run.

Still for device QA: same five checks from the iPhone after `GO на сборку` (Q27–Q29, Q32–Q33 evidence screenshots).
