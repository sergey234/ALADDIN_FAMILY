# VPN Instant Provision — TODO Tracker (MVP worker-first)

**План:** `PLAN_VPN_INSTANT_PROVISION_2026-07-22.md`  
**Backup:** `/opt/aladdin-shop-vpn-api/backups/vinst-worker-first-20260722-204434`  
**Ids:** `vinst-*`

## Инвариант

Happ `/sub/<opaque_token>` не менять; токены живых аккаунтов не ротировать.

## Todo

- [x] `vinst-00` Baseline Contabo + safety backup
- [x] `vinst-01` План MVP worker-first
- [x] `vinst-02` Worker: batch drain + next_run_at filter
- [x] `vinst-03` Continuous daemon loop (1s poll) + kick после enqueue
- [x] `vinst-04` Backoff 5/15/30/60/180/300 + alert final fail
- [x] `vinst-05` Тесты backoff/kick (unit) — 6 passed
- [x] `vinst-06` Деплой Contabo vpn-api worker (daemon, timer disabled)
- [x] `vinst-07` После: opaque_tokens совпадают + /sub/ 200
- [x] `vinst-08` Smoke latency enqueue→done (см. ниже)
- [ ] `vinst-09` (later) Sync-inline — только если нужно
- [ ] `vinst-10` (later) Location balancing

## Prod check 2026-07-22

- Worker: `Type=simple` loop `VPN_WORKER_POLL_SECONDS=1` (timer 1s отключён — был start-limit-hit)
- Tokens: **unchanged** (38/38), Darya token stable
- `/sub/` HTTP 200 для активных аккаунтов
- До: jobs ждал тик **~60 с** (и по 1 job)
- После: enqueue→done порядка **1–5 с** (зависит от Xray-скрипта)
