# Крипто-оплата: Crypto Pay (@CryptoBot) + xRocket Pay

Канон для фазы **2-*** в `telegram_stars_shop_bot`: **только USDT в сети TRC20** для счетов через провайдеров; два канала — **Crypto Pay** и **xRocket Pay** (оба дают ссылку на оплату в Telegram). Секреты только в `.env` / менеджере секретов, **никогда** в git и публичных чатах.

**Важно:** `CRYPTO_PAY_API_TOKEN` — это **не** `BOT_TOKEN` магазина (формат `123456:AA…`). Для Crypto Pay нужен **API-токен приложения** из @CryptoBot → Crypto Pay → Create App (`/pay`). Если подставить BOT_TOKEN, в логах будет предупреждение, счета не создадутся.

Официальная справка Crypto Pay: [Help Center](https://help.send.tg/en/articles/10279948-crypto-pay-api). xRocket Pay: [Pay API overview](https://docs.xrocket.tg/api/pay/pay-api-overview), OpenAPI: `https://pay.xrocket.tg/api-json` (реализация: `https://pay.xrocket.exchange`, заголовок **`Rocket-Pay-Key`**).

---

## 0. Прод: `shared/.env` + вебхуки (авто `paid`)

Секреты только в **`shared/.env` на сервере** (канон деплоя: `/opt/aladdin-telegram-shop-bot/shared/.env`), **не** в git. После правок: `systemctl restart aladdin-partner-api.service` (и при необходимости бота).

### 0.1 Минимум в `.env` для крипто-счетов и курса

| Переменная | Значение |
|------------|----------|
| `CRYPTO_PAY_ENABLED` | `true` |
| `CRYPTO_PAY_API_TOKEN` | Токен приложения Crypto Pay (**не** `BOT_TOKEN` вида `123456:AA…`). |
| `XROCKET_PAY_ENABLED` | `true` (если нужен второй канал счёта). |
| `XROCKET_PAY_API_KEY` | Rocket-Pay-Key из xRocket (Rocket Pay → API Token). |
| `USDT_RUB_RATE` | Желательно: ₽ за 1 USDT (если `0` — при недоступности `getExchangeRates` берётся `USD_RUB_RATE`). |

Без осмысленного **`USDT_RUB_RATE`** или **`USD_RUB_RATE`** сумма в USDT может не посчитаться, если Crypto Pay временно не отдаёт курсы.

### 0.2 URL вебхуков в кабинетах (публичный HTTPS → Partner API)

Подставьте свой хост (тот же базовый URL, что открыт для LAVA hook, если API одно и то же):

| Куда зарегистрировать | URL |
|------------------------|-----|
| Crypto Pay (приложение / Webhooks) | `POST https://<ваш-домен>/v1/payments/crypto-pay-webhook` |
| xRocket Pay (вебхуки приложения) | `POST https://<ваш-домен>/v1/payments/xrocket-webhook` |

Подписи и идемпотентность — в **разделе 2**, таблица «Вебхуки Partner API». После оплаты заказ из **`pending_payment`** переходит в **`paid`**, срабатывает `emit_order_status_changed` (как для LAVA).

### 0.25 Проверка на сервере (без утечки секретов)

Если в боте при выборе крипты показывается **ручной** блок (memo, «оператор отметит оплату»), значит **`crypto_pay_invoice_api_ready` и `xrocket_invoice_api_ready` оба ложны**: в `shared/.env` нет **`CRYPTO_PAY_ENABLED=true` + непустого `CRYPTO_PAY_API_TOKEN`** (и аналогично для xRocket). Пустые строки вроде `CRYPTO_PAY_API_TOKEN=` **не считаются** заданным токеном.

Проверка только имён ключей (значения не печатаются):

```bash
ENV=/opt/aladdin-telegram-shop-bot/shared/.env
grep -E '^CRYPTO_PAY_|^XROCKET_' "$ENV" | sed 's/=.*/=…/'
```

Ожидается, что присутствуют как минимум строки `CRYPTO_PAY_ENABLED`, `CRYPTO_PAY_API_TOKEN`, при необходимости блок xRocket. Шаблон всех полей — **`telegram_stars_shop_bot/env.example`**. На проде ключи должны быть **в том же файле**, что подключён в `systemctl cat aladdin-telegram-bot.service` как `EnvironmentFile=` (канон: **`shared/.env`**).

**Важно:** после получения токена в **@CryptoBot → Crypto Pay → Create App → `/pay`** вручную выставьте в `shared/.env`:

- `CRYPTO_PAY_ENABLED=true`
- `CRYPTO_PAY_API_TOKEN=<токен приложения, не BOT_TOKEN>`

и выполните `systemctl restart` для **трёх** unit’ов магазина. Пока токен пустой, Partner API на вебхуке может отвечать `CRYPTO_PAY_API_TOKEN is not set` — это нормально до заполнения.

**Вебхуки и HTTPS:** в кабинетах Crypto Pay / xRocket обычно требуется **публичный HTTPS**. Если Partner API доступен только как `http://IP:8090`, для продакшена поднимите **домен + TLS** (nginx) на те же пути `…/v1/payments/crypto-pay-webhook` и `…/xrocket-webhook`. Смоук с хоста: `curl -sS http://127.0.0.1:8090/health`.

### 0.3 Смоук перед боем

1. `curl -sS -m 8 https://<ваш-домен>/health` → `{"status":"ok"}`.
2. Малый тестовый заказ → оплата через Crypto Pay и/или xRocket → в БД статус заказа **`paid`** без ручной кнопки «Оплачен».
3. Повторный POST того же вебхука → ответ с **`duplicate": true`** (идемпотентность).

Подробнее по полям тел и заголовкам — **раздел 2** («Вебхуки Partner API») и комментарии в `env.example`.

---

## 1. Боты и хосты API

| Сеть | Бот в Telegram | Хост HTTPS API (origin без пути `/api`) |
|------|----------------|----------------------------------------|
| Mainnet | [@CryptoBot](https://t.me/CryptoBot) | `https://pay.crypt.bot` |
| Testnet | [@CryptoTestnetBot](https://t.me/CryptoTestnetBot) | `https://testnet-pay.crypt.bot` |

Токен приложения выдаётся в Crypto Pay → **Create App** после команды **`/pay`** в соответствующем боте (mainnet или testnet). Токен **mainnet** и **testnet** разные; в `.env` должен быть ровно один активный набор: `CRYPTO_PAY_API_TOKEN` + согласованный `CRYPTO_PAY_TESTNET`.

В коде origin по умолчанию выбирается из `CRYPTO_PAY_TESTNET`; при необходимости переопределение — `CRYPTO_PAY_API_HOST` (см. `env.example`).

---

## 2. Переменные окружения (фаза 2, слой спеки)

| Переменная | Назначение |
|------------|------------|
| `CRYPTO_PAY_ENABLED` | `true` — создавать счёт через Crypto Pay при наличии `CRYPTO_PAY_API_TOKEN`. |
| `CRYPTO_PAY_API_TOKEN` | **Только** API-токен приложения Crypto Pay (см. выше). Не BOT_TOKEN. |
| `CRYPTO_PAY_TESTNET` | `true` — хост `testnet-pay.crypt.bot` и токен из @CryptoTestnetBot. |
| `CRYPTO_PAY_API_HOST` | Опционально полный origin или hostname; пусто = таблица §1. |
| `CRYPTO_PAY_DEFAULT_ASSET` | Устарело: в коде для Crypto Pay всегда **`USDT`** (TRC20); иное значение игнорируется с предупреждением в логах. |
| `CRYPTO_PAY_INVOICE_EXPIRE_SECONDS` | `expires_in` счёта Crypto Pay (сек); согласовать с `ORDER_PENDING_PAYMENT_EXPIRE_MINUTES`. |
| `CRYPTO_PAY_PAID_BTN_URL` / `CRYPTO_PAY_WALLET_FALLBACK` | См. `env.example`. |
| `XROCKET_PAY_ENABLED` | `true` — второй провайдер, счёт `POST /tg-invoices`. |
| `XROCKET_PAY_API_KEY` | Заголовок **`Rocket-Pay-Key`** (Rocket Pay → API Token в боте xRocket). |
| `XROCKET_PAY_API_BASE` | По умолчанию `https://pay.xrocket.exchange`. |
| `CRYPTO_SHOW_TON_MANUAL` | `true` (по умолчанию) — в **ручном** блоке показывать TON из `CRYPTO_TON`; `false` — только USDT TRC20 в тексте ручной оплаты. |
| `CRYPTO_USDT_TRC20` | Адрес приёма **USDT TRC20** для **ручного** блока (сеть Tron, формат `T…`). Если счета Crypto Pay / xRocket создаются, покупатель в первую очередь идёт по их ссылкам; это поле — запасной путь или режим без провайдеров. |
| `CRYPTO_TON` | Адрес/реквизиты для **ручного** TON (вебхуков на TON в этом боте нет). |
| `AUTO_FULFILL_*` | Автовыдача после `paid` (план **п.37**): мастер-флаг, по типу Stars/Premium, потолок ₽, лимит попыток — см. `env.example` и `docs/IMPLEMENTATION_PLAN_AND_TASKS.md` §37.0. |

**Вебхуки Partner API (авто `pending_payment` → `paid`):**

| Провайдер | Метод | Подпись |
|-----------|--------|---------|
| Crypto Pay | `POST /v1/payments/crypto-pay-webhook` | Заголовок `crypto-pay-api-signature`: `hex(HMAC-SHA256(SHA256(CRYPTO_PAY_API_TOKEN), сырое тело))` (как pycryptopay-sdk; при несовпадении сервер дополнительно пробует компактный `json.dumps` от распарсенного JSON). |
| xRocket Pay | `POST /v1/payments/xrocket-webhook` | Заголовок `rocket-pay-signature`: `hex(HMAC-SHA256(SHA256(XROCKET_PAY_API_KEY), UTF-8 тело))` (как xrocket-pay-api-sdk; при несовпадении пробуется компактная пересборка JSON). |

Идемпотентность: `cryptobot:<invoice_id>` и `xrocket:<data.id>`. Тело Crypto Pay: `update_type: invoice_paid`, счёт в поле `payload`; xRocket: `type: invoicePay`, счёт в `data`, строка заказа в `data.payload` (`SB1|…`).

---

## 3. Политика суммы: ₽ в магазине vs USDT (TRC20) в счёте

**Инвариант каталога (без изменений):** позиции в `products.yaml` в **USD**, в боте пользователь видит и платит в **₽** по `USD_RUB_RATE` (и скидки/рефка как сейчас).

**Инвариант провайдеров:** для **Crypto Pay** и **xRocket** в инвойс уходит только **USDT** (у Telegram / xRocket это USDT в экосистеме **TRC20**; другие сети в этом боте не предлагаются).

**Политика v1:**

1. Сумма **к доплате в ₽** — как в `2-crypto-payload` / `amount_due_external`.
2. Пересчёт в **USDT**: функция `resolve_rub_per_usdt(settings)` — сначала **`getExchangeRates`** Crypto Pay (если задан `CRYPTO_PAY_API_TOKEN`), иначе пары нет → **`USDT_RUB_RATE`** или **`USD_RUB_RATE`**. Тот же курс используется для **xRocket**, чтобы оба счёта были согласованы с одной базой (при отключённом Crypto Pay курс берётся только из `.env`).
3. Crypto Pay: `createInvoice` с `asset=USDT` и строкой `amount`. xRocket: `POST /tg-invoices` с `currency: "USDT"` и числом `amount`.
4. На вебхуках (задача `2-crypto-webhook` и отдельно xRocket) — сверка `payload`, суммы и идемпотентность.

**Задача `8-crypto-fx-policy` (закрыта):** канон — этот раздел; базовое правило — **фиксация суммы USDT в инвойсе на момент `createInvoice` / `POST /tg-invoices`**, без пересчёта «задним числом» на вебхуке. Дрейф курса и повторный инвойс см. `docs/EDGE_CASES.md` и `PAYMENT_CHECKOUT_INVOICE_COOLDOWN_SECONDS` в `env.example`.

### 3.1 Поле `payload` в `createInvoice` (привязка к заказу)

Канон строки (ASCII, до 512 символов):

```text
SB1|<order_id>|<due_kop>
```

- **`SB1`** — версия схемы (AIMonkeyStars shop payload v1; префикс на wire не меняется при ребрендинге).
- **`order_id`** — целое `orders.id`.
- **`due_kop`** — сумма **к оплате через Crypto Pay в ₽**, выраженная в **копейках**: `round(due_rub, 2) * 100`, целое число (кодирование через `round`, без двоичного дрейфа float).

**Откуда `due_rub`:** то же, что `orders_repo.amount_due_external(order)`:

- `payment_method = crypto` — вся сумма заказа после скидок (`rub_after_discounts`, баланс не применялся).
- `payment_method = mix_crypto` — только внешняя доплата: `rub_after_discounts − balance_applied_rub`.

Инвойс Crypto Pay выставляется **только** для `crypto` и `mix_crypto`; для `fiat` / `mix_fiat` / баланса payload не используется.

Разбор и проверка: `bot/services/crypto_pay_payload.py` (`encode_crypto_invoice_payload`, `decode_crypto_invoice_payload`, `verify_decoded_payload_against_order`).

**Срок жизни счёта (`expires_in`):** функция `crypto_invoice_expires_in_seconds(settings)` — минимум 60 секунд и не больше окна авто-истечения заказа (`ORDER_PENDING_PAYMENT_EXPIRE_MINUTES` × 60), если TTL заказа включён; иначе только `CRYPTO_PAY_INVOICE_EXPIRE_SECONDS`.

### 3.2 Выставление счёта в боте (`2-crypto-invoice` + xRocket)

- **`shop._present_crypto_checkout`:** если настроен Crypto Pay — создаётся счёт; если настроен xRocket — второй счёт; в чате **одна или две URL-кнопки** (USDT TRC20).
- Реализация: `bot/services/crypto_pay_api.py`, `bot/services/xrocket_pay_api.py`, клавиатура `crypto_providers_kb`.
- **Без голых кошельков** при успешной ссылке(ах). Fallback на ручной адрес USDT — только `CRYPTO_PAY_WALLET_FALLBACK=true`.
- **`CRYPTO_PAY_PAID_BTN_URL`**: уходит в Crypto Pay (`paid_btn_*`) и в xRocket (`callbackUrl`), если задан https-URL.

### 3.3 Цепочка для покупателя (логика шагов)

| Способ | Шаги | Когда заказ «Оплачен» | Выдача товара |
|--------|------|------------------------|---------------|
| **LAVA (₽)** | Кнопка → страница LAVA (карта / СБП и т.д. по проекту) | Вебхук LAVA на Partner API | Дальше оператор: «В работе» → «Выдан» (вручную или полуавтоматически вне этого документа). |
| **Crypto Pay / xRocket (USDT TRC20)** | Кнопка → счёт в Telegram | Вебхук Crypto Pay или xRocket на Partner API | То же: после `paid` — очередь оператора. |
| **Ручной USDT / TON** (`CRYPTO_USDT_TRC20`, `CRYPTO_TON`) | Текст с адресом и memo `ORDER{id}` | Вручную в админке после сверки (**вебхука нет**) | То же. |

Итого: **приём денег** для LAVA и провайдеров USDT — автоматический до статуса **`paid`** при правильных URL вебхуков и `.env`. **Отправка Stars/Premium пользователю** в текущей версии — через оператора после `paid`, это не мгновенный самовыкуп из бота.

---

## 4. HTTP API (кратко для реализации)

**Crypto Pay**

- Только **HTTPS**.
- Заголовок **`Crypto-Pay-API-Token`** = `CRYPTO_PAY_API_TOKEN`.
- Вызовы: `{origin}/api/{method}` (query-параметры как в SDK).
- Смоук: **`getMe`**.

**xRocket Pay**

- База: `XROCKET_PAY_API_BASE` (prod: `https://pay.xrocket.exchange`).
- Заголовок **`Rocket-Pay-Key`** = `XROCKET_PAY_API_KEY`.
- Создание счёта: **`POST /tg-invoices`** JSON тела по OpenAPI.

---

## 5. Вебхуки (реализовано)

Эндпоинты Partner API: **`POST /v1/payments/crypto-pay-webhook`**, **`POST /v1/payments/xrocket-webhook`** — подпись тела, идемпотентность, сверка `SB1|order_id|due_kop` с заказом. Повторные доставки — ответ **200**, дубликаты помечаются в JSON.

---

## 6. Смоук testnet

1. `CRYPTO_PAY_TESTNET=true`, токен из @CryptoTestnetBot, `CRYPTO_PAY_ENABLED=true`.
2. `getMe` → 200.
3. Тестовый заказ → счёт в Telegram → оплата testnet → вебхук на Partner API → заказ **`paid`**.

---

## 7. Связь с задачами плана

| ID | Содержание |
|----|------------|
| `2-crypto-spec` | Этот документ + `Settings` / `env.example` |
| `2-crypto-payload` | ✅ `SB1|order_id|due_kop`, `crypto_pay_payload.py`, срок `expires_in` vs заказ |
| `2-crypto-invoice` | ✅ `bot/services/crypto_pay_api.py` — `getExchangeRates` + `createInvoice`, кнопка из `pay_url` / `bot_invoice_url`; чекаут в `shop._present_crypto_checkout` |
| `2-crypto-webhook` | ✅ `POST …/crypto-pay-webhook` + xRocket, подписи, idempotency |
| `8-crypto-fx-policy` | Расширение политики курса и тесты |
