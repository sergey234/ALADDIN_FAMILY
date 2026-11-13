# UX Phone QA Wave — план + чеклисты + TODO (2026-11-13)

**Статус:** EXECUTION — P0–P6 + H1–H8 + FNT-2/3 + HYBRID A–G code ✅ · **Build 23** · **OB_01 FROZEN** · карта ассетов `docs/ML_SYSTEM_ASSET_MAP_IN_APP_2026-11-14.md` · Device QA / Figma sync остаток  
**Правило:** 1 задача → static verify → следующая. Без mass. Без LocManager rewrite. Без bump без GO.  
**Сборка / Simulator / Device QA:** только в **самом конце волны** (или явный «GO на сборку»). До конца — grep/verify scripts, без `xcodebuild`.  
**Локализация:** любой новый/изменённый UI-текст = сразу **RU + EN** в `Resources/Localization/{ru,en}.lproj/Localizable.strings` (+ точечный LocManager при необходимости). **Запрет сырых ключей** на экране (`pay_pains_…` / `map_soon_…` как видимый текст).  
**Доказательство GPS:** реальный iPhone, Самара, MegaFon, «Точность ±5155 м» (не Simulator).

---

## Снимок «до волны» (заморожен 2026-11-13 16:38 +04)

| Поле | Значение |
|------|----------|
| Branch | `master` |
| HEAD (полный) | `59be653efe3b45bc1ce9ccc77aeb8d3506118677` |
| HEAD (короткий) | `59be653e` |
| Сообщение | `fix(ci): hard-fail ASC upload on agreement 403 (no false green)` |
| origin/master | совпадает с HEAD на момент снимка |
| Ассеты семьи | `~/Downloads/ALADDIN_Hero_Family_Candidates_2026-11-13/` (H25 Stand/Kneel 2x+3x, H17 Walk/Kneel 3x) |
| План | этот файл |

**Откат всей волны к этому снимку:** `git restore --source=59be653e -- <paths>` или revert коммитов после `59be653e` (только по GO владельца; не hard-reset без явной команды).

**Скрины «до»:** владельцу сохранить в Photos/Files по экранам перед каждым P* (QR overlay, Antifake, OB_01, Settings, Метки, карта ±accuracy, post-reg, Удобный). В репо скрины не коммитим без нужды.

### Список файлов по шагам (целевой blast radius)

| Шаг | Файлы |
|-----|--------|
| P0 | `Screens/MainScreenWithRegistration.swift` |
| P1 | `Screens/AntifakeHubScreen.swift` |
| P2 | `Assets.xcassets/OnboardingLogo_V2_Cinematic.imageset/*`, `Screens/14_OnboardingScreen.swift`, verify script, Figma OB_01 |
| P3 | `Screens/05_SettingsScreen.swift`, `Shared/Components/AliveIconStyle.swift`, `Resources/Localization/{ru,en}.lproj/Localizable.strings` (+ точечный LocManager) |
| P4 | `Resources/Localization/{ru,en}.lproj/Localizable.strings` (+ точечный LocManager keys `map_soon_tile_*`) |
| P5 | `Screens/FamilySafetyRemainderHub.swift`, `Screens/WhereIsPhoneScreen.swift` (+ toast strings при необходимости) |
| P6 / FNT-1 | `Screens/02_FamilyScreen.swift` (`PostRegistrationDeviceGuideModal`) |
| CAP | CapCut export → Downloads → по GO в Assets |
| FIG | отдельный Figma SimpleHome (не onboarding file) |
| P7 | `Screens/SimpleHomeScreen.swift` (+ новый imageset) |
| FNT-2 | registration/recovery chrome (файлы уточнить на старте GO) |
| FNT-3 | `Screens/05_SettingsScreen.swift` headers only |
| H1–H3 | `Screens/01_MainScreen.swift` |
| H4 | `Screens/05_SettingsScreen.swift` |
| H5 | `Screens/23_FamilyChatScreen.swift` |
| H6 | `Screens/06_AIAssistantScreen.swift` |
| H7 | Companion conversation screen |
| H8 | Family/Profile add-member entry points |

---

## Инварианты на КАЖДЫЙ шаг

- [ ] **До:** путь навигации записан (откуда → куда → назад)
- [ ] **После:** тот же путь работает
- [ ] Текст RU читаем; EN не сломан если трогали strings
- [ ] Шрифт заголовков не «поплыл» на соседних экранах
- [ ] a11y / accessibilityIdentifier на месте
- [ ] Diff только целевые файлы (нет bot / .env)
- [ ] Можно откатить: `git checkout -- <files>` или revert коммита

### Что сохранять ПЕРЕД правками (бэкап)

| Когда | Что сохранить |
|-------|----------------|
| Перед любым P* | `git status` + текущий `HEAD` hash |
| Перед P2 wordmark | imageset `OnboardingLogo_V2_Cinematic` + якоря OB_01 в `14_OnboardingScreen.swift` |
| Перед P5 GPS | снимок `FamilySafetyRemainderHub.swift` (или полагаться на git) |
| Перед P7 SimpleHome | `SimpleHomeScreen.swift` + новый CapCut PNG в Downloads |
| Перед шрифтовой очередью | список файлов шага; git достаточно для отката |
| Ассеты-кандидаты семьи | уже в Downloads: `~/Downloads/ALADDIN_Hero_Family_Candidates_2026-11-13/` |

**Откат:** каждый шаг = отдельный коммит по GO → `git revert <sha>` или `git restore --source=HEAD~1 -- path`. Флаг `PayPainsUIFlags.disableNewUIForRollback()` — аварийный откат Удобного режима (не шрифтов).

---

## Очередь задач (мастер-TODO)

| ID | Задача | Статус |
|----|--------|--------|
| P0 | Recovery overlay hide glass | ✅ code (Device QA pending) |
| P1 | Antifake scroll (hero in scroll, tabs sticky) | ✅ code (Device QA pending) |
| P2 / OB_01 | Hero + wordmark | ✅ **FROZEN** — hero 1179×2556 no-text · wordmark transparent y=**32** · см. `ONBOARDING_OB01_FREEZE_2026-11-13.md` |
| P3 | Settings contrast + short copy + «Иконки» | ✅ code |
| P4 | map_soon copy (без «заглушек») | ✅ |
| P5 | GPS accuracy gate (device Samara) | ✅ code (Device QA конец) |
| P6 | Post-reg device chrome + AladdinFamilyType title | ✅ |
| CAP | CapCut «Щит семьи» | ⏳ арт · **канон layout = HYBRID (V2)** |
| FIG | Figma SimpleHome 393×852 (не OB-файл) | ⏳ после CAP / placeholder A |
| P7 | SimpleHome HYBRID orbit + glass · list fallback | ⏳ после FIG |
| FNT-1 | Font: P6 post-reg (внутри P6) | ✅ |
| FNT-2 | Font: recovery/registration chrome titles | ✅ code |
| FNT-3 | Font: Settings section headers | ✅ code |
| FNT-N | Font: дальше только по GO владельца | ⏳ |
| H1 | Main nav | ✅ |
| H2 | Main tiles + manage/add | ✅ |
| H3 | Chat segment | ✅ |
| H4 | Settings rows | ✅ |
| H5 | FamilyChat non-send | ✅ |
| H6–H8 | AI / Companion / add-member gaps | ✅ code |
| Wave build | xcodebuild / Device QA | ⏳ только в конце |

---

## P0 — Overlay «Семья под защитой» на QR

**Файлы:** `Screens/MainScreenWithRegistration.swift` (~87, 161–223)

### Подзадачи
- [x] P0.1 Скрыть `payPainsAuthGlassOverlay` при `showFamilyCreatedModal`
- [x] P0.2 Скрыть при `showSuccessModal`
- [x] P0.3 Убедиться: уже скрыт на role/age/letter/consent/loading
- [ ] P0.4 Nav check: Добавить семью → QR → Готово тапается (Device QA / GO на сборку)
- [ ] P0.5 Nav check: Отмена / закрытие без зависания glass

**Не трогать:** RecoveryCodeModal тело, тексты pay_pains_auth.

---

## P1 — Antifake scroll

**Файлы:** `Screens/AntifakeHubScreen.swift`

### Подзадачи
- [x] P1.1 Pin только `header` + `tabPicker`
- [x] P1.2 Hero CheckScam → в ScrollView
- [x] P1.3 trustBanner + tip → в ScrollView
- [x] P1.4 tabContent + assistant + CheckFamily остаются в scroll
- [ ] P1.5 Nav: 5 вкладок + Проверить + назад (Device QA)
- [ ] P1.6 Скролл поднимает фото; tabs видны сверху (Device QA)

---

## P2 — Wordmark над головой

**Файлы:** `OnboardingLogo_V2_Cinematic` imageset; `Screens/14_OnboardingScreen.swift`; verify; Figma OB_01

### Подзадачи
- [x] P2.1 Бэкап PNG в Downloads (`ALADDIN_Wordmark_P2_backup_2026-11-13`)
- [x] P2.2–P2.3 **ОТКАТ** 2026-11-13: full-bleed ink дал **чёрную плашку** → восстановлен transparent imageset + y=**271**
- [ ] P2.4 CapCut: новый transparent wordmark (промпт ниже) — только после арта
- [x] P2.5 verify wordmark case0 = (17, **271**, 360, 121)
- [ ] P2.6 Device QA: золотые буквы **без** чёрного прямоугольника

### CapCut — промпт wordmark (ОБЯЗАТЕЛЬНО transparent)

**Цель:** слой `ALADDIN AI` золотом поверх hero, без фона.

```
Задача: экспорт логотипа ALADDIN AI для iOS онбординга OB_01.

ЧТО НУЖНО НА ВЫХОДЕ
- PNG с АЛЬФА-каналом (прозрачный фон).
- Только золотые буквы «ALADDIN AI» (serif / cinematic metallic gold).
- БЕЗ чёрной/тёмной подложки, БЕЗ прямоугольника, БЕЗ градиентной плашки.
- БЕЗ водяного знака CapCut.
- Соотношение близко к 360×121 pt (~1080×360 px @3x ок).
- Буквы по центру кадра, вокруг — чистая прозрачность (alpha=0).

КАК СДЕЛАТЬ В CAPCUT
1) Новый проект → соотношение кадра под лого (горизонталь ~3:1).
2) Фон проекта: прозрачный / checkerboard. Если CapCut даёт только чёрный — НЕ экспортируй так в Assets.
3) Текст «ALADDIN AI»: золотой градиент/металл, без stroke-подложки на весь кадр.
4) Экспорт: PNG → включить Transparent / Alpha (не JPG, не MP4-кадр с чёрным фоном).
5) Проверка ДО передачи в Xcode: открой PNG — углы должны быть прозрачными, не тёмно-серыми (30,30,30).
6) Клади в Downloads; в Assets.xcassets/OnboardingLogo_V2_Cinematic.imageset — только после проверки alpha.

ЗАПРЕЩЕНО
- «Full-bleed ink» / чёрный plate под буквами.
- Экспорт скрина CapCut с чёрным canvas.
- Накладывать лого поверх hero внутри CapCut и экспортировать весь кадр 393×852 как wordmark.
Wordmark = отдельный маленький PNG только с буквами.
Hero кадр = отдельно, без текста лого на PNG.
```

---

## P3 — Settings Classic / Gold / Иконки + чат

**Файлы:** `Screens/05_SettingsScreen.swift`; `Shared/Components/AliveIconStyle.swift`; `ru/en` Localizable.strings

### Подзадачи
- [ ] P3.1 Subtitle → «Стиль иконок на главной» (+ EN)
- [ ] P3.2 «Значки» → «Иконки» (`titleRU` / strings)
- [ ] P3.3 Segmented: читаемый невыбранный текст + tint
- [ ] P3.4 То же для «Чат по умолчанию»
- [ ] P3.5 Nav: Настройки → смена стиля → назад; главная отражает стиль

---

## P4 — Копия «Метки»

**Ключи:** `map_soon_tile_title`, `map_soon_tile_body` (ru + en + точечный LocManager)

### Подзадачи
- [ ] P4.1 RU body: `Скоро: метки вещей и питомцев на карте.`
- [ ] P4.2 EN body: `Coming soon: item and pet tags on the map.`
- [ ] P4.3 Запрет фраз: «заглушек», «фейковых точек», «Пока без…»
- [ ] P4.4 Проверка: Где семья → Безопасность → Метки

---

## P5 — GPS accuracy gate (реальный iPhone)

**Доказательство:** Самара, ±5155 м.  
**Файлы:** `Screens/FamilySafetyRemainderHub.swift` (`FamilyMapLiveLocationController`); `Screens/WhereIsPhoneScreen.swift` (~1101)

### Подзадачи
- [ ] P5.1 Не писать `coordinate` если accuracy `< 0` или `> 80`
- [ ] P5.2 `requestFreshFix`: крутить updates до хорошего фикса / timeout
- [ ] P5.3 Toast «Уточняем место…» (ключ при необходимости)
- [ ] P5.4 Не двигать камеру на cell-fix
- [ ] P5.5 Badge accuracy оставить честным
- [ ] P5.6 Device QA: без VPN, «Обновить моё место» — pin не уезжает на км при ±5000

---

## P6 — Post-reg device + шрифт title (FNT-1)

**Файлы:** `PostRegistrationDeviceGuideModal` в `Screens/02_FamilyScreen.swift`

### Подзадачи
- [ ] P6.1 Убрать белый host / выровнять под StormMesh glass
- [ ] P6.2 Title → `AladdinFamilyType` (как Удобный режим)
- [ ] P6.3 Кнопки: primary blue + secondary gold (как сейчас логика)
- [ ] P6.4 Контраст body
- [ ] P6.5 Nav: после регистрации → модалка → Позже / Устройства

---

## CAP + FIG + P7 — Удобный режим · **HYBRID MAX** (2026-11-13)

**Канон:** **V2 Гибрид MAX** — Hero **5811** · 3 glass-круга с **мини-иконками CapCut** · chips glass · list fallback.  
**Стекло / подписи / тапы** — только **SwiftUI** (не вшивать в hero PNG).  
**Не трогать:** OB_00…07 · onboarding Figma · legacy tile keys.

### Где что делается (просто)

| # | Что | Где | Кто |
|---|-----|-----|-----|
| 1 | Семья+щит 5811 (без текста) | **CapCut** → Downloads | владелец export Original |
| 2 | 3 мини-иконки дверей (прозрачный PNG) | **CapCut** | владелец по промптам ниже |
| 3 | Сетка 393×852: hero + орбита + chips | **Figma** (отдельный файл, не OB) | агент |
| 4 | Glass круги/chips + AliveGlyph + nav + a11y | **iOS P7** `SimpleHomeScreen` | агент |
| 5 | Wire иконок в Assets | **Xcode Assets** | агент после CapCut |
| 6 | Device QA | Simulator/Device | только **GO на сборку** |

### Схема HYBRID MAX
```
        [Проверить]     ← glass ~88–96pt + icon_check (CapCut mini)
              \
    [Ребёнок]  ★5811★  [Где]   ← icon_child · icon_where
              /
     ─────────────────
   [AI] [Добавить] [Меню]  ← capsule glass (Swift only)
   (опц.) Полная версия
```

### Порядок MAX (без разъезда)
1. **CAP hero** — 5811 · 1179×2556 + crop 960×660 · без текста  
2. **CAP icons** — 3 мини PNG 512×512 transparent (Проверить / Ребёнок / Где)  
3. **FIG** — отдельный файл 393×852 · якоря орбиты + chips (до кода)  
4. **P7** — HYBRID рядом с list · флаг UI · glass + icons  
5. **Nav / a11y** — `pay_pains_door_*` · companion · menu · full  
6. **Device** — только GO на сборку  

**Не делать:** орбита только картинкой CapCut; текст дверей на PNG; 3D-шары «Занятий» целиком; ломать list fallback.

### CAP подзадачи
- [x] CAP.0 Канон = **HYBRID MAX**
- [x] CAP.1 Winner **5811** · `~/Downloads/ALADDIN_SimpleHome_HYBRID_PICK_2026-11-13/`
- [x] CAP.2 Interim 1179×2556 + 960×660 · `~/Downloads/ALADDIN_SimpleHome_CAP_5811_HYBRID_2026-11-13/`  
      ⏳ CapCut **Original 5811** → заменить interim (опц. качество)
- [x] CAP.2b **3 door icons** · канон 2026-11-14 (см. карту ассетов ниже)
- [ ] CAP.3 Assets hero + 3 icons в Xcode · по GO
- [ ] CAP.4 H25/H17 compare (опц.)

### Карта ассетов Door Icons (SSOT для ML) — 2026-11-14
**Папка канона:** `~/Downloads/ALADDIN_SimpleHome_DoorIcons_CANON_2026-11-14/`  
**Копия:** `~/Downloads/ALADDIN_CapCut_SimpleHome_DoorIcons_2026-11-13/CANON_PICKS/`  
**README:** `00_CANON_MAP.txt`

| Дверь | Winner файл | CapCut id | Почему |
|-------|-------------|-----------|--------|
| **Проверить** | `door_check_WINNER_5943_512_circle.png` | **5943** | щит+дом+семья+лупа, 1280, богаче металла |
| **Ребёнок** | `door_child_WINNER_5904_512_circle.png` | **5904** | мальчик+мини-щит в орбе |
| **Где** | `door_where_WINNER_5944_512_circle.png` | **5944** | двое детей + пин + щит (=семья) |
| ALT Check | `door_check_ALT_5942_*` | 5942 | второй щит — архив |
| ALT Where | `door_where_ALT_5945_*` | 5945 | пин без семьи — не канон |

Watermark CapCut на 5943/5942/5904: смягчён soft-fill угла (не generative). 5944 — чистый.  
Фон: circle PNG = орб на прозрачном; в Swift — подпись **под** кругом.

**Стекло:** CapCut-иконки уже с орбом. В P7 — **лёгкий** Swift `stormGlass` / material + white stroke снаружи (как «Занятия»), без второго тяжёлого 3D-шара.

### FIG подзадачи
- [x] FIG.1 Новый Figma · `docs/FIGMA_SIMPLEHOME.env` · key `3xbmhXxfMNMBmIbeJdUDpW` · frame `SimpleHome_HYBRID_393x852` (`1:2`)
- [x] FIG.2 HYBRID: hero 5811 + 3 orbit doors + labels + chips + orbit-ring
- [x] FIG.3 CANON PNG на placeholder Check/Child/Where (`1:7`/`1:11`/`1:15`)
- [x] FIG.4 OB_00…07 не трогали

### P7 подзадачи
- [x] P7.1 HYBRID orbit + list fallback (`aladdin.simpleHomeHybridOrbit` + Dynamic Type)
- [x] P7.2 a11y `pay_pains_door_*` / `pay_pains_ai_friends` / `pay_pains_chip_add` / `pay_pains_menu` / full
- [x] P7.3 Haptics light/soft
- [x] P7.4 Nav сохранён (Antifake / Child sheet / Where / Companion / Menu / addMemberOptions / Main)
- [x] P7.5 Assets: `SimpleHome_Hero_5811` + `SimpleHome_Door_{Check,Child,Where}`
- [x] P7.6 Reduce Motion: без «живого» акцента кольца (статичный stroke)
- [ ] P7.7 GATES Device QA (тапы · hero не перекрывает · откат list) — **нужен GO на сборку**

### BACKUP до HYBRID (2026-11-14) — только сохранение, без правок UI
`BACKUPS/SimpleHome_PRE_HYBRID_P7_20261114_010010/`  
- `SimpleHomeScreen.swift` (1297 lines) · `PayPainsUIFlags.swift` · `NavigationManager.swift` · `SHA256.txt`  
Откат list-UI: скопировать `SimpleHomeScreen.swift` обратно (см. `00_README.txt` в папке).

### NAV карта — текущий Удобный режим (сохранить при HYBRID)

Вход: `PayPainsUIFlags.shouldOpenSimpleHomeAtLaunch` → `.simpleHome` · файл `Screens/SimpleHomeScreen.swift`.

| UI (сейчас) | a11y id | Действие | Куда |
|-------------|---------|----------|------|
| Полоска семьи (тело) | `pay_pains_family_strip` | haptic light | `.family` |
| **Добавить в семью** | `pay_pains_family_strip_add_to_family` | haptic | `.addMemberOptions` |
| Дверь **Проверить** | `pay_pains_door_check` | haptic · analytics | `navigateToAntifakeHub(tab: .text)` |
| Дверь **Ребёнок** | `pay_pains_door_child` | sheet | `showChildDoor` → под-карточки (PC / rewards / childInterface / sheets) |
| Дверь **Где** | `pay_pains_door_where` | sheet | `showWherePhone` → WhereIsPhone |
| AI Друзья | `pay_pains_ai_friends` | haptic | `navigateToCompanionHome(returnTo: .simpleHome)` |
| **Меню** | `pay_pains_menu` | sheet | тарифы / settings / protection / companion / AI / chat / notifications / full→`.main` |
| **Полная версия** | `simple_home_open_full_main` | haptic | `navigateToRoot(.main)` |
| Child → сайты/время | `pay_pains_child_*` | `leaveChildDoorThen` | `.parentalControl` / sheets / `.childRewards` / `.childInterface` |
| Меню → строки | `pay_pains_menu_*` | dismiss+push · restore menu on back | см. `payPainsMenuSheet` |

**HYBRID chips:** только **AI · Меню** (Добавить — на strip как «Добавить в семью»).

### HYBRID polish A–G (2026-11-14) — code

- [x] **A** Шапка: центр · `secondaryGold` · `AladdinFamilyType.title2()`
- [x] **B** «Добавить в семью» на strip → `addMemberOptions` · chip Добавить убран · низ AI·Меню
- [x] **C** Hero меньше/ниже · Проверить над фото · симметрия · воздух · hit ~88
- [x] **D** Strip / chips / Полная / orbit labels → New York · list не ломали
- [x] **E** Orbit только короткие имена · subtitle → `accessibilityHint` · list как был
- [ ] **F** Device QA + Figma sync layout — **нужен GO на сборку**
- [x] **G** Мягкий пульс дверей · Reduce Motion = off · без карусели
- [x] **NAV-fix** Root goBack: fade (не slide) — белая полоса Settings→SimpleHome; Меню reopen после fade

### Что ещё необходимо сделать (чеклист до «готово»)

**Nav / UX (обязательно при P7):**
- [x] P7-NAV.1 ids `pay_pains_door_*` / `pay_pains_menu` / `pay_pains_ai_friends` / `simple_home_open_full_main` (+ `pay_pains_family_strip_add_to_family`)
- [x] P7-NAV.2 Те же destinations (Antifake / Child / Where / Companion / Menu / Full Main)
- [x] P7-NAV.3 Haptic light/soft
- [x] P7-NAV.4 **Добавить в семью** на strip (не chip) → `addMemberOptions`
- [x] P7-NAV.5 `leaveChildDoorThen` / restore menu — не трогали
- [x] P7-NAV.6 Orbit layout без перекрытия лиц (code; Device QA в F)
- [x] P7-NAV.7 Dynamic Type / Reduce Motion → list + static doors
- [x] P7-NAV.8 Main tile → `navigateToSimpleHome()` без изменений

**FIG / Assets:**
- [x] FIG.3 canon door PNG
- [x] CAP.3 imageset hero 5811 + 3 door icons
- [ ] (опц.) Original 5811 заменить interim
- [ ] Figma frame sync после A–G layout (с F)

**Доказательства:**
- [ ] Device QA: 3 двери + AI + Меню + Полная + Добавить в семью + Назад
- [ ] Откат: флаг / list layout без потери nav

### CapCut — статус
- [x] Hero 5811 interim + door icons canon 5943/5904/5944  
- [ ] (опц.) Original 5811  

**Промпты:**  
`~/Downloads/ALADDIN_CapCut_SimpleHome_V1_V2_V3_PROMPTS_2026-11-13/`  
`~/Downloads/ALADDIN_CapCut_SimpleHome_DoorIcons_2026-11-13/` · канон `…DoorIcons_CANON_2026-11-14/`

---

## Шрифт AladdinFamilyType — очередь и безопасность

### Будет ли «везде как Удобный режим»?
**Не одним PR.** Канон цели: заголовки дверей/модалок/ключевых экранов → serif `AladdinFamilyType`.  
Очередь: **FNT-1 (P6) → FNT-2 recovery chrome → FNT-3 Settings headers → дальше только GO.**  
Не делаем массовую замену `.font(.h3)` по репо.

### Ничего не съедет?
Риск низкий при точечных правках title-only. Риск высокий при mass replace (ломает плотность, a11y Dynamic Type на мелких экранах). Поэтому только заголовки по списку.

### Откат?
Да: git revert шага; файлы до правки в git history. Аварийный UI-флаг Удобного режима — отдельно от шрифтов.

### Что сохранять перед шрифтовыми правками?
1. `git rev-parse HEAD`  
2. Список файлов шага  
3. Скрин «до» целевого экрана  
4. После — скрин «после» + nav checklist

---

## Хаптики H1…H8 (после P3, по одному)

| ID | Где | Подзадачи |
|----|-----|-----------|
| H1 | Main bottom nav ×5 | [ ] impact light на каждый таб [ ] nav check 5 табов |
| H2 | Main tiles + Управлять + Добавить | [ ] haptics [ ] nav |
| H3 | Chat segment главная | [ ] selection [ ] nav |
| H4 | Settings rows + pickers | [ ] без double-fire на Toggle [ ] nav |
| H5 | FamilyChat non-send | [ ] [ ] |
| H6 | AI non-send | [x] code [ ] device |
| H7 | Companion | [x] code [ ] device |
| H8 | Add-member entry gaps | [x] code [ ] device |

**Правило:** только `HapticFeedback.*`; не сырой `UIImpactFeedbackGenerator`.

---

## Nav master checklist (прогон после каждого P*/H*)

| Поток | До | После |
|-------|----|-------|
| Удобный: 3 двери / Меню / Полная / Назад | [ ] | [ ] |
| Main: 5 табов + плитки + Управлять | [ ] | [ ] |
| Регистрация: QR → Готово → post-reg | [ ] | [ ] |
| Карта: Обновить место + точность + табы | [ ] | [ ] |
| Antifake: 5 вкладок + Проверить | [ ] | [ ] |
| Settings: стили иконок + чат + Назад | [ ] | [ ] |

---

## Порядок исполнения

`P0 → P1 → P2 → P3 → P4 → P5 → P6`  
параллельно арт: `CAP → FIG → P7`  
хаптики: `H1…H8` после P3  
шрифт: FNT-1 в P6; FNT-2/3 только по GO

**Следующий шаг кода:** GO владельца на **P0**.
