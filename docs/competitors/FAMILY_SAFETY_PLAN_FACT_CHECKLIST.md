# Family Safety — plan / факт (чек-лист)

**Master:** `FAMILY_SAFETY_KASPERSKY_LIFE360_MASTER_PLAN.md` v1.4 · §17  
**Цель владельца (lock):** **100% Kaspersky A + Life360 B/C кроме Figma**; **P4 out** (live Pet GPS / roadside dispatch / multi-circle).  
**§17 hub 1–6+7a** = только первая фаза, **не** весь план.  
**Правило:** отмечать **Факт** только после кода + короткого verify (не «на словах»).  
**Сборка:** после кода 100% (кроме Figma) · владелец: сборка → правки → commit+push.

Легенда: `[ ]` нет · `[~]` в работе · `[x]` done · `[-]` ждёт GO · `[D]` долг (обязателен later)

---

## Замок продукта (не снимать)

| # | Критерий | План | Факт |
|---|----------|------|------|
| P1 | Один Map hub = `WhereIsPhone` («Где семья») | [x] | [x] |
| P2 | 4 таба **внутри** хаба (не root app TabBar) | [x] | [x] |
| P3 | 5 chips + scroll-spy на Местоположении | [x] | [x] |
| P4 | Storm mesh + gold `#F59E0B` · не purple Life360 | [x] | [x] hub chrome |
| P5 | No mock / no fake pins / no «помощь едет» | [x] | [x] |
| P6 | Calendar D = месяц + EventKit · честный local copy | [x] | [x] |
| P7 | Вождение → `DrivingReportsModal` (не вечный empty) | [x] | [x] |
| P8 | Soft Family paywall после N дней (`01e`) | [x] | [x] |
| P9 | UI только `localized()` · RU+EN | [x] | [x] |
| P10 | P4 live Pet / dispatch — **не сейчас** | [x] | [x] |

---

## §17 цепочка 1→8

| Шаг | Задача | План | Факт | Evidence / verify |
|-----|--------|------|------|-------------------|
| **1** | `L-P3-01` 4-tab + X → Удобный | [x] | [x] | HubTab + hubTabBar · X→`isPresented=false` |
| **2** | `L-P3-01d` 5 chips + scroll-spy · Pet/Items soon | [x] | [x] | sticky chips · PreferenceKey spy · soon sheets |
| **3** | Driving→modal · Sub thin→Tariffs · Safety | [x] | [x] | DrivingReportsModal · `.tariffs` · CrashSettings |
| **4** | Member · map type · Places · Always Allow | [x] | [x] | FAB · map type · Always Allow · member sheet |
| **5** | Calendar D · soft paywall `01e` | [x] | [x] | DatePicker · local store · EventKit · N=3 |
| **6** | journal/quiet/share · SOS chrome · Pet `01i` later | [x] | [x] | trail · member quiet/share · SOS chrome |
| **7a** | **B interim:** PNG pin · FAB · chips (не Figma) | [x] | [x] | xcassets FIG_L01/L03/L25 + wired pin/FAB; chips UI = SF Symbol (L25 PNG = ref); **≠ 100% Figma** |
| **7b** | **Figma later [D]:** все нужные FIG-L* / FIG-* (приоритет L34+L15+L25+L01+L03, затем остальные из промптов) · отдельный файл · не OB_* | [x] | [D] | долг недель; отдельный GO Figma MCP |
| **8** | Device / Simulator QA | [x] | [-] | после **полного** кода (кроме Figma) + `GO на сборку` |

---

## Остаток до «100% кроме Figma» (план → факт)

| Блок | Что | План | Факт |
|------|-----|------|------|
| **B-depth** | live map updates · speed badge · journal scrub · quiet slider · share duration · routes sheet · pin preview · places suggestions · invite/role (01f) | [x] | [x] |
| **01i Pet wizard** | профиль + рутины→Habits; **без** live GPS pin | [x] | [x] |
| **Wave A** | Call Directory · lists empty · Анти-Баннер · Дом/сеть · VK empty · child overview · Full/Limited · splash | [x] | [x] |
| **Wave C** | SOS hold→notify семьи · crash confirm · Tile/evac soon (честный empty) | [x] | [x] |
| **7b Figma** | все FIG-* | [x] | [D] later |
| **P4** | live Pet / dispatch / multi-circle | out | out |

### Шаг 7 — анти-путаница

| Утверждение | Верно? |
|-------------|--------|
| «PNG сделали → Figma 100%» | **Нет** |
| «7a закрыт → можно просить GO на сборку» | **Да** (с владельцем) |
| «7b можно через недели» | **Да**, но **обязан** закрыть по всем необходимым страницам плана |

---

## GATES на каждую закрытую задачу

| Gate | План | Факт |
|------|------|------|
| G1 Один hub; 4-tab внутри | [x] | [x] |
| G2 Нет spy-copy | [x] | [x] |
| G3 Нет fake dispatch/pins | [x] | [x] |
| G4 Loc integrity (если LocManager) | [x] | [x] N/A strings-only |
| G7 Storm + serif | [x] | [x] |
| G8 Нет bot/.env в commit | [x] | [ ] |

---

## Журнал план→факт (коротко)

| Дата | Шаг | Было | Стало | Verify |
|------|-----|------|-------|--------|
| 2026-11-04 | docs v1.4 + checklist | §17 lock | этот файл | — |
| 2026-11-04 | 1–6 | — | код hub Wave B | static |
| 2026-11-04 | 7 split | «Figma до QA» | **7a PNG interim · 7b Figma debt all pages** | docs lock |
| 2026-11-04 | 7a PNG | SF Symbol only | FIG_L01 pin + FIG_L03 FAB in app; L25 PNG in assets/docs | interim; 7b [D] |
| 2026-11-04 | remainder | plan only | B-depth+Pet01i+Wave A+C code (no Figma/P4) | static grep; wait GO на сборку |
| 2026-11-04 | 6 gaps | chrome-only | SOS→sendNeedHelp · pet→habit-reminders · share TTL · quiet filter · MK mapType · Full/Limited gate | code; AnalyticsViewModel(service:) compile fix |

---

## Бэкап до волны

| Артефакт | Где |
|----------|-----|
| Сейф | `~/ALADDIN_VPN_SAFE/family_safety_pre_20261104_172102/` |
| Pointer | `docs/FAMILY_SAFETY_BASELINE_RESTORE_POINTER.txt` |
| Tag local | `family-safety-baseline-20261104_172102` |
| Oct12 keep | `NEW_BACKUP_ALADDIN_20261012_123929` + zip `…_1239.zip` |
