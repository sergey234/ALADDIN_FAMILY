# PLAN — Life360 hero-art wave + закрытие иконок/стекла (2026-11-11)

**Статус:** Wave A (иконки+P4+P5) ✅ · Wave B (большие картинки H01–H28) ⏳ CapCut-пакет готов · art по GO  
**Референсы:** `docs/competitors/screenshots_life360_hero_wave_2026-11-11/L360_H01…H28`  
**CapCut / AI пакет (Загрузки):** `~/Downloads/ALADDIN_CapCut_Hero_Wave_B_2026-11-11/`  
→ **канон промптов:** `KAPCUT_PROMPTY_V2_TOP.md` (роль AI · без красного маркера · размеры QA)  
→ картинки: `KAPCUT_OTPRAVIT_SYUDA/01…23` · все 28 рефов: `refs/`  
→ `00_START_HERE_RU.md` · `AGENT_SELF_PROMPT.md`  
**Копия в репо:** `CAPCUT_ALL_PROMPTS_WAVE_B.md` (этот каталог; V2 в Downloads — SSOT для CapCut)  
**FIG-L Figma (in-app UI):** `b6gFc8GUtWC6ncPgb6X6II` · **не** трогать Onboarding `KvkUdyb5…` / OB_*  
**Бренд:** ALADDIN gold `#F59E0B` + storm · **не** копировать Life360 purple 1:1  
**Связанные:** `PLAN_ENTRY_ICONS_MAP_UNICORN_2026-11-11.md` · `FAMILY_SAFETY_UNIFIED_ML_PLAN_2026-11-09.md` §7

---

## 0. Wave A — план ↔ факт (закрыто 2026-11-11)

| Тема | В плане? | Факт |
|------|----------|------|
| 3 стиля Классика / Золото / Значки | да | ✅ |
| Размеры вкладок/плиток/дверей/тарифов/семьи | да | ✅ |
| Места Main / Удобный / Тарифы / Семья | да | ✅ |
| FAB 48 · glyph ~34 · tabs 22 | да | ✅ |
| Чипы карты = Классика | да | ✅ |
| Пин L=56 + дыхание ±8%/1.8с · Reduce Motion | P4 | ✅ |
| FAB×4 press spring | P4 | ✅ |
| SOS круг + кольцо (hold 3с) | P4 | ✅ |
| Стекло карточек: Классика solid · Золото/Значки glass | P5 | ✅ `aladdinProductCard` |
| QR / логика маршрутов / bump | вне | не трогали |
| OB-QA / DEV-88 глазами | да | ⏳ владелец |
| Bump 20 | да | ⏳ только GO |

**Как делали (фиксация):**

1. Glyph-first PNG → Assets → `AliveGlyph` / `AliveIconID`  
2. Wire Main / SimpleHome / Tariffs / Family / Where hub tabs  
3. P4 motion в `FamilyHubAvatarPinView` + `MapFabPressStyle` + `FamilySOSHoldButton`  
4. P5: `ClassicSolidCardStyle` + `AladdinProductCardStyle` · Main/Удобный/Семья/Тарифы  

**Остаток Wave A (не код):** глаза на карте P4 · Settings Золото↔Классика для стекла · OB-QA · DEV-88.

---

## 1. Инструменты: Figma vs CapCut (канон)

| Тип работы | Где | Почему |
|------------|-----|--------|
| UI-кадры in-app (sheet, empty, SOS tips, place card layout) | **Figma FIG-L** | Слои, размеры pt, export PNG → Assets, wire Swift |
| 3D-герои (семья, машина, собака, замок, календарь, ландшафт-пин) | **CapCut** (или gen → PNG) → импорт в Figma | Сложный объём/свет; CapCut = композит/реклама |
| App Store / ASC / реклама 1290×2796 | **Figma Marketing** board + опц. CapCut motion | Одни герои → два выхода: app + store |
| Короткие ролики рекламы | **CapCut** | Motion; статичный кадр всё равно в Figma |

**Правило:** сначала **место в ALADDIN + размер pt**, потом art, потом wire. Не рисовать «в воздух».

**Запрет без GO:** `xcodebuild` · bump · commit bot · mock family · правка OB_*.

---

## 2. Размеры-канон (куда вставлять)

| Слот | Canvas / pt | Notes |
|------|-------------|-------|
| In-app phone frame | **393×852** | FIG-L канон |
| Empty / tip hero | **ш ~320–360 · в ~180–220** | внутри sheet |
| Place card 3D thumb | **96×96 … 120×120** | справа от адреса |
| Calendar / lock / car / pet thumb | **72–120** | leading illustration |
| Trip card car | **80–112** | справа от маршрута |
| SOS tip carousel | full sheet · illust **~280×200** | Safety tab |
| Soft paywall / driving unlock | card **~361×220** illust | Driving tab |
| App Store shot | **1290×2796** (6.7") | ASC |
| Invite OG preview | **1200×630** | link share |
| Marketing carousel card | **~1080×1920** или phone-in-card | ads |

---

## 3. Куда в ALADDIN (логические двери)

| Зона приложения | Что уже есть | Что усиливаем Wave B |
|------------------|--------------|----------------------|
| Where · Location sheet | чипы, семья, invite card | bubble L02 · empty 3D · place thumbs |
| Where · Places | места Дом/Школа | **H14** ландшафт-пин + календарь |
| Where · Pets | chip Питомцы | **H15/H17** pet heroes + picker art |
| Where · Events | события | calendar art |
| Where · Driving | отчёты | **H16** lock paywall · **H18** car на trip · speed/crash tips |
| Where · Safety | SOS hold ✅ | **H06–H13** SOS education carousel |
| Family / Invite | код/ссылка | **H20** OG + invite beauty |
| Soft paywall / Subscription tab | premium | marketing stills reuse |
| App Store / ads | ASO | **H01–H05, H21–H28** |
| Onboarding ALADDIN | OB_* **не трогаем** | семья **H13/H19** → Family empty / «создать круг» **внутри Where/Family**, не OB |

---

## 4. Матрица H01–H28 (владелец # → план)

> Файлы `L360_Hxx` = порядок вложений в чат. Сверять по картинке; смысл = колонка «Тема».

| # | Тема (владелец) | Класс | Куда в ALADDIN | Инструмент | Размер insert | Wire / задача | Статус |
|---|-----------------|-------|----------------|------------|---------------|---------------|--------|
| 1–2 | Live location · phone-in-card | **ASO / tip** | ASC shot + optional Where tip «Где семья» | CapCut mockup → Figma Marketing | 1290×2796 · tip 361×220 | COPY ALADDIN · gold · не purple | ⏳ |
| 3–5 | Place alerts / history / tips | **ASO + in-app tip** | Where empty / Places education | Figma layout + CapCut hero | tip 361×220 | Carousel 3 cards | ⏳ |
| 6 | SOS intro «кнопка пригодится» | **In-app** | Safety · SOS onboarding sheet | Figma | 393×852 sheet · illust 280×200 | ALADDIN SOS (семья, не «скорая едет») | ⏳ |
| 7–8 | SOS tips mid | **In-app** | тот же carousel | Figma | same | 3 dots pager | ⏳ |
| 9–12 | SOS / safety tips cont. | **In-app** | Safety carousel | Figma | same | Чеклист сценариев RU | ⏳ |
| 13 | Семья красивая (маркер) | **Hero** | Family empty / «Создайте семью» · **не OB_*** | CapCut 3D → Figma | 320×220 | `FIG-L` empty family | ⏳ |
| 14 | Place 3D pin+ландшафт + календарь | **In-app** | Place detail sheet | CapCut thumbs → Assets | **120×120** pin-land · **96×96** calendar | Places + Events CTA | ⏳ |
| 15 | Собака красивая | **Hero** | Pets empty / pet card | CapCut → Assets | 120–160 | Pets chip empty | ⏳ |
| 16 | Замок 3D золотой | **In-app** | Driving soft-paywall «откройте отчёты» | CapCut → Assets | 140×140 | DrivingReports paywall | ⏳ |
| 17 | Питомцы dog/cat/other | **In-app** | Add pet type picker | Figma circles + CapCut doodle | 88×88 ×3 | Pets onboarding | ⏳ |
| 18 | Машина 3D большая | **In-app** | Trip history row | CapCut → Assets | **96–112** | Driving trip card leading/trailing | ⏳ |
| 19 | Семья permissions | **Hero** | Family permissions / Always Allow art | CapCut → Figma | 320×220 | `FIG-L18` reuse | ⏳ |
| 20 | Приглашение / OG | **Share + ASO** | Invite share link preview | Figma OG 1200×630 | 1200×630 | Deep link card · ALADDIN logo | ⏳ |
| 21 | Карта: люди+питомцы+вещи | **ASO + empty** | Marketing + Where empty «всё на карте» | CapCut → Marketing | 1290×2796 · empty 360×200 | Не копировать Life360 path purple | ⏳ |
| 22–24 | Рекламные страницы | **Ads/ASC** | App Store + site | CapCut + Figma | 1290×2796 | Batch ASO | ⏳ |
| 25 | Уведомления: кто/что произошло | **In-app + ASO** | Notifications permission preview · inbox samples | Figma | sheet 393 · rows 72 | У нас **будет** family alerts (прибыл/SOS/battery) — UI preview да; тексты ALADDIN | ⏳ |
| 26–28 | Рекламные / motion / history | **Ads/ASC** | ASC gallery | CapCut + Figma | 1290×2796 | После in-app heroes | ⏳ |

### 4.1 Ответ на H25 «у нас так же будет?»

**Да, по смыслу:** семейные пуши (место / SOS / батарея / не прибыл) уже в контуре ALADDIN.  
**Картинка H25** = превью «зачем уведомления» + примеры строк. Делаем **свой** UI (storm/gold, Аладдин), не клон Life360. Логику «скорая уже едет» **не** копируем — у нас честный family notify.

---

## 5. Очередь работ Wave B (наилучший порядок)

```
B0  GO владельца «GO Wave B hero art»
B1  Inventory: пометить маркером файлы H13–H18 в папке (уже в чате)
B2  In-app first (польза в продукте):
    H14 place thumbs → H18 car → H16 lock → H15/H17 pets → H06–H12 SOS carousel → H13/H19 empty family
B3  Share: H20 invite OG
B4  ASO/ads: H01–H05 · H21–H24 · H26–H28 (можно параллельно дизайном)
B5  Wire Swift по одному слоту + verify sizes
B6  Owner eyes · затем optional bump
```

**Не делать в B2:** live pet GPS · roadside dispatch · копирование purple brand · правка OB_*.

---

## 6. Self-prompt для агента (копировать в новый чат)

```
ROLE: ALADDIN principal iOS + product. Mech Pilot. Owner = GO.

CONTEXT:
- Repo: ALADDIN_iOS master. Icons/P4/P5 DONE (AliveGlyph · pin breathe · FAB spring · SOS ring · aladdinProductCard).
- SSOT this wave: docs/competitors/figma_preview_fig_l/PLAN_LIFE360_HERO_ART_WAVE_2026-11-11.md
- Refs: docs/competitors/screenshots_life360_hero_wave_2026-11-11/L360_H01…H28
- FIG-L Figma b6gFc8GUtWC6ncPgb6X6II. NEVER edit Onboarding KvkUdyb5 / OB_*.
- Brand: gold #F59E0B + storm. No Life360 purple clone. No QR/logic breakage. No bot in iOS commit. No xcodebuild without «GO на сборку».

GOAL: For each Hxx the owner names — (1) confirm ALADDIN insert slot + pt size from §2–§4, (2) produce ALADDIN-branded art (Figma UI / CapCut 3D still), (3) export Assets, (4) wire visual-only, (5) report table слой|size|file|✅.

BEST PATH:
1. Ask which H# batch if unclear; default next open row in §4.
2. Open ref image. List 1–3 circled elements.
3. Map to ALADDIN screen (Where Places/Pets/Driving/Safety/Family/ASC).
4. Tool: UI chrome → Figma; 3D hero → CapCut then upload Figma/Assets.
5. Sizes from §2. Name assets ICON_ALIVE_HERO_Hxx_* or FIG_Lxx_*.
6. Wire without changing SOS hold logic / map routes / chips Classic policy.
7. Evidence: path + size pt + screenshot note. Stop for owner eyes.

PHRASE GO examples:
- GO Wave B H14 place thumbs
- GO Wave B SOS carousel H06-H12
- GO Wave B ASO H01-H05
```

---

## 7. GATES перед art/wire каждого H#

- [ ] Слот in-app или только ASO?  
- [ ] Размер pt записан  
- [ ] ALADDIN copy (не Life360 trademark)  
- [ ] Gold/storm, не purple clone  
- [ ] Не ломает QR/hold/GPS  
- [ ] Figma vs CapCut выбран по §1  
- [ ] Owner GO на этот H# / батч  

---

## 8. Связь с PLAN_ENTRY

В `PLAN_ENTRY_ICONS_MAP_UNICORN_2026-11-11.md` Wave A закрыта; **следующая фаза = этот файл (Wave B)**.
