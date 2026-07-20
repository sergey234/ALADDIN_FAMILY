# HANDOFF: Hybrid «редкий софт» → ALADDIN (Единорог)

**Дата:** 2026-07-20 (rev: As-built P0–P1.6; next = P1.7 Due)  
**Для:** другая ML / агент — выполнять строго по id тикетов  
**Канонический корень iOS:** `ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
**Cursor todos:** зеркало тикетов ниже (те же id) + Wellness Gaps (`psych-*`)  
**Отдельный трек психологии (не смешивать с Unicorn P0):** [HANDOFF_WELLNESS_GUIDE_HYBRID_20260720.md](./HANDOFF_WELLNESS_GUIDE_HYBRID_20260720.md)  
**Сборка:** `xcodebuild` только по явной команде пользователя в конце.

---

## 0. Вердикт (читать первым)

| Решение | Правило |
|---------|---------|
| Путь | Гибриды на **существующих** экранах, не клоны 11 приложений |
| Питомец | **Единорог** (`UnicornPetView` / `UnicornRewardsStore`), **не** птенец Finch |
| Валюта | Одна: `unicornBalance` + parental rewards. **Не** плодить вторую |
| Петля | Голос / 1 тап / пуш → действие → `UnicornCareReward` → родителю только **агрегат** |
| Навигация | Как Simple Home в этом чате: стек + `goBackToPreviousScreen()` |
| i18n | Каждый PR: ключи **RU + EN** в `LocalizationManager` |
| Не трогать | Qalta, iForget, aicar, Holli, Motra, DAF, Sleep Cycle (исходные №10,11,12,15,16,17,18) |

**Порядок работ:** `00-contract` → P0 ✅ → `qa-hats` ✅ → P1.4–1.6 ✅ → **P1.7 Due** → P1.8 Лекарство → P2 (медали мульти + челленджи + breath+звук + p2-pol) → polish.  
**Параллельно (не блокировать Unicorn):** Wellness Guide Gaps — порядок §8 Wellness MD (`psych-01c` → `02` SSOT → `09` → `05` → `05b` after `p2-9h` → опц. `04b`; `psych-07` C **не** в релизе).  
**Anti-scope:** не начинать `p2-9h` пока `p1-7*`+`p1-8*` не ✅.  
**R1:** после 7+8 — `r1-smoke` (device) + `r1-metrics` (ручные метрики). Весь P2 scope **оставляем** (вкл. Moments фото, sound 10d–e, p2-pol).

---

## 1. Что уже есть (фундамент — не переписывать)

| Контур | Статус | Ключевые пути |
|--------|--------|----------------|
| Family habits (вода multi-slot) | ✅ | `Core/Family/FamilyHabitReminders*.swift`, `Shared/Components/FamilyHabitRemindersSection.swift`, `app/services/family_habit_reminders_store.py` |
| Voice Notes + on-device STT | ✅ | `Screens/VoiceNotesScreen.swift`, `Core/Audio/VoiceNotes*.swift`, `QuickRecorderBar` |
| Wellness check-in (mood+) | ✅ | `Screens/WellnessCheckinScreen.swift`, `WellnessHub*`, виджет |
| Companion + returnTo | ✅ | `CompanionHomeScreen`, `navigateToCompanionHome(returnTo:)` |
| Unicorn + rewards | ✅ | `UnicornCareReward`, `UnicornPetView`, `ChildRewards*` |
| Parental / Games | ✅ | `07_ParentalControlScreen`, `GamesParentalControl*` |
| Simple Home | ✅ | `SimpleHomeScreen` (+ плитка «Сказать») |
| Nav stack | ✅ | `Core/Navigation/NavigationManager.swift` |

### 1b. As-built прогресс гибрида (код — не переписывать)

| Id | Статус | Факт |
|----|--------|------|
| `00-contract` | ✅ | nav / Unicorn-only / RU+EN |
| `p0-1a`…`p0-1e` | ✅ | Done→Unicorn; push category; UI; clear pings; nav smoke (device в конце) |
| `p0-2a`…`p0-2d` | ✅ | Structure JSON + sheet + Simple «Сказать» + XP |
| `p0-3a`…`p0-3d` | ✅ | Quick emoji check-in; Companion chip; streak XP; aggregate hint |
| `qa-hats` | ✅ static | device nav smoke — перед финальным xcodebuild |
| `p1-4a`…`p1-4c` | ✅ | Break steps + checklist XP (не water) + assign child |
| `p1-5a`…`p1-5c` | ✅ | Day recap; wind_down→day-recap deeplink; XP |
| `p1-6a`…`p1-6c` | ✅ | BE `/api/family/list` last-write; `FamilyListScreen`; CTA+XP |
| `p1-7a`…`p1-7c` | ✅ | Due-ping fields + scheduler + UI (flag `due_ping` default OFF) |
| `p1-8a`…`p1-8c` | ✅ | medicine preset + disclaimer + Done→XP (via habit Done path) |
| `p2-*` / `inf-deeplink` | ❌ **next** | Focus / Moments / medals / challenges / breath+audio |
| `p2-*` / `inf-*` | ❌ later | Focus / Moments / medals / challenges / breath+audio / flags |

**Прод ops:** задеплоить `family_habit_reminders_store.py` (+ `family_list_store.py`) на MAIN при необходимости.

---

## 2. Контракт навигации (обязателен)

Файл: `Core/Navigation/NavigationManager.swift`

```
navigateTo(_:)
navigateToSimpleHome()
navigateToCompanionHome(returnTo:)
navigateToWellnessScreen(_:returnTo:)   // wellnessReturnScreen
goBackToPreviousScreen(reason:)         // НЕ хардкод .main
```

### Правила

1. **Back** на новых/трогаемых экранах = только `goBackToPreviousScreen()`.
2. Wellness / check-in / дыхание = `navigateToWellnessScreen(..., returnTo:)`.
3. Companion = `navigateToCompanionHome(returnTo:)` (из Simple Home: `returnTo: .simpleHome`).
4. Стек Simple Home: `Main → Simple → X → Back → Simple → Main`.
5. Deep link из пуша **не** форсит `.main`; сохраняет/восстанавливает контекст.
6. Новый экран: `ALADDINScreen` case + switch в `ALADDINApp` + Back по контракту.

### Карта входов

| Фича | Вход | Back |
|------|------|------|
| Habit Done / Due / **Лекарство** | Family + notification action | стек |
| Структура / Итог дня | Voice Notes (+ Simple «Сказать») | стек / returnTo |
| Check-in 1 тап | `.wellnessCheckin` + Companion chip + виджет | wellnessReturn / стек |
| Goblin шаги | Companion / AI | returnTo |
| Focus | Parental (+ Simple «Защита») | стек |
| Shared list / Moments / **свои челленджи** | Family (+ Simple «Семья») | стек |
| Дыхание 2 мин | `.wellnessExercise` / Companion | wellness return |

---

## 3. Общая гибридная схема

```
Голос / 1 тап / пуш
  → действие (шаг, check-in, вода Done, пункт списка, фокус, дыхание…)
    → UnicornCareReward.grant(reason:)
      → +balance / love↑ / hunger↓ (Единорог)
        → родителю: агрегат / streak / «фокус сегодня» — НЕ сырой дневник mood
```

**Не связывать:** наказания за плохое настроение; штрафы за пропуск воды у детей; штраф за срыв Focus.

---

## 4. Тикеты (канон для Cursor + агента)

### `00-contract` — чеклист каждого PR

- [ ] Back = `goBackToPreviousScreen`
- [ ] Companion/Wellness с `returnTo` где нужно
- [ ] Simple Home стек не сломан
- [ ] Валюта только Unicorn
- [ ] RU + EN ключи
- [ ] Нет медclaims / штрафов mood-воде детям

---

### P0.1 — Habit Done → Единорог (логика Finch на Unicorn)

**Цель:** пуш/UI «Сделано» кормит единорога.  
**Не делать:** второго питомца, магазин скинов Finch.

| Id | Работа | DoD |
|----|--------|-----|
| `p0-1a` | `UnicornCareReward.grant(reason:amount:)` → balance + love/hunger; **идемпотентность** `(day, preset/reason, childId)` против фарма | unit/smoke: повторный Done тот же день не дублирует XP |
| `p0-1b` | `UNNotificationCategory` + action `FAMILY_HABIT_DONE` для `family.habit.*`; handler читает `userInfo.preset` | action на пуше воды вызывает grant |
| `p0-1c` | UI «Сделано» в `FamilyHabitRemindersSection` (member) + опц. Companion chip | кнопка видна при enabled preset |
| `p0-1d` | После Done: снять ping id на сегодня; haptic; ключи `family_habit_done*` RU+EN | pending cleared + toast |
| `p0-1e` | Nav smoke: пуш ≠ Main; Main→Simple→Family→Back→Simple→Main | стек OK |

**Файлы:** `FamilyHabitRemindersScheduler`, notification delegate, `UnicornRewardsStore` / новый хелпер рядом с Unicorn.

---

### P0.2 — Happens: голос → структура

**Цель:** после STT кнопка «В структуру».  
**Не делать:** второй Notion.

| Id | Работа | DoD |
|----|--------|-----|
| `p0-2a` | Промпт/API: transcript → JSON `{tasks, people, urgent, list_candidates}` | валидный JSON на RU тексте |
| `p0-2b` | Кнопка в `VoiceNotesScreen` / `QuickRecorderBar` после STT | кнопка после транскрипта |
| `p0-2c` | Sheet bullets + CTA: Companion(`returnTo`), «В шаги» (→P1.4), «В список» (→P1.6 stub ok) | CTA навигирует с returnTo |
| `p0-2d` | Мелкий grant; privacy banner; `voice_structure_*` RU+EN; **Simple Home «Сказать»** → VoiceNotes или Companion talk + `returnTo: .simpleHome` | вход с Simple + Back |

---

### P0.3 — Daylio-lite: check-in 1 тап

**Цель:** emoji-only путь; parent = aggregate.  
**Не делать:** клинику / публичный фид.

| Id | Работа | DoD |
|----|--------|-----|
| `p0-3a` | Quick UI без слайдеров (ageBand child/elderly); save в существующий Wellness path | 1 тап сохраняет mood |
| `p0-3b` | Companion chip «Как день?» → `navigateToWellnessScreen(.wellnessCheckin, returnTo:)` | Back в Companion |
| `p0-3c` | Виджет / `navigateToWellnessCheckinFromDeepLink`; streak 3 дня → Unicorn XP через `p0-1a` | streak начисляет 1 раз |
| `p0-3d` | Parent только aggregate (`parentShareAggregate`); `wellness_checkin_quick_*` RU+EN | нет сырой ленты родителю |

---

### `qa-hats` — после P0 (обязательно перед P1)

- [ ] Регресс nav Simple Home
- [ ] EN spot-check новых ключей
- [ ] Нет второй валюты
- [ ] Нет штрафов mood / воде детям
- [ ] Идемпотентность XP

---

### P1.4 — Goblin: цель → микрошаги

| Id | Работа |
|----|--------|
| `p1-4a` | Companion/AI «Разбить на шаги» → 3–7 шагов (LLM) |
| `p1-4b` | Чеклист; шаг Done → grant; **не** для water habit |
| `p1-4c` | Опц. parent→child задание; Back стек; `companion_break_steps_*` RU+EN |

**Зависит от:** `p0-1a`, CTA из `p0-2c`.  
**Не делать:** project manager.

---

### P1.5 — MemoRecap: итог дня

| Id | Работа |
|----|--------|
| `p1-5a` | Режим Voice Notes: запись→STT→5 пунктов + «что сказать семье» |
| `p1-5b` | `wind_down` push `userInfo` → deep link режима; returnTo; **не** always-on mic |
| `p1-5c` | Хук save Chat/Moments (P2.9); XP; `voice_day_recap_*` RU+EN |

**Зависит от:** P0.2 pipeline.

---

### P1.6 — AnyList-lite: семейный список

| Id | Работа |
|----|--------|
| `p1-6a` | Модель+BE: `family_id`, items, **last-write wins** |
| `p1-6b` | UI Family→Список; при нужде `ALADDINScreen.familyList`; Simple→Family→List; Back контракт |
| `p1-6c` | CTA из структуры «В список»; N checked → малый XP; `family_list_*` RU+EN |

**Не делать:** рецепты / пантри.

---

### P1.7 — Due: пинг до Done

| Id | Работа |
|----|--------|
| `p1-7a` | `ping_until_done`, interval 15–30, `max N/day`; **water default OFF**; критичные пресеты включают **medicine** |
| `p1-7b` | Scheduler repeats until Done/cap; Done (`p0-1`) clears; BE normalize; **feature flag `due_ping`** |
| `p1-7c` | Toggle UI + warning про детей; `family_habit_ping_*` RU+EN |

**Зависит от:** P0.1.  
**Не делать:** агрессия по умолчанию на воду/всех детей.

---

### P1.8 — Пресет «Лекарство» (под Due) + настройки

**Зачем:** готовый шаблон «выпей лекарство» — главный кейс для жёсткого пинга (60+, хронические приёмы). Без отдельного приложения.

**Как лучше:**
1. Новый preset id: `medicine` (рядом с `water` / `phone_down` / `wind_down`).
2. Дефолты: `enabled=false`, время **09:00** (один слот/день, не multi как вода), `ping_until_done=true` (когда Due включён), interval **20 мин**, max **6**/день.
3. Настройки в Family habits (развёрнуто): время, тумблер «Пинговать до Сделано» (default ON для medicine), interval, max/день, для кого (как у других).
4. Пуш короткий: RU `💊 Лекарство — время принять.` / EN `💊 Medicine — time to take it.`
5. Done → `UnicornCareReward` + clear pings (P0.1); серия дней → медали (P2.9d–f).
6. Копирайт: **не** медсовет («мы не врачи» одной строкой в UI).

| Id | Работа | DoD |
|----|--------|-----|
| `p1-8a` | iOS+BE: preset `medicine` в `FamilyHabitPresetId` / `_VALID_PRESETS` / defaults + normalize | save/load medicine OK |
| `p1-8b` | UI строка в accordion + настройки (время, ping ON default, interval, max); summary свёрнуто | родитель включает за 30 сек |
| `p1-8c` | Scheduler 1 слот + Due-ping; notification category как habits; `family_habit_medicine_*` RU+EN; disclaimer | пуш→Done→XP; ping стоп |

**Зависит от:** `p1-7a–c` (поля ping).  
**Не делать:** трекер доз/рецептов/аптеки; несколько лекарств v1 (одно «лекарство» достаточно).

---

### P2.8 — Opal-light: Focus 25/60

| Id | Работа |
|----|--------|
| `p2-8a` | Session на Parental/Games; start/stop UI; **feature flag** |
| `p2-8b` | Успех→XP; срыв→мягкий текст **без штрафа**; вход Simple «Защита» |
| `p2-8c` | Back стек; `focus_session_*` RU+EN; не клон Opal |

---

### P2.9 — Lialy: Moments + медали серии (мульти-источники) + свои челленджи

**Зачем:** «медаль» за серию дней = удержание без второй валюты. Источники — не только вода/лекарство: телефон, вечер, дыхание, check-in, фокус + **свои челленджи** семьи.

#### Медали — как лучше

1. `HabitStreakStore`: ключ `(sourceId, memberId)` → даты Done.  
   **Встроенные sourceId:** `water`, `medicine`, `phone_down`, `wind_down`, `breath`, `checkin`, `focus`.
2. Вехи: **3 / 7 / 14 / 30** (один раз на веху на source).
3. На вехе: авто-Moment `🏅 7 дней: …` + `UnicornCareReward.streakMedal` + chip.
4. **Настройки родителя** (Family → Напоминания / Моменты → «Медали»):
   - мастер-тумблер «Медали за серии» ON/OFF (default ON);
   - **чекбоксы источников** (default ON: вода + лекарство; остальные OFF, чтобы не сыпать 🏅);
   - список включает и **свои челленджи**.
5. Разрыв серии — тихо, без штрафа.

| Id | Работа | DoD |
|----|--------|-----|
| `p2-9a` | Модель+API Moments: text, optional photo, date, childId | CRUD/list на child |
| `p2-9b` | UI на child card; голос→момент (P0.2/P1.5) | момент вручную/голосом |
| `p2-9c` | **Не** соцлента; Back; `family_moments_*` RU+EN | — |
| `p2-9d` | `HabitStreakStore` + хук Done из P0.1 (базовые presets) | streak после Done |
| `p2-9e` | Веха → авто-Moment + `streakMedal`; `family_streak_medal_*` RU+EN | веха 7д = 1 Moment |
| `p2-9f` | UI настроек: мастер ON/OFF + **чекбоксы** встроенных источников (water/medicine/phone/wind/breath/checkin/focus); default water+medicine | родитель выбирает что медалится |
| `p2-9g` | Проводка Done→streak для phone_down, wind_down, breath complete, check-in, focus success (если чекбокс ON) | каждый источник двигает свою серию |

#### Свои челленджи — как лучше

**Идея:** семья сама пишет челлендж («10 приседаний», «без сладкого», «помочь бабушке») → каждый день **Сделано** → та же механика медалей.

1. Модель `FamilyChallenge`: `id`, `title`, `emoji?`, `memberIds[]` (пусто = как habits minors), `enabled`, `createdBy`.
2. Вехи те же 3/7/14/30 (не усложнять свой календарь целей в v1).
3. UI: Family → блок **«Свои челленджи»** (аккордеон, тот же glass/chevron):
   - список; **+ Добавить** (title, emoji optional, для кого);
   - тумблер enabled; кнопка **Сделано сегодня** у участника;
   - edit/delete (parent).
4. Лимит: **max 5** активных на семью (анти-хаос).
5. Попадают в чекбоксы медалей (`p2-9f`) как `challenge:<id>`.
6. Done → `UnicornCareReward` (малый) каждый день + streak/медаль на вехах.
7. RU+EN; Back = `goBackToPreviousScreen` / sheet dismiss.

| Id | Работа | DoD |
|----|--------|-----|
| `p2-9h` | Модель+BE `FamilyChallenge` + sync family_id; normalize; max 5 | CRUD API/local |
| `p2-9i` | UI аккордеон «Свои челленджи»: add/edit/delete, enabled, «Сделано сегодня» | участник отмечает день |
| `p2-9j` | Хук Done → streak + XP; challenge в чекбоксах медалей `p2-9f` | 7д своего челленджа = Moment 🏅 |
| `p2-9k` | `family_challenge_*` RU+EN; лимит 5; nav/smoke Family→челленджи→Back | EN+стек OK |

**Зависит от:** P0.1 Done; Moments (`p2-9a–b`) до/вместе с авто-Moment; дыхание/focus/check-in — хуки после появления Done этих фич (можно stub source и включить позже).

**Не делать:** Habitica/магазин наград челленджей; чужие публичные челленджи; штрафы за пропуск; бесконечный список челленджей.

---

### P2.10 — Yinhale-lite: дыхание 2 мин + soft audio (настройки)

**Порядок внутри эпика:** сначала упражнение (`p2-10a–c`), затем звук (`p2-10d–e`).

**Как лучше (звук):**
1. 1–2 коротких bundled loop (дождь / мягкий шум), `AVAudioPlayer` **numberOfLoops = -1**.
2. Audio session: **ambient** (уважает Silent Switch телефона — важно в семье).
3. **Настройки на экране упражнения** (и persist UserDefaults):
   - тумблер «Фоновый звук» (default **ON**, громкость стартовая ~0.3);
   - выбор: Дождь / Шум;
   - слайдер громкости.
4. Старт loop при Start упражнения; стоп на Complete / Back / disappear.
5. Без онлайн-стриминга и без отдельного медиаплеера в приложении.

| Id | Работа | DoD |
|----|--------|-----|
| `p2-10a` | Пресет «Дыхание 2 мин» в `WellnessExerciseScreen` (без звука ok) | сессия 2 мин завершается |
| `p2-10b` | Companion → `navigateToWellnessScreen(.wellnessExercise, returnTo:)`; complete→XP+love | Back в Companion/Simple |
| `p2-10c` | Копирайт **без** медclaims; `wellness_breath_2min_*` RU+EN | — |
| `p2-10d` | Bundled loops + player ambient; start/stop с жизненным циклом упражнения | звук играет/стопится корректно |
| `p2-10e` | UI настроек: ON/OFF, тип, громкость; persist; `wellness_breath_audio_*` RU+EN | настройки переживают перезапуск |

---

### `p2-pol` — Planwoo-lite

Только визуал чипов/слотов в Family habits. **Не** отдельный календарь-планер.

---

### Инфра (из 6 шляп — делать по мере P0/P1)

| Id | Работа |
|----|--------|
| `inf-deeplink` | Общий router deep links: habit Done / wind_down recap / check-in / focus end / **medicine** — единая точка |
| `inf-flags` | Feature flags: `due_ping`, `focus_session` |

*Опционально позже (не в Cursor): parent daily digest раз в день (не realtime mood).*

---

## 5. Матрица XP → Единорог

| Источник | Награда | Родитель видит |
|----------|---------|----------------|
| Habit Done (вода / телефон / вечер / лекарство / **свой челлендж**) | +balance / love↑ | streak агрегат |
| Check-in 1 тап | +XP (+ серия если чекбокс) | aggregate mood only |
| Breath / Focus success (если чекбокс) | +XP + день серии | — |
| **Веха серии 3/7/14/30** (любой включённый source) | `streakMedal` + авто-Moment 🏅 | Moment + chip |
| Focus success | +XP | «фокус сегодня» |
| Goblin step Done | +XP/шаг | прогресс задания |
| List N checked | малый XP | — |
| Voice structure / day recap | малый XP | опц. Moment |
| Breath 2 min complete | +XP + love | — |

---

## 6. Что НЕ делать (жёсткий список)

- Клоны: Finch-птенец, Notion, Daylio-клиника, Opal-продукт, Due на всех, отдельный планер
- Qalta / iForget / aicar / Holli / Motra / DAF / Sleep Cycle
- Always-on mic; фоновая запись суток
- Вторая валюта / второй питомец
- Штрафы: mood, пропуск воды у детей, срыв Focus
- Медclaims в дыхании / wellness copy
- Хардкод Back → Main

---

## 7. Порядок и параллелизм

```
00-contract ✅
  └─ p0-1a…e ✅  (базис XP)
       ├─ p0-2* ✅
       └─ p0-3* ✅
            └─ qa-hats ✅ (device smoke в конце)
                 ├─ p1-4* ✅
                 ├─ p1-5* ✅
                 ├─ p1-6* ✅
                 └─ p1-7* ❌ NEXT (Due)
                      └─ p1-8* Лекарство
                           └─ r1-smoke + r1-metrics
                           └─ p2-8* / p2-9a–g / p2-10a–e / p2-pol  (можно)
                           └─ p2-9h–k  ⛔ после 7+8 ✅ only
                           └─ inf-deeplink / inf-flags

Параллельно Wellness (не блокировать):
  psych Gaps: 00 partial → 01c → 02 SSOT → 09 → 05 → 05b(after p2-9h) → опц.04b
  psych-07 C = P2 gated ❌ не сейчас
```

---

## 8. Definition of Done (эпик)

**P0 готов когда:**
1. Done на family habit меняет Unicorn (идемпотентно).
2. Voice Notes «В структуру» работает RU; UI EN есть.
3. Quick check-in 1 тап; parent без сырой ленты.
4. Nav Simple Home не регрессировал (`qa-hats`).

**P1 готов когда:** шаги / итог дня / список / Due-toggle (flagged) / **пресет Лекарство с настройками ping** работают с Back-контрактом и RU+EN.

**P2 готов когда:** Focus (flagged) / Moments / **медали с чекбоксами источников** / **свои челленджи (max 5)** / breath 2min / soft audio / polish — без медclaims и без соцленты.

---

## 9. Шесть шляп — кратко (уже учтено в тикетах)

| Шляпа | Вывод → действие в плане |
|-------|---------------------------|
| Белая | Фундамент есть; дыры = XP-связь, структура, list, Due, Focus |
| Красная | Unicorn+Moments = тепло; Due/Opal = риск раздражения → flags + default OFF |
| Чёрная | Фарм XP → идемпотентность; mood leak → aggregate; Screen Time → P2 soft |
| Жёлтая | P0 = 80% эффекта | 
| Зелёная | Simple «Сказать», deeplink router, flags, digest later |
| Синяя | Строгий порядок id; qa после P0 |

---

## 10. Инструкции агенту (чеклист старта)

1. Открыть этот файл + Cursor todo с **тем же id**.
2. Взять **один** id (`p0-1a` первым после контракта).
3. Не начинать P1 до `qa-hats` после P0.
4. Не реализовывать исключённые приложения.
5. В PR: nav smoke + RU/EN + «Единорог» в copy, не «птенец».
6. Коммиты — только если пользователь явно просит.

---

## 11. Связанный контекст чата

- Family habits вода (вариант A): multi `UNNotificationRequest`, summary `2 л · каждые 2 ч · 09:00–21:00`.
- Call labels: «Подпись на входящем: возможный мошенник».
- Simple Home nav fix: единый `goBackToPreviousScreen()`.

**Конец handoff.**
