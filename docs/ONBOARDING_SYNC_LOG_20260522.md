# SYNC-журнал Figma ↔ iOS (2026-05-22)

Источник процедуры: `ONBOARDING_FINAL_ML_ALGORITHM.md` §3.1.

**Правило:** `imageHash` Figma ≠ `md5` файла на диске (перекодирование). **SYNC-H OK** = upload **того же PNG** из `Assets.xcassets` на узел `OnboardingHero_0N` + 393×852 @ (0,0).

---

## OB_01

| Шлюз | Результат | Детали |
|------|-----------|--------|
| SYNC-H | ✅ | Xcode `f3d6d7c38e5a2eee577f7941a56a9ee9` → upload → Figma `2b1e8a9f6b31e61f2365d3a1372fb96cfb9672c2`, 393×852, 1 hero IMAGE |
| SYNC-T | ✅ | SF Pro Bold 24 / Regular 16 white 0.92; scrim 528×324; Y title 598, desc 656, wordmark 484 |
| SYNC-I | ✅ | `OnboardingFigmaAnchor` case 0 = §4 |
| SYNC-C | ✅ | TITLE/DESC = LocalizationManager |
| SYNC-D | ⏳ | Симулятор SE + Pro Max — человек |

---

## OB_02

**Бэкап:** `docs/backup/onboarding_ob02_20260522_164358/` (Xcode hero + master + 6 crop-вариантов).

| Шлюз | Результат | Детали |
|------|-----------|--------|
| SYNC-H | ✅ | Xcode `be22a36d…` → Figma `c5a72085…` (zone94 center, 393×852) |
| SYNC-T | ✅ | SF Pro; title 533/607; scrim 552×300 stops 0 / 0.189@0.45 / 0.42 |
| SYNC-I | ✅ | `OnboardingFigmaAnchor` case 1 + `scrimGradientStops` |
| SYNC-C | ✅ | Тексты совпали |
| SYNC-D | ✅ | Симулятор = Figma (build 202) |

---

## OB_03

| Шлюз | Результат | Детали |
|------|-----------|--------|
| SYNC-H | ✅ | Xcode `73cfae32…` → Figma upload (zone94-style, 393×852) |
| SYNC-T | ✅ | SF Pro; title 552; desc 630; scrim **500×320** stops 0 / 0.16@0.4 / 0.40@1 |
| SYNC-I | ✅ | `OnboardingFigmaAnchor` case 2 + `scrimGradientStops` |
| SYNC-C | ✅ | Тексты совпали |
| SYNC-D | ✅ | Симулятор = Figma (build 202) |

---

*Следующие: OB_04…06 по тому же циклу.*
