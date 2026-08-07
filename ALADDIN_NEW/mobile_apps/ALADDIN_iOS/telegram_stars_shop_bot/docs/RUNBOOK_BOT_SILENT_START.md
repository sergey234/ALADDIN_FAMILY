# Runbook: Start молчит / бот глухой к Telegram

**Хост:** Contabo `185.225.233.150` · unit `aladdin-telegram-bot.service`  
**Канон:** getMe FAIL ≠ крутить restart-loop.

## 1. Быстрый прозвон

```bash
ssh -o BatchMode=yes -o IdentitiesOnly=yes -i ~/.ssh/aladdin_server root@185.225.233.150
systemctl is-active aladdin-telegram-bot.service
TOK=$(grep -m1 '^BOT_TOKEN=' /opt/aladdin-telegram-shop-bot/shared/.env | cut -d= -f2- | tr -d '"')
curl -4 --http1.1 -sS -m 10 -w "getMe=%{http_code} t=%{time_total}\n" \
  -o /tmp/tg_me.json "https://api.telegram.org/bot${TOK}/getMe"
tail -n 40 /opt/aladdin-telegram-shop-bot/logs/bot.log | grep -E 'Start polling|Update id=|TelegramNetworkError|timeout'
```

## 2. Дерево решений

| getMe | Симптом | Действие |
|-------|---------|----------|
| FAIL / hang | unit active или нет | **Не** restart-storm. Ждать сеть / алерты `telegram_bot_api:fail`. Смотреть health log. |
| OK быстро | нет `Update id=`, сплошные timeout | `systemctl restart aladdin-telegram-bot` или дождаться smart-restart (лимит 3/час) |
| OK | есть `Update id=` | проблема не в Bot API — смотреть хендлеры / БД |

## 3. Health timer

- Скрипт: `scripts/telegram_bot_api_health.sh` (на сервере — `current_app/scripts/…`)
- Unit/timer: `docs/telegram-bot-api-health.service` + `.timer`
- Лог: `/var/log/aladdin-telegram-bot-api-health.log`
- State: `/var/lib/aladdin-bot-ops/`

## 4. Один poller

MAIN не должен крутить `bot.main`. См. `BOT_SINGLE_INSTANCE_CANON.md` / `verify_single_bot.sh`.

## 5. После восстановления

Нажать `/start` в `@AiMonkeyStars_bot`. Отдельный IP/прокси — следующий уровень (не этот runbook).
