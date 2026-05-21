# Handoff: онбординг — картинки на весь экран (ALADDIN iOS)

Документ для ML/дизайн/разработка: как добиться и сохранить **full-bleed** hero на всех страницах онбординга.

## Цель

Фоновые иллюстрации (`OnboardingHero_00` … `07`) **заполняют весь экран** — без тёмных полос по бокам/сверху от старого градиента. Поведение одинаковое на **симуляторе** и **TestFlight / iPhone**.

---

## Две разные проблемы (не путать)

| # | Симптом | Причина | Решение |
|---|---------|---------|---------|
| **A** | На симуляторе есть картинка, на телефоне пусто/эмодзи | PNG только локально, **не в git** → нет в Archive | Закоммитить imageset + `pbxproj` (build **198**, `c0cc1730`) |
| **B** | Картинка есть, но **узкая по центру**, по бокам тёмный фон | SwiftUI рисовал **`.fit`**, не **`.fill`** | `fillsViewport` + `scaledToFill` (build **199**, `9f43a362`) |

Сеть и API здесь **не при чём**.

---

## Правило для всех будущих hero-картинок

### 1. Ассет (до Xcode)

| Параметр | Значение |
|----------|----------|
| Имя в Asset Catalog | `OnboardingHero_00` … `OnboardingHero_07` |
| Размер кадра | **393 × 852 pt** (логический iPhone-эталон) |
| Сборка | `scripts/build_onboarding_hero_imagesets.py` |
| Источники | `Resources/HeroAssets/` → `Assets.xcassets/*.imageset` |
| Wide-мастера (00, 04–07) | Зона `*_figma_zone_361x460.png` на фон `#0a1128`, offset (16, 24) |
| Уже 393×852 (01–03) | Копия как есть |
| Иначе | Center **cover crop** до 393×852 |

**Обязательно:** PNG в **git** и в **Copy Bundle Resources** — иначе TestFlight без картинок.

См. также: `docs/ONBOARDING_XCODE_BATCH_20260520.md`, `docs/ONBOARDING_MAIN_HERO_HANDOFF.md` (§1.4).

### 2. Код (только онбординг = full-bleed)

| Файл | Роль |
|------|------|
| `Shared/Components/HeroAmbientPresentation.swift` | `fillsViewport`, `scaledToFill` / Lottie `scaleAspectFill` |
| `Screens/14_OnboardingScreen.swift` | `HeroAmbientLayerView` + `.ignoresSafeArea()` |

| Что | Как |
|-----|-----|
| Режим | `fillsViewport == true` для `.onboardingLanguage` и `.onboardingContent` |
| Растр | `.resizable()` → `.scaledToFill()` → `.clipped()` → frame на весь `GeometryReader` |
| Lottie | `.scaleAspectFill` + `clipsToBounds` |
| Layout | `HeroAmbientLayerView` + **`.ignoresSafeArea()`** |
| Видимость | **Не** `.opacity(0.4)` на hero; лёгкий emotion wash |
| Главный экран | `fillsViewport == false` — **fit**, не full-screen |

Тексты, CTA и `HeroBottomReadableGradient` для читаемости снизу **не убирать**.

---

## Маппинг TabView ↔ ассет

| `currentPage` | `HeroSlot` | Xcode asset |
|---------------|------------|-------------|
| 0 | `.onboardingLanguage` | `OnboardingHero_00` |
| 1 … 7 | `.onboardingContent(0…6)` | `OnboardingHero_01` … `07` |

---

## Чеклист для новой картинки `OnboardingHero_XX`

1. Экспорт / мастер в `Resources/HeroAssets/`.
2. Прогнать `python3 scripts/build_onboarding_hero_imagesets.py`.
3. Проверить размер **393×852** в imageset.
4. Закоммитить `Assets.xcassets/OnboardingHero_XX.imageset/` (+ `pbxproj` при новом файле).
5. Имя = канон в `HeroPresentation.presentation(for:)`.
6. TestFlight на **реальном iPhone**: нет полос по бокам (края могут слегка crop — норма для fill).

---

## Коммиты (хронология)

```
161d69c3  HeroAmbientLayerView + ignoresSafeArea
e833f06d  OnboardingHero_00 + pipeline docs
95e09c35  убрали opacity 0.4, осветлили wash
(batch)     PNG 393×852 (Python)
c0cc1730  heroes в git + pbxproj     ← проблема A
9f43a362  scaledToFill / fillsViewport ← проблема B
```

---

## Одна фраза

> **Full-screen онбординг = PNG 393×852 в бандле (git) + SwiftUI `scaledToFill` с `ignoresSafeArea` только для onboarding-слотов; полосы по бокам — из `.fit`, пустой экран на iPhone — из отсутствия PNG в TestFlight.**

---

## Не делать

- Не использовать **fit** для onboarding hero (только `MainHero_ambient` на главной).
- Не оставлять imageset только локально.
- Не затемнять hero `opacity(0.4)`.
- Не путать «нет картинки» (A) с «картинка в рамке» (B).

---

## Figma — текущие параметры (live, file `KvkUdyb5Ll31Z9FSzCbpNl`)

Проверено через Figma MCP `get_metadata`, 2026-05-21.

**Канон для full-bleed в приложении:** фрейм **393×852**; слой героя **361×460** @ **(16, 24)**; в Xcode финальный PNG **393×852** (`scaledToFill`).

| Страница | Figma frame | nodeId | Слой `OnboardingHero_XX` | Размер | Позиция (x,y) | Статус vs канон |
|----------|-------------|--------|--------------------------|--------|---------------|-----------------|
| OB_00 Язык | `OB_00_Language_393x852` | `7:65` | `7:66` | 361×460 | (16, 24) | OK |
| OB_01 Семья | `OB_01_Family_393x852` | `81:53` | `81:54` | 361×460 | (16, 24) | OK |
| OB_02 ИИ | `OB_02_AI_393x852` | `103:53` | `103:54` | 361×460 | (16, **26**) | y +2 |
| OB_03 Родители | `OB_03_Parents_393x852` | `108:53` | `108:54` | **401×503** | (16, **40**) | **не канон** — выровнять до 361×460 @ (16,24) |
| OB_04 Радар | `OB_04_Radar_393x852` | `117:53` | `117:54` | 361×460 | (**10**, **36**) | x/y сдвиг |
| OB_05 Дети | `OB_05_Kids_393x852` | `117:70` | `117:71` | 361×460 | (**6**, **18**) | x/y сдвиг |
| OB_06 23+ | `OB_06_Adults23_393x852` | `117:87` | `117:88` | 361×460 | (16, 24) | OK |
| OB_07 Приглашение | `OB_07_Invite_393x852` | `122:53` | `122:54` | 361×460 | (16, 24) | OK |

**Chrome (все OB_01…06):** `CHROME_bottom` 361×118 @ (16, 710); кнопка 361×50.  
**OB_00:** `CHROME_bottom` 361×85 @ (16, 743).  
**OB_07:** `CHROME_bottom` 361×**304** @ (17, **556**) — расширенный блок (согласия + 2 кнопки).

**Масштаб растра в Figma (доки QA):** OB_04–07 — pre-compose zone 361×460, upload **`scaleMode=FILL`**. OB_03 — FILL на PNG 361×460 после compose.

**Ссылки:** `docs/FIGMA_ONBOARDING.env` · чеклист `ONBOARDING_FIGMA_FRAME_CHECKLIST.md` · архив nodeId `ONBOARDING_FIGMA_EXPORT_ARCHIVE_20260519.md`

---

*Обновлено: 2026-05-21 · build 199+ (код fill), build 198 (ассеты в git)*
