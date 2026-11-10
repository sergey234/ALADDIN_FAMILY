# Family Safety — единый план для ML (SSOT · без повторов)

**Дата обновления:** 2026-11-10 · **Build в коде:** 19 · **Канон:** B · no mock  
**Этот файл = единственная очередь.** Остальные планы — ссылки, не дублировать задачи.  
**MAP-95:** ✅ **CLIP PASS** (владелец 2026-11-10) — канон настроек §3.1.

| Было 3 куска | Теперь |
|--------------|--------|
| `WHERE_PHONE_SHEET_SETTINGS_BASELINE_BEFORE_S1_…` | §2–3 здесь (baseline + S1/S1b/S2 журнал) |
| `FIGMA_FAMILY_SAFETY_ML_PROMPTS.md` | §7 здесь (полный FIG-L список) · детали промптов — там |
| Этот UNIFIED + REMAINING/MASTER | §5–6 очередь · MASTER/REMAINING = архив статусов |

**Читать рядом (не копировать очередь):**  
`FAMILY_SAFETY_KASPERSKY_LIFE360_MASTER_PLAN.md` (§ Max-UI берём/не берём) ·  
`FIGMA_FAMILY_SAFETY_ML_PROMPTS.md` (текст AI-промптов) ·  
`FAMILY_LOCATION_CANON_B_PLAN_2026-11-09.md`

**Запрет:** трогать Onboarding Figma `KvkUdyb5…` / OB_* в волне FIG-L · commit bot в iOS · mock на family/map.

---

## 0. Промпт агенту (копировать)

```text
Principal iOS + Family Safety ALADDIN. Mech Pilot.
SSOT: docs/competitors/FAMILY_SAFETY_UNIFIED_ML_PLAN_2026-11-09.md
Карта sheet 95%: **MAP-95-CLIP ✅ PASS** — канон §3.1. Не откатывать на overlay/S2 как primary на iOS 15.
«Телефон потерян»: только scroll (P0-6), sticky ОТКАТ — не возвращать.
Онбординг Hero_08 CapCut1 ✅ · OB-QA = только глаза в симе (не код).
Build 19 на master (e2f01b79 + PlaceAddress 09afdaf7). Bump 20 — только GO.
FIG-L = НОВЫЙ Figma file (§7 + §7.0 handoff). Не OB_*. Create file — только GO владельца.
```

---

## 1. Эталон владельца (скрины)

| Скрин | Что должно быть |
|-------|-----------------|
| Life360 (белый sheet) | Дверь почти на весь экран; сверху узкая полоска карты; 5 чипов; tab bar снизу виден |
| Наш sheet (Семья) | ✅ CLIP: full `cover=0.95` `strip=0.05` (лог 2026-11-10) |
| Онбординг «Где семья» | Hero_08 без обреза рук · CapCut1 fitted ✅ |

---

## 2. Первоначальные настройки sheet (ДО трёх правок S1/S1b/S2)

**Файл:** `Screens/WhereIsPhoneScreen.swift`  
**Снимок:** `docs/competitors/WHERE_PHONE_SHEET_SETTINGS_BASELINE_BEFORE_S1_2026-11-09.md`

| Параметр | Значение «как работало / mid» |
|----------|-------------------------------|
| `sheetExpansion` start | `0.08` |
| Peek / Half / Full snap | `0.08` / `0.42` / `1.0` |
| Drag thresholds | `<0.22` peek · `<0.62` half · else full |
| Высота | `fraction = 0.22 + 0.73 * expansion` · `min(usable×0.95, …)` |
| Чип не-Events | если `<0.55` → поднять до **0.55** (mid) |
| Чип Events | `expansion = 1.0` + scrollTo lost |
| Lost | только карточка в scroll |
| Layout | VStack: header + Spacer + FAB + sheet(height) + tabBar |

**Откат к этому baseline:** только по явному GO (сломает MAP-95). Рабочий канон = **§3.1 CLIP**, не эта таблица.

---

## 3. Журнал MAP-95 — ✅ PASS через CLIP

### Цель
Sheet ≈ **95%** высоты (полоска карты 5–8% сверху), любой чип → full — как Life360.

### 3.1 Канон рабочих настроек (НЕ ЛОМАТЬ без GO)

**Файл:** `Screens/WhereIsPhoneScreen.swift` · функция `locationLife360CanvasS1b`  
**Runtime канона:** **CLIP (S1b) primary на всех OS** (вкл. iOS 16+) — Life360 жест peek / mid / full 95%.  
**S2** (`presentationDetents`) — только emergency fallback (`preferLocationSystemSheetS2 = false` по умолчанию).

| Параметр | Канон (PASS) |
|----------|----------------|
| Layout | **`VStack(spacing: 0)`**: map → sheet → tabBar |
| Map | `frame(width: geoW, height: mapStripH).clipped()` — **не** full-bleed под overlay |
| `mapStripH` | `max(36, geoH − sheetH − tabBarH)` |
| `tabBarH` | `64` |
| `sheetExpansion` start | `0.08` (peek) |
| Snap points | peek `0.08` · half `0.42` · full `1.0` |
| Drag thresholds | `<0.22` → peek · `<0.62` → half · else → full |
| `fullH` / `locationSheetFullTarget` | `max(120, mapHeight * 0.95 − tabBarH)` |
| Peek / half height | `peekH = max(110, usable * 0.12)` · `halfH = usable * 0.48` · `usable = mapHeight − tab` |
| Lerp | `expansion ≤ 0.42`: peek→half; else half→full |
| Чип | chip → `expandLocationSheetToFull()` только если `sheetExpansion < 0.95` · iOS 15 `sheetExpansion = 1.0` |
| Lost CTA | только карточка в scroll (P0-6); **sticky запрещён** без нового GO |
| FAB | hide / weak hit при `expansion > 0.55` |
| DIAG лог | `WHERE_PHONE sheet S1b height` · поля `sheetH` `geoH` `mapStrip` `cover` `strip` |

**Почему заработало (корень):**  
MKMapView (Metal) рисовался **поверх** SwiftUI `.overlay` sheet → в логе `sheetH=729`, на экране mid.  
CLIP отдаёт карте только `mapStripH` в **layout** + `.clipped()` → Metal не занимает зону sheet.

**Evidence PASS (владелец, Console 2026-11-10 ~00:33):**

| Состояние | Лог |
|-----------|-----|
| appear peek (до Device QA) | `sheetH=207 geoH=835 mapStrip=563 expansion=0.08 cover=0.33 strip=0.67` |
| peek target (Device QA 2026-11-10) | `peekH≈usable×0.12` · **GATES peek: `strip ≥ 0.85` · `cover ≤ 0.15`** |
| half snap | `sheetH=370 mapStrip=400 expansion=0.42 cover=0.52 strip=0.48` |
| **full snap** | `sheetH=729 mapStrip=41 expansion=1.00 fullTarget=729 cover=0.95 strip=0.05 tab=64` |

GATES full: `cover ≥ 0.90` · `strip ≤ 0.08` — **PASS**.  
GATES peek (симметрия): `strip ≥ 0.85` · `cover ≤ 0.15` — Device QA 2026-11-10.

### 3.2 Что пробовали и почему FAIL (не повторять)

| ID | Что | Device |
|----|-----|--------|
| S1 | абсолютная высота в общем VStack с header/FAB | mid — SwiftUI сжимал `frame(height:)` |
| S1b | ZStack bottom sheet+tab; карта full-bleed | mid |
| S2 | iOS 16+ `.sheet` + detents medium/0.95 | на **15.2** путь мёртв; UI mid |
| HARD | sheet в `.overlay(alignment: .bottom)` + явный height | лог `sheetH=729` OK · **UI mid** — Metal z-order |
| **CLIP** | VStack mapStrip.clipped + sheet + tab | ✅ PASS |

### 3.3 Запреты после PASS
- Не возвращать full-bleed map + sheet overlay / ZStack поверх MKMapView  
- Не делать S2 primary на deploy 15.2  
- Не sticky «Телефон потерян» без GO  
- Не «чинить» высоту через PresentationDetent @State (ломает iOS 15 compile)  
- UIKit / S3 — только если CLIP регрессирует (новый баг, не «на всякий случай»)

---

## 4. «Телефон потерян» — что сломали и как вернули

| Шаг | Что | Вердикт владельца |
|-----|-----|-------------------|
| P0-6 | Карточка в scroll + Events → sheet lift + scrollTo | ✅ оставить |
| P0-7 / plan E | **Sticky bar** title+CTA всегда над tab bar | ❌ «не двигается / всё в одном месте / некрасиво» |
| Откат | Удалён `stickyLostBar`; chip logic временно как P0-6; потом снова chip→full в S1 | **Сейчас: только scroll-карточка** |

**Правило:** не возвращать sticky без нового явного GO. CTA = `openLocator()` в карточке внизу scroll (после Events).

---

## 5. Онбординг — проблемы и фиксы (не путать с картой)

| Проблема | Причина | Что сделали | Статус |
|----------|---------|-------------|--------|
| Отступы со всех сторон на части страниц | Stub PNG 02–07 ~200KB + `scaledToFit` | Вернули PNG **00–07 из бэкапа 29.10** (`pay_pains` zip) + Fill + zoom 1.09 | ✅ |
| «Где семья» руки обрезаны | Hero_08 edge-to-edge 0% L/R | CapCut1 → fit 1179×2556 + ~6% side pad + zoom 1.09 для 08 | ✅ владелец: «встало нормально» |
| Случайный Fit после «отката» | `git checkout` stub'ов | Не повторять checkout assets без сверки с сейфом 29.10 | — |

**Не трогать:** Hero_08 после CapCut1 без GO. OB_* Figma — только отдельный sync GO.

---

## 6. Очередь задач БЕЗ ПОВТОРОВ (актуально)

Статусы: ✅ done · 🟡 код есть / device нет · 🔓 открыто · ❌ откат · ➖ N/A

### A. Карта S03 `WhereIsPhoneScreen`

| ID | Задача | Статус | Далее |
|----|--------|--------|-------|
| **MAP-95** | Sheet ~95% как L360 | ✅ **CLIP PASS** · канон §3.1 | не ломать layout |
| **MAP-LOST** | Lost только scroll | ✅ · ⏳ smoke | не sticky |
| **MAP-PIN** | Pin → member | ✅ · ⏳ smoke | |
| **MAP-HAPTIC** | Scroll haptic | ✅ · ⏳ | |

### B. Member S19

| ID | Статус |
|----|--------|
| M19-SCROLL / CROP | ✅ код · ⏳ device |
| M19-TRIP / STAY / UPSELL | 🟡 polish · ⏳ |

### C. Онбординг

| ID | Статус |
|----|--------|
| OB-FILL + OB-PNG 29.10 | ✅ |
| OB-08 CapCut1 | ✅ |
| OB-QA | 🔓 глаза в симе/TF build 19 — **не** править PNG/код без бага |

### D. Закрытие

| ID | Статус |
|----|--------|
| DEV-88 evidence | 🔓 pin/member/lost smoke · FIG-L |
| GIT-19 commit/push | ✅ `e2f01b79` + hotfix `09afdaf7` PlaceAddress · CI Archive |
| **FIG-L** новый файл | ✅ file `b6gFc8GUtWC6ncPgb6X6II` · env ✅ · кадры 🔓 GO батч L34/L15/L25 |

### E. N/A
S39 pet live · S48 flights · S49–50 pets beacon — **не делать**.

---

## 7. FIG-L — что берём из Life360 (весь долг · новый Figma file)

**Статус волны:** 🔓 **ни один FIG-L кадр ещё не нарисован в Figma** (код/SF Symbols уже в iOS).  
**Блокер MAP-95 снят** (CLIP PASS) — можно рисовать L34 под sheet ~95%.  
**Канон берём/не берём:** `FAMILY_SAFETY_KASPERSKY_LIFE360_MASTER_PLAN.md` § Max-UI  
**Промпты AI (полный текст на каждый ID):** `FIGMA_FAMILY_SAFETY_ML_PROMPTS.md` §1 общий + §3 FIG-L01…36  
**Стиль:** Storm glass + gold `#F59E0B` · **не** purple L360 · **не** spy-copy

### 7.0 Handoff другой ML — Figma FIG-L (копировать целиком)

```text
Ты — Figma MCP agent (figma-use skill ОБЯЗАТЕЛЕН перед use_figma).
SSOT очереди: docs/competitors/FAMILY_SAFETY_UNIFIED_ML_PLAN_2026-11-09.md §7 + §7.0
Промпты кадров: docs/competitors/FIGMA_FAMILY_SAFETY_ML_PROMPTS.md
  — §1 общий промпт + §2 токены + §3 один FIG-Lid за раз
Берём/не берём: FAMILY_SAFETY_KASPERSKY_LIFE360_MASTER_PLAN.md § Max-UI
Референс JPG: docs/competitors/screenshots_life360/Lxx.jpg
  (+ _partial_L01_L30.md / _partial_L31_L60.md / _partial_L61_L90.md)
Kaspersky (после FIG-L): screenshots_kaspersky/Sxx.jpg · FIGMA_…_PROMPTS §4 FIG-01…22

ЗАПРЕТ (read-only / не трогать):
- Onboarding Figma file KvkUdyb5Ll31Z9FSzCbpNl · OB_00…08 · APP_AppStoreIcon*
- Companion file vwKcGPUUEZjgayEHNn0BJM (docs/FIGMA_COMPANION.env) — другая волна
- Sticky «Телефон потерян» · purple Life360 brand · spy-copy

СДЕЛАНО В КОДЕ (не перерисовывать как «баг UI»):
- MAP-95-CLIP: sheet full cover≈0.95 strip≈0.05 (WhereIsPhoneScreen S1b VStack)
- Heroes OB PNG 29.10 + Hero_08 CapCut1 в Assets (не FIG-L)
- Build 19 на master

FIG-L file УЖЕ создан (не onboarding / не Companion):
  key = b6gFc8GUtWC6ncPgb6X6II
  env = docs/FIGMA_FAMILY_SAFETY.env
  create_session(fileKey) перед use_figma / get_screenshot.
НЕ писать в KvkUdyb5… или vwKcGPUUEZjgayEHNn0BJM.

Порядок (GO владельца на каждый батч кадров):
1) FIG-L34 + FIG-L15 + FIG-L25  (страница 01_L34_L15_L25_Hub)
2) FIG-L01 + FIG-L03
3) FIG-L02 + FIG-L04 + FIG-L12
4) остальное по §7 таблице
5) Kaspersky FIG-01…22 только если нет reuse

На каждый кадр:
1) Открыть JPG референс из строки FIG-Lid в FIGMA_…_PROMPTS §3
2) Скопировать промпт §3 этого ID (+ общий §1)
3) use_figma → frame 393×852 или component
4) get_screenshot готового слоя — не SOLID-заглушка
5) Короткий отчёт: ID | Figma node | export path | что осталось
Export PNG/PDF — отдельный GO на вставку в xcassets (не смешивать с рисованием).
Сейчас рисуй ТОЛЬКО: <ВСТАВИТЬ FIG-Lid после GO>.
```

**Хватит ли плана другой ML?** Да, если она читает **три файла**: UNIFIED §7/§7.0 (очередь+запреты) · FIGMA_…_PROMPTS (как рисовать) · JPG Lxx (что копировать по композиции).  
**Figma file (2026-11-10):** key `b6gFc8GUtWC6ncPgb6X6II` · env `docs/FIGMA_FAMILY_SAFETY.env` · URL в env.  
Кадры FIG-L* ещё **не нарисованы** — только файл + страницы-батчи + Spec cover. Рисовать L34/L15/L25 — отдельный GO.

### Берём (композиция / смысл)
Карта full-bleed + нижняя дверь · 4 таба в хабе · FAB справа · member sheet · 5 чипов · места Дом/Школа/Работа · тип карты · день/маршрут · тихая зона · шаринг · календарь · SOS hold · empty 3D · soft paywall · роли инвайта · таб Подписка ALADDIN

### Не берём
Purple brand · второй map hub · spy-copy · fake «помощь едет» · multi-circle · Lost Pet live pins · Offers spam

### Список кадров (без повторов) · Figma status = ещё не рисовали

| ID | Простыми словами | Референс JPG | Figma |
|----|------------------|--------------|-------|
| **FIG-L34** | Главный кадр: карта + sheet ~95% + баннер + семья + 5 чипов + секции + 4 таба | L91–97, L42 | 🔓 |
| **FIG-L15** | 4 вкладки снизу | L42 | 🔓 |
| **FIG-L25** | 5 чипов Семья/Питомцы/Вещи/Места/События | L91–97 | 🔓 |
| **FIG-L01** | Пин фото+батарея | L42, L13, L83 | 🔓 |
| **FIG-L03** | FAB stack | L42 | 🔓 |
| **FIG-L02** | Last-seen bubble | L58, L83 | 🔓 |
| **FIG-L04** | Member шапка | L83, L26 | 🔓 |
| **FIG-L12** | Тип карты thumbs | L81, L25 | 🔓 |
| **FIG-L17** | Places chips | L47, L19 | 🔓 |
| **FIG-L08** | Тихая зона круг | L59, L85 | 🔓 |
| **FIG-L09** | Day journal line | L87 | 🔓 |
| **FIG-L13** | Share link card | L86, L28 | 🔓 |
| **FIG-L16** | Календарь месяц | L48–51 | 🔓 |
| **FIG-L18** | Always Allow art | L31, L70 | 🔓 |
| **FIG-L05** | Empty inbox | L23, L76 | 🔓 |
| **FIG-L06** | Full/Limited cards | L79, L21 | 🔓 |
| **FIG-L07** | Name chips + roles | L08, L82 | 🔓 |
| **FIG-L14** | Splash WORDMARK | L78 | 🔓 |
| **FIG-L10** | SOS hold | L36–40 | 🔓 |
| **FIG-L11** | Crash tip icons | L69, L54 | 🔓 |
| **FIG-L19** | Tags/Tile скоро | L45, L64 | 🔓 |
| **FIG-L20** | Roadside скоро | — | 🔓 |
| **FIG-L21** | Pet row скоро | L81 | 🔓 |
| **FIG-L22** | Driving empty | L52, L71 | 🔓 |
| **FIG-L23** | Pin preview | L13 | 🔓 |
| **FIG-L24** | Routes sheet | L61–62 | 🔓 |
| **FIG-L26** | Soft family paywall | L96 | 🔓 |
| **FIG-L27/28** | Pets/Items empty | L92, L94 | 🔓 |
| **FIG-L29** | Pet wizard | L103… | 🔓 |
| **FIG-L30** | Driving weekly | L116 | 🔓 |
| **FIG-L31** | Safety crash+contacts | L117 | 🔓 |
| **FIG-L32** | Places list | Places JPG | 🔓 |
| **FIG-L33** | Create event | create event | 🔓 |
| **FIG-L35** | Role modal | L98–99 | 🔓 |
| **FIG-L36** | Subscription ALADDIN | L118 | 🔓 |

Потом при необходимости: Kaspersky **FIG-01…22** (двери Проверить/Ребёнок) — `FIGMA_…_PROMPTS` §4 · reuse FIG-L где смысл тот же.

**Порядок рисования:** L34+L15+L25 → L01+L03 → L02+L04+L12 → остальное → Kaspersky.  
**Не рисовать в FIG-L:** онбординг «Где семья» / OB_00…08 (CapCut/Assets + onboarding Figma — другая волна).

---

## 8. Порядок работ для следующей ML

### 8.1 Hub Device QA queue (GO владельца 2026-11-10) — **code ✅ · Device QA ⏳**

**CLIP** ✅ PASS (лог Device QA: `path=CLIP` cover=0.95). **P2 VPN/DNS — НЕ делаем** (отдельная сеть/utun4).

| ID | Что | Статус |
|----|-----|--------|
| **HUB-P0.1** | Motion CTA: лог + toast (sim/unavailable / already / Settings) | ✅ code |
| **HUB-P0.2** | Quiet radius: лог `quiet meters=` при слайдере | ✅ code |
| **HUB-P0.3** | Crash Yes: статус local ok / сеть fail (явный UI) | ✅ code |
| **HUB-P0.4** | `queueHubSheet`: лог present vs pending (не misleading) | ✅ code |
| **HUB-P1.6** | Trip detail (скрин 14): reverse geocode → улица→улица, не lat/lon | ✅ code |
| **HUB-P1.7** | Карточки поездок показывают те же улицы (после geocode в ledger) | ✅ code |
| **HUB-P1.5** | Тап аватара/пина → Day Journal (эталон L360 4–13), не только HubMemberCard | ✅ code |
| **HUB-P1.8** | Sticky «шапка-невидимка» в журнале + опц. круг на карте | ✅ code |
| ~~HUB-P2~~ | ~~VPN/DNS -1001/-1003~~ | ❌ **out of scope** |

Скрины: 1→P0.1 · 2→P0.3 · 3 ok · 4–13→P1.5/8 · 5–6→P1.8 · 14→P1.6–7.

```text
1) MAP-95-CLIP ✅ · Hub CLIP primary iOS16+ ✅ — не регрессировать
2) HUB-P0.1…P0.4 + HUB-P1.6/7 ✅ code → Device QA (нужен GO на сборку)
3) HUB-P1.5 Day Journal ✅ code
4) HUB-P1.8 sticky hat + quiet circle ✅ code
5) FIG-L file ✅ · батчи §7 / §12 параллельно по GO
6) DEV-88 · bump только с GO
НЕ: Hub-P2 VPN/DNS
```

---

## 9. Журнал

| Дата | Событие |
|------|---------|
| 2026-11-09 | Baseline sheet записан · S1 · S1b · S2 · sticky lost ОТКАТ |
| 2026-11-09 | OB PNG из сейфа 29.10 · Hero_08 CapCut1 ✅ |
| 2026-11-09 | Владелец: sheet mid после S2 · этот файл = SSOT merge 3 планов |
| 2026-11-10 | DIAG: iOS 15.2 · expansion=1 · UI mid → S2 мёртв |
| 2026-11-10 | S1b-HARD FAIL (sheetH=729 / UI mid · Metal z-order) |
| 2026-11-10 | **MAP-95-CLIP PASS** · full `cover=0.95 strip=0.05 mapStrip=41` · канон §3.1 |
| 2026-11-10 | Hub P0: CLIP primary на **iOS 16+** (`preferLocationSystemSheetS2=false`) · 1A `queueHubSheet` · 3A clear nested on tab · send-fail alert · Device QA pending |
| 2026-11-10 | §8.1 Hub queue: P0 feedback + P1.6/7 улицы на trip detail · **P2 VPN ❌** · P1.5 journal после |
| 2026-11-10 | **GO реализация** · HUB-P0+P1.5/6/7/8 code ✅ · P2 VPN skipped · стоп до `GO на сборку` |
| 2026-11-10 | Build **19** push `e2f01b79` · hotfix PlaceAddress `09afdaf7` |
| 2026-11-10 | FIG-L handoff §7.0 · file `b6gFc8GUtWC6ncPgb6X6II` + `FIGMA_FAMILY_SAFETY.env` · кадры 🔓 |
| 2026-11-10 | Аудит код↔Figma батчи 1–6 · §10 world-class design · §11 icons alive · §12 checklist · Cursor `figl-*` / `ui-lift-*` |
| 2026-11-10 | **GO владельца: старт реализации** · батч1 FIG-L34+L15+L25 (+ alive icons) · §11/§12 в работе |

### 12.0 Статус реализации (живой)

| Батч | Статус |
|------|--------|
| 1 · L34+L15+L25 + ICON-HUB/CHIP | ✅ page `01` · L34=`5:2` L15=`5:63` L25=`5:81` |
| 2 · L01+L03 | ✅ page `02` · L01=`41:4` L03=`41:16` · Cursor browser skip (SSO) · смотреть Figma Desktop |
| 3 · L02+L04+L12 | ✅ page `03` · L02=`59:4` L04=`59:9` L12=`59:20` |
| 4 · L17 L08 L09 L13 L16 L18 | ✅ page `04` · L17=`60:4` L08=`60:18` L09=`60:24` L13=`60:42` L16=`60:54` L18=`60:96` |
| 5 · L05 L06 L07 L14 L35 L36 | ✅ page `04` Batch5_Board · L05=`61:4` L06=`61:10` L07=`61:30` L14=`61:46` L35=`61:52` L36=`61:62` |
| 6 · L10–L33 safety/soon/pets | ✅ page `04` Batch6_Board=`62:2` · L10=`62:4` … L33=`62:123` |
| ICON app-wide (без VPN) ✅ · Kaspersky gaps ✅ · export | 🔓 export — отдельный GO |

### 11.5 Alive icons — где делаем

**Да, здесь в том же Figma-файле** `b6gFc8GUtWC6ncPgb6X6II` (новая страница или board на `04`/`05`), не в Onboarding/Companion.  
Потом export→Assets — отдельный GO. Вставка в Swift — отдельный GO.

Состав **только:**
1. ICON-DOORS-3 (Проверить · Ребёнок · Где семья)  
2. ICON-ANTIFAKE / ICON-PARENTAL / ICON-FAMILY / ICON-TARIFF / ICON-EMPTY  
3. **Не:** VPN, tunnel, «включить VPN»

### 11.6 Kaspersky — что именно делаем («только дыры»)

Не рисуем все FIG-01…22 слепо. Сначала reuse из FIG-L:

| Kaspersky ID | Действие |
|--------------|----------|
| FIG-09 pin | **reuse L01** — не рисовать |
| FIG-11 Always Allow | **reuse L18** |
| FIG-18 Crash/SOS | **reuse L10/L11** |
| FIG-19 Tile | **reuse L19** |
| FIG-20 Evac | **reuse L20** |
| FIG-10 places markers | **reuse L17/L32** по смыслу |

**Рисуем только дыры (дверь «Проверить» / «Ребёнок»):**
- FIG-01 hero спокойный звонок  
- FIG-02 Call Directory 5 steps  
- FIG-03 Shield ON status  
- FIG-04 empty lists  
- FIG-05 child overview empty  
- FIG-06 avatar grid add child  
- FIG-13 content categories dots  
- FIG-14 Анти-Баннер story  
- FIG-15 Дом/сеть empty  
- FIG-16 Safe QR  
- FIG-17 VK empty (нейтрально)  
- FIG-07/08 invite QR — только если L07/L35 недостаточно  

Страница Figma: `05_Kaspersky_later` · после GO на Kaspersky.

### B. Figma — батч1 (обновление чеклиста)
- [x] GO → L34 + L15 + L25 стартовали  
- [x] Frames созданы на `01_L34_L15_L25_Hub`  
- [x] get_screenshot L34/L15/L25 (не solid)  
- [ ] Owner visual Approve батч1  
- [ ] GO батч2 L01+L03

---

## 10. Аудит код ↔ Figma (не потерять) · world-class lift

**Правило:** код = мозг/честность/MAP-95. Figma = лицо топ-уровня. Export→Assets = отдельный GO. Карту polyline/bubble/geofence-circle = отдельный GO кода после art.

### 10.1 Вердикт по FIG-L (кратко)

| ID | Код сейчас | После Figma | После wire (GO) |
|----|------------|-------------|-----------------|
| L34 hub full | CLIP ✅ · текст/SF | **Лучше** эталон | — layout не трогать |
| L15 4-tab | есть gold/SF | **Лучше** icons | заменить SF |
| L25 5 chips | Capsule+SF · interim PNG не в UI | **Лучше** | wire PNG/PDF |
| L01 pin+battery | круг фото/буква · **нет** battery badge · interim PNG не wired | **Лучше** | wire pin |
| L03 FAB | 1 PNG + 3 SF | **Лучше** единый set | wire all FAB |
| L02 last-seen bubble | текст в member · **нет** над пином | art | **GO код** bubble |
| L04 member hero | scroll header есть | **Лучше** | polish |
| L12 map thumbs | list sheet | **Лучше** 3×96 | replace list UI |
| L17 places chips | text capsules | **Лучше** | swap icons |
| L08 quiet circle | slider+badge · **нет** circle overlay | art | **GO код** overlay |
| L09 day journal | list+scrub · **нет** polyline | art | **GO код** line optional |
| L13 share card | shareCard есть | **Лучше** | polish |
| L16 calendar | empty+add есть | **Лучше** month art | polish |
| L18 Always Allow | text sheet | **Лучше** calm art | insert hero |
| L05 empty inbox | слабо | **Дорисовать** | wire |
| L06 Full/Limited | SimpleHome mode | **Лучше** 2 cards | polish Home |
| L07 name/role chips | invite roles | **Лучше** density | polish |
| L14 splash | brand/OB | FIG-L splash | optional launch |
| L35 role modal | InviteRoleSheet | **Лучше** | polish |
| L36 subscription tab | thin → Tariffs | **Лучше** cards | keep navigate Tariffs |
| L10 SOS hold | hold 3s bar 56pt | **Лучше** big circle | keep hold logic |
| L11 crash tips | text+toggle | **Лучше** icon row | insert |
| L19–21 soon | text soon | **Лучше** 3D empty | wire |
| L22 driving empty | DrivingReportsModal | **Лучше** teaser | polish |
| L23 pin preview | S/M/L letter | **Лучше** | polish |
| L24 routes | RoutesSheet | **Лучше** | polish |
| L26 soft paywall | softPaywallSheet | **Лучше** timeline | polish |
| L27/28 pets/items empty | soonSectionCard | **Лучше** clay | wire |
| L29 pet wizard | FamilyPetWizardSheet | **Лучше** steps | polish |
| L30 driving weekly | weekly strip | **Лучше** | polish |
| L31 safety tab | crash+contacts+SOS | **Лучше** 2 cards | polish |
| L32 places list | manage places | **Лучше** | polish |
| L33 create event | calendar add | **Лучше** form | polish |
| Kaspersky 01–22 | двери Проверить/Ребёнок | только gaps · reuse FIG-L | после FIG-L |

### 10.2 Size-spec батч 1 (канон)

Phone **393×852** · mapStrip **43** · sheet **745** · tab **64** · radius sheet **20** · H-pad **16** · chips **56×56** gap **10** · FAB/pin later **48** / **52–56**.  
Детали: AgentStore `FIG_L_BATCH1_SIZE_SPEC.md`.

### 10.3 Отдельные GO кода (после art — не смешивать с рисованием)

| GO id | Что |
|-------|-----|
| WIRE-L02 | bubble last-seen над map pin |
| WIRE-L08 | quiet-zone circle overlay на MKMap |
| WIRE-L09 | optional day polyline (если продукт GO) |
| WIRE-L01/L03/L25 | заменить SF/interim на final assets |
| WIRE-L12 | map type 3 thumbs вместо list-only |
| WIRE-L10 | SOS visual circle · hold logic сохранить |

---

## 11. World-class design — что ещё добавить (иконки «живые»)

### 11.1 Система иконок ALADDIN Alive (NEW · обязательно в FIG-L + app-wide)

Цель: иконки **яркие, объёмные, «живые»** (мягкий 3D/clay или glass+gold glow), не плоский серый SF Symbol.

| Набор | Куда | Стиль |
|-------|------|-------|
| **ICON-HUB-4** | L15 tabs | Location / Car / Shield / Crown — gold selected, soft depth |
| **ICON-CHIP-5** | L25 | People / Paw / Key / Home / Calendar — selected filled |
| **ICON-FAB-4** | L03 | Layers / Locate / Routes / Invisible |
| **ICON-DOORS-3** | SimpleHome 3 двери | Проверить / Ребёнок / Где семья — large living icons |
| **ICON-HOME-ROW** | SimpleHome secondary rows | Family / Access Full-Limited |
| **ICON-ANTIFAKE** | дверь Проверить | Call / Link / QR / Banner / Shield ON |
| **ICON-PARENTAL** | дверь Ребёнок | Limits / Content / Rewards / Screen Time |
| **ICON-FAMILY** | FamilyScreen cards | Members / Chat / Groups / Invite |
| **ICON-TARIFF** | Tariffs + L36 | Free / Family / Trial timeline |
| **ICON-COMPANION** | Companion hub | 3 heroes already Rive — не дублировать FIG-L; только chrome icons |
| **ICON-EMPTY** | all empty states | mailbox / pets / items / tile / evac — clay ALADDIN |

**⛔ НЕТ VPN в мобильном ALADDIN.** Не рисовать ICON-VPN / «VPN-дверь» / connect-tunnel art.  
Network Protection в коде (если встречается) ≠ продукт VPN для пользователя — **не включать в FIG-L alive icons.**

**Запрет иконок:** Life360 purple · Kaspersky green lockup · spy eye art · emoji как единственный icon · **VPN branding**.

**Export:** PDF/SVG предпочтительно + PNG @2x/@3x · имена `ICON_*` / `FIG_L*`.

### 11.2 Рекомендации по ключевым экранам приложения

| Экран | Сейчас | Рекомендация топ-уровня |
|-------|--------|-------------------------|
| **SimpleHome** (3 двери) | SF + storm cards | Living door icons · stronger hierarchy · Full/Limited как L06 cards · micro-motion press |
| **WhereIsPhone hub** | CLIP ✅ · SF chips/FAB | FIG-L34/15/25/01/03 first · alive icons · invite banner art |
| **Member sheet** | functional scroll | L04 hero · battery · clearer section cards |
| **Driving tab** | DrivingReportsModal | L22/L30 art · empty state premium |
| **Safety tab** | text dense | L31 2 cards · L10 circle SOS · L11 tip row · L19/20 soon art |
| **Subscription tab** | thin CTA | L36 plan cards · keep Tariffs destination |
| **Antifake / Проверить** | mixed | Kaspersky FIG only gaps · alive status shield |
| **Parental / Ребёнок** | mixed | calm icons · no spy · clear cards |
| **FamilyScreen** | many SF | ICON-FAMILY · invite L07 · empty states |
| **Tariffs** | text/cards | align with L36 · gold CTA · trust copy |
| **Network Protection** (если экран) | не путать с VPN | **не** в FIG-L alive-icons · только явный GO |
| **Profile / Settings** | dense | section icons consistent · less gray |
| **Notifications** | list | unread gold dot · empty alive |
| **Family Chat** | ok | avatar rings gold · send FAB glass |
| **Companion** | Rive heroes | **не** в FIG-L file · chrome only |
| **Onboarding OB_*** | CapCut/heroes ✅ | **не** трогать в FIG-L волне |
| **Referral** | promo | brand illustration optional later |
| **Devices** | list | device glyphs alive |
| **Analytics** | charts | keep data honest · soften chrome |

### 11.3 Карточки — единый visual language

Каждая product-card:
1. Frost glass / storm fill  
2. Stroke gold ~35–40%  
3. Radius 16–20  
4. Leading **alive icon** 28–32 (не tiny SF)  
5. Title serif/bold + sub 70% white  
6. CTA gold или quiet text  
7. Empty = illustration + one CTA (не стена текста)

### 11.4 Motion (после visuals · отдельный GO)

- Chip select spring  
- FAB press scale 0.96  
- Sheet grabber  
- SOS hold ring progress (уже hold — улучшить visual)  
Не анимировать карту Metal тяжёлым blur.

---

## 12. Чеклист владельца / агента (не забыть)

### A. Уже ✅
- [x] MAP-95 CLIP  
- [x] Baseline S1 md  
- [x] Heroes OB + CapCut1  
- [x] Build 19 + PlaceAddress  
- [x] FIG-L file + pages + env  
- [x] Аудит код↔Figma §10  
- [x] Size-spec batch1  

### B. Figma (каждый батч = GO)
- [ ] GO → L34 + L15 + L25 (+ alive icons в них)  
- [ ] GO → L01 + L03  
- [ ] GO → L02 + L04 + L12  
- [ ] GO → L17 L08 L09 L13 L16 L18  
- [ ] GO → L05 L06 L07 L14 L35 L36  
- [ ] GO → L10–L33 soon/safety pack  
- [x] ICON-DOORS-3 + ICON-HOME + ICON-FAMILY + ICON-ANTIFAKE + ICON-PARENTAL + ICON-TARIFF + ICON-EMPTY · **без VPN** · page `06_Alive_Icons` board `64:222` · 27 components · 2026-11-10  
- [x] Kaspersky gaps only · page `05` Board1 `67:171` + Board2 `68:130` · masters 393×852 · FIG-01…08 + 13…17 + REUSE legend · 2026-11-10  
- [ ] get_screenshot каждый кадр · не SOLID  

### C. Wire / iOS (отдельные GO)
- [ ] Export → xcassets  
- [ ] WIRE L01/L03/L25/L15 icons  
- [ ] WIRE-L02 bubble · WIRE-L08 circle · WIRE-L12 thumbs · WIRE-L10 SOS visual  
- [ ] SimpleHome doors icons  
- [ ] Empty states swap  
- [ ] DEV-88 smoke · OB-QA глаза  
- [ ] Bump 20 только GO  

### D. Не делать
- [ ] Ломать CLIP ratios  
- [ ] Sticky lost  
- [ ] Purple L360 / spy  
- [ ] Трогать OB_* / Companion Figma  
- [ ] Mock family/map  
- [ ] «Figma 100%» после interim PNG  

---

**Конец SSOT.** Sheet → §2–3. Figma FIG-L → §7 + §7.0 + §10–12. Icons alive → §11. Промпты кадров → `FIGMA_FAMILY_SAFETY_ML_PROMPTS.md`. Не плодить третий plan.
