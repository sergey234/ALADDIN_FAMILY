# Shop Bot — один инстанс (канон)

**Бот:** `@AiMonkeyStars_bot`  
**Проблема 2026-06-30:** два `getUpdates` (MAIN + Contabo) → `TelegramConflictError`, старое меню, разъехавшиеся `shop.db`.

## Правило (обязательно)

| Роль | Сервер | IP | `aladdin-telegram-bot` |
|------|--------|-----|-------------------------|
| **Polling (Telegram)** | Contabo | `185.225.233.150` | **active + enabled** + файл `SHOP_BOT_POLLING_HOST` |
| API / nginx proxy | MAIN | `149.154.65.180` | **disabled** + systemd `ConditionPathExists` (без маркера не стартует) |

На MAIN работают только:
- `aladdin-partner-api.service`
- `aladdin-webhook-worker.service`
- `ops-watchdog.timer` (с `SHOP_BOT_POLLING_ENABLED=false`)

## Переменные `.env`

| Хост | `SHOP_BOT_POLLING_ENABLED` |
|------|----------------------------|
| Contabo | `true` |
| MAIN | `false` |

Иначе ops-watchdog на MAIN шлёт ложный CRITICAL «bot not active» и кто-то может снова включить второй инстанс.

## Деплой

```bash
./scripts/deploy_prod.sh
./scripts/verify_single_bot.sh
```

**Никогда** не создавать на MAIN файл `SHOP_BOT_POLLING_HOST` и не делать:
```bash
systemctl start aladdin-telegram-bot   # на MAIN не поднимется без маркера
```

## Симлинки (частая ошибка)

```bash
# ПРАВИЛЬНО:
ln -sfn "${ROOT}/releases/${TS}" "${ROOT}/current_release"
ln -sfn "${ROOT}/releases/${TS}/telegram_stars_shop_bot" "${ROOT}/current_app"

# НЕПРАВИЛЬНО (код в releases, бот на старом релизе):
ln -sfn "${ROOT}/releases/${TS}/telegram_stars_shop_bot" "${ROOT}/current_release/telegram_stars_shop_bot"
```

## Откуда бот берёт данные

```
Telegram → bot.main (Contabo)
              ├─ current_app/bot/products.yaml   # меню Stars
              ├─ shared/.env                     # курс, флаги
              └─ data/shop.db                    # заказы (только Contabo — SSOT)
```

## Быстрая проверка

```bash
ssh contabo 'systemctl is-active aladdin-telegram-bot && pgrep -cf bot.main'
ssh main 'systemctl is-enabled aladdin-telegram-bot; pgrep -af bot.main || echo OK:none'
```

Ожидание: Contabo `active` + `1` процесс; MAIN `masked` + нет `bot.main`.
