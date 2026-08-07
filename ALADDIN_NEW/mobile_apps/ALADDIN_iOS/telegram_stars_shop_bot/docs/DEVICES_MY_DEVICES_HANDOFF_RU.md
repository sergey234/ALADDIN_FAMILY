# Мои устройства — handoff для ML / разработчика

**Дата канона:** 2026-07-23  
**Продукт:** AiMonkeyVPN (Telegram-бот + сайт `get.aladdin-ai.ru`)  
**SSOT рантайма:** Contabo `185.225.233.150` (`aladdin-shop-vpn-api` + `aladdin-telegram-bot` + `aladdin-partner-api`)  
**Этот документ** — итоговая картина «что сделали и как устроено».  
Старый план `DEVICES_SHOWCASE_PLAN.md` частично устарел (там ещё фигурируют платные доп. устройства и незакрытые чеклисты).

---

## 1. Продуктовый канон (финал)

| Правило | Как есть |
|--------|----------|
| Сколько устройств в подписке | **Строго 1** |
| Платные «+ устройство» | **Отменено** (задача d06 снята; пользователь отказался от 99 ₽) |
| Своя ссылка Happ | У каждого устройства свой `/sub/{opaque}` |
| После отвязки | Старая ссылка **мертва** (404); можно **бесплатно** создать замену (снова 1 из 1) |
| Слово «слот» | Только во внутреннем коде (`vpn_device_slots`). В UI: **устройство** |
| Каналы | **get.** = полная панель; **бот** = карточный пульт + ссылка в браузер |
| Mini App | **Не в v1** (d17 later) |

Потолок в API жёстко: `get_capacity()` всегда возвращает `max = 1`, даже если в БД `device_limit` / `paid_device_capacity` больше.

---

## 2. Задачи (все id из реализации)

| ID | Что | Статус |
|----|-----|--------|
| **d00** | Словарь UI: без «слот»; тексты под ТЗ Миши | ✅ |
| **d01** | Правила: 1 в подписке, отвязка убивает ссылку | ✅ |
| **d01b** | Канон ужесточён: **строго 1**, без платных доп. | ✅ |
| **d02** | Schema `vpn_device_slots` + миграция opaque → устройство #1 | ✅ Contabo |
| **d03** | `GET /sub/{opaque}` dual-lookup (slot → account fallback); touch UA/kind; revoke → 404 | ✅ |
| **d04** | Internal API: list / create / rename / revoke (+ purchase оставлен, но UI не продаёт) | ✅ |
| **d05** | HWID: лимит = active devices ≤ capacity; сброс чистит hwid слота | ✅ |
| **d06** | Оплата «+ устройство» 99 ₽ | ❌ **CANCELLED** |
| **d07** | get.: вкладка Устройства, прогресс N из M, сетка, QR/copy | ✅ |
| **d08** | get.: add / rename / revoke confirm / цвета бара | ✅ |
| **d09** | Базовый экран в боте (тизер) | ✅ → заменён d09b |
| **d09b** | Бот: карточка 1 устройства + ‹› + Copy/QR/Rename/Отвязать | ✅ |
| **d09c** | Бот: «Полная панель в браузере» → `get.…/devices` (не Mini App) | ✅ |
| **d10** | Пуш в бот: «Новое устройство подключилось: …» | ✅ |
| **d11** | Админ: `/admin_vpn_devices`, `/admin_vpn_device_revoke`, reset HWID | ✅ |
| **d12** | Pytest VPN: `tests/test_device_slots.py` | ✅ |
| **d13** | Pytest бот-карточки + SPA panel checks | ✅ |
| **d14** | Деплой Contabo (VPN + bot + partner SPA) | ✅ |
| **d15** | Ручной смоук бот + get. + Happ | ⏳ чеклист (не блокер кода) |
| **d16** | Канон UX: сайт=витрина, бот=пульт | ✅ |
| **d17** | Telegram Mini App = та же панель | ⏳ later / F5 |
| **kb-fix** | Sticky ReplyKeyboard: Remove + handlers | ✅ |

---

## 3. Архитектура (как читает ML)

```
┌─────────────────┐     session/cookie      ┌──────────────────────┐
│ get. SPA        │ ── /web/devices* ─────► │ partner_api          │
│ index.html      │                         │ web_checkout.py      │
└─────────────────┘                         └──────────┬───────────┘
                                                       │ vpn_api_client
┌─────────────────┐     post_devices_*                 │
│ Telegram bot    │ ───────────────────────────────────┤
│ vpn.py +        │                                    ▼
│ vpn_devices_ux  │                         ┌──────────────────────┐
└─────────────────┘                         │ aladdin_shop_vpn_api │
                                            │ device_slots.py      │
┌─────────────────┐     GET /sub/{opaque}   │ routes/health.py     │
│ Happ client     │ ───────────────────────►│ routes/internal.py   │
└─────────────────┘                         │ vpn.db               │
                                            └──────────────────────┘
```

- **vpn.db** (VPN API) — устройства, opaque, HWID, first_connected.  
- **shop.db** (бот/partner) — заказы, аккаунты web, дедуп пушей first-connect.  
- Публичная ссылка Happ: `/sub/{opaque}` на VPN API (через nginx).  
- Страница заказа на сайте `/o/…` — **не** Happ-ссылка.

---

## 4. Backend VPN API

### 4.1 Таблица `vpn_device_slots`

Файл: `aladdin_shop_vpn_api/aladdin_shop_vpn_api/device_slots.py`

Ключевые поля:

- `account_id`, `telegram_user_id`, `shop_account_id`
- `opaque_token` UNIQUE — токен для Happ
- `display_name`, `device_kind` (iphone/android/…/unknown)
- `first_connected_at`, `last_seen_at`, `hwid_hash`
- `revoked_at` — если не NULL, ссылка мертва
- `included_in_plan`, `purchase_id` (legacy под отменённый d06)

Миграция при старте: существующий `vpn_accounts.opaque_token` → активный слот #1 **с тем же токеном** (Happ у старых юзеров не ломается).

### 4.2 Capacity

```python
# get_capacity → (used_active, 1)
# create_device при used >= 1 → ValueError("device_limit_reached")
# revoke_device → revoked_at=now, hwid_hash=NULL; used падает → можно create снова
```

### 4.3 Dual lookup `/sub`

`resolve_account_by_opaque`:

1. Ищет строку в `vpn_device_slots` по opaque (и не revoked).  
2. Fallback: `vpn_accounts.opaque_token` (до/без слота).  
3. При первом успешном доступе: `first_connected_at`, kind из UA, автоимя если пользователь не переименовал.

Файл маршрута: `routes/health.py` → `GET /sub/{opaque_token}`.

### 4.4 Internal API (HMAC / internal auth как у остального VPN API)

Префикс internal (см. `routes/internal.py`):

| Метод | Назначение |
|-------|------------|
| `POST /devices/list` | used/max/can_add + devices[] + subscription_url |
| `POST /devices/create` | новое устройство если used &lt; max |
| `POST /devices/rename` | display_name ≤ 64 |
| `POST /devices/revoke` | soft-revoke |
| `POST /devices/purchase` | +ёмкости (оставлено в API; **UI не вызывает** после d01b) |

Ответ list отдаёт `max=1`, `can_add=(used < 1)`.

---

## 5. Сайт get. — вкладка «Устройства»

**Файлы:**

- SPA: `partner_api/static/web/index.html`
- API-прокси: `partner_api/routers/web_checkout.py`
- Публичный deep-link: `GET /devices` → та же SPA

**Роуты partner:**

- `GET  /web/devices` — list  
- `POST /web/devices/create`  
- `POST /web/devices/rename`  
- `POST /web/devices/revoke`  

Авторизация: `account_id` + `session_secret` (как web-checkout).

**UI:**

- Прогресс «Занято N из M» + цвет бара (ok/warn/bad)
- Сетка карточек: имя, статус, дата, `<details>` со ссылкой / QR / rename / отвязать
- Confirm отвязки: *«Вы точно хотите отвязать…? Ссылка станет недействительной»*
- Если лимит: кнопка add disabled + текст «отвяжите текущее, затем подключите новое»
- Роутинг SPA: `/devices`, `/#subs`, … — **не** сбрасывать `/devices` → `/` при смене вкладки (баг пофикшен)

Тест: `telegram_stars_shop_bot/tests/test_web_devices_panel.py`.

---

## 6. Бот — «Мои устройства» (карточный пульт)

**Файлы:**

- UX/HTML/клавиатуры: `bot/services/vpn_devices_ux.py`
- Хендлеры: `bot/handlers/vpn.py` (`vpn:devices*`)
- Клиент VPN: `bot/services/vpn_api_client.py` (`post_devices_*`)
- Вход с экрана VPN: callback `vpn:devices` (см. также `vpn_user_links.py`)

**Экран:**

```
🏠 Мои устройства
Занято 1 из 1
████████  🔴/🟡/🟢

📱 Имя
🟢 в сети сейчас / 🟡 был в сети / ⚪️ ожидает подключения
Подключен …
Устройство 1 из 1

[‹] [›]          — только если устройств > 1 (редко при каноне 1)
[Скопировать ссылку Happ]
[Показать QR]
[Переименовать]  — FSM: «введите имя»
[Отвязать]       — confirm → revyes
[Подключить устройство] — если can_add (после revoke)
[🌐 Полная панель в браузере] — URL get./devices
[⬅️ К VPN]
```

Rename: callback `vpn:devices:ren:{id}` → FSM → `post_devices_rename` → обновление карточки.  
QR: фото/изображение QR по `subscription_url`.

---

## 7. Пуш первого подключения (d10)

**Файлы:**

- `bot/services/vpn_device_first_notify.py` — loop ~60s
- `bot/services/vpn_device_first_notify_repo.py` — дедуп в shop.db
- Старт loop: `bot/main.py` (рядом с другими background tasks)

Логика: читает `vpn_device_slots` где `first_connected_at` свежий (lookback), не шлёт повторно по `slot_id`, текст вида:

> Новое устройство подключилось: **iPhone**  
> Управлять ссылкой и именем — «Мои устройства».

Кнопка → `vpn:devices`.

Env (типично): `VPN_DEVICE_FIRST_NOTIFY_ENABLED`, interval seconds.

---

## 8. Админ / support (d11)

В `bot/handlers/admin.py`:

| Команда | Действие |
|---------|----------|
| `/admin_vpn_devices <telegram_id>` | Список устройств |
| `/admin_vpn_device_revoke <tid> <device_id>` | Точечная отвязка |
| `/admin_vpn_device_reset <telegram_id>` | Сброс HWID (смена телефона) |

(Также есть общие VPN admin revoke/extend — не путать с device revoke.)

---

## 9. HWID / анти-шаринг (d05)

- Лимит устройств = число **active** (не revoked) слотов ≤ capacity (1).  
- Сброс HWID админом чистит `hwid_hash` у слота, чтобы тот же `/sub` можно было привязать к новому железу.  
- Gate аккаунта (старый) сохранён; слоты — дополнительный уровень.

Тесты: `aladdin_shop_vpn_api/tests/test_device_slots.py`, `test_device_binding.py`, `test_device_reset.py`.

---

## 10. UX-канон каналов (d16)

| Канал | Роль |
|-------|------|
| **get.aladdin-ai.ru** | Полная витрина: сетка, прогресс, rename на месте, QR, аккордеон |
| **Telegram bot** | Пульт: одна карточка + действия + дверь на сайт |
| Связка | «Полная панель в браузере» → обычный HTTPS URL `/devices` |
| Mini App | d17 — позже, тот же SPA |

**Не делаем в v1:** сетка 2×3 текстом в чате; спам N сообщениями; продажа доп. устройств.

---

## 11. Карта файлов (быстрый индекс)

### VPN API

- `aladdin_shop_vpn_api/aladdin_shop_vpn_api/device_slots.py` — SSOT слотов/ёмкости  
- `aladdin_shop_vpn_api/aladdin_shop_vpn_api/routes/internal.py` — devices/*  
- `aladdin_shop_vpn_api/aladdin_shop_vpn_api/routes/health.py` — GET /sub/{opaque}  
- `aladdin_shop_vpn_api/tests/test_device_slots.py`

### Bot

- `telegram_stars_shop_bot/bot/services/vpn_devices_ux.py`  
- `telegram_stars_shop_bot/bot/handlers/vpn.py` (блок `vpn:devices*`)  
- `telegram_stars_shop_bot/bot/services/vpn_api_client.py`  
- `telegram_stars_shop_bot/bot/services/vpn_device_first_notify.py`  
- `telegram_stars_shop_bot/bot/handlers/admin.py` (admin_vpn_device*)  
- `telegram_stars_shop_bot/tests/test_vpn_device_first_notify.py` (+ bot card tests из d13)

### Web

- `telegram_stars_shop_bot/partner_api/static/web/index.html` — tab `devices`  
- `telegram_stars_shop_bot/partner_api/routers/web_checkout.py` — `/web/devices*` + `/devices`  
- `telegram_stars_shop_bot/tests/test_web_devices_panel.py`

### Планы / соседние доки

- `docs/DEVICES_MY_DEVICES_HANDOFF_RU.md` — **этот файл (канон «что сделали»)**  
- `docs/DEVICES_SHOWCASE_PLAN.md` — исторический план (устарел по d06 / статусам)  
- ТЗ Миши §3 — продуктовый эталон текстов/сценариев панели  

---

## 12. Деплой Contabo (операционка)

Сервисы:

- `aladdin-shop-vpn-api.service` — vpn.db + `/sub` + internal devices  
- `aladdin-telegram-bot.service` — пульт + notify loop  
- `aladdin-partner-api.service` — get. SPA + `/web/devices*`  

Типичные пути:

- App: `/opt/aladdin-telegram-shop-bot/current_app`  
- VPN API: отдельный `/opt/...` shop-vpn (как на хосте)  
- SSH: `ssh -i ~/.ssh/aladdin_server root@185.225.233.150`

После правок слотов — рестарт **vpn-api**; после SPA/partner — **partner-api**; после bot UX/notify — **telegram-bot**.

Полный скрипт дерева бота: `telegram_stars_shop_bot/scripts/deploy_prod.sh` (не путать с точечным rsync файлов).

---

## 13. Смоук-чеклист (d15 — ручной)

1. **Бот:** VPN → Мои устройства → карточка 1/1, copy, QR, rename, отвязка confirm → add снова.  
2. **get.:** `/devices` сразу открывает вкладку Устройства (не мигает «Главная»).  
3. **Happ:** старый `/sub` после миграции жив; после revoke — 404; новый create — новый opaque.  
4. **Пуш:** первый коннект нового слота → одно сообщение в TG (без спама истории).  
5. **Админ:** list + revoke по device_id.  
6. **Регресс:** web-checkout оплата, `/o/…` ≠ `/sub/…`.

---

## 14. Что сознательно НЕ сделано

- Платные доп. устройства / товар 99 ₽ / кнопка «+ N ₽» в UI (**d06 cancelled**).  
- Telegram Mini App (**d17**).  
- Уменьшение «купленной ёмкости» при revoke (неактуально при max=1).  
- Фейковый realtime «в сети» без `last_seen` (статус = last_seen &lt; N минут).

---

## 15. Инварианты для любой будущей правки

1. Пользователю нигде не писать «слот».  
2. `get_capacity` ceiling = **1**, пока продукт не вернёт multi-device явно.  
3. Revoke всегда убивает opaque; create даёт новый.  
4. Миграция не ротирует opaque уже выданных живых ссылок без явной задачи.  
5. Бот не дублирует сетку сайта текстом — только карточка + ссылка на get.  
6. `/o/` (заказ) и `/sub/` (Happ) никогда не смешивать в копирайте.

---

*Конец handoff. При конфликте с `DEVICES_SHOWCASE_PLAN.md` приоритет у этого файла.*
