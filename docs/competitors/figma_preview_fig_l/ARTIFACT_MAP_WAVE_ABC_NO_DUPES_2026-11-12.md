# Карта артефактов Wave A / B / C — без дублей (SSOT для другой ML)

**Дата:** 2026-11-12 ~21:10 Asia/Dubai  
**Repo:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS` · ветка **`master`**  
**Цель:** одна страница «где лежит всё» + антидубль, чтобы новая ML **не рисовала вторую иконку / ASC / SOS** поверх уже сделанного.

---

## 0. Что закрыто в этом чате (2026-11-12 вечер)

| ID | Что | Статус | Код / артефакт |
|----|-----|--------|----------------|
| TIP | Tip Where→Езда→отчёты | ✅ wired | `DrivingReportsModal` + `@AppStorage("asc_tip_driving_reports_dismissed")` · keys `asc_tip_driving_reports_*` |
| SOS-MID | Safety pager mid H07–H12 | ✅ wired (text+SF) | `WhereIsPhoneScreen.safetySOSEducationCarousel` · pages **0 intro · 1–4 mid · 5 release** · keys `sos_edu_mid_*` |
| ASC-DEC | H\* + Draft A–D в App Store | ✅ решение | pack ниже · upload в ASC — когда скажете |
| WAVE-C | Child/Antifake Glyph | ⏳ **другой чат** | `ML_HANDOFF_WAVE_C_VARIANT_A_…` · **не** дублировать A07/A08 двери |

**Сервер:** Invite OG (JOB13) уже на 🇷🇺 MAIN FirstVDS (`…180`):8002 + site `aladdin-ai.ru` — tip/SOS **не** требуют деплоя API.

---

## 1. Три волны — не смешивать

| Волна | Что | Куда в UI | Не путать с |
|-------|-----|-----------|-------------|
| **A** | Clay icons `ICON_G1_*_Glyph/_Black` | Main / SimpleHome / Family / Tariffs / Where tabs+FAB+Driving | ASC PNG · CapCut heroes |
| **B** | CapCut heroes `ICON_ALIVE_HERO_*` + ASC 1290×2796 | Where sheets · Driving · Safety · invite OG | G1 icons · OB_* |
| **C** | Child + Antifake soft-clay **новые** ID | ChildInterface · Antifake hub tabs | **не** перерисовывать A07 Check / A08 Child двери Удобного |

---

## 2. Figma — страницы и ссылки

| Файл | Key / URL | Роль | Правило |
|------|-----------|------|---------|
| **Onboarding** | `KvkUdyb5Ll31Z9FSzCbpNl` · [открыть](https://www.figma.com/design/KvkUdyb5Ll31Z9FSzCbpNl) · env `docs/FIGMA_ONBOARDING.env` | OB_00…07 · wordmark | **READ-ONLY** без SYNC GO · **не** Wave A/B/C |
| **Companion** | `vwKcGPUUEZjgayEHNn0BJM` · [открыть](https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM/Companion-Heroes) · `docs/FIGMA_COMPANION.env` | Companion HERO-3 | не Family Safety |
| **Family Safety FIG-L** | `b6gFc8GUtWC6ncPgb6X6II` · [открыть](https://www.figma.com/design/b6gFc8GUtWC6ncPgb6X6II/ALADDIN-Family-Safety-FIG-L) · `docs/FIGMA_FAMILY_SAFETY.env` | L01–L36 UI frames · sizes pt | in-app layout · export → Assets |
| Preview PNG FIG-L | `docs/competitors/figma_preview_fig_l/01_…09_….png` | скрины досок | референс |
| Size catalog | `…/FIGMA_FULL_SIZE_AND_SLOT_CATALOG.md` · freeze copy `freeze_2026-11-11_clay_blue_disc/` | pt/px слоты | SSOT размеров FIG-L |
| Icons V1/V2/V3 page | Figma page **07** (в FIG-L) + `Clay_G1_12.png` / `Clay_G1_Black_12.png` | доски глифов | Wave A source boards |

**Как делали в Figma (Wave A / FIG-L):**
1. Кадр FIG-L* с канон размером (напр. L15 tabs 22 · FAB 48 · pin 56).  
2. Export PNG / crop в imageset `ICON_G1_<ID>_Glyph` + `_Black` @1x/2x/3x (1x=32·2x=64·3x=96 для G1).  
3. Wire через `AliveGlyph(id:size:)` · Классика = SF/emoji fallback · **Blue imagesets есть, в wire НЕ используем**.  
4. OB_* / Companion — **никогда** из Wave A/B/C.

---

## 3. CapCut — как делали Wave B

**Пайплайн (каждая картинка):**
1. Промпт из `~/Downloads/ALADDIN_CapCut_Hero_Wave_B_2026-11-11/KAPCUT_PROMPTY_V2_TOP.md` + папки `PO_PAPKAM_CAPCUT_01_23/NN_*`.  
2. JPG из CapCut → `~/Downloads/ALADDIN_CapCut_READY/JOBnn_*`.  
3. Pillow: flood-fill белого → RGBA (**кроме** family heroes — map bg keep).  
4. Fit export size → `Assets.xcassets/ICON_ALIVE_HERO_*` @1x/@2x/@3x.  
5. Wire Swift + strings RU/EN (не rewrite `LocalizationManager.swift`).  
6. ASC: cover-crop → **1290×2796** navy/gold · pack в репо + Downloads.

**Промпты (репо):** `docs/competitors/figma_preview_fig_l/CAPCUT_ALL_PROMPTS_WAVE_B.md`

### 3.1 CapCut READY (локально, Downloads)

`~/Downloads/ALADDIN_CapCut_READY/` — JOB01…13 PNG/JPG (PlaceLandPin, Calendar, SUV Gold/Red, GoldLock, Pets, Family Walk/Kneel, Hug Stand/Kneel, SOS Intro/Release, Invite OG).

### 3.2 ASC pack (репо + копия Downloads)

| Где | Путь |
|-----|------|
| **Канон в git** | `docs/AppStore/asc_screenshots_wave_b_2026-11-12/` |
| Зеркало Finder | `~/Downloads/ALADDIN_ASC_WaveB_All/` |
| Loc checklist | `~/Downloads/ALADDIN_ASC_WaveB_LOC_CHECK_2026-11-12/` (`00_START`…`07_FITTED`) |
| READY ASC mirrors | `docs/competitors/figma_preview_fig_l/READY/15_ASC_LiveMap` · `18_ASC_DrivingHistory` · `19_ASC_DrivingReports` |

**Файлы ASC (грузить H\* + Draft):**

| Slot | RU | EN | Тема |
|------|----|----|------|
| H01 | `…H01_MomHome_LiveMap_RU…` | `…_EN…` | Live map мама дома |
| H03 | `…H03_MariaSection_PlaceAlert_RU…` | EN | Place alert |
| H21 | `…H21_DrivingSpeed_RU…` | EN | Speed |
| H22–H24 | Family circle / sunset / path bubble | RU+EN | Map-path pack |
| H25–H26 | Trips list / day timeline | RU+EN | Driving history |
| H27–H28 | Reports dashboard / trip detail | RU+EN | Driving reports |
| **Draft A** | DrivingStats | RU+EN | статистика+Gary |
| **Draft B** | LockAlerts | RU+EN | lock-алерты |
| **Draft C** | WHO_SafetyFacts | RU+EN | ВОЗ/Mercedes facts |
| **Draft D** | TwoPhones_ShieldScan | RU+EN | два телефона |

Copy SSOT: `ASC_LOCALIZATION_SSOT.md` · `ASC_*_COPY_RU_EN.md` · `CHECKLIST_WAVE_B_H20_23_AND_LOC.md` · `README_ASC_INDEX.md`

**Gary** — оставляем на всех кадрах, где уже есть.  
**H18 / H25 / H26 ≠ H27 / H28** — разные слоты, не подменять.

---

## 4. Icons Wave A — реестр (антидубль)

**Код:** `Shared/Components/AliveIconStyle.swift` · тест `Tests/UnitTests/AliveIconStyleTests.swift`  
**Assets:** `Assets.xcassets/ICON_G1_<ID>_{Glyph|Black|Blue}.imageset/`  
**Превью стиля:** Settings → «Превью иконок G1» (`AliveIconDiscStyle`)

| ID | Asset stem | Wire (пример) | Size pt | Не дублировать |
|----|------------|---------------|---------|----------------|
| A01 | Profile | Main tab / profile | 28 | — |
| A02 | Notif | tab Уведомления | 28 | — |
| A03 | Devices | tab Устройства | 28 | — |
| A04 | Protect | tile Защита | 40 | — |
| A05 | Tariff | tile Тарифы | 40 | — |
| A06 | Premium | Where hub / tariffs | 22–28 | — |
| A07 | Check | SimpleHome дверь «Проверить» | 36/32 | Wave C **reuse**, не новый PNG |
| A08 | Child | дверь «Ребёнок» | 36/32 | Wave C **reuse** двери |
| A09 | Where | дверь «Где семья» | 36/32 | — |
| A10 | ChipFamily | chip (Классика в Gold mode) | 28 | chips Pets/Places/Events = SF |
| A11 | FabLocate | FAB | 34 | — |
| A12 | Kids | tab Kids | 28 | — |
| U01 | Unicorn | tab Игра | 28 | — |
| M01–M05 | AIFriends / Senior60 / Analytics / Settings / SimpleHome | Main + SimpleHome | 28–40 | — |
| D02/D03 | Menu / FullApp | SimpleHome | — | — |
| T01–T04 | Free/Personal/Family/Trial | Tariff cards | — | — |
| F01–F04 | Members/Chat/Groups/Invite | `02_FamilyScreen` | как Семья | образец Wave C |
| W01 | Driving | Where L15 Езда | 22 | — |

**План:** `PLAN_ENTRY_ICONS_MAP_UNICORN_2026-11-11.md` · insert map `PER_ICON_INSERT_MAP.md` · `G1_SIZE_SLOT_MATRIX.md`

**Запрет дубля:** новый Glyph с тем же смыслом, что A07/A08/F01–F04/W01 → **STOP**, wire существующий `AliveIconID`.

---

## 5. Heroes Wave B — Assets → экран

| Asset `ICON_ALIVE_HERO_*` | CapCut JOB | Экран / слот | UI pt |
|---------------------------|------------|--------------|-------|
| H14_PlaceLandPin | 01 | Places sheet | 120 |
| H14_CalendarPencil | 02 (=JOB10 skip) | Events | 96 |
| H18_SUV_Gold | 03 | DrivingReports hero | 112 |
| H18_SUV_Red | 03 | member weekly | 96 |
| H16_GoldLock | 04 | Driving paywall / unlock | 140 / 96 |
| H15_PetDog/Cat/Other | 05–07 | Pets hero + picker | 120 / 88 |
| H17_FamilyWalk / Kneel | 08 | People / soft invite | 320×220 |
| H25_FamilyHugStand / Kneel | 09 | AlwaysAllow / Groups | 320×220 |
| H06_SOSIntro | 11 | Safety pager **0** | ~280×200 |
| H13_SOSRelease | 12 | Safety pager **5** | ~280×200 |
| (mid 1–4) | H07–H12 CapCut | pager **1–4** | ⏳ optional art · сейчас SF+text |
| Invite OG H20 stack | 13 | site+API+in-app share | 1200×630 |

Код: `WhereIsPhoneScreen` · `DrivingReportsModal` · `FamilySafetyRemainderHub` · `FamilyGroupsModal`  
Хэндофф: `PLAN_WAVE_B_CAPCUT_TODAY_HANDOFF_2026-11-12.md`

---

## 6. Tip + SOS mid (сделано сейчас) — страницы

### Tip
- **Путь UI:** Где → Езда → отчёты (`DrivingReportsModal`)  
- **Файл:** `Shared/Components/Modals/DrivingReportsModal.swift`  
- **Keys:** `asc_tip_driving_reports_title` / `_body` / `_dismiss`  
- **Dismiss:** AppStorage `asc_tip_driving_reports_dismissed`

### SOS education pager (6 страниц)
- **Путь UI:** Где → Safety → SOS education  
- **Файл:** `Screens/WhereIsPhoneScreen.swift` · `safetySOSEducationCarousel`  
- **0** intro (`ICON_ALIVE_HERO_H06_SOSIntro`)  
- **1–4** mid (`sos_edu_mid_1…4_*` + SF gold) — CapCut H07–H12 позже опционально  
- **5** release (`ICON_ALIVE_HERO_H13_SOSRelease`)  
- CTA mid: `sos_edu_mid_next` («Далее» / «Next») · **не** «Понятно»

Hold 3с / `FamilySOSHoldButton` — **логику не менять**.

---

## 7. Invite OG (сервер) — уже выкатано

| Слой | URL / путь |
|------|------------|
| Site | `https://aladdin-ai.ru/family/invite/FAM-…` → `landing/family-invite.html` + `landing/og/*.jpg` |
| API | `http://149.154.65.180:8002` · `GET/POST /api/family/invite/og.jpg` · dir `/og/family-invite/` |
| In-app | `InviteOGComposer` · `InviteOGPreviewCard` |

Health check (без секретов): `curl http://149.154.65.180:8002/api/health` → `{"status":"ok"}`.

---

## 8. Wave C — что **не** брать (передано другому чату)

| Item | Почему не в Wave C |
|------|--------------------|
| OB_* | Figma SYNC онбординг |
| Draft ASC / H* | уже Wave B ASC |
| Tip / SOS mid | ✅ этот чат |
| Перерисовка A07/A08 | reuse AliveIconID |
| bot / `.env` / VPN §32 | запрет |

Старт: `ML_HANDOFF_WAVE_C_VARIANT_A_CHILD_ANTIFAKE_ICONS_2026-11-12.md` · фраза **«GO Wave C art Batch1»**.

---

## 9. Связанные планы (ссылки в репо)

| Документ | Путь |
|----------|------|
| Этот файл | `docs/competitors/figma_preview_fig_l/ARTIFACT_MAP_WAVE_ABC_NO_DUPES_2026-11-12.md` |
| Wave B handoff | `…/PLAN_WAVE_B_CAPCUT_TODAY_HANDOFF_2026-11-12.md` |
| Wave C handoff | `…/ML_HANDOFF_WAVE_C_VARIANT_A_…md` |
| Wave C plan | `…/PLAN_WAVE_C_CHILD_ANTIFAKE_ICONS_2026-11-12.md` |
| Wave A icons | `…/PLAN_ENTRY_ICONS_MAP_UNICORN_2026-11-11.md` |
| Hero art master | `…/PLAN_LIFE360_HERO_ART_WAVE_2026-11-11.md` |
| ASC pack | `docs/AppStore/asc_screenshots_wave_b_2026-11-12/` |

---

## 10. Commit / deploy границы

**В iOS-коммит Wave A+B:** Assets G1 + AliveIconStyle + wire screens · tip/SOS · strings · ASC PNG/docs · эта карта.  
**Не в коммит:** `telegram_stars_shop_bot/` · `.env` · `VPN_SPEED_DEGRADATION_HANDOFF_RU.md` · BACKUPS · `.DS_Store` · antifake `app/services/antifake_*` mass · DerivedData.  
**Push:** только после **GO на push**.  
**xcodebuild:** только после **GO на сборку**.  
**Сервер после tip/SOS:** **ничего нового** (OG уже live).
