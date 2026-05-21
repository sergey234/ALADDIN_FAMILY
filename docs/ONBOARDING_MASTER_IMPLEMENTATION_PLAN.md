# ALADDIN Onboarding — мастер-план реализации (для ML / команды)

**Назначение:** единый документ, по которому **любая ML-система** (Cursor, другой агент) понимает **что делать, в каком порядке, откуда брать эталоны** и когда страница считается готовой. Синхронизирован с TODO в Cursor и чеклистами в `docs/`.

**Краткий смысл проекта:** героев рисуем AI → экраны согласуем в Figma → онбординг уже в SwiftUI — подставляем 9 ассетов и полируем. Figma не заменяет ни генерацию, ни код, но убирает хаос с отступами.

**Текущая оценка готовности (~май 2026):** ~**70–75%** Фаза B (Figma **8/8** OB + экспорт в репо); Фаза C **не начата** (~1/9 imageset). Следующий шаг: **канон hero OB_07 = v4B** в Figma + **MAIN** → 【batch】Xcode + симулятор.

**Передача другой ML:** читать **§0** (карта файлов) → **§7** (статус) → **§7.4** (handoff) → TODO id из **§9**.

---

## 0. Карта всех документов (не искать вручную)

| Документ | Путь | Роль |
|----------|------|------|
| **Этот план** | `docs/ONBOARDING_MASTER_IMPLEMENTATION_PLAN.md` | Порядок работ, TODO ↔ шаги, ссылки |
| Handoff (канон правил) | `docs/ONBOARDING_MAIN_HERO_HANDOFF.md` | Сюжет, слои, §1.8, фазы A→B→C, Main |
| Чеклист фреймов Figma | `docs/ONBOARDING_FIGMA_FRAME_CHECKLIST.md` | Имена OB_00…07, слои, OB_00 — 100% |
| **QA после каждой страницы** | `docs/ONBOARDING_FIGMA_PAGE_QA_ALGORITHM.md` | Алгоритм сверки §A–J |
| **STOP-шлюз G1–G10** | **этот файл §4.1** | Перед закрытием `ob-0N-qa`; герой + **§E-IMG** в `ONBOARDING_FIGMA_PAGE_QA_ALGORITHM.md` |
| Фаза A (закрытие) | `docs/ONBOARDING_PHASE_A_COMPLETION.md` | URL, продукт §1–2, a11y, WCAG §4 |
| Девять экранов (индексы) | `docs/ONBOARDING_NINE_SCREENS_REFERENCE.md` | currentPage, ключи локализации, ассеты |
| WCAG числа | `docs/ONBOARDING_WCAG_MEASUREMENTS.md` | hex, контраст X:1 |
| Pipeline героев | `docs/ALADDIN_Hero_Asset_Pipeline.md` | 7 шагов на каждый PNG |
| Промпты AI | `docs/ALADDIN_Onboarding_Prompts.md` | Промпты 0…7 + Main, Tier |
| Character Bible | `docs/ALADDIN_Character_Bible.md` | Стиль персонажей |
| Шаг 0 (снимок кода) | `docs/ONBOARDING_STEP0_LANGUAGE_SNAPSHOT.md` | languageStepView |
| Figma URL / fileKey | `docs/FIGMA_ONBOARDING.env` | `KvkUdyb5Ll31Z9FSzCbpNl` |
| Как взять ссылку Figma | `docs/FIGMA_LINK_INSTRUCTIONS.md` | |
| Правило MCP Figma | `.cursor/rules/figma-mcp-onboarding-main.mdc` | figma-use перед use_figma |
| Код онбординга | `Screens/14_OnboardingScreen.swift` | **Эталон UI и текстов** |
| Код Main | `Screens/01_MainScreen.swift` | Main + герой |
| Слоты героев | `Shared/Components/HeroAmbientPresentation.swift` | `OnboardingHero_00`…`07`, `MainHero_ambient` |
| Отступы | `Shared/Styles/Spacing.swift` | screenPadding, m, l, xl |
| Цвета | `Shared/Styles/Colors.swift` | primaryBlue #2E5BFF |
| Локализация RU/EN | `Core/Localization/LocalizationManager.swift` | `onboarding_page*_title/desc` |
| Мастер PNG (исходники) | `Resources/HeroAssets/OnboardingHero_00.png` … | |
| Asset Catalog | `Assets.xcassets/OnboardingHero_00.imageset/` … | |
| AGENTS (кратко) | `AGENTS.md` | §1.8 для агентов |
| Архив Figma PNG | `docs/ONBOARDING_FIGMA_EXPORT_ARCHIVE_20260519.md` | OB_00…07 full + nodeId |
| OB_07 концепты | `docs/ONBOARDING_OB_07_CONCEPTS.md` | v4B канон; логотип вне Figma |
| Логотип page7 (PNG) | `Resources/FigmaExports/Logo_OnboardingPage7/` | @1x/@2x/@3x; **не в макете Figma** |

**Figma:** открывать через `Open-Figma-Safe.command` (не ломать OCLP Kepler). Перед `use_figma` — skill **figma-use**.

---

## 1. Три слоя (не смешивать)

| Слой | Инструмент | Результат |
|------|------------|-----------|
| 1 | AI (промпты) | 9 PNG: `OnboardingHero_00`…`07`, `MainHero_ambient` |
| 2 | Figma | 8×393×852 + 2 Main; WCAG; имена экспорта |
| 3 | Xcode (готов) | imageset + Visual QA; **не ломать §1.8** |

---

## 2. Порядок работы (глобально)

```text
Фаза A (доки, числа) ──► почти готово, §1–2 опционально параллельно
        │
        ▼
Фаза B: по ОДНОЙ странице OB_00 → OB_07 → MAIN
        │   каждая: Figma → QA-алгоритм (тексты, отступы, chrome)
        │   Hero PNG в Figma — плейсхолдер/арт по мере готовности
        ▼
Фаза C (в КОНЦЕ, одним блоком): все imageset + симулятор 0…7 + Main + §E
```

**Решение команды (2026-05-19):** Xcode не после каждой страницы, а **после всех макетов Figma**.

**Жёсткое правило:** не начинать `OB_(N+1)`, пока `OB_N` не имеет **PASS** по `ONBOARDING_FIGMA_PAGE_QA_ALGORITHM.md` (§I карточка приёмки).

---

## 3. Сквозные задачи 【План】 (8 пунктов)

Эти пункты **остаются в TODO** на весь проект; закрываются, когда выполнены все дочерние страницы.

### 【План】1 — `plan-phase-a` — Фаза A: продукт §1–2

| Что сделать | Где | Критерий готово |
|-------------|-----|-----------------|
| §0 URL Figma | `FIGMA_ONBOARDING.env`, `ONBOARDING_PHASE_A_COMPLETION.md` §0 | ✅ уже есть `KvkUdyb5Ll31Z9FSzCbpNl` |
| Подписать сюжет §1–2 | `ONBOARDING_PHASE_A_COMPLETION.md` §1–2 | Галочки «Утверждено» по 8 сценам + персонаж §5.B |
| Минимум для Figma B | только §0 | Уже можно |

**Источники сюжета:** `ONBOARDING_MAIN_HERO_HANDOFF.md` §4, §5.B.

---

### 【План】2 — `plan-phase-b` — Фаза B: 10 фреймов Figma

| Фрейм | Имя в Figma | Экспорт Xcode |
|-------|-------------|---------------|
| 0 | `OB_00_Language_393x852` | `OnboardingHero_00` |
| 1 | `OB_01_Family_393x852` | `OnboardingHero_01` |
| 2 | `OB_02_AI_393x852` | `OnboardingHero_02` |
| 3 | `OB_03_Parents_393x852` | `OnboardingHero_03` |
| 4 | `OB_04_Radar_393x852` | `OnboardingHero_04` |
| 5 | `OB_05_Kids_393x852` | `OnboardingHero_05` |
| 6 | `OB_06_Adults23_393x852` | `OnboardingHero_06` |
| 7 | `OB_07_Invite_393x852` | `OnboardingHero_07` |
| — | `MAIN_Hero_MainHero_ambient` | `MainHero_ambient` |
| — | `MAIN_FullScreen_393x852` | полный UI Main |

**Чеклист слоёв:** `ONBOARDING_FIGMA_FRAME_CHECKLIST.md`.  
**Зоны:** hero ~60%, контент ~40%, chrome ~160–200 pt снизу — `ONBOARDING_MAIN_HERO_HANDOFF.md` §1.4.  
**Готово план B:** все 10 фреймов + каждый прошёл QA-алгоритм.

---

### 【План】3 — `plan-pipeline-heroes` — Pipeline 9 PNG

**Алгоритм на каждый кадр:** `ALADDIN_Hero_Asset_Pipeline.md` (7 шагов).

1. Story → 2. Prompt (`ALADDIN_Onboarding_Prompts.md`) → 3. AI 8–12 вариантов → 4. Имя канон → 5. `Resources/HeroAssets/` → 6. `Assets.xcassets/*.imageset` → 7. Visual QA.

**Tier:** 0,1,4 — Tier 1; 2,3,6 — Tier 2 (опц. Lottie); 5,7,Main — Tier 3.

**Имена:** только `OnboardingHero_00`…`07`, `MainHero_ambient` — см. `HeroAmbientPresentation.swift`.

---

### 【План】4 — `plan-phase-c-xcode` — Фаза C: imageset

| Действие | Файлы |
|----------|--------|
| 9 imageset | `Assets.xcassets/OnboardingHero_00.imageset/` … `MainHero_ambient.imageset/` |
| Contents.json | @2x + @3x где возможно (сейчас 00 может быть только 3x — довести в §E) |
| Код | **Не менять** `languageStepView` / `onboardingPage` padding без ТЗ — §1.8 |

**Эталон интеграции 00:** `ALADDIN_Hero_Asset_Pipeline.md` §2.

---

### 【План】5 — `plan-wcag-table` — WCAG §4

Заполнить таблицу в `ONBOARDING_PHASE_A_COMPLETION.md` §4 для каждого `OB_*` и `MAIN_FullScreen`.  
Числа: `ONBOARDING_WCAG_MEASUREMENTS.md`. Минимум **4.5:1** для описания.

---

### 【План】6 — `plan-phase-c-full-qa` — Полный Visual QA

| Проверка | Где |
|----------|-----|
| `currentPage` 0…7 | Симулятор |
| Main | `01_MainScreen.swift` |
| SE / XR | Узкий / стандартный экран |
| Длинные локали | Особенно page 6, 7 |
| RTL | Smoke |
| Reduce Motion | Нет бесконечного пульса где запрещено |

**Handoff §8** — расширенный чеклист приёмки.

---

### 【План】7 — `plan-qa-e` — Приёмка §E

| Пункт | Действие |
|-------|----------|
| Слайд 0 | Намёк единорога не слишком явный (иначе v2 промпт) |
| Debug | Логи выключены при съёмке/приёмке |
| Вес PNG | @2x/@3x, не один гигантский PNG на все scale |

---

### 【План】0 (meta) — `qa-algorithm-doc` — Канон QA

✅ Документ: `ONBOARDING_FIGMA_PAGE_QA_ALGORITHM.md` — **обязателен после каждой правки Figma.**

---

## 4. Цикл на одну страницу (OB_00 … OB_07) — порядок TODO

```text
figma-ob-0N  →  hero-0N-figma  →  ob-0N-qa (§4.1 G1–G10 + §E-IMG + полный QA)  →  [Xcode batch]
```

| Шаг | TODO id | Что делать |
|-----|---------|------------|
| 1 | `figma-ob-0N` | Фрейм 393×852, слои, `CHROME_bottom` |
| 2 | `hero-0N-figma` | AI PNG → `HeroAssets/` → upload в Figma `OnboardingHero_0N` |
| 3 | `ob-0N-qa` | **§4.1 G1–G10** (обязательно) + `ONBOARDING_FIGMA_PAGE_QA_ALGORITHM.md` §A–F + **§E-IMG** |
| 4 | `hero-0N-xcode`, `ob-0N-simulator` | **【Xcode batch】** в конце проекта |

**Запрещено** закрывать `ob-0N-qa`, если не пройден **§4.1** (иллюстрация героя на скрине).

**Chrome в Figma:** `CHROME_bottom` — точки (активная = `currentPage`) + кнопка ≈361×50. Не текст-подсказка на холсте.

---

### §4.1 STOP-шлюз QA (G1–G10) — перед закрытием `ob-0N-qa`

**Зачем:** не ставить «Figma + QA ✅» с синей заглушкой (OB_01) или неверным масштабом (OB_02: FILL/FIT).

**Когда:** после `hero-0N-figma`, до `ob-0N-qa` = completed и до `figma-ob-(N+1)`.

**Полный блок растра:** `ONBOARDING_FIGMA_PAGE_QA_ALGORITHM.md` **§E-IMG** (якоря, crop, два скрина).

| # | Проверка | Как | ☐ |
|---|----------|-----|---|
| **G1** | `get_screenshot` узла **`OnboardingHero_0N`** | MCP Figma | |
| **G2** | На скрине **иллюстрация**, не SOLID-заглушка | описание скрина | |
| **G3** | Сюжет = **§5 этого плана** (OB_0N), затем `ALADDIN_Onboarding_Prompts.md` | сверить канон | |
| **G4** | `Resources/HeroAssets/OnboardingHero_0N.png` в репо | `ls` | |
| **G5** | Тексты RU = `LocalizationManager` **и** fallback Swift | `grep` | |
| **G6** | `CHROME_bottom`: точки + кнопка **~361×50** | `get_metadata` | |
| **G7** | `OnboardingHero_0N_figma_zone_361x460.png` в репо | `ls` | |
| **G8** | §E-IMG4–5: масштаб ~75–90% зоны; якоря слайда N | скрин героя | |
| **G9** | `get_screenshot` **всего фрейма** OB_NN | MCP Figma | |
| **G10** | Колонка **«Продукт»** §J — подтверждение масштаба/сюжета | человек | |

**Симулятор:** отдельно **§SIM** в QA-алгоритме (не путать с G1–G10).

**Main:** `MainHero_ambient`, без «Продолжить».

**Запрещено:** SOLID-заливка; FIT без pre-compose при «далеком» герое; «100%» без G1–G2, G7–G9; копировать hero_00 на другие N.

**Карточка в отчёт:**

```text
OB_0N — шлюз §4.1
G1–G2 герой: PASS/FAIL (nodeId: ___)
G3–G10 + §E-IMG: PASS/FAIL
Продукт OK: ☐
→ ob-0N-qa: closed только если все PASS
```

---

## 5. Детализация по страницам (TODO ↔ контент)

### OB_00 — Язык (`figma-ob-00` ✅, `ob-00-qa`, `hero-00-xcode` ✅)

| Поле | Значение |
|------|----------|
| Figma node (пример) | `7:65` — `OB_00_Language_393x852` |
| `currentPage` | 0 |
| Hero | `OnboardingHero_00` |
| Тексты RU | `languageStepTitle` → «Язык приложения»; кнопка → «Продолжить»; RU/English в списке |
| Особенности | 🌐 56pt; ROW RU/EN; hero — фон, не двигает padding |
| Сюжет | Лампа + намёк рога; Tier 1 |
| QA | `ONBOARDING_FIGMA_PAGE_QA_ALGORITHM.md` §C1; таблица §J |

---

### OB_01 — Семья (`figma-ob-01` … `ob-01-simulator`)

| Поле | Значение |
|------|----------|
| `currentPage` / `contentIndex` | 1 / 0 |
| Hero | `OnboardingHero_01` |
| Ключи | `onboarding_page1_title`, `onboarding_page1_desc` |
| RU title (fallback в Swift) | «Защита всей семьи в кармане» |
| Цвет акцента | `Color.primaryBlue` |
| Особенности UI | `OnboardingAladdinLogoView` сверху в коде |
| Промпт | `ALADDIN_Onboarding_Prompts.md` — Слайд 1, Tier 1 |

---

### OB_02 — ИИ (`figma-ob-02` …)

| Поле | Значение |
|------|----------|
| Figma | `103:53` / hero `103:54` |
| `currentPage` / `contentIndex` | 2 / 1 |
| Hero | `OnboardingHero_02` |
| Ключи | `onboarding_page2_*` |
| Цвет | `Color.successGreen` |
| **Канон визуала** | Дух **«Пробуждение»** — полуформенный из золотых частиц; tech-лампа; **без** единорога и **без** человека |
| Zone | `OnboardingHero_02_figma_zone_361x460.png` (pre-compose, ~crop_w 1050, height_frac ~0.86) |
| QA | §E-IMG + G1–G10 |

---

### OB_03 — Родители

| Поле | Значение |
|------|----------|
| Figma | `108:53` / hero `108:54` |
| `currentPage` / `contentIndex` | 3 / 2 |
| Hero | `OnboardingHero_03` |
| Ключи | `onboarding_page3_*` |
| Цвет | `Color.orange` |
| **Канон визуала** | Дух **«Страж ALADDIN»** — высокий, спокойная улыбка, индиго→бирюза, звёзды/лампа на теле, tech-лампа; **без** единорога и человека |
| QA | §E-IMG + G1–G10 |

---

### OB_04 — Радар

| Поле | Значение |
|------|----------|
| `currentPage` / `contentIndex` | 4 / 3 |
| Hero | `OnboardingHero_04` |
| Ключи | `onboarding_page4_*` |
| Цвет | `Color.red` |
| Особенности | Один «ping» при входе (код/UI) |
| **Канон визуала** | **Космос + звёзды:** дуга сканирования + ping (концепт **A**) |
| PNG | ✅ — `ONBOARDING_HERO_04_05_06_COSMIC_ASSIGNMENT.md` |

---

### OB_05 — Дети

| Поле | Значение |
|------|----------|
| `currentPage` / `contentIndex` | 5 / 4 |
| Hero | `OnboardingHero_05` |
| Ключи | `onboarding_page5_*` |
| Цвет | `Color.purple` |
| **Канон визуала** | **Космос + звёзды:** щит, угроза отражена (концепт **B**) |
| PNG | ✅ |

---

### OB_06 — 23+

| Поле | Значение |
|------|----------|
| `currentPage` / `contentIndex` | 6 / 5 |
| Hero | `OnboardingHero_06` |
| Ключи | `onboarding_page6_*` |
| Цвет | `Color.blue` |
| Особенности | Длинное описание — заложить в макете |
| **Канон визуала** | **Космос + звёзды:** лента предсказания (концепт **C**) |
| PNG | ✅ |

---

### OB_07 — Приглашение

| Поле | Значение |
|------|----------|
| `currentPage` / `contentIndex` | 7 / 6 |
| Hero | `OnboardingHero_07` — **канон v4B** «джин из куба», без круга/семьи в PNG |
| Figma | `122:53` / `122:54` |
| Ключи | `onboarding_page7_*` |
| Цвет | `Color.green` |
| Варианты hero | `variants/OB07_v4/` (A,B,C); архив C v2 в `variants/` |
| Особенности | `ScrollView` + иконка 140 pt в **коде**; chrome: согласия + «Код»/«Восстановить» |
| Кнопка chrome | **«Начать»** (`onboarding_start`) |
| **Логотип круг** | PNG: `Logo_OnboardingPage7/` — **убран с всех фреймов Figma** (нет места) |
| PNG / QA | Figma ⚠️ · hero v4B → залить на `122:54` · Продукт ☐ |

---

### MAIN (`figma-main-hero`, `main-qa`, `hero-main`, `main-simulator`)

| Поле | Значение |
|------|----------|
| Фреймы | `MAIN_Hero_MainHero_ambient`, `MAIN_FullScreen_393x852` |
| Hero | `MainHero_ambient`, слот `.mainDashboard` |
| Код | `01_MainScreen.swift`, `HeroAmbientPresentation.swift` |
| Спека героя | `ONBOARDING_MAIN_HERO_HANDOFF.md` §6 (opacity, anchor, idle, Reduce Motion) |
| Промпт | Main в `ALADDIN_Onboarding_Prompts.md`, Tier 3 |

---

## 6. Инструкция для ML-агента (пошагово)

### Старт сессии

1. Прочитать **этот файл** и `ONBOARDING_FIGMA_PAGE_QA_ALGORITHM.md`.
2. Загрузить `docs/FIGMA_ONBOARDING.env` → `FIGMA_FILE_KEY`.
3. Узнать текущую страницу из TODO (первая `pending` в порядке 00→07→MAIN).
4. **Не** перескакивать страницы.

### На странице N

```
1. figma-ob-0N
   - skill figma-use → use_figma / upload_assets
   - Чеклист: ONBOARDING_FIGMA_FRAME_CHECKLIST.md (строка OB_0N)
   - CHROME_bottom обязателен

2. ob-0N-qa
   - get_metadata + get_screenshot (fileKey, nodeId фрейма)
   - grep ключи локализации → сравнить тексты
   - Пройти §B–G QA-алгоритма; use_figma для исправлений
   - PASS → карточка §I

3. hero-0N
   - Промпт из ALADDIN_Onboarding_Prompts.md
   - 8–12 вариантов → лучший → HeroAssets/ → imageset
   - ALADDIN_Hero_Asset_Pipeline.md

4. ob-0N-simulator
   - Xcode: currentPage == N
   - Сверка с Figma; §1.8 — отступы как до арта

5. Отметить в ONBOARDING_FIGMA_PAGE_QA_ALGORITHM.md §J галочку OB_0N
```

### Команды пользователя

| Команда | Действие агента |
|---------|-----------------|
| «делай OB_01» | figma-ob-01 → ob-01-qa → … |
| «генерируй OnboardingHero_01» | только hero-01-ai + hero-01-xcode |
| «QA OB_00» | только ob-00-qa |
| «делай Фазу B» | все figma-ob-* по порядку с QA |

---

## 7. Таблица статуса (обновлять агентом/человеком)

| TODO / Страница | Figma | QA алгоритм | Hero PNG | imageset | Simulator | Принято |
|-----------------|:-----:|:-----------:|:--------:|:--------:|:---------:|:-------:|
| OB_00 | ✅ | ☐ | ✅ | ✅ | ☐ | ☐ |
| OB_01 | ✅ | ✅ | ✅ | ☐ | ☐ | ☐ |
| OB_02 | ✅ | ✅ | ✅ | ☐ | ☐ | ☐ |
| OB_03 | ✅ | ⚠️ | ✅ | ☐ | ☐ | ☐ |
| OB_04 | ✅ | ⚠️ | ✅ | ☐ | ☐ | ☐ |
| OB_05 | ✅ | ⚠️ | ✅ | ☐ | ☐ | ☐ |
| OB_06 | ✅ | ⚠️ | ✅ | ☐ | ☐ | ☐ |
| OB_07 | ✅ | ⚠️ | ⚠️ v4B в variants, Figma ждёт upload | ☐ | ☐ | ☐ |
| MAIN | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |

**Легенда QA:** ✅ = §4.1 G1–G10 + §E-IMG (агент, см. `ONBOARDING_OB_04_05_06_FIGMA_QA.md` и др.) · ⚠️ = Figma/PNG есть, **«Продукт OK»** или формальный `ob-0N-qa` не закрыт · ☐ = не сделано.

**Figma nodeId (04–07):** `117:53` / `117:70` / `117:87` / `122:53` — см. `ONBOARDING_HERO_04_05_06_COSMIC_ASSIGNMENT.md`, `ONBOARDING_OB_07_FIGMA_QA.md`.

**【План】сквозные:**

| ID | Статус |
|----|--------|
| plan-phase-a | ☐ §1–2 |
| plan-phase-b | ⚠️ **8/10** фреймов (OB_00…07 ✅; осталось MAIN×2) |
| plan-pipeline-heroes | ⚠️ **8/9** PNG (`OnboardingHero_00`…`07` ✅; нет `MainHero_ambient`) |
| plan-phase-c-xcode | ☐ **1/9** imageset (только `OnboardingHero_00`) |
| plan-wcag-table | ☐ |
| plan-phase-c-full-qa | ☐ 【batch】 |
| plan-qa-e | ☐ |
| qa-algorithm-doc | ✅ (+ §E-IMG) |

---

## 7.1 Что сделано (май 2026, актуально)

| Сделано | Детали |
|---------|--------|
| Мастер-план + QA | этот файл, `ONBOARDING_FIGMA_PAGE_QA_ALGORITHM.md` §E-IMG |
| Figma OB_00…07 | 8 фреймов, chrome, тексты RU, OB_07: согласия + 2 кнопки |
| Экспорт Figma | `FigmaExports/OB_00`…`OB_07/*_full.png` + `ONBOARDING_FIGMA_EXPORT_ARCHIVE_20260519.md` |
| PNG героев 00–06 | `HeroAssets/` + zones; космос 04–06 |
| OB_07 hero | v4A/B/C «джин из куба» в `variants/OB07_v4/`; продукт выбрал **v4B** |
| OB_07 Figma | `122:53`; hero на макете ещё **старый C v2** — заменить на v4B |
| Логотип page7 | `onboarding_page7_icon.png` + `Logo_OnboardingPage7/`; **с онбординга Figma снят** |
| OB_01 | B1 + `BLOCK_aladdin_logo` V2 |
| Downloads | `~/Downloads/ALADDIN_Figma_Onboarding_20260519.zip` |

## 7.2 Что осталось (~40–45% работы)

| Приоритет | TODO id | Задача |
|-----------|---------|--------|
| 1 | `hero-07-figma` | Залить **v4B** → `OnboardingHero_07.png`, zone, Figma `122:54` |
| 2 | `ob-07-qa` | §4.1 + Продукт OK OB_07 (hero v4B) |
| 3 | `figma-main-hero` | `MAIN_Hero` + `MAIN_FullScreen` |
| 4 | `hero-main` | AI `MainHero_ambient` |
| 5 | `main-qa` | QA Main |
| 6 | — | Продукт OK OB_03…06 (формально ⚠️) |
| 7 | `plan-phase-c-xcode` | imageset 01…07 + Main (**batch**) |
| 8 | `plan-phase-c-full-qa` | симулятор 0…7 + Main (**batch**) |
| 9 | `plan-phase-a` | §1–2 утверждение |
| 10 | `plan-wcag-table`, `plan-qa-e` | WCAG + §E |
| — | *(отложено)* | Логотип 140 pt в Figma/онбординге — нет места; PNG готов в `Logo_OnboardingPage7/` |

## 7.3 Что дальше (порядок для агента)

```text
1. hero-07-figma: v4B → HeroAssets/OnboardingHero_07.png + zone → upload 122:54
2. ob-07-qa + Продукт OK
3. figma-main-hero → hero-main → main-qa
4. Продукт OK OB_03…07 (по желанию 00–02)
5. 【batch】plan-phase-c-xcode (imageset 01…07 + Main)
6. 【batch】plan-phase-c-full-qa
7. plan-wcag-table + plan-qa-e + plan-phase-a
```

## 7.5 Фаза C: Figma → Xcode (что да / что нет)

**Аналогия:** Figma = обои; приложение = мебель и надписи (код); batch = наклеить обои в нужном размере, **не** передвигая мебель.

| Переносим в Xcode | Не переносим из Figma |
|-------------------|------------------------|
| PNG героев → `Assets.xcassets/OnboardingHero_0N.imageset/` | Тексты TITLE/DESC/кнопки |
| Имена канон: `OnboardingHero_00`…`07`, `MainHero_ambient` | Chrome (точки, «Продолжить») |
| Мастер: `Resources/HeroAssets/OnboardingHero_0N.png` | Целый фрейм `*_full.png` в imageset |
| Эталон кадра: zone `*_figma_zone_361x460.png` → imageset **393×852** | Логотип 140 pt (отложено) |

**Градиент в приложении остаётся:** `LinearGradient.backgroundGradient` + `HeroBottomReadableGradient` поверх героя (`14_OnboardingScreen.swift`) — batch **не** убирает градиент; герой — отдельный слой под ним.

**Полные страницы (эталон Figma, 393×852):** `docs/backup/ONBOARDING_FULL_PAGES_20260519/pages_393x852/` и `~/Downloads/ALADDIN_Onboarding_FullPages_20260519/`.  
**Технический снимок перед batch:** `docs/backup/onboarding_pre_xcode_batch_20260519/` (откат HeroAssets + imageset 00).

**Порядок:** (1) HeroAssets + FigmaExports готовы → (2) `plan-phase-c-xcode` imageset 00…07 + Main → (3) `plan-phase-c-full-qa` симулятор vs `FigmaExports/OB_0N/` → (4) иконка page7 в код (по решению продукта) → (5) WCAG + §E.

**Pixel-perfect как Figma full frame — не цель** текущего scope (в коде эмодзи-круги на 1–6, `ScrollView` на 7; см. handoff §1.8).

---

## 7.4 Handoff для другой ML-системы (старт за 5 минут)

1. **План:** `docs/ONBOARDING_MASTER_IMPLEMENTATION_PLAN.md` (этот файл) — §7 таблица статуса.
2. **Figma:** `docs/FIGMA_ONBOARDING.env` → fileKey `KvkUdyb5Ll31Z9FSzCbpNl`; skill **figma-use** перед `use_figma`.
3. **QA каждой страницы:** `docs/ONBOARDING_FIGMA_PAGE_QA_ALGORITHM.md` + §4.1 G1–G10 здесь.
4. **Экспорты:** `Resources/FigmaExports/OB_00`…`OB_07/`.
5. **Герои:** `Resources/HeroAssets/OnboardingHero_*.png`.
6. **Логотип page7 (не в Figma):** `Resources/FigmaExports/Logo_OnboardingPage7/`.
7. **Код-эталон UI:** `Screens/14_OnboardingScreen.swift`.
8. **TODO Cursor:** id = `figma-ob-0N`, `hero-0N-figma`, `ob-0N-qa`, `plan-phase-*` (§9).
9. **Не делать:** Xcode imageset до команды «batch»; логотип в круг на макеты OB (нет места).
10. **Открыть Figma OB_07:** `figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=122-53`

---

## 8. Что не делать

- Не менять OCLP / NVIDIA Kepler.
- Не класть сюжетный текст в PNG героя.
- Не заменять Figma только AI-полноэкранами.
- Не делать `OnboardingHero_Minimal_*`.
- Не переходить к N+1 без QA PASS на N.
- Не использовать служебные надписи `NOTE_chrome` на видимом холсте — только `CHROME_bottom`.

---

## 9. Связь с Cursor TODO

Идентификаторы задач в Cursor **совпадают** с колонками этого плана (`plan-phase-a`, `figma-ob-01`, `ob-01-qa`, …). При добавлении задач в TODO — дублировать формулировки из §3–5.

---

*Обновлять при смене имён ассетов, fileKey Figma или структуры TODO. Первичная версия: май 2026.*
