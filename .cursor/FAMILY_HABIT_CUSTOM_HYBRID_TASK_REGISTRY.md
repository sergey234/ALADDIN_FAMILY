# Family Habit Custom — Hybrid (Variant 2) SSOT

**Дата:** 2026-10-10 · **Обновлено:** 2026-10-10 (ship rules + fhc-15…17)  
**Ids:** `fhc-*`  
**Rule:** `.cursor/rules/family-habit-custom-hybrid-todo-ssot.mdc`  
**Handoff:** `docs/ML_SYSTEM_HANDOFF_FAMILY_HABIT_CUSTOM_AND_BUILD6_2026-10-10.md`  
**Экран:** Family → **Family reminders** → **ниже Medicine** → блок «Свои»  
**Сборка симулятора / Archive:** только после явного **GO на сборку**  
**Деплой API MAIN:** только после явного **GO на деплой**

---

## Ship rules (обязательно — вписать в каждую релевантную задачу)

| # | Правило | Куда в коде |
|---|---------|-------------|
| S1 | **Soft-fail sync, не wipe presets** — ошибка сети/4xx/старый API не сбрасывает water/medicine/wind_down/phone_down; custom либо остаётся в draft UI, либо честный error | `fhc-08` |
| S2 | **Test-push must** в редакторе custom (кнопка «Проверить») — как wind_down test; без ожидания слота | `fhc-05` |
| S3 | **Локаль в одном пакете с UI** — ключи `family_habit_custom_*` RU+EN закрываются вместе с `fhc-05` (не «потом») | `fhc-05` + `fhc-09` |
| S4 | **G4 = old↔new** — (a) старый клиент + новый сервер с `custom[]`; (b) новый клиент + старый сервер без `custom` / unknown fields | `fhc-07`, `fhc-08`, `fhc-12` |
| S5 | **Device-local time** — триггеры по часам телефона; TZ travel / DST edge **out of scope v1** (зафиксировано, не чинить «в дороге») | G9 · docs only |

**Порядок ship:** код G1–G7 → **GO deploy** `fhc-12` (curl G4 оба направления) → **GO build** `fhc-13` → close.  
Не закрывать Device QA, пока MAIN не принимает `custom[]`.

---

## Продукт (канон Variant 2)

| Слой | Решение |
|------|---------|
| UI | 4 шаблона без изменений. Под Medicine: **Свои напоминания** → список → **+ Добавить** |
| Модель | `config.custom: [FamilyHabitCustomReminder]` — до **5** на семью |
| Расписание | Как вода/лекарство: окно `start→end`, интервал **15 / 30 / 60 / 120** (+ clamp своих минут 15…180), max **12** слотов/день |
| Режим «как перед сном» | **Один раз в день** (`once_daily`) — как `wind_down` |
| Режим «на дату» | **`once_at`** — после G1–G7, **до маркетинга фичи** (`fhc-15`), не в критическом пути первых коммитов |
| Ping | `ping_until_done` + interval 15…30 + max/день — тот же Due-ping chain |
| Пуш | Category **`family_habit`** (reuse), action **Сделано**, deep link `aladdin://habit/done?preset=custom.<id>` |
| Кому | Те же `member_ids` + фраза в sheet «на этом телефоне / как Family reminders» (policy без изменений) |
| Медали/XP | **Не делаем** (см. § Не делаем) |
| Disclaimer | Короткий, если title похож на лекарство / health keywords |
| Локаль | RU+EN вместе с UI; без hardcoded RU в EN |
| Reorder | **Делаем** — `fhc-16` после стабильного списка |
| Analytics | **Делаем** — лёгкие события create/done **без** текста title — `fhc-17` |
| Widget / App Intent «Сделано» | **Не делаем сейчас** |

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
  "ping_max_per_day": 6,
  "sort_order": 0,
  "fire_at": null
}
```

`mode`: `window` | `once_daily` | `once_at` (код mode в модели с `fhc-01`; schedule `once_at` — в `fhc-15`).  
`fire_at`: ISO8601 или `null` (только для `once_at`).  
`sort_order`: int для reorder (`fhc-16`); default = индекс в массиве.

| mode | Смысл | Уведомление |
|------|--------|-------------|
| `window` | Каждый день в окне + интервал | Как вода/лекарство |
| `once_daily` | Каждый день в одно время | Как Отход ко сну |
| `once_at` | **Одна дата и время** | `UNCalendarNotificationTrigger` без repeats; после fire/Done → `enabled=false` |

В редакторе (после `fhc-15`): Повторять ежедневно / Окно дня / **Один раз (дата)**.  
До `fhc-15`: третий режим можно показать disabled «Скоро» **или** скрыть — не обещать в маркетинге до закрытия `fhc-15` + QA.

### Уведомления — паритет с wind_down / water

| Событие | Как у | Реализация |
|---------|-------|------------|
| Основной слот(и) | water window / wind_down once | `UNCalendarNotificationTrigger` |
| Тело пуша | title + короткий body | `family_habit_custom_push_body_fmt` |
| Кнопка Сделано | family_habit category | `FAMILY_HABIT_DONE` |
| Due-ping | medicine/water ping | `family.habit.custom.<id>.due.N` |
| После Done | clear + reschedule | как `handleDone` |
| Bootstrap | FamilyHabitRemindersBootstrap | reschedule всех custom |
| Auth denied | баннер секции | как сейчас |
| **Test-push** | wind_down test | **must** — «Проверить» в редакторе |
| Логи | — | только `id` / `mode` / counts — **не** title |

---

## Не делаем (жёсткий stop-list)

| Идея | Почему нет |
|------|------------|
| Полноценный календарь / RRULE / weekly | Другой продукт |
| Отдельная notification category | Дубли, баги Done |
| Медали / XP на custom | Размывает v1, спорный геймдизайн |
| Offline-first / CRDT | Overkill при текущем sync |
| Геофенс «у двери» | Другой домен (places) |
| AI-подсказки привычек | Шум + доверие |
| Cloud push вместо local UN | Ломает паритет, сложнее |
| Medicine dosing / «таблетка 2×» | Юр. / health риск |
| `once_at` в критическом пути первых коммитов v1 | DatePicker + `fire_at` + disable-after-fire раздувает QA до G1–G7 |
| Mock API «пока сервер не готов» | Против no-mock |
| Widget / App Intent «Сделано» | Не сейчас — отдельный follow-up после стабильного Done |
| Аналитика текста title | Privacy — только event names + ids |

---

## GATES (закрыть до «готово» / маркетинга)

| # | Gate | Доказательство |
|---|------|----------------|
| G1 | Под Medicine блок «Свои» + Add; лимит 5 | UI smoke / a11y |
| G2 | Window + once_daily → pending `family.habit.custom.*` | log / unit slots |
| G3 | Done на custom чистит due + reschedule | unit / manual |
| G4 | **Dual compat:** new server accepts `custom[]` + old JSON OK; new client tolerates server **without** `custom` (no wipe, honest error) | curl оба + decode unit |
| G5 | RU+EN + disclaimer health-like; keys с UI | keys + EN screenshot |
| G6 | Нет mock/sfm; human network errors | review |
| G7 | Static verify PASS | `scripts/verify_family_habit_custom_static.sh` |
| G8 | Device/Sim QA | только после **GO на сборку** и после **GO deploy** |
| G9 | Device-local time accepted; TZ travel out of scope | записано в REGISTRY / UI не обещает «по миру» |

**Маркетинг фичи** — только после G1–G8 (+ `fhc-15` если рекламируем «на дату»).

---

## TODO (`fhc-*`) + чеклист + как делать лучше

### fhc-00 — Registry + GATES
- [x] Этот файл актуален (ship rules S1–S5, stop-list, fhc-15…17)
- [ ] Cursor TODO создан (`merge: true`) по открытым `fhc-*`
- **Чеклист:** REGISTRY ✅ · ids не пересекают `hab-*`

### fhc-01 — Модель iOS `FamilyHabitCustomReminder`
- [x] Struct Codable: `id`, `title`, `emoji`, `enabled`, `mode`, schedule fields, ping fields, `sort_order`, optional `fire_at`
- [x] `mode` enum: `window` | `once_daily` | `once_at` (unknown → `modeRecognized=false`, skip schedule, не crash)
- [x] `FamilyHabitRemindersConfig.custom` default `[]`
- [x] Decode: нет `custom` → `[]`; лишние поля ignore
- [x] Clamp: title trim 1…40, empty reject, emoji 1 grapheme, max 5, interval 15…180, slots ≤12
- [x] Unit: `FamilyHabitCustomReminderTests` in `FamilyHabitRemindersPolicyTests.swift`
- **Как лучше:** сразу заложить `fire_at`/`sort_order`/`once_at` в decode, schedule `once_at` не включать до `fhc-15`.
- **Чеклист:** legacy JSON round-trip · unit clamp ✅ (код; xcodebuild tests — после GO на сборку)

### fhc-02 — Интервалы UI (15/30/60/120 + custom minutes)
- [x] Enum `FamilyHabitCustomInterval` chips 15/30/60/120 + `nearest` / `selection` / `clampMinutes`
- [x] Optional свои минуты с clamp (15…180) + `setIntervalMinutes` + `interval_custom_fmt`
- [x] Prefill: window 09–21 / **60**; once_daily **21:00** (`prefill(mode:)`)
- [x] `scheduleSummaryLine` — только interval · окно / время (без IoT-мусора)
- [x] Loc keys RU+EN для interval chips (минимум для summary; полный UI — fhc-05/09)
- [x] Unit tests nearest / clamp / prefill / summary
- **Как лучше:** `nearest()` к канону chips; summary без IoT-мусора.
- **Чеклист:** nearest · summary чистый ✅ (chips View — в fhc-05 на этом enum)

### fhc-03 — Scheduler: custom window + once_daily
- [x] Prefix `family.habit.custom.<id>.` (+ daily `family.habit.custom.<id>`)
- [x] Window = shared `scheduleWindowSlots`; once_daily = shared `scheduleDaily`
- [x] Due-ping `family.habit.custom.<id>.due.N`
- [x] `clearPending` / `handleDone` → `custom.<id>` (XP/streak skip for custom)
- [x] Логи: id/mode/count — **не** title
- [x] `once_at` в reschedule — skip до `fhc-15`
- [x] Deep link wire: `aladdin://habit/done?preset=custom.<id>` (полный fhc-04 позже)
- [x] Unit: id helpers + pending match + once_at skip
- **Как лучше:** вынести общий helper slot/daily, custom только передаёт id+content; не копипастить 200 строк.
- **Чеклист:** pending в логе · Done clears due · reschedule ✅ (device pending — после GO)

### fhc-04 — Deep link + NotificationManager
- [x] `aladdin://habit/done?preset=custom.<uuid>` parse + `habitReminderDeepLink` (URLComponents)
- [x] Reuse category `family_habit` / `FAMILY_HABIT_DONE` — **без** новой category
- [x] Analytics hook `FamilyHabitCustomAnalytics.log(.done)` (id/mode only; fhc-17 расширит)
- [x] `performHabitDone` shared: deep link route + NotificationManager Done + tap on done deepLink
- [x] Malformed `custom.` → Family, не crash / не fake Done
- [x] Unit: parse / userInfo preset / analytics event name
- **Чеклист:** Done clear · no crash · XP custom **не** добавлять ✅

### fhc-05 — UI блок под Medicine (+ локаль + test-push) ⚠️ S2+S3
- [x] Заголовок «Свои напоминания» / «Your reminders»
- [x] Список: emoji · title · summary · toggle
- [x] `+ Добавить` → sheet: название, emoji chips, mode, окно/время, interval, ping, disclaimer
- [x] Edit + delete mandatory
- [x] Empty state; лимит 5 → disable «+» + human copy
- [x] Кому: фраза `family_habit_custom_audience_hint`
- [x] **Test-push must:** `fireCustomTestNotification` + кнопка в sheet
- [x] Ключи `family_habit_custom_*` RU+EN (S3 / fhc-09)
- [x] a11y `family_habit_custom_*`
- [x] `once_at` — только «скоро», без маркетинга
- [x] Merge не wipe local custom; member status rows + Done
- **Как лучше:** Storm card как секция; sheet = один scroll; test-push = fire local UN через 1s с тем же category/Done.
- **Чеклист:** EN+RU · ниже Medicine · test-push ✅ (sim — после GO)

### fhc-06 — Quick templates
- [x] 6 шт: Позвонить / Зарядка / Дверь / Перерыв / Почитать / Убрать (**не** лекарство)
- [x] Тап → title+emoji only; расписание не трогает; Save отдельно
- [x] Chips в блоке + в editor (isNew); `FamilyHabitCustomQuickTemplate`
- [x] Unit: schedule preserved · no collision with system presets
- **Как лучше:** только prefill draft, не создавать на сервере до Save.
- **Чеклист:** не путать с 4 системными пресетами ✅

### fhc-07 — Сервер store + router ⚠️ S4
- [x] `normalize(custom[])`: max 5, clamp title/interval/time, unknown mode → keep **disabled**
- [x] GET/POST не ломает `presets` / `member_ids`; default `custom: []`
- [x] Старый клиент omit `custom` → POST **не wipe** stored custom (merge in set_config)
- [x] Router body `custom: Optional[...] = None`; pytest legacy + custom
- [ ] Новый клиент + старый сервер на MAIN — клиент soft-fail (`fhc-08`); curl после **GO deploy** (`fhc-12`)
- **Как лучше:** validate в store, не в роутере; pytest на legacy payload + custom payload.
- **Чеклист:** pytest ✅ · curl после GO deploy

### fhc-08 — APIService / Service sync ⚠️ S1+S4
- [x] Encode/decode `custom` — `HabitRemindersBody.custom` + GET merge preserves local custom
- [x] Save → при **успехе** reschedule local (`saveLocalThenSync` → `pushServerOnly` → `applyServerConfig`)
- [x] **Soft-fail, не wipe:** `configAfterSyncFailure` + failure branch never `.empty`; UI shows `syncErrorKey`
- [x] Новый клиент + старый сервер: `family_habit_custom_server_outdated` на permanent 4xx + custom; иначе `…_sync_failed`
- [x] Offline draft persistence — **нет** (как сегодня); только no-wipe in-memory/current config
- **Как лучше:** один путь `applyServerConfig` только после HTTP 200 + decode OK; failure branch never assigns empty. ✅
- **Чеклист:** unit body encode + soft-fail + error keys ✅ (full xcodebuild — после GO)

### fhc-09 — Локализация (закрывается вместе с fhc-05)
- [x] Ключи `family_habit_custom_*` (section, empty, add, modes, test push, limit 5, disclaimer, intervals)
- [x] Health-like disclaimer
- [x] Закрыто вместе с `fhc-05`
- **Чеклист:** hardcoded RU в новом UI нет (все через keys) ✅

### fhc-10 — Unit tests
- [x] Clamp / max 5 / empty title (`testTitleClampAndEmptyDrop`, `testMaxFiveCustom`, `testNormalizeCustomDropsEmpty…`)
- [x] Slot math window + once_daily (`testWindowSixtyMinuteSlotsExactThenCap`, `testOnceDailySchedulableSingleTime`, `testWindowSlotsCap12`)
- [x] Legacy decode; unknown mode safe
- [x] Soft-fail no-wipe (service) + body encode + error keys
- [x] Policy unchanged (`testPolicyUnchangedWithCustomPresent`)
- **Чеклист:** unit tests in file ✅ · full xcodebuild — после GO

### fhc-11 — Static verify script
- [x] `scripts/verify_family_habit_custom_static.sh` — keys, model fields, scheduler prefix, store custom, no wipe pattern (grep), test-push key
- **Чеклист:** `./scripts/verify_family_habit_custom_static.sh` → exit 0 → **G7 ✅**

### fhc-12 — Deploy API (GO) ⚠️ S4
- [ ] Backup → scp store (+ router) → `py_compile` → restart → curl
- [ ] Smoke G4: POST with `custom` · GET · POST legacy without `custom`
- **Чеклист:** только после **GO на деплой** · MAIN `…180`

### fhc-13 — Device / Sim QA (GO)
- [ ] once_daily → push (или test-push)
- [ ] window 60m → multiple pending
- [ ] ping until Done → Done stops
- [ ] 6th Add blocked
- [ ] EN labels
- [ ] Soft-fail: airplane/save fail → presets ещё на месте
- [ ] Journal 5 строк: once / window / ping / 6th / EN(+soft-fail)
- **Чеклист:** только после **GO на сборку** и после deploy `fhc-12`

### fhc-14 — Plan–Fact close (hybrid window+daily)
- [ ] G1–G9 PASS или отложены с причиной
- [ ] REGISTRY статусы ✅ для 01…13
- **Чеклист:** нет «готово» / маркетинга без evidence

### fhc-15 — once_at (конкретная дата) — **делаем** после G1–G7, до маркетинга
**Приоритет:** сразу после закрытия кода hybrid (`fhc-11` / G7), можно параллелить с ожиданием GO deploy; **обязательно до** внешнего маркетинга «свои напоминания». Не вливать в первые коммиты `fhc-01…06` как blocker UI.

- [x] Schedule path: `mode == once_at` + `fire_at` → one-shot `UNCalendarNotificationTrigger(repeats: false)` + id `.at`
- [x] DatePicker в редакторе «Один раз (дата)»
- [x] После Done → `enabled=false` + soft-sync (`disableCustomAfterOnceAtDone`)
- [x] Past `fire_at` → не ставить pending; UI hint
- [x] Server normalize принимает `fire_at` / mode `once_at` (fhc-07)
- [x] Due-ping optional only same calendar day
- [x] Tests + static verify update
- **Чеклист:** не путать с once_daily · лимит 5 · G2 `.at` ✅

### fhc-16 — Reorder списка — **делаем**
**Когда:** после стабильного списка (`fhc-05` + sync), до или сразу после `fhc-14`; не блокирует G1–G7.

- [x] `sort_order` в модели (fhc-01)
- [x] ▲▼ reorder в блоке «Свои»
- [x] Persist order в POST `custom[]` (через save)
- [x] Server сохраняет порядок / `sort_order` (fhc-07 normalize)
- **Чеклист:** unit `testReorderSortOrderPersists` ✅ · Device QA order after kill — после GO

### fhc-17 — Лёгкая аналитика событий — **делаем**
**Когда:** вместе с `fhc-04`/`fhc-08` hooks или сразу после `fhc-05`; не блокирует G1–G3.

- [x] Events: create · done · edit · delete · test_push
- [x] Params: `mode`, `id` only — `allowedParamKeys` / unit test
- [x] `AnalyticsManager.shared.trackEvent` (тот же facade)
- [x] Hooks: UI upsert/delete · Scheduler Done · test-push
- **Чеклист:** grep — нет title в analytics payload ✅

### fhc-18 — Widget / App Intent «Сделано» — **НЕ ДЕЛАЕМ СЕЙЧАС**
- [ ] Запись-заглушка: отложено; не брать в спринт
- **Чеклист:** статус `⛔ deferred` · не путать с deep link Done в пуше (он уже в scope)

---

## Порядок работы

```
fhc-00 → fhc-01 → fhc-02 → fhc-03 → fhc-04 → fhc-05 (+ fhc-09 loc) → fhc-06
       → fhc-07 → fhc-08 (no-wipe) → fhc-10 → fhc-11          ⟵ G1–G7 code
       → fhc-17 analytics (можно с 04/08)
       → [GO deploy] fhc-12
       → fhc-15 once_at          ⟵ после G1–G7, до маркетинга
       → fhc-16 reorder          ⟵ после стабильного списка
       → [GO build] fhc-13 → fhc-14
       → fhc-18 Widget/Intent    ⟵ ⛔ не делаем сейчас
```

Медали/XP / календарь / AI / гео / cloud push / mock — **stop-list**, не открывать.

---

## Файлы (ожидаемый blast)

| Файл | Роль |
|------|------|
| `Core/Family/FamilyHabitRemindersModels.swift` | custom model + sort_order + fire_at |
| `Core/Family/FamilyHabitRemindersScheduler.swift` | schedule/clear/done + once_at |
| `Core/Family/FamilyHabitRemindersService.swift` | sync soft-fail no-wipe |
| `Core/Family/UnicornDeepLinkRouter.swift` | done deep link |
| `Shared/Components/FamilyHabitRemindersSection.swift` | UI + test-push + reorder |
| `Core/Localization/LocalizationManager.swift` | RU+EN с UI |
| Analytics facade (существующий) | fhc-17 events only |
| `app/services/family_habit_reminders_store.py` | server normalize |
| `Tests/UnitTests/*FamilyHabit*` | tests |
| `scripts/verify_family_habit_custom_static.sh` | gate G7 |

---

## Статусы (обновлять)

| id | Статус |
|----|--------|
| fhc-00 | ✅ registry + GATES + ship rules + stop-list |
| fhc-01 | ✅ model + clamp + legacy decode + unit tests |
| fhc-02 | ✅ interval enum 15/30/60/120 + nearest/summary/prefill |
| fhc-03 | ✅ scheduler custom window/once_daily + due + clear/done |
| fhc-04 | ✅ deep link done + NotificationManager + analytics hook |
| fhc-05 | ✅ UI custom block + editor + test-push |
| fhc-09 | ✅ loc keys RU+EN with fhc-05 |
| fhc-06 | ✅ quick templates (prefill only) |
| fhc-07 | ✅ server normalize custom[] + router Optional (pytest OK) |
| fhc-08 | ✅ HabitRemindersBody.custom + soft-fail no-wipe + sync error keys |
| fhc-10 | ✅ unit tests clamp/slots/legacy/soft-fail/policy |
| fhc-11 | ✅ static verify script · G7 PASS |
| fhc-12 | ⏳ pending — **GO на деплой** (MAIN OpenAPI без `custom` — 2026-10-10) |
| fhc-13 | ⏳ code build OK locally · Device QA after deploy |
| fhc-14 | ⏳ pending close after deploy+QA |
| fhc-15 | ✅ once_at schedule + DatePicker + Done disable |
| fhc-16 | ✅ ▲▼ reorder + sort_order |
| fhc-17 | ✅ analytics events (no title) |
| fhc-18 | ⛔ deferred — Widget / App Intent |
