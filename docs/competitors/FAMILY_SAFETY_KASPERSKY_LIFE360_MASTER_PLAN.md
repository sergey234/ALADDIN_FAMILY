# FAMILY SAFETY — единый master-план (Kaspersky + Life360 → ALADDIN)

**Дата:** 2026-11-04 · **версия:** 1.4 (owner lock §17 · plan/fact checklist · Pet wizard = отдельный GO)  
**Для кого:** другая ML-система / агент / подрядчик — **читать этот файл первым**.  
**Статус docs:** канон реализации. **Код / Figma / xcodebuild / партнёры / Device QA — только после явного GO владельца.**  
**Plan/fact:** [`FAMILY_SAFETY_PLAN_FACT_CHECKLIST.md`](FAMILY_SAFETY_PLAN_FACT_CHECKLIST.md)

---

## 0. Одна минута — без двойных трактовок

| Вопрос | Ответ (канон) |
|--------|----------------|
| Сколько планов реализации? | **Один:** этот master. Два других файла = **аудиты-источники**, не конкурирующие планы. |
| Kaspersky MD? | Этап 1 audit SSOT: `KASPERSKY_WHOCALLS_SAFEKIDS_60_SCREEN_AUDIT_ACTION_PLAN.md` (S01–S60) |
| Life360 MD? | Этап 2 audit SSOT: `LIFE360_SCREEN_AUDIT_ACTION_PLAN.md` + `_partial_L01_L30/31_L60/61_L90.md` (L01–L90) |
| Куда код? | Удобный → 3 двери; Life360 (карта + **4 таба** + sheets) **внутри** `WhereIsPhoneScreen` — один map hub, не второй |
| Дизайн Life360 1:1? | **Max-UI + гибрид:** внутри хаба «Где семья» — **4 таба как у Life360** (Место / Вождение / Безопас. / Подписка) + map + sheets. **Не** purple бренд, **не** spy-copy. Вход в приложение = Удобный (3 двери), не выкидываем SimpleHome. |
| Шрифт / цвет / карточки? | **Как Удобный режим** (`SimpleHomeScreen`) — §2 ниже. Не Inter/Roboto. Не Kaspersky green. |
| Сразу 100% красиво? | **Да как цель ship:** каждый экран волны = prod-beautiful Storm glass + SimpleHome type. Не «временный wireframe». |
| 60+90 проанализированы? | **Да.** Индексы + карточки TAKE/ADAPT/SKIP. |
| JPG как L01.jpg? | **Да (копии):** `docs/competitors/screenshots_life360/L01.jpg`…`L90.jpg` · `screenshots_kaspersky/S01.jpg`…`S60.jpg`. Исходники Cursor = `photo_*` + FILE_INDEX. |
| Готовность «100%»? | **Docs v1.3** (+ §17 порядок исполнения). Figma/Swift = по GO. |
| Переводы по пунктам? | **Да:** правила §7.0 + glossary §7.2 на Wave B/C; Kaspersky пакеты в audit §16. Сырых ключей на экране — FAIL. |
| Навигация кликов? | **Да:** §13 (сейчас · Life360 · будет). |
| Интуиция «где/что/зачем»? | **Да:** §13.4 — по зонам; **ничего не убираем**, только ясность. |
| UX цель? | Красиво · просто · понятно (родитель за ~3 сек понимает экран). |

### Порядок чтения для ML

```text
1) ЭТОТ ФАЙЛ (master)          ← решения, дизайн, волны, backlog, GATES
2) Kaspersky audit MD          ← детали S01–S60, P0–P2
3) Life360 audit MD + partials ← детали L01–L90, P3–P4, §3b SKIP/гибрид
4) FILE_INDEX txt              ← какой JPG открыть
5) Swift якоря                 ← SimpleHome / WhereIsPhone / Parental / Tariffs
```

**Запрещено:** начинать код с partials без master; плодить второй TabView «как Life360»; писать «следим весь день»; ship mock crash/Tile/dispatch.

---

## 1. Архитектура продукта (одна IA)

```text
Удобный режим = SimpleHomeScreen          ← дверь; шрифт/карточки = эталон
├── Дверь «Проверить»                     ← Kaspersky A (Call Directory, antifake, QR, Анти-Баннер…)
├── Дверь «Ребёнок»                       ← Kaspersky A (пауза, сайты, лимит, VK empty…)
├── Дверь «Где телефон» → WhereIsPhoneScreen   ← ЕДИНСТВЕННЫЙ Map hub
│     Wave A: last-point + Places + батарея
│     Wave B: live Map + Always Allow + max-UI Life360 (sheet внутри)
│     Wave C: Crash / SOS / Tile empty / эвакуатор «скоро»
└── Меню «Все разделы» → Family · Parental · Tariffs · Помощь · Дом/сеть
```

### IA гибрид (замок владельца 2026-11-04 — 4 таба **разрешены**)

```text
Удобный режим (вход в приложение — 3 двери)
└── дверь «Где семья» → WhereIsPhone hub (ОДИН map hub)
      └── bottom bar как Life360 (РАЗРЕШЕНО):
            1. Местоположение  → карта + sheets + Places + Calendar
            2. Вождение        → UI таб есть; контент = speed badge / «скоро» / P4 later
            3. Безопасность    → Crash / SOS / Tile·evac «скоро»
            4. Подписка        → Тарифы ALADDIN (10_TariffsScreen / paywall), не чужой Store Life360
```

**Разрешено:** 4 таба Life360-паттерна **внутри** хаба «Где семья» (гибрид max-UI).  
**По-прежнему нет:** второго отдельного Map hub в другом разделе; purple brand Life360; spy-copy; fake «помощь едет»; full Driving reports как ship-продукт до P4 (таб «Вождение» при этом **показываем**).

---

## 2. Design System — эталон Удобный режим (без двойных трактовок)

**SSOT визуала для Family/Map/Kaspersky дверей:** код `Screens/SimpleHomeScreen.swift` + `Shared/Components/StormGlassCardStyle.swift` + `Shared/Styles/Spacing.swift` + `Shared/Styles/Colors.swift`.

| Элемент | Канон ALADDIN | Не делать |
|---------|---------------|-----------|
| **Фон экрана** | `LinearGradient.backgroundGradient` / storm mesh (тёмный `#0F172A` + indigo) | Плоский purple Life360 `#7D4CFA`; Kaspersky teal/green |
| **Карточка** | `.stormGlassCard(cornerRadius: CornerRadius.large)` — glass + золотая обводка | Белые Material-карточки Life360; серые плиты |
| **Заголовок двери/карточки** | `Font.system(.title2 или .title3, design: .serif).weight(.bold)` | SF Pro only everywhere; Inter |
| **Подзаголовок** | `.font(.subheadline)` · secondary/white opacity | Мелкий серый нечитаемый |
| **Акцент / pill / badge** | `Color.secondaryGold` `#F59E0B` | Life360 purple accents as brand |
| **Иконка в двери** | SF Symbol `.title` / `.title2` semibold в круге frost | Чужие PNG логотипы конкурентов |
| **Отступы** | `Spacing.m/l/xl` (16/24/32); horizontal `Spacing.l` | Магические 13/17pt |
| **Кнопка min** | `Size.buttonMinHeight` 44pt | Мелкие тапы |
| **Splash** | Full-bleed ALADDIN brand + **WORDMARK_V2** по центру (`Resources/BrandAssets/ALADDIN_AI_V2_Logo/`) | Purple splash + лого Life360 |
| **Карта** | Dark map + pin glow + FAB glass **как композиция Life360**; chrome = Storm glass | Пиксельный клон Life360 chrome colors |

### Max-UI Life360 — что именно копируем

| Берём (layout / meaning) | Не берём |
|--------------------------|----------|
| Full-bleed map + bottom sheet + **4-tab bar в хабе** | Purple brand; второй Map hub вне «Где семья» |
| FAB stack (settings / layers / locate) | Purple FAB brand |
| Member sheet: имя · «Рядом с» · время · battery | Driving locks / trip teaser как ship feature |
| Places chips Дом/Школа/Работа | Lost Pet live pins без партнёра |
| Empty 3D + CTA | Offers marketing tab |
| Map type Авто/Улицы/Спутник | Системные Settings.app wireframes |
| Hold+countdown SOS | Tap-once SOS + fake dispatch |
| Calendar month + event @ place (решение D) | Multi-circle Friends social |

**Правило красоты:** если экран «временно уродливый» — задача **не done**. Цель волны = App Store–уровень в Storm glass.

---

## 3. Решения владельца (замок 2026-11-04) — одна интерпретация

| # | Тема | Решение |
|---|------|---------|
| 1 | Spy-copy | **Функция «где семья» — ДА.** Тексты «следим весь день» — **НЕТ**. Glossary: «Где сейчас» · «На связи» · «Последняя точка». |
| 2 | IA | Один map hub в «Где семья»; **4 таба Life360 внутри хаба — ДА** (гибрид). Удобный = вход. |
| 3 | Dispatch | Empty + «В скором времени» + 112/контакты. **Запрет:** «помощь уже едет». Live = только партнёр+GO (P4+). |
| 4 | Скорость | Badge с Core Location (+ честный picker GPS/ГЛОНАСС — см. §13.5). |
| 5 | Driving reports | **Не «выдумка P4»:** UI уже есть (`DrivingReportsModal` + agent). Wave B: **включить в таб Вождение**, добить данные; hard-brake ML auto = later. |
| 6 | Flight / multi-circle / ID theft | **Не берём.** |
| 7 | Calendar / Events | **D:** полноценный **месяц-календарь** как Life360 + **EventKit** сразу (L-P3-25). Без RSVP/соцсети/multi-circle. |
| 8 | Lost Pet | UI-строка → sheet «скоро» (L-P3-26). Без fake pins. Live layer = P4+партнёр. |
| 9 | Splash | ALADDIN wordmark V2, не purple. |
| 10 | Loc | Каждый новый экран RU+EN; verify LocManager; нет сырых ключей. |
| 11 | Permissions | Свой sheet + «Открыть Настройки»; не клон Settings.app. |
| 12 | Tile/метки | Empty «скоро», без fake pin. |
| 13 | Дубли скринов | Один backlog id. |
| 14 | Who Calls reverse / Live Caller ID / full AV / Android lock | SKIP (Kaspersky §2). |
| 15 | Прод | Ноль mock/sfm_mock на family · map · parental · antifake · crash/Tile/evac. |

### Calendar D — спецификация (чтобы не двоилось с «empty only»)

1. Экран **Семейный календарь** (вход: sheet Места / Family / Places Save teaser).  
2. **Вид месяц** (как L48 visual density) + список ближайших под календарём.  
3. Empty: «Пока ничего не запланировано» + CTA создать.  
4. Форма события: название · дата/время · место (чип Дом/Школа/Работа или координата) · участники семьи · напоминание.  
5. **EventKit:** опция «Добавить в Календарь iOS» (переиспользовать паттерн `FamilyHabitEventKitSync`).  
6. Синхрон между членами семьи: family API если есть endpoint; иначе v1 локально+EventKit с честным copy «на этом iPhone / в Календаре» — **не** врать «все видят онлайн», пока нет API.  
7. **Не:** друзья вне семьи, RSVP, multi-circle events.

---

## 4. Волны A → B → C (единый порядок ship)

| Волна | Источник аудита | Содержание | Ship без mock? |
|-------|-----------------|------------|----------------|
| **A** | Kaspersky P0–P2 + Life360 Family polish | Call Directory гайд · lists empty · Анти-Баннер · Дом/сеть empty · VK empty · child overview · last-point карта · Full/Limited · invite chips · splash brand · anti-spy copy | Да при GATES |
| **B** | Life360 P3 map | Live Map · Always Allow · max-UI L42 · member sheet · Places · Day Journal · Privacy Zone · share link · Routes · map type · **Calendar D** · speed badge опция | Да при Always Allow + real points |
| **C** | Life360 + Kaspersky C | Crash honesty · SOS hold · Tile empty · Pet «скоро» · эвакуатор «скоро» | Да только empty **или** live partner |

**Не путать:** фундамент карты начинается в A (last-point); **live** = B.

---

## 5. Инвентарь скринов (пронумеровано)

| Набор | Id | Кол-во JPG на диске | Индекс | Детали UI/тексты |
|-------|-----|---------------------|--------|------------------|
| Kaspersky Who Calls + Safe Kids | **S01–S60** | **60** `photo_542510711341286*.jpg` | [`KASPERSKY_S01_S60_FILE_INDEX.txt`](KASPERSKY_S01_S60_FILE_INDEX.txt) | Карточки в Kaspersky MD §3–§4 |
| Life360 | **L01–L90** | **90** `photo_542684027874568*.jpg` | [`LIFE360_L01_L90_FILE_INDEX.txt`](LIFE360_L01_L90_FILE_INDEX.txt) | `_partial_L01_L30.md` · `_partial_L31_L60.md` · `_partial_L61_L90.md` + сводка в Life360 MD §4 |

**Правило открытия скрина:**  
`id → FILE_INDEX → полный path в Cursor assets`.  
**Не** доверять автоподписи Cursor «L01» на произвольном JPG.

**Переименование файлов на диске:** не требуется для работы. Если владелец захочет копии `L01.jpg`… — отдельный GO (диск). Сейчас SSOT = FILE_INDEX.

**Аудит закрыт?** Да: каждый id имеет вердикт TAKE/ADAPT/SKIP (или dup→канон). Сводка Life360 ≈30 TAKE / ≈34 ADAPT / ≈26 SKIP+dup.

---

## 6. Backlog единый (не два списка в голове)

### Из Kaspersky (P0–P2) — не дублировать здесь подробно

Смотри Kaspersky MD §8. Короче: Call Directory stepper · sync · parental categories · Анти-Баннер · Дом/сеть · map last-point · VK empty · loc · FIG-01…22.

### Life360-добавки (P3) — Wave B/C

| ID | Задача | Дизайн-якорь | Evidence |
|----|--------|--------------|----------|
| L-P3-01 | WhereIsPhone max-UI + **4-tab bar** | SimpleHome + L42 | L42, L91–97 |
| L-P3-01b | Tab **Вождение** → существующий `DrivingReportsModal` (+ badge скорости) | Analytics modal | L52; код ViewModels/Driving* |
| L-P3-01c | Tab Подписка → Tariffs ALADDIN | | L56, L96 |
| L-P3-01d | **Sheet 5-иконок + scroll-spy** (люди·лапа·ключ·дом·события) | Life360 strip | **L91–L97** |
| L-P3-01e | Soft Family paywall после N дней карты (dismissible) | Soft review pattern | **L96** |
| L-P3-01f | Interiors Add person / Places / Events / Pet / Drive / Safety (см. §13.6) | | L91–L118 |
| L-P3-02 | Member sheet | serif title + gold meta | L58, L83 |
| L-P3-03 | Map type sheet | | L25, L81 |
| L-P3-04 | Places chips + radius | | L47, L59 |
| L-P3-05 | Always Allow pre-prompt | | L31, L70, L72 |
| L-P3-06 | Day Journal + playback | | L87 |
| L-P3-07 | Privacy Zone («Тихая зона») | | L85 |
| L-P3-08 | Share link + duration | | L86 |
| L-P3-09 | Routes → MapKit | | L61–62 |
| L-P3-10 | Pin preview «Как вам вид?» | | L13 |
| L-P3-11 | Loc RU+EN + verify | | rule megafile |
| L-P3-12…17 | Family Full/Limited · chips · invite · rename · inbox empty | | L79, L82… |
| L-P3-18 | Splash WORDMARK_V2 | BrandAssets | L78 |
| L-P3-19…22 | Crash · tip · SOS hold · emergency contacts | | L54, L36… |
| L-P3-23 | Tile empty «скоро» | | L45, L64 |
| L-P3-24 | Evac empty «скоро» | | — |
| L-P3-25 | **Calendar month + EventKit (решение D)** | L48–L51 + SimpleHome type | §3 |
| L-P3-26 | Lost Pet row «скоро» | | L25, L81 |
| L-P3-27 | Anti-spy glossary RU+EN | | §3.1 |
| L-P3-28 | GPS speed badge | | после live Map |

### P4 (не сейчас)

Full Driving weekly · multi-circle Friends · Flight · ID theft · live Pet layer · live roadside dispatch · Offers tab.

---

## 7. Текст / Loc (канон) — обязательно по каждой задаче

### 7.0 Правила (без двойных трактовок)

1. **До кода UI** — добавить ключ в `Resources/Localization/ru.lproj/Localizable.strings` **и** `en.lproj/Localizable.strings` с **готовым человеческим** текстом.  
2. В Swift только `localizationManager.localized("key")` — **никогда** не показывать сырой ключ пользователю.  
3. Dict в `LocalizationManager.swift` — только точечный StrReplace (rule `localization-megafile-safe`).  
4. После правок: `./scripts/verify_localization_manager_integrity.sh` → OK.  
5. Device QA: язык RU и EN на дверях Удобного + карта + empty — **нет** `where_phone_*` / `map_*` на экране.  
6. Запрет: `следим весь день` · `шпионим` · `track all day` · `spy on` · `помощь уже едет` (без партнёра).  
7. Тон = двери Удобного: коротко, спокойно, польза семье.

**Проверка «всё ли предусмотрено» (честно):**  
- Правила + пакеты + glossary черновиков = **да в плане**.  
- Уже в приложении: двери `pay_pains_door_*`, часть `where_phone_*` (last-point).  
- Новые Wave B/C строки (member sheet, Always Allow, Calendar, Pet «скоро», SOS…) — **черновик ниже**; агент **вставляет в strings до UI**, потом может уточнить тон с владельцем.

### 7.1 Уже есть (не ломать смысл; можно polish)

| Key | RU сейчас | EN сейчас |
|-----|-----------|-----------|
| `pay_pains_door_check_title` | Проверить | (см. en.strings) |
| `pay_pains_door_check_subtitle` | Звонок, сообщение или видео | |
| `pay_pains_door_child_title` | Ребёнок | |
| `pay_pains_door_child_subtitle` | Сайты, лимит и пауза | |
| `pay_pains_door_where_title` | Где семья | Where they are |
| `pay_pains_door_where_subtitle` | Карта | Map |
| `where_phone_map_title` | Карта | Map |
| `where_phone_map_card_title` | Последняя точка | Last point |
| `where_phone_map_empty` | (см. strings) | No point yet… |

### 7.2 Glossary — **вписано в Localizable.strings** (2026-11-04)

Статус: ключи ниже есть в `Resources/Localization/{ru,en}.lproj/Localizable.strings` (+ `map_tab_*`, `map_soon_driving_*`).  
При UI — только `localized("…")`. Новые ключи — тем же правилом.

Формат: `key` · RU · EN. Не spy. Простой язык.

#### Пакет `map_live_*` (Wave B)

| key | RU | EN |
|-----|----|----|
| `map_live_sheet_circle` | Семья | Family |
| `map_live_sheet_places` | Места | Places |
| `map_live_sheet_help` | Помощь | Help |
| `map_live_sheet_tags` | Метки | Tags |
| `map_live_last_seen` | Был(а) здесь · %@ | Last seen · %@ |
| `map_live_near_place` | Рядом с «%@» | Near “%@” |
| `map_live_battery` | Заряд %d%% | Battery %d%% |
| `map_live_updating` | Карта обновляется | Map updating |
| `map_live_no_signal` | Пока нет сигнала | No signal yet |
| `map_live_speed_badge` | ≈ %d км/ч | ≈ %d km/h |
| `map_type_title` | Тип карты | Map type |
| `map_type_auto` | Авто | Auto |
| `map_type_street` | Улицы | Street |
| `map_type_satellite` | Спутник | Satellite |

#### Пакет `map_perm_*` (Always Allow)

| key | RU | EN |
|-----|----|----|
| `map_perm_always_title` | Разрешите «Всегда» | Allow “Always” |
| `map_perm_always_body` | Так карта семьи обновляется, когда приложение закрыто. Мы не следим «весь день» в рекламе — только чтобы вы видели, где телефоны семьи. | So the family map can update when the app is closed. We ask for location to show where family phones are — not to spy. |
| `map_perm_always_cta` | Продолжить | Continue |
| `map_perm_open_settings` | Открыть Настройки | Open Settings |
| `map_perm_precise_hint` | Включите также «Точные» места | Also turn on Precise Location |

#### Пакет `map_member_*`

| key | RU | EN |
|-----|----|----|
| `map_member_save_place` | Сохранить место | Save place |
| `map_member_directions` | Маршрут | Directions |
| `map_member_share` | Поделиться местом | Share location |
| `map_member_quiet_zone` | Тихая зона | Quiet zone |

#### Пакет `map_journal_*` / `map_share_*` / `map_privacy_*`

| key | RU | EN |
|-----|----|----|
| `map_journal_title` | История за сегодня | Today’s history |
| `map_journal_empty` | Пока нет перемещений за сегодня | No moves today yet |
| `map_share_link_title` | Ссылка на место | Location link |
| `map_share_duration` | Действует | Expires |
| `map_privacy_zone_title` | Тихая зона | Quiet zone |
| `map_privacy_zone_hint` | В этой зоне место семье не показывается | Location is hidden from family in this zone |

#### Пакет `family_cal_*` (Calendar D)

| key | RU | EN |
|-----|----|----|
| `family_cal_title` | Семейный календарь | Family calendar |
| `family_cal_empty` | Пока ничего не запланировано | Nothing planned yet |
| `family_cal_add` | Добавить событие | Add event |
| `family_cal_place` | Место | Place |
| `family_cal_to_ios` | В Календарь iPhone | Add to iPhone Calendar |
| `family_cal_local_only` | Пока видно на этом iPhone. Общий онлайн — позже. | Visible on this iPhone for now. Shared online later. |

#### Пакет `map_soon_*` (Pet / Tile / Evac)

| key | RU | EN |
|-----|----|----|
| `map_soon_pet_title` | Питомцы рядом | Pets nearby |
| `map_soon_pet_body` | В скором времени. Без карты питомцев, пока нет партнёра. | Coming soon. No pet map until a partner is live. |
| `map_soon_tile_title` | Метки | Tags |
| `map_soon_tile_body` | В скором времени. Подключим метки честно — без фейковых точек. | Coming soon. Tags will connect for real — no fake pins. |
| `map_soon_evac_title` | Помощь на дороге | Roadside help |
| `map_soon_evac_body` | В скором времени. Сейчас: 112 и ваши контакты. | Coming soon. For now: 112 and your contacts. |
| `map_soon_ok` | Понятно | Got it |

#### Пакет `sos_*` / `crash_*` (Wave C)

| key | RU | EN |
|-----|----|----|
| `sos_hold_hint` | Удерживайте для SOS | Hold for SOS |
| `sos_countdown` | Отмена · %d | Cancel · %d |
| `sos_sent_family` | Семья получила сигнал | Family got the alert |
| `crash_confirm_title` | Это авария? | Was this a crash? |
| `crash_confirm_yes` | Да, нужна помощь | Yes, need help |
| `crash_confirm_no` | Нет, всё в порядке | No, I’m fine |
| `crash_limits_body` | Мы зовём семью. Вызов эвакуатора появится, когда подключим партнёра. | We alert your family. Roadside dispatch comes when a partner is live. |

#### Пакет Kaspersky A (кратко; полные — Kaspersky MD §16)

`calldir_*` · `child_overview_*` · `adblock_*` · `home_net_*` · `vk_*` · `safesearch_*` · `content_cat_*` — те же правила RU+EN до UI.

### 7.3 Definition of Done по переводу (на задачу)

- [ ] keys в ru + en strings  
- [ ] UI только через `localized`  
- [ ] verify script OK  
- [ ] нет запрещённых фраз  
- [ ] QA RU + EN: нет сырых ключей  

---

## 8. Figma / ассеты — полный канон для Figma-ML

**Отдельный файл промптов по каждой странице (копипаст владельцу):**  
[`FIGMA_FAMILY_SAFETY_ML_PROMPTS.md`](FIGMA_FAMILY_SAFETY_ML_PROMPTS.md)

| Набор | Id | Статус | Референс JPG |
|-------|-----|--------|----------------|
| Life360 **приоритет** | FIG-L01…L24 | Спека+промпты в FIGMA_…_PROMPTS §3 | `screenshots_life360/Lxx.jpg` |
| Kaspersky | FIG-01…22 | §4 того же файла + Kaspersky MD §17 | `screenshots_kaspersky/Sxx.jpg` |
| Onboarding OB_* | — | **READ-ONLY** | не трогать |
| Logo | WORDMARK_V2 | **В репо** BrandAssets | — |

### Когда в пайплайне?

- **Можно последними:** 3D/empty иллюстрации, если код уже на SF Symbol + glass.  
- **Лучше до Device QA красоты:** FIG-L15 (4-tab) · L01 pin · L03 FAB · L10 SOS.  
- Код Wave B **не блокировать** ожиданием всего Figma.

### Стиль
Storm glass + `#F59E0B`; композиция **max Life360**; **не** purple brand; **не** Kaspersky green logo.

### Список FIG-L (имена файлов export)

| ID | Export name | Evidence L* |
|----|-------------|-------------|
| FIG-L01 | `FIG-L01_MapPinBattery` | L42, L13, L83 |
| FIG-L02 | `FIG-L02_LastSeenBubble` | L58, L83 |
| FIG-L03 | `FIG-L03_FABStack` | L42 |
| FIG-L04 | `FIG-L04_MemberSheetHero` | L83, L26 |
| FIG-L05 | `FIG-L05_EmptyMailbox` | L23, L76 |
| FIG-L06 | `FIG-L06_AccessCards` | L79, L21 |
| FIG-L07 | `FIG-L07_ChipsRoles` | L08, L82, L14 |
| FIG-L08 | `FIG-L08_GeofenceCircle` | L59, L85 |
| FIG-L09 | `FIG-L09_DayJournal` | L87 |
| FIG-L10 | `FIG-L10_SOSHold` | L36–37, L40 |
| FIG-L11 | `FIG-L11_CrashTipRow` | L69, L54 |
| FIG-L12 | `FIG-L12_MapTypeThumbs` | L81, L25 |
| FIG-L13 | `FIG-L13_ShareLinkCard` | L86, L28 |
| FIG-L14 | `FIG-L14_Splash` | L78 + BrandAssets |
| FIG-L15 | `FIG-L15_HubTabBar` | L42 tabs |
| FIG-L16 | `FIG-L16_FamilyCalendar` | L48–51 |
| FIG-L17 | `FIG-L17_PlacesChips` | L47, L19 |
| FIG-L18 | `FIG-L18_AlwaysAllow` | L31, L70, L72 |
| FIG-L19 | `FIG-L19_TagsSoon` | L45, L64 |
| FIG-L20 | `FIG-L20_EvacSoon` | C |
| FIG-L21 | `FIG-L21_PetSoonRow` | L81 |
| FIG-L22 | `FIG-L22_DrivingSoon` | L52, L71 |
| FIG-L23 | `FIG-L23_PinPreview` | L13 |
| FIG-L24 | `FIG-L24_RoutesSheet` | L61–62 |
| FIG-L25 | `FIG-L25_SheetSectionChips` | L91–97 |
| FIG-L26 | `FIG-L26_FamilySoftPaywall` | L96 |
| FIG-L27/28 | Pets/Items soon empties | L92, L94 |
| FIG-L29…33 | Pet wizard · Drive weekly · Safety · Places list · Create event | L98–L118 |
| FIG-L34 | **Location sheet FULL** (banner+5chips+sections+4tab) | L91–97 |
| FIG-L35 | Role modal | L98–99 |
| FIG-L36 | Subscription tab ALADDIN | L118 |

FIG-01…22 — см. FIGMA prompts §4 (reuse FIG-L где смысл тот же).

---

## 9. Честная готовность (что «100%», что нет)

| Блок | Готовность | Комментарий |
|------|------------|-------------|
| Аудит 60 Kaspersky | ✅ | S01–S60 + вердикты |
| Аудит 90 Life360 | ✅ | L01–L90 + partials |
| FILE_INDEX оба набора | ✅ | S + L txt |
| Единый master (этот файл) | ✅ | v1.1 + §16 красота/дыры |
| Дизайн-токены SimpleHome зафиксированы | ✅ | §2 |
| Решения владельца (SKIP/гибрид/Calendar D) | ✅ | §3 |
| Keys §7.2 в Localizable.strings RU+EN | ✅ | 2026-11-04 (+ map_tab_*, driving soon) |
| JPG копии L01…L90 / S01…S60 | ✅ | `screenshots_life360/` · `screenshots_kaspersky/` |
| FIG-L01…24 список + ML промпты | ✅ | `FIGMA_FAMILY_SAFETY_ML_PROMPTS.md` |
| Пиксельные размеры «как JPG» на каждый слой | ⚠️ | Брать с Lxx.jpg + partial при задаче |
| Figma **нарисовано** + xcassets | ❌ | Ждёт **GO Figma** (можно last для 3D) |
| Swift Wave A/B/C | ✅ код remainder (без Figma/P4) | Ждёт `GO на сборку` |
| Партнёры Tile/evac/dispatch | ❌ | Empty до договора |
| Device QA / Simulator | ❌ | Только после «GO на сборку» |

**Вывод для владельца:** docs-канон для другой ML **достаточен, чтобы начать работу без двойных трактовок**. «Оба аудита + master готовы как план». **Не** значит «приложение уже 100% в Store».

---

## 10. GATES перед словом «готово» (любая волна)

| Id | Критерий | Evidence |
|----|----------|----------|
| G1 | Один Map hub; 4-tab **внутри** WhereIsPhone OK | Нет второго map вне «Где семья»; 4-tab bar в хабе есть |
| G2 | Нет spy-copy | Grep запрещённых фраз RU/EN |
| G3 | Нет fake dispatch / fake Tile pins | UI copy + нет mock API |
| G4 | Loc integrity OK | `verify_localization_manager_integrity.sh` |
| G5 | Always Allow / Critical — свой sheet + Settings link | Код permission |
| G6 | Calendar D: месяц + EventKit; нет лжи «все онлайн» без API | UI + EventKit flag |
| G7 | Дизайн = SimpleHome type + stormGlassCard | Code review vs §2 |
| G8 | Нет bot/secrets в iOS commit | staged paths check |

---

## 11. Как владельцу передать другой ML + полный промпт

### 11.1 Что сказать / вставить владельцу

1. Workspace = корень `ALADDIN_iOS`.  
2. Новый чат → вставить **§11.2 целиком** (не старые черновики из чата).  
3. Одна фраза GO, например:  
   - `GO Figma — FIG-L34 + L15 + L25 + L01 + L03` (дизайн max Life360)  
   - `GO код Wave B — L-P3-01 + 01d (4-tab + 5 chips scroll-spy) + loc`  
   - `GO код Wave B — Driving tab → DrivingReportsModal + Safety chrome`  
4. Не «сделай всё A+B+C сразу».  
5. Сборка только: `GO на сборку`.

**Docs дописывать перед передачей не обязательно** (канон v1.3). Исполнение (Figma/Swift) = после GO.

### 11.2 Промпт (копировать другой ML) — актуальный v1.3

```text
Роль: principal iOS + product UX ALADDIN (15+ лет). Mech Pilot: владелец даёт GO; ты — минимальный diff + evidence.

ОБЯЗАТЕЛЬНО СНАЧАЛА:
1) git rev-parse --show-toplevel → …/ALADDIN_iOS; ветка master.
2) Прочитай ЦЕЛИКОМ:
   docs/competitors/FAMILY_SAFETY_KASPERSKY_LIFE360_MASTER_PLAN.md
   (версия ≥1.4 — §13.4–13.6 + §17 обязательны)
3) По GO владельца открой:
   - Код/Life360 → LIFE360_SCREEN_AUDIT_ACTION_PLAN.md + _partial_L*.md
   - Figma → docs/competitors/FIGMA_FAMILY_SAFETY_ML_PROMPTS.md (§1 + нужный FIG-L*)
   - Kaspersky Wave A → KASPERSKY_…60…md + KASPERSKY_S01_S60_FILE_INDEX.txt
4) JPG: предпочтительно docs/competitors/screenshots_life360/Lxx.jpg
   (или FILE_INDEX → photo_*.jpg). Soft-label Cursor «L01» игнорируй.

НАВИГАЦИЯ — master §13 / §13.6 (НЕ старый запрет 4 табов):
- Удобный = SimpleHomeScreen: 3 двери + Меню (вход в приложение).
- «Где семья» → WhereIsPhone hub = ЕДИНСТВЕННЫЙ Map hub.
- Внутри хаба ОБЯЗАТЕЛЬНО: bottom 4 таба Life360-style
  Местоположение | Вождение | Безопасность | Подписка.
- На Местоположение: sheet + sticky 5 chips (люди·лапа·ключ·дом·события)
  + scroll-spy (тап = прыжок; скролл = авто-highlight).
- X закрывает хаб → Удобный.
- «Проверить» / «Ребёнок» = двери Удобного (Kaspersky A), не 4-tab.

ДИЗАЙН — master §2 + max-UI Life360:
- Storm mesh · stormGlassCard · gold #F59E0B
- serif title2/title3 bold как Удобный · subheadline
- Композиция/плотность как L91–L118; НЕ purple Life360 brand
- Figma: FIG-L01…L36; приоритет FIG-L34+L15+L25

LOC — master §7 (ключи уже в Localizable.strings RU+EN):
- UI только localized(); сырых ключей = FAIL
- verify_localization_manager_integrity.sh после правок LocManager
- Запрет spy-copy / «помощь уже едет» без партнёра

ФУНКЦИИ (замок v1.3):
- Calendar D = месяц + EventKit
- Вождение tab → существующий DrivingReportsModal (не вечный «скоро»; данные честно)
- Pet: профиль+рутины ДЕЛАЕМ; live GPS/маячок железа = скоро
- Items/Tile/evac = скоро empty; Places/Events/Invite = полные interiors §13.6
- Soft Family paywall после N дней (L-P3-01e)
- no mock / no fake pins

ПОРЯДОК:
GATES → (если нужно) loc → Swift или Figma по GO → verify → отчёт было/стало → спросить GO на сборку.
Не xcodebuild без «GO на сборку». Не commit без просьбы. Не bot/.env. Не OB_* Figma.
iOS commit только master.

Сейчас выполни ТОЛЬКО то, что владелец указал в GO после этого промпта.
```

---

## 12. Связанные файлы

| Файл | Роль |
|------|------|
| [`FAMILY_SAFETY_KASPERSKY_LIFE360_MASTER_PLAN.md`](FAMILY_SAFETY_KASPERSKY_LIFE360_MASTER_PLAN.md) | **Этот** — единый план |
| [`FIGMA_FAMILY_SAFETY_ML_PROMPTS.md`](FIGMA_FAMILY_SAFETY_ML_PROMPTS.md) | Промпты Figma по FIG-L / FIG-* |
| [`KASPERSKY_WHOCALLS_SAFEKIDS_60_SCREEN_AUDIT_ACTION_PLAN.md`](KASPERSKY_WHOCALLS_SAFEKIDS_60_SCREEN_AUDIT_ACTION_PLAN.md) | Audit этап 1 |
| [`LIFE360_SCREEN_AUDIT_ACTION_PLAN.md`](LIFE360_SCREEN_AUDIT_ACTION_PLAN.md) | Audit этап 2 + §3b |
| [`KASPERSKY_S01_S60_FILE_INDEX.txt`](KASPERSKY_S01_S60_FILE_INDEX.txt) | S→JPG |
| [`LIFE360_L01_L90_FILE_INDEX.txt`](LIFE360_L01_L90_FILE_INDEX.txt) | L→JPG |
| `screenshots_life360/Lxx.jpg` | Копии референсов Life360 |
| `screenshots_kaspersky/Sxx.jpg` | Копии референсов Kaspersky |
| `_partial_L01_L30.md` … `_partial_L61_L90.md` | Полные карточки L* |
| `Screens/SimpleHomeScreen.swift` | Эталон шрифта/карточек + навигация дверей |
| `Screens/WhereIsPhoneScreen.swift` | Единственный Map hub |
| `Screens/FamilyModals.swift` → `FamilyModalBaseView` | Заголовок + **xmark закрыть sheet** |
| `docs/ML_SYSTEM_START_HERE.md` | Роутер → этот master |

---

## 13. Навигация: сейчас · Life360 · будет (клики)

### 13.1 Сейчас — Удобный режим (`SimpleHomeScreen`)

```text
Удобный режим (Storm mesh, navigationBarHidden)
├── Полоса семьи → tap → Family / добавить
├── Дверь «Проверить» → Antifake / Call Directory flow
├── Дверь «Ребёнок» → sheet child door (пауза, минуты, bedtime…)
├── Дверь «Где семья» → showWherePhone=true
│     └── sheet WhereIsPhoneScreen
│           ├── FamilyModalBaseView title «Карта»
│           ├── справа xmark.circle.fill → isPresented=false (ЗАКРЫТЬ, не «стек Назад»)
│           ├── карта + last-point / share
│           └── sheet Места → GeofencesSettingsModal
├── Ряд «AI друзья» / Voice
└── «Меню» / «Все разделы» → sheet → NavigationManager на полные экраны
      (после возврата на simpleHome можно снова открыть меню)
```

**Кнопка «назад»:** на sheet карты = **закрыть (X)**, возврат на Удобный.  
Полные разделы из Меню = `NavigationManager` goBack к simpleHome (и опционально снова Меню).

### 13.2 Как у Life360 (референс, не копируем IA)

```text
Root TabBar (4): Местоположение | Вождение | Безопасность | Подписка
Местоположение = full-bleed map
├── FAB (слои, locate, inbox…)
├── bottom sheet: список круга / member
├── tap member → member sheet
├── Places / Drive / Help = другие табы или вложенные sheets
└── системные permission = Settings.app
```

### 13.3 Будет — клик-карта ALADDIN (гибрид: 4 таба **внутри** «Где семья»)

| Клик пользователя | Куда код | Что открывается |
|-------------------|----------|-----------------|
| Удобный → «Где семья» | `showWherePhone = true` | Хаб `WhereIsPhoneScreen` + **4-tab bar** |
| Tab **Местоположение** | map root в хабе | Full-bleed map · FAB · member sheets · Places · Calendar |
| Tab **Вождение** | `DrivingReportsModal` / pane | Существующий UI отчётов + speed; не вечный «скоро» |
| Tab **Безопасность** | safety pane | Crash · SOS · Tile/evac «скоро» |
| Tab **Подписка** | tariffs | `10_TariffsScreen` / family paywall ALADDIN |
| X / закрыть хаб | `isPresented = false` | Удобный |
| FAB слои | sheet map type | Авто/Улицы/Спутник + Pet «скоро» |
| FAB locate | center on me/family | MapKit region |
| Pull sheet / список семьи | detent + list | аватарки членов |
| Tap член | member sheet | L83 · battery · speed · Save place |
| Места / календарь | Places + Calendar D | chips + месяц + EventKit |
| Always Allow | pre-prompt sheet | CTA → Open Settings |
| Удобный → «Проверить» | Antifake | Kaspersky A |
| Удобный → «Ребёнок» | child door | Kaspersky A |

**Логика «чтобы работало»:**  
точки семьи → API/local board уже в WhereIsPhone → Wave B добавляет live updates + Always Allow;  
Places → существующий geofence;  
Calendar → новый экран + EventKit;  
Crash/SOS → семья notify; dispatch/Tile — empty до партнёра.

### 13.4 Карта для пользователя: где · что · зачем (интуиция)

**Принцип владельца (замок):** красиво · просто · понятно.  
**Ничего не убираем** из согласованного гибрида (4 таба, map, sheets, Calendar, soon-экраны, Kaspersky-двери).  
Упрощаем **понимание**, не вырезаем функции. Каждый блок отвечает: *что это? зачем мне? что будет, если нажму?*

#### Удобный режим (вход)

| Где на экране | Что видит | Зачем | Нажал → |
|---------------|-----------|-------|---------|
| Верх | Полоса семьи | Кто в семье | Family / добавить |
| Карточка 1 | «Проверить» | Безопасность звонков/ссылок | Antifake + Call Directory |
| Карточка 2 | «Ребёнок» | Правила и пауза | Child sheet |
| Карточка 3 | «Где семья» | Где телефоны сейчас | Хаб карты (ниже) |
| Низ | Меню | Все остальные разделы | Полные экраны |

#### Хаб «Где семья» — общий каркас

| Зона | Расположение | Зачем | Интуиция |
|------|--------------|-------|----------|
| Карта | Почти весь экран | Видеть людей на карте | Как Life360: открыл — сразу карта |
| X | Справа сверху | Выйти на Удобный | «Закрыть», не потеряться |
| FAB | Справа стопкой | Слои / я / почта / настройки | Знакомые круглые кнопки |
| Sheet снизу | Тянется пальцем | Список семьи / детали | Потянул — увидел людей |
| **4 таба** | Самый низ | Переключение миров хаба | Как Life360: одно место — четыре ясные зоны |

#### Таб 1 — Местоположение (главный)

| Элемент | Где | Что / зачем | Нажал → |
|---------|-----|-------------|---------|
| Пины семьи | На карте | Кто где | Карточка человека |
| Last-seen / battery | У пина / в карточке | Насколько свежо и заряд | Понял без догадок |
| Speed badge | В карточке (если GPS дал) | Скорость сейчас | Не «отчёт за неделю» |
| Список в sheet | Низ | Все члены | Выбор человека |
| Места (Дом/Школа) | Sheet / chips | Зоны «пришёл/ушёл» | Редактор места |
| Календарь | Из Мест / CTA | Планы семьи у места | Месяц + событие |
| Share link | Из карточки | Временная ссылка | Duration + отправить |
| Тихая зона | Из карточки | Скрыть место в зоне | Слайдер |
| История дня | Sheet / entry | Куда ходили сегодня | Journal scrub |
| Маршрут | Из места/карточки | Как доехать | MapKit / Карты |
| Тип карты | FAB слои | Авто/Улицы/Спутник | Thumbnails |
| Pet «скоро» | В типе карты | Честно позже | Sheet «скоро» — **не убираем строку** |

#### Таб 2 — Вождение

| Элемент | Зачем | Интуиция |
|---------|-------|----------|
| Сам таб | Привычная зона Life360 | Не прячем — пользователь ищет «Вождение» здесь |
| Speed / «скоро отчёты» | Честно: скорость есть, weekly later | Пустой красивый экран + понятный текст, **не удаляем таб** |

#### Таб 3 — Безопасность

| Элемент | Зачем | Нажал → |
|---------|-------|---------|
| Crash «это авария?» | Подтвердить ложное/реальное | Семье сигнал / отмена |
| SOS hold | Позвать семью | Удержание + countdown |
| Метки «скоро» | Будущие трекеры | Empty — строка остаётся |
| Помощь на дороге «скоро» | Честно до партнёра | Empty + 112 — **не fake «едет»** |

#### Таб 4 — Подписка

| Элемент | Зачем | Нажал → |
|---------|-------|---------|
| Тарифы ALADDIN | Понять, что в Family | `10_TariffsScreen` / paywall |

#### Двери Kaspersky (не внутри 4 табов)

| Дверь | Зачем пользователю | Логика |
|-------|-------------------|--------|
| Проверить | «Это опасный звонок/ссылка?» | Отдельно от карты — другая задача мозга |
| Ребёнок | «Ограничить интернет / пауза» | Отдельно — родительский контроль |

**Почему так интуитивно:** карта = «где», Проверить = «опасно ли», Ребёнок = «правила» — три разные потребности, три двери. Внутри «где» — четыре таба Life360, которые пользователь уже узнаёт.

#### Правила ясности для ML (не ломать)

1. Подпись таба/кнопки = глагол или короткое существительное из loc (§7), не жаргон.  
2. Empty всегда с **одной** фразой «зачем это» + CTA или «скоро».  
3. Не прятать таб/строку «чтобы упростить» — упростить **текст и порядок**.  
4. Primary action на экране одна (крупная); вторичные — secondary.  
5. После каждого экрана в QA: «родитель 60+ поймёт за 3 секунды?» — если нет, правим copy/иерархию, не вырезаем фичу.

### 13.5 Уточнения владельца 2026-11-04 (Driving · позиционирование · 5 иконок · paywall)

Референсы: `screenshots_life360/L91_*.jpg` … `L97_*.jpg` (+ FILE_INDEX L91–L97).

#### A. Почему писали «отчёты скоро» — и что есть на самом деле

| Слой | Факт в репо |
|------|-------------|
| UI | **`DrivingReportsModal`** + `DrivingReportsViewModel` уже есть (вход сейчас: Analytics) |
| Backend/agent | `driving_reports_agent` / router — каркас + метрики; в UI `loadReports` **отключён** (только `componentsAnalytics`, список поездок часто пустой) |
| Где семья сегодня | Last-point · geofence пришёл/ушёл · `WherePhoneTravel` минуты между зонами — **не** weekly hard-brake Life360 |
| Яндекс | Только **открыть точку** в Яндекс.Картах (`openInYandexMaps`) — **не** отдельный локатор вместо GPS |
| GPS/ГЛОНАСС/Galileo/BeiDou | `PositioningSystemService` + picker: **предпочтение UX/регион**; на iOS всё равно Core Location — **нельзя** «включить только ГЛОНАСС» (в коде прямо: no mock force) |

**Наилучшее решение (замок):**
1. Таб **Вождение** → открывает/встраивает **существующий** Driving Reports UI (не вечный empty «скоро»).  
2. Wave B: вернуть честную загрузку поездок / startTrip, если API жив; иначе empty «Пока нет поездок — включите доступ и поезжайте» (не fake метрики).  
3. Авто-сегментация hard brake / phone-use как у Life360 Gold — только когда continuous motion pipeline стабилен (можно P4 **улучшения**, не скрывать весь таб).  
4. Speed badge на карте = Core Location `speed` когда валиден.  
5. Picker систем позиционирования — оставить в Driving/Settings с честной сноской iOS.

#### B. Баннер / paywall «одна подписка на всю семью» спустя дни (L96)

Life360: после привыкания — timeline trial Gold.

**Наилучшее для ALADDIN:**
- **Да, делать soft sheet** (не блокирующий root): через **N календарных дней** активного «Где семья» (рекомендация N=3…5) **или** после 2-го члена семьи.  
- Copy: спокойствие семьи / Family тариф ALADDIN — **не** «Gold Life360», не purple brand.  
- Кнопки: «Попробовать» → Tariffs · «Может, позже» → dismiss + cooldown (как `PayPainsSoftReview`).  
- **Не** каждый запуск; max 1× / период.  
- Задача: **L-P3-01e**.

#### C. Полоса 5 иконок + scroll-spy (L91–L97) — в плане было слабо → **теперь канон**

Под заголовком «Семья …» на sheet Местоположение — **горизонтальные 5 chips** (sticky при скролле):

| # | Иконка | Раздел | Действие / interior |
|---|--------|--------|---------------------|
| 1 | Люди | Семья | Список членов · «Добавить человека» · карточка «Создать круг для родственников» → invite / Full-Limited (**не multi-circle friends product** — один Family + invite) |
| 2 | Лапа | Животные | Empty «скоро» + CTA disabled/«Добавить питомца» → sheet скоро (**заготовка есть**, без fake GPS pet) |
| 3 | Ключ | Элементы / маячки | Empty «скоро» + «Следите за важными вещами» → soon Tile (**заготовка**) |
| 4 | Дом | Места | «Управление местами» → существующий geofence / Places UI |
| 5 | Коробочка/календарь | Предстоящие события | Empty Calendar D + «Добавить событие» → форма месяца/EventKit |

**Поведение (как Life360 — обязательно):**
- Tap chip → scroll sheet к секции (+ highlight chip).  
- Scroll вниз → chip **автоматически** переключается (scroll-spy).  
- Секции **не убираем**; soon = честный empty с продолжением (sheet «скоро» / CTA).

Задача: **L-P3-01d** + Figma FIG-L25 (5-chip strip).

#### D. Открываются ли карточки «внутрь»? Предусмотрено ли?

| Карточка | Сейчас в плане | Нужно interior |
|----------|----------------|----------------|
| Добавить человека / круг | Invite + roles (Wave A) | Да — flow уже в Family; связать с chip 1 |
| Питомец | Soon L-P3-26 | Sheet скоро (достаточно до партнёра) |
| Маячки | Soon L-P3-23 | Sheet скоро |
| Места | GeofencesSettingsModal | Да — «Управление местами» |
| События | Calendar D L-P3-25 | Да — месяц + форма |
| Soft paywall | L-P3-01e | Timeline sheet L96-style |

**Пробел:** детальные JPG «что внутри Add person / Manage places / Add event» — владелец может прислать → допишем partials. Питомцы/маячки insides не критичны (soon).

#### E. Итог: всё ли предусмотрено?

| Было до L91–97 | Стало |
|----------------|-------|
| 4 таба + Places/Calendar в тексте | + **5-chip strip + scroll-spy** канон |
| Driving «P4 скоро» | **Переподключить существующий Driving Reports** |
| Paywall soft не описан | **L-P3-01e** после N дней |
| Яндекс как «вторая GPS» | Уточнено: только open-in-maps |
| Interiors | Люди/Места/События — да; лапа/ключ — soon stubs |

### 13.6 Interiors L98–L118 — полный разбор + куда кладём (канон)

**Скрины:** `screenshots_life360/L98.jpg`…`L118.jpg` + index.  
**Принцип:** нижние **4 таба всегда** в хабе «Где семья» (как Life360). Внутри Местоположение — **5 chips + scroll-spy**. Push/sheet для deep flows. Storm+gold, не purple. **Ничего не вырезаем** — soon там, где нет железа/партнёра.

#### Наилучшая схема навигации (замок)

```text
Удобный режим
└── «Где семья»  =  Family Hub (один контейнер)
    │
    ├── [BOTTOM TAB всегда виден]
    │     1 Местоположение │ 2 Вождение │ 3 Безопасность │ 4 Подписка
    │
    ├── TAB Местоположение
    │     Map full-bleed + FAB
    │     Sheet:
    │       · баннер «Добавить близких»
    │       · заголовок семьи
    │       · 5 CHIPS (sticky + scroll-spy): Люди | Лапа | Ключ | Дом | События
    │       · секции вниз по chips
    │     Push/Sheet interiors:
    │       Люди → роль (Мама/Папа/ребёнок) → invite
    │       Лапа → мастер питомца → рутины (≈ FamilyHabit) → success
    │              маячок железа → «скоро»
    │       Ключ → promo вещей → «скоро» (не магазин Tile)
    │       Дом → список Места (Дом/Школа/Работа/…) → geofence
    │       События → календарь → «Создать событие»
    │
    ├── TAB Вождение
    │     UI как weekly report Life360 → наш DrivingReportsModal (данные честно)
    │
    ├── TAB Безопасность
    │     Crash Detection toggle + Emergency contacts
    │     (SOS hold / evac soon — отсюда или из Помощи)
    │
    └── TAB Подписка
          Тарифы ALADDIN (месяц/год, сравнение Free/Family) — не Silver/Gold Life360
```

**Почему так лучше всего:** пользователь Life360 уже знает «4 таба снизу». У нас они живут **только в хабе семьи**, Удобный не ломаем. 5 chips = быстрый прыжок по длинному sheet без второго меню.

---

#### Потоки по скринам — что делать

##### 1) Люди / invite / роль (L98–L99 и chip 1)

| Life360 | ALADDIN |
|---------|---------|
| Роль Мама/Папа/ребёнок + Пропустить | **TAKE** — уже в плане invite (L14); modal Storm |
| «Создать круг для партнёра» | **ADAPT** → «Пригласить родственников в семью» (один Family, не multi-circle) |
| Добавить человека | Invite code / share |

**Loc:** `map_role_*`, `map_add_person`, `map_invite_banner_*` (уже в strings).  
**Дизайн:** pill list, X close, skip secondary.  
**Куда:** chip Люди · баннер сверху sheet.

##### 2) Питомцы — полный мастер (L103–L111 area)

Разбор Life360: фото → порода/цвет/вес/пол/ДР → рутины (прогулка/корм/лекарства) → кому напомнить → success «защищён» → привязка GPS/Pet Tag железа.

| Часть | Вердикт ALADDIN |
|-------|-----------------|
| Профиль питомца (имя, фото, порода…) | **ДЕЛАЕМ** Wave B — локальный/family profile |
| Рутины напоминаний | **ДЕЛАЕМ** — переиспользовать `FamilyHabitReminders` + EventKit |
| Success sheet | **ADAPT** copy без «глобальной Pet Network» |
| Маячок GPS/LTE / Pet Tag магазин | **Скоро** — sheet честный (нет железа) |
| Питомец pin на карте live | **Скоро** до партнёра |

**Не убираем** chip Лапа и мастер — даже если live track later.  
**Loc:** `pet_*` пакет в strings.  
**Figma:** FIG-L27 pets + routines hero.

##### 3) Вещи / маячки (ключ) 

Promo «Чтобы вещи не терялись» + Купить/Добавить Tile.

| ALADDIN | Честный empty + «скоро»; CTA «Понятно»; без fake shop |
| Loc | `items_promo_*` |

##### 4) Места (L112 area)

Список: Добавить новое · Дом · Школа · Работа · Зал · Магазин.

| ALADDIN | **TAKE UI** → уже geofence; расширить suggestions chips |
| Loc | `map_places_*` |
| Куда | chip Дом · «Управление местами» |

##### 5) События (create event form)

Поля: имя · место · Сегодня/Завтра/дата · начало/конец.

| ALADDIN | **Calendar D** форма 1:1 по смыслу + EventKit |
| Loc | `family_cal_*` |
| Куда | chip События |

##### 6) Вождение tab (L116)

Weekly report: периоды · 4 метрики · макс скорость · поездки · карточка члена (lock если нет данных).

| ALADDIN | **TAKE layout** → оболочка `DrivingReportsModal`; empty «Поездок пока нет» честно; lock = нет данных / не тариф — **без лжи** |
| Подключить | Tab Вождение = этот экран (не Analytics-only) |

##### 7) Безопасность tab (L117)

Crash Detection FREE toggle + Emergency contacts count.

| ALADDIN | **TAKE** Wave C crash toggle + contacts list (уже L-P3-19…22) |
| Copy | без «помощь едет» |

##### 8) Подписка tab (L118)

Silver/Gold · месяц/год · feature table · trial CTA.

| ALADDIN | **ADAPT** → наши уровни Family/Premium в `10_TariffsScreen`; названия ALADDIN; Storm paywall; soft L-P3-01e после N дней |

---

#### Backlog interiors (добавка к L-P3)

| ID | Задача | Evidence |
|----|--------|----------|
| L-P3-01d | 5 chips + scroll-spy + секции | L91–97 |
| L-P3-01e | Soft Family paywall N дней | L96 |
| L-P3-01f | Role modal invite | L98–99 |
| L-P3-01g | Places suggestion list | L112 |
| L-P3-01h | Create event form | create-event JPG |
| L-P3-01i | Pet profile wizard + routines→Habits | pet JPGs |
| L-P3-01j | Pet/Items beacon **soon** sheets | beacon/items JPG |
| L-P3-01k | Driving tab = weekly UI → DrivingReportsModal | L116 |
| L-P3-01m | Safety tab Crash+contacts chrome | L117 |
| L-P3-01n | Subscription tab → Tariffs chrome | L118 |

#### GATES interiors

- G-I1: 4 tab bar всегда в хабе; выход X → Удобный.  
- G-I2: 5 chips sync scroll.  
- G-I3: Pet/Items без fake live pins / fake shop.  
- G-I4: Driving empty честный; данные только реальные.  
- G-I5: Loc RU+EN; verify script.  
- G-I6: Дизайн Storm+gold / serif titles Удобного.

---

## 14. Дерево задач: что · зачем · было · будет

### Волна A — Kaspersky UX + фундамент карты

| ID / тема | Что делаем | Зачем | Было | Будет |
|-----------|------------|-------|------|-------|
| Call Directory гайд | Stepper S02 в «Проверить» | Включить блокировку спама | Частично карта настроек | Понятный гайд + статус ON |
| Lists empty | Empty spam/own list | Честный UI без reverse | Слабый empty | 3D/Storm empty + CTA |
| Анти-Баннер | Toggle + Safari tip | Меньше рекламы | ContentBlocker есть | Дверь Проверить + copy |
| Дом/сеть | Empty «скоро/нет устройств» | Честно | Нет fake scan | Empty Storm |
| VK | Empty «Подключите» | Не врать API | Нет | Empty до OAuth GO |
| Last-point карта | Уже WhereIsPhone | База для B | Last-point + share | Polish + anti-spy copy |
| Family Full/Limited | Пресеты L79 | Privacy доверие | Частично роли | Карточки Full/Limited |
| Invite chips / role / avatar | L08/L12/L14 | Быстрый инвайт | Есть invite | Max-UI chips |
| Splash | WORDMARK_V2 | Бренд | Разный launch | Solid ALADDIN splash |
| Loc A | calldir/child/… keys | Без сырых ключей | Часть есть | Добить пакеты §7 |

### Волна B — live Map + Life360 max-UI

| ID | Что | Зачем | Было | Будет |
|----|-----|-------|------|-------|
| L-P3-01 | Max-UI map + **4 таба** + FAB | Как Life360 в хабе | Простой modal+карта | 4-tab · dark map · FAB · detents |
| L-P3-02 | Member sheet | Понять «где человек» | Список сигналов | Карточка L83 + battery |
| L-P3-03 | Map type | Слои карты | Нет | Авто/Улицы/Спутник |
| L-P3-04 | Places chips | Дом/Школа быстро | Geofence modal | Chips + preview |
| L-P3-05 | Always Allow sheet | Live без spy-тона | Системный диалог сырой | Pre-prompt + Settings |
| L-P3-06 | Day Journal | История дня | Trail частично | Playback scrub |
| L-P3-07 | Тихая зона | Privacy | Нет | Slider zone |
| L-P3-08 | Share link | Временная ссылка | Share точка | Duration picker |
| L-P3-09 | Routes | Доехать | openInMaps | Sheet Directions |
| L-P3-10 | Pin preview | Онбординг вида | Нет | «Как вам вид?» |
| L-P3-25 | Calendar D | Семья планирует | Нет UI календаря | Месяц + EventKit |
| L-P3-28 | Speed badge | Скорость честно | Нет | ≈ км/ч с GPS |
| L-P3-27 | Anti-spy glossary | Доверие | Риск spy-copy | §7.2 locked |

### Волна C — Crash / SOS / empty partners

| ID | Что | Зачем | Было | Будет |
|----|-----|-------|------|-------|
| L-P3-19…22 | Crash + SOS hold | Реальная помощь семье | План/частично | Confirm + hold countdown |
| L-P3-23 | Tile empty | Честно | Нет | «Скоро» без pin |
| L-P3-24 | Evac empty | Честно | Нет | «Скоро» + 112 |
| L-P3-26 | Pet row скоро | Честно | Нет | Row → sheet скоро |

### P4 — не сейчас

Driving weekly · multi-circle · Flight · ID theft · live Pet/dispatch.

---

## 15. Чеклист «другая ML поймёт?»

| Вопрос | Где ответ |
|--------|-----------|
| Куда клик → какой файл? | §13.3 |
| Какой шрифт/цвет/карточка? | §2 |
| Какой RU/EN текст? | §7.2 |
| Какой JPG смотреть? | FILE_INDEX |
| TAKE или SKIP? | audit MD + partials |
| Как закрыть карту? | X → isPresented (§13.1) |
| Подключать live/API? | §13.3 + GATES §10; no mock |
| Как передать задачу? | §11.1 + промпт §11.2 + GO одной волны |

---

## 16. Красота «как Life360» — что да / как / хватает ли плана

### 16.1 Будет ли дизайн максимально близок к Life360?

**Да по композиции и UX** (цель Wave B): full-bleed map · 4-tab bar · FAB · bottom sheet detents · member card · Places chips · empty 3D · pin+battery — **смысл и раскладка 1:1 с референсом L\***.

**Нет по бренду:** не purple `#7D4CFA`, не лого Life360. Оболочка = Storm glass + serif/gold Удобного (§2).

**«Так же красиво» =** повторить **иерархию, отступы, жесты, плотность** со скринов; цвета/шрифт — ALADDIN. Не «похож примерно».

### 16.2 Как ML/агент добивается красоты (ритуал)

1. Открыть задачу → колонка **Evidence** (напр. L42, L83).  
2. `LIFE360_L01_L90_FILE_INDEX.txt` → имя `photo_*.jpg` → открыть JPG в Cursor assets.  
3. Прочитать карточку в `_partial_L*.md` (слои, тексты, checklist).  
4. Сверстать SwiftUI 1:1 по слоям; токены §2.  
5. Side-by-side: скрин vs симулятор (после GO на сборку) — sheet высота, FAB stack, tab icons, typography weight.  
6. Если нужен illustration/3D empty — FIG-L* (Figma GO) или SF Symbol+glass interim, не серая заглушка.

**Сможет ли агент «отрисовать так же»?** Layout/UI в SwiftUI — **да** по скринам. Пиксельный клон чужого brand kit — **нет (запрет)**. Новые 3D-иллюстрации — Figma/ассет GO, не «из воздуха в одном Swift-файле».

### 16.3 Отсылки на скрины — есть?

| Где | Что |
|-----|-----|
| Master §6 backlog | колонка **Evidence** = Lxx / Sxx |
| Life360 MD §4 | индекс всех L01–L90 → вердикт |
| `_partial_L01_L30.md` и др. | полные UI-карточки |
| `LIFE360_L01_L90_FILE_INDEX.txt` | Lxx → JPG filename |
| Kaspersky MD + `KASPERSKY_S01_S60_FILE_INDEX.txt` | то же для Sxx |

Без Evidence id задачу **не закрывать**.

### 16.4 Отсылки на другие файлы — есть?

Да: §12 + START_HERE роутер + Swift якоря (`SimpleHomeScreen`, `WhereIsPhoneScreen`, `FamilyModalBaseView`, Tariffs, BrandAssets).

### 16.5 Достаточно ли для «100% выполнения плана»?

| Для чего | Хватает? |
|----------|----------|
| Другая ML **начинает и не двоит** IA/loc/навигацию | **Да** (docs) |
| Закрыть задачу экрана без открытия JPG+partial | **Нет** — скрин обязателен |
| Ship в Store без кода/Figma/QA | **Нет** |
| Пиксель-таблица «y=12, h=48» на каждый слой всех 90 | **Нет в master** — бери с JPG + partial; при споре — измерить и дописать в задачу |

### 16.6 Что осталось НЕ сделанным

**Docs gaps из прошлого хода — закрыты (v1.2):**
- [x] §7.2 → `Localizable.strings` RU+EN  
- [x] FIG-L01…24 имена + промпты → `FIGMA_FAMILY_SAFETY_ML_PROMPTS.md`  
- [x] Копии `L01.jpg`…`L90.jpg` / `S01.jpg`…`S60.jpg`

**Ещё ждёт GO владельца (исполнение):**
- [x] Swift §17 шаг 1…7a (см. checklist) · 7b Figma [D] · 8 Device QA → **открыт**  
- [ ] Device QA батчи W0–W9: [`FAMILY_SAFETY_DEVICE_QA_MASTER_PLAN_2026-11-05.md`](FAMILY_SAFETY_DEVICE_QA_MASTER_PLAN_2026-11-05.md)  
- [ ] Figma приоритет FIG-L34+L15+L25+L01+L03 (7b долг)  
- [ ] Партнёры или empty (Tile/evac/live Pet)  
- [ ] Commit/push по просьбе  

**Как передать Figma-ML:** файл `FIGMA_FAMILY_SAFETY_ML_PROMPTS.md` §1 + §6 (один FIG-id за раз).  
**Этап Figma:** можно last для 3D; tab/pin/FAB лучше до финальной красоты QA (§8 + FIGMA §0).

---

### 17. Порядок исполнения кода (канон владельца 2026-11-04 — lock)

**Продукт не меняем.** Оговорки ML = порядок исполнения, не смена IA.

Замок продукта (всегда): один hub · 4 таба внутри · 5 chips+scroll-spy · Storm/gold · no mock · Calendar D · Driving→`DrivingReportsModal` · soft paywall · loc · P4 live pet/dispatch — **не сейчас**.

Не весь Wave B одним PR. **GO-цепочка 1→8:**

| # | GO / задача | План | Факт (код) |
|---|-------------|------|------------|
| 1 | `L-P3-01` — 4-tab + X → Удобный | ✅ | см. checklist |
| 2 | `L-P3-01d` — 5 chips + scroll-spy; Pet/Items = **soon-sheet** (не full wizard) | ✅ | |
| 3 | Driving tab → modal · Subscription **thin** → Tariffs · Safety chrome | ✅ | |
| 4 | Member · map type · Places · Always Allow | ✅ | |
| 5 | Calendar D + EventKit · soft paywall `01e` | ✅ | |
| 6 | journal/quiet/share/routes · Wave C/A · Pet **`01i` отдельным GO** | ✅ | |
| 7a | **Interim B:** PNG-ассеты pin · FAB · chip strip (SF Symbol+glass уже в коде) | ✅ | см. checklist — **не** = «100% Figma» |
| 7b | **Figma later (обязательный долг):** отдельный файл Family Safety · **все** нужные FIG-L* / FIG-* из `FIGMA_FAMILY_SAFETY_ML_PROMPTS.md` (приоритет L34+L15+L25+L01+L03, затем остальные flagship) · **не** OB_* | ✅ долг | ⬜ до закрытия долга |
| 8 | `GO на сборку` → side-by-side JPG (после кода 1–6 + 7a; **7b не блокирует** первую Device QA) | ✅ | |

**Шаг 7 — lock владельца 2026-11-04 (вечер):**  
- PNG / SF Symbol = **interim** для ship-красоты.  
- **Запрещено** отмечать «Figma 100%» по PNG.  
- Через недели (отдельный GO): закрыть **полный** Figma-контур по всем необходимым страницам плана (не только 5 приоритетных).  
- 3D Pet / empty heroes — в том же Figma-долге, можно последними.

**«Prod-beautiful»:** цель ship; **проход 1** = каркас+жесты; **проход 2** = плотность как L91–L118; **проход 3** = Figma assets → xcassets.  
**«Ничего не убираем»:** chips/строки/табы остаются; deep Pet/Items в v1 = soon-sheet; мастер `01i` — следующий GO (фича не убита).  
**Wave A** не блокирует B (для «Где семья» сначала B).  
**Подписка-таб:** thin chrome → `10_TariffsScreen`, не копировать весь экран в tab.  
**JPG:** есть и `L91.jpg`, и `L91_sheet_*.jpg` (оба ок).  
**Не:** весь FIG-L01…36 до кода; Pet live+wizard вместе с live map; один ship A+B+C; путать PNG-interim с закрытием Figma.

Передача ML: промпт **§11.2** + одна фраза GO шага, напр.  
`GO код Wave B — L-P3-01 (4-tab + X → Удобный)`.  
Figma-долг: `GO Figma MCP — Family Safety file · закрыть FIG-L* по промптам`.

Трекинг: Cursor TODO + [`FAMILY_SAFETY_PLAN_FACT_CHECKLIST.md`](FAMILY_SAFETY_PLAN_FACT_CHECKLIST.md).

---

**Конец master v1.4 (+ §17 Figma debt lock).** Code-ML: §11.2 + §17. Figma-ML: `FIGMA_FAMILY_SAFETY_ML_PROMPTS.md`. Скрины: `screenshots_life360/Lxx.jpg`.
