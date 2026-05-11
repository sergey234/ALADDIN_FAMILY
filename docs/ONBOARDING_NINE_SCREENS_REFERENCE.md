# Девять экранов: справочник (0 + 7 онбординг + Main)

Фиксация для команды и ML: **имена ассетов героя**, **слот кода**, **ключи локализации** (копирайт не в PNG), **особенности вёрстки**. Подробный план — `ONBOARDING_MAIN_HERO_HANDOFF.md`. Отдельный снимок кода шага **0** — `ONBOARDING_STEP0_LANGUAGE_SNAPSHOT.md`.

| № | Экран | `HeroSlot` / ассет Xcode | Источник текста (контент) | Примечание |
|---|--------|--------------------------|---------------------------|------------|
| 0 | Язык | `.onboardingLanguage` → `OnboardingHero_00` | Заголовок/кнопка: локальные фразы в `languageStepTitle` / `languageStepContinueTitle` | Снимок: `ONBOARDING_STEP0_LANGUAGE_SNAPSHOT.md` |
| 1 | Контент 1 (семья) | `.onboardingContent(0)` → `OnboardingHero_01` | `onboarding_page1_title` / `onboarding_page1_desc` | `createFullPages()` первая страница; сверху `OnboardingAladdinLogoView` |
| 2 | Контент 2 (ИИ) | `.onboardingContent(1)` → `OnboardingHero_02` | `onboarding_page2_*` | Parallax в коде разрешён для этого слота |
| 3 | Контент 3 (родители) | `.onboardingContent(2)` → `OnboardingHero_03` | `onboarding_page3_*` | |
| 4 | Контент 4 (аналитика / «радар») | `.onboardingContent(3)` → `OnboardingHero_04` | `onboarding_page4_*` | Сюжетный «пинг» — задача в TODO |
| 5 | Контент 5 (дети) | `.onboardingContent(4)` → `OnboardingHero_05` | `onboarding_page5_*` | |
| 6 | Контент 6 (23+) | `.onboardingContent(5)` → `OnboardingHero_06` | `onboarding_page6_*` | |
| 7 | Контент 7 (приглашение) | `.onboardingContent(6)` → `OnboardingHero_07` | `onboarding_page7_*` | Особый layout: `ScrollView` + иконка в кольце (`contentIndex == 6`) |
| 9 | **Main** (не вкладка TabView) | `.mainDashboard` → `MainHero_ambient` | Весь UI из `01_MainScreen.swift` | `HeroMainScreenBackdrop` в ZStack под `VStack` |

**Связь индексов:** `currentPage` 0 = язык; `currentPage` 1…7 = контент; `contentIndex` в `onboardingPage` = `currentPage - 1` (0…6).

---

*Обновлять таблицу при смене ключей локализации или имён ассетов в `HeroAmbientPresentation.swift`.*
