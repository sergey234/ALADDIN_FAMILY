# ML Handoff: автовыдача Stars/Premium через Fragment (iStar)

> **Формат:** машиночитаемый план для другой ML-системы / агента.  
> **Репозиторий:** `ALADDIN_NEW/mobile_apps/ALADDIN_iOS/telegram_stars_shop_bot/`  
> **Прод:** `149.154.65.180`, `/opt/aladdin-telegram-shop-bot`, бот `@AiMonkeyStars_bot`  
> **Домен Partner API:** `https://aladdin-ai.ru/v1/` → `127.0.0.1:8090`

---

## META

| Поле | Значение |
|------|----------|
| `goal` | После оплаты в LAVA (₽) бот автоматически покупает Stars/Premium на Fragment и выдаёт на `@username` |
| `procurement_cost_stars_usd` | ~0.015 USD / Star (ориентир закупки на Fragment) |
| `fulfillment_provider` | iStar Partner API → Fragment.com |
| `wallet_asset` | TON (отдельный кошелёк магазина, пополняется вручную) |
| `stage_wallet_accounts` | **ПОСЛЕДНИЙ** этап — не блокирует работу по коду и подготовке сервера |

---

## ALREADY_IMPLEMENTED (не переписывать)

| Компонент | Путь |
|-----------|------|
| iStar HTTP client | `bot/services/istar_fulfill_client.py` |
| Auto-fulfill runner | `bot/services/auto_fulfill_runner.py` |
| Eligibility policy | `bot/services/auto_fulfill_policy.py` |
| Worker entrypoint | `partner_api/auto_fulfill_worker.py` |
| iStar webhook | `partner_api/routers/istar_webhook.py` → `POST /v1/payments/istar-webhook` |
| systemd unit template | `docs/auto-fulfill-worker.service` |
| Smoke checklist | `docs/AUTO_FULFILL_SMOKE.md` |
| Admin manual/auto controls | `bot/handlers/admin.py`, `bot/services/admin_order_ff.py` |
| Stuck orders alerts | `bot/services/stuck_orders_monitor.py` |
| Create-failed ops alert | `notify_ops_auto_fulfill_create_failed` in `auto_fulfill_runner.py` |
| Idempotent completed | `fulfillment_applied_at` in `bot/services/order_flow.py` |
| Username capture UX | `shop.py` FSM + `fulfillment_recipient.py` |
| LAVA payments | настроено на проде |

---

## GAP_ANALYSIS (что доделать)

### Правила автовыдачи — сверка с требованием заказчика

| Правило | Требование | В коде сейчас | Действие |
|---------|------------|---------------|----------|
| Минимум Stars | 50 | ✅ `stars_quantity_below_minimum` | — |
| Premium месяцы | **1 / 3 / 6 / 12** | ❌ только **3 / 6 / 12** (`premium_months_invalid` для 1) | **Код:** разрешить `duration_months=1` в `auto_fulfill_policy.py` + тест |
| Лимит ₽ | `AUTO_FULFILL_MAX_ORDER_RUB` | ✅ | На проде выставить `50000` |
| Попытки | до 5 | ✅ | — |
| Получатель `@username` | обязателен | ✅ search + `missing_recipient_username` | — |
| Ручной режим | админ `manual_only` | ✅ | — |

### Риски — сверка

| Риск | В коде | Пробел | Действие |
|------|--------|--------|----------|
| Закончился TON | ❌ | Нет мониторинга баланса / паузы авто | **Код:** `istar_wallet_balance` (если есть в API) или детект `insufficient` в ошибке create → `send_alert` + skip batch; env `ISTAR_MIN_TON_BALANCE_ALERT` |
| Курс TON / маржа | частично | `price_usd` в YAML, `USD_RUB_RATE` | **Контент:** пересчитать `products.yaml`; **опц.** runbook «раз в неделю» |
| Неверный @username | ✅ | search_failed, attempts, operator | — |
| iStar/Fragment недоступен | частично | worker retry; `STUCK_PROCESSING_ALERT_MINUTES=0` на проде | **Опс:** включить `STUCK_PROCESSING_ALERT_MINUTES=30`, `STUCK_PAID_ALERT_HOURS=24` |
| Двойная выдача | ✅ | webhook + `fulfillment_applied_at` | — |
| Долгий `processing` | ✅ код есть | флаг выключен | **Опс:** `STUCK_PROCESSING_ALERT_MINUTES=30` |
| Нет ключей при включённом авто | частично | warning в runner | **Код:** startup warning в `main.py` если `AUTO_FULFILL_ENABLED` без `ISTAR_API_KEY` |

---

## TASK_ORDER (этапы; кошелёк — в конце)

### PHASE_A — Код и тесты (без секретов, можно сейчас)

| ID | Задача | Файлы | DoD |
|----|--------|-------|-----|
| `A1` | Premium **1 мес.** в автовыдаче | `auto_fulfill_policy.py`, `test_auto_fulfill_policy.py` | `duration_months=1` → eligible |
| `A2` | Gate «низкий TON / нет средств» | новый `istar_wallet_monitor.py` или расширение `istar_fulfill_client.py`, hook в `auto_fulfill_runner.py` | при низком балансе: skip batch + ops alert (dedupe) |
| `A3` | Startup validation | `bot/main.py` | WARNING если авто включено без ISTAR / без webhook secret |
| `A4` | Пересчёт `price_usd` | **отложено** — цены в каталоге без изменений по решению заказчика |
| `A5` | Обновить `env.example` | блок AUTO_FULFILL + STUCK + ISTAR | рекомендуемые прод-значения с комментариями |
| `A6` | Расширить smoke | `docs/AUTO_FULFILL_SMOKE.md` | негативные кейсы, premium_1, алерты |
| `A7` | pytest | `tests/` | зелёный `pytest -q` |
| `A8` | Деплой кода на прод **без** включения авто | `ML_SYSTEM_HANDOFF_FINAL.md` | health 8090 OK, флаги пока false |

### PHASE_B — Подготовка сервера (без ключей iStar)

| ID | Задача | DoD |
|----|--------|-----|
| `B1` | Скопировать unit | `cp docs/auto-fulfill-worker.service /etc/systemd/system/` | файл на сервере |
| `B2` | **Не** `enable` worker до ключей | unit installed, `systemctl is-enabled` = disabled |
| `B3` | Проверить nginx | `POST https://aladdin-ai.ru/v1/payments/istar-webhook` без подписи → **401** (не 503) |
| `B4` | Подготовить merge `.env` | шаблон ниже, без реальных секретов в git |

### PHASE_C — Включение на проде (нужны `ISTAR_*` — см. PHASE_D последним)

| ID | Задача | DoD |
|----|--------|-----|
| `C1` | Записать `.env` на сервере | см. `ENV_PROD_TEMPLATE` |
| `C2` | `systemctl daemon-reload && systemctl enable --now auto-fulfill-worker` | active, логи `auto_fulfill_worker_cycle` |
| `C3` | Рестарт `aladdin-partner-api`, `aladdin-telegram-bot` | active |
| `C4` | В кабинете iStar: webhook URL + secret | совпадает с `.env` |

### PHASE_D — Смоук на проде

| ID | Шаг | Ожидание |
|----|-----|----------|
| `D1` | Заказ 100 Stars, свой `@username`, LAVA | `paid` |
| `D2` | Воркер / ожидание 60 с | `processing`, `fulfillment_provider_ref` заполнен |
| `D3` | Webhook iStar `order.completed` | `completed`, уведомление покупателю |
| `D4` | Stars в Telegram | зачислены |
| `D5` | Негатив: неверный username | остаётся `paid`, ошибка в карточке, алерт ops |
| `D6` | Premium 1 мес. (после A1) | автовыдача или ручной fallback по политике |
| `D7` | `/admqueue` | заказы в очереди оператора видны |

### PHASE_E — Аккаунты и кошелёк (**ПОСЛЕДНИЙ**, после готовности кода и смоук-плана)

| ID | Задача | DoD |
|----|--------|-----|
| `E1` | Аккаунт [fragment.com](https://fragment.com) | верифицирован |
| `E2` | Отдельный TON-кошелёк магазина | создан, не смешан с личным |
| `E3` | Регистрация iStar Partner | см. **`docs/ISTAR_ACCESS.md`** (кабинет: istar.fragmentapi.com, зеркала: fragmentapi.com, istar.tg) |
| `E4` | Привязка кошелька в iStar | `ISTAR_WALLET_TYPE=TON` |
| `E5` | Пополнение TON | резерв по нагрузке (ориентир 50–100 TON старт) |
| `E6` | Выдать `ISTAR_API_KEY`, `ISTAR_WEBHOOK_SECRET` | в `shared/.env` → PHASE_C |

---

## ENV_PROD_TEMPLATE

```env
# --- Автовыдача Fragment (iStar) ---
AUTO_FULFILL_ENABLED=true
AUTO_FULFILL_STARS_ENABLED=true
AUTO_FULFILL_PREMIUM_ENABLED=true
AUTO_FULFILL_MAX_ORDER_RUB=50000
AUTO_FULFILL_MAX_ATTEMPTS=5
AUTO_FULFILL_POLL_INTERVAL_SECONDS=60
AUTO_FULFILL_FAILURE_ALERTS_ENABLED=true

ISTAR_API_KEY=<из кабинета iStar — PHASE_E>
ISTAR_API_BASE=https://v1.fragmentapi.com/api/v1/partner
ISTAR_WALLET_TYPE=TON
ISTAR_WEBHOOK_SECRET=<из кабинета iStar — PHASE_E>

# --- Мониторинг очереди (рекомендуется включить) ---
STUCK_PAID_ALERT_HOURS=24
STUCK_PAID_CHECK_INTERVAL_SECONDS=3600
STUCK_PROCESSING_ALERT_MINUTES=30
OPERATOR_QUEUE_PROCESSING_IDLE_MINUTES=30

# --- Опционально после A2 ---
# ISTAR_MIN_TON_BALANCE_ALERT=20
```

**Webhook URL для кабинета iStar:**
```
https://aladdin-ai.ru/v1/payments/istar-webhook
```

**Worker:**
```bash
systemctl enable --now auto-fulfill-worker.service
journalctl -u auto-fulfill-worker.service -f
```

---

## ORDER_STATE_MACHINE (reference)

```
pending_payment → paid → processing → completed
                    ↑         │
                    └─────────┘  (create_failed revert)
manual_only: worker skips
max_attempts: worker skips → operator
```

---

## ACCEPTANCE_CRITERIA

- [ ] 95% тестовых Stars-заказов: `paid` → `completed` < 5 мин без оператора
- [ ] Premium 1/3/6/12 в авто (после A1)
- [ ] При пустом TON: авто не списывает, админы получают алерт
- [ ] Двойной webhook не дублирует выдачу / рефку
- [ ] `pytest -q` зелёный
- [ ] Доки: этот файл + `AUTO_FULFILL_SMOKE.md` актуальны

---

## COMMANDS

```bash
# Локально
cd telegram_stars_shop_bot && python3 -m pytest -q

# Один цикл воркера на сервере
/opt/aladdin-telegram-shop-bot/venv/bin/python3 -m partner_api.auto_fulfill_worker --limit 5

# Деплой (из ALADDIN_iOS)
# см. .cursor/rules/telegram-shop-bot-deploy.mdc и ML_SYSTEM_HANDOFF_FINAL.md §2
```

---

## OUT_OF_SCOPE

- Прямая интеграция с fragment.com без iStar (headless/cookies) — не в текущем плане
- Автопополнение TON с биржи — только ручное
- Возврат ₽ после успешной выдачи — по политике «выдан — не возврат»

---

*Создано: 2026-06-10. Обновлять при закрытии задач A1–E6.*
