# WAVE 2 — Screen Time после Assigned: полная карта UI + чеклист PROD 100%

**Дата:** 2026-10-16 (rev **PROD-100** — sync parent↔child, picker locus, store schema, Shield Action backlog)  
**Статус триггеров:**

| Событие | Факт |
|---------|------|
| App Store | **ALADDIN AI одобрен** к распространению (App Review) |
| Family Controls | **Distribution Assigned** на аккаунт (письмо Developer Relations) |
| App IDs | `ai.aladdin` · `…DeviceActivityMonitor` · `…DeviceActivityReport` · `…ShieldConfiguration` |
| App Group | `group.ai.aladdin` |
| Team | `B3WGHSWL79` |
| Request IDs (форма) | `952MH6KQWS`, `L2B4G3Y82L` (team-level; дубликат ок) |
| Build с фичами в git | **9** (без FC в бинаре на момент push) |
| Следующая сборка со Screen Time | **10** (после WAVE 2 + GO bump) |
| Profiles на Mac (2026-10-16) | **4/4 PASS** · FC + `group.ai.aladdin` в `.mobileprovision` |
| Портал W2-A | **DONE** — ждёт фразу GO на код |
| План готовность | **PROD 100%** (решения A–E зафиксированы; код ждёт GO) |

**Связанные каноны:**

| Документ | Роль |
|----------|------|
| Этот файл | **SSOT исполнения WAVE 2** + карта всех экранов + PROD-решения |
| `.cursor/SCREEN_TIME_WAVE2_TASK_REGISTRY.md` | TODO ids `st-*` для трекинга (merge-only) |
| `SCREEN_TIME_STATS_COLLECTION_PLAN_2026-10-16_RU.md` | Техархитектура A–E |
| `SCREEN_TIME_POST_BUILD8_APPROVED_FINAL_PLAN_2026-10-16_RU.md` | Порядок push 9 → FC → vNext |
| `SCREEN_TIME_NOW_VS_AFTER_FIRST_APPROVAL_2026-10-16_RU.md` | Решение «сначала публикация» |
| `FAMILY_CONTROLS_DISTRIBUTION_IMPLEMENTATION_PLAN_2026-09-09_RU.md` | Entitlement / профили |
| `FAMILY_CONTROLS_REQUEST_CLICK_BY_CLICK_2026-10-16_RU.md` | Как подавали заявку |
| `docs/RELEASE_BUILD_PROMPT.md` | Bump 9→10 |

---

## 0. Одна фраза для ML

> **Assigned + App Approved + Profiles 4/4.** План PROD-100 готов. Сейчас: после фразы GO — entitlement + Monitor/Report/ShieldConfiguration → store на child → **POST/GET aggregates на :8002** → реальные минуты у родителя во всех MUST UI → bump **10** → TF → Submit.  
> Picker+auth = **на устройстве ребёнка** (решение A). Данные usage: child DeviceActivity → App Group store → sync API → parent UI. Не путать с bypass/Content Blocker/гео.

---

## 0A. Зафиксированные PROD-решения (не переоткрывать без владельца)

| ID | Решение | Канон v1 (build 10) |
|----|---------|---------------------|
| **P-PICKER** | Где `FamilyActivityPicker` + Screen Time auth | **A — на iPhone ребёнка** (родитель рядом / guided setup «Настроить экранное время»). Tokens остаются локально на child (App Group). Parent **не** шлёт opaque tokens JSON на сервер. |
| **P-SYNC** | Как родитель видит минуты | Child пишет агрегат в store → **POST** на `:8002` (без tokens) → parent **GET** → `parental_time_stats` с `source=server`. TTL: empty если `updatedAt` старше **6 ч** (или явная «нет данных сегодня»). |
| **P-WRITE** | Кто пишет минуты в store | **Monitor** = primary writer (schedule 00:00–23:59, thresholds, mid-day refresh). **Report** = filter/context + системный отчёт UI; **не** единственный DoD для цифр. Main app читает store / server cache. |
| **P-SHIELD** | Shield appex | **Configuration** в build 10 (Identifier уже есть). **Shield Action** = backlog **build 10.1 / 11** (не сюрприз Archive). |
| **P-SCHEMA** | Ключи store | `memberId` + `deviceId` + `dayStart` (календарный день **timezone ребёнка**) + `totalSeconds` + `apps[{tokenHash, displayName?, seconds, limitSeconds?}]` + `source=device_activity` + `updatedAt`. |
| **P-DEBUG** | Non–App Store builds | `allowsSystemFamilyControls=true` в Debug уже сейчас → readiness UX `extension_missing` / empty; **не** путать с App Store path (`false` до Device QA). |
| **P-NOTIF** | Уведомления ST | v1.1 после Monitor events; **не** блокируют MUST UI D1–D3. Push родителю = backend event после sync. |

---

## 1. Архитектура данных (куда присоединяться) — PROD

```
РОДИТЕЛЬ (iPhone)                         РЕБЁНОК (iPhone)
─────────────────                         ────────────────
Family / Parental / Advanced              AuthorizationCenter.requestAuthorization
  лимиты / расписание / сон (правила)     FamilyActivityPicker (РЕШЕНИЕ A — здесь)
       |                                  tokens → App Group (локально)
       |                                  ManagedSettingsStore (shield)
       |                                  DeviceActivityMonitor → PRIMARY write store
       |                                  DeviceActivityReport → filter / системный UI
       |                                         |
       |                                         v
       |                              ScreenTimeUsageStore (App Group)
       |                              memberId+deviceId+dayStart(tz child)
       |                                         |
       |                    POST /api/.../screen-time/usage  (агрегат, без tokens)
       |                                         |
       +------ GET usage aggregate <-------------+
       |
       v
 parental_time_stats source=server|device_activity
 ParentalControlManager.fetchRealScreenTimeStats()
       |
       +-- FamilyTimeControlModal (PRIMARY)
       +-- Advanced time card
       +-- Parental 07 time + readiness
       +-- Devices / Detail status
       +-- FamilyDayStrip chip (v1)
```

**Новый / обязательный код:**

| Компонент | Путь | Роль |
|-----------|------|------|
| Store | `Core/Family/ScreenTimeUsageStore.swift` **NEW** | App Group R/W, day key tz-child, source |
| Sync client | `Core/Family/ScreenTimeUsageSync.swift` **NEW** (или метод в ParentalControlManager) | POST child / GET parent, TTL |
| API `:8002` | parental screen-time usage endpoints **NEW** | Агрегаты only; privacy parental-only |
| Manager | `ParentalControlManager.fetchRealScreenTimeStats()` | store (same device) **или** server cache |
| Monitor appex | `ai.aladdin.DeviceActivityMonitor` **NEW** | Primary writer + events |
| Report appex | `ai.aladdin.DeviceActivityReport` **NEW** | Filter/context + report UI |
| Shield Config | `ai.aladdin.ShieldConfiguration` **NEW** | Системный экран блокировки |
| Shield Action | backlog 10.1/11 | Кастомные кнопки на shield |
| Policy | `AppStoreBuildPolicy.allowsSystemFamilyControls` | `true` только после Device QA |
| Guided setup | Child onboarding / Family card CTA | «Настроить экранное время на телефоне ребёнка» |

## 2. Что НЕ является Screen Time usage (не путать)

| Данные | Где живут | Источник | WAVE 2 меняет? |
|--------|-----------|----------|----------------|
| Лимиты/расписание/сон (правила) | UD + server | Уже есть | Связать с **tokens** picker на child |
| Bypass / обход | API + local journal | Уже есть | Нет |
| Content Blocker сайты | Safari CB | Уже есть | Нет |
| Гео / geofence | Location API | Уже есть | Нет |
| Call Directory / antifake | Свои extensions | Уже есть | Нет |
| «Угрозы» в уведомлениях | parental stats / CB | Уже есть | Нет (кроме ST limit events v1.1) |
| Analytics (04) общая | продукт/маркетинг | Не Screen Time | Не подменять usage |
| `AnalyticsService.DeviceActivity` struct | другая модель | Не Apple ST | Не трогать |

---

## 3. Карта экранов — где что показывать (полнота 100%)

### 3.0. Инвентарь экранов (ничего не забыли)

| # | Экран / модуль | Файл(ы) | ST usage | ST rules | FC readiness | v1 build 10 |
|---|----------------|---------|----------|----------|--------------|-------------|
| 1 | Главная | `01_MainScreen` | — | — | опц. chip v1.1 | **не** обещать минуты |
| 2 | Удобный режим | `SimpleHomeScreen` | — | — | — | deep-link в РК/Семью |
| 3 | Семья — Контроль времени | `02_FamilyScreen` → `FamilyTimeControlModal` | **MUST** | MUST | — | PRIMARY UI |
| 4 | Семья — ScreenTimeSettings / AppLimits | те же модалки | — | MUST→tokens | — | лимиты на tokens |
| 5 | Семья — DayStrip | `FamilyDayStripView` | chip used/limit | limit | — | **MUST v1** (не откладывать) |
| 6 | Семья — bypass/гео/контент/отчёты | другие модалки | — | — | — | **не** ST |
| 7 | Родительский контроль 07 | `07_ParentalControlScreen` | **MUST** | MUST | **MUST** | time + banner |
| 8 | Advanced Protection | `AdvancedProtectionSettingsScreen` | **MUST** | link | — | `source=device_activity\|server` |
| 9 | Настройки 05 | `05_SettingsScreen` | — | — | опц. строка | → Advanced |
| 10 | Профиль 11 | `11_ProfileScreen` | — | — | опц. «РК активен» | не график |
| 11 | Устройства 20 / Detail 22 | `20_DevicesScreen` / `22_DeviceDetailScreen` | статус | — | **MUST** | memberId+deviceId |
| 12 | Уведомления 12 | `12_NotificationsScreen` | events v1.1 | — | — | после Monitor |
| 13 | Аналитика 04 | `04_AnalyticsScreen` | **запрет v1** | — | — | только v1.1 later |
| 14 | Тарифы / TariffCard | `TariffCard` / Parental section | claims gate | — | — | после QA + flag true |
| 15 | Child / teen role UI | child screens + guided setup | collect | apply | auth+picker | **MUST** setup |
| 16 | ParentalControlViewModel | `ViewModels/ParentalControlViewModel.swift` | **MUST fix** | — | — | убрать `"2:45"` |
| 17 | Мёртвый дубль | `Screens/FamilyModals.swift` | **KILL** | — | — | вне target / `#if false` + honesty |
| 18 | Elderly / Games parental | свои экраны | — | — | — | **не** смешивать |
| 19 | Review Notes / ASO | App Store Connect | claims | — | — | только факты после E |
| 20 | Privacy Nutrition Labels | ASC | parental-only | — | — | не реклама/трекинг |

### 3.1–3.12. Детали по экранам (кратко; полная матрица §7)

**Семья (`FamilyTimeControlModal`) — PRIMARY:** `fetchRealScreenTimeStats` + cache `parental_time_stats`; empty copy если нет/TTL; **никогда** мок Instagram 18m.

**РК-07:** остаток/использовано + readiness (`authorization_not_approved` / `extension_missing` / OK).

**Advanced:** тот же ключ, только `source=device_activity` **или** `server`.

**Devices:** «Экранное время: активно / нет данных / нужна авторизация на этом устройстве» + deep-link в Семью → Контроль времени. Без сырых tokens / bundle id.

**Child guided setup (NEW UX, MUST):** короткий flow на child: Auth → Picker → «Готово — данные появятся у родителя после использования». CTA с родительского телефона: «Откройте ALADDIN на телефоне ребёнка».

**Уведомления (v1.1):** `screen_time_limit_reached`, `screen_time_schedule` → tap → Семья → Контроль времени.

---

## 4. Единый контракт отображения + sync API

### 4.1. UI (все экраны с минутами)

1. Данные только из `fetchRealScreenTimeStats()` / `ScreenTimeUsageStore` / GET sync с `source=device_activity|server`.  
2. Пусто / TTL истёк → empty copy, **не** моки.  
3. Формат: `ParentalScreenTimeFormat` (ч/мин RU+EN).  
4. Лимит (правило) и used (факт) подписывать раздельно.  
5. `parental_time_stats` писать **только** из реального pipeline (store persist или sync GET).

### 4.2. API контракт (MUST — W2-C8)

**POST** (child, authenticated family member):

```json
{
  "familyId": "...",
  "memberId": "...",
  "deviceId": "...",
  "dayStart": "2026-10-16",
  "timezone": "Asia/Dubai",
  "totalSeconds": 5760,
  "apps": [
    { "tokenHash": "…", "displayName": "Instagram", "seconds": 1080, "limitSeconds": 1800 }
  ],
  "source": "device_activity",
  "updatedAt": "2026-10-16T14:02:00Z"
}
```

**GET** (parent): тот же shape за `memberId` + `dayStart` (default = сегодня в tz ребёнка).  
**Запрещено в API:** opaque `ApplicationToken` blobs, сырые bundle id всех apps, данные для рекламы.

**Клиент parent:** если `now - updatedAt > 6h` → UI empty + «Нет свежих данных».  
**Клиент child:** POST debounce ≥ 5 мин или при threshold Monitor.

Проверка UI: `./scripts/verify_parental_time_stats_honesty.sh` (после W2 — новый контракт, см. W2-D10).

---

## 5. Чеклист задач WAVE 2 (PROD 100%)

### Фаза W2-A — Портал Apple (владелец) — ✅ DONE 2026-10-16

- [x] **W2-A1** Identifiers: FC Distribution + App Groups на `ai.aladdin` + Monitor + Report + Shield  
- [x] **W2-A2** Profiles App Store 4/4 на Mac; verify `family-controls` + `group.ai.aladdin`  
- [x] **W2-A3** Family Controls Distribution **Assigned**  
- [x] **W2-A4** ALADDIN AI **approved**  
- [x] **W2-A5** Фраза **«GO на WAVE 2»** получена 2026-10-16 — код стартовал

### Фаза W2-B — Инфраструктура Xcode (агент после GO)

- [x] **W2-B1** Entitlement `com.apple.developer.family-controls` на main + Monitor + Report + ShieldConfiguration  
- [x] **W2-B2** Targets DeviceActivityMonitor / DeviceActivityReport / ShieldConfiguration, embed  
- [x] **W2-B3** App Group `group.ai.aladdin` на всех ST targets  
- [x] **W2-B4** `ScreenTimeUsageStore` — schema §0A P-SCHEMA  
- [x] **W2-B5** pbx: новые `.swift` в project  
- [ ] **W2-B6** Debug readiness: без appex → `extension_missing` (Device QA)  
- [x] **W2-B7** Shield **Action** не в v1 (backlog)

### Фаза W2-C — Сбор на ребёнке + sync родителю

- [x] **W2-C1** Auth UI + guided setup (`ChildScreenTimeSetupView`)  
- [x] **W2-C2** `FamilyActivityPicker` на child → App Group  
- [x] **W2-C3** Report extension пишет total в store  
- [x] **W2-C4** Monitor primary refresh + threshold flags  
- [x] **W2-C5** ManagedSettings shields из selection  
- [ ] **W2-C6** pull rules ↔ tokens (дожать AppLimits)  
- [x] **W2-C7** `fetchRealScreenTimeStats()` ← store / server pull  
- [x] **W2-C8** POST/GET `/api/parental-control/screen-time/usage` (iOS + router; **deploy MAIN :8002 ✅ 2026-10-16**, smoke POST/GET 200)  
- [ ] **W2-C9** Лимиты AppLimits ↔ tokenHash  
- [ ] **W2-C10** Multi-child UI binding (schema есть)  
- [x] **W2-C11** Eligibility **все** детские полосы (Child UI + Parental toddler/school/teen/adult + youngAdult 18–22/20+); роли child/teen/young_adult; **не** parent/elderly. SSOT: `FamilyScreenTimeEligibility`. App Store flag **выкл** до Device QA.

### Фаза W2-D — UI (все обязательные места)

- [ ] **W2-D1** `FamilyTimeControlModal` — реальные used/limit (local или server)  
- [ ] **W2-D2** `AdvancedProtectionSettingsScreen.familyTimeControlCard`  
- [ ] **W2-D3** `07_ParentalControlScreen` time card + readiness banner  
- [ ] **W2-D4** `ScreenTimeSettingsModal` / App limits — лимиты на tokens (child apply)  
- [ ] **W2-D5** Devices / DeviceDetail — статус ST per deviceId  
- [ ] **W2-D6** Notifications limit/schedule — **v1.1** после Monitor (не блокер D1–D3)  
- [x] **W2-D7** `FamilyDayStrip` — chip used/limit когда есть cache  
- [ ] **W2-D8** Tariffs / claims — flag остаётся false до QA  
- [x] **W2-D9** Главная / Analytics — без фейковых минут  
- [x] **W2-D10** Loc RU/EN + honesty script WAVE 2 PASS  
- [ ] **W2-D11** `allowsSystemFamilyControls = true` **только после** Device QA  
- [x] **W2-D12** ViewModel `"2:45"` убран  
- [x] **W2-D13** `FamilyModals.swift` не в pbx + warning  
- [x] **W2-D14** Child guided setup CTA в Family Time modal  
- [x] **W2-D15** Empty/TTL copy RU+EN

### Фаза W2-E — QA и релиз build 10

- [ ] **W2-E1** Device QA: 2 iPhone (parent + child), Family Sharing / child Apple ID  
- [ ] **W2-E2** Сценарии: child auth → picker → usage → **POST** → parent видит цифры → shield при лимите  
- [ ] **W2-E3** Archive entitlements check (FC в `.app` + 3× `.appex`)  
- [ ] **W2-E4** Bump **9→10** по `RELEASE_BUILD_PROMPT.md` (GO на bump)  
- [ ] **W2-E5** Commit + push (GO) — без bot/secrets/VPN vault  
- [ ] **W2-E6** TestFlight → Submit  
- [ ] **W2-E7** Review Notes: demo parent+child, шаги auth→picker→usage; ASO только факты  
- [ ] **W2-E8** Privacy Nutrition: Screen Time / device usage = **parental control only**, не трекинг/реклама  
- [ ] **W2-E9** Синхронизировать docs: stats-план §11 + POST_BUILD8 шапка (после старта кода / закрытия волны)

### Фаза W2-F — Backlog (не блокер Submit 10)

- [ ] **W2-F1** Shield Action extension (Identifiers + target)  
- [ ] **W2-F2** Main chip «Экран ребёнка: X / лимит»  
- [ ] **W2-F3** Analytics 04 секция «Экран семьи»  
- [ ] **W2-F4** Push parent на `screen_time_limit_reached`  
- [ ] **W2-F5** Weekly family digest из usage aggregates  

### Не делать (красные флаги)

- [ ] Моки usage (`1h 36m`, Instagram 18m, ViewModel `2:45`)  
- [ ] ST данные в рекламу / брокерам / Analytics marketing  
- [ ] Обещать ST в live build 8/9 до build 10  
- [ ] Путать bypass/CB/гео с минутами Screen Time  
- [ ] Слать opaque tokens на сервер  
- [ ] Picker «только на parent» без локального apply на child (отклонено для v1)  
- [ ] `xcodebuild` / Archive / bump / push без GO владельца  
- [ ] Коммитить `telegram_stars_shop_bot/` / `.env` / VPN secrets handoff  

---

## 6. Порядок работ (наилучший для прода)

```
1) W2-A ✅ портал + profiles 4/4
2) Владелец: «FC Assigned — GO на WAVE 2»
3) W2-B (Xcode + store schema + debug readiness)
4) W2-C (child pipeline) + W2-C8 (API sync) — параллельно iOS/backend по контракту §4.2
5) W2-D MUST UI + ViewModel kill mock + FamilyModals kill + honesty script
6) W2-E Device QA → GO bump 10 → push → Archive → TF → Submit
7) W2-F backlog после стабильного 10
```

Build **9** = без ST (уже в git).  
Системный Screen Time = **build 10** только после E1–E3.

---

## 7. Матрица «экран × данные» (контроль полноты)

| Экран | Usage ST | Rules/лимиты | Readiness FC | Другое parental |
|-------|----------|--------------|--------------|-----------------|
| Main | опц. v1.1 | — | опц. | защита/угрозы |
| SimpleHome | — | — | — | вход в РК |
| Family Time modal | **MUST** | MUST | — | — |
| Family DayStrip | **MUST** chip | limit | — | — |
| Family other modals | — | часть | — | bypass/гео/CB |
| ParentalControl 07 | **MUST** | MUST | **MUST** | CB/мониторинг/гео |
| Advanced Protection | **MUST** | link | — | messages/screenshots |
| Settings | — | — | опц. | → Advanced |
| Profile | — | — | опц. | семья/устройства |
| Devices / Detail | статус **MUST** | — | **MUST** | memberId+deviceId |
| Notifications | v1.1 events | — | — | bypass/threats |
| Analytics 04 | v1.1 only | — | — | не смешивать |
| Tariffs | claims gate | — | — | модули РК |
| Child guided setup | collect | apply | auth+picker | shields |
| ParentalControlViewModel | **MUST** no mock | — | — | — |
| FamilyModals.swift | **KILL** | — | — | — |

---

## 8. GATES (DoD до слова «готово»)

| # | Gate | Evidence |
|---|------|----------|
| G1 | FC Distribution Assigned | письмо Apple ✅ |
| G2 | Entitlement в подписанном Archive | `codesign -d --entitlements` main+appex |
| G3 | 3 appex embed (Monitor/Report/ShieldConfig) | Archive plugins |
| G4 | Auth approved на child | Device QA |
| G5 | Picker selection на child → App Group | Device QA |
| G6 | Parent UI показывает used после sync (не empty при реальном дне) | 2 iPhone QA |
| G7 | Claims / `allowsSystemFamilyControls=true` только после G6 | policy + ASC |
| G8 | Privacy parental-only; honesty script PASS | Nutrition + script |
| G9 | Нет `"2:45"` / `1h 36m` / мёртвый FamilyModals в live path | honesty + grep |
| G10 | API не принимает/не отдаёт opaque tokens | contract test / review |

---

## 9. Статус документа

| Поле | Значение |
|------|----------|
| G1 Assigned | **YES** |
| App Approved | **YES** |
| Портал W2-A | **DONE** |
| План PROD-100 | **YES** (rev этот файл) |
| Код WAVE 2 | Ждёт **«FC Assigned — GO на WAVE 2»** |
| Следующий номер сборки ST | **10** |
| TODO registry | `.cursor/SCREEN_TIME_WAVE2_TASK_REGISTRY.md` |

**Конец WAVE 2 UI map + checklist PROD-100.**

---

## 10. HANDOFF для другой ML-системы (код WAVE 2)

### Читать первым (SSOT)

| Приоритет | Файл |
|-----------|------|
| **1 — этот файл** | `docs/AppStore/SCREEN_TIME_WAVE2_FULL_UI_MAP_AND_CHECKLIST_2026-10-16_RU.md` |
| **2 — TODO ids** | `.cursor/SCREEN_TIME_WAVE2_TASK_REGISTRY.md` |
| 3 | `docs/AppStore/SCREEN_TIME_STATS_COLLECTION_PLAN_2026-10-16_RU.md` |
| 4 | `docs/AppStore/SCREEN_TIME_POST_BUILD8_APPROVED_FINAL_PLAN_2026-10-16_RU.md` |
| 5 | `docs/RELEASE_BUILD_PROMPT.md` |
| 6 | `docs/ML_SYSTEM_START_HERE.md` |

### Уже сделано (не повторять)

- App Store approved · FC Assigned · Profiles 4/4 на Mac  
- Build **9** на GitHub без ST targets  
- Честный empty UI; `fetchRealScreenTimeStats()` = `[]`  
- `allowsSystemFamilyControls = false` в App Store path  
- PROD-решения §0A (picker A, sync C8, Monitor writer, Shield Action backlog)

### СТОП без фразы владельца

> **FC Assigned — GO на WAVE 2**

Без неё: не создавать targets, не entitlement в git, не bump 10, не Archive, не API deploy usage без GO ops.

### Очередь после GO

1. **W2-B** entitlement + 3 targets + store schema + debug readiness  
2. **W2-C** child Auth/Picker/Monitor/Report/Shield + **C8 sync API** + multi-child keys  
3. **W2-D** MUST UI + DayStrip + ViewModel + FamilyModals kill + honesty rewrite + guided CTA  
4. **W2-E** QA 2 iPhone → bump **10** → push → Archive → TF → Submit + Privacy/Review Notes  

### Номер сборки

PREV=**9** → NEXT=**10**. Не 247/248. Team `B3WGHSWL79`. Bundle `ai.aladdin`.

**Конец handoff §10.**
