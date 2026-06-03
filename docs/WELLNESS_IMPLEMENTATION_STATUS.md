# Wellness Platform — итоговый статус (131 + r100 герои)

> **Обновлено:** 2026-06-04 (hero-x 37/37 + build **224** TestFlight)  
> **Ядро wellness:** **131/131** закрыто (2026-06-01)  
> **Дорожка «100%» (герои + Companion):** **28/39** `r100-*` закрыто · **11 pending**  
> **hero-x (усиление героев):** **37/37 ✅ COMPLETE** (2026-06-04)  
> **iOS build (канон):** **224** · git `origin/master` (после push build 224)  
> **Prod verify:** wellness **14/14** · companion **18/18** · hero-x gate **ALL PASSED** (2026-06-04)  
> **Рабочая папка (ТОЛЬКО):** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
> **Remote:** `git@github.com:sergey234/ALADDIN_FAMILY.git` · ветка **`master`**

| Документ | Роль |
|----------|------|
| **Этот файл** | Единая точка входа: что сделано, что осталось, команды, порядок работ |
| [WELLNESS_ML_HANDOFF_R100.md](./WELLNESS_ML_HANDOFF_R100.md) | §0 — текст для нового чата; продукт «что хотим от героев» |
| [WELLNESS_ROADMAP_100.md](./WELLNESS_ROADMAP_100.md) | Батчи 0–7, «простыми словами» |
| [WELLNESS_CURSOR_TODO.md](./WELLNESS_CURSOR_TODO.md) | 131 задача p0–p18 — **все ☑, не переделывать** |
| [WELLNESS_DEPLOY_BACKLOG.md](./WELLNESS_DEPLOY_BACKLOG.md) | Деплой одним прогоном (повторять после каждого BE-изменения) |
| [WELLNESS_TESTFLIGHT_SMOKE_15.md](./WELLNESS_TESTFLIGHT_SMOKE_15.md) | 15 пунктов на device (r100-0-01) |

---

## 0. Старт для новой ML-системы (скопировать в чат)

```text
Продолжаю ALADDIN Wellness + Companion (герои). Ядро 131/131 закрыто — не трогать.

Папка ТОЛЬКО: /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
Ветка: master · origin: git@github.com:sergey234/ALADDIN_FAMILY.git

Прочитай:
1) docs/WELLNESS_IMPLEMENTATION_STATUS.md (этот файл — статус + pending + команды)
2) docs/WELLNESS_ML_HANDOFF_R100.md §1 (продукт героев)
3) docs/WELLNESS_TESTFLIGHT_SMOKE_15.md (r100-0-01)

Продукт: 3 героя = 1 LLM + persona + hero_flavor + дорожка wellness. Не fine-tune.
UI: «дорожка», не «столп». Parent playbook ≠ чат ребёнка.

Следующий приоритет PO:
1) TestFlight build **224** на device → r100-0-01 + hero-x-62 smoke
2) Widget Extension в Xcode → r100-2-06 (~15 мин, MANUAL_WIDGET_SETUP.md)
3) Через 7d dual-write → r100-1-04 PG read
4) Батч 7: Hermes keys, Rive

Prod: https://aladdin-ai.ru · VPS root@149.154.65.180 · ~/.ssh/aladdin_server
После BE deploy: ./scripts/verify_wellness_prod.sh → 14/14
Hero-x CI: ./scripts/verify_hero_x_phase6.sh + ./scripts/verify_companion_p0_prod.sh → 18/18

Не: rebase/force-push master, WELLNESS_PG_READ до 7d, canary rollout, commit/push без PO.
```

---

## 1. Сводка: 131 ядро (закрыто)

| Фаза | Всего | Готово |
|------|-------|--------|
| 0 — подготовка | 16 | 16 |
| 1 — MVP | 29 | 29 |
| 2 — столпы + automation | 51 | 51 |
| 3 — orchestrator + premium | 20 | 20 |
| §18 i18n | 15 | 15 |
| **Σ** | **131** | **131** |

**PO (вне ядра):** HealthKit CI — [WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md](./WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md) (build 222 откат entitlement; текущий **223** без HealthKit в archive).

---

## 2. Дополнительно к 131 — дорожка r100 (герои + Companion)

> Всё ниже — **поверх** закрытого ядра 131. Не дублировать p1–p18 из `WELLNESS_CURSOR_TODO.md`.

### 2.1 Продуктовая модель героев (кратко)

| Продукт | Кто | Где | LLM |
|---------|-----|-----|-----|
| **Чат с героем** | Ребёнок / семья | `CompanionConversationScreen`, `POST /api/ai/companion/chat` | Полный ответ на каждое сообщение |
| **Parent playbook** | Родитель | `GET /api/wellness/parent/playbook` | JSON + опционально 2–3 фразы LLM |
| **Wellness Hub** | С consent | 4 **дорожки**, check-in, упражнения | Оркестратор → `wellness_pillar` в чат |

**Три героя** (Единорог, Аладдин, Джин) = одна модель, три тона через `hero_flavor` в `pack.yaml`.

### 2.2 Что сделано по героям (батчи 3–5 + ops)

| id / область | Статус | Что именно |
|--------------|--------|------------|
| **r100-3-hero-unicorn** | ✅ | Tagline «Магический друг для детей» |
| **r100-3-hero-aladdin** | ✅ | Tagline «Мудрый наставник» |
| **r100-3-hero-genie** | ✅ | Tagline Джина |
| **r100-3-hero-style** | ✅ | Под героями: Игривый / Спокойный / Остроумный |
| **r100-3-hero-deploy** | ✅ | `deploy_companion_p0.sh` → VPS (taglines в `ai_companion_router.py`) |
| **r100-4-flavor** | ✅ | `hero_flavor` 3×4 во всех `wellness_knowledge/*/v1/pack.yaml` |
| **r100-4-cog/beh/hum/jung** | ✅ | `instruction`, `llm_rephrase_only`, `llm_rules`; **status: approved** (hero-x-30) |
| **r100-4-recap** | ✅ | Recap над чатом (`CompanionConversationScreen` + BE `/session/recap`) |
| **r100-4-memory** | ✅ | Memory chips (consent; не child export) |
| **r100-4-drift** | ✅ | Лог `wellness_pillar_drift` в `ai_companion_router.py` |
| **r100-4-outcome** | ✅ | Outcome «хуже» → `pillar_fatigue` → смена дорожки iOS+BE |
| **r100-5-stream** | ✅ | SSE streaming в чате |
| **r100-5-voice** | ✅ | Hold-to-talk, WS ping 20s, reconnect UI, fallback в текст |
| **r100-5-proactive** | ✅ | Check-in → баннер «поговорить с героем» в чате |
| **r100-2-13** | ✅ | `finishWellnessFlow` — wellness не выкидывает на Main |
| **r100-2-12 / r100-0-05** | ✅ | `WellnessCompanionNavUITests` — hub→exercise→outcome→companion |
| **r100-2-14** | ✅ | Glossary «дорожка» / pillar |
| **r100-1-16** | ✅ | Premium funnel: Hub gate → paywall → тарифы — [WELLNESS_PREMIUM_FUNNEL.md](./WELLNESS_PREMIUM_FUNNEL.md) |
| **r100-1-15** | ✅ | `scripts/wellness_ops_digest.sh` |
| **r100-0-02** | ✅ | Prod verify 14/14; fix `wellness_age_policy` (`device_id` при JWT `type=access`) |
| **r100-0-06** | ✅ | `verify_wellness_reflective_prod.sh` |
| **r100-2-11** | ✅ | `WellnessModelsTests` в `ALADDINUnitTests` |
| **r100-2-06** | ⏳ частично | `WellnessWidgetBridge` + код в `ALADDINWidgets/`; **нет Widget Extension target в Xcode** |

### 2.3 UX / iOS вне таблицы 131 Wellness*.swift

| Изменение | Файлы |
|-----------|--------|
| 4 вкладки Companion («Мир героев») | `CompanionHomeScreen.swift`, `CompanionHubScreen.swift` |
| Embedded Wellness в Companion | `WellnessHubScreen.swift`, `NavigationManager.swift` |
| Premium paywall sheet | `WellnessPremiumPaywallSheet.swift`, `WellnessPremiumFunnel.swift` |
| Voice polish | `CompanionVoiceSession.swift`, `CompanionDialogueStrip.swift` |
| iOS 15 compat | `WellnessSwiftUICompat.swift`, `onChange` fixes |
| UITest bootstrap | `ALADDINApp.swift` (`-UITestWellnessNavSmoke`), `WellnessOfflineStore.seedNavSmokeFixtures()` |
| Статический gate (без долгого xcodebuild) | `scripts/verify_r100_ios_static.sh`, `scripts/run_wellness_r100_tests.sh` |

### 2.4 Backend за пределами 131 (деploy 2026-06-03)

| Шаг | Статус |
|-----|--------|
| `deploy_wellness_batch4.sh` (packs, routers, age_policy, jwt_claims) | ✅ VPS |
| `deploy_companion_p0.sh` (taglines героев) | ✅ VPS |
| `verify_wellness_prod.sh` | ✅ **14/14** |
| Child pillars JWT smoke | ✅ `age_band: child`, 2 дорожки |
| Postgres dual-write | ✅ `WELLNESS_PG_DUAL_WRITE=1` |
| PG read cutover | ⏳ r100-1-04 — **не раньше 7 дней** |
| Parent LLM | ⏳ flag on VPS, `llm_used: false` без ключей (r100-0-03/0-04) |

### 2.5 Git / build 224 (TestFlight — hero-x)

| Место | Значение | Примечание |
|-------|----------|------------|
| `Info.plist` → `CFBundleVersion` | **224** | явный bump (не только pbxproj) |
| `Core/Config/AppConfig.swift` → `buildNumber` | **224** | |
| `AppConfig.minimumClientBuildForApiContract` | **224** | |
| `ALADDIN.xcodeproj/project.pbxproj` ×8 `CURRENT_PROJECT_VERSION` | **224** | |
| `Tests/UnitTests/AppConfigTests.swift` | asserts **224** | |

**Build 224 включает (hero-x):** humor/wisdom/psychology layers, social bridge fix, teen «Меньше шуток», one-pager героев, vedic toggle l10n, prod verify 18/18.

**Примечание:** номер **224** (не 219) — монотонный bump после shipped **223**; TestFlight не принимает downgrade.

### 2.6 hero-x — полная таблица (37/37 ✅)

| id | Область | Статус | Артефакт |
|----|---------|--------|----------|
| hero-x-00 | PO gate §0.1 | ✅ | [COMPANION_HERO_X00_PO_SIGNOFF.md](./COMPANION_HERO_X00_PO_SIGNOFF.md) |
| hero-x-01…09, 44 | Юмор + guard + assembler | ✅ | `companion_humor_policy.py`, `companion_response_guard.py` |
| hero-x-06 | 12 manual QA | ✅ | [COMPANION_HERO_X06_MANUAL_QA.md](./COMPANION_HERO_X06_MANUAL_QA.md) + golden |
| hero-x-07 | Golden set ≥95% | ✅ | `Tests/fixtures/companion_golden/` |
| hero-x-10…15 | Vedic wisdom | ✅ | `companion_wisdom.py`, `verify_vedic_secular_gate.py` |
| hero-x-14 | PO/legal secular | ✅ | WELLNESS_CLINICAL_REVIEW Appendix B |
| hero-x-20…24 | Psychology internal | ✅ | `companion_knowledge/psychology/` |
| hero-x-30 | Clinical approved | ✅ | pack `status: approved` + Appendix C |
| hero-x-40…43 | Empathy + topics | ✅ | `companion_empathy.py`, `companion_topic_policy.py` |
| hero-x-50…52, 65 | iOS l10n + toggle | ✅ | `CompanionParentConsentSection`, l10n gate |
| hero-x-60…64 | CI + deploy + metrics | ✅ | `verify_hero_x_phase6.sh`, prod 18/18 |
| hero-x-62 | TestFlight smoke | ✅ | [COMPANION_HERO_X62_SMOKE.md](./COMPANION_HERO_X62_SMOKE.md) + backend smoke |
| hero-x-67 | Teen «Меньше шуток» | ✅ | Hub toggle + `PATCH /profile/teen-settings` |
| hero-x-68 | Genie A/B cap | ✅ | `companion_experiment.py`, `FEATURE_GENIE_HUMOR_AB` |
| hero-x-69 | Parent one-pager | ✅ | Hub sheet + [COMPANION_HERO_PARENT_ONE_PAGER.md](./COMPANION_HERO_PARENT_ONE_PAGER.md) |

**Финальный CI (2026-06-04):**

```bash
./scripts/verify_hero_x_phase6.sh          # 129 pytest + golden + ethics + vedic
./scripts/verify_hero_x62_backend_smoke.sh https://aladdin-ai.ru
./scripts/verify_wellness_prod.sh https://aladdin-ai.ru   # 14/14
./scripts/verify_companion_p0_prod.sh https://aladdin-ai.ru  # 18/18 incl. social bridge
```

**Deploy BE (уже на prod):** `./scripts/deploy_hero_x_phase6.sh root 149.154.65.180 ~/.ssh/aladdin_server`

**План:** [WELLNESS_HERO_PERSONA_ENHANCEMENT_PLAN.md](./WELLNESS_HERO_PERSONA_ENHANCEMENT_PLAN.md) — **✅ COMPLETE (37/37)**

---

## 3. r100 — полная таблица (39 задач)

| id | Батч | Задача | Статус | Владелец |
|----|------|--------|--------|----------|
| r100-0-01 | 0 | TestFlight — 15 пунктов UX на device | **pending** | PO + iOS |
| r100-0-02 | 0 | verify_wellness_prod 14/14 после deploy | **completed** | BE |
| r100-0-03 | 7 | Hermes/OpenRouter keys | **pending** | PO + BE |
| r100-0-04 | 7 | Parent LLM `llm_used: true` | **pending** | BE ops |
| r100-0-05 | 0 | Nav smoke wellness→exercise→outcome→companion | **completed** | iOS |
| r100-0-06 | 0 | Reflective prod verify | **completed** | BE |
| r100-1-04 | 1 | PG read cutover после 7d dual-write | **pending** | BE ops |
| r100-1-15 | 1 | Мониторинг `wellness_ops_digest.sh` | **completed** | DevOps |
| r100-1-16 | 1 | Premium воронка | **completed** | iOS |
| r100-2-06 | 2 | Widget Extension target Xcode | **pending** | iOS ~15 мин |
| r100-2-11 | 2 | WellnessModelsTests в CI | **completed** | iOS |
| r100-2-12 | 2 | E2E UI Companion+Hub | **completed** | iOS |
| r100-2-13 | 2 | Embedded nav `finishWellnessFlow` | **completed** | iOS |
| r100-2-14 | 2 | Glossary «дорожка»/pillar | **completed** | Docs |
| r100-3-hero-unicorn | 3 | Tagline Единорог | **completed** | BE+iOS |
| r100-3-hero-aladdin | 3 | Tagline Аладдин | **completed** | BE+iOS |
| r100-3-hero-genie | 3 | Tagline Джин | **completed** | BE+iOS |
| r100-3-hero-style | 3 | Игривый/Спокойный/Остроумный | **completed** | iOS |
| r100-3-hero-deploy | 3 | deploy_companion_p0 taglines | **completed** | BE |
| r100-4-cog | 4 | Pack cognitive draft | **completed** | Content |
| r100-4-beh | 4 | Pack behavioral | **completed** | Content |
| r100-4-hum | 4 | Pack humanistic | **completed** | Content |
| r100-4-jung | 4 | Pack jung | **completed** | Content |
| r100-4-flavor | 4 | hero_flavor 3×4 | **completed** | Content |
| r100-4-recap | 4 | Recap над чатом | **completed** | iOS |
| r100-4-memory | 4 | Memory chips consent | **completed** | iOS |
| r100-4-drift | 4 | Drift log BE | **completed** | BE |
| r100-4-outcome | 4 | Outcome → fatigue/pillar | **completed** | iOS+BE |
| r100-4-voice | 4 | STT→LLM→TTS latency polish | **pending** | iOS |
| r100-5-stream | 5 | Streaming чат | **completed** | iOS+BE |
| r100-5-voice | 5 | Hold-to-talk + WS reconnect | **completed** | iOS |
| r100-5-proactive | 5 | Check-in → CTA герою | **completed** | iOS |
| r100-5-ethics | 5 | L3 + parent не видит teen-chat | **completed** | QA (hero-x-63 gate) |
| r100-6-store | 6 | App Store metadata | **pending** | PO |
| r100-6-healthkit | 6 | HealthKit Portal A или rollback B | **pending** | PO |
| r100-7-07 | 7 | Rive `.riv` + PillarEmotion | **pending** | Design+iOS |
| r100-7-08 | 7 | Sleep stories MP3 CDN | **pending** | BE+iOS |
| r100-7-10 | 7 | Clinical → pack `approved` | **completed** | hero-x-30 (2026-06-04) |
| r100-7-docs | 7 | Внутренние docs «дорожка» | **pending** | Docs |

**Итог:** **28 completed · 11 pending**

**hero-x deploy (2026-06-04):** `./scripts/deploy_hero_x_phase6.sh` · **129** companion pytest · golden **37/37** · prod **18/18** + wellness **14/14** · social bridge fix · backlog 67–69 · BE live on VPS.

**hero-x track CLOSED (37/37):** [COMPANION_HERO_X00_PO_SIGNOFF.md](./COMPANION_HERO_X00_PO_SIGNOFF.md) · clinical Appendix B/C · [COMPANION_HERO_X62_SMOKE.md](./COMPANION_HERO_X62_SMOKE.md).

**План hero-x:** [WELLNESS_HERO_PERSONA_ENHANCEMENT_PLAN.md](./WELLNESS_HERO_PERSONA_ENHANCEMENT_PLAN.md) v2 **✅ COMPLETE**.

---

## 4. Оставшиеся 13 задач — что делать и с чего начать

> **Порядок для PO/ML (рекомендуемый):** 0-01 → 2-06 → (TestFlight снова) → 1-04 по календарю → батч 7.

### r100-0-01 — TestFlight 15 пунктов (PO + device)

- **Чеклист:** [WELLNESS_TESTFLIGHT_SMOKE_15.md](./WELLNESS_TESTFLIGHT_SMOKE_15.md)
- **Билд:** **224** (hero-x UI: teen humor, one-pager, wisdom toggle l10n)
- **Автотесты:** `WellnessCompanionNavUITests`, `WellnessModelsTests`
- **Критерий done:** все 15 галочек на реальном iPhone

### r100-2-06 — Widget Extension (~15 мин, Xcode)

- **Инструкция:** [MANUAL_WIDGET_SETUP.md](../MANUAL_WIDGET_SETUP.md) + [WELLNESS_WIDGET_TARGET_CHECKLIST.md](./WELLNESS_WIDGET_TARGET_CHECKLIST.md)
- **Код готов:** `ALADDINWidgets/WellnessCheckinWidget.swift`, `WellnessWidgetBridge` после check-in
- **Критерий done:** виджет check-in на Home Screen, App Group

### r100-1-04 — Postgres read cutover

- **Когда:** ≥7 дней после `WELLNESS_PG_DUAL_WRITE=1` (старт ~2026-06-01)
- **Док:** [WELLNESS_POSTGRES_MIGRATION.md](./WELLNESS_POSTGRES_MIGRATION.md)
- **Действие:** `WELLNESS_PG_READ=1` на VPS + smoke + verify 14/14
- **Не делать раньше срока**

### r100-0-03 / r100-0-04 — Hermes + Parent LLM

- **Док:** [WELLNESS_POSTGRES_PARENT_LLM_HANDOFF.md](./WELLNESS_POSTGRES_PARENT_LLM_HANDOFF.md)
- **PO:** ключи OpenRouter/Hermes на VPS
- **Проверка:** `curl` parent playbook → `llm_used: true`

### r100-4-voice — Latency polish

- **Файлы:** `CompanionVoiceSession.swift`, STT/TTS pipeline
- **Цель:** субъективно быстрее STT→LLM→TTS на device

### r100-5-ethics — QA audit

- L3 escalation → helpline без шуток героя
- Родитель **не** видит дословный teen-chat
- Связано с пунктами 12–14 TestFlight smoke

### r100-6-store — App Store metadata

- Скриншоты, описание, privacy nutrition labels
- Wellness + Companion в одном listing

### r100-6-healthkit — HealthKit PO

- **A:** Portal profile + entitlement (sleep read)
- **B:** оставить rollback build 222-style без entitlement (текущий 223)
- **Док:** [WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md](./WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md)

### r100-7-07 — Rive анимации

- `.riv` assets + `WellnessPillarEmotionView` binding

### r100-7-08 — Sleep CDN

- MP3 URLs для sleep stories API + iOS player

### r100-7-10 — Clinical sign-off

- ✅ **completed** hero-x-30 (2026-06-04): все 4 pack `status: approved`
- **Док:** [WELLNESS_CLINICAL_REVIEW.md](./WELLNESS_CLINICAL_REVIEW.md) Appendix C

### r100-7-docs — Внутренние docs

- Заменить оставшиеся «столп» → «дорожка» в docs (не в UI — UI уже ok)

---

## 5. Деплой backend (VPS) — актуальный чеклист

| Шаг | Статус | Команда / проверка |
|-----|--------|-------------------|
| Full wellness P1 | ✅ исторически | `./scripts/deploy_wellness_p1.sh root 149.154.65.180 ~/.ssh/aladdin_server` |
| Batch 4 (packs, age, jwt) | ✅ 2026-06-03 | `./scripts/deploy_wellness_batch4.sh …` |
| Companion P0 (taglines) | ✅ 2026-06-03 | `./scripts/deploy_companion_p0.sh …` |
| **Hero-x phase 6** | ✅ 2026-06-04 | `./scripts/deploy_hero_x_phase6.sh …` |
| Prod wellness verify | ✅ 14/14 | `./scripts/verify_wellness_prod.sh https://aladdin-ai.ru` |
| Prod companion verify | ✅ 18/18 | `./scripts/verify_companion_p0_prod.sh https://aladdin-ai.ru` |
| Hero-x local gate | ✅ | `./scripts/verify_hero_x_phase6.sh` (129 pytest) |
| Hero-x-62 backend smoke | ✅ | `./scripts/verify_hero_x62_backend_smoke.sh` |
| Reflective verify | ✅ | `./scripts/verify_wellness_reflective_prod.sh` |
| vps_smoke_wellness.py | ✅ | ALL PASSED |
| Feature flags | ✅ | `ENABLED=1`, `ORCHESTRATOR=1`, `REFLECTIVE=1`, `JUNG=1` |
| l10n gate | ✅ | `python3 scripts/check_wellness_l10n.py` — **303 keys** |
| Backend pytest | ✅ | **129** companion + wellness (`Tests/test_companion_*.py`, `test_wellness_*.py`) |

**После каждого BE-изменения:** deploy → verify 14/14 → обновить дату в этом файле.

---

## 6. iOS — сверка Wellness*.swift ↔ таргет ALADDIN

**Main app:** **25/25** wellness Swift в Compile Sources.  
**Вне таргета:** `ALADDINWidgets/WellnessCheckinWidget.swift` → **r100-2-06**.

| Companion (r100, не в таблице Wellness*) | Файл |
|------------------------------------------|------|
| Чат, recap, memory, voice | `Screens/CompanionConversationScreen.swift` |
| 4 вкладки | `Screens/CompanionHomeScreen.swift` |
| Выбор героя | `Screens/CompanionHubScreen.swift` |
| Голос WS | `Core/Voice/CompanionVoiceSession.swift` |
| Premium gate | `Core/Services/WellnessPremiumFunnel.swift` |

Полная таблица 25 файлов — без изменений с 2026-06-02 (см. git history этого файла).

---

## 7. Ключевые файлы для правок героев

| Слой | Файл |
|------|------|
| BE чат | `security/api/routers/ai_companion_router.py` |
| BE wellness | `security/api/routers/wellness_router.py` |
| Persona | `security/services/ai_platform/companion_persona.py` |
| Оркестратор | `security/services/ai_platform/wellness_orchestrator.py` |
| Промпты | `security/services/ai_platform/wellness_prompt_builder.py` |
| Knowledge Pack | `security/services/ai_platform/wellness_knowledge/*/v1/pack.yaml` |
| Age band | `security/services/ai_platform/wellness_age_policy.py` |
| iOS чат | `Screens/CompanionConversationScreen.swift` |
| iOS Hub | `Screens/WellnessHubScreen.swift` |
| iOS session | `Core/Services/WellnessSessionStore.swift` |

---

## 8. Команды (копировать)

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Статика iOS (быстро, без xcodebuild)
./scripts/verify_r100_ios_static.sh

# Backend
python3 scripts/check_wellness_l10n.py
PYTHONPATH=. python3 -m pytest Tests/test_wellness_*.py -q
PYTHONPATH=. python3 -m pytest Tests/test_wellness_age_policy_device_auth.py -q

# r100 runner
./scripts/run_wellness_r100_tests.sh backend   # | static | ios-unit | all

# Prod (после deploy)
./scripts/verify_wellness_prod.sh https://aladdin-ai.ru
./scripts/verify_wellness_reflective_prod.sh
./scripts/wellness_ops_digest.sh https://aladdin-ai.ru root 149.154.65.180 ~/.ssh/aladdin_server

# Hero-x final CI (2026-06-04)
./scripts/verify_hero_x_phase6.sh
./scripts/verify_hero_x62_backend_smoke.sh https://aladdin-ai.ru
./scripts/verify_companion_p0_prod.sh https://aladdin-ai.ru

# Deploy (когда PO разрешил)
./scripts/deploy_wellness_batch4.sh root 149.154.65.180 ~/.ssh/aladdin_server
./scripts/deploy_companion_p0.sh root 149.154.65.180 ~/.ssh/aladdin_server
./scripts/deploy_hero_x_phase6.sh root 149.154.65.180 ~/.ssh/aladdin_server
```

---

## 9. Индекс документов

| # | Файл | Зачем |
|---|------|--------|
| 1 | **WELLNESS_IMPLEMENTATION_STATUS.md** | **Этот файл — старт** |
| 2 | WELLNESS_ML_HANDOFF_R100.md | Продукт героев, §0 для чата |
| 3 | WELLNESS_ROADMAP_100.md | Батчи 0–7 |
| 4 | WELLNESS_DEPLOY_BACKLOG.md | Один деплой |
| 5 | WELLNESS_CURSOR_TODO.md | 131 ☑ справочник |
| 6 | WELLNESS_PLATFORM_MASTER_PLAN.md | Архитектура v2.5 |
| 7 | WELLNESS_TESTFLIGHT_SMOKE_15.md | r100-0-01 |
| 8 | WELLNESS_PREMIUM_FUNNEL.md | r100-1-16 |
| 9 | WELLNESS_POSTGRES_MIGRATION.md | r100-1-04 |
| 10 | WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md | r100-6-healthkit |
| 11 | MANUAL_WIDGET_SETUP.md | r100-2-06 |
| 12 | ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md | VPS SSH |
| 13 | **WELLNESS_HERO_PERSONA_ENHANCEMENT_PLAN.md** v2 | **hero-x-* (37):** юмор balance, vedic secular, psychology, guard, golden set |

---

## 10. История сессий (хронология)

| Дата | Событие |
|------|---------|
| 2026-06-01 | Ядро **131/131** closed; prod verify 14/14; Postgres dual-write |
| 2026-06-02 | iOS 15.2 shims; HealthKit CI blocker → rollback B; Wellness*.swift audit |
| 2026-06-03 | r100 батчи 3–5; build **223**; deploy batch4+companion; push `f9e65234` |
| 2026-06-04 | **hero-x 37/37** complete; social bridge 18/18; packs approved; build **224**; final CI green; push master |

---

*Финальная редакция 2026-06-04. hero-x CLOSED. Ядро 131 не reopen.*
