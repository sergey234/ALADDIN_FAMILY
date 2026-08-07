# План: быстрый `/start` + «🎁 Промокод»

**Дата:** 2026-07-31  
**Код:** `telegram_stars_shop_bot/`  
**Трекер:** [`START_PERF_AND_PROMO_TODO_TRACKER.md`](./START_PERF_AND_PROMO_TODO_TRACKER.md)  
**Порядок:** сначала **Part A** (perf), затем **Part B** (promo).

---

## Part A — Почему долго первый `/start`

### Диагноз (новый пользователь, до выбора языка)

Канал / капча / combined-онбординг **не** на критическом пути первого ответа.

| # | Причина | Где | Влияние |
|---|---------|-----|---------|
| 1 | Невидимая чистка ReplyKeyboard: `answer` + `delete` до UI | `handlers/common.py` → `strip_sticky_reply_keyboard` | 2 RTT Telegram до любого экрана |
| 2 | Каждый раз upload `monkey.jpg` вместо `file_id` | `services/branding_media.py` → `hero_photo_input` | multipart ~90 КБ на каждый язык-экран |
| 3 | Цепочка await БД до фото | upsert → throttle → analytics×2 → account → acquisition | лишние commits на критическом пути |

### Цель Part A

Сократить время до **видимого** экрана выбора языка без изменения онбординг-логики (язык → combined → капча → хаб).

### Шаги Part A

1. **A1 — `file_id` first:** в `hero_photo_input` предпочитать `START_PHOTO_FILE_ID` / кэш; локальный файл — fallback; опционально сохранить `file_id` после первой успешной отправки.
2. **A2 — strip не блокирует:** для новых / без sticky KB не ждать strip; либо после первого UI; либо `create_task`.
3. **A3 — UI раньше bookkeeping:** после минимального upsert сразу `_send_language_pick`; analytics / acquisition / account — фон (`create_task`) или один batched commit.
4. **A4 — тесты + smoke:** pytest на branding/start; Contabo — замер субъективного TTFB `/start`.
5. **A5 — деплой Contabo (+ MAIN sync).**

### Не менять (Part A)

- Combined channel+terms, captcha, hub content.
- Требование канала / согласие.

---

## Part B — ТЗ «🎁 Промокод»

### Цель

В **«👤 Личный кабинет»** (не «Профиль») кнопка **«🎁 Промокод»**: активация кодов → скидка/бонус при подходящем заказе.  
Универсальный слой для акций, блогеров, персональных офферов.

### UX

1. Кабинет → «🎁 Промокод».
2. Экран: текст из ТЗ + «✏️ Ввести промокод».
3. FSM ждёт ввод → автопроверка → сообщения успеха/ошибок из ТЗ.

### Типы кодов (комбинируемые флаги)

- **Общий** — много пользователей.
- **Персональный** — whitelist Telegram user id(s).
- **Лимитированный** — `max_activations`; после лимита недоступен.

### Reward (расширяемый)

- `%` / фикс ₽.
- Scope: Stars / Premium / VPN / весь магазин.
- Поле `reward_kind` в БД — новые типы бонусов без перестройки ядра.

### Ограничения на код

- `starts_at` / `ends_at`
- `max_activations`
- once per user
- new users only (опционально)

### Проверка (порядок)

exists → active → dates → limit → already used → personal match → new-user rule.

### Интеграция без ломки магазина

| Слой | Действие |
|------|----------|
| Активация | Привязка кода к user (активный promo) |
| Цена | `quote_product` → скидка в `rub_after_discounts` (новая колонка `promo_discount_rub` опционально) |
| Оплата / checkout flow | **не трогаем** — берут итоговую сумму как сейчас |
| Списание | при paid подходящего заказа (скидка); иные reward — при активации по типу |
| Реф/% env | не ломаем; промо **рядом**, не вместо |

### Админка

Команда в духе `/contest`: название, тип, размер, scope, даты, лимит, once-per-user, personal ids.  
Регистрация в `admin_command_catalog`.

### Файлы (ориентир)

| Зона | Путь |
|------|------|
| KB кабинета | `bot/keyboards/shop_kb.py` → `profile_inline_kb_rows_prefix` |
| Handler/FSM | `bot/handlers/` + states |
| Repo/schema | `bot/db/database.py`, `bot/services/promo_*` |
| Pricing | `bot/services/pricing.py` → `quote_product` |
| Admin | `bot/handlers/admin.py`, `admin_command_catalog.py` |
| Тесты | `tests/test_promo_*.py` |

### Не менять (Part B)

- Оформление заказа, оплату, процесс покупки «с нуля».
- Существующую бизнес-логику магазина (только точечный hook в quote).
- Названия UI: везде **«Личный кабинет»**, не «Профиль».

### Порядок Part B

1. Docs/schema + repo (коды, активации, active bind).
2. UX кабинет + FSM + copy сообщений.
3. Pricing hook + persist на заказе.
4. Redeem on paid.
5. Admin create/list.
6. pytest + Contabo deploy + smoke.

---

## Критерии готовности

**A:** первый `/start` заметно быстрее; язык без лишнего upload/strip на критическом пути.  
**B:** активация из кабинета; скидка на подходящем SKU; лимиты/ошибки по ТЗ; админ создаёт код; checkout/payment без рефакторинга.
