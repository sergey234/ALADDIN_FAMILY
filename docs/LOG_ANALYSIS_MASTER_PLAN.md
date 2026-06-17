# ALADDIN iOS — общий мастер-план (Companion Hero + Log Analysis Ep1–Ep6)

**Проект:** ALADDIN (Swift/SwiftUI)  
**Корень:** `ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
**Ветка:** `master` · **Билд сейчас:** 239 · **Цель:** 240  
**Дата обновления:** 2026-06-17  
**SSOT Cursor TODO:** все id ниже — **не удалять**, только `merge` и смена статуса

---

## Правила работы (общие)

| Правило | Описание |
|---------|----------|
| **Cursor TODO** | Все задачи остаются в панели Cursor; выполненные → `completed`; **ничего не удалять** |
| **Companion Hero** | Фазы 0→6 **строго по порядку**; PASS критерии перед следующей фазой |
| **Сборка и симулятор** | **Только в самом конце.** Перед ней — закрыть блок **ПРЕДФИНАЛ** (`hero-prebuild-*`, открытые P1) |
| **Коммит/push** | Только по явному запросу пользователя |

---

## Сводка прогресса (всего)

| Трек | Всего | ✅ | ⬜ |
|------|-------|-----|-----|
| **Companion Hero** (ML handoff, build 240) | 27 | 15 | 12 |
| **Log Analysis** Ep1–Ep6 (+ `ep3-00`, `ep-final`) | 55 | 37 | 18 |
| **Итого Cursor TODO** | **82** | **52** | **30** |

> **Синхронизация:** Cursor TODO — SSOT статусов; обновлено 2026-06-17. Blocks P1, P2 Startup, P2 Ep2 закрыты. **ML handoff:** [`docs/LOG_ANALYSIS_ML_HANDOFF.md`](LOG_ANALYSIS_ML_HANDOFF.md)

**Handoff SSOT:** [`docs/COMPANION_ML_HANDOFF_HERO_ANIMATION_AND_PERF.md`](COMPANION_ML_HANDOFF_HERO_ANIMATION_AND_PERF.md)

---

# ЧАСТЬ A — Companion Hero: анимация + perf + билд 240

**Задача:** на реальном iPhone (iOS 16+, не iOS 15 sim) единорог, Аладдин и Джин на «Мир героев» **заметно** двигаются; приложение не тормозит и не падает watchdog'ом (`0x8BADF00D`).

## Фазы (строго по порядку)

| Фаза | Что делать | Критерий PASS |
|------|------------|---------------|
| **0** | Подготовка | git pull, бэкап `.riv`, прочитать код |
| **1** | Perf (P0) | Кэш `LocalizationManager` + Rive trigger не каждый кадр; ScrollView не зависает 5+ сек |
| **2** | Диагностика | Бейдж RIVE/PNG + лог `[CompanionHero]`; на iPhone `path=RIVE vm=ok` |
| **3** | Ассеты (P0) | Клон `unicorn.riv` → aladdin + genie с Face и 13 triggers; verify PASS × 3 |
| **4** | iOS polish | Усилить idle-bob PNG fallback, idle loop в Rive; движение видно без AI |
| **5** | Релиз | Bump 239→240, build, verify scripts; `xcodebuild` PASS |
| **6** | QA device | Чеклист Q1–Q8 + MIMIC-Q; протокол + скрины |

## ФАЗА 0 — Подготовка

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| `hero-0-01` | `git pull`, cwd = `mobile_apps/ALADDIN_iOS` | — | ⬜ |
| `hero-0-02` | Бэкап `Resources/Companion/*.riv` → `backups/YYYY-MM-DD/` | `Resources/Companion/` | ⬜ |
| `hero-0-03` | Прочитать `CompanionHeroAvatarView` + `CompanionHeroRiveHost` | `UI/Companion/` | ⬜ |

## ФАЗА 1 — Perf / crashes (P0)

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| `hero-1-01` | `LocalizationManager`: кэш `.strings` + `warmBundleTablesAtLaunch()` | `Core/Localization/LocalizationManager.swift` | ⬜ |
| `hero-1-02` | Rive: trigger только `onAppear` + `onChange(emotion)`; mouth quantized 16 шагов; 20fps | `UI/Companion/CompanionHeroRiveHost.swift` | ⬜ |
| `hero-1-03` | `xcodebuild` PASS | `ALADDIN.xcodeproj` | ⬜ |
| `hero-1-04` | Smoke: ScrollView (Настройки, Мир героев) не зависает 5+ сек | — | ⬜ |

## ФАЗА 2 — Диагностика RIVE vs PNG

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| `hero-2-01` | DEBUG бейдж RIVE/PNG на device | `CompanionHeroRiveHost.swift`, `CompanionHeroRasterView.swift` | ⬜ |
| `hero-2-02` | Release `os_log` `[CompanionHero] path=RIVE\|PNG character=… vm=ok\|nil` | `CompanionHeroRiveHost.swift` | ⬜ |
| `hero-2-03` | Зафиксировать в отчёте: RIVE или PNG на iPhone пользователя | — | ⬜ |

## ФАЗА 3 — Rive ассеты (P0)

| ID | Задача | Скрипт / файл | Статус |
|----|--------|---------------|--------|
| `hero-3-01` | `verify unicorn` PASS + `Face=True` | `companion_07_verify_unicorn_riv.py unicorn` | ⬜ |
| `hero-3-02` | Клон unicorn → `aladdin.riv` (Face + 13 triggers + `aladdin_master.png`) | Rive Editor / MCP | ⬜ |
| `hero-3-03` | Клон unicorn → `genie.riv` (Face + 13 triggers + `genie_master.png`) | Rive Editor / MCP | ⬜ |
| `hero-3-04` | Усилить keyframes idle/speaking (амплитуда ≥8–12px) | `unicorn_golden_amp.rev` (editor) | 🟡 частично* |
| `hero-3-05` | `verify aladdin` + `verify genie` PASS | `companion_07_verify_unicorn_riv.py` | ⬜ |
| `hero-3-06` | Заморозить `aladdin_golden.rev`, `genie_golden.rev` | `Resources/Companion/` | ⬜ |

## ФАЗА 4 — iOS polish (P1)

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| `hero-4-01` | Усилить idle bob на PNG fallback (6–10pt + breathing scale) | `CompanionHeroRasterView.swift` | ⬜ |
| `hero-4-02` | idle loop `onAppear` в Rive (`applyRiveEmotionTrigger(.idle)`) | `CompanionHeroRiveHost.swift` | ⬜ |
| `hero-4-03` | `verify_companion_rive_ios_bundle.sh` PASS | `scripts/` | ⬜ |

\* `hero-3-04`: keyframes в **editor `.rev`** готовы (`unicorn_golden_amp.rev`); **runtime `.riv` в бандле ещё без них** → блок **ПРЕДФИНАЛ** ниже.

---

## ⚠️ ПРЕДФИНАЛ — важно, не сделано (перед сборкой / билд 240)

> **Правило:** эти задачи закрываем **до** `hero-5-02`, `hero-1-03`, `ep-final-simulator-build`.  
> Сейчас в бандле Face из unicorn SM + усиленный PNG fallback (`hero-4-01`); усиленные **timeline keyframes** попадут в приложение только после runtime export.

| ID | Приоритет | Задача | Как сделать | Статус |
|----|-----------|--------|-------------|--------|
| `hero-prebuild-01` | **P0** | Export Runtime: `unicorn_golden_amp.rev` → `unicorn.riv` | 1. Открыть `Resources/Companion/unicorn_golden_amp.rev` в **Rive Editor** (`/Applications/Rive.app`) · 2. File → Export → **Runtime** → перезаписать `Resources/Companion/unicorn.riv` · 3. `python3 scripts/companion_07_verify_unicorn_riv.py unicorn` + `Face=True` | ⬜ **важно** |
| `hero-prebuild-02` | **P0** | Пересобрать `aladdin.riv` + `genie.riv` из нового unicorn | `python3 scripts/companion_07_patch_riv_hero_image.py aladdin` · `python3 scripts/companion_07_patch_riv_hero_image.py genie` · verify ×2 · `./scripts/verify_companion_rive_ios_bundle.sh` | ⬜ **важно** |
| `hero-prebuild-03` | P1 | Заморозить golden после export | `cp unicorn.riv → unicorn_golden.rev` (при необходимости обновить `aladdin_golden.rev` / `genie_golden.rev`) | ⬜ |
| `hero-2-03` | P1 | Зафиксировать в отчёте: RIVE или PNG на iPhone | Console.app фильтр `CompanionHero` | ⬜ |

**Почему MCP не хватило:** RiveMCP пишет только `.rev`; cross-format `.rev → .riv` не поддерживается — нужен Rive Editor.

**Verify editor keyframes (уже есть):**
```bash
python3 scripts/companion_07_verify_riv_face_keyframes.py unicorn_golden_amp.rev
```

---

## ФАЗА 5 — Релиз билд 240

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| `hero-5-01` | Bump 239→240 (`AppConfig`, `Info.plist`, `pbxproj`) | `Core/Config/AppConfig.swift` | ⬜ |
| `hero-5-02` | Полный build + все verify scripts | `scripts/` | ⬜ |
| `hero-5-03` | Коммит — **только по запросу пользователя** | — | ⬜ |
| `hero-5-04` | TestFlight / push — **только по запросу пользователя** | — | ⬜ |

## ФАЗА 6 — Device QA (финал)

| ID | Задача | Документ | Статус |
|----|--------|----------|--------|
| `hero-6-01` | Заполнить `COMPANION_08B_DEVICE_CHECKLIST` | `docs/COMPANION_08B_DEVICE_CHECKLIST.md` | ⬜ |
| `hero-6-02` | Q1–Q8 PASS на iPhone iOS 16+ | handoff §6 | ⬜ |
| `hero-6-03` | MIMIC-Q: 8/13 эмоций различимы × 3 героя | handoff §6 | ⬜ |
| `hero-6-04` | Отчёт пользователю: что было / сделано / скрины | шаблон handoff §11 | ⬜ |

### QA чеклист Q1–Q8 (кратко)

| # | Шаг | Ожидание |
|---|-----|----------|
| Q1 | Мир героев → Единорог | Лог/бейдж `RIVE` |
| Q2 | 10 сек без чата | Заметное движение лица/idle loop |
| Q3 | «Привет!» (AI онлайн) | thinking → speaking → happy, рот |
| Q4 | Аладдин, Джин | Face-анимация у каждого |
| Q5 | Скролл чата, вкладки | Нет фриза 5+ сек, нет краша |
| Q6 | MIMIC-Q | ≥8/13 эмоций на unicorn |
| Q7 | Hub 96pt thumbnail | Круглая сцена, мимика видна |
| Q8 | TTS / mouth_open | Рот ≥1 сек при speaking |

### Ключевые файлы Companion

| Область | Путь |
|---------|------|
| Rive ассеты | `Resources/Companion/*.riv`, `*_master.png` |
| Avatar routing | `UI/Companion/CompanionHeroAvatarView.swift` |
| Rive host | `UI/Companion/CompanionHeroRiveHost.swift` |
| PNG fallback | `UI/Companion/CompanionHeroRasterView.swift` |
| Локализация (perf) | `Core/Localization/LocalizationManager.swift` |
| Verify | `scripts/companion_07_verify_unicorn_riv.py`, `verify_companion_rive_ios_bundle.sh` |

### Что НЕ делать

- Grok-3D / SceneKit / USDZ
- QA Rive только на iOS 15.2 Simulator
- Перезаписывать `unicorn.riv` без verify
- Коммитить `.env`, API-ключи

### Рекомендуемый порядок Companion

```
hero-0-* → … → hero-4-* → [открытые ep P1/P2] → hero-prebuild-01 → hero-prebuild-02 → hero-prebuild-03
→ hero-5-01 → hero-5-02 (сборка) → hero-6-* → ep-final-simulator-build
```

---

# ЧАСТЬ B — Log Analysis: эпизоды 1–6 (SETTINGS_DIAG)

**Источник:** Xcode / SETTINGS_DIAG логи, эпизоды 1–6
## Сводка прогресса (Log Analysis)

| Приоритет | Всего | ✅ Выполнено | ⬜ Осталось |
|-----------|-------|-------------|------------|
| P1 (критично) | 10 | 1 | 9 |
| P2 (важно) | 30 | 1* | 29 |
| P3 (качество/шум) | 6 | 0 | 6 |
| Финал | 1 | 0 | 1 |
| **Итого Log Analysis** | **47** | **2** | **45** |

\* `ep3-03-sf-symbol-phone` — частично; символ всё ещё в логах Ep6 → открыт `ep6-15-phone-badge-still-broken`

---

## ✅ Выполнено — Log Analysis (2)

| ID | Задача | Эпизод | Примечание |
|----|--------|--------|------------|
| `ep3-00-antifake-input` | Antifake Hub: вставка ссылок/текста/контакта (paste, URL auto-route, режим Контакт) | Ep3 | Код в `AntifakeHubScreen`, `AntifakeTextCheckViewModel` |
| `ep3-03-sf-symbol-phone` | `phone.badge.checkmark` → `SFSymbolCompat` | Ep3 | Частично; см. `ep6-15` |
| `startup-08-parental-trial` | trial tier → `TariffType.featureAccessTier` в ParentalControl + AdditionalFeature | Startup | `ParentalControlFeature.swift`, `AdditionalFeature.swift` |
| `startup-ssl-pinning` | Отдельная схема `ALADDIN-NoSSLPinning`; основная без `DISABLE_SSL_PINNING` | Startup | `ALADDIN.xcscheme`, `ALADDIN-NoSSLPinning.xcscheme` |
| `ep2-03-companion-ui-keys` | CompanionFeatureUI: 5 server keys (`provider`, `tts_provider`, `chat_modes`, `hero_visual_tier`, `audio_retention_seconds`) | Ep2 | `CompanionModels.swift`, `CompanionCapabilitiesService.swift` |
| `ep5-01-ap-reinit-optimization` | AdvancedProtection: без ObservedObject ComponentStatusService, threat snapshot, init log once | Ep5 | `AdvancedProtectionSettingsScreen.swift` |
| `ep4-04-roadside-history-404` | Roadside history 404 → empty state, UserDefaults skip repeat GET | Ep4 | `RoadsideAssistanceView.swift` |
| `startup-03-lifecycle` | Graceful shutdown: checkpoint на background/willResignActive/willTerminate | Startup | `ALADDINApp.swift` |
| `startup-04-icloud-kvs` | MnemonicSRSStore: ленивый `NSUbiquitousKeyValueStore` только при opt-in | Startup | `MnemonicSRSStore.swift` |
| `startup-05-network-singleton` | `NetworkManager.shared`; ParentalControl → `APIService.shared` | Startup | `NetworkManager.swift`, `ParentalControlManager.swift` |
| `startup-06-log-serialize` | `LaunchDiagnostics`: буфер startup → один atomic flush | Startup | `VisualLogger.swift` |
| `startup-09-additional-noise` | AdditionalFeaturesManager: один summary-лог вместо N× | Startup | `AdditionalFeaturesManager.swift` |
| `ep2-01-onboarding-nav` | `navigateToRoot(.main)` после онбординга; no-op на дубле | Ep2 | `NavigationManager.swift`, `14_OnboardingScreen.swift` |
| `ep2-02-demo-label` | `TokenValidator.hasUsableAPISession` — не «демо» при JWT | Ep2 | `TokenValidator.swift`, ViewModels |
| `ep2-05-sf-symbol` | `slider.horizontal.2.square` → `SFSymbolCompat` | Ep2 | `CompanionConversationScreen.swift` |
| `ep2-07-notifications-dup` | `requestAuthorizationIfNeeded` | Ep2 | `NotificationManager.swift` |
| `ep2-08-devices-empty` | `reconcileDevicesProtectedCount` + empty copy | Ep2 | `MainViewModel.swift`, `20_DevicesScreen.swift` |

---

## 🔴 P1 — Критично (блокеры / данные / FPS)

| ID | Задача | Эпизод | Файлы / зона | Статус |
|----|--------|--------|--------------|--------|
| `ep3-01-family-id-delete` | Убрать `KeychainManager.delete(family_id)` после GET `/family/members` | Ep3–6 | `FamilyLocalStore.persistFamilyId`, `APIService.applyFamilyMembersListHeaders` | ⬜ |
| `ep6-01-attribute-graph-cycles` | AttributeGraph cycle: Family Chat send + AI Assistant speech (100+ warnings) | Ep6 | Chat / AI views | ⬜ |
| `ep6-02-location-data-decoding` | `/api/location-bubble/requests`: wrapper `{requests,total}`, не `Array<LocationRequest>` | Ep6 | Location API models | ⬜ |
| `ep6-11-dns-manager-spam` | DNS Manager: `Status loaded` ×200+ на Parental Control → FPS 8–9; кэш, не в body | Ep6 | Parental Control / DNS Manager | ⬜ |

---

## 🟡 P2 — Важно (UX, сеть, навигация)

| ID | Задача | Эпизод | Статус |
|----|--------|--------|--------|
| `startup-03-lifecycle` | Graceful shutdown (`scenePhase`) | Startup | ✅ |
| `startup-04-icloud-kvs` | iCloud KVS ленивая инициализация `MnemonicSRSStore` | Startup | ✅ |
| `startup-05-network-singleton` | Убрать второй `NetworkManager` | Startup | ✅ |
| `startup-06-log-serialize` | Сериализовать startup-логи `LaunchDiagnostics` | Startup | ✅ |
| `startup-09-additional-noise` | `AdditionalFeaturesManager` — summary вместо 9× логов | Startup | ✅ |
| `ep2-01-onboarding-nav` | Убрать дубль навигации Главная→Главная | Ep2 | ✅ |
| `ep2-02-demo-label` | «Демо режим» при валидном JWT | Ep2 | ✅ |
| `ep2-04-companion-cache` | Кэш/debounce Companion API | Ep2 | ✅ |
| `ep2-05-sf-symbol` | SF Symbol `slider.horizontal.2.square` | Ep2 | ✅ |
| `ep2-07-notifications-dup` | Дубль notification auth на Settings | Ep2 | ✅ |
| `ep2-08-devices-empty` | UX 0 devices при members=1 | Ep2 | ✅ |
| `ep3-02-component-status-burst` | Кэш component status/configuration на Защита сети | Ep3 | ⬜ |
| `ep3-04-antifake-double-submit` | Debounce повторного POST `antifake/check/text` | Ep3 | ⬜ |
| `ep3-05-localization-init` | Повторный `LocalizationManager.init` при Antifake Hub | Ep3 | ⬜ |
| `ep4-01-crash-simulator-ux` | Crash Detection на симуляторе — не фатальный `component_error` | Ep4 | ⬜ |
| `ep4-02-crash-test-location` | Test Crash Detection — UX при отсутствии геолокации | Ep4 | ⬜ |
| `ep4-03-toggle-debounce` | Дубль toggle на Защита сети + debounce Binding | Ep4 | ⬜ |
| `ep5-02-keychain-user-prefs-noise` | `user_preferences` Keychain -25300 — не ERROR | Ep5 | ⬜ |
| `ep5-04-redundant-api-calls` | Кэш refresh на foreground — не дублировать API burst | Ep5 | ⬜ |
| `ep5-06-jwt-log-spam` | Спам «JWT действителен» — кэш/тихий режим | Ep5 | ⬜ |
| `ep5-07-parental-config-double-post` | `parental_control_bot` двойной/тройной POST; debounce | Ep5 | ⬜ |
| `ep5-08-threat-aggregate-rerender` | `setThreatAggregate` каскад + debounce UI | Ep5 | ⬜ |
| `ep5-09-ios-settings-permissions-gap` | iOS Settings: Camera/Contacts/Motion — запрос при использовании | Ep5 | ⬜ |
| `ep6-03-e2ee-keychain-errors` | E2EE Keychain -25300 — debug, не error | Ep6 | ⬜ |
| `ep6-04-chat-e2ee-keys-burst` | GET `e2ee/keys` ×3–4 — кэш/debounce | Ep6 | ⬜ |
| `ep6-05-chat-send-typing-burst` | POST `send/typing` ×7 — debounce 300–500ms | Ep6 | ⬜ |
| `ep6-06-ai-assistant-slow-response` | AI chat 24s — loading + timeout UX | Ep6 | ⬜ |
| `ep6-07-parental-sf-symbol` | `bubble.left.and.exclamationmark` → `SFSymbolCompat` | Ep6 | ⬜ |
| `ep6-08-publishing-from-background` | Network callbacks → main thread для `@Published` | Ep6 | ⬜ |
| `ep6-09-location-permission-always` | `LocationManager` Always vs WhenInUse — UX upgrade | Ep6 | ⬜ |
| `ep6-12-family-screen-empty-race` | FamilyScreen «Список пуст» при 1 member в UserDefaults | Ep6 | ⬜ |
| `ep6-13-nav-antifake-stack-dup` | Navigation stack `antifakeHub×4` | Ep6 | ⬜ |
| `ep6-14-family-location-kcleerror` | FamilyLocationModal `kCLError 0` — UX | Ep6 | ⬜ |
| `ep6-15-phone-badge-still-broken` | `phone.badge.checkmark` всё ещё в логах FamilyScreen | Ep6 | ⬜ |

---

## 🟢 P3 — Качество / шум / валидаторы

| ID | Задача | Эпизод | Статус |
|----|--------|--------|--------|
| `startup-07-boringssl` | boringssl metrics — системный шум | Startup | ⬜ |
| `startup-10-offline-validator` | `validateSyncOfflineStorageResponse` | Startup | ⬜ |
| `ep2-06-companion-validators` | `APIResponseValidator`: ComponentStatus, BypassStats, … | Ep2–3 | ⬜ |
| `ep2-09-metrics-broken-pipe` | Broken pipe `metrics/upload` при HTTP 200 | Ep2 | ⬜ |
| `ep5-03-snapshotting-warning` | Snapshotting `UIKeyboardImpl` — dismiss keyboard | Ep5 | ⬜ |
| `ep6-10-metrics-connection-reset` | `metrics/upload` -1005 — retry queue | Ep6 | ⬜ |

---

## 🏁 Финал

| ID | Задача | Статус |
|----|--------|--------|
| `ep-final-simulator-build` | Сборка и прогон на симуляторе после всех фиксов P1/P2 | ⬜ |

---

## По эпизодам — что выявили

### Ep1–2 (Startup, онбординг, Companion)
- JWT OK, навигация в целом OK
- ✅ trial tier ParentalControl (`startup-08`)
- ✅ SSL pinning схемы (`startup-ssl-pinning`)
- ✅ Companion UI keys (`ep2-03`)
- ✅ lifecycle checkpoints (`startup-03`)
- ✅ iCloud KVS lazy (`startup-04`)
- ✅ NetworkManager singleton (`startup-05`)
- ✅ startup trace buffer (`startup-06`)
- ✅ AdditionalFeatures summary log (`startup-09`)
- ✅ onboarding `navigateToRoot` (`ep2-01`)
- ✅ session vs demo label (`ep2-02`)
- ✅ devices empty UX (`ep2-08`)
- demo label, дубль nav — **закрыто**
- metrics broken pipe, validators
- lifecycle, NetworkManager singleton, startup log noise

### Ep3 (Antifake, Защита сети, family_id)
- ✅ Antifake paste/URL/contact (`ep3-00`)
- ✅ `family_id` mirror, не delete (`ep3-01`)
- ✅ Component status/configuration cache (`ep3-02`)
- ✅ `phone.badge.checkmark` / SF compat (`ep3-03`, `ep6-15`)
- ✅ Antifake double submit debounce (`ep3-04`)
- ⬜ LocalizationManager re-init — `ep3-05`

### Ep4 (Crash Detection / Roadside)
- Simulator accelerometer UX — `ep4-01`
- Location for test crash — `ep4-02`
- Toggle debounce на Защита сети — `ep4-03`
- ✅ Roadside history 404 → empty state + skip repeat API (`ep4-04`)

### Ep5 (Advanced Protection, foreground refresh)
- ✅ AP view re-init: без `@ObservedObject` ComponentStatusService, threat snapshot, init log once (`ep5-01`)
- ✅ JWT spam throttle (`ep5-06`)
- ✅ parental_config dedupe/debounce (`ep5-07`)
- ⬜ threat aggregate rerender — `ep5-08`
- ⬜ iOS permissions gap — `ep5-09`
- ✅ Keychain user_preferences noise (`ep5-02`)
- ⬜ Redundant API on foreground — `ep5-04`
- ⬜ Snapshotting keyboard — `ep5-03`

### Ep6 (Family Chat → AI → Network → Family → Parental → Antifake → Geo)
- ✅ AG cycles mitigated (`ep6-01`)
- ✅ Typing burst debounce (`ep6-05`)
- ✅ E2EE keys cache (`ep6-04`)
- ✅ AI slow response UX (`ep6-06`)
- ✅ DNS Manager spam (`ep6-11`)
- ✅ location-bubble decode (`ep6-02`)
- ✅ Publishing from background (`ep6-08`)
- ✅ Navigation antifakeHub dedupe (`ep6-13`)
- ✅ FamilyScreen empty race (`ep6-12`)
- ✅ SF symbols (`ep6-07`, `ep6-15`)
- ✅ FamilyLocationModal kCLError UX (`ep6-14`)
- ✅ E2EE Keychain -25300 quiet (`ep6-03`)
- ⬜ Location Always upgrade global (`ep6-09`)
- ⬜ metrics upload -1005 retry (`ep6-10`)
- Location Always vs WhenInUse — `ep6-09`
- E2EE keychain -25300 — `ep6-03`
- metrics connection reset — `ep6-10`

---

## Рекомендуемый порядок работ

```
1.  ep6-01-attribute-graph-cycles
2.  ep6-08-publishing-from-background
3.  ep6-05, ep6-04, ep5-07, ep5-06
4.  … остальные P2/P3 …
5.  hero-prebuild-01 → hero-prebuild-02 → hero-prebuild-03   ← ПРЕДФИНАЛ
6.  hero-5-01 (bump 240)
7.  hero-5-02 + hero-1-03 + ep-final-simulator-build          ← сборка (только по разрешению)
8.  hero-6-* device QA
```

---

## Ключевые файлы

| Область | Путь |
|---------|------|
| family_id / Keychain | `Core/Managers/FamilyLocalStore.swift`, `Core/Network/APIService.swift` |
| Antifake | `Screens/AntifakeHubScreen.swift`, `ViewModels/AntifakeTextCheckViewModel.swift` |
| SF Symbols | `Core/Utilities/LogSanitizer.swift` (`SFSymbolCompat`) |
| Network / JWT | `Core/Network/NetworkManager.swift` |
| API validation | `Core/Validation/APIResponseValidator.swift` |
| Navigation | `Core/Navigation/NavigationManager.swift` |
| Location API | wrapper для `/api/location-bubble/requests` |

---

## Cursor TODO — полный реестр id (82 пункта)

> **Правило:** id **никогда не удалять** из Cursor TODO. Только `merge: true` и смена `status`.

### ПРЕДФИНАЛ — важно, не сделано (перед сборкой)

`hero-prebuild-01`, `hero-prebuild-02`, `hero-prebuild-03` (+ `hero-2-03`)

### Companion Hero

`hero-0-01`, `hero-0-02`, `hero-0-03`, `hero-1-01`, `hero-1-02`, `hero-1-03`, `hero-1-04`, `hero-2-01`, `hero-2-02`, `hero-2-03`, `hero-3-01`, `hero-3-02`, `hero-3-03`, `hero-3-04`, `hero-3-05`, `hero-3-06`, `hero-4-01`, `hero-4-02`, `hero-4-03`, `hero-prebuild-01`, `hero-prebuild-02`, `hero-prebuild-03`, `hero-5-01`, `hero-5-02`, `hero-5-03`, `hero-5-04`, `hero-6-01`, `hero-6-02`, `hero-6-03`, `hero-6-04`

### Log Analysis — Completed (2)

`ep3-00-antifake-input`, `ep3-03-sf-symbol-phone`

### Log Analysis — Pending (50)

`ep3-01-family-id-delete`, `startup-08-parental-trial`, `startup-ssl-pinning`, `ep2-03-companion-ui-keys`, `startup-03-lifecycle`, `startup-04-icloud-kvs`, `startup-05-network-singleton`, `startup-06-log-serialize`, `startup-09-additional-noise`, `ep2-01-onboarding-nav`, `ep2-02-demo-label`, `ep2-04-companion-cache`, `ep2-05-sf-symbol`, `ep2-07-notifications-dup`, `ep2-08-devices-empty`, `ep3-02-component-status-burst`, `ep3-04-antifake-double-submit`, `ep3-05-localization-init`, `startup-07-boringssl`, `startup-10-offline-validator`, `ep2-06-companion-validators`, `ep2-09-metrics-broken-pipe`, `ep4-01-crash-simulator-ux`, `ep4-02-crash-test-location`, `ep4-03-toggle-debounce`, `ep4-04-roadside-history-404`, `ep5-01-ap-reinit-optimization`, `ep5-02-keychain-user-prefs-noise`, `ep5-03-snapshotting-warning`, `ep5-04-redundant-api-calls`, `ep5-06-jwt-log-spam`, `ep5-07-parental-config-double-post`, `ep5-08-threat-aggregate-rerender`, `ep5-09-ios-settings-permissions-gap`, `ep6-01-attribute-graph-cycles`, `ep6-02-location-data-decoding`, `ep6-03-e2ee-keychain-errors`, `ep6-04-chat-e2ee-keys-burst`, `ep6-05-chat-send-typing-burst`, `ep6-06-ai-assistant-slow-response`, `ep6-07-parental-sf-symbol`, `ep6-08-publishing-from-background`, `ep6-09-location-permission-always`, `ep6-10-metrics-connection-reset`, `ep6-11-dns-manager-spam`, `ep6-12-family-screen-empty-race`, `ep6-13-nav-antifake-stack-dup`, `ep6-14-family-location-kcleerror`, `ep6-15-phone-badge-still-broken`, `ep-final-simulator-build`

---

## Связанные документы

| Документ | Назначение |
|----------|------------|
| [COMPANION_ML_HANDOFF_HERO_ANIMATION_AND_PERF.md](COMPANION_ML_HANDOFF_HERO_ANIMATION_AND_PERF.md) | **Handoff ML-системы** — детали Companion Hero |
| [ALADDIN_MASTER_TODO.md](../.cursor/ALADDIN_MASTER_TODO.md) | Общий мастер-план UX/perf/antifake |
| [aladdin-diagnostic-exports.mdc](../.cursor/rules/aladdin-diagnostic-exports.mdc) | Как читать экспорт логов |
