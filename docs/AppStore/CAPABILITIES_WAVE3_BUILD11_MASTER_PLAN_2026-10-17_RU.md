# Capabilities WAVE 3 — Build 11+ (без Packet Tunnel VPN)

**Дата:** 2026-10-17  
**Пилот:** владелец · **Меха:** агент  
**Канон bump:** `docs/RELEASE_BUILD_PROMPT.md` (сейчас TF **1.0.1 / build 10**, NEXT=**11**)  
**Registry / Cursor TODO:** `.cursor/CAPABILITIES_WAVE3_TASK_REGISTRY.md` · ids `cap-*`  
**Rule:** `.cursor/rules/capabilities-wave3-todo-ssot.mdc`  
**Связка ST:** `.cursor/SCREEN_TIME_WAVE2_TASK_REGISTRY.md` (`st-E1`, `st-D11`, `st-F1` → закрываются через этот план)

---

## 0. Цель (что станет правдой для семьи)

1. Screen Time **реально включён** в App Store path (`allowsSystemFamilyControls=true`) после Device QA.  
2. Ребёнок видит shield с действиями (**спросить родителя / закрыть**), родитель получает запрос.  
3. SOS / падение / срочный антискам доходят **поверх беззвучного** (Critical Alerts — после Apple Assigned).  
4. Веб-фильтр честно: Safari CB сейчас + **системный Content Filter/DNS Proxy** когда Apple даст NE (без VPN Tunnel).  
5. Elderly: опциональный HealthKit fall → пуш семье (без медданных наружу).  
6. Входящий спам: Call Directory + Communication Notifications.  
7. Info.plist / ASO **не врут** (нет записи звонков, MDM, лишних privacy).  
8. **Геозоны** дом/школа/работа: enter/exit → локальный баннер на устройстве + пуш родителю; SOS share When In Use; soft presence без GPS; без continuous GPS / без `UIBackgroundModes location`.

### Вне scope (жёстко)

| Не делаем | Почему |
|-----------|--------|
| **Packet Tunnel / in-app VPN** | Канон — Happ / внешний клиент; отдельный NE Tunnel не в этой волне |
| **`UIBackgroundModes = location` / continuous GPS** | Review 2.5.4; батарея; у нас significant-change + region monitoring |
| Запись звонков / полный MDM | Apple consumer почти не даёт; не обещать |
| Strip Family Controls в CI | Урок #585–#588; честный FC уже в профилях |

---

## 1. Уроки сегодня (скорость WAVE 2 → темп WAVE 3)

| Что сработало | Как повторить |
|---------------|---------------|
| FC Distribution уже Assigned → код+профили+CI за один день | Параллельно: форма Apple **и** код за флагом |
| Secrets + Fastfile без strip → CI #588 SUCCESS | Для Shield Action / NE — сразу профили в GitHub secrets |
| `allowsSystemFamilyControls=false` до QA | То же для Critical Alerts / HealthKit / NE |
| Device QA в конце волны ST | **Сначала** QA build 10 (2 iPhone), потом flip FC + build 11 |

**Рекомендуемый темп (как сегодня):**

```text
День 0: план + L0 диагноз геозон ✅ · L3/L5/L1/L2 код без девайса
День 1: Device QA ST + walk-test геозон (G11/G12) → GO flip FC
День 1–2: Shield Action + L4 APNs + sync + privacy → bump 11 (MUST)
Параллельно: Critical / Comm / NE Filter формы
День 3+: Critical/HealthKit/NE/L11 за флагами → 11.x/12 когда Assigned
```

Build **11** = MUST: ST on + Shield Action + **геозоны алерты (L)** + honesty + privacy.  
Critical / NE / HealthKit App Store path — код за флагом до Assigned/GO.

---

## 2. GATES (до слова «готово»)

| # | Gate | Доказательство |
|---|------|----------------|
| G1 | Device QA ST на 2 iPhone (parent+child) PASS | чеклист `cap-A0` + скрины/журнал |
| G2 | `allowsSystemFamilyControls=true` только после G1+GO | `AppConfig.swift` + unit test |
| G3 | Shield Action в Archive + подпись | `codesign -d --entitlements` appex |
| G4 | Parent↔child minutes sync без фейка | curl POST/GET + UI empty/TTL |
| G5 | Critical Alerts: entitlement **или** честный flag off | portal Assigned / policy false |
| G6 | NE Filter: нет Packet Tunnel в pbx/entitlements | grep CI verify |
| G7 | HealthKit: только fall→push, без экспорта медданных | Review Notes + код |
| G8 | Privacy plist: ключ есть ⇒ фича/экран есть | audit table `cap-H1` |
| G9 | CI Upload TF build 11 SUCCESS | GitHub Actions |
| G10 | ASO/Notes: нет MDM / call recording | текст Submit |
| G11 | Геозона enter/exit: локальный баннер на device + событие в ленте | Device QA walk / simulate |
| G12 | Родитель на 2-м iPhone получает family alert (не только чат soft) | 2 devices |
| G13 | Нет `location` в UIBackgroundModes; purpose strings конкретные | plist + Review Notes |

---

## 3. Карта «есть → делаем»

### 3.1 Уже есть (не форма FC) — улучшаем

| Блок | Сейчас | WAVE 3 |
|------|--------|--------|
| Family Controls / ST | Assigned · build 10 · flag **false** | QA → flag **true** · sync honesty |
| Push / App Groups / Domains | ok | Critical category + App Group для Shield Action |
| Safari Content Blocker | extension | Честный copy: «Safari»; рядом NE Filter later |
| Call Directory | antifake sync | + Communication Notifications |
| Гео / геозоны | Always+WhenInUse strings; bootstrap; EventStore local UN; soft chat | **Фаза L MUST** — починить алерты + product track §4.L |
| Soft presence «я в порядке» | API без GPS | Усилить UX / offline queue |
| Location Bubble | `/api/location-bubble/*` premium | Opt-in + честный copy (не трекинг) |
| Семья / E2EE / safe-word / habits | `:8002` | Incidents → Critical push mapping |
| Antifake Share | Share + server | Без изменений scope |

### 3.2 Добавляем (с заявкой / capability)

| # | Capability | Форма Apple? | Build 11 MUST | Флаг |
|---|------------|--------------|---------------|------|
| 1 | **Shield Action** | Нет (тот же FC) | **Да** | FC on |
| 2 | **Critical Alerts** | **Да** | Код+flag; ship on после Assigned | `allowsCriticalAlerts` |
| 3 | **NE Content Filter / DNS Proxy** | **Да** | Дизайн+stub; ship on после Assigned | `allowsSystemContentFilter` |
| 4 | **HealthKit** (fall) | Capability + Review | Код+flag | `allowsHealthKitIntegration` |
| 5 | **Communication Notifications** | Portal entitlement | Код+flag | `allowsCommunicationNotifications` |

### 3.3 Не делаем

- Packet Tunnel VPN  
- Continuous GPS / `UIBackgroundModes location`  
- Обещания записи звонка / MDM  

### 3.4 Location product (канон — делать)

| Фича | Разрешение | Как |
|------|------------|-----|
| Геозоны дом/школа/работа → enter/exit | **Always** + region monitoring | Local UN на device + **server APNs** родителю |
| «Поделиться локацией сейчас» / SOS | **When In Use** + Precise коротко | One-shot `requestLocation` |
| Soft presence «я в порядке» | **Без GPS** | Уже есть — усилить |
| Location Bubble / privacy-зоны | Opt-in premium | Честный copy, не live-трек |
| Battery | significant-change + GPS boost у границы | Уже в `LocationManager` — не ломать |
| Громкий алерт «вышел из зоны» | Critical Alerts (фаза D) | После Apple Assigned |

**Форма Apple на Location — не нужна.** Только privacy strings + Nutrition Labels.

---

## 4. Фазы исполнения

### Фаза L — Location / Geofences (MUST build 11, параллельно A/B)

#### L.0 Диагноз: «вхожу/выхожу — пуш не приходит» (2026-10-17)

Цепочка сейчас:

```text
CL didEnter/Exit → GeofenceEventStore.record
  → local UN (.family) на ТОМ ЖЕ устройстве
  → GeofenceFamilyBridge.softNotify (family chat, throttle 30 мин) ≈ косвенный APNs родителю
```

**Нет отдельного server endpoint «geofence event → APNs parent».** Родитель на втором телефоне зависит от chat-push.

| # | Причина | Где в коде | Симптом |
|---|---------|------------|---------|
| L0.1 | Нет согласия мест | `GeofencePlacesConsentStore.hasAccepted` → bootstrap **return** | Регионы не мониторятся |
| L0.2 | Нет **Always** | `startMonitoring` требует `authorizedAlways`; при When In Use — throw | Enter/exit не приходят от iOS |
| L0.3 | Нет координат зоны | geocode fail / пустой address → «пропущена (нет координат)» | Зона в UI есть, CL — нет |
| L0.4 | Неверный центр (orphan `FamilyModals`) | hardcoded Москва `55.7558,37.6173` | Ложный fire / никогда не fire (файл **не в target**, но не оживлять) |
| L0.5 | iOS notifications denied / provisional | `UNUserNotificationCenter` | Local UN не виден |
| L0.6 | Категория Family выкл в настройках ALADDIN | `isCategoryEnabled(.family)` | `sendLocalNotification` skip |
| L0.7 | DND / quiet hours / rate limit 10/h | `willPresent` | Баннер подавлен (особенно foreground) |
| L0.8 | «Только важные» | `geofence_place_departure` / place arrival **не** в `isImportantNotificationType` | Exit и «место» молчат; school/home arrival — ок |
| L0.9 | Soft path родителю = chat + throttle 30м | `GeofenceFamilyBridge` | 2-й телефон молчит / раз в полчаса |
| L0.10 | Нет `familyId` / chat API fail | soft enqueue offline | Родитель без APNs |
| L0.11 | Уже внутри зоны при старте мониторинга | нет `requestState(for:)` после start | Первый enter не приходит |
| L0.12 | Радиус / GPS / Low Power / Precise off | CL system | Ложные/пропущенные границы |
| L0.13 | Ожидание пуша на **другом** телефоне при тесте на одном | product gap | «Я вошёл — на моём нет / на родителе нет» |
| L0.14 | Purpose strings слишком общие | Info.plist | Риск Review + путаница пользователя |
| L0.15 | Серверный `check_geofence_triggers` = **MOCK** (только log) | `security/api/.../parental_control_router.py` | Нет реального APNs с бэка |

#### L.0b Кто что проверяет (агент vs владелец)

**Уже подтверждено агентом по коду (2026-10-17) — не нужно гадать:**

| Факт | Доказательство |
|------|----------------|
| Local UN только на device, где сработал CL | `GeofenceEventStore.record` → `sendLocalNotification` |
| Родителю только soft chat, throttle **30 мин** | `GeofenceFamilyBridge.throttleSeconds = 30*60` |
| Нет endpoint geofence→APNs parent | grep; soft = `sendFamilyChatMessage` |
| `UIBackgroundModes` **без** `location` | `Info.plist`: fetch + remote-notification |
| Always обязателен для region monitoring | `startMonitoring` → `hasRequiredAuthorization(forBackground: true)` |
| Bootstrap без Always всё равно зовёт load (ловит throw) | `GeofenceMonitoringBootstrap` guard только WhenInUse+ |
| Consent gate | `hasAccepted` → early return |
| Important whitelist дырявый | important: school/home **arrival** + noshow; **нет** place_departure / place_arrival |
| Family category gate | `isCategoryEnabled(.family)` ← `familyEnabled` |
| Quiet / DND / max 10/h | `willPresent` + `NotificationSettingsScreen` defaults |
| Orphan Москва-заглушка | `FamilyModals.swift` **не в target** |
| Parental server geofence push = MOCK log | `check_geofence_triggers` |

**Агент может ещё сделать без девайса (в плане = код-фиксы):**

| ID | Что |
|----|-----|
| L3 | Добавить все `geofence_*` в important types |
| L1 | Bootstrap: не вызывать `startMonitoring` без Always; UI статус |
| L2 | `requestState(for:)` в `didStartMonitoringFor` |
| L5 | Переписать purpose strings |
| L10 | `verify_*.sh` grep no `location` background mode |
| L4 | Новый API + APNs (нужен **GO деплой**) |

**Владелец проверяет на телефоне (только вы / Device QA):**

##### Чеклист 1 — один iPhone (локальный баннер)

1. **iOS Настройки → ALADDIN → Геолокация → «Всегда»** (не «При использовании»). Precise = Вкл на время теста.  
2. **iOS Настройки → Уведомления → ALADDIN → Баннеры + Звук = Вкл.**  
3. В ALADDIN: **Семья → Места** — принять согласие мест (если ещё не).  
4. Статус места: должно быть «мониторинг» / monitoring, не «нужен Always» / «нет координат».  
5. ALADDIN → **Настройки уведомлений**: Семья = Вкл; «Только важные» = **Выкл** на тест; тихие часы / DND / лимит/час = Выкл.  
6. Выйти из зоны пешком/на авто **дальше радиуса** (часто 50–150 м), подождать 1–3 мин (iOS не мгновенный).  
7. Смотреть **два места**:  
   - A) баннер / lock screen  
   - B) лента событий мест в Family  

| Результат A | Результат B | Вердикт |
|-------------|-------------|---------|
| нет | нет | Always/coords/consent/мониторинг (L0.1–4, L0.11–12) |
| нет | **есть** | уведомления глушатся (L0.5–8) — пришлите скрин настроек |
| **есть** | есть | локальный путь OK → тест родителя |

##### Чеклист 2 — второй iPhone (родитель)

1. Тот же family, родитель залогинен, push на родителе работает (любой family chat тест).  
2. На детском — снова enter/exit.  
3. На родителе за 5 мин: push / сообщение в family chat?  

| Родитель | Вердикт |
|----------|---------|
| тишина | ожидаемо сейчас (L0.9–10, L0.15) → нужен **L4** |
| chat есть, баннера нет | chat OK, APNs chat presentation / настройки родителя |
| баннер есть | soft path случайно сработал — всё равно делаем L4 |

##### Что прислать агенту (если снова «нет пуша»)

- Скрин: iOS Location = Always  
- Скрин: статус места в ALADDIN (monitoring / need always / no coords)  
- Скрин: настройки уведомлений ALADDIN (Семья / только важные)  
- Ответ: событие в ленте мест **да/нет**  
- Тест: один телефон или parent+child  

| ID | Задача | DoD |
|----|--------|-----|
| **cap-L0** | Зафиксировать диагноз (этот §) | ✅ docs |
| **cap-L1** | Fix: Always gate в bootstrap + UI «нужен Always» до monitoring | status `geofence_status_need_always` → блокирует claim «мониторим» |
| **cap-L2** | Fix: `requestState(for:)` после `didStartMonitoring` + optional synthetic enter/exit | первый переход не теряется |
| **cap-L3** | Fix: important types = все geofence_* enter/exit | «Только важные» не глотает exit |
| **cap-L4** | Fix: dedicated server `POST /api/location/geofence-event` → APNs parents (не только chat) | 2 iPhone QA |
| **cap-L5** | Purpose strings RU/EN конкретные (геозоны + SOS); Review Notes «no continuous tracking» | plist + ASC |
| **cap-L6** | Place picker: lat/lon с карты / current GPS; geocode fail → честный error | нет зоны без coords |
| **cap-L7** | SOS / share location now (When In Use + Precise temporary) | Device QA |
| **cap-L8** | Soft presence polish (без GPS) + offline | smoke |
| **cap-L9** | Location Bubble: opt-in copy + premium gate honesty | UI |
| **cap-L10** | Verify: нет `location` в UIBackgroundModes; diagnose checklist в UI | script + screen |
| **cap-L11** | Geofence enter/exit → optional Critical (после D Assigned) | связка cap-D* |
| **cap-L12** | UX progressive: When In Use → экран «зачем Always» → Always **только** при включении мест | Device QA |
| **cap-L13** | Sync геозон с `:8002` (`/api/location/geofences/*`); убрать demo/fake coords из live UI | curl + UI |
| **cap-L14** | Precise Location request только setup зоны / SOS (Approximate по умолчанию) | code |
| **cap-L15** | ASC Privacy Nutrition + Review Notes: geofence alerts, **not** continuous tracking | ASC |
| **cap-L16** | Явный тумблер у члена семьи; нет скрытого GPS «для аналитики» | UI + policy |

### Фаза A — Закрытие Screen Time (пререквизит build 11)

| ID | Задача | DoD |
|----|--------|-----|
| **cap-A0** | Device QA 2 iPhone: auth → picker child → Monitor пишет → parent видит used/limit → shield | PASS / FAIL журнал |
| **cap-A1** | `AppStoreBuildPolicy.allowsSystemFamilyControls = true` + тест | GO пилота |
| **cap-A2** | Prod smoke usage sync MAIN `:8002` parent↔child | curl + UI |
| **cap-A3** | ManagedSettings лимиты / empty / TTL copy | honesty script |
| **cap-A4** | Archive: FC на main+Monitor+Report+ShieldConfig | entitlements dump |

Связь: закрывает `st-E1`, `st-D11`, частично `st-E2`.

### Фаза B — Shield Action (MUST build 11)

| ID | Задача | DoD |
|----|--------|-----|
| **cap-B1** | Target `ALADDINShieldAction` · bundle `ai.aladdin.ShieldAction` · FC + App Group · профиль Distribution | Identifiers + profile на Mac |
| **cap-B2** | `ShieldActionDelegate`: Ask Parent / Close · запись в App Group · UI copy RU/EN | Device QA |
| **cap-B3** | GitHub secrets + Fastfile sign (как ST×3) · **без strip** | CI dry path |
| **cap-B4** | Пуш родителю «ребёнок просит снять блок» (обычный push сначала) | server event + iOS |

Закрывает `st-F1`.

### Фаза C — Заявки Apple (параллельно, Account Holder)

| ID | Форма | Текст (смысл) |
|----|-------|---------------|
| **cap-C1** | Critical Alerts | Family SOS, fall alert, urgent scam-call — не маркетинг |
| **cap-C2** | Communication Notifications | Incoming spam label + Call Directory |
| **cap-C3** | Network Extension **Content Filter** и/или **DNS Proxy** | Parental web filter all apps; **explicitly NOT packet-tunnel VPN** |
| **cap-C4** | После Assigned: галочки на App IDs + новые profiles → secrets | как FC |

Пока ждём — код за флагами, App Store path = false.

### Фаза D — Critical Alerts (код + сервер)

| ID | Задача | DoD |
|----|--------|-----|
| **cap-D1** | Entitlement `com.apple.developer.usernotifications.critical-alerts` + `UNAuthorizationOptions.criticalAlert` | только после C1 |
| **cap-D2** | Server: payload `interruption-level: critical` / category SOS\|FALL\|SCAM | MAIN `:8002` + push path |
| **cap-D3** | iOS: deep link → Elderly / Family incident | UI |
| **cap-D4** | `allowsCriticalAlerts` в `AppStoreBuildPolicy` | false до Assigned+GO |

Сценарии: «мне плохо», fall, срочный антискам-звонок, safe-word escalate (если уже есть incident).

### Фаза E — Communication Notifications + Call Directory

| ID | Задача | DoD |
|----|--------|-----|
| **cap-E1** | Entitlement Communication Notifications · intent / UI входящего | после C2 |
| **cap-E2** | Call Directory setup UX + sync antifake | уже есть каркас — polish |

### Фаза F — NE Content Filter / DNS Proxy (без VPN)

| ID | Задача | DoD |
|----|--------|-----|
| **cap-F1** | Дизайн: FilterProvider vs DNS Proxy; правила из parental API; **запрет** Packet Tunnel target | ADR в этом файле §7 |
| **cap-F2** | Extension + App Group + apply blocklist/allow | после C3 Assigned |
| **cap-F3** | UI Parental: «Safari» vs «Все приложения (системный фильтр)» | честные строки |
| **cap-F4** | CI profiles / secrets NE | как ST |

### Фаза G — HealthKit (elderly fall)

| ID | Задача | DoD |
|----|--------|-----|
| **cap-G1** | HealthKit capability · `NSHealthShareUsageDescription` / Update · только fall-related | plist |
| **cap-G2** | Observer → family incident / push (не Critical пока D не on) | код |
| **cap-G3** | `allowsHealthKitIntegration=true` App Store после GO | policy + test |

### Фаза H — Privacy / Review hygiene

| ID | Задача | DoD |
|----|--------|-----|
| **cap-H1** | Аудит Info.plist: HomeKit, Music, Bluetooth… — удалить или довести фичу | таблица до/после |
| **cap-H2** | Review Notes + ASO: ST, filter, alerts; **нет** call recording / MDM | текст |

### Фаза I — Ship build 11

| ID | Задача | DoD |
|----|--------|-----|
| **cap-I1** | `scripts/verify_capabilities_wave3_static.sh` (FC, no tunnel, flags, Shield Action in pbx) | OK |
| **cap-I2** | Bump 10→11 везде по `RELEASE_BUILD_PROMPT` | только **GO на bump** |
| **cap-I3** | Commit+push → CI Upload | только **GO commit/push** |
| **cap-I4** | Device QA build 11 (все MUST-треки) | чеклист §6 |
| **cap-I5** | Submit / Notes | GO владельца |

---

## 5. AppStoreBuildPolicy (целевое состояние)

```swift
// APP_STORE_BUILD
allowsSystemFamilyControls        // true  после cap-A0+A1 GO
allowsHealthKitIntegration        // true  после cap-G* GO
allowsCriticalAlerts              // NEW — false until Apple Assigned + GO
allowsCommunicationNotifications  // NEW — false until entitlement + GO
allowsSystemContentFilter         // NEW — false until NE Assigned + GO
// NEVER: in-app Packet Tunnel flag in this wave
```

Debug/non–App Store: как сейчас, можно true для локальной разработки (кроме NE без профиля).

---

## 6. Чеклист реализации (отмечать здесь)

### L — Location / Geofences (MUST)
- [x] **cap-L0** Диагноз no-push (таблица причин)
- [x] **cap-L1** Always gate + honest monitoring status
- [x] **cap-L2** `requestState` after start monitoring
- [x] **cap-L3** Important types: all geofence enter/exit
- [ ] **cap-L4** Server geofence-event → APNs parents (**код ✅ · деплой ⏳ GO**)
- [x] **cap-L5** Purpose strings (Review Notes — при Submit)
- [ ] **cap-L6** Place coords from map/GPS (no silent skip)
- [ ] **cap-L7** SOS / share location When In Use
- [ ] **cap-L8** Soft presence polish
- [ ] **cap-L9** Location Bubble honesty
- [x] **cap-L10** Verify no background `location` mode
- [ ] **cap-L11** Critical Alerts for geofence (after D)
- [ ] **cap-L12** Progressive WhenInUse → Always UX
- [ ] **cap-L13** Sync геозон :8002 + kill fake coords
- [ ] **cap-L14** Precise only setup / SOS
- [ ] **cap-L15** ASC Privacy labels + Notes (not continuous track)
- [ ] **cap-L16** Member toggle / no hidden GPS

**One-pager завтра:** [`WAVE3_TOMORROW_TASKS_2026-10-17_RU.md`](WAVE3_TOMORROW_TASKS_2026-10-17_RU.md)

### BLOCKER перед CI Upload (2026-10-17)

`logs_105606115805`: Archive OK · **Upload FAILED 409** — `ALADDINDeviceActivityReport` был NSExtension/PlugIns.  
Фикс ExtensionKit + WAVE3 L — **локально**.  
**Политика:** один **commit+push в конце** всех задач пакета → снова **build 10** (без bump).  
Деплой L4 — отдельный GO. Verify: `./scripts/verify_capabilities_wave3_static.sh`.  
Staging list: `WAVE3_TOMORROW_TASKS` § «Что уже готово».

### A — Screen Time close
- [ ] **cap-A0** Device QA 2 iPhone build 10
- [ ] **cap-A1** `allowsSystemFamilyControls=true` + test
- [ ] **cap-A2** Sync minutes prod smoke
- [ ] **cap-A3** ManagedSettings / honesty
- [ ] **cap-A4** Archive entitlements FC

### B — Shield Action
- [ ] **cap-B1** Target + App ID + profile
- [ ] **cap-B2** Ask Parent / Close + Loc
- [ ] **cap-B3** CI secrets + Fastfile
- [ ] **cap-B4** Parent notify

### C — Apple forms
- [ ] **cap-C1** Critical Alerts submitted
- [ ] **cap-C2** Communication Notifications submitted
- [ ] **cap-C3** NE Content Filter/DNS Proxy submitted (NOT tunnel)
- [ ] **cap-C4** Assigned → App IDs + profiles + secrets

### D — Critical Alerts
- [ ] **cap-D1** Entitlement + auth options
- [ ] **cap-D2** Server critical payload
- [ ] **cap-D3** iOS routing UI
- [ ] **cap-D4** Policy flag

### E — Comm + Call Directory
- [ ] **cap-E1** Communication Notifications
- [ ] **cap-E2** Call Directory polish

### F — NE Filter (no VPN)
- [ ] **cap-F1** Design ADR
- [ ] **cap-F2** FilterProvider code
- [ ] **cap-F3** Parental honesty UI
- [ ] **cap-F4** CI NE profiles

### G — HealthKit
- [ ] **cap-G1** Capability + privacy
- [ ] **cap-G2** Fall → incident
- [ ] **cap-G3** Policy true + GO

### H — Hygiene
- [ ] **cap-H1** Plist audit
- [ ] **cap-H2** Review Notes / ASO

### I — Ship
- [ ] **cap-I1** Static verify script
- [ ] **cap-I2** Bump 11 (GO)
- [ ] **cap-I3** CI Upload (GO)
- [ ] **cap-I4** Device QA 11
- [ ] **cap-I5** Submit

---

## 7. ADR: NE Filter vs DNS Proxy (черновик для cap-F1)

| Вариант | Плюс | Минус |
|---------|------|-------|
| **A. Content Filter (NEFilterData/Control)** | Блок URL/host per flow | Сложнее, строже Review |
| **B. DNS Proxy** | Проще семантика «блок доменов» | Не всё приложение-трафик; DNS over HTTPS edge cases |
| **C. Только Safari CB** (уже есть) | Без заявки | Только Safari — уже честно писать в UI |

**Рекомендация пилоту:** подать **Content Filter** (A) как основной product claim «вне Safari»; DNS Proxy (B) — опционально второй App ID, если Apple/техника проще.  
**Запрет:** любой `NEPacketTunnelProvider` / `packet-tunnel-provider` в этой волне.

---

## 8. Порядок работ агента (без опережения GO)

1. Docs/registry/rule ✅ + **cap-L0 диагноз** ✅.  
2. **Параллельно коду без девайса:** cap-L3 (important types), cap-L5 (strings), cap-L1/L2 (bootstrap Always + requestState), cap-L10 verify.  
3. **cap-L4** server APNs — после GO на деплой MAIN `:8002`.  
4. **Стоп** → владелец **cap-A0** Device QA ST **и** walk-test геозон (G11/G12).  
5. После PASS ST → cap-A1…A4 + cap-B* код.  
6. Параллельно формы cap-C* (Account Holder).  
7. cap-D/E/F/G + **cap-L11** — за флагами до Assigned + GO.  
8. cap-H + cap-L5/L9 параллельно.  
9. cap-I только по **GO на bump** / **GO commit+push** / **GO на сборку**.

### Красные флаги

- Включать Critical/NE/HealthKit в App Store path без Assigned/GO  
- Добавлять Packet Tunnel **или** `UIBackgroundModes location` «заодно»  
- Оживлять orphan `FamilyModals.swift` (Москва-заглушка)  
- Strip FC / Shield Action в CI  
- `git restore` LocalizationManager  
- Commit bot / `.env` / VPN secrets handoff  

---

## 9. Тексты заявок Apple (черновик EN)

### Critical Alerts
> ALADDIN is a family safety app. Critical Alerts are required so caregivers receive time-sensitive notifications when an elderly member triggers SOS / fall detection, or when a high-risk scam call is detected — including when the phone is silenced. Not used for marketing.

### Communication Notifications
> Used with Call Directory to present clearer incoming-call UI for numbers identified as scam/spam for family protection. Not used for advertising.

### Network Extension — Content Filter (not VPN)
> We request Content Filter Network Extension to apply parent-configured web/app domain rules system-wide for supervised family use cases. We do **not** request Packet Tunnel VPN; VPN connectivity remains via the user’s existing client (Happ). Purpose is parental filtering only.

---

## 10. Definition of Done WAVE 3 (MUST ship в build 11)

- [x] План + registry + Cursor TODO  
- [x] cap-L0 диагноз geofence no-push  
- [ ] G1–G4, G6 (no tunnel), G8, **G11–G13** PASS  
- [ ] Shield Action в TF  
- [ ] FC flag on  
- [ ] Geofence local + parent APNs (L3/L4)  
- [ ] Privacy audit + location purpose strings  
- [ ] CI Upload build 11 SUCCESS  

**Stretch в 11** (если Assigned успели): Critical / Comm Notifications / L11 geofence critical.  
**Ожидаемо в 11.x/12:** NE Filter + HealthKit App Store on.

---

## 11. Связь с сегодняшними артефактами

| Артефакт | Роль в WAVE 3 |
|----------|----------------|
| FC profiles APP+ST×3 в GitHub secrets | Шаблон для Shield Action (+ NE later) |
| `6ddf112d` no-strip Fastfile | Не откатывать |
| MAIN `:8002` usage sync | cap-A2 / cap-B4 / cap-D2 |
| `AppStoreBuildPolicy` | единая калитка всех новых capabilities |
| RELEASE_BUILD_PROMPT NEXT=11 | cap-I2 |

---

*Конец SSOT WAVE 3. Статусы — только в registry + merge-only Cursor TODO `cap-*`.*
