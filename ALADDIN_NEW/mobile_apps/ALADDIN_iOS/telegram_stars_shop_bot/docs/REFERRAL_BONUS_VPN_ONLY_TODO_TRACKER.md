# Referral Bonus VPN-only — TODO Tracker

**SSOT Cursor TODO** · ids `rb-*`  
**План:** `PLAN_REFERRAL_BONUS_VPN_ONLY_2026-07-14.md`  
**Цель:** рефбонус нельзя тратить на Stars/Premium; только VPN (bonus-first → main).

**Канон кошельков:** `balance_rub` = основной · `ref_balance_rub` = бонусный (без перевода между ними).

Отметки: `[ ]` / `[~]` / `[x]` · в Cursor только `TodoWrite merge: true` по `rb-*`.  
Соседние треки (не удалять): `br-*` resilience, `cc-*` captcha auto-continue, `pf-*` профиль/VPN статус.  
**Пересечение:** `rb-r4-profile` делается **внутри slim-профиля** из `pf-*` (без возврата рефералки в профиль).

---

## Phase 0 — Спека и инварианты

- [x] `rb-00-canon-lock` — зафиксировать инварианты плана §2.2 в коде/доках (нет transfer bonus→main)
- [x] `rb-00-copy-keys` — утвердить user-facing строки (ошибка Stars/Premium, insufficient main, профиль)

---

## Phase R1 — Схема и helpers

- [x] `rb-r1-schema-bonus-applied` — `orders.bonus_applied_rub` (+ migrate existing → 0)
- [x] `rb-r1-ledger-kinds` — ledger: `bonus_credit`, `bonus_order_pay` (main `order_pay` без изменений смысла)
- [x] `rb-r1-balance-helpers` — `get_balances` / charge main / charge bonus VPN-only / dual charge VPN
- [x] `rb-r1-credit-ledger` — начисление в `order_flow` + запись `bonus_credit` в ledger

---

## Phase R2 — Гейты Stars / Premium

- [x] `rb-r2-stars-main-only` — Stars: только `balance_rub`; бонус игнорируется
- [x] `rb-r2-premium-main-only` — Premium (и gift): то же
- [x] `rb-r2-reject-message` — отказ: «❌ Бонусный баланс нельзя использовать…» (+ CTA VPN / топап)
- [x] `rb-r2-insufficient-main` — «❌ Недостаточно средств на основном балансе.» + «💳 Пополнить баланс»
- [x] `rb-r2-payment-kb` — кнопки оплаты Stars/Premium не предлагают бонус как источник

---

## Phase R3 — VPN bonus-first

- [x] `rb-r3-vpn-split-spend` — VPN full balance: bonus first, then main, одна транзакция
- [x] `rb-r3-vpn-mix` — VPN mix (если есть): тот же приоритет до внешней оплаты
- [x] `rb-r3-order-fields` — писать `balance_applied_rub` + `bonus_applied_rub`
- [x] `rb-r3-vpn-ui-hint` — на экране оплаты VPN показать доступный бонус / сколько спишется

---

## Phase R4 — Профиль / FAQ / API

- [x] `rb-r4-profile` — **verify** 💳/🎁 в slim-профиле после `pf-2-body-rewrite` (не второй rewrite профиля; OWNER переписывания = `pf-*`)
- [x] `rb-r4-faq` — `marketing.referral_faq_html` + реф-экран: убрать «любые покупки с баланса»
- [x] `rb-r4-partner-api` — profile JSON: оба баланса + `bonus_usable_for=vpn`
- [x] `rb-r4-ux-plan-doc` — секция spend VPN-only в `REFERRAL_UNIFIED_UX_PLAN.md` (профиль≠рефка — в том же файле разом с `pf-4-ux-doc`, один edit)

---

## Phase R5 — Тесты

- [x] `rb-r5-test-credit-bonus` — комиссия → только `ref_balance_rub`
- [x] `rb-r5-test-stars-reject` — Stars при бонусе > 0 и main = 0 → отказ
- [x] `rb-r5-test-premium-reject` — Premium аналогично
- [x] `rb-r5-test-vpn-bonus-only` — VPN полностью с бонуса
- [x] `rb-r5-test-vpn-split` — VPN split bonus+main
- [x] `rb-r5-test-topup-main` — топап не трогает бонус

---

## Phase R6 — Деплой / smoke

- [x] `rb-r6-env-flag` — optional `REF_BONUS_VPN_ONLY=true` в env.example + shared/.env
- [x] `rb-r6-deploy` — Contabo deploy (если в одном PR с `pf-*` — **один** выкат с `pf-5-deploy`)
- [ ] `rb-r6-smoke` — smoke spend: Stars fail на бонусе; VPN тратит бонус (профиль-look — вместе с `pf-5-e2e`)

---

## Out of scope (не путать)

| id | Тема |
|----|------|
| `rb-x1-proxy` | Bot API proxy / resilience (`br-*`) |
| `rb-x2-vpn-days` | Менять `VPN_REFERRAL_*_DAYS` (оставить как есть) |
| `rb-x3-payout` | Вывод бонуса в деньги / перевод людям — **запрещено навсегда** |

---

## Definition of Done

- [ ] Stars/Premium нельзя оплатить бонусом (UI + API + тесты)
- [ ] VPN списывает бонус первым, потом основной
- [ ] Рефначисления только на бонусный
- [ ] Профиль показывает два баланса + VPN-only
- [ ] Нет UI/API перевода бонус → основной
- [ ] Smoke на Contabo пройден
