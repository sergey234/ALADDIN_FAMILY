# Handoff для другой ML — Wellness + Companion «до 100%» (r100)

> **Дата handoff:** 2026-06-03  
> **Аудитория:** новая ML-система (Cursor / Claude / GPT) — **продолжение**, не старт с нуля.  
> **Рабочая папка (ТОЛЬКО):** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
> **Ядро wellness (старое):** **131/131** закрыто → [WELLNESS_CURSOR_TODO.md](./WELLNESS_CURSOR_TODO.md)  
> **Дорожная карта «100%» (новое):** [WELLNESS_ROADMAP_100.md](./WELLNESS_ROADMAP_100.md) — todo id **`r100-*`**  
> **Деплой (отложен PO):** [WELLNESS_DEPLOY_BACKLOG.md](./WELLNESS_DEPLOY_BACKLOG.md)

---

## 0. Сообщение для нового чата (скопировать целиком)

```text
Ты продолжаешь ALADDIN Wellness + Companion (герои), не начинаешь фазы 0–3 заново.

Рабочая папка ТОЛЬКО:
/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

Прочитай ОБЯЗАТЕЛЬНО в порядке:
1) docs/WELLNESS_ML_HANDOFF_R100.md (этот handoff — продукт, что сделано, r100 todo)
2) docs/WELLNESS_ROADMAP_100.md (план батчей 0–7, без canary)
3) docs/WELLNESS_IMPLEMENTATION_STATUS.md (131/131 + секции 2026-06-02 + таблица Wellness*.swift)
4) docs/WELLNESS_DEPLOY_BACKLOG.md (деплой ОДНИМ прогоном — пока НЕ делать без PO)
5) docs/WELLNESS_PLATFORM_MASTER_PLAN.md (архитектура v2.5)
6) docs/WELLNESS_CURSOR_TODO.md (131 задача — все completed, справочник)

Продуктовая цель (главное для PO):
- Три героя (Единорог, Аладдин, Джин) = ОДИН LLM + разные «костюмы» (persona + hero_flavor + дорожка wellness).
- НЕ fine-tune. «Обучение» = Knowledge Pack (pack.yaml) + промпты + метрики + правки текстов.
- Полноценный диалог друга в чате (Companion), не «дописывание фраз» в parent playbook.
- 4 дорожки самопомощи (cognitive / behavioral / humanistic / jung) — в UI «дорожка», не «столп».
- Parent playbook — отдельный продукт для родителя (готовые фразы), не чат ребёнка.

Жёсткие решения PO:
- Canary rollout ОТМЕНЁН (WELLNESS_CANARY_PERCENT=100).
- OpenRouter/Hermes keys + Rive + clinical sign-off — БАТЧ 7 (в конце), не блокер локальной работы.
- Деплой на VPS — после TestFlight/smoke, один прогон (см. DEPLOY_BACKLOG).

Сервер: root@149.154.65.180, /opt/aladdin-backend, ~/.ssh/aladdin_server
Prod: https://aladdin-ai.ru
После deploy: ./scripts/verify_wellness_prod.sh → 14/14

Сделай:
1) Подтверди понимание: 2 абзаца «что хотим от героев» + таблица 4 дорожек.
2) TodoWrite: импорт r100-* из §4 этого файла (статусы как указаны).
3) Продолжи с pending: r100-2-11 → r100-2-12 → r100-0-01/r100-0-05 → деплой по DEPLOY_BACKLOG.
4) Не коммить/push без запроса PO. Не включать WELLNESS_PG_READ до 7 дней dual-write.
```

---

## 1. Что мы хотим от героев (продукт)

### 1.1 Два разных продукта — не путать

| Продукт | Кто | API / UI | LLM |
|---------|-----|----------|-----|
| **Чат с героем** | Ребёнок / подросток / семья | `POST /api/ai/companion/chat`, `CompanionConversationScreen` | **Весь ответ** на каждое сообщение (Hermes/SFM + fallback) |
| **Parent playbook** | Родитель | `GET /api/wellness/parent/playbook` | Опционально **+2–3** фразы; основа — JSON `playbook_v1.json` (6 фраз) |
| **Wellness Hub** | Пользователь с consent | 4 дорожки, check-in, упражнения | Оркестратор выбирает дорожку; чат получает `wellness_pillar` |

### 1.2 Как устроен «герой» в коде

```
Сообщение пользователя
  → iOS: character_id + wellness_pillar (WellnessSessionStore)
  → BE: companion_persona (кто ты)
  → BE: wellness_prompt_builder + pack.yaml (дорожка, запреты, шаг упражнения, hero_flavor)
  → BE: история треда + Hermes/OpenRouter
  → BE: apply_response_guard (одна дорожка на ответ)
  → iOS: текст + эмоция + TTS
```

**Три героя** — не три модели. Одна модель, три тона (`hero_flavor` в каждом `pack.yaml`).

### 1.3 Что значит «100% герои» для PO

| Уровень | Критерий |
|---------|----------|
| Инженерия | Prod verify, PG cutover, CI, widget target, без canary |
| Герои | 4 pack с текстами (`draft` → clinical `approved`), flavor 3×4, recap/memory, drift, диалог на device OK |
| Продукт | TestFlight, доверие, App Store |

### 1.4 Что НЕ делаем

- Fine-tune / отдельная нейросеть на героя.
- Canary 5%→25%.
- Усиление parent playbook вместо качества **чата**.
- Диагноз, «терапия», школы (КПТ/Юнг) в UI и ответах LLM.
- Родитель видит дословный чат подростка.

---

## 2. Что уже было до r100 (канон — не переделывать)

| Блок | Статус | Документ |
|------|--------|----------|
| Backend wellness API | ✅ 131/131 | [WELLNESS_CURSOR_TODO.md](./WELLNESS_CURSOR_TODO.md) |
| iOS Wellness экраны | ✅ 25/25 в таргете ALADDIN | [WELLNESS_IMPLEMENTATION_STATUS.md](./WELLNESS_IMPLEMENTATION_STATUS.md) § «сверка Wellness*.swift» |
| Prod verify | ✅ 14/14 (скрипт может устареть по age policy — перепроверять) | `scripts/verify_wellness_prod.sh` |
| Postgres | dual-write ✅, read cutover ⏳ 7 дней | [WELLNESS_POSTGRES_MIGRATION.md](./WELLNESS_POSTGRES_MIGRATION.md) |
| Parent LLM flag | ✅ в .env, `llm_used: false` без валидного ключа | [WELLNESS_POSTGRES_PARENT_LLM_HANDOFF.md](./WELLNESS_POSTGRES_PARENT_LLM_HANDOFF.md) |

**Секции 2026-06-02 в IMPLEMENTATION_STATUS:** post-close iOS 15.2 shims, HealthKit CI blocker (rollback B), Ops VPS, **таблица Wellness*.swift ↔ target**.

---

## 3. Что сделали в сессии r100 (2026-06-03, в репо, деплой НЕТ)

> PO: **не деплоить** до закрытия нужного + TestFlight. Всё ниже — **локальный git**, часть только в рабочей копии.

### 3.1 UX / продукт (вне 131)

- 4 вкладки Companion («Мир героев»), «Мой мир», Hub skeleton, убран «столп» в i18n → «дорожка».
- Reflective → companion баннер/mic; age_band resolver; sprint3 deploy script (age + reflective i18n).

### 3.2 Батч 3 — герои UI

| id | Сделано |
|----|---------|
| r100-3-hero-* | Taglines: Единорог «Магический друг для детей», Аладдин «Мудрый наставник»; под героями только Игривый/Спокойный/Остроумный |
| r100-3-hero-deploy | Скрипт `deploy_companion_p0.sh` (на VPS — проверить PO) |

### 3.3 Батч 4 — «мозг» героев (без Hermes)

| id | Сделано |
|----|---------|
| r100-4-flavor | `hero_flavor` 3×4 во всех `wellness_knowledge/*/v1/pack.yaml` |
| r100-4-cog/beh/hum/jung | `instruction` + `llm_rephrase_only` на шагах упражнений; `llm_rules`; **status: draft** |
| r100-4-recap | Строка recap над чатом (`CompanionConversationScreen` + `/session/recap`) |
| r100-4-memory | Memory chips в чате (consent, не child); `GET /memory` |
| r100-4-drift | Лог `wellness_pillar_drift` в `ai_companion_router.py` |
| r100-4-outcome | `POST /outcomes` → `pillar_fatigue`; iOS переключает дорожку при «хуже» |

### 3.4 Батч 5 — «живой» чат

| id | Сделано |
|----|---------|
| r100-5-stream | Уже было: `sendText` → `streamMessage` (SSE) |
| r100-5-voice | WS ping 20s; reconnect UI «Повторить голосовой ответ»; fallback в текстовый чат; hold-to-talk polish |
| r100-5-proactive | После check-in → loop → баннер в чате с дорожкой |

### 3.5 Навигация / ops

| id | Сделано |
|----|---------|
| r100-2-13 | `finishWellnessFlow`, embedded Wellness в CompanionHome не выкидывает на Main |
| r100-1-15 | `scripts/wellness_ops_digest.sh` |
| r100-2-06 (частично) | `WellnessWidgetBridge` → App Group после check-in; **target виджета в Xcode — вручную** |

### 3.6 План / процесс

- [WELLNESS_ROADMAP_100.md](./WELLNESS_ROADMAP_100.md) — батчи 0–7, **Hermes перенесён в батч 7** с Rive.
- [WELLNESS_DEPLOY_BACKLOG.md](./WELLNESS_DEPLOY_BACKLOG.md) — очередь одного деплоя.
- Скрипт `scripts/deploy_wellness_batch4.sh`.

---

## 4. Полная таблица Todo `r100-*` (для TodoWrite)

Импортируй в Cursor с указанными статусами. **merge: true** при обновлении.

| id | Батч | Задача | Статус | Владелец |
|----|------|--------|--------|----------|
| r100-0-01 | 0 | TestFlight — 15 пунктов UX на device | **pending** | PO + iOS |
| r100-0-02 | 0 | verify_wellness_prod 14/14 после deploy | **pending** | BE ops |
| r100-0-03 | 7 | Hermes/OpenRouter keys (с Rive, **в конце**) | **pending** | PO key + BE |
| r100-0-04 | 7 | Parent LLM `llm_used: true` (после ключей) | **pending** | BE ops |
| r100-0-05 | 0 | Nav smoke: wellness→exercise→outcome→companion | **completed** | `WellnessCompanionNavUITests` + TestFlight §7–10 |
| r100-0-06 | 0 | Reflective prod verify | **completed** | — |
| r100-1-04 | 1 | PG read cutover после 7d dual-write | **pending** | BE ops |
| r100-1-15 | 1 | Мониторинг Hub/chat/drift (`wellness_ops_digest.sh`) | **completed** | DevOps |
| r100-1-16 | 1 | Premium воронка | **completed** | [WELLNESS_PREMIUM_FUNNEL.md](./WELLNESS_PREMIUM_FUNNEL.md) |
| r100-2-06 | 2 | Widget Extension target Xcode + MANUAL_WIDGET_SETUP | **pending** | iOS |
| r100-2-11 | 2 | WellnessModelsTests в CI (`ALADDINUnitTests`) | **completed** | iOS — pbxproj + ⌘U у PO |
| r100-2-12 | 2 | E2E UI Companion+Hub | **completed** | `WellnessCompanionNavUITests` в ALADDINUITests |
| r100-2-13 | 2 | Embedded nav `finishWellnessFlow` | **completed** | iOS |
| r100-2-14 | 2 | Glossary docs «дорожка»/pillar | **completed** | Docs |
| r100-3-hero-unicorn | 3 | Tagline Единорог | **completed** | BE+iOS |
| r100-3-hero-aladdin | 3 | Tagline Аладдин | **completed** | BE+iOS |
| r100-3-hero-genie | 3 | Tagline Джин | **completed** | — |
| r100-3-hero-style | 3 | Игривый/Спокойный/Остроумный | **completed** | iOS |
| r100-3-hero-deploy | 3 | deploy_companion_p0 taglines | **completed** | BE ops |
| r100-4-cog | 4 | Pack cognitive draft + instructions | **completed** | Content |
| r100-4-beh | 4 | Pack behavioral | **completed** | Content |
| r100-4-hum | 4 | Pack humanistic | **completed** | Content |
| r100-4-jung | 4 | Pack jung | **completed** | Content |
| r100-4-flavor | 4 | hero_flavor 3×4 | **completed** | Content |
| r100-4-recap | 4 | Recap над чатом | **completed** | iOS |
| r100-4-memory | 4 | Memory chips consent | **completed** | iOS |
| r100-4-drift | 4 | Drift log BE | **completed** | BE |
| r100-4-outcome | 4 | Outcome → fatigue/pillar iOS+BE | **completed** | iOS+BE |
| r100-4-voice | 4 | STT→LLM→TTS latency (частично в r100-5-voice) | **pending** | iOS |
| r100-5-stream | 5 | Streaming чат | **completed** | iOS+BE |
| r100-5-voice | 5 | Hold-to-talk + WS reconnect | **completed** | iOS |
| r100-5-proactive | 5 | Check-in → CTA герою | **completed** | iOS |
| r100-5-ethics | 5 | Не ослаблять L3; parent не видит teen chat | **pending** | QA audit |
| r100-6-store | 6 | App Store metadata | **pending** | PO |
| r100-6-healthkit | 6 | HealthKit PO (Portal A или B) | **pending** | PO |
| r100-7-07 | 7 | Rive `.riv` + PillarEmotion | **pending** | Design+iOS |
| r100-7-08 | 7 | Sleep CDN mp3 | **pending** | BE+iOS |
| r100-7-10 | 7 | Clinical → pack `approved` | **pending** | PO+внешний |
| r100-7-docs | 7 | Docs «столп»→«дорожка» | **pending** | Docs |

### 4.1 Рекомендуемый порядок работы

1. **r100-2-11** — убедиться `WellnessModelsTests.swift` в `ALADDINUnitTests` + CI green.  
2. **r100-2-12** или **r100-0-05** — сценарии навигации/Hub/Companion.  
3. **r100-2-06** — [WELLNESS_WIDGET_TARGET_CHECKLIST.md](./WELLNESS_WIDGET_TARGET_CHECKLIST.md) + [MANUAL_WIDGET_SETUP.md](../MANUAL_WIDGET_SETUP.md).  
4. **r100-0-01** TestFlight на device.  
5. **Деплой** — [WELLNESS_DEPLOY_BACKLOG.md](./WELLNESS_DEPLOY_BACKLOG.md).  
6. **r100-0-02** verify 14/14.  
7. Через 7 дней dual-write → **r100-1-04**.  
8. **Батч 7** — Rive, ключи Hermes, clinical.

---

## 5. Ключевые файлы (где править)

### 5.1 Companion / герои

| Файл | Роль |
|------|------|
| `security/api/routers/ai_companion_router.py` | Чат, stream, drift log, CHARACTERS taglines |
| `security/services/ai_platform/companion_persona.py` | Личность героя |
| `security/services/ai_platform/wellness_orchestrator.py` | Дорожка, loop, guard |
| `security/services/ai_platform/wellness_prompt_builder.py` | Prefix `[WELLNESS v1]` |
| `security/services/ai_platform/wellness_knowledge/*/v1/pack.yaml` | Knowledge Pack + hero_flavor |
| `Core/Voice/CompanionVoiceSession.swift` | WS голос |
| `Screens/CompanionConversationScreen.swift` | Чат, recap, memory chips, voice |
| `Screens/CompanionHomeScreen.swift` | 4 вкладки |
| `Screens/CompanionHubScreen.swift` | Выбор героя |
| `Core/Navigation/NavigationManager.swift` | `finishWellnessFlow`, companion return |

### 5.2 Wellness

| Файл | Роль |
|------|------|
| `security/api/routers/wellness_router.py` | REST, outcomes + fatigue |
| `Screens/WellnessHubScreen.swift` | Hub, embedded nav |
| `Screens/WellnessOutcomeSheet.swift` | «легче/хуже» → API |
| `Screens/WellnessCheckinScreen.swift` | Check-in + widget bridge |
| `Core/Services/WellnessSessionStore.swift` | pillar, consent, `WellnessWidgetBridge` |

---

## 6. Полный список документов (индекс «100%»)

### 6.1 Обязательные для старта

| # | Файл | Зачем |
|---|------|--------|
| 1 | **WELLNESS_ML_HANDOFF_R100.md** | **Этот файл** — продолжение r100 |
| 2 | **WELLNESS_ROADMAP_100.md** | План батчей, «простыми словами» герои, r100 id |
| 3 | **WELLNESS_IMPLEMENTATION_STATUS.md** | 131/131, деплой, **2026-06-02**, **Wellness*.swift таблица** |
| 4 | **WELLNESS_DEPLOY_BACKLOG.md** | Один деплой когда PO скажет |
| 5 | **WELLNESS_CURSOR_TODO.md** | 131 задача p0–p18 (все ☑) |
| 6 | **WELLNESS_PLATFORM_MASTER_PLAN.md** | Архитектура v2.5, API, Knowledge Pack |

### 6.2 Ops / backend

| # | Файл |
|---|------|
| 7 | WELLNESS_POSTGRES_MIGRATION.md |
| 8 | WELLNESS_POSTGRES_PARENT_LLM_HANDOFF.md |
| 9 | WELLNESS_CANARY_RUNBOOK.md (справочно; **rollout не делаем**) |
| 10 | ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md |
| 11 | WELLNESS_CLINICAL_REVIEW.md |

### 6.3 iOS / QA / контент

| # | Файл |
|---|------|
| 12 | WELLNESS_I18N_CHECKLIST.md |
| 13 | WELLNESS_I18N_GLOSSARY.md |
| 14 | WELLNESS_WIDGET_TARGET_CHECKLIST.md |
| 15 | MANUAL_WIDGET_SETUP.md |
| 16 | WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md |
| 17 | WELLNESS_APPLE_HEALTHKIT_SETUP.md |

### 6.4 Companion (смежные)

| # | Файл |
|---|------|
| 18 | docs/COMPANION_ML_HANDOFF_FULL.md |
| 19 | docs/WELLNESS_ML_HANDOFF.md (старый handoff 131 — справочно) |
| 20 | docs/ADR-WELLNESS-PLATFORM.md |
| 21 | docs/WELLNESS_ESCALATION_LADDER.md |
| 22 | docs/WELLNESS_PLAN_FACT.md |

### 6.5 Cursor rules

| # | Путь |
|---|------|
| 23 | `.cursor/rules/wellness-platform-expert.mdc` |
| 24 | `.cursor/rules/prod-no-mock-bypass.mdc` (parental bypass) |

---

## 7. iOS — сверка `Wellness*.swift` (канон 2026-06-02 + дополнения 2026-06-03)

**Источник истины:** [WELLNESS_IMPLEMENTATION_STATUS.md](./WELLNESS_IMPLEMENTATION_STATUS.md) § «iOS — сверка Wellness*.swift».

| Итог | Значение |
|------|----------|
| Main app ALADDIN | **25/25** wellness Swift в Compile Sources |
| Вне таргета | `ALADDINWidgets/WellnessCheckinWidget.swift` (нужен Widget Extension — **r100-2-06**) |

**Companion-файлы (r100)** — не в таблице Wellness*, но критичны:

- `Screens/CompanionConversationScreen.swift`, `CompanionHomeScreen.swift`, `CompanionHubScreen.swift`
- `Core/Voice/CompanionVoiceSession.swift`, `UI/Companion/CompanionDialogueStrip.swift`

---

## 8. Тесты и команды

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# i18n
python3 scripts/check_wellness_l10n.py

# Backend wellness (ожидание ~110 passed)
PYTHONPATH=. python3 -m pytest Tests/test_wellness_*.py -q

# Pillar prompts
PYTHONPATH=. python3 -m pytest Tests/test_wellness_pillar_prompts.py -q

# Prod (после deploy)
./scripts/verify_wellness_prod.sh https://aladdin-ai.ru

# Ops digest
./scripts/wellness_ops_digest.sh https://aladdin-ai.ru root 149.154.65.180 ~/.ssh/aladdin_server
```

---

## 9. Деплой — напоминание (не выполнять без PO)

См. [WELLNESS_DEPLOY_BACKLOG.md](./WELLNESS_DEPLOY_BACKLOG.md):

- `./scripts/deploy_wellness_batch4.sh`
- `./scripts/deploy_companion_p0.sh`
- iOS TestFlight build
- verify 14/14

**Не в деплое сейчас:** OpenRouter, Rive, clinical `approved`.

---

## 10. «Уточнить тексты упражнений» — что это (для ML)

В `pack.yaml` для каждой дорожки:

- **hint** — текст шага для пользователя в Hub.
- **instruction** — что герой должен сказать на этом шаге (один вопрос, одна дорожка).
- **llm_rules** — общий тон сессии.

Статус **draft** до **r100-7-10** (clinical). Менять YAML ≠ обучать нейросеть.

---

*Handoff подготовлен после сессии Cursor 2026-06-03. Синхронизировать с WELLNESS_ROADMAP_100.md при изменении приоритетов PO.*
