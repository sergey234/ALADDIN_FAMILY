# Build 232 — Release Summary (SSOT по antifake M2/M3)

**Build:** **232** · **Ветка:** `master` · **Remote:** `git@github.com:sergey234/ALADDIN_FAMILY.git`  
**Канонический путь:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
**Обновлено:** 2026-06-13

> **Главный документ по этой части работы.** Все трекеры ссылаются сюда; детали звонков — [`ANTIFAKE_CALLS_PRODUCT_SCOPE.md`](../ANTIFAKE_CALLS_PRODUCT_SCOPE.md).

---

## 1. Что вошло в build 232

### Ядро (commit `3cfcf256`)

| Область | Deliverable |
|---------|-------------|
| **M2 Calls** | Call Directory Extension, sync API, post-call observer + push |
| **M3 Semi-auto** | История 50 проверок, quick voice 5 с |
| **Hub UX** | `AntifakeQuickAccessCard` на экране Защиты, accordion ux-1-07 |
| **Wellness** | Placeholder/coachmark снов, contrast Values Form, reflective prompt |

### Supplemental (commit после `3cfcf256`)

| ID | Задача | Файлы |
|----|--------|-------|
| P0-2 / P0-1 | CI + Fastlane: 4-й extension Call Directory | `check-secrets.yml`, `Fastfile`, `decode_call_directory_profile_ci.sh` |
| P0-3 | af-8 честные тексты (18+, FAQ voices/phone) | `LocalizationManager.swift` |
| P1-5 | af-5-04 deepfakes Premium + server sync | `ProtectionSettingsManager.swift` |
| P1-6 | af-4-05 spoof heuristics | `antifake_service.py`, `test_antifake_call_spoof.py` |
| P1-7 | af-4-01 scope doc звонков | `docs/ANTIFAKE_CALLS_PRODUCT_SCOPE.md` |
| P1-8 | MARKETING_VERSION extension 1.0.0 | `ALADDINCallDirectory/Info.plist`, `project.pbxproj` |
| P1 | af-4-03 post-call banner + deep link | `NavigationManager`, `NotificationManager`, `AntifakeMediaCheckView`, `ALADDINApp` |

---

## 2. Build number 232 — где проверено

| Место | Значение |
|-------|----------|
| `Info.plist` (CFBundleVersion) | **232** |
| `ALADDINCallDirectory/Info.plist` (CFBundleVersion) | **232** |
| `project.pbxproj` (CURRENT_PROJECT_VERSION × 12 targets) | **232** × 12 |
| `Core/Config/AppConfig.swift` (`buildNumber`) | **232** |
| `Core/Config/AppConfig.swift` (`minimumClientBuildForApiContract`) | **232** |
| Simulator build artifact `ALADDIN.app` | **232** |
| Embedded `ALADDINCallDirectory.appex` | **232** |

**MARKETING_VERSION Call Directory:** `1.0.0` (согласовано с app semver).

---

## 3. xcodebuild (2026-06-13)

```
xcodebuild -scheme ALADDIN \
  -destination 'platform=iOS Simulator,name=iPhone 13 Pro Max,OS=18.4' \
  -configuration Debug build
→ BUILD SUCCEEDED
```

Валидация: `ALADDINCallDirectory.appex`, `ALADDINAntifakeShare.appex`, `ALADDINContentBlocker.appex` — embedded OK.

---

## 4. QA bypass (⏸ до TestFlight)

| Флаг | Файл | Prod значение |
|------|------|---------------|
| `bypassPremiumGate = true` | `AntifakeAccessPolicy.swift` | `false` |
| `ANTIFAKE_ALLOW_FREE=1` | `antifake_premium.py` / env | `0` |

**Не откатывали в этом коммите** — по согласованному плану (P0-4) перед релизом.

---

## 5. Связанные документы

| Документ | Роль |
|----------|------|
| **[`.cursor/BUILD_232_AGREED_TRACKER.md`](../../.cursor/BUILD_232_AGREED_TRACKER.md)** | Чеклист опросника (сделано / в конце) |
| **[`MASTER_STATUS_INDEX.md`](MASTER_STATUS_INDEX.md)** | Единый индекс всех треков |
| **[`ANTIFAKE_CALLS_PRODUCT_SCOPE.md`](../ANTIFAKE_CALLS_PRODUCT_SCOPE.md)** | Честные обещания по звонкам |
| **[`ANTIFAKE_APPLE_LIMITS_AND_CLAIMS.md`](../ANTIFAKE_APPLE_LIMITS_AND_CLAIMS.md)** | Apple limits + маркетинг |
| **[`.cursor/ANTIFAKE_PRODUCTION_TODO.md`](../../.cursor/ANTIFAKE_PRODUCTION_TODO.md)** | 72 задачи `af-*` |

---

## 6. Осталось до App Store

1. P0-4 — revert QA bypass (iOS + backend env)
2. Device QA — Call Directory в Настройки → Телефон → Блокировка и идентификация
3. R-07 — Archive + TestFlight (направление 143)

---

*При следующем bump build менять: `Info.plist`, `project.pbxproj` (12×), `AppConfig.swift` (2 поля), `ALADDINCallDirectory/Info.plist`.*
