# Краевые случаи и статусы заказов (EDGE_CASES)

Краткий операционный слой к политике из FAQ (источник правды в боте — `bot/services/marketing.py`, блоки «Возвраты» / «Возврат средств»): **возвраты по умолчанию не гарантируются**; исключения — только через поддержку с доказательствами. Авто-возвратов и массовых частичных возвратов в продукте **нет**. Здесь — **техника**: статусы в SQLite, переходы, чтобы не было противоречий вроде «оплачен и отменён как товар» без правил.

**Резервное копирование:** регулярный cron-бэкап **не входит** в обязательный план; достаточно **ручного** снимка перед релизами (см. `ML_SYSTEM_HANDOFF_FINAL.md`).

---

## 1. Статусы заказа (`orders.status`)

### Статусы в коде (v1 прод)

| Статус | Смысл |
|--------|--------|
| `pending_payment` | Заказ создан, ждём оплату (LAVA / Crypto Pay / ручная сверка по старой схеме). По таймеру `ORDER_PENDING_PAYMENT_EXPIRE_MINUTES` бот может перевести в `expired`. |
| `paid` | Оплата подтверждена (вебхук или баланс / смешанный сценарий согласно коду). |
| `processing` | Оператор взял в работу (выдача). |
| `completed` | Товар выдан; срабатывают побочные эффекты (рефералка и т.д. по текущей логике). |
| `expired` | Истёк срок оплаты инвойса (`pending_payment` → больше не оплачиваем автоматически). Из него допустим только переход в `refunded` (операционная чистка). |
| `refunded` | Деньги возвращены / сторно на стороне провайдера **или** зафиксирован ручной итог разбора поддержки (без выдачи). Терминальный. |
| `payment_disputed` | Разбор chargeback/спора; из него только в `refunded` или обратно в `paid` по решению супер-админа + аудит. |

**Не использовать** `cancelled` для **оплаченного** заказа товара: в коде `cancelled` уже относится к **заявкам на выкуп** (`sell_requests`), путаница с заказами Stars/Premium недопустима.

---

## 2. Матрица допустимых переходов (целевое состояние)

Столбец «Кто» — кто инициирует переход.

| Из | В | Кто | Условие / примечание |
|----|---|-----|----------------------|
| `pending_payment` | `paid` | LAVA webhook / Crypto Pay webhook / логика баланса | Сумма и идемпотентность совпали; для заказов с крипто-счётом (Crypto/xRocket включены) обычная кнопка «Оплачен» в админке **заблокирована** — только вебхук или **break-glass** `adm:paidbg` (супер-админ, аудит `adm:paid_break_glass`). |
| `pending_payment` | `expired` | Система (TTL job) | Инвойс просрочен; повторная оплата — новый заказ или повторный запрос счёта с кулдауном `PAYMENT_CHECKOUT_INVOICE_COOLDOWN_SECONDS` (`8-invoice-reissue`). |
| `pending_payment` | `refunded` | Только админ после факта от провайдера | Редкий кейс (ошибочный заказ до оплаты не нужен; обычно достаточно `expired`). |
| `paid` | `processing` | Админ | Начало выдачи. |
| `paid` | `refunded` | Админ + аудит | Сторно LAVA/Crypto / итог поддержки; **запрет** перевода в `completed`. |
| `paid` | `payment_disputed` | Админ | Временно; дальше только `refunded` или `paid` с записью в аудит. |
| `processing` | `payment_disputed` | Админ | Временно до разбора (аналогично из `paid`). |
| `processing` | `completed` | Админ | Выдача подтверждена; идемпотентность рефки — см. туду `3-fulfillment-idem`. |
| `processing` | `refunded` | Админ + аудит | Не смогли выдать, возврат согласован политикой. |
| `completed` | — | — | **Терминальный**; любой откат только офлайн-учётом, не статусом без миграции данных. |

**Инвариант:** `completed` **только** из `paid` или `processing`, никогда из `pending_payment` напрямую.

---

## 3. Краевые сценарии

### 3.1 Рефералка + Partner API

- Заказ с `source=api` и тем же `user_id`, что у покупателя в боте: реферал привязывается к **пользователю** в `users`; убедиться, что `referrer_id` не перезаписывается и **самореферал** запрещён (уже в `set_referrer_if_empty`).
- **Канон триггеров (v1):** и скидка приглашённому (`REF_BUYER_*` / `quote_product` при отсутствии своих `completed`), и комиссия рефереру (`REF_REFERRER_*` / `apply_completed_side_effects`) — обе привязаны к **первой выдаче** (`completed`), не к первой оплате (`paid`). Счётчики в профиле и Partner `GET /user/profile` — см. `users_repo.user_stats`.

### 3.2 Mix (баланс + LAVA / баланс + крипта)

- Внешняя часть к оплате (`amount_due_external`) должна совпадать с суммой в инвойсе LAVA / Crypto Pay / xRocket (USDT TRC20). Для Crypto Pay и xRocket поле `payload` счёта — канон **`SB1|order_id|due_kop`** (`docs/CRYPTO_PAY_SPEC.md` §3.1, `crypto_pay_payload.py`).
- Идемпотентность вебхука привязана к **остатку к доплате**, не к полной сумме заказа — регрессии: `tests/test_price_integrity_lite.py`, `tests/test_crypto_pay_payload.py`.

### 3.3 Двойной вебхук

- Один и тот же провайдерский ключ (`lava:invoice_id`, `cryptobot:invoice_id`) → повторный вызов даёт `duplicate`, статус заказа не «дрожит».

### 3.4 Автовыдача недоступна

- Сейчас: переход в `processing` вручную; сообщение пользователю из шаблона поддержки; SLA не обещать в боте без продукта.
- Целевая гибридная автовыдача (после оплаты, с ручным резервом) — **`37-auto-fulfill-hybrid`** в `docs/IMPLEMENTATION_PLAN_AND_TASKS.md` (пункт 37). В БД заказа: `fulfillment_mode` (`auto` \| `manual_only`), счётчики попыток и последняя ошибка — см. **§37.0** того же плана.

### 3.5 Сторно на стороне LAVA / Crypto Pay

- Продуктовая политика: **не автоматический** возврат клиенту из бота; фиксация факта — статус `refunded` или `payment_disputed` + запись в аудит (кто, когда, основание).
- **Супер-админ** в карточке заказа: кнопки «Сторно (refunded)», «Спор», при споре — «Снять спор → оплачен» (`adm:refund` / `adm:disp` / `adm:dispok`); покупателю — тексты из `buyer_order_notify.py`.
- Частичный возврат в v1 **не автоматизировать**; при необходимости — ручная корректировка и один согласованный терминальный статус.

### 3.6 Partner API: rate limit и «paid без движения»

- **Лимиты запросов** (`partner_api/rate_limit_middleware.py`, окно **60 с**, in-memory на процесс): отдельные потолки для **вебхуков** (по IP), для **`/v1` с `X-API-KEY`** (по хэшу ключа + IP) и для **прочих** путей вроде `/health` / OpenAPI (по IP). Переменные: `PARTNER_API_RATE_LIMIT_WEBHOOK_PER_MINUTE`, `PARTNER_API_RATE_LIMIT_API_PER_MINUTE`, `PARTNER_API_RATE_LIMIT_PUBLIC_PER_MINUTE`; **`0` = отключить** соответствующий класс лимита. Ответ **429** с телом `{"code":"rate_limited",…}`.
- Ответы вебхуков с **HTTP ≥ 400** дополнительно пишутся в лог уровня **WARNING** (`partner_api_webhook_error`).
- **Зависшие оплаченные заказы:** фоновый цикл в боте (`bot/services/stuck_orders_monitor.py`) раз в `STUCK_PAID_CHECK_INTERVAL_SECONDS` ищет заказы в **`paid`** или **`processing`**, у которых `updated_at` старше **`STUCK_PAID_ALERT_HOURS`** часов, и логирует **WARNING** со списком id (до 200 строк за проход). SQL: `orders_repo.list_order_ids_stuck_paid_or_processing`. Если **`STUCK_PAID_ALERT_HOURS=0`**, этот шаг пропускается.
- **Зависшие только в `processing`:** при **`STUCK_PROCESSING_ALERT_MINUTES` > 0** в том же цикле дополнительно проверяются заказы в **`processing`** без обновления дольше N минут (`orders_repo.list_order_ids_stuck_processing_only`), с отдельным ops-алертом. Фоновый цикл **запускается**, если **`STUCK_PAID_ALERT_HOURS` > 0 или `STUCK_PROCESSING_ALERT_MINUTES` > 0** (`bot/main.py`).
- **Алерт операторам при сбое create iStar:** после отката в `paid` (`auto_fulfill_runner`) при **`AUTO_FULFILL_FAILURE_ALERTS_ENABLED=true`** и **`ALERTS_ENABLED=true`** уходит `send_alert` (дедуп по заказу).
- **Очередь внимания в боте:** команда **`/admqueue`** (только `ADMIN_IDS`) — список заказов `paid` с непустой `fulfillment_last_error` или `processing` без движения дольше **`OPERATOR_QUEUE_PROCESSING_IDLE_MINUTES`** (по умолчанию 30).

### 3.7 Feature flags (поэтапный прод)

- **`CRYPTO_PAY_ENABLED`** (+ токен Crypto Pay), **`XROCKET_PAY_ENABLED`** — включают счёт и вебхуки; при `false` остаётся фиат/ручной сценарий по текущей логике бота.
- **`AUTO_FULFILL_ENABLED`** и дочерние **`AUTO_FULFILL_*`** — автоматическая выдача после `paid` (воркер + iStar); при `false` — только ручная цепочка оператора. Порядок смоука: `docs/AUTO_FULFILL_SMOKE.md`, спека плана п.37.

---

## 4. Порядок внедрения (согласовано)

1. Инварианты БД и **явный автомат статусов** (`3-state-machine`).  
2. Платежи: LAVA + только ₽ в UI (`1-*`; `1-rub-only` — без UAH/BYN в подсказках).  
3. Crypto Pay (`2-*`).  
4. Выдача и админка (`4-*`).  
5. Рефералка и меню (`5-*`, `6-*`).  
6. Операционные задачи `8-*` (без отменённого cron-бэкапа).

---

## 5. Ссылки

- Политика возвратов в тексте бота: `bot/services/marketing.py` (`payment_faq_html`, `faq_comprehensive_html`).
- Деплой и ручной бэкап: `docs/ML_SYSTEM_HANDOFF_FINAL.md`.

## 6. Реализация в коде (переходы)

Допустимые переходы для существующих статусов проверяются в `bot/services/order_status.py` (`can_transition` / `require_transition`).  
`orders_repo.update_status` загружает заказ и отклоняет недопустимый переход; `provider_mark_paid` перед `paid` вызывает `require_transition`. Терминальные для вебхука оплаты: `paid`, `completed`, `refunded` (`provider_mark_paid` не переводит из них в `paid`). Статусы `expired`, `refunded`, `payment_disputed` — в матрице §2 и в `order_status.py`.

**Баланс / mix (`bal`, `mixfi`, `mixcr`):** в `create_paid_order_from_balance` и `create_order_with_balance_partial` после `BEGIN IMMEDIATE` вызывается `balance_repo.ensure_balance_user_row`, списание — одним `UPDATE … SET balance_rub = round(balance_rub - ?, 2) WHERE … AND balance_rub + 1e-6 >= ?` с проверкой `rowcount`. Зачисление топапа — `approve_topup` в одной транзакции `BEGIN IMMEDIATE`. Вспомогательные `add_balance` / `charge_balance` — отдельные `BEGIN IMMEDIATE` на вызов (не вкладывать в уже открытую транзакцию).

**Лимиты:** `balance_repo.create_topup_request` в одной транзакции `BEGIN IMMEDIATE` проверяет сумму (`TOPUP_MIN_RUB` / `TOPUP_MAX_RUB`), число заявок со статусом `pending` (`TOPUP_MAX_PENDING_PER_USER`, 0 = без лимита) и минимальный интервал между заявками (`TOPUP_MIN_INTERVAL_SECONDS`, 0 = выкл.). Лимит заказов `pending_payment` на пользователя — `orders_repo.require_pending_order_cap` (`MAX_PENDING_PAYMENT_ORDERS_PER_USER`, 0 = без лимита): перед созданием заказа в боте (фиат/крипта), внутри `create_order_with_balance_partial` при остатке к доплате и в `create_order_partner_api` перед вставкой.

**Идемпотентность выдачи:** после `completed` вызывается `order_flow.apply_completed_side_effects` (в админке только при первом переходе в `completed`). Внутри — `BEGIN IMMEDIATE`, защита по `orders.fulfillment_applied_at` и атомарный `UPDATE orders … WHERE commission_paid = 0` перед начислением `ref_balance_rub`. Повторный переход `completed`→`completed` в автомате статусов запрещён.

**Админ-операции:** при непустом `SUPER_ADMIN_IDS` с пересечением с `ADMIN_IDS` остальные админы — «операторы»: только `adm:proc`, без «Оплачен»/«Выдан», без `top:ok`, без завершения/отмены выкупа (`sel:done`/`sel:can`), без создания/активации/массового выключения конкурсов. Все успешные `adm:*`, `top:ok`, `sel:*`, `contest:*` пишутся в `admin_audit_log` (JSON в `payload_json`).
