# ALADDIN Memory Academy — Project Sync (единый источник истины для ML)

**Updated:** 2026-06-06  
**Рабочий корень:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
**Прогресс:** **111 / 119 задач (93%)** · **Код: 100%** · **Phase C (QA): 8 задач осталось**

| Документ | Роль |
|----------|------|
| **Этот файл** | Полная синхронизация: что сделано, что осталось, файлы, тесты, флаги |
| `MNEMONICS_CHILD_IMPLEMENTATION_PLAN.md` §Q | Чекбоксы задач (источник для `mnemo_batch_progress.py`) |
| `MNEMONICS_ML_HANDOFF.md` | Краткий handoff + архитектура + ограничения |
| `MNEMONICS_CURSOR_BATCH_TRACKER.md` | Таблица батчей + команды gate |
| `MNEMO_EN_NATIVE_REVIEW_CHECKLIST.md` | B14-T15 — native EN review (процесс) |

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
python3 scripts/mnemo_batch_progress.py          # 111/119
python3 scripts/child_localization_gate.py --mnemo-full  # 389 keys PASS
```

---

## 1. Статус фаз

| Фаза | Описание | Статус |
|------|----------|--------|
| **A** | v2 код B0–B7 + B10 SRS/push код | ✅ **DONE** |
| **B** | v3 код B9–B15 (spine, pictogram, MQ, table, parent, optional) | ✅ **DONE** |
| **C** | Сборка, xcodebuild test, manual QA, F1–F15 sign-off | ⏳ **8 задач** |

**Правило:** `xcodebuild test` и полная сборка — **только Phase C** (по запросу пользователя в конце).

---

## 2. Оставшиеся 8 задач (Phase C)

| ID | Тип | Что сделать | Артефакт / команда |
|----|-----|-------------|-------------------|
| **B8-T02** | Unit | Прогнать MnemoCore v2 suites | `./scripts/mnemo_run_tests.sh` (unit часть) |
| **B8-T03** | UITest | Прогнать B8-T03 тесты (код ✅) | `MnemoAcademyUITests` — banner, 4 phases, SRS→lesson |
| **B8-T04** | Manual | Smoke 4 возраста × 8 мнемо-категорий | Документировать PASS в manual matrix |
| **B8-T05** | Sign-off | F1–F10 → `[x]` в §N.5 | После T02–T04 green |
| **B9-T08** | Unit | Прогнать unlock/mastery tests | Частично в `MnemoCoreV3Tests` (20 tests, код ✅) |
| **B10-T08** | Unit | failure + notifications tests | Написать/прогнать при Phase C |
| **B15-T04** | Manual | 8 семестров × 4 возраста | Manual matrix + §N.5 F11 |
| **B15-T05** | Sign-off | F1–F15 все `[x]` | Финальный MNEMO 100% |

### Порядок Phase C (рекомендуемый)

```
1. python3 scripts/child_localization_gate.py --mnemo-full
2. ./scripts/mnemo_run_tests.sh                    # все unit + UITest
3. Manual B8-T04 (4×8) + B15-T04 (8×4)
4. §N.5: отметить F1–F15
5. §Q: отметить B8-T02–T05, B9-T08, B10-T08, B15-T04–T05
```

---

## 3. F-flags (§N.5) — sign-off

| Flag | Код готов? | Sign-off | Owner batch |
|------|------------|----------|-------------|
| F1 | ✅ labels по возрасту | ⏳ | B8-T05 |
| F2 | ✅ SRS + skill | ⏳ | B8-T05 |
| F3 | ✅ study 4 фазы | ⏳ | B8-T05 |
| F4 | ✅ games.05 recall | ⏳ | B8-T05 |
| F5 | ✅ 30 study page_2 | ⏳ | B8-T05 |
| F6 | ✅ songs…education recall | ⏳ | B8-T05 |
| F7 | ✅ MnemonicRewardBridge | ⏳ | B8-T05 |
| F8 | ✅ parent mastery % | ⏳ | B8-T05 |
| F9 | ✅ gate PASS (389 keys) | ⏳ formal | B8-T05 |
| F10 | ⏳ device smoke | ⏳ | B8-T04 |
| F11 | ✅ spine UI + UITest код | ⏳ run + manual | B15-T03/T04/T05 |
| F12 | ✅ baseline + MQ UI | ⏳ | B15-T05 |
| F13 | ✅ push + deeplink код | ⏳ | B15-T05 |
| F14 | ✅ pictogram recall | ✅ | B15 |
| F15 | ✅ study.09 table | ⏳ | B15-T05 |
| F16 | ✅ Brand Academy | ✅ | B1C |

---

## 4. Полный реестр 119 задач

### ✅ B0 Foundation (2/2)

| ID | Статус | Deliverable |
|----|--------|-------------|
| B0-T01 | ✅ | Шапка «Привет!» / «Hi!» |
| B0-T02 | ✅ | 48+ `child_mnemo_*` RU+EN |

### ✅ B1C Brand (8/8) → F16

| ID | Статус | Deliverable |
|----|--------|-------------|
| B1C-T01 | ✅ | `MnemoBrandChrome` |
| B1C-T02 | ✅ | i18n brand keys §AA.2 |
| B1C-T03 | ✅ | catalog header title + tagline |
| B1C-T04 | ✅ | academy banner promise + superpower |
| B1C-T05 | ✅ | parent Smart Memory |
| B1C-T06 | ✅ | level-up superpower toast |
| B1C-T07 | ✅ | onboarding OB_05 |
| B1C-T08 | ✅ | gate brand keys |

### ✅ B1 UI Labels (6/6) → F1 код

| ID | Статус | Deliverable |
|----|--------|-------------|
| B1-T01–T06 | ✅ | `MnemoCategoryChrome`, 8 категорий, SRS badge stub, gate |

### ✅ B2 MnemoCore (7/7)

| ID | Статус | Deliverable |
|----|--------|-------------|
| B2-T01–T07 | ✅ | Technique, SRS, SkillTracker, JourneyPath, unit `MnemonicSRSStoreTests` |

### ✅ B3 Games (7/7)

| ID | Статус | Deliverable |
|----|--------|-------------|
| B3-T01–T07 | ✅ | games.05 recall, games.12, i18n, gate |

### ✅ B4 Study 4ф + 30 предметов (11/11)

| ID | Статус | Deliverable |
|----|--------|-------------|
| B4A–B4D | ✅ | 4-phase lesson, study.01–30 content (study.26 → B12) |

### ✅ B5 Songs + Cartoons (5/5)

| ID | Статус | Deliverable |
|----|--------|-------------|
| B5-T01–T05 | ✅ | 3 трека, recall, i18n |

### ✅ B6 Teen + Young (6/6)

| ID | Статус | Deliverable |
|----|--------|-------------|
| B6-T01–T06 | ✅ | music/video/movies/education mnemo flows |

### ✅ B7 Rewards + Parent (5/5)

| ID | Статус | Deliverable |
|----|--------|-------------|
| B7-T01–T05 | ✅ | `MnemonicRewardBridge`, recommender, parent mastery % |

### 🔄 B8 QA v2 (1/5) — Phase C

| ID | Статус | Deliverable |
|----|--------|-------------|
| B8-T01 | ✅ | full localization gate v2 |
| B8-T02 | ⏳ | **прогон** unit tests |
| B8-T03 | ⏳ | **прогон** `MnemoAcademyUITests` (код ✅) |
| B8-T04 | ⏳ | manual 4×8 |
| B8-T05 | ⏳ | F1–F10 sign-off |

### 🔄 B9 Curriculum Spine (7/8)

| ID | Статус | Deliverable |
|----|--------|-------------|
| B9-T01 | ✅ | `MnemonicCurriculumSpine` 8 semesters |
| B9-T02 | ✅ | `MnemonicTechniqueMastery` 10×4 |
| B9-T03 | ✅ | `MnemoSemesterLockView`, item lock, ≥70% |
| B9-T04 | ✅ | journey 40 stops + i18n 21–40 |
| B9-T05 | ✅ | semantic stops study.01→30 |
| B9-T06 | ✅ | semester progress in banner |
| B9-T07 | ✅ | semester i18n RU+EN |
| B9-T08 | ⏳ | **прогон** unit unlock + mastery |

### 🔄 B10 SRS v2 + Push (7/8)

| ID | Статус | Deliverable |
|----|--------|-------------|
| B10-T01–T07 | ✅ | recordFailure, dueItems, scheduler, push, deeplink, iCloud |
| B10-T08 | ⏳ | **прогон** unit failure + notifications |

### ✅ B11 Co-creation (6/6)

| ID | Статус | Deliverable |
|----|--------|-------------|
| B11-T01 | ✅ | `MnemonicPictogramStore` |
| B11-T02 | ✅ | `MnemoPictogramEncodeCTA` |
| B11-T03 | ✅ | `MnemoPictogramDrawingSheet` |
| B11-T04 | ✅ | `MnemoPictogramRecallHint` |
| B11-T05 | ✅ | i18n pictogram 11 keys |
| B11-T06 | ✅ | parent pictogram count |

### ✅ B12 Assessment (8/8)

| ID | Статус | Deliverable |
|----|--------|-------------|
| B12-T01–T07 | ✅ | Baseline, MQ, quarterly, parent trend, capstone, championship |
| B12-T08 | ✅ | `MnemonicBaselineAssessmentTests` (17) |

### ✅ B13 Мнемотаблица (6/6)

| ID | Статус | Deliverable |
|----|--------|-------------|
| B13-T01–T06 | ✅ | TableEngine, study.09, pictogram cells, SRS, i18n, gate |

### ✅ B14 Parent + Polish (16/16)

| ID | Статус | Deliverable |
|----|--------|-------------|
| B14-T01 | ✅ | `parent_mnemo_guide_*` 30 keys + `MnemoParentGuideSheet` |
| B14-T02 | ✅ | Parent WebView guide |
| B14-T03 | ✅ | `MnemoParentTechniqueMasteryView` |
| B14-T04 | ✅ | `MnemonicHintLadder` + `MnemoHintLadderRecallView` |
| B14-T05 | ✅ | `MnemoWarmupPhaseView` 30s (7+) |
| B14-T06 | ✅ | `MnemoReflectPhaseView` (13+) |
| B14-T07 | ✅ | `MnemoTechniquePickerView` (13+) |
| B14-T08 | ✅ | `MnemoMemoryHeroChrome` + flag `memoryHeroAvatars` |
| B14-T09 | ✅ | `awardRecallAttempt` micro-win 🦄 |
| B14-T10 | ✅ | `child_mnemo_exam_hacks_*` + flag `teenExamHacksCopy` |
| B14-T11 | ✅ | `MnemoFamilyMemoryChallengeCard` + flag |
| B14-T12 | ✅ | `MnemoCompanionSRSReminderCard` + opt-in + flag |
| B14-T13 | ✅ | `MnemoStoriesRecallHookBanner` + flag |
| B14-T14 | ✅ | `MnemoAdvancedNumberPegsCard` + flag |
| B14-T15 | ✅ | `docs/MNEMO_EN_NATIVE_REVIEW_CHECKLIST.md` |
| B14-T16 | ✅ | `MnemoParentSemesterProgressView` |

### 🔄 B15 QA v3 (3/5) — Phase C

| ID | Статус | Deliverable |
|----|--------|-------------|
| B15-T01 | ✅ | `--mnemo-full` 389 keys (min 350) |
| B15-T02 | ✅ | `MnemoCoreV3Tests` + `ALADDIN_MnemoCore.xctestplan` 7 suites (код ✅) |
| B15-T03 | ✅ | `MnemoAcademyUITests` lock + deeplink (код ✅) |
| B15-T04 | ⏳ | manual 8 semesters × 4 ages |
| B15-T05 | ⏳ | F1–F15 sign-off |

---

## 5. Индекс файлов MnemoCore (39 Swift)

```
Core/Content/Mnemonics/
  MnemoCategoryChrome.swift          # labels, brand, phases
  MnemonicSRSStore.swift
  MnemonicSkillTracker.swift
  MnemonicJourneyPath.swift          # 40 stops
  MnemonicStudyTechniqueMap.swift
  MnemonicTechnique.swift            # 10 techniques
  MnemonicRewardBridge.swift         # 🦄 + micro-wins
  MnemoDeepLinkRouter.swift
  MnemonicNotificationScheduler.swift
  MnemonicCurriculumSpine.swift      # 8 semesters, SemesterGate
  MnemonicTechniqueMastery.swift
  MnemoAcademyBannerView.swift
  MnemoSemesterLockView.swift
  MnemoFeatureFlags.swift            # 6 optional flags (prod 4–22 v1: 4 on, 2 off)
  MnemoLessonFlow.swift              # WARMUP/REFLECT/techniquePick ages
  MnemonicHintLadder.swift
  MnemoHintLadderRecallView.swift
  MnemoWarmupPhaseView.swift
  MnemoReflectPhaseView.swift
  MnemoTechniquePickerView.swift
  MnemonicPictogramStore.swift
  MnemoPictogramEncodeCTA.swift
  MnemoPictogramDrawingSheet.swift
  MnemoPictogramRecallHint.swift
  MnemonicBaselineAssessment.swift
  MnemoBaselineAssessmentView.swift
  MnemoParentMQTrendView.swift
  MnemonicCapstoneStore.swift
  MnemoStudyCapstoneExperienceView.swift
  MnemonicChampionshipStore.swift
  MnemoChampionshipExperienceView.swift
  MnemonicTableEngine.swift
  MnemoTableExperienceView.swift
  MnemoTableCellVisual.swift
  MnemoParentGuideContent.swift
  MnemoParentGuideSheet.swift
  MnemoParentTechniqueMasteryView.swift
  MnemoParentSemesterProgressView.swift
  MnemoOptionalFeatures.swift        # B14-T08,T10–T14 optional UI

Screens/
  ChildContentScreen.swift           # catalog, lock, optional cards
  ChildContentExperienceScreen.swift # lessons, stories hook
  ParentDashboardView.swift
  08_ChildInterfaceScreen.swift

Tests/UnitTests/
  MnemonicSRSStoreTests.swift
  MnemonicBaselineAssessmentTests.swift
  MnemonicCapstoneStoreTests.swift
  MnemonicChampionshipStoreTests.swift
  MnemonicPictogramStoreTests.swift
  MnemonicTableEngineTests.swift
  MnemoCoreV3Tests.swift             # 20 tests spine+flow+ladder

Tests/UITests/
  MnemoAcademyUITests.swift          # B8-T03 (2) + B15-T03 (3)

scripts/
  mnemo_run_tests.sh                 # gate + 7 unit suites + UITest
  mnemo_batch_progress.py
  child_localization_gate.py         # --mnemo-full, --prefix
```

---

## 6. Тесты (написаны, прогон — Phase C)

| Suite | Файл | Задачи | Тестов (approx) |
|-------|------|--------|-----------------|
| MnemonicSRSStoreTests | Unit | B2, deeplink parse | несколько |
| MnemonicBaselineAssessmentTests | Unit | B12-T08 | 17 |
| MnemonicCapstoneStoreTests | Unit | B12 | — |
| MnemonicChampionshipStoreTests | Unit | B12 | — |
| MnemonicPictogramStoreTests | Unit | B11 | — |
| MnemonicTableEngineTests | Unit | B13 | — |
| MnemoCoreV3Tests | Unit | B15-T02, B9-T08 overlap | 20 |
| MnemoAcademyUITests | UITest | B8-T03, B15-T03 | 5 |

**Test plan:** `ALADDIN.xcodeproj/xcshareddata/xctestplans/ALADDIN_MnemoCore.xctestplan`

**Launch args (UITest):**
- `-UITestSkipOnboarding`
- `-UITestMnemoAcademy` — seed SRS games.05, games catalog
- `-UITestMnemoSemesterLocked` — force semesters ≥1 locked (DEBUG)

**Deeplink:** `aladdin://mnemo/review?category=games`

---

## 7. i18n и gate

| Метрика | Значение |
|---------|----------|
| Mnemo full keys | **389** (min 350) |
| RU+EN паритет | обязателен |
| Последний gate | ✅ PASS |

```bash
python3 scripts/child_localization_gate.py
python3 scripts/child_localization_gate.py --mnemo-full
python3 scripts/child_localization_gate.py --prefix child_mnemo_exam_
```

---

## 8. B14 optional feature flags — Prod preset **4–22 v1**

| Key | Prod default | UI scope |
|-----|--------------|----------|
| `mnemo.memoryHeroAvatars` | **ON** | skill card всех мнемо-каталогов |
| `mnemo.teenExamHacksCopy` | **ON** | accent + banner только teen 13–17 |
| `mnemo.advancedNumberPegs` | **ON** | карточка teen + youngAdult (opt-in внутри) |
| `mnemo.storiesRecallHook` | **ON** | конец сказки в stories |
| `mnemo.familyMemoryChallenge` | OFF | включить после QA smoke share sheet |
| `mnemo.companionVoiceReminder` | OFF | волна 2 (голос + политика) |

Явное значение в UserDefaults **перебивает** prod default (`MnemoFeatureFlags.resolved`).

Отключить в debug: `defaults write … mnemo.memoryHeroAvatars -bool false`

Доп. opt-in внутри UI:
- `mnemo.companionVoiceReminder.optIn`
- `mnemo.advancedNumberPegs.optIn`

---

## 9. Урок v3 — фазы по возрасту

| Возраст | Фазы lesson flow |
|---------|------------------|
| kids | ENCODE → ANCHOR → RECALL → REWARD |
| school (7+) | WARMUP → ENCODE → ANCHOR → RECALL → REWARD |
| teen (13+) | techniquePick → WARMUP → … → REWARD → REFLECT |
| youngAdult | как teen + REFLECT |

Catalog banner: всегда **4 точки** (`MnemoAcademyPhase.catalogPhases`).

---

## 10. Промпт для следующей ML-сессии (Phase C)

```
Рабочий корень: ALADDIN_NEW/mobile_apps/ALADDIN_iOS
Прочитай docs/MNEMO_PROJECT_SYNC.md (этот файл) + §Q + MNEMONICS_ML_HANDOFF.md
Прогресс: 111/119. Весь КОД готов. NEXT: Phase C только (8 задач).
НЕ пиши новый функционал без запроса. Запускай xcodebuild только в Phase C.
Порядок: gate --mnemo-full → mnemo_run_tests.sh → manual → §N.5 F-flags → §Q [x]
Жёстко: не менять ChildCategoryKey, не home blocks, no mock bypass, commit по запросу.
```

---

## 11. Жёсткие ограничения (всегда)

| Запрет | Причина |
|--------|---------|
| Новые блоки на главном экране ребёнка | Product |
| Менять `ChildCategoryKey` / seed IDs | Same ID, new soul |
| Mock parental bypass API | Production policy |
| i18n только RU или только EN | Gate |
| Commit без просьбы | Git policy |
| xcodebuild в середине реализации | Policy — только Phase C |

---

*Синхронизировано с §Q в `MNEMONICS_CHILD_IMPLEMENTATION_PLAN.md`. При расхождении — §Q + `python3 scripts/mnemo_batch_progress.py` побеждают.*
