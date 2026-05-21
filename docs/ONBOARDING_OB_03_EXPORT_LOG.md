# OB_03 — параметры зоны героя и Figma (журнал)

**Дата:** 2026-05-19  
**Фрейм:** `OB_03_Parents_393x852` (`108:53`)  
**Слой героя:** `OnboardingHero_03` (`108:54`)

## Ничего не удалено

| Файл | Назначение |
|------|------------|
| `Resources/HeroAssets/OnboardingHero_03.png` | Каталогный мастер 393×852 (без изменений) |
| `Resources/HeroAssets/variants/OnboardingHero_03_master.png` | AI-мастер 1536×1024 |
| `Resources/HeroAssets/OnboardingHero_03_figma_zone_361x460_BEFORE_20260519.png` | **Бэкап** зоны до отдаления |

## Параметры compose (pre-compose → Figma FILL)

### Было (до отдаления, 2026-05-19 ~15:15)

| Параметр | Значение |
|----------|----------|
| Источник | `variants/OnboardingHero_03_master.png` (1536×1024) |
| `crop_w` | ~1000 (оценка по полному заполнению зоны) |
| `height_frac` | ~0.88 |
| `y_bias` | ~0.42 |
| Фон | `#0a1128` |
| Размер файла zone | 254 279 байт (~248 KB) |
| Силуэт в зоне | ~на всю высоту 460 pt |

### Стало (после «чуть отдалить»)

| Параметр | Значение |
|----------|----------|
| Источник | `variants/OnboardingHero_03_master.png` |
| **`crop_w`** | **1050** |
| **`height_frac`** | **0.82** |
| **`y_bias`** | **0.43** |
| Фон | `#0a1128` |
| Размещение в 361×460 | `nw=361`, `nh=352`, `ox=0`, `oy=46` |
| Figma `scaleMode` | **FILL** (PNG уже 361×460) |
| Размер файла zone | 196 385 байт (~192 KB) |

## Figma upload

- **2026-05-19:** заливка на `108:54`, `imageHash` в сессии MCP.
- Bounds: `361×460` @ `(16, 24)`, `cornerRadius` 8.

## Тексты RU (эталон код)

- **Title:** «Родительский контроль» — `onboarding_page3_title`
- **Desc:** «Система обучения детей безопасности. Вы видите всю активность детей в интернете. Самообучающаяся система защиты AI» — `onboarding_page3_desc` (`14_OnboardingScreen.swift` fallback; сверить с `LocalizationManager`)

## QA

| Проверка | Статус |
|----------|--------|
| §E-IMG6–7 скрины | после upload |
| G1–G10 | Figma QA — в работе |
| Продукт OK | ☐ |
| imageset / симулятор | 【Xcode batch】 |
