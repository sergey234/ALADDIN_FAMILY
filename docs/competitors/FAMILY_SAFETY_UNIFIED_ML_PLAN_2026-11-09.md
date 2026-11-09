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
Онбординг Hero_08 CapCut1 ✅ — не переделывать без GO.
FIG-L = НОВЫЙ Figma file, не OB_*. Список §7.
Сборка / commit / push / FIG create — только после явного GO владельца.
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
**Runtime канона:** iOS **15.2** (deploy target) → путь **S1b CLIP** (не S2 modal).  
**S2** (`presentationDetents`) остаётся только для iOS 16+; на 15.x **не** primary.

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
| Peek / half height | `peekH = usable * 0.22` · `halfH = usable * 0.48` · `usable = mapHeight − tab` |
| Lerp | `expansion ≤ 0.42`: peek→half; else half→full |
| Чип | любой чип → `expandLocationSheetToFull()` → на iOS 15 `sheetExpansion = 1.0` |
| Lost CTA | только карточка в scroll (P0-6); **sticky запрещён** без нового GO |
| FAB | hide / weak hit при `expansion > 0.55` |
| DIAG лог | `WHERE_PHONE sheet S1b height` · поля `sheetH` `geoH` `mapStrip` `cover` `strip` |

**Почему заработало (корень):**  
MKMapView (Metal) рисовался **поверх** SwiftUI `.overlay` sheet → в логе `sheetH=729`, на экране mid.  
CLIP отдаёт карте только `mapStripH` в **layout** + `.clipped()` → Metal не занимает зону sheet.

**Evidence PASS (владелец, Console 2026-11-10 ~00:33):**

| Состояние | Лог |
|-----------|-----|
| appear peek | `sheetH=207 geoH=835 mapStrip=563 expansion=0.08 cover=0.33 strip=0.67` |
| half snap | `sheetH=370 mapStrip=400 expansion=0.42 cover=0.52 strip=0.48` |
| **full snap** | `sheetH=729 mapStrip=41 expansion=1.00 fullTarget=729 cover=0.95 strip=0.05 tab=64` |

GATES: `cover ≥ 0.90` · `strip ≤ 0.08` на full — **PASS**. Владелец: «Сейчас все работает корректно».

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
| OB-QA | ⏳ глазами после сборки |

### D. Закрытие

| ID | Статус |
|----|--------|
| DEV-88 evidence | 🔓 MAP-95 ✅ · дальше pin/member/lost + FIG-L |
| GIT-19 commit/push | 🔓 GO |
| **FIG-L** новый файл | 🔓 после стабильного sheet UX (§7) |

### E. N/A
S39 pet live · S48 flights · S49–50 pets beacon — **не делать**.

---

## 7. FIG-L — что берём из Life360 (весь долг · новый Figma file)

**Канон берём/не берём:** `FAMILY_SAFETY_KASPERSKY_LIFE360_MASTER_PLAN.md` § Max-UI  
**Промпты AI:** `FIGMA_FAMILY_SAFETY_ML_PROMPTS.md`  
**Стиль:** Storm glass + gold `#F59E0B` · **не** purple L360 · **не** spy-copy

### Берём (композиция / смысл)
Карта full-bleed + нижняя дверь · 4 таба в хабе · FAB справа · member sheet · 5 чипов · места Дом/Школа/Работа · тип карты · день/маршрут · тихая зона · шаринг · календарь · SOS hold · empty 3D · soft paywall · роли инвайта · таб Подписка ALADDIN

### Не берём
Purple brand · второй map hub · spy-copy · fake «помощь едет» · multi-circle · Lost Pet live pins · Offers spam

### Список кадров (без повторов)

| ID | Простыми словами | Референс |
|----|------------------|----------|
| **FIG-L34** | Главный кадр: карта + sheet ~95% + баннер + семья + 5 чипов + секции + 4 таба | L91–97, L42 |
| **FIG-L15** | 4 вкладки снизу | L42 |
| **FIG-L25** | 5 чипов Семья/Питомцы/Вещи/Места/События | L91–97 |
| **FIG-L01** | Пин фото+батарея | L42, L13, L83 |
| **FIG-L03** | FAB stack | L42 |
| **FIG-L02** | Last-seen bubble | L58, L83 |
| **FIG-L04** | Member шапка | L83, L26 |
| **FIG-L12** | Тип карты thumbs | L81, L25 |
| **FIG-L17** | Places chips | L47, L19 |
| **FIG-L08** | Тихая зона круг | L59, L85 |
| **FIG-L09** | Day journal line | L87 |
| **FIG-L13** | Share link card | L86, L28 |
| **FIG-L16** | Календарь месяц | L48–51 |
| **FIG-L18** | Always Allow art | L31, L70 |
| **FIG-L05** | Empty inbox | L23, L76 |
| **FIG-L06** | Full/Limited cards | L79, L21 |
| **FIG-L07** | Name chips + roles | L08, L82 |
| **FIG-L14** | Splash WORDMARK | L78 |
| **FIG-L10** | SOS hold | L36–40 |
| **FIG-L11** | Crash tip icons | L69, L54 |
| **FIG-L19** | Tags/Tile скоро | L45, L64 |
| **FIG-L20** | Roadside скоро | — |
| **FIG-L21** | Pet row скоро | L81 |
| **FIG-L22** | Driving empty | L52, L71 |
| **FIG-L23** | Pin preview | L13 |
| **FIG-L24** | Routes sheet | L61–62 |
| **FIG-L26** | Soft family paywall | L96 |
| **FIG-L27/28** | Pets/Items empty | L92, L94 |
| **FIG-L29** | Pet wizard | L103… |
| **FIG-L30** | Driving weekly | L116 |
| **FIG-L31** | Safety crash+contacts | L117 |
| **FIG-L32** | Places list | Places JPG |
| **FIG-L33** | Create event | create event |
| **FIG-L35** | Role modal | L98–99 |
| **FIG-L36** | Subscription ALADDIN | L118 |

Потом при необходимости: Kaspersky **FIG-01…22** (двери Проверить/Ребёнок) — reuse FIG-L где смысл тот же.

**Порядок рисования:** L34+L15+L25 → L01+L03 → L02+L04+L12 → остальное → Kaspersky.  
**Не рисовать в FIG-L:** онбординг «Где семья» / OB_00…08 (это CapCut/Assets, не FIG-L34).

---

## 8. Порядок работ для следующей ML

```text
1) MAP-95-CLIP ✅ PASS — канон §3.1 · не регрессировать
2) Device smoke остальное: pin→member · Events→lost CTA
3) OB-QA глазами (уже ассеты ✅) — не чинить без бага
4) GO FIG-L → create file → L34/L15/L25 first
5) DEV-88 · GO commit (без telegram_stars_shop_bot) · GO push
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

---

**Конец SSOT.** Вопросы по sheet — только §2–3. По Figma — только §7. Не плодить третий «sheet plan».
