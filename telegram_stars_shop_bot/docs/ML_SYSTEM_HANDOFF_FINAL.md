# Telegram Shop Bot — Final ML Handoff

## 0) Журнал: фактический деплой на production (2026-04-20)

Ниже зафиксированы **реальные шаги**, которые были выполнены для выкладки бота на прод (без изменения мобильного приложения и без изменения `/opt/aladdin-backend`).

1. **Внешний health основного ALADDIN API (до SSH):**  
   `curl -s -S -m 8 http://149.154.65.180:8002/api/health` → ожидаемо `{"status":"ok"}` (порядок действий с хостом — в `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md`).

2. **SSH на прод:** пользователь `root`, хост `149.154.65.180`; для неинтерактивного входа использован существующий ключ **`~/.ssh/aladdin_server`** с опциями в духе `ssh -o IdentitiesOnly=yes -i ~/.ssh/aladdin_server` (ключ `~/.ssh/aladdin_prod` в окружении агента отсутствовал — важно зафиксировать фактически рабочий путь к ключу).

3. **Проверка дерева бота на сервере:** каталог `ROOT=/opt/aladdin-telegram-shop-bot` существует; активная версия до выкладки указывала на предыдущий релиз в `ROOT/releases/.../telegram_stars_shop_bot`; симлинки `current_app` и `current_release` уже использовались.

4. **Подготовка каталога нового релиза:** на сервере выполнено `mkdir -p "${ROOT}/releases/<TS>/telegram_stars_shop_bot"` (конкретный timestamp см. п. 6).

5. **`rsync` с машины разработки** из корня монорепозитория, где лежит `telegram_stars_shop_bot/` (пример пути локально: `.../mobile_apps/ALADDIN_iOS`): синхронизация в `root@149.154.65.180:${ROOT}/releases/<TS>/telegram_stars_shop_bot/` с транспортом `rsync -e "ssh … -i ~/.ssh/aladdin_server"` и исключениями **`--exclude`**: `.git`, `__pycache__`, `*.pyc`, `.venv`, `venv`, **`data`** (SQLite на проде), **`.env`** (секреты не из репозитория), плюс режим **`--delete`** для зеркалирования кода без лишних файлов — **без** затрагивания `ROOT/shared/.env`, `ROOT/venv/`, `ROOT/logs/`.

6. **Фактический активный релиз после этой выкладки:**  
   `/opt/aladdin-telegram-shop-bot/releases/20260420-233510/telegram_stars_shop_bot`  
   (timestamp в формате `YYYYMMDD-HHMMSS` от локальной машины на момент деплоя).

7. **Переключение симлинков на сервере:**  
   `ln -sfn "${ROOT}/releases/<TS>" "${ROOT}/current_release"`  
   `ln -sfn "${ROOT}/releases/<TS>/telegram_stars_shop_bot" "${ROOT}/current_app"`

8. **Зависимости Python:**  
   `sudo "${ROOT}/venv/bin/pip" install -r "${ROOT}/current_app/requirements.txt"`  
   (общий venv в `ROOT/venv`, код — в `current_app`).

9. **Рестарт сервисов бота:**  
   `systemctl restart aladdin-telegram-bot.service aladdin-partner-api.service aladdin-webhook-worker.service`

10. **Пост-деплой проверки на сервере:**  
    `curl -s -S -m 8 http://127.0.0.1:8090/health` → `{"status":"ok"}`;  
    `systemctl is-active` для трёх unit’ов выше → `active`.

**Инварианты этой сессии:** дерево **мобильного приложения** в репозитории не менялось для целей деплоя; на сервере **не** выполнялись правки в **`/opt/aladdin-backend`** и не перезапускался `aladdin-backend` в рамках этой выкладки.

**Дальше по эксплуатации:** полный канон команд (`rsync` / `git pull` / `scp`, симлинки, что нельзя затирать) — в подразделе **«Доставка кода на production (канон)»** ниже в разделе 2; быстрый смоук в Telegram (`/start`, сценарии оплаты и т.д.) — **раздел 9** этого файла и чеклисты по ссылкам в разделе 10.

---

Этот документ — единая входная точка для другой ML/agent системы.  
Цель: открыть один файл и быстро понять, **что развернуто, где лежит, как работает, как проверять и где риски**.

## 1) Что это за система

Развернут отдельный Telegram Shop Bot с Partner API:

- Telegram-бот (aiogram) для пользователей/админов.
- Partner API (FastAPI) для партнёров.
- Worker очереди исходящих webhook.
- Отдельный деплой на сервере, не затрагивающий основной ALADDIN backend.

Архитектура: **один бот + один API + один worker + SQLite БД бота**.

## 2) Где что находится

### Локальный репозиторий

- Код бота: `telegram_stars_shop_bot/`
- Ключевая документация: `telegram_stars_shop_bot/docs/`
- CI workflow: `.github/workflows/telegram_shop_bot_ci.yml`

### Сервер (production)

- Основной ALADDIN backend (отдельно, не трогать): `/opt/aladdin-backend`
- Отдельный бот-проект:
  - `/opt/aladdin-telegram-shop-bot/current_app`
  - `/opt/aladdin-telegram-shop-bot/current_release`
  - `/opt/aladdin-telegram-shop-bot/releases/<timestamp>/telegram_stars_shop_bot`
  - `/opt/aladdin-telegram-shop-bot/shared/.env`
  - `/opt/aladdin-telegram-shop-bot/venv`
  - `/opt/aladdin-telegram-shop-bot/logs`

### Доставка кода на production (канон)

**Корень на сервере:** `ROOT=/opt/aladdin-telegram-shop-bot`.  
**Новый релиз:** каталог `ROOT/releases/<timestamp>/telegram_stars_shop_bot/`. **Активная версия:** симлинки `ROOT/current_release` → каталог релиза и `ROOT/current_app` → `.../telegram_stars_shop_bot` внутри него.

**Секреты:** только файл `ROOT/shared/.env` на сервере. Не заливать поверх него локальный `.env` с машины разработчика и не включать `shared/.env` в команды копирования «поверх всего дерева».

**Нельзя перезатирать или удалять при обновлении кода:** `ROOT/shared/.env`, дерево `ROOT/venv/`, каталог **`data/`** внутри приложения (по умолчанию там SQLite `shop.db`), каталог **`ROOT/logs/`**. В `rsync` с `--delete` обязательно исключать `data`, иначе можно уничтожить продовую БД.

**SSH и порядок действий с хостом** (ключ, health основного API при необходимости): см. `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md` в корне монорепозитория. IP прод-сервера в примерах ниже — тот же, что в гайде.

**Перед деплоем:** убедиться, что unit-файлы systemd указывают на канонические пути, например `WorkingDirectory=/opt/aladdin-telegram-shop-bot/current_app` и `EnvironmentFile=/opt/aladdin-telegram-shop-bot/shared/.env` (`systemctl cat aladdin-telegram-bot.service` и аналогично для API и worker).

#### Вариант A (рекомендуется): `rsync` в новый release + переключение симлинков

С локальной машины, из каталога, где лежит папка `telegram_stars_shop_bot/` (например корень клона `ALADDIN_iOS`):

```bash
export SSH_HOST="root@149.154.65.180"
export ROOT="/opt/aladdin-telegram-shop-bot"
export TS="$(date +%Y%m%d-%H%M%S)"
rsync -az --delete \
  --exclude '.git' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.venv' \
  --exclude 'venv' \
  --exclude 'data' \
  --exclude '.env' \
  ./telegram_stars_shop_bot/ "${SSH_HOST}:${ROOT}/releases/${TS}/telegram_stars_shop_bot/"
```

На сервере после успешной синхронизации (подставить тот же `TS`):

```bash
ROOT=/opt/aladdin-telegram-shop-bot
sudo ln -sfn "${ROOT}/releases/${TS}" "${ROOT}/current_release"
sudo ln -sfn "${ROOT}/releases/${TS}/telegram_stars_shop_bot" "${ROOT}/current_app"
```

Если менялся `telegram_stars_shop_bot/requirements.txt`, на сервере обновить зависимости в общем venv:

```bash
sudo /opt/aladdin-telegram-shop-bot/venv/bin/pip install -r /opt/aladdin-telegram-shop-bot/current_app/requirements.txt
```

Рестарт и проверка API (полный smoke — раздел 9 ниже):

```bash
sudo systemctl restart aladdin-telegram-bot.service aladdin-partner-api.service aladdin-webhook-worker.service
curl -s -S -m 8 http://127.0.0.1:8090/health
```

**Компактно одной цепочкой** (после `rsync` с локальной машины; пути SSH/ключ — как в вашем окружении):

```bash
TS="$(date +%Y%m%d-%H%M%S)" && rsync -az --delete \
  --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' \
  --exclude '.venv' --exclude 'venv' --exclude 'data' --exclude '.env' \
  ./telegram_stars_shop_bot/ "root@149.154.65.180:/opt/aladdin-telegram-shop-bot/releases/${TS}/telegram_stars_shop_bot/" && \
ssh root@149.154.65.180 "TS='${TS}' ROOT=/opt/aladdin-telegram-shop-bot && sudo ln -sfn \"\$ROOT/releases/\$TS\" \"\$ROOT/current_release\" && sudo ln -sfn \"\$ROOT/releases/\$TS/telegram_stars_shop_bot\" \"\$ROOT/current_app\" && sudo systemctl restart aladdin-telegram-bot.service aladdin-partner-api.service aladdin-webhook-worker.service && curl -s -S -m 8 http://127.0.0.1:8090/health"
```

(При необходимости добавьте к `ssh` опции ключа, например `-o IdentitiesOnly=yes -i ~/.ssh/aladdin_prod`.)

#### Вариант B: `git pull` в каталоге активного приложения

Если `current_app` — рабочий клон того же репозитория с настроенным `origin`:

```bash
cd "$(readlink -f /opt/aladdin-telegram-shop-bot/current_app)"
git fetch origin && git checkout <ветка_или_тег> && git pull --ff-only
sudo systemctl restart aladdin-telegram-bot.service aladdin-partner-api.service aladdin-webhook-worker.service
curl -s -S -m 8 http://127.0.0.1:8090/health
```

`git push` на `origin` **сам по себе сервер не обновляет** — на хосте всё равно нужен pull (вариант B) или выкладка файлов (вариант A).

#### Вариант C: точечный hotfix через `scp`

Для срочной подмены одного файла в уже активном дереве:

```bash
scp ./telegram_stars_shop_bot/bot/handlers/shop.py \
  root@149.154.65.180:/opt/aladdin-telegram-shop-bot/current_app/bot/handlers/shop.py
sudo systemctl restart aladdin-telegram-bot.service aladdin-partner-api.service aladdin-webhook-worker.service
```

Минус: расхождение с релизами в `releases/`; после патча лучше закрепить состояние через вариант A или B.

## 3) Сервисы systemd (production)

- `aladdin-telegram-bot.service` — Telegram polling.
- `aladdin-partner-api.service` — FastAPI на `:8090`.
- `aladdin-webhook-worker.service` — фоновая доставка исходящих webhook.
- `aladdin-backend.service` — основной ALADDIN backend, отдельный.

Проверка:

```bash
systemctl is-active aladdin-telegram-bot.service
systemctl is-active aladdin-partner-api.service
systemctl is-active aladdin-webhook-worker.service
systemctl is-active aladdin-backend.service
```

## 4) Обязательные env-переменные бота

Файл: `/opt/aladdin-telegram-shop-bot/shared/.env`

Минимум:

- `BOT_TOKEN`
- `ADMIN_IDS` (ID живых админов Telegram)
- `API_KEY_PEPPER`
- `PAYMENT_WEBHOOK_SECRET`

Дополнительно:

- `SENTRY_DSN`, `SENTRY_ENVIRONMENT`, `SENTRY_TRACES_SAMPLE_RATE`
- `PARTNER_API_CORS_ORIGINS`
- `SUPPORT_URL` / `SUPPORT_USERNAME`

## 5) Ключевые runtime-эндпоинты

- Partner API health: `http://127.0.0.1:8090/health`
- OpenAPI: `http://127.0.0.1:8090/openapi.json`
- Внешний health (основной ALADDIN): `http://149.154.65.180:8002/api/health`

## 6) Что уже проверено

- Автотесты: `13 passed`.
- Bot polling поднят.
- Partner API работает (profile/orders/topups/webhooks).
- Payment webhook (`/v1/payments/provider-webhook`) переводит заказ в `paid`.
- Исходящие webhooks идут через очередь + retry worker.
- Меню Telegram:
  - `/start` -> первая страница -> `Далее` -> 10 карточек.
  - `/menu` (через кнопку Menu внизу) -> те же 10 карточек.

## 7) Критичные operational нюансы

1. **ADMIN_IDS**  
   Должны быть реальные user_id админов.  
   Каждый админ обязан открыть бота и нажать `/start`, иначе Telegram `sendMessage` может отдавать `400/403`.

2. **Telegram egress**  
   Если появляются `TelegramNetworkError timeout`, проверять доступность `api.telegram.org:443` с сервера.
   В текущем проде применён фикс резолва в `/etc/hosts` на рабочий Telegram DC IP.

3. **Разделение проектов**  
   Любые действия по этому боту делать только в `/opt/aladdin-telegram-shop-bot/**`.  
   Не менять `/opt/aladdin-backend/**`, если задача не про основной ALADDIN backend.

4. **Worker обязателен**  
   `aladdin-webhook-worker.service` должен быть активен, иначе `outbound_webhook_events` будет копиться в `pending/failed`.

## 8) Логи и диагностика

- `/opt/aladdin-telegram-shop-bot/logs/bot.log`
- `/opt/aladdin-telegram-shop-bot/logs/partner_api.log`
- `/opt/aladdin-telegram-shop-bot/logs/webhook_worker.log`

Быстрая проверка:

```bash
tail -n 100 /opt/aladdin-telegram-shop-bot/logs/bot.log
tail -n 100 /opt/aladdin-telegram-shop-bot/logs/partner_api.log
tail -n 100 /opt/aladdin-telegram-shop-bot/logs/webhook_worker.log
```

## 9) Минимальный smoke-check после изменений

1. Проверить `systemctl is-active` для 3 сервисов бота.
2. Проверить `curl http://127.0.0.1:8090/health`.
3. В Telegram: `/start` -> `Далее` -> видны 10 карточек.
4. В Telegram: `/menu` -> видны те же 10 карточек.
5. Сделать тестовый API заказ и проверить, что статус/уведомление проходят.

## 10) Ссылки на основные документы проекта

- Runbook: `docs/RUNBOOK.md`
- Acceptance: `docs/ACCEPTANCE_CHECKLIST.md`
- Final hardening: `docs/FINAL_HARDENING_CHECKLIST.md`
- Sentry incident response: `docs/SENTRY_INCIDENT_RESPONSE.md`
- Deploy webhook worker: `docs/DEPLOY_WEBHOOK_WORKER.md`
- Systemd unit worker template: `docs/webhook-worker.service`
- Cron template worker: `docs/webhook-worker.crontab`
- Separate server deployment: `docs/SERVER_DEPLOY_SEPARATE.md`
- Roadmap A/B: `docs/ROADMAP_PLANS_A_B.md`
- Progress tracker: `docs/PROGRESS_TRACKER.json`
- OpenAPI v1: `docs/openapi_v1.yaml`

## 11) Definition of done (для следующей ML системы)

Если новая система может подтвердить все пункты ниже — контекст считан корректно:

- Понимает разделение `/opt/aladdin-backend` и `/opt/aladdin-telegram-shop-bot`.
- Умеет проверить 3 systemd сервиса бота + health `:8090`.
- Знает, где env, логи, OpenAPI, worker queue.
- Знает канон доставки кода (подраздел «Доставка кода на production» в разделе 2): `rsync` в `releases/` + симлинки, либо `git pull` в `current_app`, исключения для `data/`, `shared/.env`, `venv/`.
- Понимает критичные риски: `ADMIN_IDS`, Telegram egress, активность worker.

## 12) Карта модулей (кодовая структура)

### `bot/`

- `bot/main.py` — запуск polling, middleware, регистрация Telegram Menu команд.
- `bot/handlers/common.py` — `/start`, `/menu`, `/my`, `/orders`.
- `bot/handlers/hub.py` — основной UI хаба (10 карточек), навигация, профиль, support/API экран.
- `bot/handlers/shop.py` — checkout-поток покупки Stars/Premium.
- `bot/handlers/admin.py` — админские callback-действия (статусы, топап, sell).
- `bot/middlewares/*` — внедрение зависимостей и антифлуд.
- `bot/keyboards/shop_kb.py` — inline keyboards.
- `bot/states/*` — FSM состояния.
- `bot/db/database.py` — схема SQLite + legacy миграции.

### `bot/services/`

- `orders_repo.py` — CRUD заказов, API idempotency, статусные операции.
- `order_flow.py` — side effects при `completed` (рефералка/комиссия).
- `balance_repo.py` — баланс и topup.
- `sell_repo.py` — заявки на выкуп и пагинация.
- `api_clients_repo.py` — API ключи, owner binding, webhook subscription поля.
- `partner_outbound.py` — очередь + retry доставки `order.status_changed`.
- `payment_events_repo.py` — идемпотентность входящего payment webhook.
- `catalog.py`, `pricing.py`, `marketing.py`, `users_repo.py`, `hmac_util.py` — доменная логика.

### `partner_api/`

- `partner_api/main.py` — FastAPI app, роуты, CORS, health.
- `partner_api/deps.py` — auth по `X-API-KEY`, rate limit, контекст запроса.
- `partner_api/routers/orders.py` — create/list/get заказов API.
- `partner_api/routers/topups.py` — create/list/get пополнений.
- `partner_api/routers/profile.py` — профиль владельца ключа.
- `partner_api/routers/payment_provider.py` — входящий webhook оплаты `mark_paid`.
- `partner_api/routers/webhooks_partner.py` — подписка партнёра на исходящие webhooks.
- `partner_api/webhook_worker.py` — CLI worker для обработки очереди webhook.
- `partner_api/schemas.py`, `notify.py`, `ratelimit.py` — схемы/уведомления/лимиты.

## 13) Таблица endpoint -> handler -> БД таблицы

| Endpoint | Handler | Основные таблицы |
|---|---|---|
| `GET /health` | `partner_api.main:create_app.health` | — |
| `GET /v1/user/profile` | `partner_api/routers/profile.py:get_profile` | `users`, `api_clients` |
| `POST /v1/orders/create` | `partner_api/routers/orders.py:create_order` | `orders`, `users`, `api_clients` |
| `GET /v1/orders` | `partner_api/routers/orders.py:list_orders` | `orders` |
| `GET /v1/orders/{order_id}` | `partner_api/routers/orders.py:get_order` | `orders` |
| `POST /v1/topups/create` | `partner_api/routers/topups.py:create_topup` | `topup_requests`, `api_clients` |
| `GET /v1/topups` | `partner_api/routers/topups.py:list_topups` | `topup_requests` |
| `GET /v1/topups/{topup_id}` | `partner_api/routers/topups.py:get_topup` | `topup_requests` |
| `POST /v1/payments/provider-webhook` | `partner_api/routers/payment_provider.py:payment_provider_webhook` | `orders`, `payment_provider_events`, `outbound_webhook_events` |
| `GET /v1/webhooks/subscription` | `partner_api/routers/webhooks_partner.py:get_webhook_subscription` | `api_clients` |
| `PUT /v1/webhooks/subscription` | `partner_api/routers/webhooks_partner.py:put_webhook_subscription` | `api_clients` |

## 14) Таблица callback/action в боте

| Callback / Command | Где обрабатывается | Что делает |
|---|---|---|
| `start:hub` | `bot/handlers/hub.py:onboarding_continue` | Переход к хабу (10 карточек) |
| `nav:hub` | `bot/handlers/hub.py:nav_hub` | Возврат в хаб |
| `nav:buy_stars` | `bot/handlers/hub.py` | Открывает каталог Stars |
| `nav:premium` | `bot/handlers/hub.py` | Открывает каталог Premium |
| `nav:orders:0` / `nav:orders:{page}` | `bot/handlers/hub.py` | Пагинация «Мои заказы» |
| `nav:sells:0` / `nav:sells:{page}` | `bot/handlers/hub.py` | Пагинация «Мои заявки на выкуп» |
| `nav:privacy` | `bot/handlers/hub.py` | Экран политики данных |
| `api:partner_key` / `api:req` | `bot/handlers/hub.py` | Выдача/запрос API ключа |
| `adm:paid|proc|done:{id}` | `bot/handlers/admin.py` | Изменение статуса заказа админом |
| `top:ok:{id}` | `bot/handlers/admin.py` | Подтверждение топапа админом |
| `sel:proc|done|can:{id}` | `bot/handlers/admin.py` | Статусы заявки sell |
| `/menu` | `bot/handlers/common.py:cmd_menu` | Открывает тот же хаб (10 карточек) |

## 15) Release chronology (что и зачем меняли)

1. **База/архитектура API v1:** добавлены `api_clients`, поля `orders.source/api_client_id/idempotency_key/external_ref`, idempotency индекс.  
   **Зачем:** безопасная партнёрская интеграция без дубликатов.
2. **Partner API endpoints:** profile/orders/topups + OpenAPI draft.  
   **Зачем:** дать партнёрам stable HTTP контракт.
3. **Bot UX hardening:** pagination orders/sells, privacy screen, empty catalog UX.  
   **Зачем:** завершённый клиентский опыт без тупиков.
4. **Sentry + структурные логи:** инициализация в bot/api, scrub секретов.  
   **Зачем:** наблюдаемость и безопасный error tracking.
5. **Payment webhook + idempotency:** `POST /v1/payments/provider-webhook`.  
   **Зачем:** автоплатежи v1 с контролем повторов.
6. **Outbound webhooks + subscription:** `order.status_changed`, `PUT /v1/webhooks/subscription`.  
   **Зачем:** уведомлять партнёра о статусах заказа.
7. **Webhook queue + worker:** `outbound_webhook_events`, retry/backoff, `partner_api.webhook_worker`.  
   **Зачем:** не терять события при сетевых ошибках.
8. **CI усиление:** `ruff`, optional `mypy`, расширение тестов (до 13).  
   **Зачем:** снизить риск регрессий.
9. **Отдельный production deploy:** `/opt/aladdin-telegram-shop-bot` + отдельные systemd units.  
   **Зачем:** полная изоляция от `/opt/aladdin-backend`.
10. **Telegram menu UX:** регистрация `/menu` в `setMyCommands`.  
    **Зачем:** доступ к хабу как через «Далее», так и через кнопку Menu.

## 16) Known limitations + future migration notes

### Known limitations

- SQLite подходит для малого/среднего трафика, но имеет предел под high concurrency.
- Outbound webhook retry есть, но без DLQ/отдельного durable брокера.
- `mypy` пока optional в CI (не gate).
- Telegram-зависимость чувствительна к сетевой доступности `api.telegram.org`.
- `ADMIN_IDS` должны быть валидными и админы должны нажать `/start`.

### Future migration notes

1. **DB migration:** SQLite -> Postgres при росте нагрузки (заказы, webhook queue, ledger).
2. **Webhook delivery v2:** отдельный worker process с DLQ, jitter backoff, replay CLI.
3. **Observability v2:** метрики Prometheus/Grafana + SLO по API/webhook.
4. **Security v2:** регулярная ротация API/webhook секретов + audit trail.
5. **CI v2:** сделать `mypy` обязательным, добавить контрактные API тесты из OpenAPI.
