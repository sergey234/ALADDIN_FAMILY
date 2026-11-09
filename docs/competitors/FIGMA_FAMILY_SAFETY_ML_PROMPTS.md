# Figma ML — промпты по страницам (Kaspersky + Life360 → ALADDIN)

**Дата:** 2026-11-04 · **для:** отдельная ML-система / дизайнер в Figma  
**Очередь + статусы (SSOT):** [`FAMILY_SAFETY_UNIFIED_ML_PLAN_2026-11-09.md`](FAMILY_SAFETY_UNIFIED_ML_PLAN_2026-11-09.md) §7 — этот файл = тексты промптов, не дублировать backlog.  
**Канон продукта:** [`FAMILY_SAFETY_KASPERSKY_LIFE360_MASTER_PLAN.md`](FAMILY_SAFETY_KASPERSKY_LIFE360_MASTER_PLAN.md)  
**Приоритет отрисовки:** **сначала Life360 (FIG-L\*)**, потом Kaspersky (FIG-01…22) если не reuse.  
**Блокер перед FIG-L:** MAP-95 sheet 95% на device (UNIFIED §3) — иначе дважды перерисовывать L34.

---

## 0. Когда делать Figma в пайплайне?

| Этап | Что | Figma? |
|------|-----|--------|
| 1. Docs (готово) | Master + audits + Lxx.jpg | — |
| 2. **Рекомендуемо параллельно с Wave B кодом** | FIG-L flagship (пин, FAB, empty 3D, SOS, journal) | **Да — лучший момент** |
| 3. Можно **в последнюю очередь** | Иллюстрации/3D, если код уже на SF Symbol + stormGlass | **Да**, но «100% красиво» закрывается только после вставки ассетов |
| 4. До кода Wave B | Опционально: сетка frames + pin/FAB | Ускоряет код |
| 5. Onboarding OB_* | **Не трогать** | Запрет |

**Ответ владельцу:** Figma-картинки **можно последними**, если Swift уже max-UI на символах/glass.  
**Наилучший порядок:** (а) код структуры 4-tab+map → (б) FIG-L иллюстрации → (в) вставка в xcassets → (г) polish QA.  
Или Figma flagship **до** финального Device QA красоты.

**Не ждать Figma**, чтобы начать: live Map, Always Allow, Calendar D, SOS hold — можно на SF Symbols.

### Долг владельца (lock 2026-11-04) — interim PNG ≠ Figma done

| Фаза | Что | Статус в плане |
|------|-----|----------------|
| **7a Interim B** | PNG pin / FAB / chips (или SF Symbol) | ship-beauty сейчас |
| **7b Figma later** | Отдельный файл Family Safety · **все необходимые** FIG-L* / FIG-* из этого документа (не только L34/L15/L25/L01/L03) · **не** OB_* | **обязательный долг**, отдельный GO через недели |

**Запрет:** отмечать «Figma 100%» после PNG. SSOT закрытия Figma = MCP + frames по списку §3–§4.

---

## 1. Общий промпт Figma-ML (копировать целиком + один FIG-id)

```text
Роль: product designer + Figma MCP agent для ALADDIN family-safety.

SSOT: docs/competitors/FAMILY_SAFETY_KASPERSKY_LIFE360_MASTER_PLAN.md
Этот файл промптов: docs/competitors/FIGMA_FAMILY_SAFETY_ML_PROMPTS.md
Референс Life360: docs/competitors/screenshots_life360/Lxx.jpg + _partial_L*.md
Референс Kaspersky: docs/competitors/screenshots_kaspersky/Sxx.jpg + Kaspersky audit MD
НЕ трогать Onboarding файл KvkUdyb5… / OB_00…07 / APP_AppStoreIcon.

ЦЕЛЬ: ассеты ALADDIN Storm glass (тёмный mesh, glass card, accent #F59E0B gold).
НЕ копировать Life360 purple #7D4CFA и лого Life360.
Композиция / плотность / смысл = максимально как Life360 (приоритет) или Kaspersky (дверь Проверить/Ребёнок).
Типографика в спеке для iOS: serif bold titles как SimpleHome; в Figma можно SF Pro + отдельный note «iOS = serif title».
Экспорт: PDF/SVG или PNG @2x/@3x → потом Assets.xcassets (отдельный GO кода).
Имена слоёв: FIG-Lxx_… / FIG-xx_… английский snake или Pascal.

Перед рисованием: открой референс JPG из таблицы ниже + partial/audit.
После кадра: get_screenshot слоя; кратко «что сделано / export path».
Сейчас рисуй ТОЛЬКО: <ВСТАВИТЬ FIG-Lxx или FIG-xx>.
```

---

## 2. Дизайн-токены (для каждой страницы)

| Токен | Значение |
|-------|----------|
| Canvas phone | 393×852 (как онбординг) или component-only artboard |
| Фон app | dark `#0F172A` + indigo mesh (не purple flat) |
| Card | frost glass + stroke gold 38% opacity, radius large ~16–20 |
| Accent | `#F59E0B` |
| Title | Bold large; note: iOS serif |
| Sub | Secondary / white 70% |
| Map | dark map style; pin with avatar ring |
| Tab bar (в хабе) | 4 icons: Location / Driving / Safety / Membership — стиль Life360 density, цвета ALADDIN |
| Запрет | Life360 wordmark, Kaspersky green logo lockup, spy marketing art |

---

## 3. PRIORITY 1 — Life360 FIG-L\* (отрисовать обязательно)

Для каждой строки: **Что** · **Зачем** · **Референс JPG** · **Промпт-страница** · **Export** · **Куда в iOS**.

### FIG-L01 — Map pin + avatar ring + battery
- **Зачем:** главный маркер на карте (L42/L83).  
- **Референс:** `screenshots_life360/L42.jpg`, `L13.jpg`, `L83.jpg`  
- **Промпт:**  
  `Нарисуй map annotation: круглый аватар 48–56pt, золотое/светлое кольцо, badge батареи справа-снизу (молния или %). Стиль Life360 pin, цвета ALADDIN gold+storm. Без текста бренда. Component FIG-L01_MapPinBattery. Export PNG @2x/@3x + PDF.`  
- **iOS:** `WhereIsPhoneScreen` Map annotation  
- **Этап:** до/с Wave B L-P3-01

### FIG-L02 — Last-seen bubble
- **Зачем:** «Был(а) здесь · 5 мин» над пином.  
- **Референс:** `L58.jpg`, `L83.jpg`  
- **Промпт:**  
  `Bubble/callout над пином: скруглённый glass, одна строка last-seen. Hierarchy как Life360. Component FIG-L02_LastSeenBubble.`  
- **iOS:** member pin overlay  
- **Этап:** Wave B

### FIG-L03 — FAB glass stack
- **Зачем:** кнопки settings / inbox / layers / locate как у Life360.  
- **Референс:** `L42.jpg`  
- **Промпт:**  
  `Вертикальный stack 4 круглых FAB 44–48pt, frost glass, тонкая gold stroke, SF-symbol-like icons (gear, tray, square.3.layers, location). Spacing 10–12. Component FIG-L03_FABStack.`  
- **iOS:** map FAB  
- **Этап:** L-P3-01

### FIG-L04 — Member sheet hero / 3D teaser (без Driving lock как продукта)
- **Зачем:** верх member sheet; 3D clay опционально.  
- **Референс:** `L83.jpg`, `L26.jpg`  
- **Промпт:**  
  `Шапка member sheet: аватар large, имя, «Рядом с Дом», время, battery row. Опционально мягкая 3D-иллюстрация семьи (не Life360 brand). Не обещать trip report. FIG-L04_MemberSheetHero.`  
- **iOS:** L-P3-02  
- **Этап:** Wave B

### FIG-L05 — Empty mailbox / inbox 3D
- **Зачем:** честный empty inbox.  
- **Референс:** `L23.jpg`, `L76.jpg`  
- **Промпт:**  
  `3D/clay mailbox или конверт на storm фоне, empty state. Без Offers spam art. FIG-L05_EmptyMailbox.`  
- **iOS:** inbox empty  
- **Этап:** Wave A/B

### FIG-L06 — Full vs Limited cards
- **Зачем:** privacy пресеты семьи.  
- **Референс:** `L79.jpg`, `L21.jpg`  
- **Промпт:**  
  `Две selectable cards Full / Limited: icon, title, 3 benefit pills. Glass+gold selected state. FIG-L06_AccessCards.`  
- **iOS:** Family create  
- **Этап:** Wave A

### FIG-L07 — Name chips + role pills
- **Зачем:** создание семьи / инвайт.  
- **Референс:** `L08.jpg`, `L82.jpg`, `L14.jpg`  
- **Промпт:**  
  `Horizontal chips имён + role pills Мама/Папа/Ребёнок. Как Life360 density. FIG-L07_ChipsRoles.`  
- **iOS:** Family invite  
- **Этап:** Wave A

### FIG-L08 — Geofence / Quiet zone circle
- **Зачем:** Places radius + Privacy Zone.  
- **Референс:** `L59.jpg`, `L85.jpg`, `L27.jpg`  
- **Промпт:**  
  `Map overlay: полупрозрачный круг accent gold/cyan (НЕ purple Life360), slider hint. FIG-L08_GeofenceCircle.`  
- **iOS:** Places / Quiet zone  
- **Этап:** Wave B

### FIG-L09 — Day Journal polyline + time chip
- **Зачем:** история дня.  
- **Референс:** `L87.jpg`  
- **Промпт:**  
  `Карта с polyline маршрута за день + time bubble + scrub hint. FIG-L09_DayJournal.`  
- **iOS:** L-P3-06  
- **Этап:** Wave B

### FIG-L10 — SOS hold button + countdown ring
- **Зачем:** Wave C SOS.  
- **Референс:** `L36.jpg`, `L37.jpg`, `L40.jpg`  
- **Промпт:**  
  `Огромная круглая SOS кнопка, ring countdown, hint «удерживайте». Не tap-once. Цвета danger/gold на storm. FIG-L10_SOSHold.`  
- **iOS:** L-P3-21  
- **Этап:** Wave C (можно рисовать заранее)

### FIG-L11 — Crash tip permission icons
- **Зачем:** checklist tip.  
- **Референс:** `L69.jpg`, `L54.jpg`  
- **Промпт:**  
  `Ряд emoji/иконок разрешений + title «Это авария?» sheet chrome. FIG-L11_CrashTipRow.`  
- **iOS:** Crash  
- **Этап:** Wave C

### FIG-L12 — Map type thumbnails
- **Зачем:** Авто/Улицы/Спутник.  
- **Референс:** `L81.jpg`, `L25.jpg`  
- **Промпт:**  
  `3 thumbnail карты 96×96 с labels (тексты из loc map_type_*). Pet row = disabled «скоро» без pins. FIG-L12_MapTypeThumbs.`  
- **iOS:** L-P3-03 / L-P3-26  
- **Этап:** Wave B

### FIG-L13 — Share-link preview card
- **Зачем:** временная ссылка.  
- **Референс:** `L86.jpg`, `L28.jpg`  
- **Промпт:**  
  `Карточка превью карты + duration chips. FIG-L13_ShareLinkCard.`  
- **iOS:** L-P3-08  
- **Этап:** Wave B

### FIG-L14 — Splash ALADDIN WORDMARK
- **Зачем:** brand splash.  
- **Референс:** `L78.jpg` (композиция), BrandAssets WORDMARK_V2  
- **Промпт:**  
  `Full-bleed ALADDIN dark/storm (НЕ purple). Центр: WORDMARK_V2 из BrandAssets (импорт). FIG-L14_Splash.`  
- **iOS:** Launch / L-P3-18  
- **Этап:** Wave A

### FIG-L15 — 4-tab bar icons (Location / Driving / Safety / Membership)
- **Зачем:** гибрид 4 таба в хабе.  
- **Референс:** `L42.jpg` (низ), любой Life360 tab bar crop  
- **Промпт:**  
  `Bottom tab bar 4 items, иконки+labels RU placeholders. Selected = gold. Unselected = white 50%. Density как Life360. FIG-L15_HubTabBar.`  
- **iOS:** L-P3-01  
- **Этап:** Wave B **сразу**

### FIG-L16 — Calendar month empty + CTA
- **Зачем:** Calendar D.  
- **Референс:** `L48.jpg`, `L49.jpg`–`L51.jpg`  
- **Промпт:**  
  `Месяц-сетка + empty illustration + CTA «Добавить событие». Storm glass. FIG-L16_FamilyCalendar.`  
- **iOS:** L-P3-25  
- **Этап:** Wave B

### FIG-L17 — Places chips Дом/Школа/Работа
- **Зачем:** Places.  
- **Референс:** `L47.jpg`, `L19.jpg`  
- **Промпт:**  
  `Chips + list rows places. FIG-L17_PlacesChips.`  
- **iOS:** L-P3-04  
- **Этап:** A→B

### FIG-L18 — Always Allow pre-prompt art
- **Зачем:** permission без spy.  
- **Референс:** `L31.jpg`, `L70.jpg`, `L72.jpg`  
- **Промпт:**  
  `Sheet hero: спокойная иллюстрация «карта обновляется» (семья/телефон), НЕ слежка. FIG-L18_AlwaysAllow.`  
- **iOS:** L-P3-05  
- **Этап:** Wave B

### FIG-L19 — Tile / Tags empty «скоро»
- **Зачем:** честный empty.  
- **Референс:** `L45.jpg`, `L64.jpg`  
- **Промпт:**  
  `Empty tags/метки illustration + badge Скоро. Без fake map pins. FIG-L19_TagsSoon.`  
- **iOS:** L-P3-23  
- **Этап:** Wave C

### FIG-L20 — Roadside / Evac empty «скоро»
- **Зачем:** без «уже едет».  
- **Референс:** Life360 store roadside vibe; не US fake dispatch UI  
- **Промпт:**  
  `Иллюстрация помощи на дороге + «Скоро» + hint 112. FIG-L20_EvacSoon.`  
- **iOS:** L-P3-24  
- **Этап:** Wave C

### FIG-L21 — Pet row «скоро» (не слой на карте)
- **Зачем:** L-P3-26.  
- **Референс:** `L81.jpg` pet toggle area  
- **Промпт:**  
  `List row pet + chevron + soon badge. FIG-L21_PetSoonRow.`  
- **Этап:** Wave C

### FIG-L22 — Driving tab empty / speed only
- **Зачем:** таб есть, reports P4.  
- **Референс:** `L52.jpg`, `L71.jpg` (layout only)  
- **Промпт:**  
  `Driving tab empty: speed gauge soft OR «скоро отчёты» card. Не weekly locks paywall как продукт. FIG-L22_DrivingSoon.`  
- **iOS:** L-P3-01b  
- **Этап:** Wave B

### FIG-L23 — Pin preview onboarding «Как вам вид?»
- **Референс:** `L13.jpg`  
- **Промпт:** `Preview pin styles picker. FIG-L23_PinPreview.`  
- **iOS:** L-P3-10

### FIG-L24 — Routes sheet chrome
- **Референс:** `L62.jpg`, `L61.jpg`  
- **Промпт:** `Routes options list glass. FIG-L24_RoutesSheet.`  
- **iOS:** L-P3-09

### FIG-L25 — Sheet 5-chip strip (people · paw · key · home · events) + scroll-spy
- **Зачем:** главная навигация секций на Location sheet (как Life360).  
- **Референс:** `L91`…`L97` в `screenshots_life360/`  
- **Промпт:**  
  `Горизонтальный ряд 5 rounded chips: люди, лапа, ключ, дом, календарь/коробка. Selected = тёмный fill + белая иконка (ALADDIN gold/storm, НЕ purple). Unselected = outline. Sticky под заголовком семьи. Component FIG-L25_SheetSectionChips.`  
- **iOS:** L-P3-01d  
- **Этап:** Wave B **сразу с L-P3-01**

### FIG-L26 — Soft Family trial/paywall timeline (после N дней)
- **Референс:** `L96_paywall_trial_banner.jpg`  
- **Промпт:**  
  `Sheet: заголовок «Одна подписка для всей семьи», timeline Сегодня / День N / конец trial, CTA Попробовать + Может позже. Storm+gold, НЕ Life360 Gold purple. FIG-L26_FamilySoftPaywall.`  
- **iOS:** L-P3-01e  

### FIG-L27… — Section empties (pets / items / events) 3D
- **Референс:** L92 pets, L94 items, L97 events  
- **Промпт:** `Empty cards 3D clay ALADDIN-style + CTA. Pets/Items = «скоро». Events = Calendar empty. FIG-L27_PetsSoon / FIG-L28_ItemsSoon / reuse FIG-L16 events.`

### FIG-L29 — Pet wizard (photo · form · routines · success)
- **Референс:** `L103`… pet flow JPGs в screenshots_life360  
- **Промпт:** `Экраны: добавить фото на pin; форма порода/цвет/вес/пол; рутины hero; success без Pet Network brand. Storm+gold. FIG-L29_PetWizard.`  
- **iOS:** L-P3-01i · live map pet = soon  

### FIG-L30 — Driving weekly report chrome
- **Референс:** L116  
- **Промпт:** `Weekly report: period pills, 4 metric chips, max speed, trips, member row. ALADDIN colors. FIG-L30_DrivingWeekly.`  

### FIG-L31 — Safety tab Crash + emergency contacts
- **Референс:** L117  
- **Промпт:** `Two sections cards: Crash toggle FREE + Emergency contacts row. FIG-L31_SafetyTab.`  

### FIG-L32 — Places add list
- **Референс:** Places modal JPG  
- **Промпт:** `List Дом/Школа/Работа/… + Add new. FIG-L32_PlacesList.`  

### FIG-L33 — Create event form
- **Референс:** create event JPG  
- **Промпт:** `Form name/location/today-tomorrow/date/start/end. FIG-L33_CreateEvent.`  

### FIG-L34 — Location sheet FULL frame (max Life360 UI)
- **Зачем:** главный кадр «как у них» — баннер + семья + 5 chips + секции + 4-tab.  
- **Референс:** `L91.jpg`…`L97.jpg`, L42  
- **Промпт:**  
  `Phone 393×852: сверху кусок dark map; white/Storm sheet с rounded top. 1) Invite banner (конверт 3D ALADDIN, не purple Life360) + CTA Добавить близких. 2) Title семьи. 3) Sticky FIG-L25 5 chips. 4) Секция Люди: карточка члена + Добавить человека + teaser родственники. 5) Ниже намётки Pets/Items/Places/Events cards. 6) Bottom FIG-L15 4-tab, Location selected. Композиция и плотность 1:1 Life360; цвета Storm+gold. Frame name: FIG-L34_LocationSheetFull.`  
- **iOS:** L-P3-01 + 01d  
- **Этап:** **первым** после GO Figma (вместе с L15/L25)

### FIG-L35 — Invite role modal
- **Референс:** L98–L99  
- **Промпт:** `Modal: вопрос роли; pills Мама/Папа/Ребёнок; Пропустить. Storm glass. FIG-L35_RoleModal.`  
- **iOS:** L-P3-01f  

### FIG-L36 — Subscription tab (Family plans, не Silver/Gold)
- **Референс:** L118 (layout only)  
- **Промпт:** `Tab Подписка: eyebrow Семейный тариф; title; Month/Year toggle; 2 plan cards ALADDIN Free/Family; feature row history days; CTA trial. НЕ лого Life360, НЕ purple brand kit. FIG-L36_SubscriptionTab.`  
- **iOS:** L-P3-01n  

### FIG-L22 — уточнение
Использовать **FIG-L30** для weekly Driving UI; FIG-L22 только если нужен сверх-короткий empty teaser.

---

## 4. PRIORITY 2 — Kaspersky FIG-01…22 (если нет reuse)

Полная таблица смысла — Kaspersky MD §17. Кратко для Figma-ML:

| ID | Референс | Промпт одной строкой | Куда |
|----|----------|----------------------|------|
| FIG-01 | S02 | Hero «спокойный звонок» storm+gold | Проверить |
| FIG-02 | S02 | 5 step circles Settings/Phone/toggle | Call Directory |
| FIG-03 | S12 | Shield ON status 64–96 | Status |
| FIG-04 | S08 | Empty list line-art | Lists |
| FIG-05 | Safe Kids empty | Child overview empty soft | Дверь Ребёнок |
| FIG-06 | S37–41 | Avatar placeholders grid | Add child |
| FIG-07 | invite | QR/share cards | Family |
| FIG-08 | S40 | Waiting / link illustration | Invite wait |
| FIG-09 | — | = reuse FIG-L01 если готов | Map |
| FIG-10 | Places | Home/school markers | Places |
| FIG-11 | S32 | Always allow art → prefer FIG-L18 | Perm |
| FIG-12 | S32 | Onboarding map tip (не ломать OB_*) | Optional tip in-app |
| FIG-13 | categories | Traffic-light dots | Content cats |
| FIG-14 | S29 | Adblock story | Анти-Баннер |
| FIG-15 | S27 | Router/home empty | Дом/сеть |
| FIG-16 | QR | Safe QR icon | Проверить |
| FIG-17 | VK | Neutral connect (не воровать бренд криво) | VK empty |
| FIG-18 | — | = FIG-L10/L11 | Crash/SOS |
| FIG-19 | — | = FIG-L19 | Tile |
| FIG-20 | — | = FIG-L20 | Evac |
| FIG-21 | paywall | Family seats cards | Tariffs |
| FIG-22 | toast | Soft premium bar | Notif |

**Правило:** если FIG-L\* уже закрывает смысл — **не дублировать**, поставить link «reuse FIG-Lxx».

---

## 5. Порядок рисования (рекомендуемый sprint)

1. **FIG-L15** tab bar + **FIG-L01** pin + **FIG-L03** FAB → каркас хаба  
2. **FIG-L02**, **FIG-L04**, **FIG-L12**, **FIG-L17** → map daily UX  
3. **FIG-L18**, **FIG-L08**, **FIG-L09**, **FIG-L13**, **FIG-L16** → B polish  
4. **FIG-L14**, **FIG-L06**, **FIG-L07**, **FIG-L05** → Family/A  
5. **FIG-L10**, **FIG-L11**, **FIG-L19–22** → C / soon  
6. Kaspersky FIG-01…08, 13–17, 21 — если не reuse  

---

## 6. Как владельцу передать Figma-ML одну страницу

```text
[Вставить общий промпт §1]

Сейчас рисуй ТОЛЬКО: FIG-L01
Референс: docs/competitors/screenshots_life360/L42.jpg и L83.jpg
Partial: docs/competitors/_partial_L61_L90.md (карточка L83) + L42 в _partial_L31_L60.md
Export: FIG-L01_MapPinBattery @2x @3x PNG + PDF
Не трогать Onboarding Figma.
После — короткий отчёт + screenshot слоя.
```

Повторить, меняя только FIG-id и референсы из §3–§4.

---

## 7. Definition of Done Figma-страницы

- [ ] Референс JPG открыт  
- [ ] Нет purple Life360 brand / чужого лого  
- [ ] Storm + gold  
- [ ] Имя слоя FIG-*  
- [ ] Export 2x/3x  
- [ ] Запись в master/checklist «FIG-Lxx ✅»  
- [ ] Не тронут OB_*  

---

**Конец.** Приоритет = Life360 отрисовки. Kaspersky — двери Проверить/Ребёнок. Figma можно last для 3D; tab/pin/FAB лучше до Device QA красоты.
