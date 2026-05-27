# Companion P0 — деплой и проверка (согласовано с server guide)

**Главный документ:** [../ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md](../ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md)

## Куда деплоить (и куда НЕ)

| Путь | Назначение |
|------|------------|
| `/opt/aladdin-backend/` | **Да** — основной FastAPI/gunicorn на `:8002` |
| `/opt/aladdin-backend/security/api/routers/` | Роутеры companion, platform, voice WS |
| `/opt/aladdin-backend/security/services/ai_platform/` | JWT, policy, store, modules |
| `/opt/aladdin-backend/app/routers/auth_router.py` | JWT claims при login/register-device |
| `/opt/aladdin-backend/data/` | `companion_platform.db` (SQLite P0) |
| `/opt/aladdin-telegram-shop-bot/` | **Нет** — другой продукт |

**Снаружи:** `https://aladdin-ai.ru` → nginx → `127.0.0.1:8002`  
**Прямой IP:** `http://149.154.65.180:8002` (может быть закрыт firewall — предпочитайте домен).

## OPS-04 — алерт стоимости LLM (cron)

На VPS (после деплоя), например каждый час:

```bash
COMPANION_COST_ALERT_RUB_DAY=500 \
COMPANION_DB_PATH=/opt/aladdin-backend/data/companion_platform.db \
/opt/aladdin-backend/scripts/companion_llm_cost_alert.sh
```

Скрипт в репо: `scripts/companion_llm_cost_alert.sh` (exit 2 = порог превышен). Опционально: `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`.

## Быстрый выкат (рекомендуется)

```bash
cd mobile_apps/ALADDIN_iOS
chmod +x scripts/deploy_companion_p0.sh scripts/verify_companion_p0_prod.sh

# SSH-ключ как в server guide, например ~/.ssh/aladdin_server
./scripts/deploy_companion_p0.sh root 149.154.65.180 ~/.ssh/aladdin_server

./scripts/verify_companion_p0_prod.sh https://aladdin-ai.ru
```

Скрипт `deploy_companion_p0.sh`:
1. Бэкап старых файлов в `backups/companion_p0_<timestamp>/`
2. `scp` каждого файла в **полный** путь на сервере (не только в корень)
3. Дописывает в `.env`: `FEATURE_*`, `COMPANION_DB_PATH`
4. `py_compile` + `systemctl restart aladdin-backend.service`
5. Проверяет OpenAPI на `127.0.0.1:8002`

## Env (на сервере `/opt/aladdin-backend/.env`)

```bash
FEATURE_VOICE_ENABLED=true
FEATURE_COMPANION_ENABLED=true
FEATURE_CHAT_CORE=true
FEATURE_TRUST_ENABLED=true
COMPANION_DB_PATH=/opt/aladdin-backend/data/companion_platform.db
```

Полный пример: [COMPANION_FEATURE_FLAGS.env.example](./COMPANION_FEATURE_FLAGS.env.example)

## nginx: WebSocket голос

Семейный чат уже описан в server guide (`location /ws/`).  
Companion voice: **`/api/ai/voice/realtime`** — тоже WebSocket.

Убедитесь, что прокси для `/api/` (или отдельный `location`) передаёт:

- `proxy_http_version 1.1`
- `Upgrade` / `Connection` (map `$connection_upgrade`)
- увеличенные `proxy_read_timeout` / `proxy_send_timeout`

Иначе iOS получит ошибку handshake (как `-1011` у family chat).

Проверка на сервере:

```bash
curl -sS -m 5 -i \
  -H "Connection: Upgrade" -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  "http://127.0.0.1:8002/api/ai/voice/realtime?token=INVALID" | head -8
```

Ожидаемо: **403** от FastAPI (невалидный token), не HTML nginx и не SFM JSON.

**Блок nginx** (вставить **перед** `location /api/ {`), см. `ALADDIN_COMPANION_VOICE_WS` в vhost — на проде добавлен 2026-05-26:

```nginx
location /api/ai/voice/realtime {
    proxy_pass http://127.0.0.1:8002;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $connection_upgrade;
    ...
}
```

После reload nginx: с валидным ephemeral-token — `HTTP/1.1 101` и `session.ready`.  
С **невалидным** token — **403** (это норма, значит маршрут живой; WebSocket **не** попадает в OpenAPI `paths`).

**Прод 2026-05-27:** backend + nginx ✅ (403 на `?token=INVALID`). OpenAPI REST не содержит WS — не считать MISSING ошибкой.

## OPS-04 — cron на VPS (установлено)

```bash
# Скрипт: /opt/aladdin-backend/scripts/companion_llm_cost_alert.sh
# Лог: /var/log/aladdin-backend/companion_llm_cost.log
# Каждый час :15
crontab -l | grep companion_llm_cost
```

## Как понять, что выкат успешен

| Проверка | До выката (сейчас на проде) | После выката |
|----------|-----------------------------|--------------|
| `GET /api/ai/companion/characters` | `get_ai_companion_characters`, `mock-real-protection` | JSON `{"characters":[...]}` |
| JWT после `register-device` | нет `age_band` | `"age_band":"child"` |
| `GET /api/ai/companion/capabilities` | SFM envelope | `features`, `limits` |

## Локальные тесты (без сервера)

```bash
cd mobile_apps/ALADDIN_iOS
PYTHONPATH=. python3 Tests/test_companion_p0_smoke.py
```

## iOS

Код companion только в репозитории; для TestFlight нужна сборка с новыми Swift-файлами (`CompanionHubScreen`, `CompanionAPIService`, …).

Вход: **Child Rewards → «Поговорить с героем»**.
