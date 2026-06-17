# ALADDIN iOS — ML Handoff (Log Analysis + Companion Hero)

**Дата:** 2026-06-17  
**Корень:** `ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
**Ветка:** `master` · **Билд:** 239 → цель **240**  
**Прогресс:** **52 / 82** Cursor TODO выполнено (**30 осталось**)

---

## 1. Жёсткие правила (для любой ML-системы)

| # | Правило |
|---|---------|
| 1 | **Cursor TODO — SSOT статусов.** Обновлять только `merge: true`. **Никогда не удалять** id задач. |
| 2 | **Синхронизировать** `docs/LOG_ANALYSIS_MASTER_PLAN.md` после смены статусов (сводка + эпизоды). |
| 3 | **Нет `xcodebuild` / симулятора / TestFlight** до явного разрешения пользователя (`hero-1-03`, `hero-5-02`, `ep-final-simulator-build`). |
| 4 | **Нет git commit/push** без явного запроса. |
| 5 | Перед финальной сборкой закрыть **ПРЕДФИНАЛ Hero:** `hero-prebuild-01/02` (Rive Editor вручную). |
| 6 | Минимальный diff: не трогать несвязанный код, ML_SYSTEM_PACKAGE, CLEAN_EXPORT2. |
| 7 | Production policy: parental bypass — без mock/fallback (см. `.cursor/rules/prod-no-mock-bypass.mdc`). |

**Два SSOT-документа:**

- План и порядок: [`LOG_ANALYSIS_MASTER_PLAN.md`](LOG_ANALYSIS_MASTER_PLAN.md)
- Companion Hero детали: [`COMPANION_ML_HANDOFF_HERO_ANIMATION_AND_PERF.md`](COMPANION_ML_HANDOFF_HERO_ANIMATION_AND_PERF.md)

---

## 2. Сводка прогресса

| Трек | Всего | ✅ | ⬜ |
|------|-------|-----|-----|
| Companion Hero | 27 | 15 | 12 |
| Log Analysis Ep1–Ep6 | 55 | **37** | **18** |
| **Итого** | **82** | **52** | **30** |

---

## 3. Что уже сделано (кратко по блокам)

### Log Analysis — закрыто

| Блок | ID (примеры) | Суть |
|------|----------------|------|
| **P1** | `ep3-00`…`ep3-01`, `startup-08`, `startup-ssl-pinning`, `ep2-03`, `ep4-04`, `ep5-01`, Ep6 P1/P2 | Antifake input, family_id, trial tier, SSL schemes, Companion UI keys, roadside 404, AP re-init, AG cycles, chat/E2EE, DNS spam, nav dedupe, … |
| **P2 Startup** | `startup-03`…`06`, `startup-09` | Lifecycle checkpoints, lazy iCloud KVS, `NetworkManager.shared`, startup trace buffer, AdditionalFeatures summary log |
| **P2 Ep2** | `ep2-01`, `ep2-02`, `ep2-04`, `ep2-05`, `ep2-07`, `ep2-08` | `navigateToRoot(.main)`, `TokenValidator.hasUsableAPISession`, companion cache, `SFSymbolCompat.sliderHorizontal2Square`, `requestAuthorizationIfNeeded`, devices reconcile + empty UX |
| **P2 Ep3–Ep5** | `ep3-02`…`04`, `ep5-02`, `ep5-06`, `ep5-07` | Component cache, SF compat, antifake debounce, keychain/JWT/parental noise |

### Companion Hero — закрыто (фазы 0–4)

`hero-0-*`, `hero-1-01/02`, `hero-2-01/02`, `hero-3-01/02/03/05/06`, `hero-4-01/02/03` — perf, Rive triggers, клоны unicorn→aladdin/genie, PNG idle, verify scripts.

### Ключевые файлы последней сессии (Ep2)

| Файл | Изменение |
|------|-----------|
| `Core/Navigation/NavigationManager.swift` | `navigateToRoot` no-op; онбординг → root без дубля стека |
| `Core/Managers/TokenValidator.swift` | `hasUsableAPISession` |
| `ViewModels/MainViewModel.swift` | Ожидание SubscriptionManager; `reconcileDevicesProtectedCount` |
| `Core/Notifications/NotificationManager.swift` | `requestAuthorizationIfNeeded()` |
| `Screens/20_DevicesScreen.swift` | Empty state при members≥1 |
| `Core/Utilities/LogSanitizer.swift` | `SFSymbolCompat.sliderHorizontal2Square` |

---

## 4. Что осталось — приоритетный порядок

### 4.1 ПРЕДФИНАЛ Hero (P0, ручной Rive Editor)

| ID | Задача | Как сделать |
|----|--------|-------------|
| `hero-prebuild-01` | Export `unicorn_golden_amp.rev` → `unicorn.riv` | Rive Editor → Export Runtime → `Resources/Companion/unicorn.riv` → `scripts/verify_companion_rive_ios_bundle.sh` |
| `hero-prebuild-02` | Patch `aladdin.riv` + `genie.riv` | `scripts/companion_07_patch_riv_hero_image.py` из нового unicorn |
| `hero-prebuild-03` | Обновить `*_golden.rev` после export | После prebuild-01 |

> `unicorn_golden_amp.rev` может быть только у пользователя / в `backups/` — проверить glob.

### 4.2 Log Analysis — P2 (следующий блок)

| ID | Задача | Файлы | Как лучше |
|----|--------|-------|-----------|
| `ep3-05-localization-init` | Повторный `LocalizationManager.init` на Antifake Hub | `LocalizationManager.swift`, навигация | Уже есть warm/cache (`hero-1-01`); найти второй `LocalizationManager()` в Antifake path → заменить на `.shared` |
| `ep4-01-crash-simulator-ux` | Crash Detection на симуляторе | Crash views, component status | Не слать `component_error` как фатальный; показать «акселерометр недоступен» |
| `ep4-02-crash-test-location` | Test Crash без геолокации | Crash test UI | When In Use или понятный empty state |
| `ep4-03-toggle-debounce` | Дубль toggle Защита сети | `03_NetworkProtectionScreen.swift` | Debounce Binding 300–500 ms; guard рекурсии `blocked` |
| `ep5-04-redundant-api-calls` | Foreground burst API | `ContentBackgroundSyncScheduler`, SubscriptionManager | Throttle/coalesce status + parental + content/delta (как `ep5-07`) |
| `ep5-08-threat-aggregate-rerender` | setThreatAggregate каскад | `AdvancedProtectionSettingsScreen`, API | Batch `updateStatus` + debounce toggle (частично сделано в `ep5-01`) |
| `ep5-09-ios-settings-permissions-gap` | Camera/Contacts/Motion | Settings, first-use flows | Запрос при первом использовании или deep link |
| `ep6-09-location-permission-always` | Always vs WhenInUse | `LocationManager`, Family modals | UX upgrade path, не запрашивать Always сразу |

### 4.3 Log Analysis — P3

| ID | Задача | Примечание |
|----|--------|------------|
| `startup-07-boringssl` | boringssl metrics | Документировать как системный шум |
| `startup-10-offline-validator` | `validateSyncOfflineStorageResponse` | `APIResponseValidator.swift` |
| `ep2-06-companion-validators` | Validators для ComponentStatus, SecurityVerdict… | `APIResponseValidator.swift` |
| `ep2-09-metrics-broken-pipe` | metrics/upload broken pipe HTTP 200 | Retry/ignore в metrics client |
| `ep5-03-snapshotting-warning` | UIKeyboardImpl snapshotting | Dismiss keyboard до background |
| `ep6-10-metrics-connection-reset` | metrics -1005 | Retry queue |

### 4.4 Companion Hero — оставшееся

| ID | Фаза | Задача |
|----|------|--------|
| `hero-3-04` | 3 | Keyframes idle/speaking в runtime `.riv` (зависит от prebuild-01) |
| `hero-1-03`, `hero-1-04` | 1 | xcodebuild + smoke ScrollView (**только по разрешению**) |
| `hero-2-03` | 2 | Зафиксировать RIVE vs PNG на iPhone |
| `hero-5-01`…`04` | 5 | Bump 239→240, build, commit/push по запросу |
| `hero-6-01`…`04` | 6 | Device checklist Q1–Q8, MIMIC-Q, отчёт |

### 4.5 ФИНАЛ

| ID | Когда |
|----|-------|
| `ep-final-simulator-build` | После всех P1/P2 + hero-prebuild + hero-5-01 |

---

## 5. Рекомендуемый workflow для следующего агента

```
1. Прочитать этот файл + LOG_ANALYSIS_MASTER_PLAN.md (сводка).
2. Cursor TODO: merge:true — не удалять id.
3. Следующий код-блок: P2 Ep3/Ep4/Ep5 (таблица §4.2) ИЛИ hero-prebuild (ручной).
4. После каждого блока: обновить MASTER_PLAN + TODO.
5. verify_*.py и shell-verify — можно без сборки.
6. xcodebuild — только когда пользователь скажет «можно собирать».
```

---

## 6. Карта важных путей

| Область | Путь |
|---------|------|
| План | `docs/LOG_ANALYSIS_MASTER_PLAN.md` |
| Этот handoff | `docs/LOG_ANALYSIS_ML_HANDOFF.md` |
| Hero handoff | `docs/COMPANION_ML_HANDOFF_HERO_ANIMATION_AND_PERF.md` |
| TODO rule | `.cursor/rules/log-analysis-todo-ssot.mdc` |
| Navigation | `Core/Navigation/NavigationManager.swift` |
| Session | `Core/Managers/TokenValidator.swift` |
| Network singleton | `Core/Network/NetworkManager.swift` |
| Main dashboard | `ViewModels/MainViewModel.swift` |
| Companion Rive | `Resources/Companion/*.riv`, `UI/Companion/` |
| Verify | `scripts/verify_companion_rive_ios_bundle.sh` |

---

## 7. Незакоммиченные изменения

Все правки сессий 2026-06-17 (P1, P2 Startup, P2 Ep2, Ep3–Ep6) **могут быть не в git** — коммит только по запросу пользователя (`hero-5-03`).

---

## 8. Контакт с предыдущим контекстом

Transcript чата: `agent-transcripts/b294263f-ae62-4a6e-a8a4-cc5717e144b2.jsonl`  
Искать по id задачи (`ep6-11`, `hero-prebuild-01`, …) перед изменением поведения.
