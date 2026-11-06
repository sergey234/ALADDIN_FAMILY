# Antifake worker without `.env` — all media checks dead

## 0) Карточка инцидента

- `date_start_utc:` ≤ 2026-10-16 12:50 (journal horizon; real start may be earlier)
- `date_end_utc:` 2026-11-06 12:32
- `timezone_note:` server logs in MSK
- `component:` `other` (iOS backend · 🇷🇺 MAIN — FirstVDS / Аладдин · запас · Россия (`…180`))
- `incident_type:` `other` — antifake-worker-missing-env
- `short_summary:` Antifake RQ worker crashed on every media job (`DATABASE_URL environment variable is required`). Voice / video / document / call checks never finished; users saw endless upload → timeout. Found during L-W1-AF-SMOKE (Family Safety device QA Q27–Q33).

## 1) Симптомы

1. iPhone: Antifake voice / document / video / call stuck on «Загрузка файла…», then «Анализ занял слишком много времени». Text check worked.
2. Nightly `aladdin-antifake-prod-smoke.service` failed every night: `audio/video/document/call job poll timeout`; auto-remediation (2 restarts) did not help → «FAIL — need human».
3. Nobody was alerted: the failed nightly unit stayed `failed` silently.

## 2) Проверки health

- `curl http://149.154.65.180:8002/api/health` → 200 ok (API itself healthy).
- OpenAPI: all antifake media routes present, 202/200 declared.
- `systemctl status aladdin-antifake-worker` → active (process alive, but each forked job crashed on import).
- `journalctl -u aladdin-antifake-worker` → `RuntimeError: DATABASE_URL environment variable is required` from `app/database/database.py` via `app/services/antifake_jobs_store.py`. 0 successful jobs in 21 days; 355 failed in last 24h.

## 3) Timeline

- T0 (≤ 2026-10-16): worker starts crashing on media jobs.
- T1 2026-11-06 15:2x MSK: smoke diagnosis — worker unit has no `EnvironmentFile`; backend unit has `/opt/aladdin-backend/.env`.
- T2 15:32 MSK (owner GO): unit backup → drop-in `env.conf` with `EnvironmentFile=-/opt/aladdin-backend/.env` → daemon-reload → restart worker only.
- T3 15:34 MSK: media smoke with real files 4/4 PASS; canonical text/URL smoke PASS.

## 4) Что сделали

1. Backup `/root/backups/antifake-worker-unit-20261106_153248`.
2. `/etc/systemd/system/aladdin-antifake-worker.service.d/env.conf`.
3. `systemctl daemon-reload && systemctl restart aladdin-antifake-worker.service` (API `:8002` not restarted).

## 5) Result

- PASS: voice 4.1s, video 10.1s, document 4.1s, call 2.0s — all `completed` with valid verdicts. Evidence: `docs/competitors/qa_device_2026-11-05/evidence/antifake_smoke_20261106.md`.
- Why the job never became `failed`: `fail_job` lives in the same crashing module, so the job stayed `queued` and the client polled to SLA.

## 5b) Почему молчало (audit 2026-11-06, read-only)

1. Smoke last success `2026-09-08T21:00:53Z` — media broken **since ≥ 2026-09-09** (~2 months), not 21 days. Failures: `* job poll timeout` (worker) + `429` (fixed device id; 1 run = 1 try + 2 retries = 12 media checks > 10/h limit, so retries could never pass).
2. Smoke did call Telegram notify, but **Bot API POST from MAIN times out** (`URLError: timed out`, 3/3; direct and via local tor). On-box alerts from MAIN never arrive.
3. `scripts/antifake_ops_alerts.py` cron (*/15) crashed every run with the same `DATABASE_URL` error (5559 tracebacks) and ran without notify.
4. `/api/health` = process up, not "checks complete" — stayed ok the whole time.
5. `aladdin-security-prod-smoke` failed only because its `antifake` domain failed (10/11 domains pass) — same root cause, not a second outage.
6. 15 689 jobs stuck in `queued`/`processing` forever.

## 6) Action items

Code ready locally (17/17 `backend_tests/test_antifake_pipeline_resilience.py`), **deploy = owner GO**:

- [x] `app/database/database.py` — loads backend `.env` itself when `DATABASE_URL` missing (`override=False`): any worker / cron / script.
- [x] `app/workers/antifake_ml_worker.py` — preflight (DB `SELECT 1`, tasks import, redis ping) in `--warm` (ExecStartPre) and `--listen`; fails unit start instead of crashing each job.
- [x] `app/services/antifake_job_staleness.py` + `antifake_jobs_store.get_job` — queued > 90s → `failed: worker_unavailable`; processing > SLA+60s → `worker_timeout`. iOS already stops on `failed` and shows retry.
- [x] `app/services/antifake_pipeline_health.py` + `GET /api/antifake/pipeline-health` — ok/degraded: worker registered, not all media failing, no stuck queue, smoke ≤ 26h.
- [x] `scripts/antifake_ops_alerts.py` — restored (local copy was 0 bytes), `--check-pipeline`, crashing check = ALERT not traceback.
- [x] `scripts/ops/main_antifake_watchdog.py` — runs on **Brain** (Contabo, Telegram works), */5, alert after 2 fails, re-alert 1h, recovery message.
- [x] Smoke: unique device id per run (`%Y%m%d%H%M%S`), SLA-aligned polling.
- [ ] Deploy to MAIN + restart backend/worker → smoke wrapper (writes timestamp) — owner GO.
- [ ] Install watchdog cron on Brain + one test alert — owner GO.
- [ ] One-off: mark 15 689 dead `queued`/`processing` jobs older than 1 day as `failed` — owner GO.
- [ ] `.env` lines 29–31 not parseable by python-dotenv (systemd accepts) — check format, values untouched.
