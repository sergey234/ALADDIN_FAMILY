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
