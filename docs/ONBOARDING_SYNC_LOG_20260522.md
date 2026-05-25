# SYNC-журнал Figma ↔ iOS (2026-05-22)

Источник процедуры: `ONBOARDING_FINAL_ML_ALGORITHM.md` §3.1.

**Правило:** `imageHash` Figma ≠ `md5` файла на диске (перекодирование). **SYNC-H OK** = upload **того же PNG** из `Assets.xcassets` на узел `OnboardingHero_0N` + 393×852 @ (0,0).

---

## OB_01

| Шлюз | Результат | Детали |
|------|-----------|--------|
| SYNC-H | ✅ | Xcode `f3d6d7c38e5a2eee577f7941a56a9ee9` → upload → Figma `2b1e8a9f6b31e61f2365d3a1372fb96cfb9672c2`, 393×852, 1 hero IMAGE |
| SYNC-T | ✅ | SF Pro Bold 24 / Regular 16 white 0.92; scrim 528×324 stops 0/0.2025@0.45/0.45; wordmark 354×121 @10,354; title **508**; desc **593** w346 |
| SYNC-I | ✅ | `OnboardingFigmaAnchor` case 0 = §4 |
| SYNC-C | ✅ | TITLE/DESC = LocalizationManager |
| SYNC-D | ✅ | Принято 2026-05-23; повторная сверка live Figma `81:53` 2026-05-23 — координаты без изменений |

---

## OB_02

**Бэкап:** `docs/backup/onboarding_ob02_20260522_164358/` (Xcode hero + master + 6 crop-вариантов).

| Шлюз | Результат | Детали |
|------|-----------|--------|
| SYNC-H | ✅ | Xcode `be22a36d…` → Figma `c5a72085…` (zone94 center, 393×852) |
| SYNC-T | ✅ | SF Pro; title **479** x10; desc **552** w364 x7; scrim 552×300 stops 0 / 0.189@0.45 / 0.42 |
| SYNC-I | ✅ | `OnboardingFigmaAnchor` case 1 + `scrimGradientStops` |
| SYNC-C | ✅ | Тексты совпали |
| SYNC-D | ✅ | Принято 2026-05-23 |

---

## OB_03

| Шлюз | Результат | Детали |
|------|-----------|--------|
| SYNC-H | ✅ | Xcode `73cfae32…` → Figma upload (zone94-style, 393×852) |
| SYNC-T | ✅ | SF Pro; title 552; desc 630; scrim **500×320** stops 0 / 0.16@0.4 / 0.40@1 |
| SYNC-I | ✅ | `OnboardingFigmaAnchor` case 2 + `scrimGradientStops` |
| SYNC-C | ✅ | Тексты совпали |
| SYNC-D | ⏳ | Симулятор ≈ Figma — ждём «Принято» |

---

## OB_04 — OB_07 (build 203)

| OB | SYNC-I | Примечание |
|----|--------|------------|
| 04 | ✅ case 3 | Y **468/544** (desc h112), scrim 542×310 |
| 05 | ✅ case 4 | Y **468/544** (desc h112), scrim 532×320 |
| 06 | ✅ case 5 | Y 496/566, scrim 552×300 |
| 07 | ✅ case 6 | wordmark **250**; title **462**; desc **536**; legal privacy отдельной строкой; hero zone upload `122:54` |

*См. `ONBOARDING_COORDINATES_AND_SYNC.md`, `ONBOARDING_OB_07_SYNC_PLAN.md`.*
