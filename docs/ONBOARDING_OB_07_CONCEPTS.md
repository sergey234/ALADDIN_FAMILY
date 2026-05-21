# OB_07 — концепты героя «Присоединяйтесь» (2026-05-19)

## Продуктовый выбор (зелёная шляпа)

| ID | Название | Файл варианта | Назначение |
|----|----------|---------------|------------|
| **v4** | **Джин из куба** | `variants/OB07_v4/OnboardingHero_07_v4{B}.png` | **Актуальный выбор продукта** — без круга/семьи |
| v4A | Rise | `OnboardingHero_07_v4A_genie_from_cube.png` | Сильный луч из куба |
| v4B | Centered | `OnboardingHero_07_v4B_genie_from_cube_centered.png` | **Рекомендован** — центр, руки в кадре, хвост в свет куба |
| v4C | Wide arms | `OnboardingHero_07_v4C_genie_from_cube_wide.png` | Широкий жест |
| C v2 | (архив) | `OnboardingHero_07_conceptC_v2_centered.png` | С кругом доверия — снят с канона |
| A | Лампа ярче всех | `variants/OnboardingHero_07_conceptA_lamp_bright.png` | Запасной |
| B | Созвездие ALADDIN | `variants/OnboardingHero_07_conceptB_constellation.png` | Запасной |

Порядок генерации: **C → A → B**.

## Смысл кадра (канон арки)

- **0** — лампа в тумане → **7** — яркая tech-лампа + **замкнутый золотой круг доверия**
- **2–3** — дух Страж (тот же силуэт, что OB_03–06)
- **4–6** — звёздное небо + далёкая галактика
- Взгляд духа на зрителя — приглашение «присоединяйтесь»
- **Без текста** на PNG; кольцо под иконку — в UI; в Figma `GUIDE_icon_ring_placeholder` (иконку позже)
- **Chrome финала:** `BLOCK_final_legal` + `ROW_secondary_actions` — тексты из LM (согласия, «У МЕНЯ ЕСТЬ КОД», «ВОССТАНОВИТЬ»)
- **Логотип 140 pt:** PNG в `FigmaExports/Logo_OnboardingPage7/`; **в Figma на онбординге убран** (нет места на макетах); в приложении — слайд 7 (`ScrollView`) — позже

## Концепты (кратко)

### v4 — Джин из tech-куба (канон, май 2026)

Дух **вылетает из золотого куба-лампы** (синее ядро); **без** круга доверия и **без** силуэтов семьи в hero PNG. Обе руки и торс в кадре; космос 04–06; низ спокойный под title + chrome. Круг доверия — только в UI приложения (кольцо иконки), не в иллюстрации.

### A — Лампа ярче всех

Крупная лампа в центре (ярче, чем на 0); дух полупрозрачный сбоку, жест «добро пожаловать»; один оборот света вокруг лампы и духа.

### B — Созвездие ALADDIN

Дух в профиле; созвездие-лампа/щит на небе; золотые линии сходятся к tech-лампе внизу.

## AI / Tier

- Референс: `OnboardingHero_03_master` (Страж) + космос `OnboardingHero_06`
- Tier 3, без текста на изображении

## Zone 361×460 (как 04–06)

| Параметр | Значение |
|----------|----------|
| `crop_w` | 1100 (v2 centered) |
| `height_frac` | 0.78 |
| `y_bias` | 0.40 |
| Фон зоны | `#0a1128` |

Файлы zone:

- Канон: `Resources/HeroAssets/OnboardingHero_07_figma_zone_361x460.png`
- Экспорт: `Resources/FigmaExports/OB_07/OnboardingHero_07_cosmic_stars_zone.png`
- Варианты: `Resources/FigmaExports/OB_07/concepts/zone_{C,A,B}_361x460.png`

## Figma

| Элемент | nodeId |
|---------|--------|
| Фрейм `OB_07_Invite_393x852` | `122:53` |
| Герой `OnboardingHero_07` | `122:54` |
| Guide кольцо иконки | `122:70` `GUIDE_icon_ring_placeholder` |

Клон от `117:87` (OB_06).

## Тексты RU (эталон)

| Слой | Текст |
|------|-------|
| TITLE | Присоединяйтесь к ALADDIN |
| DESC | Спокойствие близких - бесценно. Защита начинается сегодня! |
| Кнопка | **Начать** (`onboarding_start`, не «Продолжить») |

## Chrome

- Активная точка: **8-я** (index 7)
- Кнопка: `CHROME_btn_continue` → label «Начать»

## Смена концепта в Figma

1. Скопировать выбранный master из `variants/` → пересобрать zone (скрипт как для 04–06) или взять готовый `concepts/zone_*_361x460.png`
2. `upload_assets` → `122:54`, `scaleMode=FILL`
3. Обновить `OnboardingHero_07.png` в `HeroAssets/`

## Batch (не в этой сессии)

- `OnboardingHero_07.imageset`
- Симулятор `currentPage == 7`
- **MAIN** — следующий шаг: дух + лампа, calm idle «остались с вами»

## QA

См. `docs/ONBOARDING_OB_07_FIGMA_QA.md` — §E-IMG + G1–G10; **Продукт OK** — после вашего выбора C / A / B.
