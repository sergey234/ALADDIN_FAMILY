# Family Habit Custom — Hybrid (Variant 2) SSOT

**Дата:** 2026-10-10  
**Ids:** `fhc-*`  
**Rule:** `.cursor/rules/family-habit-custom-hybrid-todo-ssot.mdc`  
**Экран:** Family → **Family reminders** → **ниже Medicine** → блок «Свои»  
**Сборка симулятора / Archive:** только после явного **GO на сборку**  
**Деплой API MAIN:** только после явного **GO на деплой**

---

## Продукт (канон Variant 2)

| Слой | Решение |
|------|---------|
| UI | 4 шаблона без изменений. Под Medicine: **Свои напоминания** → список → **+ Добавить** |
| Модель | `config.custom: [FamilyHabitCustomReminder]` — до **5** на семью |
| Расписание | Как вода/лекарство: окно `start→end`, интервал **15 / 30 / 60 / 120** (+ clamp своих минут 15…180), max **12** слотов/день |
| Режим «как перед сном» | Опция **Один раз в день** (как `wind_down` / `phone_down`) — один календарный триггер |
| Ping | `ping_until_done` + interval 15…30 + max/день — тот же Due-ping chain |
| Пуш | Category `family_habit`, action **Сделано**, deep link `aladdin://habit/done?preset=custom.<id>` |
| Кому | Те же `member_ids` + «на этом телефоне» (policy без изменений) |
| Медали/XP | **Не в v1** — только надёжные пуши + Done clear/reschedule |
| Disclaimer | Короткий, если title похож на лекарство / health keywords |
| Локаль | RU+EN, без hardcoded RU в EN UI |

### Модель custom (JSON)

```json
{
  "id": "uuid",
  "title": "Позвонить маме",
  "emoji": "📞",
  "enabled": true,
  "mode": "window",
  "hour": 9,
  "minute": 0,
  "end_hour": 21,
  "end_minute": 0,
  "interval_minutes": 60,
  "ping_until_done": false,
  "ping_interval_minutes": 20,
  "ping_max_per_day": 6
}
```

`mode`: `window` | `once_daily` | `once_at` (v1.1).

| mode | Смысл | Уведомление |
|------|--------|-------------|
| `window` | Каждый день в окне + интервал | Как вода/лекарство |
| `once_daily` | Каждый день в одно время | Как Отход ко сну |
| `once_at` | **Одна дата и время** (событие) | `UNCalendarNotificationTrigger` без repeats; после срабатывания `enabled=false` |

**Идеал для «наметить дату»:** в редакторе «Свои» — переключатель режимов: Повторять ежедневно / Окно дня / **Один раз (дата)**.  
Для `once_at` поле `fire_at` (ISO8601, timezone устройства). Лимит слотов не применяется (1 пуш + optional due-ping до Done в тот же день).  
Это **fhc-15** (после fhc-01…11), не блокирует v1 hybrid.

### Уведомления — паритет с wind_down / water

| Событие | Как у | Реализация |
|---------|-------|------------|
| Основной слот(и) | water window / wind_down once | `UNCalendarNotificationTrigger` repeats / one-shot chain |
| Тело пуша | title + короткий body | `family_habit_custom_push_body_fmt` |
| Кнопка Сделано | family_habit category | тот же `FAMILY_HABIT_DONE` |
| Due-ping | medicine/water ping | `family.habit.custom.<id>.due.N` |
| После Done | clear pending + reschedule | как `handleDone` |
| Bootstrap / scene active | FamilyHabitRemindersBootstrap | reschedule всех custom |
| Auth denied | баннер | как сейчас у секции |
| Тест-пуш (опционально) | wellness wind_down test | кнопка «Проверить» в редакторе custom |

---

## GATES (закрыть до «готово»)

| # | Gate | Доказательство |
|---|------|----------------|
| G1 | Под Medicine виден блок «Свои» + Add; лимит 5 | UI smoke / a11y id |
| G2 | Window + once_daily ставят pending `family.habit.custom.*` | log pending count / unit slots |
| G3 | Done на custom чистит due + reschedule | unit / manual push |
| G4 | GET/POST `/api/family/habit-reminders` принимает `custom[]`, старые клиенты без лома | curl + decode old JSON |
| G5 | RU+EN локаль; disclaimer на health-like title | keys + screenshot EN |
| G6 | Нет mock/sfm; ошибки сети человеческие | code review |
| G7 | Static verify script PASS | `scripts/verify_family_habit_custom_static.sh` |
| G8 | Device/Sim QA | только после **GO на сборку** |

---

## TODO (`fhc-*`) + чеклист после каждой задачи

### fhc-00 — Registry + GATES
- [ ] Этот файл в git / актуален
- [ ] Cursor TODO создан (`merge: true`)
- **Чеклист:** REGISTRY ✅ · GATES записаны · ids `fhc-*` не пересекают `hab-*`

### fhc-01 — Модель iOS `FamilyHabitCustomReminder`
- [ ] Struct Codable + `mode` window/once_daily
- [ ] `FamilyHabitRemindersConfig.custom: […]` default `[]`
- [ ] Decode backward-compatible (нет `custom` → `[]`)
- [ ] Clamp: title 1…40, max 5, interval 15…180, slots ≤12
- **Чеклист:** decode старого JSON без crash · unit test round-trip

### fhc-02 — Интервалы UI (15/30/60/120 + custom minutes)
- [ ] Enum/chips как water, плюс 15/30
- [ ] Опционально «свои минуты» с clamp
- **Чеклист:** nearest() · summary line без «термостат»-мусора

### fhc-03 — Scheduler: custom window + once_daily
- [ ] Prefix `family.habit.custom.<id>.`
- [ ] Window = `scheduleWindowSlots` path (как water/medicine)
- [ ] once_daily = `scheduleDaily` path (как wind_down)
- [ ] Due-ping chain per custom id
- [ ] clearPending / handleDone понимают `custom.<id>`
- **Чеклист:** pending ids в логе · Done clears due · reschedule after Done

### fhc-04 — Deep link + NotificationManager
- [ ] Router: `aladdin://habit/done?preset=custom.<uuid>`
- [ ] Category/action без новой category (reuse `family_habit`)
- **Чеклист:** tap Done → XP optional skip · clear works · no crash

### fhc-05 — UI блок под Medicine
- [ ] Заголовок «Свои напоминания» / «Your reminders»
- [ ] Список: emoji · title · summary · toggle
- [ ] `+ Добавить` → sheet/editor (название, emoji chips, mode, окно/время, interval, ping, disclaimer)
- [ ] Edit / delete / reorder optional (edit+delete mandatory)
- [ ] Empty state понятный
- [ ] a11y identifiers `family_habit_custom_*`
- **Чеклист:** EN+RU · Storm card style · ниже medicine · лимит 5 с human error

### fhc-06 — Подсказки при создании (зелёная шляпа)
- [ ] 4–6 quick templates: Позвонить / Зарядка / Проверить дверь / Перерыв / … (не лекарство)
- [ ] Тап подставляет title+emoji, дальше своё расписание
- **Чеклист:** не путать с 4 системными пресетами сверху

### fhc-07 — Сервер store + router
- [ ] `family_habit_reminders_store.py`: normalize `custom[]`, max 5, validate fields
- [ ] GET/POST без breaking presets
- [ ] Messages/body defaults EN-safe on server if any
- **Чеклист:** unit/pytest normalize · curl GET round-trip (после GO deploy)

### fhc-08 — APIService / Service sync
- [ ] Client encode/decode `custom`
- [ ] Save → reschedule local
- [ ] Soft-fail network copy (localized)
- **Чеклист:** offline draft? no — save requires network like today · honest error

### fhc-09 — Локализация RU+EN
- [ ] Все ключи `family_habit_custom_*`
- [ ] Disclaimer health-like
- [ ] Interval labels 15/30 min
- **Чеклист:** grep hardcoded RU in new UI = 0

### fhc-10 — Unit tests
- [ ] Model clamp / max 5
- [ ] Slot math window + once
- [ ] Policy unchanged
- [ ] Decode legacy config
- **Чеклист:** tests green locally (без full sim если нет GO)

### fhc-11 — Static verify script
- [ ] `scripts/verify_family_habit_custom_static.sh` — keys, model fields, scheduler prefix, store custom
- **Чеклист:** script exit 0

### fhc-12 — Deploy API (GO)
- [ ] Backup → scp store (+ router if needed) → py_compile → restart → curl
- **Чеклист:** OpenAPI/smoke · **только после GO на деплой**

### fhc-13 — Device / Sim QA (GO)
- [ ] Create 1 custom once_daily → push fires
- [ ] Create 1 custom window 60m → multiple pending
- [ ] Ping until Done → due → Done stops
- [ ] 6th Add blocked
- [ ] EN UI labels
- **Чеклист:** journal 3 bullets · **только после GO на сборку**

### fhc-14 — Plan–Fact close
- [ ] Все G1–G8 PASS или явно отложены с причиной
- [ ] REGISTRY статусы ✅
- **Чеклист:** нет «готово» без evidence

### fhc-15 — once_at (конкретная дата) — после v1
- [ ] mode `once_at` + `fire_at` ISO8601
- [ ] DatePicker в редакторе «Один раз (дата)»
- [ ] One-shot trigger, no repeats; after fire/Done → enabled=false
- **Чеклист:** не путать с once_daily · лимит 5 всё ещё действует

---

## Порядок работы

```
fhc-00 → fhc-01 → fhc-02 → fhc-03 → fhc-04 → fhc-05 → fhc-06
       → fhc-07 → fhc-08 → fhc-09 → fhc-10 → fhc-11
       → [GO deploy] fhc-12 → [GO build] fhc-13 → fhc-14
       → [optional] fhc-15 once_at
```

Медали/XP custom — **отдельный** follow-up (не блокирует v1).

## Файлы (ожидаемый blast)

| Файл | Роль |
|------|------|
| `Core/Family/FamilyHabitRemindersModels.swift` | custom model |
| `Core/Family/FamilyHabitRemindersScheduler.swift` | schedule/clear/done |
| `Core/Family/FamilyHabitRemindersService.swift` | sync |
| `Core/Family/UnicornDeepLinkRouter.swift` | done deep link |
| `Shared/Components/FamilyHabitRemindersSection.swift` | UI под medicine |
| `Core/Localization/LocalizationManager.swift` | RU+EN |
| `app/services/family_habit_reminders_store.py` | server normalize |
| `Tests/UnitTests/*FamilyHabit*` | tests |
| `scripts/verify_family_habit_custom_static.sh` | gate G7 |

## Статусы (обновлять)

| id | Статус |
|----|--------|
| fhc-00 | ✅ registry + GATES |
| fhc-01…fhc-11 | ⏳ pending (код) |
| fhc-12 | ⏳ pending — **GO на деплой** |
| fhc-13 | ⏳ pending — **GO на сборку** |
| fhc-14 | ⏳ pending |
