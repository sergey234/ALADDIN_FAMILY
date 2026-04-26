# Runbook: Telegram Shop Bot + Partner API

## 1. Окружение

- **Python** 3.9+ (рекомендуется 3.11 в CI).
- Скопируйте `env.example` → `.env` в каталоге `telegram_stars_shop_bot/`.
- Обязательно: `BOT_TOKEN`, `ADMIN_IDS`, для Partner API — **`API_KEY_PEPPER`**.
- Опционально: `DATABASE_PATH` (иначе `data/shop.db` относительно проекта), `PARTNER_API_CORS_ORIGINS`, `SUPPORT_URL` / `SUPPORT_USERNAME`.

## 2. Установка

```bash
cd telegram_stars_shop_bot
python3 -m pip install -r requirements.txt
```

Для разработки и тестов:

```bash
python3 -m pip install -r requirements-dev.txt
```

## 3. Запуск бота

```bash
cd telegram_stars_shop_bot
python3 -m bot.main
```

(или точка входа, которую вы используете для polling.)

## 4. Запуск Partner API

```bash
cd telegram_stars_shop_bot
python3 -m partner_api.main
```

По умолчанию порт **8090**. На проде — **TLS только за reverse-proxy** (nginx, Caddy, cloud LB).  
Документация API: `http://<хост>:8090/docs`, контракт: `docs/openapi_v1.yaml`.

## 5. Резервная копия БД

Файл по умолчанию: `telegram_stars_shop_bot/data/shop.db` (или путь из `DATABASE_PATH`).

```bash
cp data/shop.db "data/shop_backup_$(date +%Y%m%d_%H%M).db"
```

Храните бэкапы вне сервера приложения.

## 6. Smoke после деплоя

1. `/start` — экран 1 → «Далее» → хаб из 10 кнопок.
2. **Купить Stars** — открывается каталог (или сообщение о пустом каталоге).
3. **Пополнить баланс** — создаётся заявка, админу приходит сообщение.
4. **Partner API** — `GET /health` → `{"status":"ok"}`; с ключом `GET /v1/user/profile` → 200.
5. Создать тестовый заказ через бота или API — админу приходит уведомление с кнопками.

Чеклист приёмки: `docs/ACCEPTANCE_CHECKLIST.md`.

## 7. Логи

- По умолчанию текстовый `logging.INFO`.
- События бизнес-логики дублируются через `bot.logutil.slog` (ключ=значение в одной строке).
- **Не логировать** значение `X-API-KEY` и сырой API-ключ.

## 8. Sentry (опционально)

Зависимость уже в `requirements.txt`. Включение:

- `SENTRY_DSN` — не коммитить в git.
- Опционально: `SENTRY_ENVIRONMENT`, `SENTRY_TRACES_SAMPLE_RATE` (по умолчанию `0.0`).
- Инициализация в коде: `bot.main` и `partner_api.main` (lifespan); заголовки `X-API-KEY` и др. фильтруются в `bot/sentry_util.py`.

## 9. Автоплатежи v1 (входящий вебхук провайдера)

Оркестратор или эквайринг после успешной оплаты вызывает Partner API (тот же процесс, что и `/v1`, отдельная аутентификация от `X-API-KEY`):

- **URL:** `POST /v1/payments/provider-webhook`
- **Секрет:** переменная окружения `PAYMENT_WEBHOOK_SECRET` (длинная случайная строка на сервере).
- **Подпись:** hex `HMAC-SHA256(PAYMENT_WEBHOOK_SECRET, raw_body)` в заголовке `X-Payment-Signature` (допустим префикс `sha256=`).
- **Тело JSON:** `idempotency_key` (строка 8–128 символов, уникальная от провайдера), `order_id`, `action`: `"mark_paid"`.
- **Эффект:** заказ в статусе `pending_payment` переводится в `paid`; повтор с тем же `idempotency_key` — ответ `duplicate`; если уже `paid`/`completed` — `already_terminal` без ошибки.
- Дальнейшая выдача Stars по-прежнему через админку (`processing` / `completed`) или вашу автоматизацию.

## 10. Исходящие вебхуки партнёру (`order.status_changed`)

- Настройка: `PUT /v1/webhooks/subscription` с `X-API-KEY` (тело: `webhook_url` https, опционально `rotate_secret`; пустой `webhook_url` — отключить; поле `webhook_url` можно не слать, чтобы только ротировать секрет).
- **Событие:** при смене статуса заказа с `source=api` после действий админа или после успешного `mark_paid` из раздела 9.
- **Запрос к URL партнёра:** `POST`, JSON с полями `event`, `order_id`, `status`, `previous_status`, `external_ref`, `occurred_at`; заголовок `X-Partner-Signature: sha256=<hmac>` от тела с ключом `signing_secret` (префикс `whsec_`), выданным один раз при настройке или ротации.
- Контракт также в `docs/openapi_v1.yaml`.

### Периодическая доставка очереди webhook (обязательно для прод)

Сервис пишет события в таблицу `outbound_webhook_events`. Для гарантированной доставки запускайте worker:

```bash
cd telegram_stars_shop_bot
python3 -m partner_api.webhook_worker --limit 200
```

Варианты эксплуатации:

- **cron (раз в минуту):**
  `* * * * * cd /opt/telegram_stars_shop_bot && /usr/bin/python3 -m partner_api.webhook_worker --limit 200 >> /var/log/aladdin-webhook-worker.log 2>&1`
- **systemd (долгоживущий режим):**
  `python3 -m partner_api.webhook_worker --forever --sleep-sec 30 --limit 200`

Готовые шаблоны:
- `docs/webhook-worker.service`
- `docs/webhook-worker.crontab`
- пошаговая установка: `docs/DEPLOY_WEBHOOK_WORKER.md`

## 10.1 Автовыдача (обязательно для 100% automation)

`partner_api.webhook_worker` доставляет исходящие webhook партнёрам, но **не** делает выдачу Stars/Premium.
Для автовыдачи нужен отдельный процесс:

```bash
cd /opt/aladdin-telegram-shop-bot/current_app
/opt/aladdin-telegram-shop-bot/venv/bin/python3 -m partner_api.auto_fulfill_worker --forever --limit 10
```

Рекомендуемый systemd unit:
- `docs/auto-fulfill-worker.service`

Установка:

```bash
cp /opt/aladdin-telegram-shop-bot/current_app/docs/auto-fulfill-worker.service /etc/systemd/system/auto-fulfill-worker.service
systemctl daemon-reload
systemctl enable --now auto-fulfill-worker.service
systemctl status --no-pager auto-fulfill-worker.service
```

Смоук:

```bash
journalctl -u auto-fulfill-worker.service -n 100 --no-pager
```

Ожидание: в логах есть `auto_fulfill_worker_cycle stats=...`.

## 11. Break-glass (`adm:paidbg`) — боевой чеклист

`adm:paidbg` использовать только при недоступном/потерянном вебхуке провайдера и подтверждённом факте оплаты.

Проверить перед нажатием:

1. Провайдер и канал оплаты подтверждены (Crypto Pay/xRocket/LAVA).
2. Есть внешний идентификатор счёта/платежа (если доступен) и сумма совпадает с заказом.
3. Есть ссылка на доказательство (`evidence_ref`: тикет/скрин/tx hash/receipt).
4. Если сумма выше `BREAK_GLASS_TWO_EYES_THRESHOLD_RUB` и супер-админов 2+, применить правило «вторые глаза».

Аудит для каждого `adm:paidbg` (обязательно, пишется в `admin_audit_log.payload_json`):

- `reason_code`
- `provider`
- `external_invoice_id`
- `evidence_ref`
- `two_eyes_required`

Операционный контроль:

- На каждый `adm:paidbg` отправляется ops-алерт.
- Периодический отчёт по break-glass: `BREAK_GLASS_REPORT_INTERVAL_SECONDS` / `BREAK_GLASS_REPORT_LOOKBACK_HOURS`.

## 12. Partner API rate-limit: memory/redis + edge Nginx

### 12.1 Режимы backend лимитов

- `PARTNER_API_RATE_LIMIT_BACKEND=memory` — локальные лимиты на процесс (подходит для 1 инстанса API).
- `PARTNER_API_RATE_LIMIT_BACKEND=redis` — общий лимит между несколькими инстансами API.
- Если Redis недоступен, код автоматически делает fallback на `memory` и пишет warning в лог.

Переменные:

- `PARTNER_API_RATE_LIMIT_API_PER_MINUTE`
- `PARTNER_API_RATE_LIMIT_WEBHOOK_PER_MINUTE`
- `PARTNER_API_RATE_LIMIT_PUBLIC_PER_MINUTE`
- `REDIS_URL` или связка `REDIS_HOST` / `REDIS_PORT` / `REDIS_DB` / `REDIS_PASSWORD`

### 12.2 Минимальный Redis smoke (на сервере)

```bash
# Проверка доступности Redis
redis-cli -u "$REDIS_URL" ping

# Проверка API
curl -s -S -m 8 http://127.0.0.1:8090/health
```

Ожидание: `PONG` и `{"status":"ok"}`.

### 12.3 Smoke "2 воркера -> 1 общий лимит" (ручной)

1. Поднимите 2 процесса Partner API с одинаковым `REDIS_URL` и `PARTNER_API_RATE_LIMIT_BACKEND=redis`.
2. Временно установите, например, `PARTNER_API_RATE_LIMIT_PUBLIC_PER_MINUTE=5`.
3. Отправьте 6+ запросов на `/health` через оба инстанса суммарно.
4. Ожидание: суммарно после 5 запросов получаете `429` (общий счётчик).

Пример генерации нагрузки:

```bash
for i in {1..8}; do curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8090/health; done
```

### 12.4 Edge rate-limit в Nginx (до Python/FastAPI)

Пример (адаптируйте путь include под ваш nginx):

```nginx
limit_req_zone $binary_remote_addr zone=shop_wh:10m rate=20r/s;
limit_req_zone $binary_remote_addr zone=shop_api:10m rate=15r/s;

server {
    # Webhook endpoints
    location ~ ^/v1/payments/(lava-webhook|crypto-pay-webhook|xrocket-webhook|provider-webhook|istar-webhook)$ {
        limit_req zone=shop_wh burst=40 nodelay;
        proxy_pass http://127.0.0.1:8090;
    }

    # API endpoints
    location /v1/ {
        limit_req zone=shop_api burst=30 nodelay;
        proxy_pass http://127.0.0.1:8090;
    }
}
```

После изменения nginx:

```bash
nginx -t && systemctl reload nginx
```

### 12.5 Мониторинг Redis для лимитов

- Проверять память: `redis-cli -u "$REDIS_URL" INFO memory`
- Проверять keyspace/TTL: `redis-cli -u "$REDIS_URL" INFO keyspace`
- Отслеживать warning в логах:
  - `rate_limit_redis_connect_failed_fallback_memory`
  - `rate_limit_redis_runtime_failed_fallback_memory`

## 13. Ops watchdog + heartbeat (alerts)

Цель: дежурный админ получает `PROBLEM`/`RECOVERY`, а при нормальной работе — heartbeat каждые 30 минут.

Минимальные env в `shared/.env`:

- `ALERTS_ENABLED=true`
- `ALERT_TELEGRAM_BOT_TOKEN=<ops_bot_token>`
- `ALERT_TELEGRAM_CHAT_ID=<ops_chat_id>`
- `ALERT_COOLDOWN_SECONDS=300`
- Гибрид выдачи (оператор): при необходимости задать `STUCK_PROCESSING_ALERT_MINUTES` (отдельный алерт по «зависшему» `processing`), `OPERATOR_QUEUE_PROCESSING_IDLE_MINUTES` (порог для `/admqueue`), `AUTO_FULFILL_FAILURE_ALERTS_ENABLED` (алерт при откате после ошибки create iStar). В боте у админов: команда **`/admqueue`** — список заказов, требующих внимания.
- `OPS_WATCHDOG_ENABLED=true`
- `OPS_HEARTBEAT_INTERVAL_SECONDS=1800`

Дополнительно:

- `OPS_WATCHDOG_LOG_SCAN_LINES=300`
- `OPS_WATCHDOG_ERROR_BURST_THRESHOLD=5`
- `OPS_WATCHDOG_WEBHOOK_BACKLOG_WARN=50`

Что проверяет watchdog:

- `CRITICAL`: любой из unit'ов `aladdin-telegram-bot.service`, `aladdin-partner-api.service`, `aladdin-webhook-worker.service` не `active`; `/health` не `200`/`{"status":"ok"}`.
- `WARNING`: burst ошибок в `bot.log`, markers Redis fallback->memory, рост backlog `outbound_webhook_events (pending/failed)`.
- `INFO`: heartbeat `OK: ops heartbeat`.

Установка timer (на сервере):

```bash
cp /opt/aladdin-telegram-shop-bot/current_app/docs/ops-watchdog.service /etc/systemd/system/ops-watchdog.service
cp /opt/aladdin-telegram-shop-bot/current_app/docs/ops-watchdog.timer /etc/systemd/system/ops-watchdog.timer
systemctl daemon-reload
systemctl enable --now ops-watchdog.timer
systemctl status --no-pager ops-watchdog.timer
```

Ручной прогон:

```bash
cd /opt/aladdin-telegram-shop-bot/current_app
/opt/aladdin-telegram-shop-bot/venv/bin/python -m bot.services.ops_watchdog
```
