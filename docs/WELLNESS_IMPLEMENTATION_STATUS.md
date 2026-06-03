# Wellness Platform — статус реализации (131 задача)

> **Обновлено:** 2026-06-03 (build **223**, r100 premium funnel, handoff)  
> **Ядро:** 131/131 · **Дорожка «100%»:** [WELLNESS_ROADMAP_100.md](./WELLNESS_ROADMAP_100.md) (`r100-*`)  
> **PO-трекинг:** 133/134 (`po-healthkit` → [rollback plan](./WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md))  
> **Рабочая папка:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
> **Чеклист ядра:** [WELLNESS_CURSOR_TODO.md](./WELLNESS_CURSOR_TODO.md)  
> **Handoff для новой ML (продолжение):** [WELLNESS_ML_HANDOFF_R100.md](./WELLNESS_ML_HANDOFF_R100.md)  
> **Handoff 131 (архив):** [WELLNESS_ML_HANDOFF.md](./WELLNESS_ML_HANDOFF.md)  
> **Деплой (отложен):** [WELLNESS_DEPLOY_BACKLOG.md](./WELLNESS_DEPLOY_BACKLOG.md)

---

## Сводка

| Фаза | Всего | Готово | % |
|------|-------|--------|---|
| 0 — подготовка | 16 | 16 | 100% |
| 1 — MVP | 29 | 29 | 100% |
| 2 — столпы + automation | 51 | 51 | 100% |
| 3 — orchestrator + premium | 20 | 20 | 100% |
| §18 i18n | 15 | 15 | 100% |
| **Σ** | **131** | **131** | **100%** |

**Осталось (ядро):** 0. **PO (отложено):** откат HealthKit для CI — [WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md](./WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md) · Portal HealthKit (вариант A) — [WELLNESS_APPLE_HEALTHKIT_SETUP.md](./WELLNESS_APPLE_HEALTHKIT_SETUP.md).

---

## План vs факт (финальный срез)

| Блок | План | Факт |
|------|------|------|
| Backend REST | `/api/wellness/*` 80+ routes | ✅ `wellness_router.py` + smoke |
| i18n | 297 keys ru/en + 25 JSON | ✅ `check_wellness_l10n.py` |
| Premium | ethics (p3-12) + subscription (p3-06) | ✅ `wellness_premium_access.py` |
| Errors API | p18-15 structured `{code, message_key, message}` | ✅ `errors_v1.json` + catalog |
| Ф3 extras | widget/PDF/values/seasonal/sleep/senior | ✅ API + iOS scaffold |
| Postgres | p3-11 migration | ✅ scaffold + runbook (prod still SQLite) |
| Canary | p3-10 runbook | ✅ `WELLNESS_CANARY_RUNBOOK.md` |

**Scaffold (ops позже):** Postgres cutover, Rive `.riv` assets, CDN sleep audio URLs, `FEATURE_WELLNESS_PARENT_LLM=1`.

---

## Деплой backend (VPS) — чеклист

| Шаг | Статус | Как проверить |
|-----|--------|----------------|
| `deploy_wellness_p1.sh` — все `wellness_*.py` + router + i18n JSON | ✅ | scp ~60 файлов на `149.154.65.180:/opt/aladdin-backend` |
| Restart `aladdin-backend.service` | ✅ | smoke на localhost:8002 |
| `vps_smoke_wellness.py` | ✅ 2026-06-01 | ALL PASSED (incl. phq9_child_block, errors_catalog n=19) |
| Prod через nginx | ✅ 2026-06-03 14:21 | `verify_wellness_prod.sh` — **14/14** (child pillars: `device_id` + `age_band` после fix `wellness_age_policy`) |
| Feature flags prod | ✅ | `ENABLED=1`, `ORCHESTRATOR=1`, `REFLECTIVE=1`, `JUNG=1` |
| l10n gate | ✅ | `python3 scripts/check_wellness_l10n.py` — 297 keys |

**Команда выката:**

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./scripts/deploy_wellness_p1.sh root 149.154.65.180 ~/.ssh/aladdin_server
./scripts/verify_wellness_prod.sh https://aladdin-ai.ru
```

---

## iOS — финальные экраны / сервисы

| Компонент | Задачи |
|-----------|--------|
| Hub, Check-in, Consent, Trust, Assessment, Exercise, Dream, Timeline | Ф1–Ф2 |
| `WellnessAgeL10n` child/teen | p18-14 |
| `WellnessPremiumPaywallSheet` | p3-06 |
| `WellnessValuesCardSheet` | p3-07 |
| `WellnessProgressPDFService` | p3-19 |
| `WellnessCheckinWidget` | p3-18 |
| `WellnessPillarEmotionView` | p3-09 |
| `WellnessHealthSleepReader` | p2-36 · **CI:** entitlement блокирует archive → rollback B запланирован |
| `WellnessSwiftUICompat` | post-close — iOS 15.2 API shims |
| `WellnessNavigationStack` / `WellnessMultilineField` | внутри compat |

---

## 2026-06-02 — post-close iOS fixes (после 131/131)

> Задачи **не** в `WELLNESS_CURSOR_TODO.md` — стабилизация сборки Xcode (deployment target **15.2**).

| Изменение | Файлы | Зачем |
|-----------|--------|--------|
| iOS 15.2 shims | `Shared/Components/WellnessSwiftUICompat.swift` | `NavigationStack` → `root:`; `NavigationView` на 15; `presentationDetents`; multiline `TextField` |
| HealthKit sleep stages | `Core/Services/WellnessHealthSleepReader.swift` | `#available(iOS 16)` для asleepCore/Deep/REM vs legacy `.asleep` |
| Share PDF | `Screens/WellnessTimelineScreen.swift` | `ShareSheet` вместо `ShareLink` (iOS 16+) |
| Referral sheet | `Screens/WellnessReferralSheet.swift` | Убран мусор в импорте; compat navigation |
| Privacy Policy | `Screens/18_PrivacyPolicyScreen.swift` | `case .wellness` в deprecated `content` switch |
| Navigation icons | `Core/Navigation/NavigationManager.swift` | `.wellnessAssessmentsHub`, `.wellnessAssessmentFlow` |
| Xcode target | `ALADDIN.xcodeproj/project.pbxproj` | В **Compile Sources**: PDF, compat, Paywall, Values, Referral (уник. ID), **PillarEmotion** |

**PO:** после правок — Clean Build (⇧⌘K) → Build (⌘B).

### 2026-06-02 — CI build 221: HealthKit blocker (archive failed)

| Факт | Деталь |
|------|--------|
| Git | `95439b21` на `origin/master`, build **221**, Wellness + HealthKit entitlement |
| CI log | `logs_71945656834` — Fastlane archive **FAILED** |
| Ошибка | Profile `ALADDIN App Store Distribution new` **без** HealthKit; entitlement в `ALADDIN.entitlements` **есть** |
| Другие Health-типы | **Нет** — только read sleep для check-in |
| Предупреждение CI | Профили Development/Ad Hoc в secrets — отдельно от HealthKit; исправить при варианте A |
| **Решение PO** | ✅ **Вариант B** build **222**; текущий iOS build **223** (r100 wellness + companion) |
| План | [WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md](./WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md) |

Check-in **без HealthKit:** ползунок «Как спал(а)?» 3–12 ч — работает всегда.

### 2026-06-02 — Ops ML (handoff выполнен на VPS)

| Шаг | Статус | Деталь |
|-----|--------|--------|
| Parent LLM A | ✅ | `FEATURE_WELLNESS_PARENT_LLM=1`, backend active |
| Playbook curl | ✅ | JSON-фразы ru; `llm_used: false` (Hermes fallback — проверить ключи на VPS) |
| verify prod | ✅ | `verify_wellness_prod.sh` — 14/14 |
| Postgres B1–B4 | ✅ | DB `wellness` создана, migrate **160 rows**, `WELLNESS_PG_DUAL_WRITE=1` |
| PG read cutover | ⏳ | `WELLNESS_PG_READ=0` — включить через **7 дней** мониторинга (handoff B5) |
| smoke VPS | ✅ | `vps_smoke_wellness.py` — ALL PASSED |
| iOS unit test | ✅ | `WellnessModelsTests.swift` → таргет `ALADDINUnitTests` |
| Widget Extension | 📋 | Код в `ALADDINWidgets/` — таргет в Xcode: [MANUAL_WIDGET_SETUP.md](../MANUAL_WIDGET_SETUP.md) (~15 мин) |

Скрипт миграции: поддержка `companion_platform.db` (prod path).

---

## iOS — сверка `Wellness*.swift` ↔ таргет ALADDIN

Проверено: **2026-06-02**. Таргет: **ALADDIN** (main app). Отдельного **Widget Extension** в проекте нет.

| Файл | В репо | В таргете ALADDIN | Примечание |
|------|:------:|:-----------------:|------------|
| `Screens/WellnessConsentScreen.swift` | ✅ | ✅ | p1-10 |
| `Screens/WellnessHubScreen.swift` | ✅ | ✅ | p1-12 |
| `Screens/WellnessCheckinScreen.swift` | ✅ | ✅ | p1-13 |
| `Screens/WellnessTrustCenterScreen.swift` | ✅ | ✅ | p1-24 |
| `Screens/WellnessPhqLiteScreen.swift` | ✅ | ✅ | p1-06 |
| `Screens/WellnessExerciseScreen.swift` | ✅ | ✅ | p2-21 |
| `Screens/WellnessTimelineScreen.swift` | ✅ | ✅ | p2-19 |
| `Screens/WellnessDreamJournalScreen.swift` | ✅ | ✅ | p2-20 |
| `Screens/WellnessAssessmentFlowScreen.swift` | ✅ | ✅ | p2-03 (+ Hub внутри) |
| `Screens/WellnessReflectiveModeScreen.swift` | ✅ | ✅ | p2-22 |
| `Screens/WellnessTogetherModeScreen.swift` | ✅ | ✅ | p2-44 |
| `Screens/WellnessOutcomeSheet.swift` | ✅ | ✅ | p2-42 |
| `Screens/WellnessReferralSheet.swift` | ✅ | ✅ | p2-43 |
| `Screens/WellnessPremiumPaywallSheet.swift` | ✅ | ✅ | p3-06 (добавлен в target 2026-06-02) |
| `Screens/WellnessValuesCardSheet.swift` | ✅ | ✅ | p3-07 (добавлен в target 2026-06-02) |
| `Screens/WellnessPillarEmotionView.swift` | ✅ | ✅ | p3-09 (добавлен в target 2026-06-02) |
| `Core/Services/WellnessAPIService.swift` | ✅ | ✅ | p1-11 |
| `Core/Services/WellnessOfflineStore.swift` | ✅ | ✅ | p2-23 |
| `Core/Services/WellnessHealthSleepReader.swift` | ✅ | ✅ | p2-36 |
| `Core/Services/WellnessProgressPDFService.swift` | ✅ | ✅ | p3-19 (добавлен в target 2026-06-02) |
| `Core/Services/WellnessSessionStore.swift` | ✅ | ✅ | — |
| `Core/Services/WellnessLoopCoordinator.swift` | ✅ | ✅ | — |
| `Core/Models/WellnessModels.swift` | ✅ | ✅ | incl. `WellnessAgeL10n` |
| `Core/Models/WellnessTogetherSession.swift` | ✅ | ✅ | p2-44 |
| `Shared/Components/WellnessSwiftUICompat.swift` | ✅ | ✅ | post-close 2026-06-02 |
| `ALADDINWidgets/WellnessCheckinWidget.swift` | ✅ | ⚠️ нет | p3-18 scaffold; нужен **Widget Extension** target |
| `Tests/UnitTests/WellnessModelsTests.swift` | ✅ | ✅ | `ALADDINUnitTests` — `scripts/run_wellness_r100_tests.sh` |

**Итого main app:** 25/25 Swift-файлов wellness в таргете · **1** файл вне compile: widget (`ALADDINWidgets/` → r100-2-06).

**UI smoke (2026-06-03):** `Tests/UITests/WellnessCompanionNavUITests.swift` — r100-0-05 / r100-2-12.  
**Статический gate (без xcodebuild):** `./scripts/verify_r100_ios_static.sh` — таргеты, UITest bootstrap, чеклисты.

---

## 2026-06-03 — дорожка r100 (Companion + герои, без деплоя PO)

> Детали: [WELLNESS_ML_HANDOFF_R100.md](./WELLNESS_ML_HANDOFF_R100.md) · План: [WELLNESS_ROADMAP_100.md](./WELLNESS_ROADMAP_100.md)

| Область | Статус в репо |
|---------|----------------|
| hero_flavor 3×4, pack instructions | ✅ draft |
| Recap, memory chips, outcome→fatigue, drift log | ✅ |
| Voice reconnect, embedded nav, check-in→hero banner | ✅ |
| Hermes keys, Rive, clinical | ⏳ батч 7 |
| Premium funnel (r100-1-16) | ✅ Hub gate + paywall → тарифы — [WELLNESS_PREMIUM_FUNNEL.md](./WELLNESS_PREMIUM_FUNNEL.md) |
| Деплой VPS + TestFlight | ⏳ [WELLNESS_DEPLOY_BACKLOG.md](./WELLNESS_DEPLOY_BACKLOG.md) |

---

## r100 — осталось (13 из 39) · 26 закрыто

> Полная таблица: [WELLNESS_ML_HANDOFF_R100.md](./WELLNESS_ML_HANDOFF_R100.md) §4.

| id | Простыми словами | Кто |
|----|------------------|-----|
| r100-0-01 | TestFlight: 15 пунктов на телефоне | PO |
| r100-0-03 | Ключи Hermes (батч 7) | PO |
| r100-0-04 | Parent LLM `llm_used: true` | BE ops |
| r100-1-04 | Postgres **read** через 7 дней dual-write | BE ops |
| r100-2-06 | **Виджет** check-in на Home Screen (Widget Extension в Xcode) | iOS ~15 мин |
| r100-4-voice | Полировка задержки голоса | iOS |
| r100-5-ethics | Аудит L3 + родитель не видит teen-chat | QA |
| r100-6-store | App Store metadata | PO |
| r100-6-healthkit | HealthKit Portal A или откат B | PO |
| r100-7-07 | Rive анимации героев | Design |
| r100-7-08 | Sleep stories MP3 на CDN | BE+iOS |
| r100-7-10 | Clinical sign-off → pack `approved` | Внешний |
| r100-7-docs | Внутренние docs: «дорожка» не «столп» | Docs |

**Не путать с «4 виджета»:** только **r100-2-06** — виджет; остальное — ethics, docs, voice.

**Сборка 223 (канон):** `AppConfig.swift` · `AppConfigTests.swift` · `ALADDIN.xcodeproj` (`CURRENT_PROJECT_VERSION`).

---

## Пакет для передачи другой ML (индекс)

| Файл | Зачем |
|------|--------|
| **[WELLNESS_ML_HANDOFF_R100.md](./WELLNESS_ML_HANDOFF_R100.md)** | **Главный handoff 2026-06-03** — герои, r100 todo, что сделано, деплой |
| [WELLNESS_ROADMAP_100.md](./WELLNESS_ROADMAP_100.md) | План до 100%, батчи, r100-* |
| [WELLNESS_DEPLOY_BACKLOG.md](./WELLNESS_DEPLOY_BACKLOG.md) | Один деплой когда PO готов |
| [WELLNESS_CURSOR_TODO.md](./WELLNESS_CURSOR_TODO.md) | **131** задача — все ☑ (справочник) |
| [WELLNESS_PLATFORM_MASTER_PLAN.md](./WELLNESS_PLATFORM_MASTER_PLAN.md) | Архитектура **v2.5** |
| **WELLNESS_IMPLEMENTATION_STATUS.md** | Этот файл — 131/131, **2026-06-02**, **Wellness*.swift** |
| [WELLNESS_ML_HANDOFF.md](./WELLNESS_ML_HANDOFF.md) | Старый handoff 131 (не дублировать работу) |
| [WELLNESS_POSTGRES_PARENT_LLM_HANDOFF.md](./WELLNESS_POSTGRES_PARENT_LLM_HANDOFF.md) | Postgres + Parent LLM |
| `.cursor/rules/wellness-platform-expert.mdc` | Правило Cursor |
| [ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md](../ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md) | VPS |

> **Версии:** канон **131 ядро** (2026-06-01) + **r100** (2026-06-03). Новой ML: [WELLNESS_ML_HANDOFF_R100.md](./WELLNESS_ML_HANDOFF_R100.md) §0.

### Как передать ML (кратко)

1. Папка только: `…/mobile_apps/ALADDIN_iOS`.
2. Новый чат → вставить **§0** из [WELLNESS_ML_HANDOFF_R100.md](./WELLNESS_ML_HANDOFF_R100.md).
3. `@docs/WELLNESS_ML_HANDOFF_R100.md` `@docs/WELLNESS_ROADMAP_100.md` `@docs/WELLNESS_IMPLEMENTATION_STATUS.md`.
4. TodoWrite: **r100-*** из handoff §4 (не переделывать 131).
5. Деплой — только по [WELLNESS_DEPLOY_BACKLOG.md](./WELLNESS_DEPLOY_BACKLOG.md) после TestFlight.

---

## Тесты (локально)

```bash
python3 scripts/check_wellness_l10n.py
PYTHONPATH=. python3 -m pytest Tests/test_wellness_*.py -q
```

Ожидание: **110/110** passed (18 test modules).

---

## Документы

| Документ | Статус |
|----------|--------|
| [WELLNESS_CURSOR_TODO.md](./WELLNESS_CURSOR_TODO.md) | 131/131 ☑ |
| [WELLNESS_I18N_CHECKLIST.md](./WELLNESS_I18N_CHECKLIST.md) | §17 errors ☑ |
| [WELLNESS_CANARY_RUNBOOK.md](./WELLNESS_CANARY_RUNBOOK.md) | p3-10 |
| [WELLNESS_POSTGRES_MIGRATION.md](./WELLNESS_POSTGRES_MIGRATION.md) | p3-11 |
| [WELLNESS_APPLE_HEALTHKIT_SETUP.md](./WELLNESS_APPLE_HEALTHKIT_SETUP.md) | PO manual |

---

*Синхронизировано с WELLNESS_CURSOR_TODO.md · ядро CLOSED 2026-06-01 · iOS target audit 2026-06-02.*
