# Трекер: быстрый `/start` + «🎁 Промокод»

**План:** [`PLAN_START_PERF_AND_PROMO_2026-07-31.md`](./PLAN_START_PERF_AND_PROMO_2026-07-31.md)  
**Статус:** ✅ A+B задеплоены · Contabo `20260731-140208`

---

## Part A — `/start` perf

| ID | Задача | Статус |
|----|--------|--------|
| sp-00-docs | PLAN + этот трекер | ✅ |
| sp-01-file-id | `hero_photo_input`: `file_id` first, upload fallback (+ process cache) | ✅ |
| sp-02-strip | Strip sticky KB не блокирует первый UI (background task) | ✅ |
| sp-03-critical-path | Язык сразу после upsert+throttle; side effects после UI | ✅ |
| sp-04-tests | pytest branding/start path | ✅ |
| sp-05-deploy | Contabo (+ MAIN sync), smoke `/start` | ✅ `20260731-140208` |

---

## Part B — Промокод

| ID | Задача | Статус |
|----|--------|--------|
| pm-00-docs | ТЗ зафиксирован в PLAN (кабинет, не «Профиль») | ✅ |
| pm-01-schema | Таблицы `promo_codes` / `promo_activations` (+ миграция) | ✅ |
| pm-02-repo | CRUD + validate (exists/active/dates/limit/used/personal/new-user) | ✅ |
| pm-03-ux | Кнопка в «Личный кабинет» + экран + FSM ввод | ✅ |
| pm-04-copy | Сообщения успеха/ошибок по ТЗ | ✅ |
| pm-05-pricing | Hook в `quote` → `rub_after_discounts` (без ломки checkout) | ✅ |
| pm-06-redeem | Списание при paid (mark_paid + balance) | ✅ |
| pm-07-admin | `/admin_promo` (create/list/on/off) + catalog | ✅ |
| pm-08-tests | pytest: типы, лимиты, scope, once-per-user | ✅ |
| pm-09-deploy | Contabo (+ MAIN), smoke активация + заказ со скидкой | ✅ `20260731-140208` |

---

## Ручной smoke

**A:** `/start` новым аккаунтом → язык появляется быстро (без долгой «тишины»).  
**B:** Кабинет → «🎁 Промокод» → ввод → успех/ошибка; заказ категории со скидкой; повтор → «уже активировали».

**Статус:** ✅ задеплоено Contabo `20260731-140208` (bot active).