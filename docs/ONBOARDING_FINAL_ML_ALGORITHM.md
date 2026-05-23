# Финальный алгоритм онбординга ALADDIN (для ML / агентов / команды)

**Версия:** 2026-05-22 · **Проект:** `ALADDIN_iOS` only (не `ALADDIN_PUSH187`).  
**Figma file key:** `KvkUdyb5Ll31Z9FSzCbpNl` · env: `docs/FIGMA_ONBOARDING.env`.

Этот файл — **единая точка входа**. Другая ML-система должна начать здесь, затем ссылаться на детальные документы.

---

## 0. К чему стремимся (эталон)

### 0.1 Продуктовый эталон (после 4 wellness-референсов)

| Принцип | Эталон | Запрещено |
|---------|--------|-----------|
| Hero | **Full-bleed** 393×852 в PNG, в приложении `scaledToFill` + `ignoresSafeArea` | Ужимать hero до 60% в ассете; «две картинки» (zone растянута на весь экран) |
| Текст | **Низ экрана**, читаемая зона со **scrim**, не по центру `Spacer` | Серый `textSecondary` на фото; левый «журнал» |
| Шрифт | **SF Pro**: title **24 Bold** (22 на SE), body **16 Regular**, **белый** body **~92%** | Inter в макете/коде для 01–06 |
| Позиция текста | **Y из Figma** (`OnboardingFigmaAnchoredContent`) | Плавающий блок без координат |
| Copy | Только из `LocalizationManager` / ключи `onboarding_pageN_*` | Новый текст в PNG hero; выдуманный copy в Figma |
| Chrome | Точки + одна CTA в **коде** (вне TabView) | Tab bar как у референсов |
| Лого wordmark | **Только OB_01** — `OnboardingLogo_V2`, 361×104 @ y=484 | Wordmark на 02–06 |
| Слои | PNG = **только арт**; UI в SwiftUI | Текст/кнопки в экспорте hero |

### 0.2 Технический эталон «одна правда»

```text
master (или канон PNG)
    → cover / compose → OnboardingHero_0N.png (393×852)
    → ОДИН MD5 в Figma (node OnboardingHero_0N) И в Assets.xcassets
    → iOS: HeroAmbientLayerView + OnboardingFigmaAnchoredContent (Y из Figma)
    → Visual QA: симулятор SE + Pro Max ≈ Figma frame
```

**STOP:** не писать «готово», пока **симулятор ≠ Figma по hero/scrim** или §D Visual QA не пройден.  
`imageHash` Figma **≠** `md5` файла — это норма; критерий — **один и тот же PNG** залит в imageset и в Figma upload.

### 0.3 Инцидент OB_02 / OB_03 (2026-05-22) — обязательные проверки

| Было не так | Симулятор | Figma (эталон) |
|-------------|-----------|----------------|
| OB_02 hero | cover-crop `dc46b525…` | zone94 center `be22a36d…` / hash `c5a72085…` |
| OB_03 hero | старый full-bleed ≠ макет | zone94-style `73cfae32…` |
| Scrim stops | везде middle **@0.4** | OB_02 **@0.45** (0.189), OB_03 **@0.4** (0.16) |

**Правила против регрессии:**

1. **SYNC-H:** после правки hero — `cp` PNG в `Assets.xcassets` **и** `upload_assets` с **этого же файла**; записать md5 в `ONBOARDING_SYNC_LOG_*.md`.
2. **SYNC-T-S5 (новое):** `READABILITY_scrim_bottom.gradientStops` = `scrimGradientStops(for: anchor)` (позиция **и** alpha).
3. **SYNC-D (обязательно):** `xcrun simctl launch booted family.aladdin.ios -RESET_ONBOARDING -OnboardingPageN` — сравнить с Figma frame **до** ✅.
4. **Нельзя** помечать SYNC-I ✅, если imageset md5 не обновляли после смены Figma hero.

**Мастер TODO:** `docs/ONBOARDING_TODO_MASTER.md` (≈30 пунктов, 11 открыты).

---

## 1. Общая картина: 9 экранов

| OB | `currentPage` | `contentIndex` | Figma frame | nodeId | Hero asset | Scope финального алгоритма |
|----|---------------|----------------|-------------|--------|------------|----------------------------|
| **00** | 0 | — | `OB_00_Language_393x852` | `7:65` | `OnboardingHero_00` | Отдельный snapshot; **не** 01–06 readability |
| **01** | 1 | 0 | `OB_01_Family_393x852` | `81:53` | `OnboardingHero_01` | ✅ H,T,I,C — ⏳ **D** |
| **02** | 2 | 1 | `OB_02_AI_393x852` | `103:53` | `OnboardingHero_02` | ✅ H,T,I,C — ⏳ **D** (zone94) |
| **03** | 3 | 2 | `OB_03_Parents_393x852` | `108:53` | `OnboardingHero_03` | ✅ H,T,I,C — ⏳ **D** (zone94-style) |
| **04** | 4 | 3 | `OB_04_Radar_393x852` | `117:53` | `OnboardingHero_04` | ⏳ Figma Y + MD5 |
| **05** | 5 | 4 | `OB_05_Kids_393x852` | `117:70` | `OnboardingHero_05` | ⏳ Figma Y + MD5 |
| **06** | 6 | 5 | `OB_06_Adults23_393x852` | `117:87` | `OnboardingHero_06` | ⏳ Figma Y + MD5 |
| **07** | 7 | 6 | `OB_07_Invite_393x852` | `122:53` | `OnboardingHero_07` | **Вне scope** (ScrollView, согласия) |
| Main | — | — | — | — | `MainHero_ambient` | `01_MainScreen.swift` |

**Индексы:** `contentIndex = currentPage - 1` для контента 1…7.

---

## 2. Ключевые файлы (куда смотреть)

| Назначение | Путь |
|------------|------|
| Экран онбординга | `Screens/14_OnboardingScreen.swift` |
| Hero слой, parallax, fill | `Shared/Components/HeroAmbientPresentation.swift` |
| Figma Y anchors | `OnboardingFigmaAnchor` в `14_OnboardingScreen.swift` |
| Локализация RU/EN | `Core/Localization/LocalizationManager.swift` |
| Сборка imageset | `scripts/build_onboarding_hero_imagesets.py` |
| Мастера hero | `Resources/HeroAssets/`, `Resources/HeroAssets/variants/` |
| Детальный QA одной страницы | `docs/ONBOARDING_FIGMA_PAGE_QA_ALGORITHM.md` |
| План читаемости 01–06 | `docs/ONBOARDING_OB_01_06_READABILITY_PLAN.md` |
| Журнал по страницам | `docs/ONBOARDING_PAGE_BY_PAGE_LOG.md` |
| Правила слоёв | `docs/ONBOARDING_LAYER_RULES.md` |
| Индексы/ключи | `docs/ONBOARDING_NINE_SCREENS_REFERENCE.md` |
| Приёмка растра §E-IMG | `docs/ONBOARDING_FIGMA_PAGE_QA_ALGORITHM.md` §E-IMG |
| Сюжет героя | `docs/ALADDIN_Onboarding_Prompts.md` |

---

## 3. Финальный алгоритм на ОДНУ страницу (OB_01…OB_06)

**Не переходить к OB_(N+1), пока OB_N не «Принято».**

**Правило синхронизации:** после **каждой** подзадачи (hero / Figma / iOS / тексты) — обязательный шлюз **§3.1 SYNC**. Без галочки SYNC следующий шаг **запрещён**.

---

### §3.1 SYNC — сверка Figma ↔ iOS (после КАЖДОЙ подзадачи)

Одна страница `OB_NN`, `contentIndex = N-1`. Инструменты: Figma MCP `use_figma` / `get_screenshot`, `md5` PNG, симулятор Xcode, `grep` в `14_OnboardingScreen.swift`.

#### SYNC-H — после Hero (шаг 1)

| # | Figma | iOS / репо | Критерий «ОК» |
|---|-------|------------|---------------|
| H-S1 | Узел `OnboardingHero_0N`: **393×852**, (0,0) | `Assets.xcassets/OnboardingHero_0N.imageset/*.png` | Размер **393×852** |
| H-S2 | `imageHash` из fill слоя (справочно) | `md5` imageset PNG | Записать md5 в SYNC-log; upload из **этого** PNG |
| H-S3 | `get_screenshot` hero — силуэт целиком | Симулятор `currentPage==N` — **тот же кадр** | Нет полос; руки/лампа видны (OB_02: zone94) |
| H-S4 | В Figma **один** слой hero (не два RECTANGLE с IMAGE) | `HeroAmbientLayerView` — один raster/Lottie | Нет «двух картинок» |
| H-S6 | **md5 до/после** в журнале | Файл на диске после `cp` | Не оставлять старый md5 в imageset при «готовом» Figma |

**Записать в журнал:** `ONBOARDING_PAGE_BY_PAGE_LOG.md` — MD5 / imageHash.

#### SYNC-T — после типографики в Figma (шаг 2)

| # | Figma (`use_figma` audit) | iOS (эталон) | Критерий «ОК» |
|---|-------------------------|--------------|---------------|
| T-S1 | `TITLE_pageN`: **SF Pro Bold**, 24 | `OnboardingWholeWordText` Bold 24 | Совпадает |
| T-S2 | `DESC_pageN`: **SF Pro Regular**, 16, white **~92%** | white.opacity(0.92) | Не серый #BFC7D9 |
| T-S3 | Y title / desc / wordmark | §4 таблица | **±0 pt** в Figma; в iOS — те же числа в `OnboardingFigmaAnchor` |
| T-S4 | `READABILITY_scrim_bottom` y,h | `anchor.scrim` rect | **±0 pt** y,h,w |
| T-S5 | `gradientStops` (pos + alpha) | `scrimGradientStops(for:)` | OB_02: **0.45**/0.189; OB_03: **0.4**/0.16; max = `scrimMaxOpacity` |

#### SYNC-I — после правки iOS (шаг 3)

| # | Проверка в коде | Критерий «ОК» |
|---|-----------------|---------------|
| I-S1 | `OnboardingFigmaAnchor.forContentIndex(N-1)` **не nil** | case есть для страницы |
| I-S2 | CGRect title/desc/scrim == §4 | Побайтно те же x,y,w,h |
| I-S3 | `onboardingPage` → `OnboardingFigmaAnchoredContent`, **не** `OnboardingBottomTextPanel` | Для 01–06 после внедрения |
| I-S4 | `onboarding_pageN_title/desc` в `LocalizationManager` | Строки = Figma §C |

#### SYNC-C — тексты (шаг 4, можно вместе с SYNC-I)

| # | Figma слой | Код |
|---|------------|-----|
| C-S1 | `TITLE_pageN`.characters | `localized("onboarding_pageN_title")` |
| C-S2 | `DESC_pageN`.characters | `localized("onboarding_pageN_desc")` |

#### SYNC-D — финал страницы (шаг 5 + STOP)

| # | Действие | Критерий «ОК» |
|---|----------|---------------|
| D-S1 | Скрин **всего фрейма** Figma `OB_NN_*` | Скрин симулятора `-OnboardingPageN` | Hero **не другой кадр** |
| D-S2 | Side-by-side: hero + scrim + текст + chrome | Визуально **≈** (SE ±8–12 pt по Y) | Scrim переход плавный, не «полоса» |
| D-S3 | RU + EN в симуляторе | Текст в границах, целые слова |
| D-S4 | Статус в журнале | **«Принято»** только после D-S1…D-S3 |

```text
Подзадача H → SYNC-H → OK?
Подзадача Figma T → SYNC-T → OK?
Подзадача iOS I → SYNC-I (+ SYNC-C) → OK?
Подзадача §D → SYNC-D → «Принято» → следующая страница
```

**STOP:** если SYNC на любом шаге FAIL — **не** переходить к OB_(N+1); исправить и повторить SYNC.

---

### Шаг 0 — STOP-шлюз (в конце, обязателен)

См. `ONBOARDING_FIGMA_PAGE_QA_ALGORITHM.md` §0 и §E-IMG:

- [ ] `get_screenshot` узла `OnboardingHero_0N` — не пустая заливка
- [ ] Голова / руки / ключевой силуэт **целиком** (инцидент OB_02: битый 393×852)
- [ ] **MD5** (или визуально идентично) Figma fill == `Assets.xcassets/OnboardingHero_0N.imageset`
- [ ] Тексты §C = LocalizationManager
- [ ] Visual QA §D: симулятор ≈ Figma

---

### Шаг 1 — Hero (процесс 1–4 из согласования)

| # | Действие | Как |
|---|----------|-----|
| H1 | Взять **мастер** | `Resources/HeroAssets/variants/OnboardingHero_0N_master.png` или канон из `ONBOARDING_MASTER_IMPLEMENTATION_PLAN.md` §5 |
| H2 | Собрать **393×852** | **Предпочтительно:** center **cover crop** из master. **Нельзя:** растянуть `*_figma_zone_361x460.png` на весь экран как финал (OB_02 инцидент). Для 04–06: compose zone на `#0a1128` только если zone качественная |
| H3 | Записать в Xcode | `Assets.xcassets/OnboardingHero_0N.imageset/OnboardingHero_0N.png` + `Resources/HeroAssets/OnboardingHero_0N.png` |
| H4 | Загрузить в Figma | `upload_assets` → node `OnboardingHero_0N`, **393×852** @ (0,0), `scaleMode=FILL` |
| H5 | Проверить MD5 | Figma imageHash / export == Xcode file |

**Скрипт `build_onboarding_hero_imagesets.py`:** если `mw==393 && mh==852`, **не слепо копировать** — сверить с master (TODO: доработать скрипт).

---

### Шаг 2 — Figma макет (типографика + scrim)

На фрейме `OB_NN_*_393x852`:

| Слой | Эталон |
|------|--------|
| `OnboardingHero_0N` | 393×852 @ (0,0), без текста в PNG |
| `READABILITY_scrim_bottom` | Градиент снизу (opacity по таблице §4) |
| `TITLE_pageN` | SF Pro **Bold 24**, white, center, **Y из §4** |
| `DESC_pageN` | SF Pro **Regular 16**, white **92%**, center, **Y из §4** |
| `WORDMARK_V2` | **Только N=1** |
| `CHROME_bottom` | Плейсхолдер (реальный chrome в iOS под TabView) |

---

### Шаг 3 — iOS код

| # | Действие | Где |
|---|----------|-----|
| I1 | Добавить case в `OnboardingFigmaAnchor.forContentIndex` | `14_OnboardingScreen.swift` — **rect из §4** |
| I2 | Убедиться: страница идёт через `OnboardingFigmaAnchoredContent`, **не** `OnboardingBottomTextPanel` | `onboardingPage()` |
| I3 | Шрифт/цвет | `OnboardingWholeWordText`: Bold 24 / Regular 16, white / white 0.92 |
| I4 | Перенос | Целые слова: `allowsTightening(false)`, `lineLimit` по длине desc |
| I5 | Градиент экрана | `HeroBottomReadableGradient(strong:)` для `currentPage` 1…6 |
| I6 | Parallax | Только OB_02 (`OnboardingHero_02`) — декоративные круги, не второй PNG |

**Координаты:** screen Y (852 canvas) → TabView: `tabTopY(y) = (y - 52) * (tabHeight / 646)`.

---

### Шаг 4 — Сверка текстов (§C)

| Ключ | Проверка |
|------|----------|
| `onboarding_pageN_title` | = слой `TITLE_pageN` в Figma |
| `onboarding_pageN_desc` | = слой `DESC_pageN` |

Источник: `LocalizationManager.swift` (RU для базового макета).

---

### Шаг 5 — Visual QA (§D)

Устройства: **iPhone SE (375)** + **Pro Max (430+)**. Языки: **RU + EN**.

- [ ] Hero на весь экран, без полос «другого фона» по краям
- [ ] Руки/голова/лампа не обрезаны
- [ ] Текст не уходит под точки/кнопку; не режет слова посередине
- [ ] Позиция текста визуально ≈ Figma (допуск ~8–12 pt на SE из-за scale)

---

## 4. Таблица координат Figma → iOS (эталон Y, 393×852)

**Screen Y** (от верха фрейма 852). iOS: `OnboardingFigmaAnchor` + `OnboardingFigmaScreenLayout` (`skipBandHeight=52`, `chromeBandHeight=154`, `tabDesignHeight=646`).

| OB | Wordmark (x,y,w,h) | Title (x,y,w,h) | Desc (x,y,w,h) | Scrim (y,h) | opacity | iOS anchor | Статус |
|----|-------------------|-----------------|---------------|-------------|---------|------------|--------|
| **01** | 16,**484**,361,104 | 16,**598**,361,50 | 16,**656**,361,48 | **528**,324 | 0.45 | ✅ case 0 | ✅ |
| **02** | — | 12,**533**,361,60 | 12,**607**,361,80 | **552**,300 | 0.42 | ✅ case 1 | ✅ SYNC H,T,I,C |
| **03** | — | 16,**552**,361,60 | 14,**630**,361,80 | **500**,320 | 0.40 | ✅ case 2 | ✅ H,T,I,C — ⏳ D |
| **04** | — | 16,**496**,361,60 | 16,**566**,361,100 | **542**,310 | 0.35 | ⏳ case 3 | ⏳ |
| **05** | — | 16,**496**,361,60 | 16,**566**,361,100 | **532**,320 | 0.38 | ⏳ case 4 | ⏳ |
| **06** | — | 16,**496**,361,60 | 16,**566**,361,100 | **552**,300 | 0.40 | ⏳ case 5 | ⏳ |

**Figma nodeId hero:** 01 `81:54`, 02 `103:54`, 03 `108:54`, 04 `117:54`, 05 `117:71`, 06 `117:88`.

---

## 5. Сюжет героя (что должно быть видно — §E-IMG)

| N | Обязательно в кадре | Запрещено |
|---|---------------------|-----------|
| 1 | Человек B1, дом, лампа | Единорог, двойная голова в PNG |
| 2 | Дух «Пробуждение», руки, tech-лампа | Человек, единорог, двойной composite |
| 3 | Дух «Страж», силуэт, лампа | Человек, единорог |
| 4 | Космос, радар, дух | Дубль ping в PNG+код |
| 5 | Щит, защита детей | — |
| 6 | Лента сейчас→скоро→предотвращено | — |

Промпты: `docs/ALADDIN_Onboarding_Prompts.md`.

---

## 6. Текущий статус реализации (снимок 2026-05-22)

| Блок | 01 | 02 | 03 | 04 | 05 | 06 |
|------|----|----|----|----|----|-----|
| Figma SF Pro + white desc | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Figma scrim layer | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Figma hero 393×852 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| iOS белый текст + gradient | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| iOS **Figma Y** anchors | ✅ | ✅ | ✅ | ⏳ | ⏳ | ⏳ |
| Hero PNG = Figma upload | ✅ | ✅ zone94 | ✅ zone94 | ⏳ | ⏳ | ⏳ |
| Scrim stops = код | ✅ | ✅ @0.45 | ✅ @0.4 | ⏳ | ⏳ | ⏳ |
| §D Visual QA | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |

---

## 7. Очередь работ (строго по порядку)

```text
См. docs/ONBOARDING_TODO_MASTER.md (30 пунктов, ~11 открыты)

OB_01 → только SYNC-D (симулятор ≈ Figma)
OB_04 → hero (тот же PNG → imageset + upload) → anchor case 3 → SYNC H,T,I,C,D
OB_05 → то же → case 4
OB_06 → то же → case 5
Скрипт build_onboarding_hero_imagesets.py → не слепо копировать 393×852
read-docs → §11 ONBOARDING_FIGMA_PAGE_QA_ALGORITHM на 01–06
```

**Перед ✅:** всегда SYNC-H (md5 + upload) → SYNC-T (**T-S5 stops**) → SYNC-I → **SYNC-D**.

**OB_07** — отдельный трек (согласия, ScrollView), не смешивать с 01–06.

---

## 8. Deep links Figma (desktop Mac)

```text
OB_01: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=81-53
OB_02: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=103-53
OB_03: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=108-53
OB_04: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=117-53
OB_05: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=117-70
OB_06: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=117-87
OB_07: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=122-53
```

---

## 9. Типичные ошибки (не повторять)

| Симптом | Причина | Fix |
|---------|---------|-----|
| «Две картинки», полосы по краям | Битый 393×852 (zone stretched) | master → cover → один MD5 |
| Руки/голова обрезаны | FILL на плохом PNG | Пересобрать кадр, §E-IMG5 |
| Текст выше/ниже Figma | `OnboardingBottomTextPanel` вместо anchor | Добавить `OnboardingFigmaAnchor` case |
| Серый desc | `textSecondary` | white 0.92 |
| «Готово» без скрина | Пропуск §0 / §D | STOP-шлюз |

---

## 10. Definition of Done (страница OB_01…06)

Страница **«Принято»** только если пройдены **все SYNC-шлюзы** §3.1:

1. ✅ **SYNC-H** — hero MD5 Figma = Xcode, один слой, §E-IMG  
2. ✅ **SYNC-T** — Figma SF Pro, white desc, Y из §4  
3. ✅ **SYNC-I** — iOS anchor = §4, не BottomTextPanel  
4. ✅ **SYNC-C** — строки = LocalizationManager  
5. ✅ **SYNC-D** — симулятор ≈ Figma (SE + Pro Max, RU + EN)  
6. ✅ Запись в `ONBOARDING_PAGE_BY_PAGE_LOG.md` (MD5, hashes, дата SYNC)

---

## 11. Чеклист SYNC по страницам (копипаст в todo)

| OB | Hero SYNC-H | Figma SYNC-T | iOS SYNC-I | Тексты SYNC-C | Visual SYNC-D | Принято |
|----|:-----------:|:------------:|:----------:|:-------------:|:-------------:|:-------:|
| 01 | ✅ | ✅ | ✅ | ✅ | ⏳ | ⏳ |
| 02 | ✅ | ✅ | ✅ | ✅ | ⏳ | ⏳ |
| 03 | ✅ | ✅ | ✅ | ✅ | ⏳ | ⏳ |
| 04 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 05 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 06 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |

---

*При расхождении между файлами приоритет: этот алгоритм (§3.1 SYNC, §0–§4) → `ONBOARDING_FIGMA_PAGE_QA_ALGORITHM.md` → журнал страницы.*
