# Handoff: CI signing для ALADDINAntifakeShare (build 227+)

**Дата:** 2026-06-11  
**Аудитория:** следующая ML/агентская система и человек-ревьюер.  
**Связанные документы:** `docs/CI_RELEASE_WORKFLOW.md`, `docs/HANDOFF_BUILD_187_GIT_AND_PUSH.md`  
**Workflow:** `.github/workflows/check-secrets.yml` (имя в UI: **Build and Upload to App Store**)

---

## 1. Краткое резюме

В **build 227** добавлен третий подписываемый target — **ALADDINAntifakeShare** (Share Extension для antifake). До этого CI подписывал только **ALADDIN** и **ALADDINContentBlocker** — для них профили давно лежат в GitHub Secrets, сборки проходили без ошибок.

После добавления AntifakeShare CI начал падать:

```text
No profile for team matching 'ALADDINAntifakeShare App Store Distribution'
(in target 'ALADDINAntifakeShare')
** ARCHIVE FAILED **
```

**Исправление в build 228** (`64a3baaf`): AntifakeShare переведён на **Automatic signing** в `project.pbxproj`, убран глобальный `CODE_SIGN_STYLE=Manual` в Fastlane, добавлен экспорт App Store Connect API для `-allowProvisioningUpdates`.

**Опционально (рекомендуется для стабильного CI):** секрет `PROVISIONING_PROFILE_ANTIFAKE_SHARE` — тогда AntifakeShare подписывается вручную, как App и ContentBlocker.

---

## 2. Канонический репозиторий и правила пуша

| Параметр | Значение |
|----------|----------|
| Путь на диске | `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS` |
| Remote | `git@github.com:sergey234/ALADDIN_FAMILY.git` |
| Ветка релиза | `master` |
| Workflow | `check-secrets.yml` |

**Перед работой (обязательно):**

```bash
git remote -v
git branch --show-current
git log --oneline -n 3
```

**Перед push (sanity-check):**

```bash
git fetch origin master
git merge-base HEAD origin/master   # должен вернуть hash; иначе СТОП
git push origin master
```

**Запрещено без явного разрешения пользователя:** rebase, force-push в `master`, смена `git config`, работа из копий проекта с другим `.git`.

---

## 3. Что такое provisioning profile и секрет PROVISIONING_PROFILE_ANTIFAKE_SHARE

**Provisioning profile** (`.mobileprovision`) — файл Apple, который разрешает подписать конкретный **bundle ID** сертификатом **Apple Distribution** с нужными **entitlements**.

Секрет **`PROVISIONING_PROFILE_ANTIFAKE_SHARE`** в GitHub Actions — **base64** App Store Distribution профиля для target AntifakeShare:

| Параметр | Значение |
|----------|----------|
| Target | `ALADDINAntifakeShare` |
| Bundle ID | `family.aladdin.ios.ALADDINAntifakeShare` |
| Entitlements | App Group `group.com.aladdin.family` |
| Тип | App Store Distribution (без `ProvisionedDevices`) |
| Файл entitlements | `ALADDINAntifakeShare/ALADDINAntifakeShare.entitlements` |

**Зачем:** при **manual signing** runner не имеет профилей «из воздуха» — только то, что декодировано из Secrets (как `PROVISIONING_PROFILE_APP` и `PROVISIONING_PROFILE_EXTENSION`).

**Если секрета нет:** CI использует **Automatic signing** + `-allowProvisioningUpdates` — Xcode создаёт/скачивает профиль через App Store Connect API.

---

## 4. Почему раньше ошибки не было

| Период | Подписываемые targets | Секреты в GitHub |
|--------|----------------------|------------------|
| До build 227 | ALADDIN, ALADDINContentBlocker | `PROVISIONING_PROFILE_APP`, `PROVISIONING_PROFILE_EXTENSION`, `IOS_DISTRIBUTION_CERTIFICATE` |
| Build 227+ | + ALADDINAntifakeShare | Antifake-секрета **не было** |

**Локально на Mac** Xcode часто подтягивает профили через Apple ID / Automatic signing — сборка проходит. **В CI** runner чистый: без секрета и без корректного Automatic path archive падает.

**Дополнительная причина первого падения (build 227):** в `project.pbxproj` Release для AntifakeShare стояли `CODE_SIGN_STYLE = Manual` и `PROVISIONING_PROFILE_SPECIFIER = "ALADDINAntifakeShare App Store Distribution"`, а глобальный `CODE_SIGN_STYLE=Manual` в Fastlane/xcodebuild перебивал попытки включить Automatic только для AntifakeShare.

---

## 5. Архитектура подписи в CI

```text
check-secrets.yml
    │
    ├─ Decode PROVISIONING_PROFILE_APP        → ALADDIN (manual)
    ├─ Decode PROVISIONING_PROFILE_EXTENSION  → ALADDINContentBlocker (manual)
    ├─ Decode PROVISIONING_PROFILE_ANTIFAKE_SHARE (optional)
    │       ├─ есть  → ALADDINAntifakeShare (manual)
    │       └─ нет   → ALADDINAntifakeShare (automatic + ASC API)
    │
    └─ fastlane ios build_archive
            └─ xcodebuild archive → export IPA → TestFlight upload
```

**Ключевые файлы:**

| Файл | Роль |
|------|------|
| `.github/workflows/check-secrets.yml` | Декод секретов, xcconfig, Fastlane, export, upload |
| `fastlane/Fastfile` | Lane `build_archive`: per-target signing, xcodebuild archive |
| `scripts/decode_antifake_share_profile_ci.sh` | Декод optional antifake profile → `ANTIFAKE_PROFILE_UUID` |
| `ALADDIN.xcodeproj/project.pbxproj` | Release AntifakeShare: `CODE_SIGN_STYLE = Automatic` (build 228+) |

**Существующие секреты (уже были до AntifakeShare):**

- `IOS_DISTRIBUTION_CERTIFICATE` + `IOS_DISTRIBUTION_CERTIFICATE_PASSWORD`
- `PROVISIONING_PROFILE_APP`
- `PROVISIONING_PROFILE_EXTENSION`
- `APPLE_TEAM_ID`
- `APP_STORE_CONNECT_API_KEY`, `APP_STORE_CONNECT_ISSUER_ID`, `APP_STORE_CONNECT_API_KEY_ID`

---

## 6. Хронология коммитов (master)

| Hash | Описание |
|------|----------|
| `96a2d0ec` | build 227 closeout — добавлен target ALADDINAntifakeShare, FAQ, OB_02, backend |
| `518834f0` | Первая попытка CI-fix: Fastfile, decode script, workflow hooks для AntifakeShare |
| `64a3baaf` | **build 228** — финальный CI-fix: Automatic в pbxproj, убран global Manual, ASC API env |

---

## 7. Что сделано в build 228 (`64a3baaf`)

1. **`ALADDIN.xcodeproj/project.pbxproj`**
   - Release `ALADDINAntifakeShare`: `CODE_SIGN_STYLE = Automatic`
   - Удалён `PROVISIONING_PROFILE_SPECIFIER = "ALADDINAntifakeShare App Store Distribution"`
   - `CURRENT_PROJECT_VERSION = 228` (все targets)

2. **`fastlane/Fastfile`**
   - Убран глобальный `CODE_SIGN_STYLE=Manual` из xcconfig и командной строки xcodebuild
   - Manual только для `ALADDIN` и `ALADDINContentBlocker` (с UUID профилей)
   - AntifakeShare: Automatic + `APP_STORE_CONNECT_API_*` для `-allowProvisioningUpdates`
   - Явная очистка `ALADDINAntifakeShare_PROVISIONING_PROFILE_SPECIFIER=` при automatic path

3. **`.github/workflows/check-secrets.yml`**
   - `RELEASE_CFBundleVersion=228`
   - Экспорт `APP_STORE_CONNECT_API_KEY_ID`, `ISSUER_ID`, `API_KEY_PATH` перед Fastlane
   - Убран global `CODE_SIGN_STYLE = Manual` в шаге xcconfig
   - `-allowProvisioningUpdates` при export IPA, если antifake-профиля нет

4. **Номер сборки 228** в `Info.plist`, `AppConfig.swift`, `AppConfigTests.swift`

---

## 8. Два пути для AntifakeShare

### Путь A — Automatic (текущий по умолчанию, секрет не нужен)

**Условия:**

- Секреты `APP_STORE_CONNECT_API_KEY`, `APP_STORE_CONNECT_ISSUER_ID`, `APP_STORE_CONNECT_API_KEY_ID` заданы
- Bundle ID `family.aladdin.ios.ALADDINAntifakeShare` зарегистрирован в Apple Developer
- App Group `group.com.aladdin.family` включён для этого App ID

**Плюсы:** не нужен новый секрет.  
**Минусы:** зависимость от ASC API; при проблемах с правами/API archive может упасть.

**В логе CI ожидается:**

```text
⚠️  PROVISIONING_PROFILE_ANTIFAKE_SHARE not set
    ALADDINAntifakeShare → Automatic signing (-allowProvisioningUpdates)
✅ App Store Connect API key configured for automatic AntifakeShare provisioning
```

### Путь B — Manual (рекомендуется для стабильности, как App + ContentBlocker)

Добавить секрет **`PROVISIONING_PROFILE_ANTIFAKE_SHARE`**.

**В логе CI ожидается:**

```text
✅ Antifake Share profile UUID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
ANTIFAKE_USE_AUTOMATIC_SIGNING=false
```

---

## 9. Пошагово: создать и добавить PROVISIONING_PROFILE_ANTIFAKE_SHARE

### 9.1 Apple Developer Portal

1. **Identifiers → App IDs** — создать (если нет):
   - Description: `ALADDIN Antifake Share`
   - Bundle ID: `family.aladdin.ios.ALADDINAntifakeShare`
   - Capability: **App Groups** → `group.com.aladdin.family`

2. **Profiles → + → App Store Connect** (Distribution):
   - App ID: `family.aladdin.ios.ALADDINAntifakeShare`
   - Certificate: тот же **Apple Distribution**, что используется для основного приложения
   - Имя (пример): `ALADDINAntifakeShare App Store Distribution`
   - Скачать `.mobileprovision`

### 9.2 Проверка профиля (Mac)

```bash
security cms -D -i ~/Downloads/ALADDINAntifakeShare.mobileprovision | plutil -p -
```

Проверить:

- `application-identifier` → `TEAMID.family.aladdin.ios.ALADDINAntifakeShare`
- App Group `group.com.aladdin.family` присутствует
- **Нет** ключа `ProvisionedDevices` (иначе это не App Store profile)

### 9.3 Base64 и GitHub Secret

```bash
base64 -i ALADDINAntifakeShare.mobileprovision | tr -d '\n' | pbcopy
```

GitHub → `sergey234/ALADDIN_FAMILY` → **Settings → Secrets and variables → Actions → New repository secret**:

- **Name:** `PROVISIONING_PROFILE_ANTIFAKE_SHARE`
- **Value:** base64 одной строкой (без переносов)

### 9.4 Перезапуск CI

Actions → **Build and Upload to App Store** → **Run workflow** на ветке `master`,  
или push любого коммита в `master`.

---

## 10. Если CI снова упадёт — чеклист

### 10.1 Скачать логи

Actions → failed run → job **Build and Upload to App Store Connect** → скачать log / artifact.

### 10.2 Быстрый grep

```bash
grep -E "error:|ARCHIVE FAILED|No profile|signing|EXPORT FAILED" build.log | head -40
```

### 10.3 Типичные ошибки

| Сообщение | Причина | Действие |
|-----------|---------|----------|
| `No profile for ... ALADDINAntifakeShare` | Нет профиля, Automatic не сработал | Путь B: добавить `PROVISIONING_PROFILE_ANTIFAKE_SHARE` или проверить ASC API |
| `Automatic signing failed` | Нет/битые ASC ключи | Проверить 3 секрета `APP_STORE_CONNECT_*` |
| `No profile for ... ALADDIN` / `ContentBlocker` | Проблема со старыми секретами | Проверить `PROVISIONING_PROFILE_APP`, `PROVISIONING_PROFILE_EXTENSION` |
| App Group not included | Профиль без App Group | Пересоздать профиль с `group.com.aladdin.family` |
| Export IPA failed | Archive OK, export нет профиля | При manual antifake — нужен секрет; иначе `-allowProvisioningUpdates` |
| Duplicate build / version conflict | Номер уже в ASC | Bump build (см. §11) |

### 10.4 Что смотреть в логе Fastlane

- `Antifake Share Profile UUID:` — manual path активен
- `PROVISIONING_PROFILE_ANTIFAKE_SHARE not set` — automatic fallback
- `App Store Connect API key configured` — automatic path с API

---

## 11. Bump номера сборки (при необходимости)

Менять **после всех исправлений**, перед commit + push:

| Файл | Поле / мест |
|------|-------------|
| `Info.plist` | `CFBundleVersion` — 1 место |
| `ALADDIN.xcodeproj/project.pbxproj` | `CURRENT_PROJECT_VERSION` — 8 мест (все targets) |
| `Core/Config/AppConfig.swift` | `buildNumber` + `minimumClientBuildForApiContract` |
| `Tests/UnitTests/AppConfigTests.swift` | assert на `buildNumber` |
| `.github/workflows/check-secrets.yml` | `RELEASE_CFBundleVersion` в шаге Workflow marker |

---

## 12. Что ещё не закрыто (вне CI signing)

- Archive / TestFlight на локальной Mac (R-07)
- PNG Hub screenshots на устройстве (`docs/release/gates/testflight-build228/` или актуальная папка)
- Backend antifake rate limits задеплоены на VPS (`149.154.65.180`) — отдельно от iOS CI

---

## 13. Быстрая справка для агента

**Вопрос:** почему CI сломался на build 227?  
**Ответ:** добавили третий extension без CI-профиля и с manual signing в pbxproj.

**Вопрос:** что делать в первую очередь?  
**Ответ:** убедиться, что на `master` есть `64a3baaf` или новее; перезапустить workflow; если падает — добавить `PROVISIONING_PROFILE_ANTIFAKE_SHARE` (§9).

**Вопрос:** обязателен ли секрет antifake?  
**Ответ:** нет, если работает Automatic + ASC API. Для production CI надёжнее — да, по аналогии с app/extension.

---

*Handoff v1.0 · build 228 · `64a3baaf` on `master`*
