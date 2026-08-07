# План: мгновенная автовыдача VPN (2026-07-22) — MVP worker-first

**ТЗ:** быстрее ключ/ссылка после оплаты.  
**Трекер:** `VPN_INSTANT_PROVISION_TODO_TRACKER.md` (`vinst-*`)  
**Safety backup Contabo:** `/opt/aladdin-shop-vpn-api/backups/vinst-worker-first-20260722-204434`

---

## Продуктовое решение (Six Hats → MVP)

**Не делаем сразу всё.** Сначала ускоряем «повара» (очередь jobs).

| Фаза | Что | Статус |
|------|-----|--------|
| **MVP P0** | Worker-first: timer ~1 с + kick после enqueue + drain пачки jobs + backoff ТЗ + alert | **сейчас** |
| P1 | Sync-inline `ready` | только если после P0 P95 &gt; 3 с |
| P2 | Push bot «ready» | позже |
| P3 | Балансировка локаций | позже |

**Честный SLA после MVP:** P50 ≤ 2–3 с, P95 ≤ 5 с при здоровом Contabo.  
(«P99 &lt; 1 с» — не обещаем в UI.)

---

## Главный инвариант: Happ-ссылки

Сейчас выдача **медленная, но надёжная**. После изменений должно остаться так же надёжно.

**Не меняем:**

- формат URL `https://aladdin-ai.ru/sub/<opaque_token>`
- генерацию / ротацию `opaque_token` у живых аккаунтов (кроме уже существующего revoke/expire)
- тело `/sub/` для Happ (профили VLESS)
- UI бота, платежи, shop.db, реф finalize

**Меняем только:** как быстро worker забирает `jobs` после оплаты.

**Проверка до/после:** снимок `opaque_tokens.tsv` в бэкапе — токены активных пользователей **идентичны**.

---

## Как сейчас (bottleneck)

`POST /provision` → job `pending` → systemd timer **60 с**, **1 job** за тик → бот поллит `/sub/`.

## MVP: что делаем

1. Timer `OnUnitActiveSec=1`, `AccuracySec=1`
2. Worker drain: до N jobs за один запуск (default 16)
3. `kick_worker()` сразу после INSERT job (provision/extend/trial/revoke/…)
4. Backoff: **5, 15, 30, 60, 180, 300** с; max attempts = 5
5. После финального fail — лог + optional Telegram alert
6. Фильтр `next_run_at <= now` (корректные ретраи)

---

## Откат

Из бэкапа: `worker.py`, timer/service, при необходимости `vpn.db` + `env`.
