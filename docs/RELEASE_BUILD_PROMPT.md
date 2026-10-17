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

**Что уже в Apple / GitHub (факт на 2026-10-17):**

| Слой | Факт |
|------|------|
| Commit tip **origin/master** | `6ddf112d` — FC profiles without strip |
| Код в git (номера) | Version **1.0.1** · Build **10** |
| CI канон | `check-secrets.yml` («Build and Upload to App Store») |
| Ранее: Upload 409 | Report как NSExtension → нужен **ExtensionKit** (урок §4) |
| Владелец: «последний успешный приём Apple» | часто помнят **build 8** — **сверить ASC TestFlight** (Ready), не гадать |
| Локально **ahead of origin** | WAVE3 + ExtensionKit + Shield Action CI + portal docs (**~11 commits**, tip `60e4a492`) — **ещё не в GitHub / не в TF** |

**Правило перед следующим Upload:**  
ASC → TestFlight → `ai.aladdin` → 1.0.1 → Builds:

- если **build 10 уже Ready** → следующий ship только после **«GO на bump»** → **11** (Apple не примет второй раз тот же CFBundleVersion);  
- если **10 нет / был UPLOAD FAILED** → можно один push **без bump** (остаёмся на 10) с ExtensionKit + WAVE3.

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
| `PROVISIONING_PROFILE_ST_SHIELD_ACTION` + `_UUID` | Shield **Action** | **2026-10-17** UUID `22b594dc-…` |

CI decode: `scripts/decode_screen_time_profiles_ci.sh` (включая Shield Action).  
Wiring в workflow: `.github/workflows/check-secrets.yml`.

### Как смотреть сборку (после push)

```bash
gh run list --repo sergey234/ALADDIN_FAMILY --workflow "Build and Upload to App Store" --limit 5
gh run view <RUN_ID> --repo sergey234/ALADDIN_FAMILY
# или UI: github.com/sergey234/ALADDIN_FAMILY/actions
```

Зелёный релиз = шаги **Archive + Export + Upload** все OK. Artifact IPA ≠ TestFlight.

---

## 0b. Правильный push + сборка GitHub (копировать)

```text
1) cd …/ALADDIN_iOS
   git rev-parse --show-toplevel   → …/ALADDIN_iOS
   git branch --show-current       → master
   git remote -v                   → origin = git@github.com:sergey234/ALADDIN_FAMILY.git
2) ASC TestFlight: какой максимальный Build Ready на 1.0.1?
   → если 10 уже Ready → нужен «GO на bump» до 11 ПЕРЕД push
   → если 10 нет / Upload failed → можно ship на 10 без bump
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

## 0c. План–факт WAVE3 (после build 8 → сейчас) — просто

### Уже в коде (локальный master, часть уже в commits)

| Тема | Факт |
|------|------|
| ExtensionKit DeviceActivityReport | ✅ код (фикс ASC 409) |
| Геозоны L1–L16 + honesty | ✅ код · L4 API на MAIN ✅ · walk-test ⏳ |
| Shield Action Ask Parent | ✅ target + UI · FC Assigned · profile + secrets ✅ |
| Privacy ASC Location | ✅ Published (Tracking No) |
| Critical Alerts форма | ✅ Request **`VX53USXWCJ`** · ждём Assigned |
| Comm Notifications | ✅ галочка на App ID |
| NE Content Filter | ✅ Network Extensions On · Personal VPN Off |
| Review Notes ASC | ⏸ отложено до Submit / сборки |
| D4 flags Critical/Comm/NE | ✅ `false` до Assigned |
| CI Shield Action decode | ✅ commit `60e4a492` · **push ⏳** |
| Main App Store profile | ✅ regenerated · secret APP обновлён |

### Ещё не в origin / не в TestFlight

Все commits после `6ddf112d` (ahead) — пока только локально.

### Owner GO 2026-10-17 — в билде **10** (код)

| Флаг / фича | Статус |
|-------------|--------|
| A1 `allowsSystemFamilyControls` | **true** (App Store path) |
| E1 Communication Notifications | **true** + presenter |
| F2 Content Filter | target `ALADDINContentFilter` · embed skip until profile |
| G «Срочный сигнал семье» | motion + manual + loc RU/EN · HK entitlement deferred for CI |
| Critical Alerts | **false** until `VX53USXWCJ` Assigned |

### Осталось после push 10

1. CI Upload зелёный → TF Ready **10**.  
2. Device QA 2 iPhone (ST + геозоны + срочный сигнал).  
3. Portal: App ID `ai.aladdin.ContentFilter` + profile (F4).  
4. Optional: HealthKit capability on App ID + regen APP profile → add HK entitlement.  
5. Critical Assigned → D1–D3 / L11.  
6. Notes ASC перед Submit.

Registry: `.cursor/CAPABILITIES_WAVE3_TASK_REGISTRY.md`.

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

### 7A. Ship текущего пакета **без bump** (только если TF ещё **нет** Ready build 10)

```text
A. Код WAVE3 уже в локальных commits (ahead of origin) · verify ALL OK
B. L4 geofence-event на MAIN уже (walk-test отдельно)
C. Владелец сверил ASC: build 10 НЕ Ready
D. «GO на push» → git push origin master
E. CI check-secrets → Archive + Export + Upload все зелёные
F. TF 1.0.1 / build 10 → Ready
G. Если UPLOAD FAILED — logs_*.zip · шаг Upload (не путать с artifact)
```

### 7B. Сборка 11 (если build 10 уже Ready **или** сказали GO на bump)

```text
A. Владелец: «GO на bump» (+ потом commit/push)
B. В коде: Build 10 → 11 во всех файлах §1A (+ Shield Action plist если hardcoded)
C. В этом файле: PREV_BUILD=11  NEXT_BUILD=12
D. Marketing 1.0.1, ЕСЛИ train ASC ещё открыт
E. commit → «GO на push» → CI Upload зелёный
F. TestFlight: Version 1.0.1 · Build 11
```

### 7C. Наилучший путь «прямо сейчас» (рекомендация пилоту)

```text
1. ASC TestFlight → посмотреть Ready builds на 1.0.1
2. Если максимальный Ready ≤ 8 или 10 отсутствует/Failed:
      → «GO на push» без bump (ship 10 с ExtensionKit+WAVE3+Shield Action)
3. Если Ready = 10:
      → «GO на bump» 10→11 → commit → «GO на push»
4. После Ready: Device QA 2 iPhone (ST + геозоны) → потом FC flag on
5. Notes ASC — перед Submit, не блокер TF
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
