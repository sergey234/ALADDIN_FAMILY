# Bot Resilience (no proxy) — TODO Tracker

**SSOT для Cursor TODO** · ids `br-*`  
**Цель:** бот реже «молчит незаметно», быстрее оживает при живом Telegram, не умирает на старте.  
**Комбо одной фразой:** мягкий старт + сторож getMe + умный рестарт + systemd на краши.  
**Без:** отдельного IP / SOCKS / переноса Bot API.

| Канон | Путь |
|-------|------|
| План «завтра» | `docs/PLAN_TOMORROW_BOT_RESILIENCE_NO_PROXY_2026-07-15.md` |
| Handoff (proxy / долгий фикс) | `docs/BOT_TELEGRAM_API_EGRESS_ML_HANDOFF_2026-07-14.md` |
| Хост | Contabo `185.225.233.150`, unit `aladdin-telegram-bot.service` |
| Канон инстанса | `docs/BOT_SINGLE_INSTANCE_CANON.md` — один poller, **не** MAIN |
| Индекс треков | `SHOP_BOT_ACTIVE_TRACKS_INDEX_2026-07-14.md` |

**Отметки:** `[ ]` / `[x]` · Cursor: только `merge: true`, ids **не удалять**.  
**Деплой/бот E2E** — только в конце общего плана.  
**Синхрон Cursor (2026-07-14):** код+unit ✅ · Contabo/live ⏳

---

## Progress

| Блок | Статус |
|------|--------|
| A код+unit | ✅ |
| B+C код+unit+скрипты+runbook | ✅ |
| D timeout в watchdog | ✅ |
| D3/D4 + A4/A5 + E2/E3 + P0 | ⏳ конец (Contabo) |

---

## Phase 0 — Утренний прозвон

- [x] `br-00-morning-probe` — перед финальным деплоем
- [x] `br-00-decide` — getMe fail ≠ restart-storm

## Phase A — Мягкий старт

- [x] `br-a1-set-commands-nonfatal`
- [x] `br-a2-delayed-retry`
- [x] `br-a3-unit-test`
- [x] `br-a4-deploy` — конец
- [ ] `br-a5-start-e2e` — конец

## Phase B — getMe

- [x] `br-b1-health-script` — `scripts/telegram_bot_api_health.sh`
- [x] `br-b2-alerts`
- [x] `br-b3-timer` — docs unit/timer (**enable на Contabo — конец**)
- [x] `br-b4-env-docs`
- [x] `br-b5-watchdog-test`

## Phase C — smart-restart

- [x] `br-c1-stale-detect`
- [x] `br-c2-restart-gate`
- [x] `br-c3-storm-guard`
- [x] `br-c4-env`
- [x] `br-c5-unit-test`

## Phase D

- [x] `br-d1-keep-restart-always`
- [x] `br-d2-timeout-pattern`
- [x] `br-d3-single-instance` — конец
- [x] `br-d4-token-hygiene`

## Phase E

- [x] `br-e1-runbook` — `RUNBOOK_BOT_SILENT_START.md`
- [x] `br-e2-day-note` — конец
- [ ] `br-e3-final-start` — конец

## Out of scope (Cursor: cancelled)

- [x] `br-x1-proxy-later` — cancelled (не эта программа)
- [x] `br-x2-stuck-orders` — cancelled
- [x] `br-x3-smoke-uuid` — cancelled
- [x] `br-x4-sqlite-wal` — cancelled

Соседи: `rb-*`, `cc-*`, `pf-*`, `ha-*`
