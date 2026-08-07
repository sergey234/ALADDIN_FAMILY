# План: Lava support + legal + trial expire (2026-08-05)

**Источник:** замечания службы поддержки Lava по `@AiMonkeyStars_bot` + жалоба владельца на «пробник не гасится».  
**Прод проверен:** Contabo `185.225.233.150`, сайт `aimonkeystars.ru`, vpn.db / xray / bot `.env`.

---

## Статус внедрения (2026-08-05 вечер)

| ID | Статус |
|----|--------|
| lava-2 in-bot support → только админам | ✅ деплой Contabo |
| lava-3 таблица сроков в боте | ✅ |
| lava-1 `/v1/legal/refund` + refunds.html | ✅ |
| trial-6 lifecycle + sync shop.db | ✅ 1 delivered / 12 expired / 4 paid_after_trial |
| trial-8 72ч + Happ в expire DM | ✅ |
| trial-7 metrics/orphan | ⬜ |
| lava-9 ответ Lava | ⬜ владелец |

### Прод trial сейчас

| Метрика | N |
|---------|---|
| trial active | **1** |
| trial expired | **12** |
| trial_used_at всего | **17** |
| paid after trial (active) | **4** |

## 0. Вердикт одной фразой

| Тема | Вердикт |
|------|---------|
| **Кнопка «Поддержка»** | Сломана по смыслу: `SUPPORT_URL` = сам бот `t.me/AiMonkeyStars_bot` → петля, нет чата с человеком |
| **Сроки возврата на сайте** | В тексте **уже есть** (полный `/v1/legal/refund` + таблица на `/refunds.html`); Lava видит дыру в **боте** (нет таблицы как в шаблоне) и в **канале связи** |
| **Trial не гасится** | Control-plane на Contabo **сейчас гасит** (`paid_until` → `vpn_expired` + peer-down). Жалоба чаще = Happ-кэш / путаница paid vs trial / UX `vpn_trial_requests=pending` / исторические зомби. Нужен harden + сверка с пользователями |

---

## 1. Замечания Lava — разбор

### 1.1 «Кнопка поддержки не работает»

**Факт прод:**
```text
SUPPORT_URL=https://t.me/AiMonkeyStars_bot
SUPPORT_USERNAME=
```

Кнопка «💬 Написать в поддержку» / префиллы открывают **тот же** `@AiMonkeyStars_bot`.  
Для Lava и покупателя это не канал к оператору → «не работает».

**Нужно:**
1. Завести/подтвердить **человеческий** контакт (`@support_xxx` или отдельный support-бот с inbox).
2. В `.env`: `SUPPORT_URL=https://t.me/<HUMAN>` (или `SUPPORT_USERNAME=`), **не** shop-bot.
3. Smoke: из раздела Поддержка URL уходит **не** на `@AiMonkeyStars_bot`.
4. Опционально: свободный текст в боте → тикет в admin chat (assistant escalate), если человека нет 24/7.

### 1.2 «Не прописаны сроки и условия как в шаблоне — на сайте и в боте»

**Сайт (проверено curl 200):**

| URL | Сроки Lava |
|-----|------------|
| `https://aimonkeystars.ru/v1/legal/refund` | ✅ полный текст: 3 дн / 14 кал / 10 раб / 14 раб / «выдан» |
| `https://aimonkeystars.ru/refunds.html` | ✅ **таблица** как в цитате Lava |
| `https://aimonkeystars.ru/v1/legal/offer` | ✅ те же сроки в оферте |

**Бот (проверено):**
- URLs в env: `REFUND_POLICY_URL`, `PUBLIC_OFFER_URL`, … → aim ✅  
- Экран «Политика магазина» — **только ссылки**, без таблицы.  
- `refund_policy_blurb_html` — короткий абзац (нет явной строки «5 мин–24 ч», «возврат денег до 14 раб. дн.» как в шаблоне).

**Почему Lava права частично:** шаблон = **таблица сроков + рабочая Поддержка**. Полный `/v1/legal/refund` — стена текста без таблицы; в боте таблицы нет.

**Нужно:**
1. В `/v1/legal/refund` (и/или канон `legal/refund_policy_ru.txt`) добавить ту же **таблицу Сроки**, что на `refunds.html`.  
2. В боте: экран поддержки / «Политика» / оплата — **явный блок сроков** (копия таблицы Lava) + ссылка на полный текст.  
3. Кнопка «Политика возвратов» должна открываться с первого экрана Поддержки (не только вложенно).  
4. Сверить Lava Success/Fail URL на aim (уже отмечалось ✅ get-E) — не смешивать с этим окном правок.

### 1.3 Таблица Lava (канон для UX)

| Пункт | Условие |
|-------|---------|
| После выдачи («выдан») | Возврату не подлежат |
| Оказание услуги | Факт 5 мин–24 ч; макс. 3 календарных дня с оплаты |
| Подача заявки | 14 календарных дней после просрочки 3-дневного срока, если не «выдан» |
| Рассмотрение | До 10 рабочих дней |
| Возврат денег | До 14 рабочих дней после одобрения, те же реквизиты, полный объём |

---

## 2. Trial: почему «не заканчивается» — все причины

### 2.1 Как должно работать (канон)

1. Trial: `paid_until = now + VPN_TRIAL_HOURS` (прод **72**), `account_kind=trial`.  
2. Реферал: другу **не** добавляют вторые 3 дня (`friend_days=0`); пригласившему **+1** день.  
3. Гашение: **vpn-worker** → `status=vpn_expired`, rotate `opaque_token`, `xray-peer-down` / `wg-peer-down`.  
4. Бот **не** гасит туннель — только напоминания.

### 2.2 Живой снимок Contabo (2026-08-05)

| Проверка | Результат |
|----------|-----------|
| `aladdin-shop-vpn-worker` | active, expire в логах |
| `VPN_*_POST_EXPIRE_SCRIPT` | заданы |
| Overdue still `vpn_active` | **0** |
| Expired trial с UUID в БД | **0** |
| Чистый trial active | 1 шт., внутри 72ч (~43ч) |
| `/sub/` expired token | **403** |
| Orphan UUID в xray vs active | **2** (мелкий хвост) |

**Вывод:** «код не срабатывает совсем» — **не** текущая картина. Проблема = смесь UX/кэша/путаницы + harden.

### 2.3 Гипотезы (по вероятности)

| # | Причина | Почему похоже | Что сделать |
|---|---------|---------------|-------------|
| H1 | **Happ кэш** конфига после expire | `/sub/` 403, UUID снят, но старый VLESS в приложении ещё «зелёный» до reconnect | UX: после trial_expired — «Обновите подписку / удалите профиль»; smoke на реальном телефоне |
| H2 | Путают **paid** (после оплаты/года) с «пробником» | В БД есть `trial_used_at` + `account_kind=paid` + `paid_until` 2027 | Админ: `/admin_vpn_trial_status`; в UI явно «оплачено до …» |
| H3 | **+1 день** рефереру / платные ref 7+14 | grants в shop.db есть | Ок по правилам; текст trial не обещать «ровно 3 дня всем» |
| H4 | `vpn_trial_requests.status='pending'` навсегда | Все trial_req на прод **pending**, даже после expire | Баг учёта shop.db → статусы completed/expired |
| H5 | Исторические зомби до peer-down | Сейчас почти чисто; 2 orphan UUID | Разовый reconcile xray↔db |
| H6 | Worker/скрипт fail (check=False) | Сейчас OK; регресс возможен | Алерт если `vpn_expired` без снятия UUID / orphan count |
| H7 | Ожидание «календарные 3 дня» vs **72 часа** | 72ч с вечера = 4-й календарный день | Копирайт: «72 часа (3 суток)» |
| H8 | Деплой «правили» только бот/текст, не worker | Worker крутится с 31.07 | Любой fix expire — рестарт worker + smoke SQL |

### 2.4 Наилучший режим на будущее (anti-recurrence)

1. **SSOT expire** = vpn-worker + peer-down (уже так); бот никогда не «обещает» гашение сам.  
2. **Reconcile cron** (раз в час): UUID в xray ∉ active DB → remove + alert.  
3. **Метрика:** `vpn_trial_overdue_active`, `xray_orphan_clients`.  
4. **Shop.db:** обновлять `vpn_trial_requests` → `provisioned` / `expired`.  
5. **E2E smoke:** lab tid → provision trial 2 мин → expire → assert 403 `/sub/` + UUID absent in config + Happ refresh = disconnect.  
6. **Админ кнопка:** «просроченные trial ещё active» = 0.  
7. Не смешивать окна: trial harden ≠ Lava URL ≠ entry cutover.

---

## 3. План работ (порядок)

### P0 — Lava (касса / комплаенс) — отдельное GO

1. Сменить `SUPPORT_URL` на человека.  
2. Таблица сроков в боте + усилить `/v1/legal/refund` таблицей.  
3. Ответ Lava: ссылки + скрин Поддержки с рабочим URL.

### P1 — Trial harden

1. SQL+Happ drill на 1–2 жалобах (TID).  
2. Fix `vpn_trial_requests` lifecycle.  
3. Orphan reconcile + alert.  
4. Копирайт 72ч; явный статус trial vs paid.

### P2 — UX resilience (связь с VPN F02/F03)

«Если VPN не коннектится / trial кончился» — 4 шага в боте.

---

## 4. Cursor TODO ids

См. TodoWrite: `lava-*`, `trial-*`.

---

## 5. Запреты

- Не ставить `SUPPORT_URL` = shop-bot.  
- Не «чинить trial» только текстом в боте без сверки vpn.db/xray.  
- Не stop 149 / не мешать Lava-окно с VPN entry cutover.  
- Секреты не в чат/git.
