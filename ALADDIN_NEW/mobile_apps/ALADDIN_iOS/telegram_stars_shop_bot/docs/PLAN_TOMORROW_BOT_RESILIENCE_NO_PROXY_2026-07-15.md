# План на завтра: устойчивость бота к «глухому» Telegram API

**Для кого:** владелец / исполнитель (прочитать утром и идти по чеклисту)  
**Дата плана:** 2026-07-14 → работать **на следующий день**  
**Контекст:** бот `@AiMonkeyStars_bot` на Contabo; инцидент 13–14 июля (Start не отвечал)  
**Канон хоста:** Contabo `185.225.233.150`, SSH `~/.ssh/aladdin_server`  
**Документ-близнец (техhandoff для ML):** `BOT_TELEGRAM_API_EGRESS_ML_HANDOFF_2026-07-14.md`  
**Cursor TODO SSOT (трекер задач):** `BOT_RESILIENCE_NO_PROXY_TODO_TRACKER.md` (ids `br-*`)  
**Следующий продукт (отдельный трек, не в тот же деплой):** рефбонус только VPN — `PLAN_REFERRAL_BONUS_VPN_ONLY_2026-07-14.md` / TODO `rb-*`  
**UX оплаты (отдельный трек):** после капчи сразу счёт — `PLAN_CHECKOUT_CAPTCHA_AUTO_CONTINUE_2026-07-14.md` / TODO `cc-*`  
**UX профиля (отдельный трек):** без рефки + VPN статус — `PLAN_PROFILE_REF_DEDUP_VPN_STATUS_2026-07-14.md` / TODO `pf-*`  
**Happ Android (SSOT шагов, не копировать):** `VPN_HAPP_ANDROID_CONNECT_GUIDE.md` / TODO `ha-*`  
**Индекс всех треков + антидубли:** `SHOP_BOT_ACTIVE_TRACKS_INDEX_2026-07-14.md`

---

## 1. Что случилось (чтобы помнить утром)

1. Пользователи жали **Start** — бот молчал.  
2. Сеть телефона и VPN API были живы.  
3. Причина: Contabo **не получал ответы** Telegram Bot API на живой токен (`getMe` / `getUpdates` висели).  
4. Процесс бота часто оставался `active`, крутил timeout — systemd его **не перезапускал**.  
5. После ручного stop → проверки → start бот ожил, потому что **канал к Telegram уже восстановился**.  
6. Авторестарт `Restart=always` **уже есть**, но он лечит только **падение процесса**, не «живой, но глухой» бот.

**Важно на завтра:**  
Цель дня — **комбо без покупки отдельного IP/прокси**.  
Отдельный мини-VPS под Bot API — **не в обязательной программе завтра**, а запасной этап «когда будете готовы».

---

## 2. Цель на завтра (что должно стать правдой к вечеру)

К концу дня должны быть верны все пункты:

- [ ] Бот стартует polling **даже если** `set_my_commands` упал по timeout  
- [ ] Есть автопроверка `getMe` раз в 1–2 минуты  
- [ ] При 3 fails подряд — алерт в ops-чат  
- [ ] При восстановлении — алерт «RECOVERED»  
- [ ] Умный рестарт: только если `getMe` OK, а polling «мёртв»; при мёртвом `getMe` — **не** долбить рестарт  
- [ ] Написан короткий runbook «что делать, если Start снова молчит»  
- [ ] Вы сами нажали `/start` и бот ответил  

Опционально (если останется время): заметка «когда покупать мини-VPS» — без внедрения.

---

## 3. Чего завтра НЕ делать (чтобы не распылиться)

- Не покупать и не настраивать SOCKS/мини-VPS (это отдельный день).  
- Не переносить бота на MAIN.  
- Не включать второй poller.  
- Не чинить «зависшие заказы 73/79» и smoke UUID вперемешку с этой задачей (отдельные тикеты).  
- Не ротировать токен, если нет времени на аккуратный `.env` + рестарт + проверку (можно днём 2).

---

## 4. Утро: 15 минут — статус «жив ли бот сейчас»

### 4.1 SSH и быстрый прозвон

```bash
ssh -o BatchMode=yes -o IdentitiesOnly=yes -i ~/.ssh/aladdin_server root@185.225.233.150
```

```bash
systemctl is-active aladdin-telegram-bot.service
TOK=$(grep -m1 '^BOT_TOKEN=' /opt/aladdin-telegram-shop-bot/shared/.env | cut -d= -f2- | tr -d '"')
curl -4 --http1.1 -sS -m 10 -w "getMe=%{http_code} t=%{time_total}\n" \
  -o /tmp/tg_me.json "https://api.telegram.org/bot${TOK}/getMe"
head -c 180 /tmp/tg_me.json; echo
tail -n 30 /opt/aladdin-telegram-shop-bot/logs/bot.log | grep -E 'Start polling|Update id=|TelegramNetworkError|timeout'
```

**Если `getMe` не 200 / t > 5с:**  
не начинать разработку вслепую — сначала зафиксировать outage (алерт себе), дальше всё равно делать код watchdog (он как раз для таких дней).  
Рестарт в цикле **не крутить**, пока `getMe` мёртв.

**Если всё ок:** идёте к Фазе A.

### 4.2 Где код локально

Рабочий корень бота:

`ALADDIN_NEW/mobile_apps/ALADDIN_iOS/telegram_stars_shop_bot/`

Ключевые файлы:

| Файл | Зачем |
|------|--------|
| `bot/main.py` | старт, `set_my_commands`, polling |
| `bot/config.py` | новые env-флаги |
| `bot/services/ops_watchdog.py` | образец алертов (не копировать слепо VPN-логику) |
| `bot/services/alerts.py` | send_alert |
| `env.example` | задокументировать новые переменные |
| systemd unit на сервере | `Restart=already always` — не ломать |

---

## 5. Фаза A — мягкий старт (код, ~1 час)

### Задача A1. `set_my_commands` не должен валить весь бот

**Где:** `bot/main.py`, функция `_setup_bot_commands` и вызов в `run()`.

**Сейчас:**  
`await bot.set_my_commands(commands)` — при timeout падает весь `run()` → процесс выходит → systemd рестартит → снова падает, если API плохой.

**Сделать:**

```text
try:
    await bot.set_my_commands(commands)
except Exception as e:
    log WARNING: set_my_commands failed, continue polling
```

Потом всё равно создавать Dispatcher и `start_polling`.

### Задача A2. Отложенный retry команд (желательно)

После старта polling — фоновая задача:

- ждать 60–120 с  
- снова `set_my_commands`  
- если ок — лог INFO  
- если снова fail — молча (не крашить)

**Проверка локально/тестом:** мок exception на первой установке команд → polling всё равно стартует (хотя бы unit-тест на helper, если удобно).

### Задача A3. Деплой только этой правки

По канону деплоя бота (см. `docs/ML_SYSTEM_HANDOFF_FINAL.md` / rule telegram-shop-bot-deploy):

1. rsync нового кода на Contabo release  
2. symlink current  
3. `systemctl restart aladdin-telegram-bot`  
4. в логе: `Start polling` без traceback на start  

**Критерий done:** бот отвечает на `/start` после деплоя.

---

## 6. Фаза B — сторож `getMe` (самое важное на завтра, ~2–3 часа)

### Задача B1. Скрипт проверки

Создать что-то вроде:

`deploy/scripts/telegram_bot_api_health.sh`  
или  
`telegram_stars_shop_bot/scripts/telegram_bot_api_health.sh`

Логика (простая):

1. Прочитать `BOT_TOKEN` из `/opt/aladdin-telegram-shop-bot/shared/.env`  
2. `curl -4 --http1.1 -m 8` → `getMe`  
3. Если HTTP 200 и время &lt; порога (например 5с) → exit 0, записать state `ok`  
4. Иначе exit 1, state `fail`  

State-файлы (как у VPN ops):

`/var/lib/aladdin-vpn-ops/telegram_bot_api_ok` или `/var/lib/aladdin-bot-ops/`

### Задача B2. Алерт в тот же ops-канал

Варианты (выбрать один, проще — B2a):

- **B2a:** вызвать существующий `vpn_ops_notify.sh` / `send_alert` путь с ключом `telegram_bot_api:fail` / `:recovered`  
- **B2b:** расширить `ops_watchdog.py` отдельным check `telegram_getme`

Сообщения человеку:

- fail: `❌ Telegram Bot API getMe FAILED on Contabo (бот может не видеть /start)`  
- recovered: `✅ Telegram Bot API getMe RECOVERED`

**Dedupe:** не слать каждые 2 минуты одно и то же (cooldown 15–30 мин).

### Задача B3. Timer / cron

Предпочтительно systemd timer (как `ops-watchdog.timer`):

- каждые **2 минуты** (или 1 мин)  
- `OnBootSec=1min`

Или cron:

```cron
*/2 * * * * root /opt/.../telegram_bot_api_health_with_alerts.sh >>/var/log/aladdin-telegram-bot-api-health.log 2>&1
```

### Задача B4. Ручной тест сторожа

1. Временно подставить неверный URL/короткий timeout → должен алерт fail (на тестовом ключе или dry-run).  
2. Вернуть нормальный → recovered.  
**Не** ломать прод токеном в чат.

**Критерий done:** в логе health есть успешные строки; при искусственном fail приходит алерт (или dry-run в файле state).

---

## 7. Фаза C — умный рестарт (осторожно, ~1–2 часа)

### Правило (выписать и соблюдать)

| getMe | Признаки «глухого» polling | Действие |
|-------|----------------------------|----------|
| FAIL | любые | **Только алерт**, НЕ restart |
| OK | N минут сплошные `TelegramNetworkError` / нет `Update id=` при active | `systemctl restart` + алерт «smart-restart» |
| OK | polling жив | ничего |

### Задача C1. Параметры в `.env`

Примеры имён:

```text
TELEGRAM_BOT_API_HEALTH_ENABLED=true
TELEGRAM_BOT_API_HEALTH_INTERVAL_SEC=120
TELEGRAM_BOT_API_GETME_TIMEOUT_SEC=8
TELEGRAM_BOT_API_FAIL_STREAK=3
TELEGRAM_BOT_SMART_RESTART_ENABLED=true
TELEGRAM_BOT_SMART_RESTART_MAX_PER_HOUR=3
TELEGRAM_BOT_POLLING_STALE_MINUTES=10
```

### Задача C2. Защита от storm

Файл `/var/lib/.../smart_restart.count` — не больше 3 рестартов в час.  
После лимита — только CRITICAL алерт «нужны руки / возможен долгий outage».

### Задача C3. Проверка

Сложно симулировать без вреда — минимум: код-ревью логики + unit-тест на «FAIL → no restart».

**Критерий done:** при `getMe` fail скрипт никогда не вызывает restart.

---

## 8. Фаза D — документация себе на 20 минут

Обновить/добавить короткий runbook (можно секцию в том же MD или `docs/RUNBOOK_BOT_SILENT_START.md`):

### Если Start молчит

1. `systemctl is-active aladdin-telegram-bot`  
2. `getMe` curl (команда из §4)  
3. Если getMe fail → **ждать/разбирать сеть**, не restart-loop; смотреть алерты  
4. Если getMe OK, а бот молчит → smart-restart или ручной `systemctl restart`  
5. Проверить, что на MAIN нет второго `bot.main`  
6. Нажать `/start` самому  

В конце дня: 5 строк «что задеплоено / какие env / где логи».

---

## 9. Расписание дня (пример)

| Время | Блок |
|-------|------|
| 0:00–0:15 | Утренний прозвон §4 |
| 0:15–1:15 | Фаза A (мягкий старт) + деплой |
| 1:15–1:30 | Проверка `/start` |
| 1:30–4:00 | Фаза B (getMe health + alerts + timer) |
| 4:00–5:30 | Фаза C (smart restart + лимиты) |
| 5:30–6:00 | Фаза D + финальный `/start` + запись «done» |

Если день короткий — **минимум: A + B**. Фаза C можно на послезавтра.

---

## 10. Definition of Done (чеклист вечером)

- [ ] В `main.py` старт не падает на `set_my_commands`  
- [ ] На Contabo крутится health timer/`getMe`  
- [ ] Есть fail/recover алерт с dedupe  
- [ ] Smart-restart **не** вызывается при мёртвом getMe (доказано логикой/тестом)  
- [ ] `/start` работает вручную  
- [ ] Заметка: «отдельный IP/прокси — следующий уровень, не сделан намеренно»  

---

## 11. День «послезавтра» (не смешивать с завтра)

Когда захотите **долгую** защиту от soft-block Contabo:

1. Купить мини-VPS  
2. SOCKS/HTTP только для Bot API  
3. `TELEGRAM_PROXY_URL` в aiogram  
4. VPN остаётся на Contabo  

Зачем помнить: всё, что сделаете завтра, **не отменяет** пользу отдельного IP; оно **дополняет**.  
Завтра вы закрываете «слепоту и плохой старт»; IP закрывает «репутацию адреса с VPN».

---

## 12. Риски и как не наступить

| Риск | Как избежать |
|------|----------------|
| Restart-storm при outage | getMe FAIL → never restart |
| Алерт-спам | dedupe 15–30 мин |
| Сломать деплой бота | не трогать MAIN polling; один Contabo |
| Утечка токена в чат/логи | не `curl -v` с токеном в историю |
| Смешать с VPN smoke-фиксами | отдельные коммиты/задачи |

---

## 13. Одной фразой «что я делаю завтра»

> Делаю бота устойчивым **без нового сервера**: он не умирает на старте из‑за Telegram, сам сообщает если `getMe` мёртв, и рестартится умно только когда Telegram уже отвечает, а процесс залип.

Удачи. Если утром бот снова глухой — начните с §4 и Фазы B (алерт), не с покупки VPS.
