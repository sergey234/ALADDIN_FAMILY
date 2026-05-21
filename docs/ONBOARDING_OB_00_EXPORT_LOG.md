# OB_00 — сохранение и статус (принято для Фазы B)

**Дата:** 2026-05-19  
**Стратегия:** Figma + QA по страницам сейчас; **Xcode batch в конце** (все imageset + симулятор).

## Полное сохранение макета (репозиторий)

| Файл | Описание |
|------|----------|
| `Resources/FigmaExports/OB_00/OB_00_Language_393x852_full.png` | **Весь фрейм** 393×852 (эталон «как в Figma») |
| `Resources/HeroAssets/OnboardingHero_00_figma_zone_361x460.png` | Слой героя для экспорта |
| `Resources/HeroAssets/OnboardingHero_00.png` | Мастер AI |
| Figma cloud | `FIGMA_ONBOARDING.env` → node `7:65` |

**Рекомендация в Figma:** *File → Save version* → `OB_00 accepted 2026-05-19`.

## QA Figma (без симулятора — отложен в конец)

| Проверка | Статус |
|----------|--------|
| Структура слоёв + CHROME_bottom | ✅ |
| Тексты RU = код | ✅ |
| OnboardingHero_00 export presets | ✅ |
| WCAG §4 Phase A | ☐ (при финале) |
| Симулятор | ☐ → **финальный Xcode batch** |

## Тексты

Продакшен: `14_OnboardingScreen.swift` + `LocalizationManager` (RU/EN в рантайме). Figma — только RU-макет.
