# Separate Server Deployment (Bot isolated from ALADDIN mobile/backend)

Цель: держать Telegram Shop Bot в полностью отдельном дереве на сервере, не затрагивая `/opt/aladdin-backend`.

## Текущее раздельное размещение (уже создано)

- Основной ALADDIN backend: `/opt/aladdin-backend` (не изменяется этим деплоем).
- Telegram Shop Bot: `/opt/aladdin-telegram-shop-bot`
  - `releases/<timestamp>/telegram_stars_shop_bot`
  - `current_release` (symlink)
  - `current_app` (symlink)
  - `shared/.env`
  - `venv/`
  - `logs/`

## Доставка кода (rsync / git / scp, симлинки)

Полная пошаговая инструкция: подраздел **«Доставка кода на production (канон)»** в `docs/ML_SYSTEM_HANDOFF_FINAL.md` (варианты A: `rsync` в `releases/<timestamp>/` + `current_release` / `current_app`, B: `git pull` в `current_app`, C: точечный `scp`; исключения для `data/`, `venv/`, `shared/.env`; рестарт трёх unit’ов и `curl` health).

## Раздельные systemd-юниты

- `aladdin-telegram-bot.service`
- `aladdin-partner-api.service`
- `aladdin-webhook-worker.service`

Эти юниты не пересекаются с `aladdin-backend.service`.

## Обязательная настройка .env (перед запуском bot/api)

Файл: `/opt/aladdin-telegram-shop-bot/shared/.env`

Минимально обязательные переменные:
- `BOT_TOKEN=...`
- `ADMIN_IDS=123,456`
- `API_KEY_PEPPER=...`
- `PAYMENT_WEBHOOK_SECRET=...`

### Крипто (Crypto Pay + xRocket) и авто `paid`

Чеклист переменных и URL вебхуков для Partner API: **`docs/CRYPTO_PAY_SPEC.md`** (раздел **«0. Прод: shared/.env + вебхуки»**). Кратко:

- В `shared/.env`: `CRYPTO_PAY_ENABLED=true`, `CRYPTO_PAY_API_TOKEN=` (не BOT_TOKEN); при xRocket — `XROCKET_PAY_ENABLED=true`, `XROCKET_PAY_API_KEY=`; задать **`USDT_RUB_RATE`** или **`USD_RUB_RATE`** как резерв курса.
- В кабинетах провайдеров указать публичные HTTPS URL:  
  `https://<ваш-хост>/v1/payments/crypto-pay-webhook` и  
  `https://<ваш-хост>/v1/payments/xrocket-webhook`  
  (тот же хост/прокси, что обслуживает `aladdin-partner-api`).
- После смены секретов или URL: `sudo systemctl restart aladdin-partner-api.service`, затем смоук из спеки §0.3.

### LAVA (₽): что в `.env`, а что в кабинете LAVA

В **`shared/.env`** только техническое подключение магазина к API LAVA и вебхуку Partner API: `LAVA_SHOP_ID`, `LAVA_SECRET_KEY`, `LAVA_HOOK_URL` (публичный URL до `…/v1/payments/lava-webhook`), `LAVA_WEBHOOK_ADDITIONAL_SECRET` (проверка входящего POST), плюс опционально `LAVA_SUCCESS_URL` / `LAVA_FAIL_URL`, `LAVA_INCLUDE_SERVICES` и т.д.

**Банковский счёт, карта для выручки, график выплат** задаются в **личном кабинете LAVA** (договор, реквизиты мерчанта) — в переменные бота это не дублируется. После оплаты на странице LAVA заказ в боте переходит в **`paid`** по вебхуку; дальше выдача товара — сценарий оператора в админке бота («В работе» → «Выдан»).

## Команды включения после заполнения .env

```bash
sudo systemctl restart aladdin-telegram-bot.service
sudo systemctl restart aladdin-partner-api.service
sudo systemctl restart aladdin-webhook-worker.service

sudo systemctl status aladdin-telegram-bot.service --no-pager
sudo systemctl status aladdin-partner-api.service --no-pager
sudo systemctl status aladdin-webhook-worker.service --no-pager
```

Проверка API:

```bash
curl -s -S -m 8 http://127.0.0.1:8090/health
```

## Логи

- `/opt/aladdin-telegram-shop-bot/logs/bot.log`
- `/opt/aladdin-telegram-shop-bot/logs/partner_api.log`
- `/opt/aladdin-telegram-shop-bot/logs/webhook_worker.log`

## Zero-touch правило для мобильного приложения/ALADDIN

При работе с ботом не изменять:
- `/opt/aladdin-backend/**`
- `aladdin-backend.service`
- маршруты/файлы мобильного приложения ALADDIN

Любые обновления Telegram Shop Bot делать только внутри:
- `/opt/aladdin-telegram-shop-bot/**`
- `aladdin-telegram-*.service`
