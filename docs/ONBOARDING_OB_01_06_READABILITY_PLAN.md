# План: читаемость текста OB_01…OB_06 (как референсы, full-bleed hero)

**Статус:** iOS + **Figma синхронизированы** (2026-05-22) — QA симулятор + визуальный просмотр Figma  
**Полный алгоритм приёмки (ML):** `ONBOARDING_FINAL_ML_ALGORITHM.md`  
**Область:** только `currentPage` **1…6** (контент `contentIndex` **0…5**).  
**Не трогаем:** **OB_00** (язык), **OB_07** (приглашение + согласия), copy, hero PNG, TabView chrome.

**Цель:** hero на **весь экран** в ассетах; текст в **нижней читаемой зоне** (~35–40% высоты) с плотным затемнением; **SF Pro**; body **белый**, не серый на фото.

---

## 1. Целевая формула экрана (01–06)

```text
┌──────────────────────── 393 pt ────────────────────────┐
│  HERO full-bleed (OnboardingHero_01…06)                 │  ~58–62% визуально
│  scaledToFill + ignoresSafeArea                         │
│                                                         │
│  ░░░ градиент + scrim (код) ░░░░░░░░░░░░░░░░░░░░░░░░░  │
├─────────────────────────────────────────────────────────┤
│  ТЕКСТОВАЯ ЗОНА (привязка к низу, над chrome)           │  ~300–320 pt
│  [лого V2 только OB_01]                                 │
│  Заголовок 24–26 Bold, white, center                    │
│  Описание 16–17 Regular/Medium, white ~90–100%          │
├─────────────────────────────────────────────────────────┤
│  Точки + «Продолжить» (как сейчас)                      │  ~130–160 pt
└─────────────────────────────────────────────────────────┘
```

**Не делаем:** левый «журнал», укорочение hero до 60% в PNG, tab bar, смену формулировок.

---

## 2. Типографика (единая для 01–06)

| Элемент | Значение | Примечание |
|---------|----------|------------|
| Шрифт | **SF Pro** (`.system`) | Как референсы |
| Заголовок | **24 pt Bold** (22 на SE при Dynamic Type) | `.foregroundColor(.white)` |
| Описание | **16 pt Regular** или **Medium** | `.foregroundColor(.white.opacity(0.92))` — не `textSecondary` |
| Межстрочный | `lineSpacing(4…6)` | |
| Выравнивание | **center** | Онбординг, не статья |
| Wordmark OB_01 | h=**104**, maxWidth **361** | Только `contentIndex == 0` |

---

## 3. Затемнение (читаемость на ярких hero)

**Два слоя (код):**

1. `HeroBottomReadableGradient` — для `currentPage` **1…6** всегда **`strong: true`** (opacity низа **≥0.62**, при необходимости **0.72**).
2. **Scrim-плашка** под текстом (новый компонент) — `Color.black.opacity(0.35…0.45)` на высоте текстовой зоны, скругление не обязательно (full width).

**Критерий приёмки:** контраст заголовка и body **≥4.5:1** на worst-case кадре (OB_02, OB_03).

---

## 4. Размещение по страницам (01–06)

Высоты от низа экрана (эталон **852 pt**, без home indicator — safe area добавляет Xcode).

| OB | `currentPage` | Hero asset | Лого в текстовой зоне | Высота текстовой зоны (от низа) | Особенности hero / градиент |
|----|---------------|------------|------------------------|--------------------------------|-----------------------------|
| **01** | 1 | `OnboardingHero_01` | **Да** — `OnboardingLogo_V2` 104pt | **~300 pt** (лого + title + desc) | Яркое лицо сверху; **самый сильный scrim** 0.45 |
| **02** | 2 | `OnboardingHero_02` | Нет | **~220 pt** | Parallax оставить; светлые блики — strong gradient |
| **03** | 3 | `OnboardingHero_03` | Нет | **~220 pt** | Яркая сцена — strong + scrim 0.40 |
| **04** | 4 | `OnboardingHero_04` | Нет | **~240 pt** | Тёмный космос — scrim **0.35** (слабее) |
| **05** | 5 | `OnboardingHero_05` | Нет | **~240 pt** | Средняя яркость — scrim 0.38 |
| **06** | 6 | `OnboardingHero_06` | Нет | **~220 pt** | strong gradient |

**Отступы внутри текстовой зоны:**
- horizontal: `Spacing.screenPadding` (16) или 16 как в Figma  
- между лого и заголовком: `Spacing.s` (12)  
- между заголовком и описанием: `Spacing.m` (16)  
- низ текстовой зоны → верх chrome: **≥16 pt**

**Figma-ориентиры (обновить после вёрстки в коде):** OB_01 title y≈598 → эквивалент «низ минус 250pt».

---

## 5. Изменения в коде (порядок работ)

### Этап A — фундамент (один раз)

| # | Задача | Файл |
|---|--------|------|
| A1 | Константы зоны: `onboardingTextZoneMinHeight`, отступ над chrome | `14_OnboardingScreen.swift` или `Spacing.swift` |
| A2 | Компонент `OnboardingBottomTextPanel` — VStack title/desc, optional logo, scrim background | `14_OnboardingScreen.swift` или `Shared/Components/` |
| A3 | `HeroBottomReadableGradient`: `strong` для `currentPage` 1…6 | `14_OnboardingScreen.swift` |
| A4 | Убрать `Spacer()` «плавающий» layout для `contentIndex` 0…5 | `onboardingPage()` |

### Этап B — по страницам (после **каждой** подзадачи → SYNC §3.1 в `ONBOARDING_FINAL_ML_ALGORITHM.md`)

| # | Страница | Подзадачи | Обязательная сверка Figma ↔ iOS |
|---|----------|-----------|----------------------------------|
| B1 | OB_01 | hero → Figma T → iOS I → QA | **SYNC-H,T,I,C,D** — эталон |
| B2 | OB_02 | hero → Figma T → iOS I → QA | **SYNC-H,T,I,C,D** |
| B3 | OB_03 | hero → Figma T → iOS I → QA | **SYNC-H,T,I,C,D** |
| B4 | OB_04 | hero → Figma T → iOS I → QA | **SYNC-H,T,I,C,D** |
| B5 | OB_05 | hero → Figma T → iOS I → QA | **SYNC-H,T,I,C,D** |
| B6 | OB_06 | hero → Figma T → iOS I → QA | **SYNC-H,T,I,C,D** |

**Без галочки SYNC** следующая подзадача / страница **не начинается**.

### Этап C — документация

| # | Задача |
|---|--------|
| C1 | Обновить `ONBOARDING_PAGE_BY_PAGE_LOG.md` — блок «readability 01–06» |
| C2 | Отметить в `ONBOARDING_LAYER_RULES.md` ссылку на этот план |

---

## 6. Что не меняем

| Элемент | Причина |
|---------|---------|
| OB_00 | Язык — отдельный layout (`languageStepView`) |
| OB_07 | ScrollView, согласия, 2 кнопки — по запросу позже |
| PNG `OnboardingHero_*` | Full-bleed остаётся |
| Локализация page1…page6 | Copy утверждён |
| Пропустить / точки / CTA | Только позиция относительно новой зоны |

---

## 7. Критерии «сдано» (01–06)

- [x] Код: `OnboardingBottomTextPanel` + привязка к низу (`chromeBottomReserve` 162pt)
- [x] Body **белый** 92% на 01–06
- [x] `HeroBottomReadableGradient(strong:)` для `currentPage` 0…6
- [x] Figma 01–06: **SF Pro Bold 24** title, **SF Pro Regular 16** desc **white 92%**
- [x] Figma 01–06: слой **`READABILITY_scrim_bottom`** (градиент)
- [x] Figma 04–06: hero **393×852** из Xcode assets
- [ ] Текст **не пересекается** с лицами — проверка SE + Pro Max
- [ ] Длинные desc (02, 05) не выходят за зону — проверка RU/EN
- [ ] OB_00 и OB_07 **без регрессий**

---

*Создано: 2026-05-22 · ветка работ: ALADDIN_iOS onboarding readability*
