# Storm Mesh — Cursor Todo (39 задач)

**Синхронизировано:** 2026-06-08 · **Build:** 227 (local, pending commit)  
**Handoff:** `docs/STORM_MESH_PREMIUM_DESIGN_HANDOFF.md` · **Continue:** `docs/STORM_MESH_AGENT_CONTINUE.md`

**Счёт:** 38 ✅ · 1 ❌ skip = 39

---

## Foundation & strategy (5/5 ✅)

| ID | Задача | Статус |
|----|--------|--------|
| `batch-0` | Batch 0 — Colors, StormMesh, StormGlass, pbxproj | ✅ build 226 |
| `infra-build` | SPM Rive, unlock build DB, provisioning | ✅ |
| `strategy-light-premium` | §1.5.1 Light Premium + режимы A/B/C | ✅ |
| `imp-hub-v12` | hub v1.2 atmosphere, indigo/lightning/gold, scrim 28% | ✅ |
| `imp-glass-frost-v12` | frost, gold rim 38%, dual shadow | ✅ |

## Calibration (1/1 ✅)

| ID | Задача | Статус |
|----|--------|--------|
| `mesh-variants-light-calibration` | IMP-07 — `.premium`/`.family`/`.shield`/… light ≤ Main | ✅ |

## §4.2 экраны (24/25 — 1 freeze)

| ID | Экран | Статус |
|----|-------|--------|
| `screen-01-main` … `screen-28-join-device` | 24 экрана §4.2 | ✅ |
| `screen-14-onboarding` | 14_Onboarding — **FREEZE** | ❌ skip |

## Batch 9 (6/6 ✅)

| ID | Задача | Статус | Build 227 |
|----|--------|--------|-----------|
| `batch-9-companion` | Companion 60+ `.warm` + glass | ✅ | |
| `batch-9-games` | Games/Rewards `.growWarm` + glass | ✅ | |
| `batch-9-learn` | Learn `.growWarm`/`.grow` + glass | ✅ | |
| `batch-9-wellness` | Wellness 16/16 warm/neutral/premium | ✅ | all Wellness screens |
| `batch-9-shield-settings` | Shield settings `.shield` mesh | ✅ | |
| `batch-9-flows` | AddMember `.family`, MainWithReg `.hub` | ✅ | |

**Batch 9 extras (6/6 ✅):** FamilyProtector `.family`, ParentDashboard `.grow`, NotificationSettings, LanguageSettings, WidgetConfiguration, VoiceNotes `.neutral`.

**Deferred polish (не блокирует 100%):** FamilyModals inner sheets, Elderly sub-views, `Simple*` / `*_Old` / debug screens — не в production nav.

## Финальные батчи (3/3 ✅)

| ID | Задача | Статус |
|----|--------|--------|
| `batch-6-glass` | Chrome pass + shield rows + Main tab glass scrim | ✅ build 227 |
| `batch-7-qa` | xcodebuild iPhone 13 Pro Max 15.2, Reduce Motion in StormMesh | ✅ |
| `batch-8-aso` | ASO 6 slides hub light — `docs/ASO_HUB_LIGHT_6_SLIDES.md` + Preview | ✅ |

---

## QA (Batch 7)

- Simulator: **iPhone 13 Pro Max 15.2** (`A900C6B0-…`)
- `StormMeshBackground`: `accessibilityReduceMotion` → blobs off, flat storm ✅
- Production `Screens/`: legacy full-screen gradient только freeze OB + deferred list ✅
- xcodebuild: см. build log после clean DerivedData
