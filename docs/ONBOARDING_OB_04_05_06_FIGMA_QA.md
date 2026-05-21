# OB_04–06 — Figma + §E-IMG QA (2026-05-19)

## Figma nodeId

| Страница | Фрейм | Герой |
|----------|-------|-------|
| OB_04 | `117:53` `OB_04_Radar_393x852` | `117:54` `OnboardingHero_04` |
| OB_05 | `117:70` `OB_05_Kids_393x852` | `117:71` `OnboardingHero_05` |
| OB_06 | `117:87` `OB_06_Adults23_393x852` | `117:88` `OnboardingHero_06` |

## §4.1 G1–G10 (агент)

| # | OB_04 | OB_05 | OB_06 |
|---|:-----:|:-----:|:-----:|
| G1 скрин героя | ✅ | ✅ | ✅ |
| G2 иллюстрация | ✅ космос радар | ✅ космос щит | ✅ космос лента |
| G3 сюжет | ✅ A | ✅ B | ✅ C |
| G4 PNG в репо | ✅ | ✅ | ✅ |
| G5 тексты RU | ✅ | ✅ | ✅ |
| G6 chrome 361×50 | ✅ | ✅ | ✅ |
| G7 zone 361×460 | ✅ | ✅ | ✅ |
| G8 §E-IMG масштаб | ✅ | ✅ | ✅ |
| G9 скрин фрейма | ✅ | ✅ | ✅ |
| G10 Продукт | ☐ | ☐ | ☐ |

## Тексты (эталон Swift)

**04:** «Аналитика рисков» / desc `onboarding_page4_desc`  
**05:** «Защита для детей!» / desc `onboarding_page5_desc`  
**06:** «Защита для людей 23+» / desc `onboarding_page6_desc`

## Chrome dots (active = `currentPage`)

| Page | Активная точка |
|------|----------------|
| 4 | 5-я (x≈78) |
| 5 | 6-я (x≈94) |
| 6 | 7-я (x≈110) |

## Экспорт в репо

- `Resources/FigmaExports/OB_04/OB_04_Radar_393x852_full.png`
- `Resources/FigmaExports/OB_05/OB_05_Kids_393x852_full.png`
- `Resources/FigmaExports/OB_06/OB_06_Adults23_393x852_full.png`

## Batch (не в этой сессии)

- `OnboardingHero_04|05|06.imageset`
- Симулятор `currentPage` 4, 5, 6
