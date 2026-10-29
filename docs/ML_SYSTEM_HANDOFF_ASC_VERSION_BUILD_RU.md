# ML Handoff: ASC Version + Build (ai.aladdin Path B)

**Дата фиксации:** 2026-10-16 · **обновлён** 2026-10-23 (Build **15** · ITMS-90894 + HealthKit UI + OB_07)
**Приложение:** `ai.aladdin` / ALADDIN AI (команда **B3WGHSWL79**, org SAUDAPAYDI)
**Не путать** с личным TF `family.aladdin.ios` / team `6CJVBBUGSN` / номерами 247–248.

**Канон релиза (SSOT — читать первым):** `docs/RELEASE_BUILD_PROMPT.md`
→ §**0** факт · §**0a** secrets через `gh` · §**0b** push+CI · §**0c** план–факт · §**4** уроки 409/подпись
**Рабочий корень:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`
**Ветка:** только `master` · **Remote:** `git@github.com:sergey234/ALADDIN_FAMILY.git`
**CI:** `check-secrets.yml` · candidate **1.0.1 / 15** (после **GO на push** · Archive+Upload)

---

## 1. Два разных номера (обязательно понять)

| Имя | Что это | Ключи в коде | Сейчас (канон) | В App Store Connect |
|-----|---------|--------------|----------------|---------------------|
| **Version** (версия приложения) | Marketing / «поезд» ASC | `MARKETING_VERSION`, `CFBundleShortVersionString`, `AppConfig.appVersion` | **1.0.1** | iOS version **1.0.1** |
| **Build** (номер сборки) | Уникальный билд внутри version | `CFBundleVersion`, `CURRENT_PROJECT_VERSION`, `AppConfig.buildNumber` | **16** | Review был **14**/TF **15**; candidate upload **16** |

В Xcode должно читаться: **Version 1.0.1 · Build 15**.

- Следующее поднятие **Build** (15→16): только после нового **GO на bump** build.
- Поднимать **Version** (1.0.1→1.0.2): только если ASC закрыл train / после approve, и только после **GO** + создания новой version в ASC.
- **Нельзя** заливать новые Build на уже closed/approved marketing train (урок ниже).

---

## 2. Актуальная пара в каноне

Файл: `docs/RELEASE_BUILD_PROMPT.md`

```text
PREV_BUILD = 15
NEXT_BUILD = 16
CURRENT_MARKETING_VERSION = 1.0.1
```

После успешного bump **build**: `PREV_BUILD` = выпущенный, `NEXT_BUILD` = +1.
После bump **marketing**: обновить `CURRENT_MARKETING_VERSION`.

---

## 3. Куда менять Build (CFBundleVersion → например 16)

| Файл | Поле |
|------|------|
| `Info.plist` | `CFBundleVersion` |
| `ALADDIN.xcodeproj/project.pbxproj` | все `CURRENT_PROJECT_VERSION = …;` (сейчас ×20, единственное значение) |
| `Core/Config/AppConfig.swift` | `buildNumber` **и** `minimumClientBuildForApiContract` |
| `Tests/UnitTests/AppConfigTests.swift` | assert `buildNumber` |
| `ALADDINCallDirectory/Info.plist` | `CFBundleVersion` (hardcoded) |
| `ALADDINDeviceActivityMonitor/Info.plist` | `CFBundleVersion` |
| `ALADDINDeviceActivityReport/Info.plist` | `CFBundleVersion` |
| `ALADDINShieldConfiguration/Info.plist` | `CFBundleVersion` |
| `ALADDINShieldAction/Info.plist` | `CFBundleVersion` |
| `ALADDINContentFilter/Info.plist` | `CFBundleVersion` |
| `ALADDINWidgets/Info.plist` | обычно `$(CURRENT_PROJECT_VERSION)` — ок, если pbx обновлён |

Проверка:

```bash
/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' Info.plist
rg 'CURRENT_PROJECT_VERSION = ' ALADDIN.xcodeproj/project.pbxproj | sort | uniq -c
rg 'static let buildNumber|minimumClientBuildForApiContract' Core/Config/AppConfig.swift
```

Все значения Build должны совпадать. Остатка старого Build в этих файлах быть не должно.

---

## 4. Куда менять Version / marketing (→ например 1.0.2)

**Сначала в ASC:** Приложения → ALADDIN (`ai.aladdin`) → App Store → **«+»** у iOS → новая version (например `1.0.2`) → Создать.
Кнопка **«Добавить платформу»** — **не то**.

**Потом в git (только после GO):**

| Файл | Поле |
|------|------|
| `ALADDIN.xcodeproj/project.pbxproj` | все `MARKETING_VERSION = …;` |
| `Core/Config/AppConfig.swift` | `appVersion` |
| `Tests/UnitTests/AppConfigTests.swift` | assert `appVersion` |
| `ALADDINCallDirectory/Info.plist` | `CFBundleShortVersionString` |
| `ALADDINWidgets/Info.plist` | `CFBundleShortVersionString` |
| `ALADDINDeviceActivityMonitor/Info.plist` | `CFBundleShortVersionString` |
| `ALADDINDeviceActivityReport/Info.plist` | `CFBundleShortVersionString` |
| `ALADDINShieldConfiguration/Info.plist` | `CFBundleShortVersionString` |
| `ALADDINShieldAction/Info.plist` | `CFBundleShortVersionString` |
| `ALADDINContentFilter/Info.plist` | `CFBundleShortVersionString` |
| `Info.plist` | обычно `$(MARKETING_VERSION)` |

Проверка:

```bash
rg 'MARKETING_VERSION = ' ALADDIN.xcodeproj/project.pbxproj | sort | uniq -c
rg 'static let appVersion' Core/Config/AppConfig.swift
/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' ALADDINCallDirectory/Info.plist
```

---

## 5. Подтверждение: как должно быть для ASC 1.0.1 + Build 12

### Build = 12

| Файл | Значение |
|------|----------|
| `Info.plist` → `CFBundleVersion` | **12** |
| `project.pbxproj` → `CURRENT_PROJECT_VERSION` | **12** (единственное значение) |
| `AppConfig.buildNumber` | **12** |
| `AppConfig.minimumClientBuildForApiContract` | **12** |
| CallDirectory / ST/NE extensions `CFBundleVersion` | **12** |
| Widgets | `$(CURRENT_PROJECT_VERSION)` → 12 |
| `AppConfigTests` (build) | **12** |
| Team `DEVELOPMENT_TEAM` | **B3WGHSWL79** ×20 |
| Канон PREV/NEXT | PREV=**12** NEXT=**13** |

### Version = 1.0.1

| Файл | Значение |
|------|----------|
| `project.pbxproj` → `MARKETING_VERSION` | **1.0.1** ×20 |
| `AppConfig.appVersion` | **1.0.1** |
| `AppConfigTests` (appVersion) | **1.0.1** |
| CallDirectory / Widgets / ST×3 short | **1.0.1** |
| `Info.plist` short | `$(MARKETING_VERSION)` |
| Канон | `CURRENT_MARKETING_VERSION = 1.0.1` |
| ASC | iOS **1.0.1** Подготовка к отправке |

---

## 6. Урок: почему сборка 9 не появилась в TestFlight

**Лог CI:** GitHub Actions run (Build and Upload to App Store), artifact logs `logs_*.zip`.

| Шаг | Результат |
|-----|-----------|
| Archive | OK |
| Export IPA | OK → `ALADDIN.ipa` |
| Upload (`altool` / apple-actions) | **FAIL** |

Ошибки Apple (409):

1. `Invalid Pre-Release Train. The train version '1.0.0' is closed for new build submissions`
2. `CFBundleShortVersionString [1.0.0] must contain a higher version than that of the previously approved version [1.0.0]`

Следствия:

- Зелёный Archive / IPA artifact в GitHub **≠** билд в TestFlight.
- Нужен зелёный шаг **Upload to App Store Connect**.
- Job мог выглядеть «успешным» из‑за upload artifact после fail upload — всегда читать лог `altool` / `UPLOAD FAILED`.
- Исправление: ASC version **выше** closed train + тот же номер в `MARKETING_VERSION` / short version во всех targets.

---

## 7. CI / TestFlight — что смотреть

Workflow: `.github/workflows/check-secrets.yml`
UI name: **Build and Upload to App Store**
Триггер: `push` на `master` и `workflow_dispatch`.

Обязательные зелёные шаги:

1. Build Archive
2. Export IPA
3. **Upload to App Store Connect** (`apple-actions/upload-testflight-build`)

После upload: ASC → TestFlight → Processing (часто 10–60+ мин) → Ready to Test → группа тестеров.

ExportOptions: app + ContentBlocker + AntifakeShare + CallDirectory + Widgets + ST
`DeviceActivityMonitor` / `DeviceActivityReport` / `ShieldConfiguration` / **`ShieldAction`** / **`ContentFilter`**.

Content Filter + Shield Action: UUID в pbx SPECIFIER (`scripts/apply_appex_profile_uuids_to_pbx.py`), не имя профиля.
Host app: `content-filter-provider` only. Shield Action id: `com.apple.ManagedSettings.shield-action-service`.
HealthKit: и Share, и **Update** purpose string. Подробно: `RELEASE_BUILD_PROMPT.md` §4.

### Screen Time / Family Controls и CI (уроки #585–#588)

**#585/#586 FAIL → #587 cancelled → #588 честный FC (`6ddf112d`):**

1. Secret `PROVISIONING_PROFILE_APP` = профиль **с** `family-controls` (не без FC).
2. Secrets ST: `PROVISIONING_PROFILE_ST_{MONITOR,REPORT,SHIELD}` + `*_UUID`
   → `scripts/decode_screen_time_profiles_ci.sh` · заливка `scripts/set_github_st_fc_secrets.sh`.
3. В `Fastfile` **нет** strip FC — entitlement в Archive.
4. Полный рецепт push/bump/секреты: **`docs/RELEASE_BUILD_PROMPT.md` §0b, §3–§7**.
5. `allowsSystemFamilyControls` → true только после Device QA + GO.

### DeviceActivityReport ExtensionKit (урок `logs_105606115805`)

| Шаг | Результат |
|-----|-----------|
| Archive + Export | OK |
| Upload | **FAILED 409** |
| GitHub artifact IPA | OK ≠ TestFlight |

Причина: Report собран как **NSExtension** в `PlugIns/`. Нужен **ExtensionKit**:
`EXAppExtensionAttributes` · `productType = extensionkit-extension` · embed `Extensions/` (`dstSubfolderSpec = 16`).

Канон и антипаттерн «вернуть NSExtension»: **`docs/RELEASE_BUILD_PROMPT.md` §4 + §8**.
Verify: `./scripts/verify_capabilities_wave3_static.sh`.

Куда смотреть сборку после успешного Upload:
ASC → Apps → ALADDIN AI → **TestFlight** → iOS → **1.0.1** → Builds.

---

## 8. Порядок работы для следующей ML-системы

1. Прочитать этот handoff + `docs/RELEASE_BUILD_PROMPT.md` (§0 + §0b).
2. One-pager дня: `docs/AppStore/WAVE3_TOMORROW_TASKS_2026-10-17_RU.md`.
3. `git rev-parse --show-toplevel` · ветка `master` · remote канон.
4. Показать фактические Version + Build командами из §3–4.
5. **Не** менять номера / не push без явного GO.
6. Перед push: `verify_capabilities_wave3_static.sh` → ALL OK.
7. Зелёный релиз = Archive + Export + **Upload**.
8. Если Upload падает на closed train — ASC «+» version; 409 Report — ExtensionKit; 409 Filter/HK/Shield — §4 канона.
   Следующий бинарь после Ready **10** — только «GO на bump» → 11.
9. Не коммитить `telegram_stars_shop_bot/**`, `.env`, секреты.
10. Не путать Path A (247/личный team) с Path B.

---

## 9. История (кратко)

| Событие | Деталь |
|---------|--------|
| ASC approved / closed | marketing **1.0.0** (в UI часто «1.0»), билд **8** на странице дистрибуции |
| feat(build 9) | Build 9 в git; Upload FAIL (train 1.0.0 closed) |
| feat(build 10) + ST WAVE2 | `1773deeb` — Build 10, ещё marketing 1.0.0 |
| Владелец | ASC создал **1.0.1** Подготовка к отправке |
| GO 2026-10-16 | marketing **1.0.1**, Build **10**, commit + push |
| GO 2026-10-17 | `6ddf112d` честный FC → CI #588 Upload OK → TF **1.0.1/10** (старый бинарь) |
| Run `logs_105606115805` | Archive OK · Upload **FAIL 409** Report NSExtension |
| Вечер 2026-10-17 | `67790dff` UUID SPECIFIER · `3f59110c` HK/NE/Shield id · CI Archive+Export+Upload · владелец видит **10** WAVE3 в кабинете |

---

## 10. Антипаттерны

- Таблица «везде 5 / 247→248 / team 6CJ…» как инструкция для текущего приложения.
- Путать **Version** и **Build**.
- Повторно пушить тот же Build на closed marketing train.
- Считать зелёный Archive / IPA artifact = TestFlight.
- Bump build без согласованных extension plists.
- Коммит iOS-релиза не на `master`.
- Вернуть DeviceActivityReport на NSExtension / PlugIns.
