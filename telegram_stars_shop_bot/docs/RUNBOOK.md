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
