# ALADDIN Memory Academy — Handoff для ML-системы

**Updated:** 2026-06-06  
**Версия плана:** v2.3 (`docs/MNEMONICS_CHILD_IMPLEMENTATION_PLAN.md`)  
**Полная синхронизация:** `docs/MNEMO_PROJECT_SYNC.md` ← **для другой ML: читать первым**  
**Прогресс:** **119 / 119 (100%)** · код ✅ · Phase C ✅ **2026-06-14**

---

## 0. Инструкция для следующей ML-системы (прочитать первым)

### 0.1 Что мы реализуем

**«Академия памяти» / Memory Academy** — детская мнемотехника внутри iOS-приложения ALADDIN.

- **Педагогика:** AIM + 4D + 3R + 5L  
- **Цикл урока v2:** ENCODE → ANCHOR → RECALL → REWARD  
- **Цикл v3 (расширение):** + WARMUP (7+), REFLECT (13+)  
- **8 мнемо-категорий** (Same ID, new soul — переименованные лейблы по возрасту)  
- **Leitner SRS:** интервалы 1, 3, 7, 14, 30 дней  
- **v3:** 8 семестров longitudinal curriculum (4→22 года)

### 0.2 Рабочий корень (обязательно)

```
/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
```

Все пути в документации — относительно этой папки.

### 0.3 Жёсткие ограничения (НЕ нарушать)

| Запрет | Причина |
|--------|---------|
| ❌ Новые блоки на главном экране ребёнка | Product policy |
| ❌ Менять `ChildCategoryKey` / seed item IDs | Same ID, new soul |
| ❌ Mock/fallback для parental bypass API | Production policy |
| ❌ i18n только RU или только EN | Gate требует паритет |
| ❌ Коммит без явной просьбы пользователя | Git policy |
| ⚠️ Длинный `xcodebuild test` в середине работы | Зависает 5–10+ мин — **тесты в конце** |

### 0.4 С чего начать (NEXT SESSION) — **Phase C only**

**Весь проект готов (119/119).** Новый функционал не писать без явного запроса.

| # | ID | Действие |
|---|-----|----------|
| 1 | B15-T01 | `python3 scripts/child_localization_gate.py --mnemo-full` (389 keys) |
| 2 | B8-T02, B9-T08, B10-T08, B15-T02 | `./scripts/mnemo_run_tests.sh` — unit suites |
| 3 | B8-T03, B15-T03 | UITest `MnemoAcademyUITests` (5 tests) |
| 4 | B8-T04 | Manual smoke 4 ages × 8 categories |
| 5 | B15-T04 | Manual 8 semesters × 4 ages |
| 6 | B8-T05, B15-T05 | §N.5 F1–F15 → `[x]`; §Q → 119/119 |

Детали: `docs/MNEMO_PROJECT_SYNC.md` §2–§3.

### 0.5 Как закончить проект (100%)

Проект **MNEMO 100%** когда:

- Все **119** чекбоксов §Q = `[x]`  
- Все **F1–F15** в §N.5 = `[x]` (сейчас только **F16** ✅)  
- `python3 scripts/child_localization_gate.py` → PASS  
- `scripts/mnemo_run_tests.sh` → green (или эквивалентные короткие `-only-testing` команды)

**Финальный commit (пример):** `feat(mnemo): MNEMO-B15 final QA F1–F15 sign-off`

---

## 1. PROMPT — Phase C для ML (copy-paste)

```
Ты завершаешь ALADDIN Memory Academy — Phase C (QA).

1. Прочитай docs/MNEMO_PROJECT_SYNC.md (полная синхронизация 119/119).
2. Рабочий корень: ALADDIN_NEW/mobile_apps/ALADDIN_iOS
3. Создай TodoWrite merge=false с 8 pending из §Q.1.A:
   B8-T02, B8-T03, B8-T04, B8-T05, B9-T08, B10-T08, B15-T04, B15-T05
4. Код НЕ писать. Только: gate → mnemo_run_tests.sh → manual → §N.5 sign-off.
5. xcodebuild только по явной команде пользователя (долго).
6. После Phase C: обнови §Q, tracker, MNEMO_PROJECT_SYNC.md, §N.5 F-flags.
7. Commit только по запросу.
8. Не меняй ChildCategoryKey. Не добавляй home screen blocks.
```

---

## 2. Архитектура (**39 файлов** `Core/Content/Mnemonics/`)

```
Screens/
  08_ChildInterfaceScreen.swift      # age tabs + category tiles
  ChildContentScreen.swift           # catalog, lock gate, SRS badge
  ChildContentExperienceScreen.swift # 4-phase lessons, games recall
  ParentDashboardView.swift          # Smart Memory, mastery % (+ T16 widget)

Core/Content/Mnemonics/              # 39 Swift files — полный список: MNEMO_PROJECT_SYNC.md §5
  1.  MnemoCategoryChrome.swift      # labels, brand, MnemoAcademyPhase.catalogPhases
  2.  MnemonicSRSStore.swift         # Leitner + recordFailure + iCloud opt-in
  3.  MnemonicSkillTracker.swift     # recalls, anchors, 3 levels
  4.  MnemonicJourneyPath.swift     # 40 stops (B9-T04 ✅)
  5.  MnemonicStudyTechniqueMap.swift
  6.  MnemonicTechnique.swift       # 10 techniques enum
  7.  MnemonicRewardBridge.swift    # 🦄 + technique mastery hook
  8.  MnemoDeepLinkRouter.swift      # aladdin://mnemo/review?category=games
  9.  MnemonicNotificationScheduler.swift
  10. MnemonicCurriculumSpine.swift # 8 semesters, SemesterGate, unlock 70%
  11. MnemonicTechniqueMastery.swift # 10 techniques × 4 stages
  12. MnemoAcademyBannerView.swift   # brand banner (extracted from ChildContentScreen)
  13. MnemoSemesterLockView.swift    # lock banner a11y child_mnemo_semester_locked
  14. MnemoFeatureFlags.swift        # B14 optional flags (default off)
  15. MnemonicPictogramStore.swift   # co-created PNG per itemId (B11-T01 ✅)
  16. MnemoPictogramEncodeCTA.swift   # ENCODE «Нарисуй свой образ» (B11-T02 ✅)
  17. MnemoPictogramDrawingSheet.swift # mini canvas save (B11-T03 ✅)
  18. MnemoPictogramRecallHint.swift   # RECALL hint level 1 (B11-T04 ✅)
  19. MnemonicBaselineAssessment.swift # 5 words / 2 min MQ baseline (B12-T01 ✅)
  20. MnemoBaselineAssessmentView.swift # child baseline sheet UI (B12-T01 ✅)
  21. MnemoParentMQTrendView.swift       # parent MQ sparkline (B12-T04 ✅)
  22. MnemonicCapstoneStore.swift        # study.26 capstone persist (B12-T05 ✅)
  23. MnemoStudyCapstoneExperienceView.swift # teach-back 3 min (B12-T05 ✅)
  24. MnemonicChampionshipStore.swift        # 20 pegs / 5 min personal best (B12-T06 ✅)
  25. MnemoChampionshipExperienceView.swift    # games.05 championship variant (B12-T06 ✅)
  26. MnemonicTableEngine.swift                 # 3×3 mnemotable show/hide/recall (B13-T01 ✅)
  27. MnemoTableExperienceView.swift            # table UI study.09 literature (B13-T02 ✅)
  28. MnemoTableCellVisual.swift                # B13-T03 ✅
  29. MnemoParentGuideContent.swift            # B14-T01
  30. MnemoParentGuideSheet.swift              # B14-T02
  31. MnemoParentTechniqueMasteryView.swift    # B14-T03
  32. MnemonicHintLadder.swift                 # B14-T04
  33. MnemoHintLadderRecallView.swift          # B14-T04
  34. MnemoLessonFlow.swift                    # B14-T05/T06/T07 age gates
  35. MnemoWarmupPhaseView.swift               # B14-T05
  36. MnemoReflectPhaseView.swift              # B14-T06
  37. MnemoTechniquePickerView.swift           # B14-T07
  38. MnemoParentSemesterProgressView.swift    # B14-T16
  39. MnemoOptionalFeatures.swift              # B14-T08,T10–T14 optional UI

Core/Navigation/NavigationManager.swift
ALADDINApp.swift                        # deeplink, -UITestMnemoAcademy, -UITestMnemoSemesterLocked
Core/Notifications/NotificationManager.swift
Core/Content/Seed/ContentSeedProvider.swift
```

**Поток SRS + push:**

```
Lesson fail → MnemonicSRSStore.recordFailure → box 0, +1 day
Lesson pass → recordSuccess → Leitner advance
persist() → MnemonicNotificationScheduler.rescheduleDailyReminder()
Push tap / deeplink → MnemoDeepLinkRouter → NavigationManager.navigateToMnemoReview
→ ChildContentScreen → SRS badge or auto-open first due item
```

---

## 3. Сводка прогресса

| Метрика | Значение |
|---------|----------|
| Всего задач §Q | **119** |
| ✅ Done (код/docs) | **111** |
| ⏳ Phase C | **8** |
| v2 MVP (B0–B8) | **58 / 62** (код ✅; 4 QA pending) |
| v3 Course (B9–B15) | **53 / 57** (код ✅; 4 QA pending) |
| i18n mnemo full | **389 keys** PASS |
| F-flags signed | **F14, F16** ✅; F1–F13, F15 ⏳ Phase C |

**Быстрая проверка прогресса (короткие команды):**

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
grep -c '\[x\] MNEMO-B' docs/MNEMONICS_CHILD_IMPLEMENTATION_PLAN.md
grep -c '\[ \] MNEMO-B' docs/MNEMONICS_CHILD_IMPLEMENTATION_PLAN.md
python3 scripts/child_localization_gate.py
python3 scripts/mnemo_batch_progress.py
```

---

## 4. Что уже сделано (111 задач) — детали в `MNEMO_PROJECT_SYNC.md` §4

### ✅ B0 — Foundation (2/2)
- Приветствие «Привет!» / «Hi!»
- 48+ ключей `child_mnemo_*` RU+EN

### ✅ B1C — Brand (8/8) → **F16 ✅**
- `MnemoBrandChrome`, catalog header, academy banner
- Parent «Умная память», onboarding OB_05, level-up toast

### ✅ B1 — UI Labels (6/6) → **F1 в коде**
- 8 мнемо-категорий × 4 возраста через `MnemoCategoryChrome`
- Subtitle, 4 phase dots, greeting, SRS badge

### ✅ B2 — MnemoCore (7/7) → **F2 в коде**
- Leitner SRS, SkillTracker, JourneyPath, unit tests базовые

### ✅ B3 — Games (7/7) → **F4 в коде**
- `games.05` palace, `games.12` pairs, SRS on win

### ✅ B4 — Study (11/11) → **F3, F5 в коде**
- 4 фазы в `StudyLessonTestExperienceView`
- Fail → CTA games + `recordFailure`
- study.01–25, 27–30 page_2 (study.26 → B12)

### ✅ B5 — Songs + Cartoons (5/5)
### ✅ B6 — Teen + Young (6/6) → **F6 в коде**

### ✅ B7 — Rewards + Parent (5/5) → **F7, F8 в коде**
- `MnemonicRewardBridge` (+3/+5/+10 🦄)
- Recommender SRS due + fail→games.05
- Parent mastery %, seed tag `mnemo`

### 🔄 B8 — QA (1/5 done, 4 deferred)
- ✅ B8-T01 localization gate PASS (550 keys)
- ⏳ T02–T05 — **в конце**

### 🔄 B9 — Curriculum Spine (7/8)
- ✅ T01 `MnemonicCurriculumSpine.swift` (8 semesters)
- ✅ T02 `MnemonicTechniqueMastery.swift` (10×4 stages)
- ✅ T05 semantic journey stops study.01→30
- ✅ T06 semester progress UI in banner
- ✅ T07 i18n semester 0–7 title/subtitle RU+EN
- ✅ T03 unlock UI (`MnemoSemesterLockView`, item row lock, `SemesterGate`)
- ✅ T04 journey 40 stops + i18n 21–40
- ⏳ T08 unit tests (defer)

### 🔄 B10 — SRS v2 (7/8)
- ✅ T01–T07 код (failure, dueItems, scheduler, push, deeplink, badge tap, iCloud)
- ⏳ T08 unit tests — **Phase C**

### ✅ B11 — Co-creation (6/6) → F14 код
### ✅ B12 — Assessment (8/8) → F12 код
### ✅ B13 — Мнемотаблица (6/6) → F15 код
### ✅ B14 — Parent + polish (16/16) incl. optional flags
### 🔄 B15 — QA v3 (3/5)
- ✅ T01 gate 389 keys, T02 unit code, T03 UITest code
- ⏳ T04 manual 8×4, T05 F1–F15 sign-off

---

## 5. Definition of Done — F1–F16

| Flag | Описание | Код | Sign-off §N.5 |
|------|----------|-----|---------------|
| F1 | 8 mnemo labels × age | ✅ | ☐ B8-T05 |
| F2 | SRS + skill 3 levels | ✅ | ☐ B8-T05 |
| F3 | Study 4ф + fail→games | ✅ | ☐ B8-T05 |
| F4 | games.05 palace | ✅ | ☐ B8-T05 |
| F5 | 30 study page_2 | ✅ | ☐ B8-T05 |
| F6 | recall all categories | ✅ | ☐ B8-T05 |
| F7 | 🦄 RewardBridge | ✅ | ☐ B8-T05 |
| F8 | parent mastery % | ✅ | ☐ B8-T05 |
| F9 | localization gate 389 keys | ✅ PASS | ☐ B8-T05 formal |
| F10 | manual smoke 4×8 | ☐ | ☐ B8-T04/T05 |
| F11 | 8 semesters unlock 70% | ✅ B9-T03 UI | ☐ B15 |
| F12 | Memory Quotient | 🔄 B12-T01–T04 ✅ | ☐ B15 sign-off |
| F13 | push + deeplink | ✅ код | ☐ B8/B10 tests |
| F14 | co-created pictogram | ✅ B11 | ✅ |
| F15 | mnemotable study.09 | ✅ B13 | ☐ B15 sign-off |
| F16 | Brand Academy | ✅ | ✅ |

---

## 6. ПОЛНЫЙ TODO — 8 pending Phase C (119 total)

> Статус: `docs/MNEMO_PROJECT_SYNC.md` · §Q.1.A · 2026-06-06

### BATCH 8 — QA v2 (4 pending) — **ДЕЛАТЬ В КОНЦЕ v2**

| ID | Задача | Файл / команда |
|----|--------|----------------|
| MNEMO-B8-T02 | Unit tests MnemoCore v2 | `scripts/mnemo_run_tests.sh` или `-only-testing:ALADDINUnitTests/MnemonicSRSStoreTests` |
| MNEMO-B8-T03 | UITest 4-phase + SRS | `Tests/UITests/MnemoAcademyUITests.swift`, flag `-UITestMnemoAcademy` |
| MNEMO-B8-T04 | Manual 4×8 smoke | `docs/MNEMO_B8_MANUAL_SMOKE_4x8.md` |
| MNEMO-B8-T05 | F1–F10 sign-off | §N.5 все `[x]` |

### BATCH 9 — Curriculum Spine (1 pending)

| ID | Задача | Файл | Acceptance |
|----|--------|------|------------|
| ~~MNEMO-B9-T03~~ | ✅ Unlock ≥70% UI | `MnemoSemesterLockView`, `ChildContentScreen` | Lock banner + locked rows; a11y `child_mnemo_semester_locked` |
| ~~MNEMO-B9-T04~~ | ✅ Journey 40 stops | `MnemonicJourneyPath.swift` | `stopCount=40`; i18n 21–40 RU+EN |
| MNEMO-B9-T08 | Unit tests unlock + mastery | `Tests/UnitTests/` | `masteryFraction` + `itemGate`; defer with B8 |

### BATCH 10 — SRS (1 pending)

| ID | Задача | Файл |
|----|--------|------|
| MNEMO-B10-T08 | Unit tests failure + notifications | `MnemonicSRSStoreTests.swift` (defer with B8-T02) |

### BATCH 11 — Co-creation ✅ (6/6) → F14

| ID | Задача |
|----|--------|
| ~~MNEMO-B11-T01~~ | ✅ `MnemonicPictogramStore.swift` — PNG per itemId, local |
| ~~MNEMO-B11-T02~~ | ✅ ENCODE CTA «Нарисуй свой образ» |
| ~~MNEMO-B11-T03~~ | ✅ Handoff to drawing / mini canvas |
| ~~MNEMO-B11-T04~~ | ✅ RECALL hint level 1: `MnemoPictogramRecallHint` |
| ~~MNEMO-B11-T05~~ | ✅ i18n `child_mnemo_pictogram_*` (11 keys); gate PASS |
| ~~MNEMO-B11-T06~~ | ✅ Parent: `parent_dashboard_mnemo_pictogram_count` |

### BATCH 12 — Assessment + Capstone ✅ (F12 code complete; sign-off B15)

| ID | Задача |
|----|--------|
| ~~MNEMO-B12-T01~~ | ✅ `MnemonicBaselineAssessment` — 5 words / 2 min + sheet |
| ~~MNEMO-B12-T02~~ | ✅ Memory Quotient 0–100 (persist `child.mnemo.mq.latest.v1`) |
| ~~MNEMO-B12-T03~~ | ✅ Quarterly re-test (90 days, max 1×/calendar quarter) |
| ~~MNEMO-B12-T04~~ | ✅ Parent MQ trend sparkline (`MnemoParentMQTrendView`) |
| ~~MNEMO-B12-T05~~ | ✅ study.26 Capstone teach-back → Champion unlock |
| ~~MNEMO-B12-T06~~ | ✅ Championship 20 items / 5 min personal best (`games.05` segmented mode) |
| ~~MNEMO-B12-T07~~ | ✅ i18n assessment + capstone (21 baseline + 18 capstone keys; gate 617 PASS) |
| ~~MNEMO-B12-T08~~ | ✅ Unit tests MQ + quarterly schedule (17 tests; run in Phase C) |

### BATCH 13 — Мнемотаблица ✅ (F15 code complete; sign-off B15)

| ID | Задача |
|----|--------|
| ~~MNEMO-B13-T01~~ | ✅ `MnemonicTableEngine` 3×3 + `MnemoTableExperienceView` |
| ~~MNEMO-B13-T02~~ | ✅ study.09 routes to table experience (`child_experience_category_study_table`) |
| ~~MNEMO-B13-T03~~ | ✅ `MnemoTableCellVisual` + `study.09.table.N` pictogram keys |
| ~~MNEMO-B13-T04~~ | ✅ `recordRecallSuccess` → SRS + studyPass reward (perfect 6/6) |
| ~~MNEMO-B13-T05~~ | ✅ i18n `child_mnemo_table_*` (14 keys RU+EN) |
| ~~MNEMO-B13-T06~~ | ✅ gate 631 keys PASS; micro-gate `--prefix child_mnemo_table_` |

### BATCH 14 — Parent Guide + polish ✅ (16/16)

| ID | Задача |
|----|--------|
| ~~MNEMO-B14-T01~~ | ✅ `parent_mnemo_guide_*` 30 keys + `MnemoParentGuideContent.swift` |
| ~~MNEMO-B14-T02~~ | ✅ `MnemoParentGuideSheet` local HTML WebView + dashboard CTA |
| ~~MNEMO-B14-T03~~ | ✅ `MnemoParentTechniqueMasteryView` 10 techniques × 4 stages |
| ~~MNEMO-B14-T04~~ | ✅ `MnemonicHintLadder` + `MnemoHintLadderRecallView` in study RECALL |
| ~~MNEMO-B14-T05~~ | ✅ WARMUP 30s (`MnemoWarmupPhaseView`); catalog banner 4 dots |
| ~~MNEMO-B14-T06~~ | ✅ REFLECT phase 13+ (`MnemoReflectPhaseView`) |
| ~~MNEMO-B14-T07~~ | ✅ technique picker before study (`MnemoTechniquePickerView` 13+) |
| ~~MNEMO-B14-T08~~ | ✅ Memory Hero avatars (`MnemoMemoryHeroChrome` + flag) |
| ~~MNEMO-B14-T09~~ | ✅ micro-wins +1 🦄 за попытку recall (`awardRecallAttempt`) |
| ~~MNEMO-B14-T10~~ | ✅ teen exam-hacks i18n (`child_mnemo_exam_hacks_*`) |
| ~~MNEMO-B14-T11~~ | ✅ Family Memory Challenge (`MnemoFamilyMemoryChallengeCard`) |
| ~~MNEMO-B14-T12~~ | ✅ Companion voice SRS (`MnemoCompanionSRSReminderCard`) |
| ~~MNEMO-B14-T13~~ | ✅ stories recall hook (`MnemoStoriesRecallHookBanner`) |
| ~~MNEMO-B14-T14~~ | ✅ advanced number pegs 15+ (`MnemoAdvancedNumberPegsCard`) |
| ~~MNEMO-B14-T15~~ | ✅ EN checklist `docs/MNEMO_EN_NATIVE_REVIEW_CHECKLIST.md` |
| ~~MNEMO-B14-T16~~ | ✅ Parent widget «до следующего семестра: N%» (`MnemoParentSemesterProgressView`) |

### BATCH 15 — Final QA v3 (2 pending — Phase C)

| ID | Задача |
|----|--------|
| ~~MNEMO-B15-T01~~ | ✅ full gate `--mnemo-full` 389 keys (min 350) |
| ~~MNEMO-B15-T02~~ | ✅ `MnemoCoreV3Tests` + xctestplan; run green Phase C |
| ~~MNEMO-B15-T03~~ | ✅ UITest lock + deeplink (run Phase C) |
| MNEMO-B15-T04 | manual 8 semesters × 4 ages |
| MNEMO-B15-T05 | F1–F15 all ✅ |

---

## 7. Рекомендуемый порядок выполнения (start → finish)

```
ФАЗА A — v2 код (DONE ✅)
ФАЗА B — v3 код (DONE ✅) — B9–B15, B14 optional, тесты НАПИСАНЫ
ФАЗА C — QA финал (NEXT 🏁)
  gate --mnemo-full → mnemo_run_tests.sh → manual → F1–F15 sign-off
```

---

## 8. 8 мнемо-категорий (Same ID)

| Age | Category ID | Mnemo label key |
|-----|-------------|-----------------|
| Kids 4–6 | `child_interface_category_songs` | `child_mnemo_label_songs_kids` |
| School 7–12 | games, study, cartoons | `*_games_school`, `*_study_school`, `*_cartoons_school` |
| Teen 13–17 | music, video | `*_music_teen`, `*_video_teen` |
| Young 18–22 | movies, education | `*_movies_young`, `*_education_young` |

---

## 9. Ключевые файлы и скрипты

| Файл | Назначение |
|------|------------|
| `docs/MNEMONICS_CHILD_IMPLEMENTATION_PLAN.md` | Master plan v2.3, §Q = 118 TODO |
| `docs/MNEMONICS_CURSOR_BATCH_TRACKER.md` | Dashboard батчей |
| `docs/MNEMO_B8_MANUAL_SMOKE_4x8.md` | Manual QA matrix |
| `docs/MNEMONICS_ML_HANDOFF.md` | **Этот handoff** |
| `scripts/child_localization_gate.py` | i18n gate (быстро, ~1 сек) |
| `scripts/mnemo_batch_progress.py` | Progress counter |
| `scripts/mnemo_run_tests.sh` | Unit + UITest (длинно — только в конце) |
| `scripts/patch_study_mnemo_page2.py` | Study content mnemo stops |
| `ALADDIN.xcodeproj/xcshareddata/xctestplans/ALADDIN_MnemoCore.xctestplan` | Test plan MnemoCore |
| `Tests/UnitTests/MnemonicSRSStoreTests.swift` | 8 unit tests |
| `Tests/UITests/MnemoAcademyUITests.swift` | UITest mnemo path |

---

## 10. UITest / deeplink шпаргалка

**Launch flags (UITest):**
```
-UITestSkipOnboarding
-UITestMnemoAcademy
-UITestMnemoSemesterLocked
--uitesting
```

`-UITestMnemoSemesterLocked` — DEBUG only; forces semesters ≥1 locked (semester 0 stays open). Для B15-T03 без mock API.

**Accessibility IDs:**
- `child_mnemo_academy_banner`
- `child_mnemo_brand_title`
- `child_mnemo_phase_label_0` … `_3`
- `child_mnemo_srs_due_badge`
- `child_mnemo_lesson_phase_header`
- `child_mnemo_semester_progress`
- `child_mnemo_semester_locked`

**Deep link:**
```
aladdin://mnemo/review?category=games
```
→ `MnemoDeepLinkRouter` → `NavigationManager.navigateToMnemoReview`

---

## 11. Короткие команды тестов (только в конце)

```bash
# Gate (быстро)
python3 scripts/child_localization_gate.py

# Unit only (может занять несколько минут)
xcodebuild test -scheme ALADDIN \
  -destination 'platform=iOS Simulator,name=iPhone 16' \
  -only-testing:ALADDINUnitTests/MnemonicSRSStoreTests

# UITest only
xcodebuild test -scheme ALADDIN \
  -destination 'platform=iOS Simulator,name=iPhone 16' \
  -only-testing:ALADDINUITests/MnemoAcademyUITests
```

**Известные fix'ы project.pbxproj (если build fail):**
- `Tests/UnitTests/PaymentQRViewModelProtectionTests.swift` — path must include `Tests/UnitTests/`
- `Tests/UnitTests/DEFENSIVEJWTTests.swift` — same
- UITest `CompanionSmokeUITests` — use `isEnabled` not `isDisabled`

---

## 12. Commit format

```
feat(mnemo): MNEMO-B{n} краткое описание
```

Примеры:
- `feat(mnemo): MNEMO-B9 curriculum unlock 70 percent`
- `feat(mnemo): MNEMO-B8 QA sign-off mnemo academy 100%`

---

## 13. Связанные документы

1. **Master plan:** `docs/MNEMONICS_CHILD_IMPLEMENTATION_PLAN.md`  
2. **Batch tracker:** `docs/MNEMONICS_CURSOR_BATCH_TRACKER.md`  
3. **Manual smoke:** `docs/MNEMO_B8_MANUAL_SMOKE_4x8.md`  
4. **Production bypass rule:** `.cursor/rules/prod-no-mock-bypass.mdc`

---

---

## 14. B9-T03 — UI spec semester lock (реализовано)

### 14.1 Три уровня блокировки

| Уровень | Где | Поведение |
|---------|-----|-----------|
| **Banner lock** | Под `MnemoAcademyBannerView` | `MnemoSemesterLockView` если `gate(for: category).isAccessible == false` |
| **Item row** | Каталог `dataDrivenContent` | Dim + 🔒 + hint; tap не открывает lesson sheet |
| **Deeplink/SRS** | `tryOpenPendingMnemoItem` / `openFirstDueMnemoItem` | Skip если `itemGate` locked |

**Не делаем:** overlay на главном экране ребёнка; блок home tiles.

### 14.2 i18n ключи (RU+EN)

| Key | Назначение |
|-----|------------|
| `child_mnemo_semester_locked_title` | Заголовок баннера |
| `child_mnemo_semester_locked_subtitle` | «Сначала пройди „%@“» (название prior semester) |
| `child_mnemo_semester_locked_progress` | «%d%% из %d%% до открытия» |
| `child_mnemo_semester_item_locked_hint` | Подпись на карточке урока |

Micro-gate: `python3 scripts/child_localization_gate.py --prefix child_mnemo_semester_locked`

### 14.3 Маппинг category → semester

Источник: `MnemonicCurriculumSpine.semesters[].primaryCategories`.

| Category | Semesters (indices) | Gate rule |
|----------|---------------------|-----------|
| songs | 0, 1 | `minimumSemesterIndex` = **0** |
| games | 1, 2, 7 | min = **1** |
| cartoons | 2 | **2** |
| study | 3, 4, 7 | **item-level** (см. ниже) |
| music, video | 5 | **5** |
| movies, education | 6, 7 | min = **6** |

**Multi-semester study** (`requiredSemesterIndex(forItemId:)`):

- `study.01`…`study.10` → semester **3**
- `study.11`…`study.20` → semester **4**
- `study.21`…`study.30` → semester **7**

Unlock: `masteryFraction(semester N-1) ≥ 0.70` (`SemesterGate.unlockThresholdPercent = 70`).

### 14.4 API spine

> **Полный реестр:** `docs/MNEMO_PROJECT_SYNC.md` §10 (baseline, SRS, flags, UITest args, a11y IDs).

```swift
MnemonicCurriculumSpine.shared.gate(for: category)       // category-level
MnemonicCurriculumSpine.shared.itemGate(forItemId:category:) // item-level (study split)

// Baseline / MQ (B12)
MnemonicBaselineAssessment.shared.offerKind()            // .initialBaseline | .quarterlyRetest
MnemonicBaselineAssessment.shared.isQuarterlyRetestDue()
MnemonicBaselineAssessment.shared.daysUntilRetest()
MnemonicBaselineAssessment.shared.nextRetestDate()
MnemonicBaselineAssessment.shared.hasSession(inCalendarQuarterOf:)
// DEBUG: -UITestMnemoBaselineRetest, -UITestMnemoBaseline
```

---

## 15. Улучшения плана (P0–P3)

### P0 ✅
- Tracker: B9=6/8, B10=7/8, v3=14/56
- UI spec §14 + i18n keys
- Category→semester table §14.3

### P1 (B9-T04 / B9-T08)
- `child_mnemo_semester_locked` a11y ✅
- После T04: audit `stopCount` / `% stopCount` в `ChildContentScreen`, `MnemonicStudyTechniqueMap`, `nextAvailableStop`
- B9-T08: unit tests `masteryFraction` + false-unlock guards

### P2 — структура
- Acceptance criteria: колонка в §6 + `§Q.1` master plan
- Risk register: `§RISK` master plan
- Feature flags B14 optional: `MnemoFeatureFlags` → `§FLAGS` master plan
- F-flag sign-off owners: `§N.5.1` master plan

### P3 — iOS
- B11 PNG → `Application Support/MnemoPictograms/` (не Documents)
- B10 iCloud KVS ≤1 MB — chunk SRS или opt-in warning (`§IOS-NOTES`)
- B14 WARMUP/REFLECT: расширить lesson enum; banner остаётся `MnemoAcademyPhase.catalogPhases` (4 dots)

---

## 16. Метод 6 шляп (зафиксировано)

| Шляпа | Вывод |
|-------|-------|
| 🤍 Белая | **119/119**; catalog v4 + Phase C sign-off 2026-06-14 |
| 🔴 Красная | План зрелый; главный риск — B14 scope (16 tasks) + mastery 70% heuristic |
| ⚫ Чёрная | `categoryBoost` false unlock → B9-T08; Companion → flag; gate churn → **incremental gate**; banner extracted |
| 🟡 Жёлтая | Same ID new soul (zero migration); deferred QA для agents; SRS+push+deeplink wired; 8 semesters longitudinal; B11 co-creation + B12 MQ |
| 🟢 Зелёная | `MnemoSemesterLockView`; `-UITestMnemoSemesterLocked`; `gate.py --prefix`; B14 split; **B14-T16 parent progress widget** |
| 🔵 Синяя | B11→B15 → фаза C; incremental gate после каждого i18n-batch |

---

## 17. B14 split (optional не блокирует 100%)

| Группа | Tasks | Flag |
|--------|-------|------|
| **B14-core** | T01–T07, T09, **T16** | always on |
| **B14-optional** | T08, T10–T14 | `MnemoFeatureFlags` (default off до sign-off) |
| **B14-process** | T15 | docs |

---

## 18. Incremental gate (обязательный шаг)

После **каждого batch** с изменением i18n или child screens:

```bash
python3 scripts/child_localization_gate.py
# B15 full mnemo gate (389 keys, min 350):
python3 scripts/child_localization_gate.py --mnemo-full
# micro-gate новых ключей:
python3 scripts/child_localization_gate.py --prefix child_mnemo_journey_stop_
```

Полный acceptance criteria: master plan **§Q.1.A** (8 pending Phase C) + **§Q.1.B** (справочник).

---

*Конец handoff. Следующая ML-сессия: **Phase C** (B8-T02–T05, B9-T08, B10-T08, B15-T04–T05). Сборка + xcodebuild — только в конце.*
