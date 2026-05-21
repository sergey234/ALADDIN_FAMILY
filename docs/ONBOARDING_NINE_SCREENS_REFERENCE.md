# Девять экранов: справочник (0 + 7 онбординг + Main)

Фиксация для команды и ML: **имена ассетов героя**, **слот кода**, **ключи локализации** (копирайт не в PNG), **особенности вёрстки**. Подробный план — `ONBOARDING_MAIN_HERO_HANDOFF.md`. Отдельный снимок кода шага **0** — `ONBOARDING_STEP0_LANGUAGE_SNAPSHOT.md`.

**Фаза A (wireframe, зоны, WCAG):** детально в `ONBOARDING_MAIN_HERO_HANDOFF.md` §**1.4–1.7** (393×852, hero ~60% / карточка ~40%, нижний chrome, матрица индексов, таблица `page.color`). **Готовые замеры контраста (hex + X:1):** `ONBOARDING_WCAG_MEASUREMENTS.md`. **Чеклист слоёв по каждому фрейму Figma (копипаст):** `ONBOARDING_FIGMA_FRAME_CHECKLIST.md`. **Закрытие Фазы A (продукт, a11y-строки, WCAG в макете, URL Figma):** `ONBOARDING_PHASE_A_COMPLETION.md`. **URL/file key для MCP:** `docs/FIGMA_ONBOARDING.env` (шаблон: `FIGMA_ONBOARDING.env.example`). **Как взять ссылку и key:** `FIGMA_LINK_INSTRUCTIONS.md`.

| № экрана для человека | `currentPage` | `contentIndex` | Экран | Акцент `page.color` (`createFullPages`) | `HeroSlot` / ассет Xcode | Ключи локализации (контент) | Примечание |
|----------------------|---------------|----------------|--------|----------------------------------------|--------------------------|----------------------------|------------|
| 0 | `0` | — | Язык | (шаг языка, не `OnboardingPage`) | `.onboardingLanguage` → `OnboardingHero_00` | `languageStepTitle` / `languageStepContinueTitle` (и список языков) | `ONBOARDING_STEP0_LANGUAGE_SNAPSHOT.md` |
| 1 | `1` | `0` | Семья / щит | `Color.primaryBlue` | `.onboardingContent(0)` → `OnboardingHero_01` | `onboarding_page1_title` / `onboarding_page1_desc` | Сверху `OnboardingAladdinLogoView` |
| 2 | `2` | `1` | ИИ | `Color.successGreen` | `.onboardingContent(1)` → `OnboardingHero_02` | `onboarding_page2_*` | Parallax в коде разрешён для этого слота |
| 3 | `3` | `2` | Родители | `Color.orange` | `.onboardingContent(2)` → `OnboardingHero_03` | `onboarding_page3_*` | |
| 4 | `4` | `3` | Аналитика / радар | `Color.red` | `.onboardingContent(3)` → `OnboardingHero_04` | `onboarding_page4_*` | Сюжетный **ping** при входе — в коде TODO |
| 5 | `5` | `4` | Дети | `Color.purple` | `.onboardingContent(4)` → `OnboardingHero_05` | `onboarding_page5_*` | |
| 6 | `6` | `5` | 23+ | `Color.blue` | `.onboardingContent(5)` → `OnboardingHero_06` | `onboarding_page6_*` | |
| 7 | `7` | `6` | Приглашение | `Color.green` | `.onboardingContent(6)` → `OnboardingHero_07` | `onboarding_page7_*` | `ScrollView` + иконка в кольце при `contentIndex == 6` |
| Main | — | — | Главный | — | `.mainDashboard` → `MainHero_ambient` | UI `01_MainScreen.swift` | `HeroMainScreenBackdrop` под `VStack` |

**Связь индексов:** `currentPage == 0` → язык; `currentPage == 1…7` → контент; **`contentIndex = currentPage - 1`** (0…6) внутри `onboardingPage`.

**Индекс вкладки `TabView`:** совпадает с `currentPage` для шагов 0…7.

---

*Обновлять таблицу при смене ключей локализации, имён ассетов в `HeroAmbientPresentation.swift` или акцентных цветов в `createFullPages()`.*
