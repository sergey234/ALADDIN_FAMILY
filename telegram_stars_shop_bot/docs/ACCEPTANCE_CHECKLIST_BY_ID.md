# Приёмка по ID плана (44 строки §3.0)

Канон списка задач: `docs/IMPLEMENTATION_PLAN_AND_TASKS.md` §3.0. **45-го ID в таблице нет** (блок `37-auto-fulfill-hybrid` — заголовок для `37-1`…`37-8`).

**После деплоя на сервер** пройдите чеклист применения изменений: `docs/ML_SYSTEM_HANDOFF_FINAL.md` **§2.1** (rsync, `shared/.env`, симлинки, три сервиса, health, смоук §9).

Этот файл — **жёсткая трассировка**: что можно подтвердить автотестами, что — только документом или руками на стенде/проде. Колонка **«Человек»** заполняется при приёмке (ФИО или инициалы, дата, окружение: `local` / `staging` / `prod`).

**Связанные документы**

- Сценарный ручной чеклист UI: `docs/ACCEPTANCE_CHECKLIST.md`
- Смоук автовыдачи: `docs/AUTO_FULFILL_SMOKE.md`
- Деплой и пост-релиз: `docs/ML_SYSTEM_HANDOFF_FINAL.md`

---

## Как прогонять автоматическую часть

Из каталога `telegram_stars_shop_bot/`:

```bash
python3 -m pytest -q
```

Ожидание: все тесты зелёные. Зафиксируйте внизу файла (или в тикете) **дату**, **hash коммита** и **версию Python**.

**Легенда колонки «pytest»**

| Значение | Смысл |
|----------|--------|
| **Да** | Есть тесты, по смыслу покрывающие задачу (регрессия в CI). |
| **Частично** | Тесты есть, но нет полного E2E всех подпунктов (например, только юниты / только API). |
| **Нет** | Задача преимущественно операционная или документарная; `pytest` не доказывает выполнение. |

Колонка **«Человек»**: `☐` не проверяли; после проверки замените на `☑` и краткую подпись, например `☑ И.И., 2026-04-22, staging`.

---

## Сводная таблица

| № | ID | pytest | Доказательства (тесты, код, доки) | Человек |
|---|-----|--------|--------------------------------------|---------|
| 1 | `0-backup` | Нет | `docs/IMPLEMENTATION_PLAN_AND_TASKS.md` §1.1–1.2; `docs/ML_SYSTEM_HANDOFF_FINAL.md` (бэкап перед деплоем) | ☐ |
| 2 | `1-lava-prod` | Частично | `tests/test_lava_webhook.py`, `tests/test_payment_provider_webhook.py`; retry/UX в `bot/services/lava_api.py`, `bot/handlers/shop.py`; прод-смоук — вручную | ☐ |
| 3 | `1-lava-ttl` | Да | `tests/test_pending_payment_ttl.py`; `orders_repo` + sweep в боте | ☐ |
| 4 | `1-rub-only` | Да | `tests/test_fx_display.py`, `tests/test_bot_domain_suite.py` (`test_fx_payment_hints_contains_usdt_rub_only` и др.) | ☐ |
| 5 | `2-crypto-spec` | Да | `tests/test_crypto_pay_config.py`; `docs/CRYPTO_PAY_SPEC.md`; `bot/config.py`, `env.example` | ☐ |
| 6 | `2-crypto-payload` | Да | `tests/test_crypto_pay_payload.py`; `bot/services/crypto_pay_payload.py` | ☐ |
| 7 | `2-crypto-invoice` | Частично | `tests/test_crypto_pay_api.py`, `tests/test_xrocket_pay_api.py`; полный UX в Telegram — `ACCEPTANCE_CHECKLIST.md` | ☐ |
| 8 | `2-crypto-webhook` | Да | `tests/test_crypto_pay_webhook.py`, `tests/test_xrocket_webhook.py`; роуты `partner_api/` | ☐ |
| 9 | `2-crypto-admin` | Да | `tests/test_admin_crypto_paid_gate.py`; `bot/handlers/admin.py`, `admin_crypto_paid_gate.py`, `shop_kb.py` | ☐ |
| 10 | `2-crypto-tests` | Да | То же, что п.9–8 (вебхуки + гейт) | ☐ |
| 11 | `3-state-machine` | Да | `tests/test_order_status.py`, `tests/test_order_flow.py`, `tests/test_provider_mark_paid_unit.py`; `bot/services/order_status.py` | ☐ |
| 12 | `3-tx-balance` | Частично | `tests/test_price_integrity_lite.py`, `tests/test_crypto_pay_payload.py` (mix), `tests/test_limits_antifraud.py`; политика транзакций — `docs/EDGE_CASES.md` §3.2 | ☐ |
| 13 | `3-topup-antifraud` | Да | `tests/test_limits_antifraud.py` (суммы, pending cap, интервал) | ☐ |
| 14 | `3-pending-limits` | Да | `tests/test_limits_antifraud.py` (`require_pending_order_cap`, partner API cap) | ☐ |
| 15 | `3-fulfillment-idem` | Да | `tests/test_order_flow.py` (повторный `completed`, комиссия); `order_flow.py`, `fulfillment_applied_at` | ☐ |
| 16 | `3-admin-ops` | Да | `tests/test_admin_ops.py`; `admin_audit_repo`, роли в `bot/config.py` | ☐ |
| 17 | `4-fulfill-hybrid` | Частично | `tests/test_auto_fulfill_policy.py`, `tests/test_orders_revert_auto_fulfill.py`, `docs/AUTO_FULFILL_SMOKE.md`; полный цикл на проде — вручную | ☐ |
| 18 | `4-fragment` | Частично | `tests/test_istar_fulfill_client.py`, `tests/test_istar_webhook.py`, `tests/test_fulfillment_recipient.py`; реальный partner API (iStar) — смоук вне CI | ☐ |
| 19 | `4-admin-ui` | Да | `tests/test_admin_order_ff.py` (`adm:ff*` / клавиатуры) | ☐ |
| 20 | `5-ref-rules` | Да | `tests/test_bot_domain_suite.py` (`test_quote_first_order_discount_and_wholesale`, `test_commission_for_first_order`); `EDGE_CASES.md` §3.1 | ☐ |
| 21 | `5-ref-stats` | Да | `tests/test_referral_stats.py`; `hub.py`, Partner profile в коде Partner API | ☐ |
| 22 | `6-menu-ux` | Частично | Косвенно `tests/test_bot_domain_suite.py`, `test_marketing_onboarding_*`; меню целиком — `ACCEPTANCE_CHECKLIST.md` §1–2 | ☐ |
| 23 | `6-premium-shelf` | Да | `tests/test_bot_domain_suite.py` (`hide_from_menu` для `premium_1`, фильтр меню) | ☐ |
| 24 | `7-docs-deploy` | Нет | `docs/TZ_VS_IMPLEMENTATION.md`, перекрёстные ссылки; выкат — `ML_SYSTEM_HANDOFF_FINAL.md` §0–2 | ☐ |
| 25 | `8-provider-reversal` | Да | `tests/test_order_status.py` (переходы), `tests/test_provider_mark_paid_unit.py` (`refunded`); `admin.py`, `shop_kb.py`, `buyer_order_notify.py`, `EDGE_CASES.md` §3.5 | ☐ |
| 26 | `8-invoice-reissue` | Да | `tests/test_invoice_checkout_cooldown.py`; `bot/services/invoice_checkout_cooldown.py`, `shop.py` | ☐ |
| 27 | `8-crypto-fx-policy` | Да | `docs/CRYPTO_PAY_SPEC.md` §3; `tests/test_price_integrity_lite.py`, `tests/test_crypto_pay_payload.py` | ☐ |
| 28 | `8-rate-limit-api` | Да | `tests/test_partner_api_rate_limit.py`; `partner_api/rate_limit_middleware.py` | ☐ |
| 29 | `8-secrets-runbook` | Нет | `docs/SECRETS_AND_ROTATION_RUNBOOK.md` (чтение и актуальность — человек) | ☐ |
| 30 | `8-price-integrity-lite` | Да | `tests/test_price_integrity_lite.py` | ☐ |
| 31 | `8-monitoring-stuck` | Частично | `tests/test_stuck_orders_query.py`; логи вебхуков и цикл `stuck_orders_monitor.py` — без автотеста на реальный cron времени | ☐ |
| 32 | `8-feature-flags` | Частично | `tests/test_crypto_pay_config.py` (флаги auto fulfill), `env.example`; полный прод-порядок — `EDGE_CASES.md` §3.7 + ручная проверка флагов | ☐ |
| 33 | `8-backup-cron` | **N/A** | Задача **отменена** по плану; приёмка не требуется | — |
| 34 | `8-edge-cases-doc` | Нет | `docs/EDGE_CASES.md` (актуальность — человек) | ☐ |
| 35 | `8-rollout-order-doc` | Нет | `docs/EDGE_CASES.md` §4 | ☐ |
| 36 | `8-refund-policy` | Частично | `docs/EDGE_CASES.md` вступление; FAQ в `bot/services/marketing.py` — выборочно `tests/test_bot_domain_suite.py` | ☐ |
| 37 | `37-1-env-spec` | Да | `tests/test_crypto_pay_config.py` (блок `AUTO_FULFILL_*`); `env.example`, `bot/config.py` | ☐ |
| 38 | `37-2-data-model` | Да | `tests/test_auto_fulfill_policy.py` (`test_db_migration_has_fulfillment_columns`); `bot/db/database.py` | ☐ |
| 39 | `37-3-fulfill-api` | Да | `tests/test_istar_fulfill_client.py`, `tests/test_fulfillment_recipient.py` | ☐ |
| 40 | `37-4-worker-queue` | Частично | `partner_api/routers/istar_webhook.py`, `bot/services/auto_fulfill_runner.py`, worker entrypoint по плану; отдельного долгого E2E воркера в pytest может не быть | ☐ |
| 41 | `37-5-state-machine` | Да | `tests/test_orders_revert_auto_fulfill.py`; связка с `order_status` / revert в `orders_repo` | ☐ |
| 42 | `37-6-admin-ui` | Да | `tests/test_admin_order_ff.py` | ☐ |
| 43 | `37-7-buyer-ux` | Да | `tests/test_buyer_order_notify.py`; тексты в `buyer_order_notify.py` | ☐ |
| 44 | `37-8-tests-smoke` | Частично | Тесты из п.42–43 и `docs/AUTO_FULFILL_SMOKE.md`; полный смоук по документу — человек | ☐ |

---

## Журнал прогона pytest (заполнять при приёмке)

| Дата | Commit (короткий SHA) | Команда | Результат | Кто запускал |
|------|-------------------------|---------|------------|--------------|
| | | `python3 -m pytest -q` | | |

---

## Примечание для «100% уверенности»

**Зелёный pytest** не заменяет: бэкап на проде, реальный выкат, LAVA/Crypto на живом URL, визуальный проход `ACCEPTANCE_CHECKLIST.md`. Строки с **pytest: Нет** или **N/A** требуют только ручной или документальной фиксации.

Опциональные будущие усиления — `docs/OPS_PHASE2_PLAN.md`.
