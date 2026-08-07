# Telegram Shop Bot — архитектура и устройство системы

Документ для людей и для других ML/agent-систем: **одна точка входа в понимание кода**, чтобы при необходимости **воспроизвести бота по файлам** и не путать его с iOS-приложением или основным ALADDIN backend.

**Связанные документы:**

- Деплой, серверные пути, `rsync`, systemd: [`ML_SYSTEM_HANDOFF_FINAL.md`](./ML_SYSTEM_HANDOFF_FINAL.md).
- Переменные окружения (шаблон): `../env.example`.

---

## 1. Назначение и границы продукта

В каталоге **`telegram_stars_shop_bot/`** лежит **отдельный продукт**: Telegram-магазин (Stars, Premium, подарки и смежные сценарии) с **Partner HTTP API**, общей **SQLite БД** и **воркером исходящих webhook** для партнёров.

Это **не** мобильное приложение ALADDIN (код iOS — вне этого каталога) и **не** `/opt/aladdin-backend` (основной API ALADDIN деплоится отдельно).

**Инвариант продакшена:** один инстанс бота (polling), один процесс Partner API (uvicorn/FastAPI), один процесс webhook-worker; все три читают **один и тот же файл БД** на диске (путь из `DATABASE_PATH` / дефолт `data/shop.db` относительно корня приложения).

---

## 2. Стек технологий

| Слой | Технология |
|------|------------|
| Telegram | **aiogram 3.x** (`Dispatcher`, роутеры, FSM) |
| Хранилище FSM | **`MemoryStorage`** — состояния чек-аута в памяти процесса |
| БД | **SQLite** через **aiosqlite**, схема + миграции «на лету» в `bot/db/database.py` |
| Конфиг | **pydantic-settings** (`bot/config.py`, переменные из `.env` / `shared/.env`) |
| Каталог товаров | **YAML** (`bot/products.yaml`), загрузка `load_products()` |
| Partner API | **FastAPI** + **uvicorn**, порт по умолчанию **8090** |
| HTTP-клиенты | **httpx** (платежи, фулфилмент, внешние API) |
| Наблюдаемость | **Sentry** (опционально), логирование стандартным `logging` |
| Rate limit API | In-memory или **Redis** (зависит от `PARTNER_API_RATE_LIMIT_BACKEND`) |
| Прочее | **matplotlib** — графики в админ-дашборде; **redis** — опционально для лимитов |

Файл зависимостей: **`requirements.txt`** в корне `telegram_stars_shop_bot/`.

---

## 3. Точки входа и процессы

### 3.1. Telegram-бот

- **Файл:** `bot/main.py`
- **Функция:** `run()` → `asyncio.run(run())` из `main()`
- **Запуск в проде:** обычно `python -m bot.main` из `WorkingDirectory` (на сервере это **`current_app`** — см. раздел 17).

Последовательность при старте (упрощённо):

1. `load_settings()` — без валидного `USD_RUB_RATE` приложение не поднимется.
2. Подключение к SQLite: `connect(settings.database_path)`.
3. Загрузка каталога: `load_products(settings.products_path)`.
4. `Bot(..., parse_mode=HTML)`.
5. `Dispatcher(storage=MemoryStorage())`.
6. Регистрация middleware и роутеров (см. раздел 7).
7. Фоновые задачи (см. раздел 15), затем `dp.start_polling(bot)`.

### 3.2. Partner API

- **Файл:** `partner_api/main.py`
- **Приложение:** `app = create_app()` — те же `load_settings` / `load_products`, что и у бота.
- **Здоровье:** `GET /health` → `{"status":"ok"}`.
- Документация OpenAPI: `/docs`, `/redoc`.

### 3.3. Webhook worker (исходящая очередь)

- **Файл:** `partner_api/webhook_worker.py`
- **Назначение:** циклически обрабатывает таблицу **`outbound_webhook_events`** (доставка событий партнёрам по их `webhook_url`).
- Режимы: одноразовый прогон или `--forever` с паузой.

### 3.4. Прочие исполняемые модули

- `partner_api/auto_fulfill_worker.py` — политики автовыдачи (при включённых флагах в конфиге).
- В репозитории есть скрипты в `scripts/` (например курсы) — вспомогательные, не ядро UX бота.

---

## 4. Структура каталогов (обзор)

```
telegram_stars_shop_bot/
├── bot/
│   ├── main.py              # точка входа polling
│   ├── config.py          # Settings / env
│   ├── ui_copy.py         # крупные тексты UI
│   ├── logutil.py         # структурированные служебные логи
│   ├── sentry_util.py
│   ├── support_links.py
│   ├── products.yaml      # каталог (можно переопределить путь)
│   ├── db/database.py     # SCHEMA + migrate_legacy + connect
│   ├── handlers/          # common, hub, shop, admin
│   ├── keyboards/         # Inline-клавиатуры
│   ├── middlewares/       # inject, throttle, channel_gate
│   ├── services/          # репозитории, платежи, аналитика, captcha, …
│   └── states/checkout.py # FSM группы
├── partner_api/
│   ├── main.py
│   ├── deps.py            # зависимости FastAPI (ключи, БД)
│   ├── routers/           # orders, webhooks, profile, legal, …
│   ├── rate_limit_*.py
│   ├── notify.py
│   └── webhook_worker.py
├── legal/                 # privacy_policy_ru.txt, terms_of_service_ru.txt
├── tests/                 # pytest
├── docs/                  # операторская и ML-документация
├── env.example
└── requirements.txt
```

Код **не** должен полагаться на глобальное состояние для БД/настроек в хендлерах: их кладёт middleware (см. ниже).

---

## 5. Конфигурация (`Settings`)

Источник правды: класс **`Settings`** в `bot/config.py`, поля мапятся на переменные окружения (`BOT_TOKEN`, `ADMIN_IDS`, провайдеры оплаты, URL юридических страниц, канал, лимиты и т.д.).

**Критично для старта:**

- `BOT_TOKEN`
- `USD_RUB_RATE` > 0
- Для Partner API: `API_KEY_PEPPER` (пустой pepper → API не стартует по задумке lifespan)

**Юридические ссылки для кнопок в боте:**

- `PRIVACY_POLICY_URL`, `TERMS_OF_SERVICE_URL` — по умолчанию указывают на `https://aladdin-ai.ru/v1/legal/...` (страницы отдаёт Partner API из `legal/*.txt`).

Полный перечень переменных см. **`env.example`**.

---

## 6. База данных SQLite

### 6.1. Подключение и миграции

- **`connect()`** в `bot/db/database.py`: создаёт таблицы из **`SCHEMA`**, затем **`migrate_legacy()`** — добавляет колонки и вспомогательные таблицы на существующих базах без отдельного миграционного фреймворка.

### 6.2. Основные сущности (логически)

| Область | Таблицы / назначение |
|---------|---------------------|
| Пользователи | `users` — профиль, реферал, балансы, **`locale`**, **`terms_accepted_at`**, **`onboarding_completed_at`**, антифрод-поля (`checkout_captcha_ok_until`, `last_start_command_at`, …) |
| Заказы | `orders` — статус, суммы, скидки, провайдер, фулфилмент, P&L-снимки, связь с API-клиентом |
| Аналитика | `analytics_events` — в т.ч. `bot_entry` для воронки |
| Партнёрский API | `api_clients`, уникальность заказов партнёра (`idempotency_key`) |
| Финансы пользователя | `ledger`, `topup_requests` |
| B2C заявки | `sell_requests`, `api_key_requests` |
| Исходящие webhook | `outbound_webhook_events` |
| Капча | `captcha_challenges` |
| Аудит | `admin_audit_log` |
| Конкурсы | `partner_contests` |
| Платежный анти-дубликат | `payment_provider_events` |

Репозитории с SQL обычно лежат в **`bot/services/*_repo.py`** (например `users_repo`, `orders_repo`, `captcha_repo`, `analytics_repo`).

---

## 7. Telegram-бот: диспетчер, middleware, роутеры

### 7.1. Инъекция контекста

**`InjectMiddleware`** (`bot/middlewares/inject.py`) на уровне **`dp.update.middleware`** заполняет для каждого хендлера:

- `settings`
- `conn` (соединение SQLite)
- `products` (список `Product`)

Так хендлеры остаются чистыми функциями от глобалов.

### 7.2. Антифлуд по сообщениям

**`ThrottleMiddleware`** (`bot/middlewares/throttling.py`) на **`dp.message.middleware`**: не чаще ~0.6 с на пользователя для **сообщений** (админы из `ADMIN_IDS` пропускаются).

Отдельно от этого действуют **интервалы в БД**: троттлинг `/start` и создания заказов (`start_command_min_interval_seconds`, `order_create_min_interval_seconds` в `Settings`).

### 7.3. Гейт канала на покупках

**`ChannelGateMiddleware`** (`bot/middlewares/channel_gate.py`) подключён **только** к **`callback_query`** роутера **`shop`**:

- Если задан канал (`REQUIRED_CHANNEL_ID`) и callback относится к покупке (`buy:`, `prem:`, `pay:`, `order:submit`, навигация в витрину `nav:buy_stars`, `nav:premium`, `nav:gifts`), выполняется проверка членства через Telegram API.
- Иначе хендлер вызывается без проверки.

Это сознательный баланс: не дергать `getChatMember` на каждый клик в профиле/FAQ.

### 7.4. Роутеры и порядок подключения

В `bot/main.py`:

1. **`common_handlers`** — `/start`, язык, оферта, канал онбординга, капчи (`onb:*`, `chk:c:*`), команды `/my`, `/orders`, `/menu`.
2. **`hub_handlers`** — «SPA» главного меню: `nav:*`, заказы `ord:*`, поддержка `sup:*`, API `api:*`, топап `top:*`, продажа Stars, конкурсы и т.д.
3. **`shop_handlers`** (+ ChannelGate на callbacks) — витрина, оплата, FSM чек-аута.
4. **`admin_handlers`** — `/admin`, `ast:*`, очередь оператора, конкурсы, финансовые действия.

Порядок важен только там, где пересекаются фильтры; в проекте префиксы в основном разведены по файлам.

---

## 8. Пространство `callback_data` (маршрутизация как «страницы»)

В Telegram UX строится на **сообщениях + inline-кнопках**; «переходы» — `edit_text` / новые сообщения. Ниже — **договорённость по префиксам** (не жёсткий enum, а карта для разработки).

| Префикс / паттерн | Где обрабатывается | Назначение |
|-------------------|-------------------|------------|
| `onb:lang:*` | `common.py` | Выбор языка (ru/en) |
| `onb:terms:yes` / `no` | `common.py` | Legacy: принятие оферты (старые сообщения) |
| `onb:ch:check` | `common.py` | Проверка подписки + запись согласия (`terms_accepted_at`) |
| `onb:c:*` | `common.py` | Эмодзи-капча онбординга |
| `chk:c:*` | `common.py` | Эмодзи-капча перед подтверждением заказа |
| `start:hub` | `hub.py` | Выход из стены канала в хаб |
| `nav:hub` | `hub.py` | Главное меню |
| `nav:buy_stars`, `nav:premium`, `nav:gifts` | `hub.py` | Вход в витрину (гейт канала на стороне shop middleware для shop callbacks) |
| `nav:orders:*`, `ord:*` | `hub.py` | Список заказов и карточка |
| `nav:profile`, `nav:ref`, `nav:reffaq`, … | `hub.py` | Профиль и рефералка |
| `nav:api`, `api:*` | `hub.py` | Partner API ключи и заявки |
| `nav:topup`, `top:*` | `hub.py` | Пополнение баланса |
| `sup:*`, `nav:privacy`, … | `hub.py` | Поддержка, FAQ, политика (ссылки на URL) |
| `nav:contest` | `hub.py` | Конкурсная витрина |
| `buy:*`, `prem:*` | `shop.py` | Выбор товара Stars / Premium |
| `pay:*`, `pay:bcc:*` | `shop.py` | Способ оплаты (в т.ч. BC Ckassa) |
| `usr:ok`, `usr:ed` | `shop.py` | Подтверждение username в FSM |
| `order:submit`, `order:cancel` | `shop.py` | Финализация / отмена заказа |
| `ast:*` | `admin.py` | Админ-статистика (периоды, CSV, графики) |
| `adm:*` | `admin.py` | Действия по заказам, топапам и т.п. |

Длина `callback_data` в Telegram ограничена **64 байтами** — при расширении новых кодов это нужно помнить.

---

## 9. Онбординг (последовательность экранов)

Цепочка централизована в **`bot/services/onboarding_gate.py`** (`resume_onboarding_pipeline`).

**Логический порядок:**

1. **Язык** — если в `users.locale` пусто: экран с `onboarding_language_kb()`, сохранение `ru`/`en`, удаление сообщения, снова pipeline.
2. **Канал + согласие (один экран)** — пока нет `terms_accepted_at` **или** (включён гейт канала и пользователь не в канале): `onboarding_combined_caption_html` + `onboarding_combined_kb` (URL канала, URL соглашения и политики, callback `onb:ch:check`). Успешная проверка подписки → **`users_repo.accept_terms`** (`terms_accepted_at`) и продолжение pipeline. Legacy `onb:terms:yes` / `onb:terms:no` оставлены для старых сообщений в чате.
3. **Капча** — пока не завершён онбординг: **`emoji_captcha.send_onboarding_captcha_photo`** пишет задание в `captcha_challenges`, пользователь жмёт `onb:c:{challenge_id}:{idx}`; успех → **`users_repo.complete_onboarding`** → приветствие хаба.
4. **Хаб** — `send_hub_welcome`: опционально второе фото (`START_PHOTO_FILE_ID_2`), текст **`ONBOARDING_SCREEN_2`** из `ui_copy.py`, клавиатура **`hub_menu_kb(settings)`**.

Повторное подтверждение документов в VPN не требуется, если уже есть shop `terms_accepted_at` (`has_vpn_legal_accepted`).

Команды **`/menu`**, **`/my`**, **`/orders`** проходят через **`ensure_shop_access`** в `common.py`: сначала завершённый онбординг + подписка (если канал включён), иначе возобновление pipeline или стена канала.

**Реферальный deep link:** `/start ref_<telegram_id>` обрабатывается в `cmd_start` — установка реферера, если ещё не задан.

---

## 10. Два уровня проверки канала

| Уровень | Механизм | Когда срабатывает |
|---------|----------|-------------------|
| Команды и хаб | `ensure_shop_access` / прямые проверки в `/start` | Любой доступ к «магазинному» контенту после онбординга |
| Покупка | `ChannelGateMiddleware` только на **shop** `callback_query` | Клики по витрине, оплате, `order:submit` |

Так уменьшается число запросов к Telegram API и сохраняется правило: **без канала — нельзя инициировать покупку**.

---

## 11. Магазин, заказ и оплата

### 11.1. FSM чек-аута

**`CheckoutStates`** (`bot/states/checkout.py`):

- `waiting_recipient` — ввод получателя (Stars/подарки).
- `waiting_verify_username` — подтверждение username кнопками `usr:ok` / `usr:ed`.
- `waiting_confirm` — итоговая сумма и подтверждение (`order:submit`).

Отмена: **`/cancel`** и **`order:cancel`**.

Другие FSM: **`TopupStates`**, **`ApiKeyStates`** — для сценариев произвольного топапа, заявки на API-ключ.

### 11.2. Капча на чек-ауте

Перед **`order:submit`** может требоваться эмодзи-капча: при успехе выставляется окно **`checkout_captcha_ok_until`** (`CHECKOUT_CAPTCHA_TTL_SECONDS`). Callback **`chk:c:*`** совпадает по идее с онбординговой капчей, но с `purpose="checkout"` в `captcha_repo`.

### 11.3. Антифрод при создании заказа

В **`orders_repo`** (и связанных вызовах из `shop.py`) используются интервалы между созданием заказов и лимиты висящих `pending_payment` — параметры из `Settings`.

### 11.4. Провайдеры оплаты (концептуально)

Реализация разнесена по **`bot/services/`** и вебхук-роутерам **`partner_api/routers/`**:

- **Ckassa** — Shop API (`do-pay`) и/или универсальная страница BC (`CKASSA_BC_UNIVERSAL_PAYMENT_URL`), колбэк на Partner API.
- **LAVA** — счета и вебхук.
- **Crypto Pay** (@CryptoBot) — счета через API.
- **xRocket Pay** — USDT счета.
- Ручные инструкции / резерв при недоступности провайдера (флаги и тексты в конфиге).

После отметки оплаченным запускаются сценарии уведомлений покупателю, операторов, автозакрытие **`pending_payment`** по таймеру, опционально **auto-fulfill** через iStar (`istar_*` настройки и клиент `istar_fulfill_client.py`).

Детали протоколов и переменных см. узкоспециализированные документы в `docs/` (`CRYPTO_PAY_SPEC.md`, runbooks по FX и т.д.).

---

## 12. Partner API (FastAPI)

**Монтирование роутеров** — `partner_api/main.py`, префикс **`/v1`** для бизнес-роутов.

Типичный набор областей:

| Роутер | Назначение |
|--------|------------|
| `legal_pages` | `GET /v1/legal/privacy`, `GET /v1/legal/terms` — HTML из `legal/*.txt` |
| `profile` | Профиль и баланс по API-ключу |
| `orders` | Создание и чтение заказов партнёра |
| `topups` | Пополнения по API |
| `payment_provider` | Унифицированные колбэки «оплачено» и служебные методы |
| `lava_webhook`, `ckassa_webhook`, `crypto_pay_webhook`, `xrocket_webhook`, `istar_webhook` | Входящие уведомления провайдеров |
| `webhooks_partner` | Подписка партнёра на события по заказам |

**Аутентификация партнёра:** заголовок **`X-API-KEY`** (хеш с `API_KEY_PEPPER`), детали в `partner_api/deps.py`.

**Rate limiting:** `PartnerRateLimitMiddleware` + `rate_limit_store.py` (memory или Redis).

---

## 13. Юридические тексты вне Telegram

Исходники текстов: **`legal/privacy_policy_ru.txt`**, **`legal/terms_of_service_ru.txt`**.

Partner API отдаёт их как безопасный HTML (экранирование через `html.escape` в `partner_api/routers/legal_pages.py`). Бот в интерфейсе ссылается на URL из настроек (`PRIVACY_POLICY_URL`, `TERMS_OF_SERVICE_URL`).

**Важно для прокси:** публичный домен должен проксировать **`/v1/*`** на процесс Partner API (порт **8090** на сервере), иначе ссылки из бота дадут 404.

---

## 14. Фоновые циклы в процессе бота

Запускаются в `bot/main.py` параллельно с polling:

1. **`pending_payment_ttl_loop`** — перевод просроченных неоплаченных заказов из pending (интервал из `ORDER_PENDING_PAYMENT_SWEEP_INTERVAL_SECONDS`).
2. **`stuck_paid_orders_loop`** (если пороги > 0) — предупреждения по «зависшим» оплаченным / processing.
3. **`break_glass_report_loop`** (если интервал > 0) — отчёты по break-glass операциям.

Эти циклы используют тот же `settings` и при необходимости отправку алертов (`alerts.py`).

---

## 15. Аналитика и админка

- **События:** `analytics_repo.log_event` — например `bot_entry` с `via: start/menu` для оценки воронки.
- **Админы:** список `ADMIN_IDS`; финансово-критичные действия могут быть ограничены **`SUPER_ADMIN_IDS`** (`Settings.is_super_admin`).
- **Дашборд:** callback-префикс **`ast:*`** — периоды, продажи, топ прибыли, динамика, matplotlib-графики, CSV.
- **Очередь оператора:** `/admqueue` — заказы долго в processing.
- **Конкурсы:** `/contest`, таблица `partner_contests`.
- **Аудит:** записи в `admin_audit_log` на чувствительные действия.

---

## 16. Деплой и эксплуатация (кратко)

Полный канон команд — в **[`ML_SYSTEM_HANDOFF_FINAL.md`](./ML_SYSTEM_HANDOFF_FINAL.md)**.

Ключевые моменты для «точной копии» окружения:

1. На сервере код должен быть доступен по симлинку **`current_app`** → `releases/<TS>/telegram_stars_shop_bot`, потому что **systemd** часто использует именно **`WorkingDirectory=.../current_app`**.
2. Обновлять зависимости через **`/opt/.../venv/bin/pip install -r current_app/requirements.txt`** (не системный `pip` без venv — PEP 668).
3. Не затирать **`shared/.env`**, **`data/`** с `shop.db`, **`venv/`**, **`logs/`**.
4. После выкладки перезапускать **три** unit'а: бот, Partner API, webhook-worker.

---

## 17. Чеклист для воспроизведения «клона» бота из репозитория

1. Скопировать каталог **`telegram_stars_shop_bot/`** целиком.
2. Создать `shared/.env` или `.env` по **`env.example`**: токен бота, курс `USD_RUB_RATE`, админы, провайдеры оплаты, URL вебхуков, канал (если нужен гейт).
3. Установить зависимости из **`requirements.txt`** в виртуальное окружение.
4. Убедиться, что существует каталог для БД (дефолт **`data/`**) и права на запись.
5. Запустить бота: `python -m bot.main`; Partner API: `python -m uvicorn partner_api.main:app --host 0.0.0.0 --port 8090`; worker: `python -m partner_api.webhook_worker --forever`.
6. Настроить reverse-proxy на **`/v1`** к Partner API для публичных ссылок (оплата, legal).
7. Прогнать **`pytest`** в `tests/`.

---

## 18. Сильные стороны архитектуры

- Чёткое разделение **`handlers`** по зонам ответственности и **систематические префиксы** callback — проще сопровождать, чем монолитный файл.
- **Один каталог товаров** и общие типы для бота и API.
- **Partner API** принимает вебхуки и партнёрский трафик отдельно от polling-процесса бота.
- **SQLite + репозитории** дают предсказуемую модель данных без внешней БД на старте.
- Точечный **гейт канала** на покупках снижает нагрузку на Telegram API.

---

## 19. Компромиссы и зоны внимания

| Тема | Суть |
|------|------|
| FSM в памяти | После рестарта процесса пользователь выходит из состояния чек-аута; для HA-кластера обычно берут Redis storage |
| Дублирование проверки канала | Команды через `ensure_shop_access`, покупки через middleware — при новых «платных» входах нужно явно добавить проверку |
| Аналитика воронки | Зависит от успешных записей в `analytics_events`; сбои логирования дают «дыры» в отчётах |
| SQLite | Один писатель; три процесса должны использовать **один файл БД** и адекватный timeout (конфигурация `aiosqlite`) |
| Callback 64 байта | Новые действия должны укладываться в лимит или использовать короткие идентификаторы |

---

## 20. Карта пользовательских экранов (кратко)

1. **`/start`** → upsert пользователя → троттлинг → событие `bot_entry` → реферал из payload → язык (если впервые) → pipeline (оферта → канал → капча) → хаб.
2. **Хаб** → разделы через `nav:*` (покупки, профиль, заказы, поддержка, топап, API, конкурс).
3. **Покупка** → витрина → котировка → (Premium: назначение) → способ оплаты → экран оплаты провайдера → статусы заказа в «Мои заказы».
4. **Админ** → `/admin` и ветка `ast:*` для метрик; операторские команды по документации в `docs/RUNBOOK.md`.

---

## 21. Сценарий end-to-end: Stars, фиат, Ckassa BC и вебхук Ckassa

Ниже — «сквозной» разбор с **именами функций** в `bot/handlers/shop.py`, **`bot/services/orders_repo.py`** и вебхука Partner API. Важно различать два способа оплаты через Ckassa:

| Способ | Как появляется в боте | Авто-статус «Оплачен» |
|--------|------------------------|------------------------|
| **Универсальная страница BC** (`CKASSA_BC_UNIVERSAL_PAYMENT_URL`, часто с **`CKASSA_BC_SOLO_CHECKOUT=true`**) | Покупатель сам вводит сумму на сайте Ckassa; в чате показывается мемо **`ORDER{id}`** | **Нет** привязки к HTTP-колбэку ЦК с `orderId` заказа бота; покупатель жмёт **«Я оплатил»** → `pay:bcc:{id}` → уведомление админам для ручной сверки |
| **Ckassa Shop API** (`do-pay`, `create_ckassa_payment_meta`) | Кнопка открывает страницу с **уже подставленной суммой** и `orderId` = ID заказа в БД | **Да**: POST/GET на **`/v1/payments/ckassa-webhook`** → проверка подписи → `pending_payment` → **`paid`** |

Один и тот же экран фиата строит функция **`_present_fiat_checkout`**; она ветвится по `solo_bc`, `ckassa_checkout_configured`, `lava_checkout_configured`.

### 21.1. Предпосылки в конфиге

- Для **только BC** (типичный прод-упрощённый поток): заданы **`CKASSA_BC_UNIVERSAL_PAYMENT_URL`**, **`CKASSA_BC_SOLO_CHECKOUT=true`**, включён фиатный метод у товара.
- Для **автовебхука Ckassa**: **`CKASSA_ENABLED=true`**, токен/секрет магазина, **`CKASSA_CALLBACK_PUBLIC_URL`** указывает на публичный **`…/v1/payments/ckassa-webhook`**, вызывается **`create_ckassa_payment_meta`** (Shop API).

### 21.2. Цепочка UX: Stars → фиат → заказ (бот)

Все шаги в **`bot/handlers/shop.py`**, если не указано иное.

| Шаг | Действие пользователя | Обработчик / функция | Заметки |
|-----|------------------------|----------------------|---------|
| 1 | Хаб → «Купить Stars» | В **`hub.py`**: callback `nav:buy_stars` → сообщение с товарами и `buy:{product_id}` | Гейт канала: **`ChannelGateMiddleware`** |
| 2 | Выбор пакета Stars | **`open_product`** (`@router.callback_query(F.data.startswith("buy:"))`) | `quote_product` (**`bot/services/pricing.py`**), `_fmt_quote_html`, для Stars — подсказка про получателя; **`analytics_repo.log_event`** `product_view` |
| 3 | «Карта / СБП» (фиат) | **`choose_payment`** (`pay:fiat:{product_id}`) | Для Stars (не Premium self): **`CheckoutStates.waiting_recipient`** |
| 4 | Ввод `@username` | **`read_recipient`** | Проверка **`_USERNAME_RE`** |
| 5 | Подтверждение получателя | **`verify_username_ok`** (`usr:ok`) | Переход в **`CheckoutStates.waiting_confirm`**, **`confirm_order_kb()`** |
| 6 | Возможная капча | Перед созданием заказа в **`order_submit` / `_gate_captcha_or_finalize`**: **`users_repo.checkout_captcha_valid`**; если нет — **`emoji_captcha.prompt_checkout_captcha`** + FSM `awaiting_checkout_after_captcha`; callback **`chk:c:*`** → **`finalize_checkout_order`** (без повторного клика). После успешного create заказа при **`CHECKOUT_CAPTCHA_ONCE_PER_ORDER=true`** (дефолт) — **`clear_checkout_captcha`**: следующий заказ снова с капчей. | TTL **`CHECKOUT_CAPTCHA_TTL_SECONDS`** (короткое окно между капчей и auto-finalize). План: `PLAN_CHECKOUT_CAPTCHA_AUTO_CONTINUE_2026-07-14.md` (`cc-*`). |
| 7 | «Создать заказ» | **`order_submit`** (`order:submit`) | **`orders_repo.allow_order_create_interval`**, **`orders_repo.require_pending_order_cap`**, затем **`orders_repo.create_order`** со статусом **`pending_payment`**, `payment_method="fiat"` |
| 8 | Экран оплаты | **`_present_fiat_checkout`** | Сначала **`allow_checkout_invoice_attempt`** (**`bot/services/invoice_checkout_cooldown.py`**), при необходимости обращение к **`orders_repo.assert_invoice_request_allowed`** через тот же слой cooldown |

### 21.3. Ветка «только BC» (solo) внутри `_present_fiat_checkout`

Условие: **`ckassa_bc_universal_payment_url`** не пусто и **`ckassa_bc_solo_checkout`** = true (и задан `univers`).

| Что делает код | Функция / вызов |
|----------------|-----------------|
| Помечает счёт как поток BC | **`orders_repo.set_invoice_provider_metadata`** — `provider="ckassa_bc"`, `external_id=None` |
| Собирает текст (сумма, минимум эквайринга, мемо `ORDER{id}`) | Тело **`_present_fiat_checkout`** (список `parts`) |
| Клавиатура: ссылка на BC + «Я оплатил» | **`fiat_checkout_options_kb`** в **`bot/keyboards/shop_kb.py`** — callback **`pay:bcc:{order_id}`** |

После оплаты на сайте:

| Шаг | Callback | Обработчик | Репозиторий / эффект |
|-----|----------|------------|----------------------|
| «Я оплатил» | `pay:bcc:{order_id}` | **`bc_universal_payment_claim`** | **`orders_repo.touch_bc_payment_claim_if_allowed`** (коды `ok` / `cooldown` / `wrong_user` / …) |
| Уведомление операторам | — | **`_notify_admins_bc_payment_claim`** | **`orders_repo.get_order`**, **`operator_bc_manual_checklist_html`** (**`bot/services/operator_payment_memo.py`**) |

Перевод заказа в **`paid`** делается админом вручную (команды/callback’и в **`admin.py`**) после сверки в ЛК Ckassa — это вне данного сквозного автоматического webhook.

### 21.4. Ветка «Ckassa Shop API» и HTTP webhook

Когда **`ckassa_checkout_configured`** истинно и в **`_present_fiat_checkout`** создан счёт через **`create_ckassa_payment_meta`** (**`bot/services/ckassa_api.py`**):

| Шаг | Где | Что происходит |
|-----|-----|----------------|
| Создание ссылки оплаты | **`create_ckassa_payment_meta`** | HTTP к API Ckassa, URL для покупателя |
| Сохранение внешнего id | **`orders_repo.set_invoice_provider_metadata`** | `provider="ckassa"` или `"multi"`, `invoice_last_external_id` |
| Колбэк от ЦК | **`partner_api/routers/ckassa_webhook.py`** | **`ckassa_payment_webhook_post`** / **`ckassa_payment_webhook_get`** → общая **`_ckassa_payment_webhook_impl`** |
| Разбор тела | **`_flat_request_params`** | form / JSON / query |
| Проверки | **`_ckassa_payment_webhook_impl`** | `shop`, подпись **`ckassa_callback_signature`**, сумма в копейках vs **`orders_repo.amount_due_external`** или **`rub_after_discounts`** |
| Идемпотентный переход в оплачен | **`bot/services/provider_mark_paid.py`** | **`mark_order_paid_idempotent`** — таблица **`payment_provider_events`**, **`orders_repo.update_status_no_commit`** → **`paid`** |
| Обновление regPayNum | После commit | **`orders_repo.set_invoice_provider_metadata`** с `external_id=reg_pay_num` |
| Исходящий webhook партнёра | Фоном | **`emit_order_status_changed`** (**`bot/services/partner_outbound.py`**) |

Ответ провайдеру — **`PlainTextResponse("success")`** или **`"fail"`** (текст/plain, как ожидает ЦК).

### 21.5. Сводка по `orders_repo` для этого сценария

Функции, которые последовательно или альтернативно участвуют в Stars + фиат:

- **`count_user_completed_orders`** — через **`_is_first_purchase`** → реферальная скидка в котировке.
- **`require_pending_order_cap`** — лимит висящих **`pending_payment`**.
- **`create_order`** — INSERT заказа **`pending_payment`**.
- **`set_invoice_provider_metadata`** — провайдер счёта (ckassa / ckassa_bc / lava / multi).
- **`touch_bc_payment_claim_if_allowed`** — только для BC «Я оплатил».
- **`get_order`**, **`amount_due_external`** — UI админам и сверка в webhook.

### 21.6. Связанные тесты и смоук

- Логика Ckassa webhook: **`tests/test_ckassa_webhook.py`** (при изменении протокола прогонять вместе с **`partner_api`**).
- После деплоя: **`curl`** на **`/v1/payments/ckassa-webhook`** с тестовым телом не должен отдавать 5xx из-за rate limit middleware (в коде зафиксирован ответ 200 + `fail` при ошибках — см. комментарии в **`ckassa_webhook.py`**).

---

*Документ описывает состояние кодовой базы в репозитории `telegram_stars_shop_bot`. При расхождении с прод-сервером приоритет имеет фактическая выкладка и `shared/.env` на хосте.*
