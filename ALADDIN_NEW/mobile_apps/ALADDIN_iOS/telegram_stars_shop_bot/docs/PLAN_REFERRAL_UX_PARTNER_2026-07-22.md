# План: Referral UX + Partner + Withdraw (2026-07-22)

**Статус:** ✅ реализовано и задеплоено (Contabo + MAIN).  
**Трекер:** `REFERRAL_UX_PARTNER_TODO_TRACKER.md`  
**Деплои:** `20260722-213923` (реф UX), `20260722-215635` (VPN paid→completed + реф side-effects).

---

## 1. Тексты (утверждённый гибрид, актуальный UI)

### Главный экран

```
👥 Пригласить друга

Получайте 15% бонуса от первой покупки друга.
Бонус — на баланс магазина: можно потратить внутри магазина
или вывести на свою карту.

Как это работает:
1️⃣ Отправьте ссылку другу
2️⃣ Друг сделает первую покупку у нас
3️⃣ Вам начислится 15% бонуса после оплаты и выдачи заказа друга

🔗 Ваша ссылка:
…

📊 Приглашено: X
💳 С выданной покупкой: Y
🎁 Накоплено бонусов: Z ₽

────────
🚀 Нужен повышенный процент?
Приведите от 5 друзей с оплаченным VPN и напишите нам.
Для сильных партнёров доступны индивидуальные условия —
бонус до 30% от суммы первой покупки приглашённого.
```

> **Важно:** в UI пишем **«С выданной покупкой»**, не «С покупкой» — чтобы не путать оплату (`paid`) и выдачу (`completed` + `fulfillment_applied_at`).

---

## 2. Канон продукта (v1.1 — зафиксировано)

1. Базовый бонус: **15%** от **первой выданной** покупки друга → `users.ref_balance_rub`.
2. Бонус можно: **тратить в магазине** (Stars / Premium / VPN) **и** подать **заявку на вывод на карту** (ручной approve админом).
3. Повышенный % (до **30%**, индивидуально) — после **≥5** оплаченных/выданных VPN-приглашений + заявка в поддержку; % **не светить** в UI статуса.
4. Ссылку `?start=ref_<id>`, антиабуз, first-order механику **не ломать**.
5. Автовыплата на карту в v1 **не** делаем.

---

## 3. Что сделано (код)

| Слой | Файл / место | Изменение |
|------|----------------|-----------|
| UX тексты/клавы | `bot/services/referral_ux.py` | home / stats / boost / withdraw; «С выданной покупкой» |
| Навигация | `bot/handlers/hub.py` | `nav:ref`, `nav:refstats`, `nav:refboost`, `nav:refwithdraw`, `ref:wd:ask` |
| Spend бонуса | `bot/services/dual_wallet.py` | при `REF_BONUS_VPN_ONLY=false` — bonus-first на любой товар |
| Partner override | `users.ref_partner_status`, `users.ref_commission_override_pct` | миграции + `pricing.commission_for_first_order(..., override_percent=)` |
| Side-effects | `bot/services/order_flow.py` → `apply_completed_side_effects` | комиссия только на **первом completed** |
| Withdraw | `bot/services/ref_withdraw_repo.py` + таблица `ref_withdraw_requests` | pending / paid / rejected |
| Админ | `bot/handlers/admin.py` | `/admin_ref_partner`, `/admin_ref_withdraw` |
| Prod env | Contabo + MAIN `shared/.env` | `REF_BONUS_VPN_ONLY=false` |
| Тесты | `tests/test_referral_ux_partner.py`, dual_wallet | ✅ |

---

## 4. Критический фикс: paid → completed (реф не ломался)

### Симптом
Заказ VPN друга (пример **#104**, 500 ₽, `referrer_id=493897224`) завис в **`paid`**: VPN в `vpn.db` уже `vpn_active`, но shop-заказ без `completed` / `fulfillment_applied_at` → в реф-статистике «приглашено 1 / с покупкой 0 / бонус 0».

### Корневая причина
`vpn_payment_hook` после admin/webhook «Оплачен» делал **provision/extend**, но **не** переводил заказ в `completed` и **не** вызывал `apply_completed_side_effects`.  
«Оплачен» ≠ «Выдан». Рефка ждёт **выдачу**.

### Решение (для всех пользователей)
| Модуль | Роль |
|--------|------|
| `bot/services/vpn_order_finalize.py` | `finalize_vpn_order_completed()` — идемпотентно `paid`/`processing` → `completed` + side-effects |
| `vpn_payment_hook.py` | после успешного provision/extend → finalize |
| `vpn_post_purchase_delivery.py` | после успешной Happ-доставки → finalize (догон) |
| `/admin_vpn_finalize <id\|stuck>` | ручной/массовый дожим stuck VPN |

### Repair на Contabo (2026-07-22)
Закрыты stuck VPN с активным аккаунтом: **#73, #79, #96, #101, #104**.  
**#104:** `completed`, `commission_rub=75`, `commission_paid=1` → рефереру **75 ₽** (15% от 500).

### Проверка после repair
- Заказ #104: `completed` + `fulfillment_applied_at` заполнен  
- `users.ref_balance_rub` для `493897224` = **75.0**  
- Реф-метрики: приглашено 1 · с выданной покупкой 1 · баланс 75 ₽  
- Реф-логика first-order / override **не менялась** — только догонка выдачи

---

## 5. Не делаем в v1 (по-прежнему)

- Автовыплата на карту (только заявка + ручной approve)
- Публичные цифры 20/25/30 в статусе пользователя
- Смена first-order механики на «% со всех оплат»

---

## 6. Следующее ТЗ

Автовыдача VPN-ключей (мгновенная) — см.  
`PLAN_VPN_INSTANT_PROVISION_2026-07-22.md` + `VPN_INSTANT_PROVISION_TODO_TRACKER.md`.
