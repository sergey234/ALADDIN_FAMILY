# Релизный канон ALADDIN iOS — для ML-системы (Path B)

**Читать первым перед любым bump / commit / push.**
Доп. контекст ASC (поезда Version): `docs/ML_SYSTEM_HANDOFF_ASC_VERSION_BUILD_RU.md`.

---

## 0. Сейчас в git / что грузить (не гадать)

```text
App:          ai.aladdin  (ALADDIN AI)
Team:         B3WGHSWL79  (SAUDAPAYDI)   ← НЕ 6CJVBBUGSN
Version:      1.0.1       (= marketing / ASC iOS version)
Build:        14          (= CFBundleVersion / next upload candidate)
PREV_BUILD:   14
NEXT_BUILD:   15          ← подставлять ТОЛЬКО после GO на bump
CURRENT_MARKETING_VERSION = 1.0.1
Ветка:        master
Remote:       git@github.com:sergey234/ALADDIN_FAMILY.git
Корень:       /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
```

| Что | Куда смотреть | Сейчас |
|-----|---------------|--------|
| Version | ASC «iOS App Version» + код `MARKETING_VERSION` / `appVersion` | **1.0.1** |
| Build | код `CFBundleVersion` / `buildNumber` | **14** |
| TestFlight max Ready | ASC TestFlight → iOS version 1.0.1 | **11 Ready** (ожидаемо) |
| След. Build | только после следующей фразы владельца **«GO на bump»** | **15** |
| След. Version | только если ASC закрыл train 1.0.1 / approve + **GO** | например **1.0.2** |

**Запрещено:** номера 247/248, `family.aladdin.ios`, team `6CJVBBUGSN` как «куда пушить».

**Что уже в Apple / GitHub (факт вечер 2026-10-17, владелец видит в кабинете):**

| Слой | Факт |
|------|------|
| Commit tip **origin/master** | `3f59110c` — ASC upload checks (HK string · Shield Action id · host NE) |
| Код в git (номера) | Version **1.0.1** · Build **14** |
| TestFlight | **1.0.1 / 11** был в ASC; candidate **12** — Bypass card + Content Filter compile fix |
| CI канон | `check-secrets.yml` («Build and Upload to App Store») |
| Зелёный релиз | **Archive + Export + Upload** все OK · Job green ≠ TF, если `altool` FAIL |
| Урок подписи | Content Filter + Shield Action: UUID в pbx Release SPECIFIER, не имя `… App Store.` (§4c) |
| След. Upload | текущий candidate **14**; следующий после него — только **15** |

One-pager дня: `docs/AppStore/WAVE3_TOMORROW_TASKS_2026-10-17_RU.md`.
Portal session: `docs/AppStore/WAVE3_PORTAL_6_TASKS_STATUS_AND_CLICKS_RU.md`.

---

## 0a. Как агент / ML заходит в GitHub (секреты + Actions) — канон

**Не** логиниться в github.com через браузер с паролем в чате.
**Не** вставлять токены / содержимое `.mobileprovision` / base64 в коммит или в ответ пользователю.

### Инструмент
На Mac владельца уже есть **GitHub CLI** `gh`, аккаунт **`sergey234`**, auth через **keyring** (scopes: `repo`, `read:org`, …).

```bash
# проверка (без секретов в выводе)
gh auth status
# ожидаемо: Logged in to github.com as sergey234
```

Репозиторий релиза: **`sergey234/ALADDIN_FAMILY`**
Remote в git: `git@github.com:sergey234/ALADDIN_FAMILY.git`

### Как обновляли provisioning secrets (2026-10-17)

1. Владелец скачал `.mobileprovision` в `~/Downloads/…`.
2. Агент на Mac:
   - `security cms -D -i …` → UUID, `family-controls`, `group.ai.aladdin`
   - `base64 -i file.mobileprovision | tr -d '\n' > …/NAME.b64`
   - staging **вне репо**: `~/ALADDIN_VPN_SAFE/github_profile_secrets_staging_*`
3. Запись в Actions secrets:

```bash
gh secret set PROVISIONING_PROFILE_APP --repo sergey234/ALADDIN_FAMILY < …/PROVISIONING_PROFILE_APP.b64
gh secret set PROVISIONING_PROFILE_ST_SHIELD_ACTION --repo sergey234/ALADDIN_FAMILY < …/….b64
gh secret set PROVISIONING_PROFILE_ST_SHIELD_ACTION_UUID --repo sergey234/ALADDIN_FAMILY < …/….txt
# список имён (не значения):
gh secret list --repo sergey234/ALADDIN_FAMILY | grep PROVISIONING_PROFILE
```

Альтернатива пачкой (старый скрипт, нужен staging dir): `scripts/set_github_st_fc_secrets.sh`.

### Что лежит в GitHub Actions (релевантное ST/FC)

| Secret | Назначение | Обновлено |
|--------|------------|-----------|
| `PROVISIONING_PROFILE_APP` | main `ai.aladdin` App Store (+ FC) | **2026-10-17** UUID `8b748ae9-…` |
| `PROVISIONING_PROFILE_ST_MONITOR` + `_UUID` | Monitor | 2026-10-16 |
| `PROVISIONING_PROFILE_ST_REPORT` + `_UUID` | Report | 2026-10-16 |
| `PROVISIONING_PROFILE_ST_SHIELD` + `_UUID` | Shield **Configuration** | 2026-10-16 |
| `PROVISIONING_PROFILE_ST_SHIELD_ACTION` + `_UUID` | Shield **Action** | **2026-10-17** |
| `PROVISIONING_PROFILE_NE_CONTENT_FILTER` + `_UUID` | Content Filter `ai.aladdin.ContentFilter` | **2026-10-17** |

CI decode: `scripts/decode_screen_time_profiles_ci.sh` (включая Shield Action).
Wiring в workflow: `.github/workflows/check-secrets.yml`.

### Как смотреть сборку (после push)

```bash
gh run list --repo sergey234/ALADDIN_FAMILY --workflow "Build and Upload to App Store" --limit 5
gh run view <RUN_ID> --repo sergey234/ALADDIN_FAMILY
# или UI: github.com/sergey234/ALADDIN_FAMILY/actions
```

Зелёный релиз = шаги **Archive + Export + Upload** все OK. Artifact IPA ≠ TestFlight.
Шаг Upload в Actions может быть зелёным при `altool UPLOAD FAILED` — читать лог `UPLOAD FAILED` / `VALIDATION_ERROR`, не только галочку job.

---

## 0b. Правильный push + сборка GitHub (копировать)

```text
1) cd …/ALADDIN_iOS
   git rev-parse --show-toplevel   → …/ALADDIN_iOS
   git branch --show-current       → master
   git remote -v                   → origin = git@github.com:sergey234/ALADDIN_FAMILY.git
2) ASC TestFlight: какой максимальный Build Ready на 1.0.1?
   → 2026-10-18: **11** успешно в ASC; после GO на bump текущий candidate = **12**
   → если максимальный Ready < текущего git Build / Upload failed → можно ship без bump
3) ./scripts/verify_capabilities_wave3_static.sh   → ALL OK
4) Ждать явный GO владельца:
     «GO на bump» / «GO на commit» / «GO на push»
     (можно одной фразой: «GO commit+push» · bump — только если сказали)
5) Staging checklist:
   git diff --cached --name-only | grep -E '^telegram_stars_shop_bot/|^\.env$' && echo STOP || echo OK
6) commit (если ещё не закоммичено) → «GO на push» →
   git push origin master
7) GitHub Actions → «Build and Upload to App Store» (check-secrets.yml)
8) Дождаться Upload OK → ASC TestFlight → 1.0.1 → Builds → Processing → Ready
```

| Не путать | Правда |
|-----------|--------|
| Зелёный Archive / artifact IPA | **≠** TestFlight |
| `UPLOAD FAILED` в `logs_*.zip` | В ASC **ничего нового** |
| Job «зелёный» с artifact после fail upload | Читать шаг Upload / `altool` |
| `git push` без GO | **запрещено** правилами репо |
| Локальный `xcodebuild` как «релиз» | только CI Upload = релиз TF |

Куда смотреть TF: App Store Connect → Apps → **ALADDIN AI** → **TestFlight** → iOS → version **1.0.1** → Builds.

---

## 0c. План–факт WAVE3 (вечер 2026-10-17) — просто

### Уже в TestFlight **1.0.1 / 10** (`3f59110c`)

| Тема | Факт |
|------|------|
| ExtensionKit DeviceActivityReport | ✅ в TF |
| Геозоны L1–L16 + honesty | ✅ код в TF · L4 API на MAIN ✅ · **walk-test ⏳** |
| Shield Action Ask Parent | ✅ в TF · CI UUID SPECIFIER |
| Content Filter | ✅ в TF · host `content-filter-provider` · **не** Packet Tunnel |
| HealthKit | ✅ entitlement + Share **и** Update purpose strings |
| Privacy ASC Location | ✅ Published (Tracking No) |
| Critical Alerts форма | ✅ Request **`VX53USXWCJ`** · ждём Assigned · флаг **false** |
| Comm Notifications | ✅ галочка на App ID · в билде |
| Review Notes ASC | ✅ 2.1 закрыт (прод) · What’s New build 12: `docs/AppStore/REVIEW_NOTES_CURRENT.md` |
| CI Shield / Filter | ✅ decode + UUID в pbx (`67790dff` + `3f59110c`) |

### Owner GO 2026-10-17 — в билде **10**

| Флаг / фича | Статус |
|-------------|--------|
| A1 `allowsSystemFamilyControls` | **true** (App Store path) |
| E1 Communication Notifications | **true** + presenter |
| F2/F4 Content Filter | **true** + CI + TF |
| G «Срочный сигнал семье» | motion + manual · HK on |
| Critical Alerts | **false** until `VX53USXWCJ` Assigned |

### Осталось после TF 10 (завтра)

1. Device QA 2 iPhone (ST + геозоны + фильтр + срочный сигнал).
2. Walk-test геозон · parent APNs (L4 уже на MAIN).
3. Critical Assigned → entitlement + regen APP + D2 / L11.
4. Notes: Guideline 2.1 уже закрыт (прод). Для сборки — короткий What’s New: `docs/AppStore/REVIEW_NOTES_CURRENT.md`.
5. След. бинарь после текущего candidate 12 — только **«GO на bump 13»**.

Registry: `.cursor/CAPABILITIES_WAVE3_TASK_REGISTRY.md`.

---

## 1. Два номера — вставлять сюда

### A) Build (номер сборки) — при GO: PREV → NEXT (после bump: 12 → 13)

Везде одно и то же число **NEXT_BUILD**:

| Файл | Поле | Пример сейчас → после bump |
|------|------|----------------------------|
| `Info.plist` | `CFBundleVersion` | `12` → `13` |
| `ALADDIN.xcodeproj/project.pbxproj` | **все** `CURRENT_PROJECT_VERSION = …;` | `12` → `13` |
| `Core/Config/AppConfig.swift` | `buildNumber` **и** `minimumClientBuildForApiContract` | `"12"` → `"13"` |
| `Tests/UnitTests/AppConfigTests.swift` | assert build | `12` → `13` |
| `ALADDINCallDirectory/Info.plist` | `CFBundleVersion` | `12` → `13` |
| `ALADDINDeviceActivityMonitor/Info.plist` | `CFBundleVersion` | `12` → `13` |
| `ALADDINDeviceActivityReport/Info.plist` | `CFBundleVersion` | `12` → `13` |
| `ALADDINShieldConfiguration/Info.plist` | `CFBundleVersion` | `12` → `13` |
| `ALADDINShieldAction/Info.plist` | `CFBundleVersion` | `12` → `13` |
| `ALADDINContentFilter/Info.plist` | `CFBundleVersion` | `12` → `13` |
| `ALADDINWidgets/Info.plist` | обычно `$(CURRENT_PROJECT_VERSION)` | ок, если pbx = 12 |
| **этот файл** | `PREV_BUILD` / `NEXT_BUILD` | PREV=12, NEXT=13 |

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
| CallDirectory / Widgets / Monitor / Report / Shield / ShieldAction / ContentFilter `Info.plist` | `CFBundleShortVersionString` |
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

### Урок подписи Content Filter / Shield Action (2026-10-17 вечер)

Xcode ищет `PROVISIONING_PROFILE_SPECIFIER` **по имени** из pbx.
`ALADDINContentFilter_PROVISIONING_PROFILE_SPECIFIER=UUID` в xcconfig **не** перекрывает имя
`ALADDIN AI ContentFilter App Store.` / `…ShieldAction App Store.`

Канон (как у основного приложения):

1. Release SPECIFIER в git для этих двух таргетов = `""` (не устаревшее имя).
2. Перед archive: `scripts/apply_appex_profile_uuids_to_pbx.py` пишет UUID из decode.
3. Fastfile + `check-secrets.yml` оба вызывают скрипт.
4. Профиль лежит как `~/Library/MobileDevice/Provisioning Profiles/<UUID>.mobileprovision`.

Коммит: `67790dff`.

### Урок Upload 409 после зелёного Archive (run 39039619395)

Подпись уже OK. Apple отверг IPA по трём пунктам (не duplicate 10):

| Ошибка | Канон |
|--------|--------|
| нет `NSHealthUpdateUsageDescription` | ключ в `Info.plist` + RU/EN `InfoPlist.strings` (даже если не пишем в Health) |
| `com.apple.ManagedSettingsUI.shield-action-service` invalid | только `com.apple.ManagedSettings.shield-action-service` |
| host без `networkextension` | в `ALADDIN.entitlements` массив **только** `content-filter-provider` · **не** `packet-tunnel` |

Коммит: `3f59110c`. Verify: `verify_capabilities_wave3_static.sh`.

---

## 4b. Следующая волна capabilities (build 11+)

**SSOT:** `docs/AppStore/CAPABILITIES_WAVE3_BUILD11_MASTER_PLAN_2026-10-17_RU.md`
**TODO:** `.cursor/CAPABILITIES_WAVE3_TASK_REGISTRY.md` · ids `cap-*`
**Утро / one-pager:** `docs/AppStore/WAVE3_TOMORROW_TASKS_2026-10-17_RU.md`
**OUT:** Packet Tunnel / in-app VPN · `UIBackgroundModes location`.

MUST после TF: Device QA 2 iPhone · walk-test геозон · Notes = короткий What’s New (2.1 уже закрыт).
Bump **11** — только «GO на bump». Critical ship-код — после Assigned `VX53USXWCJ`.

## 5. Family Controls / Screen Time (не ломать)

Apple **Distribution Assigned**. В CI **не снимать** entitlement.

| Секрет GitHub Actions | Содержимое |
|----------------------|------------|
| `PROVISIONING_PROFILE_APP` | App Store profile **с** `family-controls` (не старый без FC) · UUID после regen 2026-10-17: `8b748ae9-…` |
| `PROVISIONING_PROFILE_ST_MONITOR` + `_UUID` | DeviceActivityMonitor App Store |
| `PROVISIONING_PROFILE_ST_REPORT` + `_UUID` | DeviceActivityReport App Store |
| `PROVISIONING_PROFILE_ST_SHIELD` + `_UUID` | ShieldConfiguration App Store |
| `PROVISIONING_PROFILE_ST_SHIELD_ACTION` + `_UUID` | ShieldAction App Store · UUID `22b594dc-…` (2026-10-17) |

Decode в CI: `scripts/decode_screen_time_profiles_ci.sh` (Monitor/Report/Shield/**ShieldAction**).
Заливка с Mac: `gh secret set …` (§0a) или `scripts/set_github_st_fc_secrets.sh` (нужен `gh auth`).

В `Fastfile`: **нет** вызова `ci_strip_family_controls_entitlement.sh`.
Если ST UUID пустые — CI может skip embed ST (fallback); для прод-сборки со Screen Time секреты **должны** быть.

`AppStoreBuildPolicy.allowsSystemFamilyControls` → `true` только после Device QA + **GO** (не путать с entitlement в профиле).

Имена ST-профилей в pbx Release (Monitor/Report/Shield Config) — **с точкой в конце**, как у Apple
(напр. `ALADDIN AI DeviceActivityMonitor App Store.`).

**Content Filter + Shield Action:** имена в pbx **не** использовать — только UUID через `apply_appex_profile_uuids_to_pbx.py` (§4).

**Report = ExtensionKit** (см. §4 урок 409) — Monitor/Shield Config остаются обычными app-extension в PlugIns.
Shield Action identifier: `com.apple.ManagedSettings.shield-action-service` (без `UI`).

---

## 6. Перед commit — файлы в pbxproj реально в git

Урок CI: Archive падает, если файл в `project.pbxproj`, но не в git.

1. `git status` — нет забытых `??` релизных `.swift`
2. Новые Sources из pbx есть в `git ls-files`
3. Не тащить bot / `.env`

---

## 7. Рецепт «следующая сборка» (два сценария)

### 7A. Ship текущего пакета **без bump** (только если TF ещё **нет** Ready build 12)

```text
A. Код (Bypass+CF + bump 12) уже в локальных commits · verify ALL OK
B. L4 geofence-event на MAIN уже (walk-test отдельно)
C. Владелец сверил ASC: build 12 НЕ Ready
D. «GO на push» → git push origin master
E. CI check-secrets → Archive + Export + Upload все зелёные
F. TF 1.0.1 / build 12 → Ready
G. Если UPLOAD FAILED — logs_*.zip · шаг Upload (не путать с artifact)
```

### 7B. Сборка 13 (если build 12 уже Ready **или** сказали GO на bump)

```text
A. Владелец: «GO на bump» (+ потом commit/push)
B. В коде: Build 12 → 13 во всех файлах §1A (+ Shield Action plist если hardcoded)
C. В этом файле: PREV_BUILD=13  NEXT_BUILD=14
D. Marketing 1.0.1, ЕСЛИ train ASC ещё открыт
E. commit → «GO на push» → CI Upload зелёный
F. TestFlight: Version 1.0.1 · Build 13
```

### 7C. Наилучший путь «прямо сейчас» (рекомендация пилоту)

```text
1. ASC TestFlight → посмотреть Ready builds на 1.0.1
2. Если максимальный Ready = 11:
      → текущий candidate 12 уже готов к commit/push (этот рецепт)
3. Если Ready = 12:
      → новый «GO на bump» 12→13 → commit → «GO на push»
4. После Ready: Device QA 2 iPhone (ST + геозоны + Bypass + Content Filter)
5. Notes ASC — короткий What’s New; 2.1 не переотправлять
6. Critical/Comm ship-код — только после Apple Assigned
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
- Имена `ALADDIN AI ContentFilter/ShieldAction App Store.` в pbx (нужен UUID)
- `ManagedSettingsUI.shield-action-service`
- Host app без `content-filter-provider` при встроенном фильтре
- HealthKit entitlement без `NSHealthUpdateUsageDescription`
- Packet Tunnel / Personal VPN в entitlements
- Менять marketing без новой version в ASC
- Local Xcode Archive вместо CI upload как «релиз»

---

## 9. Актуальная пара (обновлять после каждого успешного bump)

```text
PREV_BUILD = 14
NEXT_BUILD = 15
CURRENT_MARKETING_VERSION = 1.0.1
```

После bump build N: `PREV_BUILD = N`, `NEXT_BUILD = N+1`.
После bump marketing: обновить `CURRENT_MARKETING_VERSION`.
