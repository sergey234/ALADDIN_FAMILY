# План: вход SimpleHome + иконки + карта + единорог

**Дата:** 2026-11-11  
**Статус:** план (код — только после GO по фазам)  
**Порядок:** P0 → P1 → иконки **по одному слоту** (не mass) · 3 варианта Settings  
**Доказательство логов:** симулятор `ALADDIN[56253]` · 17:54

---

## 0A. Аудит 3 вариантов (2026-11-11 18:20) — факты

### Что есть в Assets (канон 1x=32 · 2x=64 · 3x=96)

| Набор | Count | Статус |
|-------|-------|--------|
| `*_Glyph` (Золото) | **12/12** A01–A12 | ✅ wire |
| `*_Black` (Значки) | **12/12** | ✅ wire |
| `*_Blue` | 12 в Assets | ⛔ **не используем** (канон владельца 2026-11-11) |
| Классика | emoji/SF | ✅ без PNG |

**P0 ✅ 2026-11-11:** SimpleHome всем · `HOME_ENTRY` лог · parent после онбординга · quiet-zone gold · chips SF · Glyph без Blue.

### Wire сейчас (AliveGlyph ↔ слот)

| ID | Слот | Классика | Золото | Значки | Wire size |
|----|------|----------|--------|--------|-----------|
| A01 | Main profile + tab Профиль | 👤 | Glyph ✅ | Black ✅ | **28** |
| A02 | tab Уведомления | 🔔 | ✅ | ✅ | **28** |
| A03 | tab Устройства | 📱 | ✅ | ✅ | **28** |
| A04 | tile Защита | 🛡️ | ✅ | ✅ | **40** |
| A05 | tile Тарифы | 💎 | ✅ | ✅ | **40** |
| A06 | Premium crown | SF | ✅ Where hub 22 + pane 28 | same | P2 |
| A07 | SimpleHome дверь Проверить | SF | ✅ | ✅ | 36/32 |
| A08 | дверь Ребёнок | SF | ✅ | ✅ | 36/32 |
| A09 | дверь Где семья | SF | ✅ | ✅ | 36/32 |
| A10 | Where chip **Семья** | SF | Blue disc* | Black* | **28** |
| A11 | Where FAB Locate | SF | Blue disc ✅ | Black ✅ | **34** |
| A12 | tab Kids | ✨ | ✅ | ✅ | **28** |

\*План владельца: chips Where в режиме **Золото** оставить **Классику** (не Blue disc) — правка поведения P0.4, не новый art.

### Нет ассета / нет wire (очередь по слотам, не mass)

| ID | Слот | Сейчас | Нужно |
|----|------|--------|-------|
| U01 | tab **Игра** единорог | 🦄 emoji | crop → Glyph+Black (+optional Blue) · wire 28 |
| M02 | tile 60+ | 🧓 | ✅ art Glyph+Black + wire 40 |
| M03 | tile Аналитика | 📊 | ✅ art Glyph+Black + wire 40 |
| M04 | tile Настройки | ⚙️ | ✅ art Glyph+Black + wire 40 |
| M05 | tile Удобный режим | 🏠 | ✅ art Glyph+Black + wire 32 |
| M01 | AI Друзья (строка Удобный) | SF | ✅ Glyph+Black + wire 28 |
| A06 | Premium | asset ✅ | ✅ Where + Tariffs cards |
| chips Pets/Things/Places/Events | SF | оставить Классику (так решили) |
| D02/D03 Меню / Полная версия | SF | ✅ Glyph+Black + wire |
| T01–T04 Free/Personal/Family/Trial | emoji | ✅ Glyph+Black + wire карточек |
| quiet-zone map | purple | P0 gold (цвет, не icon) |

**Вывод:** для согласованного **G1 якоря A01–A12** три варианта **полные по файлам**; UI chrome **12/12** (A06 ✅ P2 Where) + chip strip частично. Main tiles / tariffs — **отдельные волны art→export→wire по одному**.

---

## 0. Вердикт по логам (почему Main)

```
RESET_ONBOARDING env=1 → hasCompletedOnboarding=false → онбординг OK
…
✅ Онбординг завершён, вход = 01_MainScreen
🧭 Navigation: Обучение → <-- Root (Главная)
…
позже вручную: Главная → Удобный режим
«Назад» / Root из Удобного → снова Главная (корень = Main)
```

`navigateToHomeEntry` вернул **`.main`**, не `.simpleHome`.

`PayPainsUIFlags.shouldOpenSimpleHomeAtLaunch` = false, когда:

1. `current_user_role` ∈ {child, teenager, teen, elderly, senior}, **или**
2. `aladdin.payPains.newUIEnabled` = false.

В этой сессии JWT/семья **не** сброшены (`MEM_0FE236A1`, `FAM_*`, parental `childId=MEM_0FE236A1`) — роль в UD почти наверняка **child** (или blocked).  
`markPrimaryUserRoleParentIfUnset()` **не** перезаписывает непустую роль → SimpleHome заблокирован.

---

## 1. Канон входа (решение владельца 2026-11-11)

| Правило | Было | Станет |
|---------|------|--------|
| После онбординга | SimpleHome только parent/adult | **Всегда SimpleHome** (все роли) |
| Main (сетка) | Иногда корень | Только по явному действию пользователя («Полная версия» / Меню) |
| «Назад» из SimpleHome | иногда Root→Main | Root = **SimpleHome** (homeEntry) |

### P0-A · код входа

1. `PayPainsUIFlags.shouldOpenSimpleHomeAtLaunch` — **убрать blocklist ролей** для cold-start / post-onboarding (или invert: SimpleHome всегда при `newUIEnabled`).  
2. После онбординга: `current_user_role = parent` если пользователь завершил **родительский** онбординг (не «if empty»). Child-онбординг/детский shell — отдельный путь, не путать.  
3. Лог обязателен:  
   `🏠 HOME_ENTRY screen=… role=… newUI=… reason=onboarding.finish`  
4. `navigateToHomeEntry` / `goToRoot` / empty-stack fallback — уже на `homeEntryScreen()`; проверить что SimpleHome **не** зовёт `navigateToRoot(.main)` как «домой» (строки ~865/939/1098 в `SimpleHomeScreen` — только явная «Полная версия»).  
5. Smoke: RESET_ONBOARDING → finish → **первый** экран = SimpleHome · в Console есть `HOME_ENTRY … simpleHome`.

---

## 2. Превью иконок — 3 варианта для пользователя

Оставить Settings picker. Имена:

| raw (storage) | UI RU | UI EN (позже) | Поведение |
|---------------|-------|---------------|-----------|
| `legacy` | **Классика** | Classic | emoji / SF (как сейчас) |
| `aliveBlue` | **Золото** | Gold | Glyph-first: tab/tile/door **без** disc; chip/FAB — см. §2.1 |
| `aliveBlack` | **Значки** | Badges | полный black-disc A/B (все wired G1) |

«Старые» → **Классика** (не звучит как брак).

### §2.1 Исключения Where (как нравится владельцу)

| Слот | Классика | Золото | Значки |
|------|----------|--------|--------|
| Chip strip Семья·Питомцы·Вещи·Места·События | SF + золотая капсула ✅ | **оставить Классику** (не blue disc) | опционально позже / не форсить Blue |
| FAB Locate | SF | Blue disc OK **или** Glyph | Black disc |
| Quiet-zone на карте | — | **gold/storm**, не purple | same |
| Map pin (буква) | storm+gold ✅ | не менять | не менять |

---

## 3. Матрица размеров (перепроверка 2026-11-11)

Канон export imageset: **1x=32 · 2x=64 · 3x=96** (квадрат).  
Wire frame pt ниже.

### 3.1 G1 якоря A01–A12 (уже assets Blue/Black/Glyph)

| ID | Слот | Классика | Золото (Glyph) pt | Значки (disc) pt | Asset |
|----|------|----------|-------------------|------------------|-------|
| A01 | Main profile circle | emoji | **28** | 28 in disc | `…_Profile_{Glyph\|Black\|Blue}` |
| A01 | Main tab Профиль | emoji | **28** | 28 | same |
| A02 | tab Уведомления | emoji | **28** | 28 | Notif |
| A03 | tab Устройства | emoji | **28** | 28 | Devices |
| A04 | tile Защита | emoji | **40** | 40 | Protect |
| A05 | tile Тарифы | emoji | **40** | 40 | Tariff |
| A06 | Premium / Where crown | SF | **28** pane / **22** hub tab | same | ✅ P2 wire Where |
| A07 | SimpleHome дверь Проверить | SF | **32–36** | 36 | Check |
| A08 | дверь Ребёнок | SF | **32–36** | 36 | Child |
| A09 | дверь Где семья | SF | **32–36** | 36 | Where |
| A10 | Where chip Семья | SF **классика** | **не wire Blue** | optional later | ChipFamily |
| A11 | Where FAB | SF | 24 in **48** FAB | Black/Blue disc | FabLocate |
| A12 | tab Kids | emoji | **28** | 28 | Kids |

### 3.2 Очередь P-MAIN / P-DOORS / P-TARIFF (ещё нет G1)

| ID | Слот | UI pt | Статус |
|----|------|-------|--------|
| M01 | Удобный AI Друзья | 28 | ✅ art+wire (плитки Main нет) |
| M02 | Main 60+ | 40 | ✅ P2 art+wire |
| M03 | Main Аналитика | 40 | ✅ P2 art+wire |
| M04 | Main Настройки | 40 | ✅ P2 art+wire |
| M05 | Main Удобный режим | 32 | ✅ P2 art+wire |
| M06 / U01 | tab **Игра** единорог | **28** tab | ✅ P1 Glyph+Black · Классика 🦄 |
| T01–T04 | Tariffs Free/Personal/Family/Trial | 32 | ✅ Glyph+Black + wire |
| D02/D03 | Удобный Меню / Полная | 28 | ✅ Glyph+Black + wire |
| FIG-L | L15 tabs 22 · FAB locate 34/48 · L01 pin / L25 chips | §2.1+§3.3 | ✅ tabs+FAB · pin/chips **не трогаем** (канон) |

### 3.3 Where / карта (не G1 chrome)

| Элемент | Size | Цвет / стиль |
|---------|------|--------------|
| Chip strip | capsule + SF ~16 | золото selected · **без** purple/blue disc |
| FAB | 48 | disc только в Значки/Золото-FAB |
| Avatar pin | 36–52 | storm fill + gold stroke (уже) |
| Quiet-zone circle | meters from store | **P0:** fill/stroke **gold** `#F59E0B` @0.18/0.85 · убрать Life360 purple `rgb(0.45,0.28,0.85)` |

---

## 4. Фазы работ (порядок)

### P0 — вход + карта (без сборки агентом)

| # | Задача | Файлы |
|---|--------|-------|
| P0.1 | SimpleHome **всегда** post-onboarding / cold-start (все роли) + лог HOME_ENTRY | `PayPainsUIFlags.swift`, `OnboardingScreen`, `NavigationManager` |
| P0.2 | Не затирать детский shell отдельно — явное ТЗ: взрослый онбординг → parent; детский вход — отдельный флаг | онбординг + role |
| P0.3 | Quiet-zone purple → gold/storm | `FamilySafetyRemainderHub.swift` |
| P0.4 | Chip strip: не подменять AliveGlyph Blue на «Семья» в режиме Золото | `WhereIsPhoneScreen` + `AliveIconStyle` |

### P1 — Settings имена + единорог + wire polish

| # | Задача |
|---|--------|
| P1.1 | Titles: Классика / Золото / Значки + подпись Settings |
| P1.2 | Tab «Игра»: PNG/glyph единорога (crop из `Resources/Companion/unicorn_master.png`) · frame 28 · **не** emoji 🦄 |
| P1.3 | DEBUG default = **Золото** или оставить Значки только для A/B по выбору владельца |
| P1.4 | Verify sizes A01–A12 vs §3.1 |

### P2 — полный охват иконок

| # | Задача |
|---|--------|
| P2.1 | Figma+export M01–M06 (Main remaining tiles + unicorn) |
| P2.2 | Wire Main tiles AI/Analytics/Settings/60+/Удобный |
| P2.3 | Tariffs T* + Premium A06 везде |
| P2.4 | FIG-L L01/L15/L25 final assets (отдельный export GO) |

### P3 — QA (владелец собирает)

- RESET_ONBOARDING → finish → **SimpleHome** first  
- Settings: 3 стиля на Main tabs/tiles + doors  
- Where: chips классика · карта без purple · FAB  
- Tab Игра: новый единорог  

### P4 — Motion + живой пин ✅ GO 2026-11-11

**Не трогаем:** QR · маршруты · чипы Классика · логику SOS (hold 3с → семья) · quiet-zone meters.

| # | Статус | Решение |
|---|--------|---------|
| **P4.1 Пин больше** | ✅ | L **48 → 56** · cap view 64 |
| **P4.2 Пин «дышит»** | ✅ | scale **1.0↔1.08** · цикл **1.8 с** · Reduce Motion off |
| **P4.3 FAB tap** | ✅ | spring **все 4** FAB · `MapFabPressStyle` |
| **P4.4 SOS кольцо** | ✅ | круг Ø132 + trim-кольцо · полоска убрана · hold 3с тот же |
| P4.5 / **P5 Стекло** | ✅ | `aladdinProductCard`: **Классика = solid** · **Золото/Значки = stormGlass** · Main/Удобный/Семья/Тарифы · карту FAB/пин не трогали |

### P6 — Wave B большие картинки Life360 (следующая фаза)

**SSOT:** [`PLAN_LIFE360_HERO_ART_WAVE_2026-11-11.md`](./PLAN_LIFE360_HERO_ART_WAVE_2026-11-11.md)  
Рефы: `docs/competitors/screenshots_life360_hero_wave_2026-11-11/L360_H01…H28`  
Старт: фраза **`GO Wave B …`** (см. self-prompt в том файле §6).

---

## 5. Не делать без GO

- `xcodebuild` / Simulator (агент)  
- bump build  
- commit bot / secrets  
- трогать OB_* / Companion Figma files  

---

## 6. Rollback

- Вход: вернуть role blocklist + `simpleHomePreferred`  
- Иконки: Settings → **Классика** · tag `pre-alive-icons-2026-11-11`  
- Карта: git revert quiet-zone colors  

---

## 7. GO чеклист владельца

Отметь фразой, что делать сейчас:

- [ ] **GO P0** — вход SimpleHome всем + quiet-zone gold + chip классика  
- [ ] **GO P1** — имена Классика/Золото/Значки + единорог tab  
- [ ] **GO P2** — art/export остальных Main tiles  
- [ ] **GO на сборку** — после P0/P1  

**Рекомендация меха:** сначала **GO P0**, потом P1, сборка тобой.
