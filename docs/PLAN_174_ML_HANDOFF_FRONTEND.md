# Handoff для ML: 174 закрытые задачи плана (фронт / клиент iOS)

**Сгенерировано:** 2026-04-25 (UTC) — **исторический снимок** (см. §0)  
**Канонический план-факт (чекбоксы):** `docs/EXECUTION_AND_LOCALIZATION_DASHBOARD.md`  
**Короткий список открытого:** `docs/CURSOR_CHAT_PENDING_CHECKLIST.md`  
**Машинные числа (Swift):** `Core/Planning/ImplementationPlanProgressValues.swift` (обновлять: `python3 scripts/update_dashboard_stats.py`)

---

## 0. Текущий факт vs этот документ (anti-drift)

- **На 2026-04-29** канонический дашборд показывает **178 / 178** закрытых задач плана (`docs/EXECUTION_AND_LOCALIZATION_DASHBOARD.md`).
- Этот файл сохраняет **тематический handoff**, снятый на момент, когда в дашборде было **174 / 178** — полезно как «что именно делали» и какие артефакты смотреть, но **не** как источник «сколько открыто сегодня».
- **Детский контент end-to-end (178 + 68 + 275):** `docs/CHILD_CONTENT_FINAL_SYSTEM_HANDOFF.md`

---

## 1. Цифры (что значит «174» в этом файле)

| Показатель | Значение |
|------------|----------|
| Всего задач в плане | **178** |
| **Выполнено на дату снимка (2026-04-25)** | **174** |
| **Осталось на дату снимка** | **4** (все в **Track B** / governance) |
| **Текущее состояние дашборда (2026-04-29)** | **178 / 178** (см. `docs/EXECUTION_AND_LOCALIZATION_DASHBOARD.md`) |
| Track A (core product) | **149 / 149** (100%) |
| Track B (governance / quality) | на снимке: **25 / 29** (~86%) — 4 открытые; **сейчас:** закрыто вместе с остальным планом |

**Важно для ML:** «174» здесь — это **счётчик закрытых пунктов** в `EXECUTION_AND_LOCALIZATION_DASHBOARD.md` *на дату генерации*, а не 174 отдельных **новых** URL бэкенда. Новые маршруты API — в **`/openapi.json`**, дельта между релизами — diff снимков.

---

## 2. Что вошло в закрытые 174: темы работ (весь «фронт» клиента)

Ниже — **сжатая карта**, чтобы другая система поняла *что делали*, без перечисления 174 строк.

### 2.1 Продуктовый и compliance-фундамент (Phase 0, Track A)

- MVP-рамка, **Must/Should/Could/Won’t**, DoD с **RU+EN** на UI.
- **Privacy / COPPA+GDPR рамка:** consent versioning, DSAR-направления (export/delete) в клиенте, политики — в т.ч. `ParentDashboardView` + `ProfileManager`.
- Разделение **Family Sharing** (системные покупки) и **in-app** семейного roster/профилей.

### 2.2 Контент (Phases 1–3, 7)

- **Стек:** `ContentManager`, `ContentDatabase`, `ContentSyncManager`, `ContentVersionManager`, `ContentCacheManager`, манифест/delta, валидация, оффлайн.
- **Модели:** `ContentItem`, категории, прогресс, метаданные.
- **Персонализация / прогресс:** трекинг, ачивки, streak, рекомендации, родительский **Parent dashboard** (обзор, лимиты, фильтры).

### 2.3 Медиа, анимация, VFX (Phases 4–6)

- `AudioManager`, `SoundEffectPlayer`, `AudioSettingsView`.
- `AnimatedButton`, `TransitionManager`, `CharacterSystem`, `ParticleSystem`, микро-интеракции / feedback.

### 2.4 Профили, семья, родительский контур (Phase 7)

- `ChildProfile`, `ProfileManager`, `FamilyAccessPolicy`, `ParentSessionGate` (PIN/биометрия, rate limit, secure storage).
- `FamilyViewModel` / `02_FamilyScreen` — критичные действия через **подтверждение взрослого**.
- Ветка **Device-level** parental (entitlements, Family Controls pipeline — по плану).

### 2.5 Тестирование, перф, security (Phase 8)

- Скрипты `phase8_*_smoke.py`, UX/устройства/безопасность/производительность; DSAR и parental в compliance-smoke.
- **Примечание:** стабилизация **`ALADDINUnitTests`** вынесена **post-plan** (после закрытия всех открытых пунктов плана) — не входит в 178 как отдельный «зелёный» критерий plan-fact.

### 2.6 60+ / детский конверджент, локализация (Phase 9 — почти всё)

- На дату снимка: **45 / 49** пунктов Phase 9 были закрыты (остаток пересекался с **Track B**).
- **Текущее состояние:** Phase 9 закрыт полностью в рамках **178 / 178** (см. `docs/EXECUTION_AND_LOCALIZATION_DASHBOARD.md`).

### 2.7 Governance / Track B (большей частью сделано)

- **Wave 2** lint-gate, KPI/runbook-артефакты, AES-256 gate, monthly log audit, и т.д. (см. `docs/TRACKB_*.md`, `scripts/trackb_*_smoke.py`).
- Реализован **independent acceptance gate:** `scripts/independent_acceptance_gate.py` + `docs/INDEPENDENT_SMOKE_SUITE_REPORT.md`.

### 2.8 Локализация (сквозняком по 174)

- Массовая замена **hardcoded** строк на `LocalizationManager` + ключи в `en`/`ru`.
- Инструмент: `scripts/localization_lint.py`; ongoing **Wave 1 Baseline** — в **открытых** задачах (см. §4).

### 2.9 Сборка Xcode / целостность таргета

- В `ALADDIN` target добавлены критичные файлы (в т.ч. `GamesParentalControlScreen`, `WelcomeCardForCreator`, `CrashDetectionSettingsModal`) — **сборка** `ALADDIN` для симулятора проходила после правок.

---

## 3. Как проверяли (артефакты для ML)

| Проверка | Где | Назначение |
|----------|-----|------------|
| Независимый gate (smoke) | `scripts/independent_acceptance_gate.py` → `docs/INDEPENDENT_SMOKE_SUITE_REPORT.md` | Репозиторий: Phase8/9 + TrackB smokes, **FAIL = fail** |
| OpenAPI method-aware | `scripts/openapi_conformant_audit.py` → `docs/OPENAPI_CONFORMANT_AUDIT_LATEST.*` | Соответствие **документированных** HTTP-операций прод-стенду; последний прогон: `2026-04-25T18:16:19Z` |
| API / JWT SSOT | `ALADDIN_JWT_API_ARCHITECTURE_COMPLETE.md` | Политика токенов, три уровня проверки, 5xx |
| Endpoint + health | `docs/ENDPOINT_CONTRACT_AND_SERVER_ACCESS.md` | Content contract, health, ссылки |
| План-факт | `docs/EXECUTION_AND_LOCALIZATION_DASHBOARD.md` | Единый чеклист 178 задач |

**HTTP по OpenAPI (последний срез):** 395 операций, **316** ответов не 404, **1** ответ **5xx** на `GET /api/gamification/rewards/history` — требует бэкенд-разбора; это **не** «всё идеально», см. JWT-док.

---

## 4. Что оставалось открытым на снимке 2026-04-25 (и почему это больше не «текущий факт»)

На дату генерации этого handoff в дашборде оставались **4** сквозных пункта **Track B** (baseline локализации, размер IPA, COPPA, обязательный родительский контроль как закрывающий чекбокс).

**Сейчас:** эти пункты закрыты в **`docs/EXECUTION_AND_LOCALIZATION_DASHBOARD.md` (178 / 178)**. Если вы видите расхождение между «174» в заголовке и дашбордом — читайте **§0**.

---

## 5. Что делать следующей ML-системе

1. Читать **чекбоксы** только в `EXECUTION_AND_LOCALIZATION_DASHBOARD.md` (источник истины по «сделано/не сделано»).
2. Для **кода** смотреть **репозиторий** (пути в §2), не только этот handoff.
3. Для **API** — не выводить «всё ОК» из чисел плана: смотреть **OpenAPI LATEST** + **ALADDIN_JWT** (5xx, 422).
4. После любых изменений плана — `update_dashboard_stats.py` и при необходимости новый **OpenAPI** прогон.

---

## 6. Связанные файлы (быстрый index)

- План: `NEXT_VERSION_IMPLEMENTATION_PLAN.md`
- RU объяснение HTTP-проверок: `docs/OPENAPI_HTTP_CHECKS_EXPLAINED_RU.md`
- Матрица plan→proof (если ведёте): `docs/PLAN_PROOF_MATRIX.json`
- Недельный Phase8/9 пак: `scripts/weekly_phase8_phase9_regression.py`
- **Полный перечень по этому workstream** — [§6.1](#61-где-лежат-остальные-артефакты-полный-index), [§7](#7-детский-контур-что-улучшили-именно-для-детей), [§8](#8-клиент-vs-сервер-риски-прод-критерий-работоспособности) (E2E / риски / 100%)

### 6.1 Где лежат остальные артефакты (полный index)

| Категория | Пути (репозиторий) |
|-----------|--------------------|
| **Handoff + чеклисты** | `docs/PLAN_174_ML_HANDOFF_FRONTEND.md` (этот файл), `docs/CURSOR_CHAT_PENDING_CHECKLIST.md`, `docs/EXECUTION_AND_LOCALIZATION_DASHBOARD.md` |
| **Независимые аудиты / gate** | `docs/INDEPENDENT_SMOKE_SUITE_REPORT.md`, `docs/INDEPENDENT_SMOKE_SUITE_REPORT.json`, `docs/INDEPENDENT_PLAN_FACT_AUDIT_174.md`, `docs/INDEPENDENT_XCODE_TARGET_MEMBERSHIP_AUDIT.md`, `scripts/independent_acceptance_gate.py` |
| **OpenAPI + JWT** | `scripts/openapi_conformant_audit.py`, `docs/OPENAPI_CONFORMANT_AUDIT_LATEST.md`, `docs/OPENAPI_CONFORMANT_AUDIT_LATEST.json`, `docs/OPENAPI_HTTP_CHECKS_EXPLAINED_RU.md`, `ALADDIN_JWT_API_ARCHITECTURE_COMPLETE.md` |
| **Контракт API / сервер** | `docs/ENDPOINT_CONTRACT_AND_SERVER_ACCESS.md` |
| **Track B (governance)** | `docs/TRACKB_*.md` (KPI, AES, localization gate, testflight, cross-audience, и др.), `scripts/trackb_*_smoke.py`, `scripts/localization_lint.py` |
| **Phase8 smokes** | `scripts/phase8_*_smoke.py` (compliance, content/device, offline sync, performance, security, UX) |
| **Phase9 smokes** | `scripts/phase9_*_smoke.py` (в т.ч. `phase9_access_rules`, `phase9_family_flow`, `phase9_unified_family_model`, `phase9_content_safety`, `phase9_data_integrity`, elderly-гейты) |
| **Регресс-лаунчер** | `scripts/weekly_phase8_phase9_regression.py` |
| **Локализация** | `docs/LOCALIZATION_*.md` (baseline, key map, standard, PR checklist), `Resources/Localization/en.lproj/Localizable.strings`, `ru.lproj/Localizable.strings` |
| **Контент (клиент)** | `Core/Content/**` (manager, DB, sync, cache, versions, seed, parent dashboard systems, gamification-пересечения по данным) |
| **Семья / дети / профили** | `Core/Profile/**` (`ChildProfile`, `ProfileManager`, policies, `ParentSessionGate`) |
| **Прогресс плана (Swift / генерация)** | `Core/Planning/ImplementationPlanProgressValues.swift`, `scripts/update_dashboard_stats.py` |

*Примечание.* Файлы с префиксом `PHASE8_*_VALIDATION.md` / `PHASE9_*_VALIDATION.md` в `docs/` — отчётные чек-листы фаз, не дубликат handoff.

---

## 7. Детский контур: что улучшили именно для детей

Сводка **по коду и плану** (не маркетинг): что даёт детскому сценарию.

### 7.1 Интерфейс и контент

- **Упрощённый детский экран** `Screens/08_ChildInterfaceScreen.swift`: крупные кнопки, возрастные вкладки (дошкольники / школа / тин / young adult), смена фона, приветствие, карта «время у экрана», интеграция с `ContentManager` при появлении (`runUnifiedLifecycle`).
- **Экран категорий** `Screens/ChildContentScreen.swift`: **персонализированная подача** через `ContentManager.loadPersonalizedContent(for:ageBand:)` (возрастная «полоса» согласована с `ChildInterfaceScreen.AgeGroup`), **прогресс** по элементам, градиенты и сценарии под возраст, **маскот/персонаж** с `CharacterEmotion` (эмоция и анимация), тематические зоны (игры, обучение, творчество, мультики, игрушки, рисование, песни, истории) с локализованными приветствиями и подсказками **a11y**.

### 7.2 Мотивация и игра

- **Награды / геймификация** на детской ветке: `ChildRewardsScreen`, модальные `RewardsModalView` / `RewardsQuickModal`, сценарии «колесо / единороги» (см. `UnicornUniverseView`, `WheelOfFortuneView`, `YoungDefenderView`) — часть **визуального и сценарного** слоя для ребёнка, не заменяющая серверные правила.
- **Родительский контроль игр** (настройка со стороны взрослого): `GamesParentalControlScreen` (в target сборки после правок `project.pbxproj`).

### 7.3 Семья, политика и данные

- **Профиль ребёнка в модели**: `ChildProfile` + `ProfileManager`, согласование **roster** (`ChildRosterReconcilePolicy`, тесты в `Tests/UnitTests/ChildRosterReconcilePolicyTests.swift`). Это **целостность** списка детей и их данных между локальным состоянием и сценариями семьи.
- **Доступ взрослого к критичным действиям**: `FamilyViewModel` / `02_FamilyScreen`, `ParentSessionGate` — сценарии, где **ребёнок не обходит** родительский слой.
- **Контент и безопасность (семейный мост)**: `FamilyContentSafetyBridge` и сид-данные/категории (см. `ContentSeedProvider`) — выравнивание категорий и **фильтрация по политике** для детей и других ролей в одном согласованном слое.

### 7.4 Аудио, анимация, доступность

- `AudioManager`, `SoundEffectPlayer`, `AudioSettingsView` — обратная связь и мягкая настройка звука; микро-анимации (`Core/Animation/**`, `Shared/Styles/MicroInteractionStyles`) — **меньше сухой UI** для детей при включённых эффектах, уважение `Reduce Motion` в экране контента.

### 7.5 Что **не** является «только детским»

- **Phase8/9 smokes** и **Track B** — сквозное качество (в т.ч. `phase9_access_rules` защищает **все** роли, не только child UI). **Локализация RU/EN** — на всём продукте, но детские ключи `child_*` в `Localizable.strings` напрямую влияют на детский UX.

*Итог.* Для детей усилены: **доступ к возрастному контенту**, **прогресс и персонализация**, **игрово-мотивационный** слой, **родительские ограничители** и **целостность** семейной модели — при сохранении общей архитектуры `ContentManager` + профили + политика доступа.

---

## 8. Клиент vs сервер, риски прод, критерий «работоспособности»

### 8.1 Где логика на устройстве, где на бэкенде

| Сценарий | Клиент (iOS) | Сервер |
|----------|----------------|--------|
| Детский UI, сиды, БД до первого sync | `ContentSeedProvider` → `ContentManager.bootstrapLocalContentIfNeeded`, выдача карточек | Необязателен для **показа** сидов; для **актуального** каталога — `GET /api/content/manifest` и `GET /api/content/delta` |
| Персонализация/ранжирование | `ContentRecommender`, `active_child_profile_server_id` в `UserDefaults` | ID ребёнка обычно приходит из auth/семьи; без id — деградация к обобщённому ранжированию |
| Награды: баланс / магазин | `ChildRewardsScreen`, `APIService` | `GET/POST` под `/api/gamification/...` |
| История операций (дети) | Вкладка «История» + `rewards_history` (мердж с сервером) | **Рекомендуемый** контракт: `GET /api/gamification/balance/history?userId=…` (см. `docs/API_DOCUMENTATION_NEW_ENDPOINTS.md`) |
| `GET /api/gamification/rewards/history` | Больше **не** единственный источник списка: при 5xx/пусто клиент уходит в **историю баланса** | Ошибка **500** на проде (см. `docs/OPENAPI_CONFORMANT_AUDIT_LATEST.json`) — **нужен фикс бэка** для полноценного «штатного» ответа по этому пути |

### 8.2 Что сделано в клиенте для «максимально рабочей» ветки (2026-04-25)

- **Исправлен URL** запроса истории операций: `AppConfig.Endpoint.gamificationBalanceHistory` = `"/api/gamification/balance/history"` (раньше ошибочно указывал на тот же path, что и баланс).
- **Устойчивый декод** `BalanceHistoryResponse` / `BalanceHistoryEntry` (корневой массив и объект, опциональные поля, поле `type` с бэка).
- **Экран `ChildRewardsScreen`:** после вызова `rewards/history` список для UI строится из **истории баланса** (с мерджем с локальным `rewards_history`), так что **пустой/500 на rewards/history** не оставляет ребёнка без ленты, если `balance/history` и локальный кэш дают данные.
- **Health** прод-API: `GET http://149.154.65.180:8002/api/health` → **200** (см. периодические прогонки и гайд подключения).

### 8.3 «100%» end-to-end и чекбоксы плана

- **100% продуктовой готовности по план-факту (клиентский чеклист 178):** на **2026-04-29** это **178 / 178** в `docs/EXECUTION_AND_LOCALIZATION_DASHBOARD.md` (исторически последние «хвосты» были в Track B — baseline локализации, размер IPA, COPPA, родительский контроль как закрывающий чекбокс).
- **100% по геймификации на бэке** = устранение **500** на `GET /api/gamification/rewards/history` (если бизнесу нужен именно этот маршрут) + повторный `scripts/openapi_conformant_audit.py` и обновление `docs/OPENAPI_CONFORMANT_AUDIT_LATEST.*`.
- **Релиз по детям:** клиент **готов** показывать контент и **устойчивую** историю кошелька при корректном `balance/history` и/или локальных данных; **go/no-go** на «жёсткий» прод снимайте по результатам smokes + прод-контрактам, не только по числу закрытых строк плана.

### 8.4 Сводка по детям (суть, одна таблица)

| Тема | Суть |
|------|------|
| Интерфейс | `ChildInterfaceScreen` — детский хаб, возраст, `ContentManager.runUnifiedLifecycle` |
| Контент | `ChildContentScreen` + локальная БД, sync, персонализация по `ContentAgeBand` / id |
| Награды | `ChildRewardsScreen` — баланс/магазин/история; история: **сервер (`balance/history`) + локальный мердж** |
| Родитель | `GamesParentalControlScreen`, `ParentSessionGate`, `02_FamilyScreen` |
| Безопасность категорий | `FamilyContentSafetyBridge`, сиды `ContentSeedProvider` |
| Медиа/UX | `Core/Animation/**`, `Audio*`, a11y на детских экранах |
