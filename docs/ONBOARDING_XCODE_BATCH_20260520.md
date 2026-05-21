# Xcode batch — OnboardingHero imageset (2026-05-20)

## Выполнено

| imageset | Источник | Метод |
|----------|----------|--------|
| `OnboardingHero_00` … `07` | `Resources/HeroAssets/` | Скрипт `Scripts/build_onboarding_hero_imagesets.py` |

**Правило:** каждый PNG в каталоге = **393×852** pt.

| N | Мастер | Сборка |
|---|--------|--------|
| 01–03 | уже 393×852 | копия мастера |
| 00, 04–07 | 1536×1024 | zone `*_figma_zone_361x460.png` @ (16,24) на фоне `#0a1128` (00 — тёмный фон) |

## Не менялось

- `Screens/14_OnboardingScreen.swift`
- `HeroAmbientPresentation.swift`
- Локализация, градиент `LinearGradient.backgroundGradient`

## Откат

- Код: `docs/backup/onboarding_mobile_pre_batch_20260520/`
- imageset 00 до batch: `docs/backup/onboarding_pre_xcode_batch_20260519/imagesets_snapshot/`

## Следующий шаг

`plan-phase-c-full-qa` — симулятор `currentPage` 0…7, сверка с `FigmaExports/OB_0N/*_full.png`.
