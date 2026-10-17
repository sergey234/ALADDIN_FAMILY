# Релизный канон ALADDIN iOS — для ML-системы (Path B)

**Читать первым перед любым bump / commit / push.**  
Доп. контекст ASC (поезда Version): `docs/ML_SYSTEM_HANDOFF_ASC_VERSION_BUILD_RU.md`.

---

## 0. Сейчас в git / что грузить (не гадать)

```text
App:          ai.aladdin  (ALADDIN AI)
Team:         B3WGHSWL79  (SAUDAPAYDI)   ← НЕ 6CJVBBUGSN
Version:      1.0.1       (= marketing / ASC iOS version)
Build:        10          (= CFBundleVersion / TestFlight)
PREV_BUILD:   10
NEXT_BUILD:   11          ← подставлять ТОЛЬКО после GO на bump
CURRENT_MARKETING_VERSION = 1.0.1
Ветка:        master
Remote:       git@github.com:sergey234/ALADDIN_FAMILY.git
Корень:       /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
```

| Что | Куда смотреть | Сейчас |
|-----|---------------|--------|
| Version | ASC «iOS App Version» + код `MARKETING_VERSION` / `appVersion` | **1.0.1** |
| Build | TestFlight + код `CFBundleVersion` / `buildNumber` | **10** |
| След. Build | только после фразы владельца **«GO на bump»** | **11** |
| След. Version | только если ASC закрыл train 1.0.1 / approve + **GO** | например **1.0.2** |

**Запрещено:** номера 247/248, `family.aladdin.ios`, team `6CJVBBUGSN` как «куда пушить».

**Последний релизный push (канон FC → TF):**  
`6ddf112d` — `fix(ci): ship Family Controls App Store profiles without strip`  
CI: workflow **Build and Upload to App Store** = `.github/workflows/check-secrets.yml`  
Успешный Upload → TestFlight **1.0.1 / build 10** (run вроде **#588**).

**Локально (ещё не в origin):**  
WAVE3 L-фиксы геозон + **DeviceActivityReport → ExtensionKit** (ASC 409) + планы.  
**Политика владельца:** один **commit+push в конце** всех задач WAVE3-пакета → снова **build 10** (без bump).  
Не коммитить «по ходу». One-pager: `docs/AppStore/WAVE3_TOMORROW_TASKS_2026-10-17_RU.md` § «Что уже готово».

---

## 0b. Правильный push + сборка GitHub (копировать)

```text
1) toplevel = …/ALADDIN_iOS · branch = master · origin = ALADDIN_FAMILY.git
2) ./scripts/verify_capabilities_wave3_static.sh   → ALL OK
   (ExtensionKit Report · no UIBackgroundModes location · L gates)
3) Ждать GO: bump? → commit? → push?  (можно «GO commit+push» без bump)
4) git status — нет bot / .env в staging
5) commit → «GO на push» → git push origin master
6) GitHub → Actions → «Build and Upload to App Store» (check-secrets.yml)
7) Зелёный релиз = Archive + Export + Upload  (все три!)
8) ASC → TestFlight → ai.aladdin → 1.0.1 → Builds → Processing → Ready
```

| Не путать | Правда |
|-----------|--------|
| Зелёный Archive / artifact IPA | **≠** TestFlight |
| `UPLOAD FAILED` в `logs_*.zip` | В ASC **ничего нового** |
| Job «зелёный» с artifact после fail upload | Читать шаг Upload / `altool` |

Куда смотреть TF: App Store Connect → Apps → **ALADDIN AI** → **TestFlight** → iOS → version **1.0.1** → Builds.

---

## 1. Два номера — вставлять сюда

### A) Build (номер сборки) — при GO: PREV → NEXT (сейчас 10 → 11)

Везде одно и то же число **NEXT_BUILD**:

| Файл | Поле | Пример сейчас → после bump |
|------|------|----------------------------|
| `Info.plist` | `CFBundleVersion` | `10` → `11` |
| `ALADDIN.xcodeproj/project.pbxproj` | **все** `CURRENT_PROJECT_VERSION = …;` | `10` → `11` |
| `Core/Config/AppConfig.swift` | `buildNumber` **и** `minimumClientBuildForApiContract` | `"10"` → `"11"` |
| `Tests/UnitTests/AppConfigTests.swift` | assert build | `10` → `11` |
| `ALADDINCallDirectory/Info.plist` | `CFBundleVersion` | `10` → `11` |
| `ALADDINDeviceActivityMonitor/Info.plist` | `CFBundleVersion` | `10` → `11` |
| `ALADDINDeviceActivityReport/Info.plist` | `CFBundleVersion` | `10` → `11` |
| `ALADDINShieldConfiguration/Info.plist` | `CFBundleVersion` | `10` → `11` |
| `ALADDINWidgets/Info.plist` | обычно `$(CURRENT_PROJECT_VERSION)` | ок, если pbx = 11 |
| **этот файл** | `PREV_BUILD` / `NEXT_BUILD` | PREV=11, NEXT=12 |

Проверка (должно быть одно значение):

```bash
/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' Info.plist
rg 'CURRENT_PROJECT_VERSION = ' ALADDIN.xcodeproj/project.pbxproj | sort | uniq -c
rg 'static let buildNumber|minimumClientBuildForApiContract' Core/Config/AppConfig.swift
```

Только **+1**. Понижать нельзя. Прыжки +2/+10 — только по явному GO.

### B) Version / marketing — при GO + после «+» version в ASC

**Сначала ASC:** App Store Connect → ALADDIN (`ai.aladdin`) → App Store → **«+»** у списка iOS versions → новая version (напр. `1.0.2`) → Создать.  
Не путать с «Добавить платформу».

**Потом код** (одно и то же marketing):

| Файл | Поле |
|------|------|
| `project.pbxproj` | все `MARKETING_VERSION = …;` |
| `AppConfig.swift` | `appVersion` |
| `AppConfigTests.swift` | assert `appVersion` |
| CallDirectory / Widgets / Monitor / Report / Shield `Info.plist` | `CFBundleShortVersionString` |
| `Info.plist` | обычно `$(MARKETING_VERSION)` |
| **этот файл** | `CURRENT_MARKETING_VERSION = …` |

**Урок:** после approve/close train (как 1.0.0) нельзя заливать новые Build на старый marketing — Upload падает. Сначала ASC «+» version, потом bump в коде, потом push.

---

## 2. Порядок работы (копировать как чеклист)

```text
1) git rev-parse --show-toplevel   → …/ALADDIN_iOS
2) git branch --show-current       → master  (иначе СТОП)
3) git remote -v                   → origin = git@github.com:sergey234/ALADDIN_FAMILY.git
4) Прочитать ПАРУ PREV/NEXT/MARKETING в ЭТОМ файле
5) Показать фактические номера командами из §1
6) Ждать явный GO владельца:
     • «GO на bump»     → менять Build PREV→NEXT
     • «GO на marketing»→ менять Version (после ASC «+»)
     • «GO на commit»   → коммит
     • «GO на push»     → git push origin master
7) Без GO — код номеров / push НЕ трогать
```

---

## 3. Commit + Push (как именно)

### Что коммитить
Только файлы задачи релиза.  
**Никогда в iOS-релизный commit:**

- `telegram_stars_shop_bot/**`
- `.env`, ключи, сертификаты, секреты
- BACKUPS, `.derivedData*`, локальный мусор

Проверка перед commit:

```bash
git diff --cached --name-only | grep -E '^telegram_stars_shop_bot/|^\.env$' && echo STOP || echo OK
```

### Команды push (только после GO на push)

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
git branch --show-current          # master
git push origin master
# ожидать: … master -> master
git log -1 --oneline origin/master
```

Запрещено: force-push в `master`, rebase без GO, push с другой ветки, другой remote.

### Сообщение коммита (стиль)
- bump: `feat(build N): …`
- ci/signing: `fix(ci): …`
- marketing: `fix(ios): marketing X.Y.Z … (keep build N)`

---

## 4. CI → TestFlight (какой workflow)

| Workflow | Файл | Грузит в ASC? |
|----------|------|----------------|
| **Build and Upload to App Store** | `.github/workflows/check-secrets.yml` | **ДА** — это канон |
| test-appstore / legacy appstore | другие yml | не считать релизом |

Триггер канона: **`push` на `master`** (и `workflow_dispatch`).

Зелёный релиз = все три шага зелёные:

1. `Build Archive with Fastlane`
2. Export IPA
3. **Upload to App Store Connect**

Только Archive без Upload → в TestFlight **нет**.  
После Upload: ASC → TestFlight → Processing (10–60+ мин) → Ready to Test.

### Урок `logs_105606115805` (2026-10-17) — Upload 409

| Шаг | Результат |
|-----|-----------|
| Archive + Export | OK |
| Upload `altool` | **UPLOAD FAILED** |
| Artifact `ALADDIN-IPA` | OK — **не** TestFlight |

Ошибка Apple: `ALADDINDeviceActivityReport.appex` как **NSExtension** в `PlugIns/`, нужен **ExtensionKit**  
(`EXAppExtensionAttributes` + embed в `Extensions/`, `dstSubfolderSpec = 16`,  
`productType = com.apple.product-type.extensionkit-extension`).

**Канон Report (не откатывать):**  
`ALADDINDeviceActivityReport/Info.plist` — **без** `NSExtension`, только `EXAppExtensionAttributes`  
+ pbx: `Embed ExtensionKit Extensions` (не вместе с ContentBlocker в PlugIns).  
Static gate: `./scripts/verify_capabilities_wave3_static.sh` → строка ExtensionKit OK.

---

## 4b. Следующая волна capabilities (build 11+)

**SSOT:** `docs/AppStore/CAPABILITIES_WAVE3_BUILD11_MASTER_PLAN_2026-10-17_RU.md`  
**TODO:** `.cursor/CAPABILITIES_WAVE3_TASK_REGISTRY.md` · ids `cap-*`  
**Утро / one-pager:** `docs/AppStore/WAVE3_TOMORROW_TASKS_2026-10-17_RU.md`  
**OUT:** Packet Tunnel / in-app VPN · `UIBackgroundModes location`.

MUST до/в 11: ExtensionKit Report (CI upload) · Device QA ST → FC on · Shield Action · геозоны L · privacy audit.  
Parallel Apple forms: Critical Alerts · Communication Notifications · NE Content Filter/DNS Proxy.

## 5. Family Controls / Screen Time (не ломать)

Apple **Distribution Assigned**. В CI **не снимать** entitlement.

| Секрет GitHub Actions | Содержимое |
|----------------------|------------|
| `PROVISIONING_PROFILE_APP` | App Store profile **с** `family-controls` (не старый без FC) |
| `PROVISIONING_PROFILE_ST_MONITOR` + `_UUID` | DeviceActivityMonitor App Store |
| `PROVISIONING_PROFILE_ST_REPORT` + `_UUID` | DeviceActivityReport App Store |
| `PROVISIONING_PROFILE_ST_SHIELD` + `_UUID` | ShieldConfiguration App Store |

Decode в CI: `scripts/decode_screen_time_profiles_ci.sh`  
Заливка с Mac (если надо обновить): `scripts/set_github_st_fc_secrets.sh` (нужен `gh auth`).

В `Fastfile`: **нет** вызова `ci_strip_family_controls_entitlement.sh`.  
Если ST UUID пустые — CI может skip embed ST (fallback); для прод-сборки со Screen Time секреты **должны** быть.

`AppStoreBuildPolicy.allowsSystemFamilyControls` → `true` только после Device QA + **GO** (не путать с entitlement в профиле).

Имена ST-профилей в pbx Release — **с точкой в конце**, как у Apple  
(напр. `ALADDIN AI DeviceActivityMonitor App Store.`).

**Report = ExtensionKit** (см. §4 урок 409) — Monitor/Shield остаются обычными app-extension в PlugIns.

---

## 6. Перед commit — файлы в pbxproj реально в git

Урок CI: Archive падает, если файл в `project.pbxproj`, но не в git.

1. `git status` — нет забытых `??` релизных `.swift`
2. Новые Sources из pbx есть в `git ls-files`
3. Не тащить bot / `.env`

---

## 7. Рецепт «следующая сборка» (два сценария)

### 7A. Одна сборка 10 в конце пакета (ExtensionKit + WAVE3 L) — **без bump**

```text
A. Доделать код WAVE3-пакета (без промежуточных push)
B. (Опционально раньше) «GO на деплой» geofence-event на MAIN :8002
C. В КОНЦЕ: владелец «GO на commit» + «GO на push»
D. ./scripts/verify_capabilities_wave3_static.sh → ALL OK
E. Один commit (staging checklist в WAVE3_TOMORROW § пакет) · без bot/.env
F. push origin master → CI → Upload ЗЕЛЁНЫЙ → TF 1.0.1 / build 10
G. Если UPLOAD FAILED — читать logs_*.zip шаг Upload
```

### 7B. Сборка 11 (когда скажут GO на bump)

```text
A. Владелец: «GO на bump» (+ commit/push)
B. В коде: Build 10 → 11 во всех файлах §1A
C. В этом файле: PREV_BUILD=11  NEXT_BUILD=12
D. Marketing 1.0.1, ЕСЛИ train ASC ещё открыт
E. commit → push → CI Upload зелёный
F. TestFlight: Version 1.0.1 · Build 11
```

---

## 8. Антипаттерны (СТОП)

- Брать 247/248 как PREV/NEXT  
- Пушить не с `master` / не в `ALADDIN_FAMILY`  
- Класть bot в iOS commit  
- Bump без GO / push без **GO на push**  
- Archive «успех» без Upload → говорить «в TestFlight готово»  
- Снова включать strip Family Controls в CI  
- Вернуть Report на `NSExtension` / embed в PlugIns (ASC 409)  
- Менять marketing без новой version в ASC  
- Local Xcode Archive вместо CI upload как «релиз»

---

## 9. Актуальная пара (обновлять после каждого успешного bump)

```text
PREV_BUILD = 10
NEXT_BUILD = 11
CURRENT_MARKETING_VERSION = 1.0.1
```

После bump build N: `PREV_BUILD = N`, `NEXT_BUILD = N+1`.  
После bump marketing: обновить `CURRENT_MARKETING_VERSION`.
