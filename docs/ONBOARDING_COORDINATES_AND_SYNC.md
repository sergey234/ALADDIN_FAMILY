# Онбординг OB_00–OB_07: координаты Figma ↔ iOS и статус синхронизации

**Дата снимка:** 2026-05-23  
**Сборка:** `AppConfig.buildNumber` = **203**  
**Код (источник правды для Y):** `Screens/14_OnboardingScreen.swift` → `OnboardingFigmaAnchor`, `scrimGradientStops(for:)`, `onboardingPage`  
**Figma file:** `KvkUdyb5Ll31Z9FSzCbpNl` · страница **`OnboardingHero_00`**

---

## 1. Как читать координаты

| Поле | Значение |
|------|----------|
| **Canvas** | 393×852 pt (iPhone 14 Pro logical) |
| **Screen Y** | От верха фрейма 852 (как в Figma) |
| **contentIndex** | Индекс в `pages[]`: 0 = OB_01 … 5 = OB_06 |
| **currentPage (TabView)** | 0 = язык OB_00, 1…6 = OB_01…OB_06, 7 = OB_07 |
| **Layout в iOS** | `OnboardingFigmaAnchoredContent` — фиксированные `CGRect`, не `Spacer` + нижняя панель |

**Масштаб в TabView:** `OnboardingFigmaScreenLayout` — `skipBandHeight=52`, `chromeBandHeight=154`, `tabDesignHeight=646`.

---

## 2. Что добавлено в код (OB_01–OB_06)

Все контент-страницы **01–06** используют **`OnboardingFigmaAnchor`** (cases **0…5**).  
В `onboardingPage` ветка **`figmaAnchor` идёт раньше** `OnboardingBottomTextPanel` — нижняя панель для 0…5 **не используется**.

| OB | RU-заголовок (ключ) | `contentIndex` | `case` | Заголовок Y | Описание Y | Scrim (y × h) | opacity | `maxBodyLines` |
|----|---------------------|----------------|--------|-------------|------------|---------------|---------|----------------|
| **01** | Защита всей семьи… | 0 | 0 | **536** | **615** | **528×324** | 0.45 | 4 |
| **02** | Персональный агент… | 1 | 1 | **479** | **552** | **552×300** | 0.42 | 6 |
| **03** | Родительский контроль | 2 | 2 | **552** | **630** | **500×320** | 0.40 | 5 |
| **04** | Аналитика рисков | 3 | 3 | **496** | **566** | **542×310** | 0.35 | 5 |
| **05** | Защита для детей! | 4 | 4 | **496** | **566** | **532×320** | 0.38 | 6 |
| **06** | Защита для людей 23+ | 5 | 5 | **496** | **566** | **552×300** | 0.40 | 5 |
| **07** | Присоединяйтесь к ALADDIN | 6 | 6 | **482** | **520** | **480×372** | 0.42 | 4 |
| **07** wordmark | — | 6 | — | **374** (h **104**) | — | — | — | — |

---

## 3. Полная таблица координат (Figma = iOS)

### OB_01 — `case 0` · frame `OB_01_Family` · `81:53`

| Слой | x | y | w | h |
|------|---|---|---|---|
| Wordmark | 10 | **354** | 360 | 121 |
| Title | 16 | **536** | 361 | 50 |
| Desc | 16 | **615** | 346 | 48 |
| Scrim | 0 | **528** | 393 | 324 |

**Scrim gradient:** mid **0.2025 @ 0.45**, max **0.45**  
**Hero asset:** `OnboardingHero_01` · Figma hero `81:54`

---

### OB_02 — `case 1` · `OB_02_AI` · `103:53`

| Слой | x | y | w | h |
|------|---|---|---|---|
| Title | 10 | **479** | 361 | 60 |
| Desc | 7 | **552** | 364 | 79 |
| Scrim | 0 | **552** | 393 | 300 |

**Scrim gradient:** mid **0.189 @ 0.45**, max **0.42**  
**Hero:** `OnboardingHero_02` · `103:54` · zone94

---

### OB_03 — `case 2` · `OB_03_Parents` · `108:53`

| Слой | x | y | w | h |
|------|---|---|---|---|
| Title | 16 | **552** | 361 | 60 |
| Desc | 14 | **630** | 361 | 80 |
| Scrim | 0 | **500** | 393 | 320 |

**Scrim gradient:** mid **0.16 @ 0.4**, max **0.40**  
**Hero:** `OnboardingHero_03` · `108:54` · zone94

---

### OB_04 — `case 3` · `OB_04_Radar` · `117:53`

| Слой | x | y | w | h |
|------|---|---|---|---|
| Title | 16 | **496** | 361 | 60 |
| Desc | 16 | **566** | 361 | 100 |
| Scrim | 0 | **542** | 393 | 310 |

**Scrim gradient:** mid **0.1575 @ 0.45**, max **0.35**  
**Hero:** `OnboardingHero_04` · `117:54`

---

### OB_05 — `case 4` · `OB_05_Kids` · `117:70`

| Слой | x | y | w | h |
|------|---|---|---|---|
| Title | 16 | **496** | 361 | 60 |
| Desc | 16 | **566** | 361 | 100 |
| Scrim | 0 | **532** | 393 | 320 |

**Scrim gradient:** mid **0.171 @ 0.45**, max **0.38**  
**Hero:** `OnboardingHero_05` · `117:71` · Figma scrim `217:57`

---

### OB_06 — `case 5` · `OB_06_Adults23` · `117:87`

| Слой | x | y | w | h |
|------|---|---|---|---|
| Title | 16 | **496** | 361 | 60 |
| Desc | 16 | **566** | 361 | 100 |
| Scrim | 0 | **552** | 393 | 300 |

**Scrim gradient:** mid **0.18 @ 0.45**, max **0.40**  
**Hero:** `OnboardingHero_06` · `117:88` · Figma scrim `217:58`

---

### OB_00 — язык (вне `OnboardingFigmaAnchor`)

| Поле | Значение |
|------|----------|
| `currentPage` | **0** |
| UI | `languageStepView()` — выбор RU/EN, не anchor-layout |
| Hero | `OnboardingHero_00` · frame `7:65` |
| Статус | ✅ отдельный трек |

---

### OB_07 — приглашение (`case 6`, layout `ob07Final`)

| Слой | x | y | w | h |
|------|---|---|---|---|
| Hero | 16 | **24** | 361 | 460 |
| WORDMARK | 7 | **374** | 361 | **104** |
| Title | 12 | **470** | 361 | 60 |
| Desc | 12 | **508** | 361 | 80 |
| Scrim | 0 | **480** | 393 | 372 |

**Legal (chrome, `OnboardingOB07LegalBlock`):** 4 строки @ x=16, max width 361 — info+политика → чекбокс данных → ссылка соглашения → чекбокс соглашения.

| Поле | Значение |
|------|----------|
| `contentIndex` | **6** |
| `currentPage` | **7** |
| UI | `OnboardingFigmaAnchoredContent` + `OnboardingOB07LegalBlock` |
| Hero | `OnboardingHero_07` · `122:53` |
| Статус | ✅ SYNC-I ⏳ SYNC-D |

---

## 4. Scrim gradient stops (`scrimGradientStops`)

Ключ: `(scrim.origin.y, scrimMaxOpacity)` → mid stop → max stop @ 1.0

| OB | scrim Y | max α | mid location | mid α |
|----|---------|-------|--------------|-------|
| 01 | 528 | 0.45 | 0.45 | 0.2025 |
| 02 | 552 | 0.42 | 0.45 | 0.189 |
| 03 | 500 | 0.40 | 0.40 | 0.16 |
| 04 | 542 | 0.35 | 0.45 | 0.1575 |
| 05 | 532 | 0.38 | 0.45 | 0.171 |
| 06 | 552 | 0.40 | 0.45 | 0.18 |

*Примечание:* OB_02 и OB_06 оба имеют scrim Y=552, но разный `scrimMaxOpacity` (0.42 vs 0.40) — в `switch` разные ветки.

---

## 5. Подтверждение синхронизации по страницам (2026-05-23)

Легенда: **SYNC-I** = координаты в Swift = таблица §3 · **SYNC-L** = layout path = `OnboardingFigmaAnchoredContent` · **SYNC-B** = сборка включает изменения

| OB | SYNC-I (код = эталон) | SYNC-L (не bottom panel) | Hero imageset | Figma frame | SYNC-B build 202 | SYNC-D визуал |
|----|----------------------|---------------------------|---------------|-------------|------------------|---------------|
| **00** | n/a (язык) | n/a | ✅ `OnboardingHero_00` | ✅ `7:65` | ✅ | ✅ принято |
| **01** | ✅ case 0 | ✅ | ✅ | ✅ `81:53` | ✅ | ✅ принято |
| **02** | ✅ case 1 | ✅ | ✅ zone94 | ✅ `103:53` | ✅ | ✅ принято |
| **03** | ✅ case 2 | ✅ | ✅ zone94 | ✅ `108:53` | ✅ | ✅ H,T,I,C — ⏳ D |
| **04** | ✅ case 3 | ✅ | ✅ | ✅ `117:53` | ✅ | ⏳ проверка пользователя |
| **05** | ✅ case 4 | ✅ | ✅ | ✅ `117:70` | ✅ | ⏳ проверка пользователя |
| **06** | ✅ case 5 | ✅ | ✅ | ✅ `117:87` | ✅ | ⏳ проверка пользователя |
| **07** | ✅ case 6 | anchor + legal block | ✅ | ✅ `122:53` | ✅ | ⏳ SYNC-D |

**Автопроверка кода (2026-05-23):**

- `OnboardingFigmaAnchor` cases: **0, 1, 2, 3, 4, 5** — все присутствуют
- `onboardingPage`: `figmaAnchor` **до** `zoneConfig` — OK
- `xcodebuild` Debug iPhone Simulator: **BUILD SUCCEEDED**

**Риск рассинхрона (закрыт для 01–06):** ранее OB_04–06 шли через `OnboardingBottomTextPanel` → текст на герое. Сейчас все six используют anchor — **рассинхрон layout path устранён**.

**Остаётся рассинхрон только если:**

1. На устройстве старая сборка **без** cases 3–5 (нужна установка build **≥ 202** с актуальным `14_OnboardingScreen.swift`).
2. Hero PNG в Xcode ≠ upload в Figma (SYNC-H) — см. `ONBOARDING_PAGE_BY_PAGE_LOG.md`.
3. Визуальное отличие SE vs 393 pt (допуск §D ~8–12 pt) — SYNC-D.

---

## 6. Сборка: симулятор и телефон

### Симулятор (DEBUG)

```bash
cd mobile_apps/ALADDIN_iOS
xcodebuild -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 16e' -configuration Debug build
# Установка + прыжок на страницу N (1=OB_01 … 6=OB_06):
xcrun simctl launch booted family.aladdin.ios -RESET_ONBOARDING -OnboardingPage4
```

| `currentPage` | OB | Launch arg |
|---------------|-----|------------|
| 1 | OB_01 | `-OnboardingPage1` |
| 2 | OB_02 | `-OnboardingPage2` |
| 3 | OB_03 | `-OnboardingPage3` |
| 4 | OB_04 | `-OnboardingPage4` |
| 5 | OB_05 | `-OnboardingPage5` |
| 6 | OB_06 | `-OnboardingPage6` |

### Физический iPhone

1. **Product → Archive** (или CI) с тем же коммитом, где есть cases **3–5**.
2. Убедиться в **Настройки → ALADDIN** (или About): **Build 202** (или выше после следующего bump).
3. Удалить приложение и установить заново **или** сбросить онбординг (первый запуск / debug).
4. Пройти OB_04 → OB_05 → OB_06: текст **под** героем, не на нём.

*Release-сборка не поддерживает `-OnboardingPageN` — только полный проход онбординга.*

---

## 7. Deep links Figma (desktop Mac)

```text
OB_00: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=7-65
OB_01: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=81-53
OB_02: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=103-53
OB_03: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=108-53
OB_04: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=117-53
OB_05: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=117-70
OB_06: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=117-87
OB_07: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=122-53
```

**В Layers:** на канвасе OB_03 и OB_04 рядом — выбирать frame по имени (`OB_04_Radar`, не `OB_03_Parents`).

---

## 8. Связанные документы

| Документ | Назначение |
|----------|------------|
| `ONBOARDING_FINAL_ML_ALGORITHM.md` | Алгоритм SYNC-H/T/I/D |
| `ONBOARDING_PAGE_BY_PAGE_LOG.md` | Hero MD5, история правок |
| `ONBOARDING_TODO_MASTER.md` | Чеклист ~30 пунктов |
| `Screens/14_OnboardingScreen.swift` | Реализация |

---

*Обновлять §2–§5 после любого изменения `OnboardingFigmaAnchor` или scrim stops.*
