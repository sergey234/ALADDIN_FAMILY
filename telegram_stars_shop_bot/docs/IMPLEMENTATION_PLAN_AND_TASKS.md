# План работ, бэкап и список задач (магазин-бот)

Единый файл для отслеживания: **полный бэкап**, **все согласованные задачи**, ссылки на краевые случаи и **оценка мер безопасности**.

## Где выполняем работы (надёжнее всего)

1. **Локально** в репозитории `telegram_stars_shop_bot/`: правки кода, `pytest`, при необходимости ручной смоук бота с тестовой БД.  
2. **Деплой на прод** только после зелёных тестов — по `docs/ML_SYSTEM_HANDOFF_FINAL.md` (`rsync` в `releases/<TS>/`, симлинки `current_app`, `pip` при смене зависимостей, `systemctl restart` трёх сервисов).

Правки напрямую на сервере без копии в git — только для экстренного hotfix с последующей синхронизацией репозитория.

### VPN Shop (AiMonkeyVPN) — отдельный контур

Задачи **vpn-00 … vpn-40** (60+ пунктов плана), статус ✅/🟡/⏳, цепочка **оплата → Telegram ID → 📥/📷**, деплой на VPS:

| Документ | Назначение |
|----------|------------|
| **`docs/VPN_TASKS_STATUS.md`** | **Главный реестр todo** (обновлять при выкатах) |
| `docs/VPN_SHOP_INTEGRATION_PLAN.md` | Архитектура, §13–§14 |
| `docs/VPN_ML_SYSTEM_HANDOFF.md` | Handoff для агентов / пост-деплой |
| `docs/VPN_SHOP_API.md` | Контракт API |

---

## 1. Полный бэкап бота

### 1.1 Локально (код в монорепозитории) — уже можно считать сделанным

Снимок дерева `telegram_stars_shop_bot/` (без `data/`, без venv, без `__pycache__`) сохраняется в каталог, который **не коммитится** в git:

- Путь: `mobile_apps/ALADDIN_iOS/BACKUPS/telegram_shop_bot/`
- Имя файла: `telegram_stars_shop_bot_code_YYYYMMDD-HHMMSS.tar.gz`

Повторить вручную при необходимости:

```bash
cd /path/to/ALADDIN_iOS
mkdir -p BACKUPS/telegram_shop_bot
TS="$(date +%Y%m%d-%H%M%S)"
tar --exclude='telegram_stars_shop_bot/.venv' \
  --exclude='telegram_stars_shop_bot/venv' \
  --exclude='telegram_stars_shop_bot/**/__pycache__' \
  --exclude='telegram_stars_shop_bot/**/*.pyc' \
  -czf "BACKUPS/telegram_shop_bot/telegram_stars_shop_bot_code_${TS}.tar.gz" \
  telegram_stars_shop_bot
```

`data/` в архив **намеренно не входит** (локальная SQLite может быть пустой/тестовой). Продовая БД — только на сервере (п. 1.2).

### 1.2 Production (обязательно перед выкладкой кода на сервер)

`ROOT=/opt/aladdin-telegram-shop-bot`. Канон исключений при `rsync` — `docs/ML_SYSTEM_HANDOFF_FINAL.md`.

**Минимум «полного бэкапа» на хосте:**

1. Копия секретов: `cp -a "${ROOT}/shared/.env" "${ROOT}/shared/.env.bak_$(date +%Y%m%d-%H%M%S)"`
2. Копия базы (путь к `shop.db` как на сервере, часто `current_app/data/shop.db`):
   `cp -a "${ROOT}/current_app/data/shop.db" ~/shop.db.bak_$(date +%Y%m%d-%H%M%S)`  
   (если `DATABASE_PATH` другой — взять из `shared/.env` / `systemctl cat`.)
3. Архив активного приложения **и** `shared/` — важно: `current_app` — **симлинк**, иначе в архив не попадёт код. Используйте раскрытие ссылок **`-h`** (GNU tar):
   ```bash
   TS="$(date +%Y%m%d-%H%M%S)"
   tar -czhf "${HOME}/shop_bot_backups/current_app_deref_shared_${TS}.tar.gz" \
     -C "${ROOT}" -h current_app shared
   ```
   Фактический каталог бэкапов на проде (пример): `/root/shop_bot_backups/` — файлы `shared.env.bak_*`, `shop.db.bak_*`, `current_app_deref_shared_*.tar.gz`.

**Регулярный cron-бэкап** по решению команды **не входит** в обязательный план; достаточно **полного снимка перед релизом/крупными изменениями**.

Задача в Cursor Todo: **`0-backup`** — закрыть после выполнения п. 1.2 на проде (и при желании повтором п. 1.1 локально).

---

## 2. Связанные документы

**Без дублирования смысла:** список задач по фазам ведётся **только в этом файле** (§3) и в Cursor Todo; `EDGE_CASES.md` — про статусы/края и согласование с кодом, а не вторая копия бэклога. `ML_SYSTEM_HANDOFF_FINAL.md` — канон деплоя на сервер (не дублирует §3, а ссылается на процедуру).

| Документ | Назначение |
|----------|------------|
| `docs/EDGE_CASES.md` | Статусы заказов, переходы, сторно провайдера, mix, рефка+API, порядок внедрения |
| `docs/ML_SYSTEM_HANDOFF_FINAL.md` | Деплой, `rsync`, симлинки, systemd, health `:8090` |
| `docs/TZ_VS_IMPLEMENTATION.md` | Сверка с ТЗ (обновлять по мере релизов) |
| `docs/CRYPTO_PAY_SPEC.md` | Crypto Pay: боты, testnet/mainnet, env, политика суммы ₽↔crypto, задел под вебхук |
| `docs/OPS_PHASE2_PLAN.md` | Опциональная фаза 2: Redis rate limit, алерты, инвойс в БД, авто-сторно по API, CI/CD |
| `docs/ACCEPTANCE_CHECKLIST_BY_ID.md` | Приёмка по каждому ID §3.0: pytest / доки / ручная колонка |
| `docs/FX_RATES_RUNBOOK.md` | Курсы `USD_RUB_RATE` / `USDT_RUB_RATE`, ЦБ, регламент на проде |

---

## 3. Список задач (согласованный бэклог)

Статусы в Cursor Todo могут отличаться; здесь — **канонический перечень**. Префикс **8-*** — операционный и краевой слой.

### 3.0 Сводная таблица 44 ID (для Notion / трекера)

**Про п.37:** в сумме **44** входят только строки **`37-1` … `37-8`**. Название **`37-auto-fulfill-hybrid`** в §3 — это **заголовок блока**, отдельного 45-го ID в этой математике нет (все восемь подзадач закрыты — блок считается выполненным).

| № | ID | Статус |
|---|-----|--------|
| 1 | `0-backup` | Готово |
| 2 | `1-lava-prod` | Готово |
| 3 | `1-lava-ttl` | Готово |
| 4 | `1-rub-only` | Готово |
| 5 | `2-crypto-spec` | Готово |
| 6 | `2-crypto-payload` | Готово |
| 7 | `2-crypto-invoice` | Готово |
| 8 | `2-crypto-webhook` | Готово |
| 9 | `2-crypto-admin` | Готово |
| 10 | `2-crypto-tests` | Готово |
| 11 | `3-state-machine` | Готово |
| 12 | `3-tx-balance` | Готово |
| 13 | `3-topup-antifraud` | Готово |
| 14 | `3-pending-limits` | Готово |
| 15 | `3-fulfillment-idem` | Готово |
| 16 | `3-admin-ops` | Готово |
| 17 | `4-fulfill-hybrid` | Готово |
| 18 | `4-fragment` | Готово |
| 19 | `4-admin-ui` | Готово |
| 20 | `5-ref-rules` | Готово |
| 21 | `5-ref-stats` | Готово |
| 22 | `6-menu-ux` | Готово |
| 23 | `6-premium-shelf` | Готово |
| 24 | `7-docs-deploy` | ✅ `TZ_VS_IMPLEMENTATION.md`, перекрёстные ссылки на handoff и новые операции; выкат на прод — по `ML_SYSTEM_HANDOFF_FINAL.md` |
| 25 | `8-provider-reversal` | ✅ `refunded` / `payment_disputed`, `order_status.py`, админка `adm:refund|disp|dispok`, покупатель `buyer_order_notify`, `EDGE_CASES` |
| 26 | `8-invoice-reissue` | ✅ `invoice_checkout_cooldown.py`, `PAYMENT_CHECKOUT_INVOICE_COOLDOWN_SECONDS`, вызов из `shop.py`, тесты |
| 27 | `8-crypto-fx-policy` | ✅ Канон в `CRYPTO_PAY_SPEC.md` §3 + тесты целостности due |
| 28 | `8-rate-limit-api` | Готово |
| 29 | `8-secrets-runbook` | ✅ `docs/SECRETS_AND_ROTATION_RUNBOOK.md` |
| 30 | `8-price-integrity-lite` | ✅ `tests/test_price_integrity_lite.py` (`amount_due_external`, mix partial) |
| 31 | `8-monitoring-stuck` | Готово |
| 32 | `8-feature-flags` | Готово |
| 33 | `8-backup-cron` | Отменено |
| 34 | `8-edge-cases-doc` | Готово |
| 35 | `8-rollout-order-doc` | Готово |
| 36 | `8-refund-policy` | Готово |
| 37 | `37-1-env-spec` | Готово |
| 38 | `37-2-data-model` | Готово |
| 39 | `37-3-fulfill-api` | Готово |
| 40 | `37-4-worker-queue` | Готово |
| 41 | `37-5-state-machine` | Готово |
| 42 | `37-6-admin-ui` | Готово |
| 43 | `37-7-buyer-ux` | Готово |
| 44 | `37-8-tests-smoke` | Готово |

**По плану в репозитории:** таблица §3.0 закрыта; следующий шаг только **операционный** — смоук и выкат на живой URL по `docs/ML_SYSTEM_HANDOFF_FINAL.md` (при необходимости новый timestamp релиза). Жёсткая приёмка по строкам таблицы: `docs/ACCEPTANCE_CHECKLIST_BY_ID.md`.

### Гибрид G+ (усиление авто + оператор)

| ID | Задача | Статус |
|----|--------|--------|
| `gplus-1-ops-alert-create-failed` | После отката iStar `create_failed` → `paid`: `notify_ops_auto_fulfill_create_failed` + env `AUTO_FULFILL_FAILURE_ALERTS_ENABLED` | ✅ `auto_fulfill_runner.py` |
| `gplus-2-stuck-processing` | Отдельный алерт для долгого `processing`: `STUCK_PROCESSING_ALERT_MINUTES`, `list_order_ids_stuck_processing_only`, цикл в `stuck_orders_monitor.py`; старт цикла в `main.py` если часов **или** минут > 0 | ✅ |
| `gplus-3-admqueue` | Команда `/admqueue` + `list_orders_operator_attention_queue` + `OPERATOR_QUEUE_PROCESSING_IDLE_MINUTES` | ✅ `admin.py`, `orders_repo.py` |
| `gplus-4-tests-docs` | `tests/test_hybrid_g_plus.py`, правки `EDGE_CASES.md`, `env.example`, `test_crypto_pay_config.py` | ✅ |

### Фаза 0 — перед кодом на прод

| ID | Задача |
|----|--------|
| `0-backup` | ✅ Полный бэкап на проде: `.env`, `shop.db`, архив `current_app` + `shared`; локально — tar в `BACKUPS/telegram_shop_bot/` |

### Фаза 1 — LAVA и только ₽

| ID | Задача |
|----|--------|
| `1-lava-prod` | ✅ Тексты только LAVA (stub, `.env`, provider-webhook); retry `invoice/create` до 3 раз при сетевых/5xx/429; UX шагов 1→2→3 и прод-смоук — при выкате по чеклисту |
| `1-lava-ttl` | ✅ TTL просрочки `pending_payment` → `expired`, фоновый sweep в боте, сообщение пользователю + FAQ |
| `1-rub-only` | ✅ Убрать UAH/BYN из UI, marketing, FAQ, env.example, тестов |

### Фаза 2 — Crypto Pay

| ID | Задача |
|----|--------|
| `2-crypto-spec` | ✅ `docs/CRYPTO_PAY_SPEC.md`, `Settings` + `env.example`, `crypto_pay_api_origin()` |
| `2-crypto-payload` | ✅ `SB1|…` payload, `crypto_pay_payload.py`, сверка с `amount_due_external`, лимит `expires_in` |
| `2-crypto-invoice` | ✅ Crypto Pay + xRocket Pay, только USDT TRC20; `crypto_pay_api.py`, `xrocket_pay_api.py`, `_present_crypto_checkout`, `CRYPTO_PAY_WALLET_FALLBACK` |
| `2-crypto-webhook` | ✅ `POST …/crypto-pay-webhook` + `POST …/xrocket-webhook`, подписи, idempotency `cryptobot:{id}` / `xrocket:{id}` |
| `2-crypto-admin` | ✅ Гейт `adm:paid` для `pending_payment` + crypto/xRocket счёт; `adm:paidbg` + аудит `adm:paid_break_glass` (`admin_crypto_paid_gate.py`, `admin.py`, `shop_kb.py`) |
| `2-crypto-tests` | ✅ Pytest на оба вебхука (`tests/test_crypto_pay_webhook.py`, `tests/test_xrocket_webhook.py`) |

### Фаза 3 — Защита и целостность

| ID | Задача |
|----|--------|
| `3-state-machine` | ✅ Явный автомат статусов; запрет `completed` без `paid` |
| `3-tx-balance` | ✅ `bal` / `mixfi` / `mixcr`: `BEGIN IMMEDIATE`, блокировка user |
| `3-topup-antifraud` | ✅ Лимиты топапа, опционально двухглазое зачисление |
| `3-pending-limits` | ✅ Лимит `pending_payment` на пользователя |
| `3-fulfillment-idem` | ✅ Идемпотентность выдачи / защита двойной рефки (`fulfillment_applied_at`, транзакция, запрет `completed`→`completed`) |
| `3-admin-ops` | ✅ Роль оператора (`SUPER_ADMIN_IDS`), аудит в `admin_audit_log`, без отдельного UX-подтверждения крупных сумм (при необходимости — позже) |

### Фаза 4 — Выдача

| ID | Задача |
|----|--------|
| `4-fulfill-hybrid` | ✅ Спека `paid` → auto / `processing` → `completed` — реализовано в **п.37** (`auto_fulfill_runner`, `buyer_order_notify`, смоук `AUTO_FULFILL_SMOKE.md`) |
| `4-fragment` | ✅ Провайдер выдачи: **iStar partner API** (`istar_fulfill_client.py`, вебхук `istar_webhook`) — в скоупе **п.37** |
| `4-admin-ui` | ✅ Админка: `adm:ffman` / `adm:ffauto` / `adm:ffrst`, ref/ошибка в карточке — **п.37.6** (`admin.py`, `shop_kb.py`, `admin_order_ff.py`) |

### Фаза 5–6 — Рефералка и меню

| ID | Задача |
|----|--------|
| `5-ref-rules` | ✅ Оба триггера — **первая выдача** (`completed`): скидка `quote_product` / `is_first_order`, комиссия `order_flow.apply_completed_side_effects` — см. `EDGE_CASES.md` §3.1, `pricing.py`, `order_flow.py` |
| `5-ref-stats` | ✅ Счётчики и сумма начислений: `users_repo.user_stats`, профиль и экран «Реф-ссылка» в `hub.py`, Partner `GET /v1/user/profile` |
| `6-menu-ux` | ✅ Хаб AIMonkeyStars: `hub_menu_kb`, `ui_copy` / `marketing.onboarding_screen_1_html`; «Продать Stars» убран из главного меню, остаётся в **Профиль** |
| `6-premium-shelf` | ✅ Витрина Premium в боте без 1 мес.: `hide_from_menu` в `products.yaml` + фильтр в `nav_premium` (`catalog.Product`) |

### Фаза 7 — Доки и выкат

| ID | Задача |
|----|--------|
| `7-docs-deploy` | ✅ Доки и перекрёстные ссылки; **фактический cutover** (`rsync` + 3 `systemd` + смоук) — вне кода, см. `ML_SYSTEM_HANDOFF_FINAL.md` §0–2 |

### Операционный слой (8-*)

| ID | Задача | Примечание |
|----|--------|------------|
| `8-provider-reversal` | ✅ Сторно/спор: `refunded`, `payment_disputed`; админка; `EDGE_CASES` §1–2 | |
| `8-invoice-reissue` | ✅ Кулдаун повторного счёта на `order_id` + тест | |
| `8-crypto-fx-policy` | ✅ `CRYPTO_PAY_SPEC.md` §3 + тесты due | |
| `8-rate-limit-api` | ✅ Rate limit Partner API: `partner_api/rate_limit_middleware.py`, env `PARTNER_API_RATE_LIMIT_*`, тесты `tests/test_partner_api_rate_limit.py` | |
| `8-secrets-runbook` | ✅ `docs/SECRETS_AND_ROTATION_RUNBOOK.md` | |
| `8-price-integrity-lite` | ✅ Тесты `amount_due_external` и `create_order_with_balance_partial` | |
| `8-monitoring-stuck` | ✅ Логи: вебхуки HTTP≥400 (`partner_api_webhook_error`); «paid без движения» — цикл `stuck_orders_monitor.py` + `STUCK_PAID_*`, `orders_repo.list_order_ids_stuck_paid_or_processing` | |
| `8-feature-flags` | ✅ Поэтапный прод: зафиксировано в `EDGE_CASES.md` §3.7 + блоки в `env.example` (`CRYPTO_PAY_*`, `XROCKET_*`, `AUTO_FULFILL_*`) | |

**Уже сделано / отменено:**

| ID | Статус |
|----|--------|
| `8-backup-cron` | **Отменено** — регулярный cron не делаем |
| `8-edge-cases-doc` | **Готово** — `docs/EDGE_CASES.md` |
| `8-rollout-order-doc` | **Готово** — порядок в `EDGE_CASES.md` §4 |
| `8-refund-policy` | **Готово** — вступление + ссылка на `marketing.py` в `EDGE_CASES.md` |

### Пункт 37 — Автовыдача Stars / Premium (гибрид с ручным резервом)

| ID | Задача (верхний уровень) |
|----|---------------------------|
| `37-auto-fulfill-hybrid` | Автовыдача через partner API после `paid` + полный ручной fallback + флаги, идемпотентность, аудит, смоук и runbook |

**Подзадачи в Cursor Todo (спринт):** `37-1-env-spec` … `37-8-tests-smoke` (см. список задач агента; при реализации закрывать по порядку или параллельно 1↔2, затем 3→4→5, 6↔7, финал 8).

#### 37.0 Статус реализации (обновляйте по мере кода)

| Подзадача | Статус | Где в репозитории |
|-----------|--------|-------------------|
| `37-1-env-spec` | ✅ | `bot/config.py` (`AUTO_FULFILL_*`), `env.example`, этот файл |
| `37-2-data-model` | ✅ | `bot/db/database.py` — колонки `fulfillment_mode`, `fulfillment_attempt_count`, `fulfillment_last_error`, `fulfillment_last_attempt_at`, `fulfillment_provider_ref` + `migrate_legacy`; `bot/services/auto_fulfill_policy.py`; `tests/test_auto_fulfill_policy.py` |
| `37-3-fulfill-api` | ✅ | `bot/services/istar_fulfill_client.py`, `bot/services/fulfillment_recipient.py`, `ISTAR_*` в `bot/config.py` + `env.example`, тесты |
| `37-4-worker-queue` | ✅ | `bot/services/auto_fulfill_runner.py`, `orders_repo.claim_auto_fulfill_attempt_slot`, `python -m partner_api.auto_fulfill_worker`, вебхук завершения `partner_api/routers/istar_webhook.py` → `POST /v1/payments/istar-webhook` |
| `37-5-state-machine` | ✅ | `order_status`: `processing`→`paid` при сбое create; `orders_repo.revert_processing_to_paid_after_auto_fulfill_failure`; вебхук `order.failed` фиксирует ошибку; без авто-refund |
| `37-6-admin-ui` | ✅ | `bot/handlers/admin.py` (`adm:ffman` / `adm:ffauto` / `adm:ffrst`), `bot/keyboards/shop_kb.py`, `bot/services/admin_order_ff.py`, `orders_repo.set_order_fulfillment_mode` / `super_reset_paid_auto_fulfill_fields`, аудит `admin_audit_log` |
| `37-7-buyer-ux` | ✅ | `bot/services/buyer_order_notify.py` — авто-выдача + вебхук iStar + админка (`admin.py`); ссылки в поддержку через `support_order_question_url` |
| `37-8-tests-smoke` | ✅ | `tests/test_admin_order_ff.py`, `docs/AUTO_FULFILL_SMOKE.md`; алерты «paid без completed» — см. `8-monitoring-stuck` |

**Цель простыми словами:** после того как заказ стал **«Оплачен»**, бот **сам** пытается отправить Stars или Premium получателю (`user_note`); если API недоступен, получатель невалиден или сработал лимит — заказ остаётся на **операторе** по текущей схеме (кнопки **«В работе» → «Выдан»**), без потери денег и без двойной выдачи.

#### 37.1 Принципы гибрида

1. **По умолчанию безопасно:** `AUTO_FULFILL_ENABLED=false` до явного включения на проде после смоука.
2. **Раздельно по типу товара:** флаги вида `AUTO_FULFILL_STARS_ENABLED` / `AUTO_FULFILL_PREMIUM_ENABLED` (или один флаг + YAML-исключения по `product_id`) — чтобы включать Stars раньше Premium или наоборот.
3. **Порог «только вручную» (опционально):** `AUTO_FULFILL_MAX_ORDER_RUB` (0 = без потолка) или whitelist пользователей — крупные заказы только с оператором.
4. **Ручной override на заказ:** в админке флажок «не автоматизировать этот заказ» → только цепочка оператора; запись в `admin_audit_log`.
5. **Состояния (уже есть в автомате):** `paid` → при старте авто попытка перевести в **`processing`** → при успехе API → **`completed`**; при отказе — остаться в `paid` или `processing` с понятным кодом ошибки (см. 37.5).

#### 37.2 Интеграция выдачи (partner API / иной провайдер)

- Отдельный модуль `bot/services/fragment_fulfill.py` (или нейтральное имя `stars_premium_fulfill.py`), **секреты только в `shared/.env`**, не в git.
- Официальный/договорённый API: лимиты RPS, таймауты, **идемпотентный ключ** на заказ (`fulfillment_id` / `order_id` + hash), повтор безопасен.
- Маппинг заказа: `product_id` → тип выдачи (Stars количество / Premium срок), получатель из `user_note` (@username), валидация **до** вызова API.
- Логирование: сырой ответ провайдера (усечённо), correlation id, длительность.

#### 37.3 Триггер «когда крутить авто»

- **Вариант A (рекомендуется):** фоновая задача в боте или **отдельный worker** (уже есть `aladdin-webhook-worker`) — периодический выбор заказов `status=paid` AND `auto_fulfill_eligible` AND нет блокировки оператором, с `BEGIN IMMEDIATE` и блокировкой строки заказа.
- **Вариант B:** сразу после вебхука `paid` в том же процессе — риск таймаута HTTP вебхука; лучше ставить в **очередь** (таблица или in-memory с персистом) и обрабатывать в worker.
- Не блокировать ответ провайдеру LAVA/Crypto: вебхук быстро **200**, выдача — асинхронно.

#### 37.4 Идемпотентность и «не выдать дважды»

- Использовать уже заложенное в **`3-fulfillment-idem`**: `fulfillment_applied_at` / уникальный ключ попытки; перед API-проверкой «уже completed».
- Поля в `orders`: `fulfillment_attempt_count`, `fulfillment_last_error`, `fulfillment_last_attempt_at`, `fulfillment_provider_ref`, `fulfillment_mode` (`auto` \| `manual_only`) — для поддержки и ретраев (миграция в `bot/db/database.py`).
- Админ-кнопка **«Повторить авто»** (супер-админ) — только если не `completed` и не превышен лимит попыток.

#### 37.5 Ошибки, ретраи, ручной режим

- Классы ошибок: сеть 5xx / rate limit → **экспоненциальный backoff**, N попыток; 4xx «неверный username» → **не ретраить**, уведомление админам + пользователю «проверьте @username».
- После исчерпания ретраев — статус остаётся **`paid`** (или **`processing`** если ввели промежуточный «в очереди на выдачу»), пуш админам как сейчас.
- **Сторно оплаты** при ошибке выдачи автоматом **не делать** (политика уже в `EDGE_CASES` / возвраты — только поддержка); авто только **не завершает** заказ до разбора.

#### 37.6 UX для покупателя

- После `paid`: «Оплата получена, отправляем Stars / Premium…»; при `completed`: «Готово».
- При задержке: «Обрабатываем, обычно до X минут»; при ручном эскалау — ссылка на поддержку с `order_id`.

#### 37.7 Наблюдаемость и смоук

- Метрика или лог-агрегат: «paid без completed > N минут»; счётчик ошибок выдачи.
- Смоук: testnet / малый пакет Stars → полный авто-путь; второй смоук — отключённый флаг → только ручной путь.

#### 37.8 Связь с существующими ID

- **`4-fragment`**, **`4-fulfill-hybrid`**, **`4-admin-ui`** — закрыты реализацией **37** (см. §3 фаза 4). **`8-feature-flags`**, **`8-monitoring-stuck`** — по-прежнему операционный слой вокруг тех же флагов и «paid без completed».

---

## 4. Достаточно ли запланированного по безопасности?

**Для v1 небольшого магазина в Telegram — да, набора мер достаточно как разумный baseline к продакшену**, при условии что задачи **3-*** и **8-*** реально доведены до кода и смоуков, а секреты и админ-доступ бережно хранятся.

Что этот план **хорошо закрывает:**

- подделка вебхуков (подписи, идемпотентность);
- гонки и частичная оплата (транзакции, mix);
- спам заказами и зависшие оплаты (лимиты, TTL, мониторинг);
- человеческий фактор админа (роли, лог, break-glass для crypto);
- краевые сценарии (документ `EDGE_CASES.md`);
- поэтачный выкат (feature flags).

Что **остаётся вне** этого плана (и не заменяется им):

- отдельный **pentest** или формальный security audit;
- **юридический** и налоговый контур (оферта, крипто/фиат в вашей юрисдикции);
- **физическая** безопасность сервера и SSH;
- страхование от убытков и процедуры с платёжными провайдерами при спорах.

**Итог:** для заявленных целей план **не слабый**; «достаточно» — **да для старта прод**, при выполнении задач и дисциплине деплоя. Усиление сверх этого — по мере роста трафика и инцидентов, а не обязательный блокер для первого релиза.

---

## 5. Рекомендуемый порядок старта реализации

1. Закрыть **`0-backup`** на проде (§1.2).  
2. **`3-state-machine`** + **`3-tx-balance`** (фундамент).  
3. **`1-*`** → **`2-*`** → **`37-auto-fulfill-hybrid`** (покрывает бывшие **`4-*`**) → **`5-*` / `6-*`** → **`7-docs-deploy`** и оставшиеся **`8-*`**.  
4. **Политика деплоя:** финальный прод-переход из **`7-docs-deploy`** (домены, `rsync`, `systemd`, чеклист секретов, смоук на живом URL) — **последний крупный шаг** после закрытия остальных задач плана и Cursor Todo; параллельно с разработкой вести **стенд/копию БД**, документированные скрипты/чеклисты и выкладки на **непрод** или «тихий» прод с выключенными feature-флагами — иначе в конце всплывут расхождения окружения, вебхуков и таймзон.
