# Referral UX + Partner + Withdraw — TODO Tracker

**План:** `PLAN_REFERRAL_UX_PARTNER_2026-07-22.md`  
**Дата:** 2026-07-22 (обновлено вечером — finalize paid→completed)  
**Ids:** `refux-*` (не затирать `br-*` / `rb-*` / `af-*` / `vinst-*`)

## Канон продукта (v1.1)

1. Базовый бонус: **15%** от **первой выданной** покупки друга → `ref_balance_rub`.
2. Бонус можно: **тратить в магазине** (Stars / Premium / VPN) **и** подать **заявку на вывод на карту** (ручная обработка админом).
3. Повышенный % (до **30%**, индивидуально) — после **≥5** оплаченных/выданных VPN-приглашений + заявка в поддержку; % **не светить** в UI.
4. Ссылку `ref_`, антиабуз, first-order механику **не ломать**.
5. UI: **«С выданной покупкой»** (не «С покупкой»).

## Todo

- [x] `refux-00` Аудит кода/прода
- [x] `refux-01` Трекер + ТЗ v1.1
- [x] `refux-02` Главный экран `nav:ref`
- [x] `refux-03` Экран `nav:refstats`
- [x] `refux-04` Экран повышенного % + прогресс 5 VPN
- [x] `refux-05` Spend бонуса в магазине + заявка на вывод
- [x] `refux-06` Админ: partner + override % + approve withdraw
- [x] `refux-07` Тесты + деплой MAIN/Contabo (`20260722-213923`)
- [x] `refux-08` UI copy: «С выданной покупкой»
- [x] `refux-09` VPN finalize: paid→completed + реф side-effects (`vpn_order_finalize.py`)
- [x] `refux-10` Repair Contabo stuck VPN (#73/#79/#96/#101/#104) → #104 = +75 ₽ рефереру
- [x] `refux-11` `/admin_vpn_finalize` + деплой `20260722-215635` + тесты finalize

## Следующий эпик

`vinst-*` — мгновенная автовыдача VPN: `PLAN_VPN_INSTANT_PROVISION_2026-07-22.md`
