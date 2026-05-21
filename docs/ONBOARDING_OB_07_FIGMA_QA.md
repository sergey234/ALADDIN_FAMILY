# OB_07 — Figma + §E-IMG QA (2026-05-19)

## Figma nodeId

| Страница | Фрейм | Герой | Guide |
|----------|-------|-------|-------|
| OB_07 | `122:53` `OB_07_Invite_393x852` | `122:54` `OnboardingHero_07` | `122:70` `GUIDE_icon_ring_placeholder` |

**CHROME_bottom** `122:55` (y=548, h=304): `BLOCK_final_legal`, `ROW_secondary_actions`, кнопка «Начать», точки.

## §4.1 G1–G10 (агент)

| # | Статус | Примечание |
|---|:------:|------------|
| G1 скрин героя | ✅ | Концепт **C v2** centered (2026-05-19) |
| G2 иллюстрация | ✅ | Космос + круг доверия + лампа |
| G3 сюжет | ✅ | Замыкание арки 0→7 |
| G4 PNG в репо | ✅ | Master + 3 variants + zone |
| G5 тексты RU | ✅ | Title, desc, «Начать» + согласия + «Код»/«Восстановить» (LM) |
| G6 chrome 361×50 | ✅ | 8-я точка; расширенный chrome h=304 |
| G7 zone 361×460 | ✅ | crop 1050, hf 0.82, y 0.43 |
| G8 §E-IMG масштаб | ✅ | FILL на pre-composed zone |
| G9 скрин фрейма | ✅ | `FigmaExports/OB_07/OB_07_Invite_393x852_full.png` |
| G10 Продукт | ☐ | Выбор C / A / B |

## §E-IMG

| E0 | IMAGE fill на `122:54` | ✅ |
| E1 | Зона 361×460, позиция (16, 24) | ✅ |
| E2 | Pre-compose zone, не raw master в Figma | ✅ |
| E3 | Низ кадра не обрезан под title | ✅ (проверить визуально) |
| E4 | Без текста на герое | ✅ |

## Тексты (эталон `LocalizationManager` RU)

| Слой Figma | Ключ |
|------------|------|
| `TITLE_page7` | `onboarding_page7_title` |
| `DESC_page7` | `onboarding_page7_desc` |
| `CHROME_btn_continue` / `LABEL_continue` | `onboarding_start` |
| `TEXT_data_collection_info` | `onboarding_data_collection_info` |
| `TEXT_privacy_policy_link` | `onboarding_privacy_policy_link` |
| `ROW_data_consent` | `onboarding_data_consent` |
| `TEXT_terms_of_service_link` | `onboarding_terms_of_service_link` |
| `ROW_terms_consent` | `onboarding_terms_consent` |
| `CHROME_btn_have_code` | `onboarding_have_code` |
| `CHROME_btn_recover` | `onboarding_recover` |

**Позже:** `GUIDE_icon_ring_placeholder` → App Icon 140pt (не wordmark OB_01).

## Chrome dots

| Page | Активная точка |
|------|----------------|
| 7 | 8-я (index 7, 12×12, синяя) |

## Экспорт в репо

- `Resources/FigmaExports/OB_07/OB_07_Invite_393x852_full.png`
- `Resources/FigmaExports/OB_07/OnboardingHero_07_cosmic_stars_zone.png`
- `Resources/FigmaExports/OB_07/concepts/zone_{C,A,B}_361x460.png`

## Концепты

См. `ONBOARDING_OB_07_CONCEPTS.md`. По умолчанию в макете **C**.

## Batch (не в этой сессии)

- `OnboardingHero_07.imageset`
- Симулятор `currentPage == 7`
