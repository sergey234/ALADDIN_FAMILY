# Wellness Platform — статус реализации (131 задача)

> **Обновлено:** 2026-06-02 (post-close iOS Xcode sync + `Wellness*.swift` ↔ target audit)  
> **Ядро:** 131/131 · **PO-трекинг:** 133/134 (`po-healthkit` открыт)  
> **Рабочая папка:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
> **Чеклист:** [WELLNESS_CURSOR_TODO.md](./WELLNESS_CURSOR_TODO.md)  
> **Handoff для ML:** [WELLNESS_ML_HANDOFF.md](./WELLNESS_ML_HANDOFF.md)

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

**Осталось (ядро):** 0. **PO вручную:** HealthKit capability в Apple Developer Portal — [WELLNESS_APPLE_HEALTHKIT_SETUP.md](./WELLNESS_APPLE_HEALTHKIT_SETUP.md).

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
| Prod через nginx | ✅ 2026-06-01 21:36 | `verify_wellness_prod.sh` — **14/14** |
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
| `WellnessHealthSleepReader` | p2-36 / po-healthkit |
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
| `Tests/UnitTests/WellnessModelsTests.swift` | ✅ | ⚠️ нет | не в `ALADDINUnitTests` (pytest backend отдельно) |

**Итого main app:** 25/25 Swift-файлов wellness в таргете · **2** файла в репо вне compile (widget + unit test).

---

## Пакет для передачи другой ML (индекс)

| Файл | Зачем |
|------|--------|
| [WELLNESS_ML_HANDOFF.md](./WELLNESS_ML_HANDOFF.md) | Главная инструкция — §0 стартовое сообщение, шаги A–D, gate, DoD, ошибки |
| [WELLNESS_CURSOR_TODO.md](./WELLNESS_CURSOR_TODO.md) | **131** задача `p0-01`…`p3-20`, `p18-*` + **3 PO** → **134** трекинг |
| [WELLNESS_PLATFORM_MASTER_PLAN.md](./WELLNESS_PLATFORM_MASTER_PLAN.md) | Архитектура **v2.5** (§4.3 Knowledge Pack, §19 ML) |
| [WELLNESS_IMPLEMENTATION_STATUS.md](./WELLNESS_IMPLEMENTATION_STATUS.md) | Этот файл — факт, деплой, iOS audit |
| [WELLNESS_POSTGRES_PARENT_LLM_HANDOFF.md](./WELLNESS_POSTGRES_PARENT_LLM_HANDOFF.md) | Ops: Postgres cutover + Parent LLM на VPS |
| `.cursor/rules/wellness-platform-expert.mdc` | Правило Cursor для wellness-файлов |
| [WELLNESS_APPLE_HEALTHKIT_SETUP.md](./WELLNESS_APPLE_HEALTHKIT_SETUP.md) | PO: capability Portal |
| [ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md](../ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md) | Deploy VPS |

> **Версии:** в старых переписках встречаются «120 задач» и master plan **v2.4** — канон сейчас **131 ядро + §18** и **v2.5-final** (2026-06-01). Фазы 0–3 **закрыты**; новой ML — не «Старт Фаза 0», а ops/App Store (см. handoff §11).

### Как передать ML (кратко)

1. Папка только: `…/mobile_apps/ALADDIN_iOS` (не весь `ALADDIN_NEW` ~28GB).
2. Новый чат → `@docs/WELLNESS_ML_HANDOFF.md` + `@WELLNESS_CURSOR_TODO.md` + `@WELLNESS_PLATFORM_MASTER_PLAN.md`.
3. Вставить блок **§0** из handoff → дождаться **Шага A** (таблица 4 столпа / запреты / риски).
4. TodoWrite: импорт **131** id (все `completed`) + PO `po-healthkit` `pending`.
5. Работа: Postgres/Parent LLM handoff, `verify_wellness_prod.sh`, iOS TestFlight.

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
