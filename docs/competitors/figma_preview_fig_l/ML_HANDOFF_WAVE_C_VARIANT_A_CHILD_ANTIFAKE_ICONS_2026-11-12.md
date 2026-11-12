# ML HANDOFF — Wave C · Вариант A «всё как Семья»

**Дата:** 2026-11-12  
**Владелец / пилот:** человек (решения + GO)  
**Исполнитель:** другая ML-система (этот документ = полный бриф)  
**Стиль зафиксирован владельцем:** **Вариант A** — один язык с Wave A / Семья (F01–F04)  
**Статус продукта:** **PRODUCTION** iOS app `ai.aladdin` · семья / parental / antifake — живые пользователи  
**Ставка:** от ясности UI зависят доверие родителей и скорость защиты от мошенников — **ноль халтуры, ноль «примерно»**

Рабочий корень (единственный):

`/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`

Перед правками: `git rev-parse --show-toplevel` · `git branch --show-current` (**только `master` для iOS commit**) · `git status --short`

---

## 0. Промпт роли (копировать в старт чата другой ML)

```
Ты — principal iOS / product design engineer с 15+ годами опыта (SwiftUI, HIG,
семейный safety UX, App Store production). Репозиторий ALADDIN_iOS — прод.

Миссия Wave C Variant A: заменить SF/emoji на soft-clay AliveGlyph
(Классика / Золото Glyph / Значки Black) на экранах «Ребёнок» и «Проверить»
ТОЧНО как уже сделано для Семьи F01–F04 и Wave A. От качества зависят
тысячи семей и защита от мошенников — работай как staff, не как junior.

Канон исполнения:
1) Прочитай ЦЕЛИКОМ этот handoff + PLAN_ENTRY_ICONS_MAP_UNICORN + AliveIconStyle.swift
2) GATES до кода: список слотов C/P/AF + размеры + файлы wire (уже в § ниже)
3) Art → Assets ICON_G1_<ID>_Glyph + _Black → AliveIconID → AliveGlyph wire
   по ОДНОМУ слоту (не mass)
4) Классика = существующий SF/emoji fallback внутри AliveGlyph { }
5) НЕ трогать: OB_*, Draft ASC A–D, telegram_stars_shop_bot, .env, VPN secrets,
   LocalizationManager rewrite, pin/chips Where канон, xcodebuild без GO
6) Commit только по фразе владельца «Сохраняй»; push только «GO на push»
7) Evidence: таблица слот|asset|size|file:line|Classic/Gold/Black OK
8) Не выдумывать ID/пути — только из этого документа
9) Если неясно — ОДИН вопрос владельцу с вариантами A/B/C, не молчаливый guess
10) Говори кратко по делу; код минимальный; красота = ясность + единый язык

Стиль иконок Variant A (LOCKED):
- Soft clay / matte 3D, ALADDIN gold #F59E0B + storm navy #0B1220
- НЕ purple Life360, НЕ flat Material, НЕ neon lab tiles (это был Variant B — ОТКЛОНЁН)
- Табы Антифейк = маленькие знакомые глифы в ряду, КАК ряды Семьи — не «лаборатория»
```

---

## 1. Контекст: что уже сделано (не переделывать)

### Wave A ✅ (образец)

| Что | План | Факт |
|-----|------|------|
| Settings 3 стиля | Классика / Золото / Значки | `AliveIconDiscStyle` · key `aladdin_icon_disc_style` |
| Wire helper | `AliveGlyph` | `Shared/Components/AliveIconStyle.swift` |
| Naming | `ICON_G1_<AliveIconID.rawValue>_Glyph` / `_Black` | Blue **запрещён** |
| Семья | F01–F04 | Members / Chat / Groups / Invite · size **28–32** |
| Удобный двери | A07 Check · A08 Child · A09 Where | уже Glyph — **не перерисовывать** |
| P4/P5 | pin breathe · FAB spring · glass cards | ✅ |

Канон размеров Wave A (повтор):

| UI | display pt | 2x | 3x |
|----|------------|----|----|
| List / family row | **28** | 56 | 84 |
| Door prominent | **36** | 72 | 108 |
| Door normal | **32** | 64 | 96 |
| Main tile | **40** | 80 | 120 |

Планы-образцы:
- `docs/competitors/figma_preview_fig_l/PLAN_ENTRY_ICONS_MAP_UNICORN_2026-11-11.md`
- `docs/competitors/figma_preview_fig_l/PLAN_LIFE360_HERO_ART_WAVE_2026-11-11.md` §0 Wave A ✅

### Wave B ✅ (не смешивать с Wave C)

- ASC H01–H28 + **Draft A–D** → грузить в App Store (**H\* + Draft**)  
- Файлы: `docs/AppStore/asc_screenshots_wave_b_2026-11-12/` · `~/Downloads/…/07_FITTED_1290x2796/`  
- Draft = **только ASC**, никогда не вставлять в Ребёнок/Проверить  

### Variant A vs B (для ясности)

| | A (LOCKED) | B (отклонён) |
|--|------------|--------------|
| Ребёнок / ПК | clay Glyph как Семья | то же |
| Табы Проверить | **те же глифы в ряду** | крупные «lab» плитки |
| Визуальный язык | **один** | два диалекта |

---

## 2. Как должно ВЫГЛЯДЕТЬ (Variant A)

### Общий вид
- Фон экранов уже storm / product cards — **не менять layout**.  
- Меняется **только иконка слева** (или в табе): при Золото/Значки — PNG глиф; при Классика — нынешний SF/emoji.  
- Цвет акцента карточек/табов (gold selected) — **оставить** как сейчас.  
- Глиф: читаемый силуэт на прозрачном фоне, без мелкого текста внутри PNG, без Life360, без водяных знаков CapCut.

### Метафоры (art brief одной строкой)

| ID | Метафора (clay) |
|----|-----------------|
| C01_MapVis | сложенная карта / пин на карте |
| C02_MapAll | 3 силуэта семьи (можно близко к F03) |
| C03_MapMe | 1 силуэт |
| C04_Pause | пауза в круге / щит+пауза |
| C05_Sites | глобус |
| C06_Limit | песочные часы |
| C07_Bedtime | луна / zzz |
| C08_Reward | подарок (не путать с большим U01 единорогом на CTA Семьи) |
| C09_Minutes | часы |
| C10_ChildScreen | геймпад |
| P01_ContentBlock | замок |
| P02_Time | таймер |
| P03_Monitor | глаз / взгляд |
| P04_Geo | пин локации |
| P05_Reports | столбцы/отчёт |
| P06_More | шестерёнка (reuse M04 ок после ревью) |
| P07_Bypass | сирена / щит-тревога |
| AF01_Text | кавычки / абзац |
| AF02_Doc | документ + рамка скана |
| AF03_Audio | waveform |
| AF04_Video | камера |
| AF05_Call | трубка |
| AF07_Ask | sparkles (reuse M01 ок) |
| AF08_FamilyDB | 3 человека / семейный щит |

**AF06 Trust** — optional v1.1 (можно оставить SF).

---

## 3. Полный реестр слотов → размеры → куда wire

### 3.1 Ребёнок — `Screens/SimpleHomeScreen.swift`

Функции: `payPainsChildDoorSheet` · `familyMapVisibilityCard` · `payPainsDoor(aliveIcon:)`

| ID | Место | Classic fallback | Wire size | Как вставлять |
|----|-------|------------------|-----------|---------------|
| C01_MapVis | header «Кто виден на карте» | `map.fill` | **28** | заменить `Image(systemName: "map.fill")` → `AliveGlyph(id: .mapVis, size: 28) { Image(systemName: "map.fill")… }` |
| C02_MapAll | capsule «Вся семья» | `person.3.fill` | **18** | Glyph в HStack кнопки; не раздувать capsule |
| C03_MapMe | capsule «Только я» | `person.fill` | **18** | то же |
| C04_Pause | door Пауза `prominent: true` | `pause.circle.fill` | **36** (уже formula prominent) | `payPainsDoor(..., aliveIcon: .childPause, …)` |
| C05_Sites | door Сайты | `globe` | **32** | `aliveIcon: .childSites` |
| C06_Limit | door Лимит | `hourglass` | **32** | `aliveIcon: .childLimit` |
| C07_Bedtime | door Сон | `moon.zzz.fill` | **32** | `aliveIcon: .childBedtime` |
| C08_Reward | door Награда | `gift.fill` | **32** | `aliveIcon: .childReward` |
| C09_Minutes | door Минуты | `clock.fill` | **32** | `aliveIcon: .childMinutes` |
| C10_ChildScreen | door Экран ребёнка | `gamecontroller.fill` | **32** | `aliveIcon: .childScreen` |

**Не трогать:** chevron, toolbar Done, StormMeshBackground, тексты, navigation.

`payPainsDoor` уже принимает `aliveIcon: AliveIconID?` — **использовать**, не invent второй helper.

### 3.2 Родительский контроль (Семья) — `Screens/02_FamilyScreen.swift`

Struct `FamilyParentalControlCard` сейчас: `icon: String` emoji · `.font(.system(size: 28))` · frame height 32.

**Изменение API (минимальное):**
```swift
// добавить:
var aliveIcon: AliveIconID? = nil
// в body вместо Text(icon):
AliveGlyph(id: aliveIcon ?? /* only if non-nil */, size: 28) {
    Text(icon).font(.system(size: 28))
}
```
Или: `aliveIcon` required for new cards + keep `icon` as Classic string.

| ID | Карточка | Classic | Wire size |
|----|----------|---------|-----------|
| P01_ContentBlock | Блокировка контента | 🔒 | **28** |
| P02_Time | Управление временем | ⏱️ | **28** |
| P03_Monitor | Мониторинг | 👀 | **28** |
| P04_Geo | Геолокация | 📍 | **28** |
| P05_Reports | Отчёты | 📊 | **28** |
| P06_More | Дополнительно | ⚙️ | **28** |
| P07_Bypass | Защита от обхода | 🚨 | **28** |

**Не трогать:** badge/statusText/metric layout · unicorn reward CTA 🦄 · referral 🎁 (out of Wave C v1).

### 3.3 Проверить — `Screens/AntifakeHubScreen.swift`

| ID | Место | Classic SF | Wire size |
|----|-------|------------|-----------|
| AF01_Text | tab Текст | `text.quote` | **28** |
| AF02_Doc | tab Документ | `doc.text.viewfinder` | **28** |
| AF03_Audio | tab Голос | `waveform` | **28** |
| AF04_Video | tab Видео | `video.fill` | **28** |
| AF05_Call | tab Звонок | `phone.fill` | **28** |
| AF07_Ask | card «Спросить помощника» | `sparkles` | **28** |
| AF08_FamilyDB | семейная база / share family | `person.3.fill` | **28** |

Wire pattern для табов:
```swift
enum AntifakeHubTab {
  var aliveIcon: AliveIconID { … }
  var iconName: String { … } // Classic
}
// tabPicker:
AliveGlyph(id: tab.aliveIcon, size: 28) {
  Image(systemName: tab.iconName).font(.body.weight(.semibold))
}
```

**Визуал таба Variant A:** плитка selected gold остаётся; внутри — глиф 28, подпись caption как сейчас.  
**НЕ** увеличивать таб до «lab tile 48» (это B).

**Не трогать v1:** paste/check/translate buttons · input mode pills · info.circle · xmark share tip · premium lock UI chrome.

---

## 4. Assets + enum (точные имена)

Добавить в `AliveIconID` (пример rawValue — **соблюсти**):

```
C01_MapVis, C02_MapAll, C03_MapMe,
C04_Pause, C05_Sites, C06_Limit, C07_Bedtime, C08_Reward, C09_Minutes, C10_ChildScreen,
P01_ContentBlock, P02_Time, C03… → P03_Monitor, P04_Geo, P05_Reports, P06_More, P07_Bypass,
AF01_Text, AF02_Doc, AF03_Audio, AF04_Video, AF05_Call, AF07_Ask, AF08_FamilyDB
```

Файлы imageset:
`ICON_G1_C04_Pause_Glyph` · `ICON_G1_C04_Pause_Black`  
(аналогично для каждого ID)

`assetName(for:)` уже строит `ICON_G1_\(rawValue)_Glyph` — rawValue **должен** совпадать с суффиксом после `ICON_G1_`.

**Reuse (после ревью, не ломая смысл):**
- C02 ≈ F03_Groups  
- P06 ≈ M04_Settings  
- AF07 ≈ M01_AIFriends  

Если reuse — wire существующий `AliveIconID`, **не** дублировать PNG.

---

## 5. Порядок выполнения (строго)

### Phase 0 — GATES (до art)
- [ ] Прочитан этот handoff  
- [ ] Подтверждено Variant **A**  
- [ ] Список ID = §3 (без лишних)  
- [ ] Запреты §7 понятны  

### Phase 1 — Art (CapCut или FIG-L) по батчам
1. **Batch Child doors** C04–C10 (7) — самый частый UX  
2. **Batch Parental** P01–P07 (7)  
3. **Batch Antifake tabs** AF01–05 (5)  
4. **Batch map + CTA** C01–C03 · AF07–AF08  

Каждый PNG: прозрачный фон · квадрат · субъект inset 8–10% · gold/navy · без текста · без watermark.

Export в `Assets.xcassets` imagesets @1x/@2x/@3x **или** один PDF/template как в Wave A (смотреть существующие `ICON_G1_F01_*`).

### Phase 2 — Code wire (по одному батчу)
1. Extend `AliveIconID`  
2. Child doors `aliveIcon:`  
3. Parental card API + callers  
4. Antifake tabs + ask + family DB  
5. Map visibility icons  

### Phase 3 — Verify (без xcodebuild пока нет GO)
- Grep: каждый новый слот имеет `AliveGlyph`  
- Manual: Settings → Классика / Золото / Значки на трёх экранах  
- a11y: labels не сломаны (glyph `accessibilityHidden`, label на кнопке)  
- Таблица evidence владельцу  

### Phase 4 — Human
- Owner глаза  
- «Сохраняй» → commit **только** iOS paths  
- GO на сборку → sim QA  

---

## 6. Definition of Done (Wave C Variant A)

| # | Критерий | Evidence |
|---|----------|----------|
| 1 | Все слоты §3.1–3.3 wired | diff + grep |
| 2 | Classic fallback = старый SF/emoji | sim / preview |
| 3 | Gold/Black показывают PNG | Settings toggle |
| 4 | Нет Blue assets в wire | code review |
| 5 | Layout/spacing экранов не разъехались | screenshot owner |
| 6 | Antifake tabs = glyph-in-row, не lab tiles | visual |
| 7 | Нет Draft ASC / OB_* в diff | `git diff --name-only` |
| 8 | Нет bot / .env в commit | staged check |
| 9 | Отчёт таблица слот\|size\|asset\|file | chat |

---

## 7. Запреты (hard)

- `*_Blue` disc  
- Mass rewrite `LocalizationManager.swift`  
- `telegram_stars_shop_bot/` · `.env` · VPN secrets handoff  
- Onboarding OB_00…07 Figma / wordmark в этом пакете  
- Замена Draft A–D / ASC H*  
- `sfm_mock` / mock parental  
- `xcodebuild` / Simulator без **GO на сборку**  
- Commit без **«Сохраняй»** · push без **GO на push**  
- Branch ≠ `master` для iOS commit  
- Variant B lab tiles «чтобы было круче» без нового GO владельца  

---

## 8. Связанные open items (НЕ Wave C — не брать в этот пакет)

| Item | Где |
|------|-----|
| ASC upload H*+Draft | Wave B · файлы готовы · upload когда скажет владелец |
| Tip wire Where→Езда | ✅ DONE 2026-11-12 · не брать |
| SOS mid-tips H07–H12 | ✅ DONE wire (SF mid) · CapCut art optional · не брать |
| Карта путей / антидубль | `ARTIFACT_MAP_WAVE_ABC_NO_DUPES_2026-11-12.md` — читать первой |
| OB_01 wordmark выше головы | Figma SYNC отдельно |
| OB-QA / DEV-88 / bump 20 | Wave A remainder |

---

## 9. Быстрый старт другой ML (чеклист дня 1)

1. Открыть workspace `ALADDIN_iOS`  
2. Вставить **§0 промпт роли**  
3. Прочитать `AliveIconStyle.swift` + F01 wire в `02_FamilyScreen.swift` (~3304)  
4. Прочитать `payPainsDoor` в `SimpleHomeScreen.swift` (~408)  
5. Спросить владельца: **«GO Wave C art Batch1 C04–C10?»**  
6. После art — wire Batch1 → evidence → стоп → следующий batch  

---

## 10. Контакты канона в репо

| Документ | Путь |
|----------|------|
| Этот handoff | `docs/competitors/figma_preview_fig_l/ML_HANDOFF_WAVE_C_VARIANT_A_CHILD_ANTIFAKE_ICONS_2026-11-12.md` |
| Краткий план Wave C | `…/PLAN_WAVE_C_CHILD_ANTIFAKE_ICONS_2026-11-12.md` |
| Wave A icons | `…/PLAN_ENTRY_ICONS_MAP_UNICORN_2026-11-11.md` |
| Wave B ASC | `…/PLAN_WAVE_B_CAPCUT_TODAY_HANDOFF_2026-11-12.md` |
| ASC checklist | `docs/AppStore/asc_screenshots_wave_b_2026-11-12/CHECKLIST_WAVE_B_H20_23_AND_LOC.md` |
| Mech Pilot | `.cursor/rules/mech-pilot.mdc` · skill `aladdin-mech-pilot` |
| No mock | `.cursor/rules/prod-no-mock-bypass.mdc` |

---

**Владелец зафиксировал Variant A.**  
Следующая фраза для старта исполнения: **«GO Wave C art Batch1»** (или полный **«GO Wave C Variant A»**).
