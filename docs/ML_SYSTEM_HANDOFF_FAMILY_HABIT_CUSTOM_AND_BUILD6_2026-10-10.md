# Handoff для другой ML-системы — Family Habit Custom + Build 6 + CI fix

**Дата:** 2026-10-10  
**Репозиторий:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
**Ветка:** только `master` · remote `git@github.com:sergey234/ALADDIN_FAMILY.git`  
**App:** `ai.aladdin` · Team `B3WGHSWL79` · Path B нумерация с 1  
**Канон сборки:** `docs/RELEASE_BUILD_PROMPT.md`

---

## 0. Кто ты и правила

1. Читай `docs/ML_SYSTEM_START_HERE.md` §0A Mech Pilot + GATES.
2. iOS-коммиты **только на `master`**. Не коммитить `telegram_stars_shop_bot/` и `.env`.
3. `xcodebuild` / Simulator / Archive — только после фразы владельца **GO на сборку**.
4. Deploy / SSH на MAIN — только после **GO на деплой**.
5. Push — только после **GO на push**.
6. TODO ids `fhc-*`: merge-only · SSOT `.cursor/FAMILY_HABIT_CUSTOM_HYBRID_TASK_REGISTRY.md` · rule `family-habit-custom-hybrid-todo-ssot.mdc`.
7. Не продолжать личные TF номера 247/248 — Path B: сейчас **build 6**.

---

## 1. Зачем эта работа (продукт)

На экране **Family → Family reminders** уже есть 4 шаблона: вода, убрать телефон, перед сном, лекарство.  
Владелец хочет, чтобы пользователь мог добавить **свои** напоминания (название + расписание + пуши), красиво и понятно, **под блоком Medicine**.

**Variant 2 — Hybrid (канон):**
- Шаблоны сверху не трогать.
- Ниже: «Свои напоминания» → список → **+ Добавить**.
- Настройки как у воды/лекарства: окно дня, интервал 15/30/60/120, ping until Done, кому слать, пуш с кнопкой **Сделано**.
- Лимит **5** своих на семью.
- Медали/XP для custom — **не в v1**.

### Можно ли наметить конкретную дату?

| Сейчас в плане v1 | Идеал (v1.1 / `fhc-15`) |
|-------------------|-------------------------|
| `once_daily` — каждый день в одно время (как Отход ко сну) | `once_at` — **одна дата+время** |
| `window` — каждый день в окне | DatePicker в редакторе «Один раз (дата)» |

**Идеальное решение:** третий mode `once_at` + поле `fire_at` (ISO8601).  
Локальный пуш: `UNCalendarNotificationTrigger` **без** `repeats`. После срабатывания или Done → `enabled=false`.  
Не строить полноценный Calendar app — только одноразовое событие внутри Family reminders.

---

## 2. Что уже сделано в этом чате (до handoff)

### 2.1 Home map / IoT / локаль / ошибки сети (в коммите build 6)

| Проблема | Решение |
|----------|---------|
| RU «Умная камера / термостат» на EN UI | Ключи `iot_seed_*` → **Пример: камера / Пример: климат** · EN **Example: camera / Example: climate** |
| «HTTP ошибка» / смесь RU в EN | `NetworkManager` без RU fallback; `NetworkError.userFacingDetail` режет кириллицу |
| 504 на Devices | human copy `network_error_http_504`; soft IoT load |
| Resume IoT 404 | На MAIN **нет** `POST /api/iot/.../unblock` в OpenAPI — клиент показывает `home_map_iot_resume_unavailable`; нужен **GO деплой** `app/routers/iot.py` unblock |
| Unicorn crop | Пересобран `Resources/Companion/unicorn_master.png` из CONCEPT |

**Коммит:** `6e77e6e9` — `feat(build 6): Home map IoT loc, network EN errors, unicorn PNG, bump 5→6`  
**Bump Path B:** везде **5 → 6** (не 248!). Team `B3WGHSWL79`.  
`PREV_BUILD=6` / `NEXT_BUILD=7` в `docs/RELEASE_BUILD_PROMPT.md`.

### 2.2 CI Archive упал (`logs_103160727163.zip`)

Checkout был **`6e77e6e9`**. Ошибки:

```
FamilyLocalStore has no member 'loadPersistedMembers'
GeofenceGeocodingService has no member 'reverseGeocodeLocality'
GeofenceGeocodingService has no member 'isDemoPlaceholderAddress'
```

**Причина:** вызовы уже в git, а реализации лежали **только локально uncommitted** в:
- `Core/Managers/FamilyLocalStore.swift`
- `Core/Services/GeofenceGeocodingService.swift`

**Фикс:** закоммитить и запушить эти два файла (hotfix поверх build 6).

### 2.3 План Custom Habits (ещё не реализован в коде)

SSOT: `.cursor/FAMILY_HABIT_CUSTOM_HYBRID_TASK_REGISTRY.md`  
Ids: `fhc-00` ✅ … `fhc-01`…`fhc-14` ⏳  
GATES G1–G8 в registry.

Порядок кода:
```
fhc-01 model → fhc-02 intervals → fhc-03 scheduler → fhc-04 deeplink
→ fhc-05 UI → fhc-06 quick templates → fhc-07 server → fhc-08 sync
→ fhc-09 loc → fhc-10 tests → fhc-11 static verify
→ [GO deploy] fhc-12 → [GO build] fhc-13 → fhc-14
→ [optional] fhc-15 once_at date
```

---

## 3. Как делать Custom Habits (технически)

### 3.1 Модель

Расширить `FamilyHabitRemindersConfig`:

```swift
var custom: [FamilyHabitCustomReminder] // max 5
```

`FamilyHabitCustomReminder`: `id`, `title`, `emoji`, `enabled`, `mode` (`window`|`once_daily`|позже `once_at`),  
`hour/minute/end_hour/end_minute/interval_minutes`, ping fields как у preset.

Decode: нет `custom` → `[]` (backward compatible).

### 3.2 Уведомления (паритет wind_down / water)

| Mode | Путь | ID prefix |
|------|------|-----------|
| window | `scheduleWindowSlots` (как water/medicine) | `family.habit.custom.<id>.` |
| once_daily | `scheduleDaily` (как wind_down) | `family.habit.custom.<id>` |
| once_at | one-shot calendar, no repeats | `family.habit.custom.<id>.at` |

- Category: **`family_habit`** (reuse), action **Сделано** = `FAMILY_HABIT_DONE`
- Due-ping: `family.habit.custom.<id>.due.N` если `ping_until_done`
- Done → `clearPending` + `reschedule` (как `FamilyHabitRemindersScheduler.handleDone`)
- Bootstrap: `FamilyHabitRemindersBootstrap` уже тянет members через `loadPersistedMembers` — после CI fix это компилируется
- Deep link: `aladdin://habit/done?preset=custom.<uuid>` в `UnicornDeepLinkRouter`

Файлы:
- `Core/Family/FamilyHabitRemindersModels.swift`
- `Core/Family/FamilyHabitRemindersScheduler.swift`
- `Core/Family/FamilyHabitRemindersService.swift`
- `Shared/Components/FamilyHabitRemindersSection.swift` — UI **под Medicine**
- `app/services/family_habit_reminders_store.py` — normalize `custom[]`
- `Core/Localization/LocalizationManager.swift` — `family_habit_custom_*` RU+EN

### 3.3 Сервер

`GET/POST /api/family/habit-reminders` — добавить `custom` в config JSON.  
Не ломать существующие `presets` / `member_ids`.  
Max 5, title length clamp, validate mode/intervals.

Deploy на 🇷🇺 MAIN (`149.154.65.180`) — только **GO на деплой**, runbook `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md`.

### 3.4 UI (красота)

Под Medicine:
1. Заголовок «Свои напоминания» / «Your reminders»
2. Empty: коротко «Добавьте своё — например позвонить или зарядка»
3. Row: emoji · title · summary · toggle
4. `+ Добавить` → sheet: название, emoji chips, mode, время/окно, interval chips, ping, disclaimer если health-like title
5. Quick templates (не путать с 4 системными): Позвонить / Зарядка / Дверь / Перерыв
6. a11y: `family_habit_custom_*`

---

## 4. Связанные прод-дыры (не custom, но знать)

| Issue | Статус |
|-------|--------|
| IoT `unblock` 404 на MAIN | Код в `app/routers/iot.py` есть, **не в OpenAPI прода** — нужен деплой |
| Demo IoT names | Клиент мапит на Пример: камера / климат; сиды в DB могут ещё быть RU |
| Devices 504 | nginx timeout `/api/devices` — UX смягчён; ops отдельно |

---

## 5. Чеклист следующей ML (старт сессии)

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
git rev-parse --show-toplevel   # must be ALADDIN_iOS
git branch --show-current       # must be master
git status --short
/usr/bin/grep -A1 'CFBundleVersion' Info.plist
/usr/bin/grep 'static let buildNumber' Core/Config/AppConfig.swift
```

1. Открыть `.cursor/FAMILY_HABIT_CUSTOM_HYBRID_TASK_REGISTRY.md`
2. TodoWrite `merge: true` только по `fhc-*`
3. Начать с **fhc-01** (модель), чеклист после каждой задачи в REGISTRY
4. Не запускать sim без GO
5. После кода: commit на master (если просили) → push только по GO
6. CI: убедиться что `FamilyLocalStore.loadPersistedMembers` и geocoding helpers **в git**

---

## 6. GATES закрытия Custom v1

| Gate | Evidence |
|------|----------|
| G1 UI под Medicine + max 5 | screenshot / a11y |
| G2 pending `family.habit.custom.*` | log |
| G3 Done clears due | unit/manual |
| G4 API custom[] compatible | curl |
| G5 RU+EN | keys |
| G6 no mock | review |
| G7 static verify | script |
| G8 Device QA | GO build |

---

## 7. Контакты канона в репо

| Тема | Файл |
|------|------|
| Custom habits SSOT | `.cursor/FAMILY_HABIT_CUSTOM_HYBRID_TASK_REGISTRY.md` |
| Старые habits addendum | `.cursor/FAMILY_HABITS_PLACES_ADDENDUM_TASK_REGISTRY.md` (`hab-*` ✅) |
| Release bump | `docs/RELEASE_BUILD_PROMPT.md` |
| Server | `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md` |
| Этот handoff | `docs/ML_SYSTEM_HANDOFF_FAMILY_HABIT_CUSTOM_AND_BUILD6_2026-10-10.md` |

**Не пушить секреты. Не класть bot в iOS-релиз.**
