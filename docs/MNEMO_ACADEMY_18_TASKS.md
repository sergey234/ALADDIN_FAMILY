# Академия памяти — 18 задач (catalog fix batch)

**Updated:** 2026-06-13  
**Корень:** `ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
**Политика:** код/docs ✅ · **xcodebuild / test — только Phase C в конце**

---

## Статус

| # | ID | Задача | Код | Docs | Run (Phase C) |
|---|-----|--------|-----|------|---------------|
| 1 | mnemo-p0-alert | Alert на 🔒 «осталось N% до семестра M» | ✅ | ✅ | manual 4×8 |
| 2 | mnemo-p0-progress-split | «Открывал» / «Запомнил», без +20%/тап | ✅ | ✅ | manual |
| 3 | mnemo-p0-catalog-full | PlanItem275 manifest `seed-manifest-v4` | ✅ | ✅ | reseed smoke |
| 4 | mnemo-p0-games-order | `games.05` первая, «Дворец образов» | ✅ | ✅ | catalog open |
| 5 | mnemo-p1-study-intro | `study.01–03` без сем. 3 | ✅ | ✅ | manual study |
| 6 | mnemo-p1-songs-bind | 1 card = 1 mnemo track + recall | ✅ | ✅ | songs row |
| 7 | mnemo-p1-semester-mastery | Unlock от recall/SRS | ✅ | ✅ | 8×4 manual |
| 8 | mnemo-p1-fail-cta | Fail study → `games.05` | ✅ | ✅ | study fail path |
| 9 | mnemo-p2-optional-flags | family + voice reminder ON | ✅ | ✅ | optional UI |
| 10 | mnemo-p2-school-warmup | Warmup 30s school | ✅ (B14) | ✅ | study school |
| 11 | mnemo-p2-unified-srs | Единая очередь «Повтори сегодня» | ✅ | ✅ | SRS badge |
| 12 | mnemo-phase-c-gate | `child_localization_gate.py --mnemo-full` | — | ✅ | **RUN LAST** |
| 13 | mnemo-phase-c-unit | `mnemo_run_tests.sh` unit | tests written | ✅ | **RUN LAST** |
| 14 | mnemo-phase-c-uitest | `MnemoAcademyUITests` | tests exist | ✅ | **RUN LAST** |
| 15 | mnemo-phase-c-manual-4x8 | `MNEMO_B8_MANUAL_SMOKE_4x8.md` | — | ✅ | **RUN LAST** |
| 16 | mnemo-phase-c-manual-8x4 | `MNEMO_B15_MANUAL_SMOKE_8x4.md` | — | ✅ | **RUN LAST** |
| 17 | mnemo-phase-c-signoff | F1–F15 §N.5 + tracker | — | ✅ | 2026-06-14 |
| 18 | mnemo-fix-v4-verify | Reseed v4 + device smoke | — | ✅ | Xcode build 15.2 |

**18/18 задач:** ✅ код · docs · sign-off (2026-06-14)

---

## Ключевые файлы (batch 2026-06-13)

| Область | Файлы |
|---------|--------|
| Catalog tap / alert / progress | `Screens/ChildContentScreen.swift` |
| Manifest v4 | `ContentSeedProvider.swift`, `MnemoCatalogManifestBuilder.swift`, `MnemoCatalogTitles.generated.swift` |
| Reseed trigger | `ContentManager.swift` (`seed-manifest-v1…v4`) |
| Study intro gate | `MnemonicCurriculumSpine.swift` |
| SRS unified queue | `MnemonicSRSStore.swift` |
| Recall % UI | `MnemoItemProgress.swift` |
| Songs 1:1 track | `ChildContentExperienceScreen.swift` → `KaraokeExperienceHostView` |
| Fail → palace | `StudyLessonTestExperienceView` |
| Flags | `MnemoFeatureFlags.swift` |
| i18n RU/EN | `LocalizationManager.swift` (+397 mnemo keys gate) |
| Unit tests (written) | `MnemoCoreV3Tests.swift`, `MnemonicSRSStoreTests.swift` |

---

## Новые i18n ключи (RU + EN)

- `child_mnemo_item_locked_alert_title` / `_message`
- `child_mnemo_progress_opened_yes` / `_no` / `_recalled`
- `child_mnemo_catalog_subtitle`
- `child_mnemo_fail_cta_games_action`
- `child_catalog_item_*` — 140 titles via `MnemoCatalogTitles.generated.swift` fallbacks

---

## Phase C — порядок (не запускать раньше)

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
python3 scripts/child_localization_gate.py --mnemo-full
MNEMO_TEST_DEST='platform=iOS Simulator,name=iPhone 13 Pro Max,OS=18.4' ./scripts/mnemo_run_tests.sh
# Manual: docs/MNEMO_B8_MANUAL_SMOKE_4x8.md + docs/MNEMO_B15_MANUAL_SMOKE_8x4.md
# Sign-off: MNEMONICS_CHILD_IMPLEMENTATION_PLAN.md §N.5 F1–F15
```

---

*Синхронизировано с `MNEMO_PROJECT_SYNC.md` §13.*
