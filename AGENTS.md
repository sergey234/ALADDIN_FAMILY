# ALADDIN iOS — руководство для AI/ML агентов

**Единая точка входа для другой ML-системы (роутер + дорожная карта):**  
[`docs/ML_SYSTEM_START_HERE.md`](docs/ML_SYSTEM_START_HERE.md) — открыть **первым** (§0A **Mech Pilot**), дальше по таблице маршрутов.  
**Business / метрики / рост:** [`docs/business/ML_SYSTEM_BUSINESS_START_HERE.md`](docs/business/ML_SYSTEM_BUSINESS_START_HERE.md).  
**Mech Pilot:** rule `.cursor/rules/mech-pilot.mdc` · skill `@aladdin-mech-pilot` · GATES `@aladdin-gates`.  
**Pilot stack / Bonsai draft:** [`docs/ML_SYSTEM_LOCAL_LLM_BONSAI_PILOT.md`](docs/ML_SYSTEM_LOCAL_LLM_BONSAI_PILOT.md) · `@aladdin-local-llm` · START_HERE §0B.  
**Tailscale admin (не продукт):** [`docs/ADMIN_MESH_TAILSCALE_HYBRID_PLAN_2026-07-27.md`](docs/ADMIN_MESH_TAILSCALE_HYBRID_PLAN_2026-07-27.md).

Рабочий корень (единственный):

`/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`

Перед любыми правками:

1. `git rev-parse --show-toplevel` — должен совпадать с путём выше
2. `git branch --show-current`
3. `git status --short`

---

## CRITICAL — VPN secrets handoff (never push)

**Файл:** `aladdin_shop_vpn_api/deploy/VPN_SPEED_DEGRADATION_HANDOFF_RU.md`  
В нём **§32 FULL SECRETS VAULT** (ключи WG, токены бота, env, Xray, vpn.db).

| Запрещено | Разрешено |
|-----------|-----------|
| `git add` / `commit` / `push` этого файла | Хранить только локально |
| Вставлять §32 / секреты в GitHub, чат, PR | Пользоваться `~/ALADDIN_VPN_SAFE/*.tar.enc` |
| Ослаблять `.gitignore` на этот файл | Читать handoff локально для restore |

Cursor rule (alwaysApply): `.cursor/rules/vpn-handoff-secrets-never-push.mdc`

---

## Как пользоваться (авто vs вручную)

### Работает автоматически (ничего не нажимать)

| Что | Когда срабатывает |
|-----|-------------------|
| **`aladdin-principal-ios-architect.mdc`** | Каждый чат в этом репо — роль principal iOS + UX/архитектура |
| **`mech-pilot.mdc`** | Пилот (владелец) vs меха (агент): GATES → evidence → human Approve |
| **`ios-working-root.mdc`** | Напоминает правильный корень репозитория |
| **`vpn-handoff-secrets-never-push.mdc`** | **Всегда:** не пушить/не вставлять `VPN_SPEED_DEGRADATION_HANDOFF_RU.md` (§32 secrets) |
| **`common-security.mdc`** | Security checks + запрет push VPN secrets handoff |
| **Hooks** (`hooks.json`) | Старт чата → ветка и прошлый summary; конец → сохранение в `.cursor/session/`; предупреждения при `.env` и секретах в промпте |
| **`.cursorignore`** | Cursor не индексирует 35k backup-файлов — быстрый поиск |
| **Repowise MCP** (self-host, free) | Два slim-индекса: **`repowise-bot`** → `../aladdin_repowise_index` (Stars/VPN/Premium); **`repowise-ios`** → `../aladdin_repowise_ios` (Core/Screens/…). CLI: `.venv-repowise/bin/repowise`. Rule: `repowise-first.mdc`. После commit — фоновый `update` обоих. |
| **Skills с хорошим `description`** | Cursor может сам подключить skill по смыслу задачи (bypass, Figma, бот) |

### Подключать явно (когда нужно усилить)

| Действие | Как |
|----------|-----|
| Code review Swift | В чате: «используй `swift-reviewer`» или `@swift-reviewer` |
| Перед релизом | «пройди `verification-loop`» |
| Деплой сервера | «по `aladdin-server-deploy`» |
| Security audit | `npx ecc-agentshield scan -p .cursor --supply-chain` |
| Бэкап | `./scripts/create_clean_mobile_backup.sh` |

### Правила по темам (когда задача узкая)

Rules с `alwaysApply: false` (Figma, bypass, bot, companion) — Cursor подхватывает по **описанию задачи** или если упомянуть: «по правилу prod-no-mock-bypass».

### Новый чат

Открой папку **`ALADDIN_iOS`** как workspace root — тогда все rules и hooks активны. Можно писать задачу простым языком; роль principal уже в контексте.

---

## Карта: задача → skill / agent / rule

| Задача | Что использовать |
|--------|------------------|
| Навигация бот Stars/Premium/VPN | MCP **`repowise-bot`**: `get_overview`/`get_context`/`get_risk` |
| Навигация iOS (Core/Screens/VPN UI) | MCP **`repowise-ios`**: то же для Swift-слоёв (без полного 25GB дерева) |
| Любая iOS-работа | Rules `aladdin-principal-ios-architect.mdc` + `ios-working-root.mdc` + **`mech-pilot.mdc`** |
| Постановка задачи агенту / «пилот» | Skill **`aladdin-mech-pilot`** + `aladdin-gates` + START_HERE §0A |
| Local LLM / Bonsai (draft only) | Skill **`aladdin-local-llm`** + `docs/ML_SYSTEM_LOCAL_LLM_BONSAI_PILOT.md` · START_HERE §0B |
| Карта кода (граф) | **Repowise** MCP · не orch GraftQueue · не trailhq Graft без ROI-GO |
| Tailscale admin mesh | `docs/ADMIN_MESH_TAILSCALE_HYBRID_PLAN_2026-07-27.md` · не закрывать VPN/HTTPS порты |
| Parental bypass, anti-mock API | Rule `prod-no-mock-bypass.mdc` + skill `security-review` + agent `security-reviewer` |
| Изменения `.swift` | Rules `swift-*.mdc` + agent `swift-reviewer` |
| Ошибки сборки Xcode | Agent `swift-build-resolver` или `build-error-resolver` |
| Деплой backend `149.154.65.180` | Rule `aladdin-server-connection.mdc` + `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md` |
| **SFM статус (перед любым отчётом о SFM)** | **`docs/SFM_ML_QUICKSTART.md`** → `docs/server/sfm_truth_check.sh` · спека: `docs/SFM_SINGLE_SOURCE_OF_TRUTH.md` |
| Security 100% / 138 / antifake | **`ML_SYSTEM_HANDOFF_SECURITY_100_PERCENT.md`** + `.cursor/IMPLEMENTATION_BATCHES_TODO.md` |
| Деплой Telegram-бота | **`telegram-shop-bot-deploy-safe.mdc`** (канон) · `telegram-shop-bot-deploy.mdc` = redirect · Contabo: `shop-ops deploy verify\|payment-patch\|full` · **не** FINAL §2 Variant A (DEPRECATED) · Mac: `aladdin-contabo` · **не** в iOS-коммиты |
| **Бот молчит на `/start` (Telegram soft-block)** | **`telegram_stars_shop_bot/docs/ML_SYSTEM_HANDOFF_TELEGRAM_BOTAPI_SOFTBLOCK.md`** · VPN playbook **§15.8** · rule `telegram-bot-api-softblock.mdc` · на Contabo `shared/ml/` |
| **Оплата LAVA СБП/карта (H2H ↔ classic)** | **`telegram_stars_shop_bot/docs/ML_SYSTEM_HANDOFF_PAYMENTS_LAVA_H2H_CLASSIC_2026-08-17.md`** · VPN playbook **§17** · rule `lava-h2h-classic-switch.mdc` |
| **VPN — архитектура + карта всех MD (канон #1)** | **`aladdin_shop_vpn_api/deploy/VPN_RU_ENTRY_CLONE_AND_SCALE_PLAYBOOK_RU.md` §0.3** · сейф `~/ALADDIN_VPN_SAFE/ENTRY_CLONE_KIT/README.md` · SSH **#3** `…/SERVERS_ACCESS_CANON.md` · глушилки **#2** Dendi + three-way |
| **Глушилки — Dendi + Frosty + Aim (three-way, серверы, rollout)** | **`aladdin_shop_vpn_api/deploy/VPN_JAMMING_THREE_WAY_DENDI_FROSTY_AIMONKEY_2026-08-26.md`** · Dendi: `…/VPN_JAMMING_DENDI_VS_AIMONKEY_…2026-08-20.md` · registry `.cursor/VPN_JAMMING_TASK_REGISTRY.md` · **P9 REG:** `…/ML_SYSTEM_HANDOFF_P9_REG_RU_LTE_NIGHT_2026-08-29.md` · rule `vpn-jamming-dendi-todo-ssot.mdc` |
| **Инцидент deploy 2026-08-19 (LAVA + restore витрины)** | **`telegram_stars_shop_bot/docs/ML_SYSTEM_HANDOFF_INCIDENT_2026-08-19_LAVA_DEPLOY_RESTORE.md`** · rule `telegram-shop-bot-deploy-safe.mdc` |
| Figma ↔ iOS онбординг | Rules `figma-mcp-onboarding-main.mdc`, `onboarding-figma-ios-sync-mandatory.mdc` + skill `figma-use` (prerequisite) |
| Перед релизом / merge | Skill `verification-loop` + smoke на сервере |
| Security audit `.cursor/` | `npx ecc-agentshield scan -p .cursor --supply-chain` |
| Чистый бэкап iOS | `./scripts/create_clean_mobile_backup.sh` + rule `aladdin-clean-backup.mdc` |
| Бэкап бота (отдельно) | `./scripts/create_telegram_bot_backup.sh` |
| **DeepSeek Flash / Codex `/goal`** (API drift, contract tests, bot triage) | **`docs/PLAN_DEEPSEEK_FLASH_GOAL_PIPELINE_2026-08-02.md`** · JWT SSOT · `smart_api_tester.py` · Cursor TODO `ds-p0-*` / `ds-p1-*` |
| **`/goal` guardrails (конец задачи)** | **`docs/GOAL_GUARDRAILS_CHECKLIST.md`** — VPN§32 · bot∉iOS · no mock bypass |
| **Deer / docs-only `/goal` sink** | **`tools/deer-flow-sandbox/`** + `DENY.yaml` · `assert_deer_safe.py` |
| **Assistant write-tools** | Design only: `telegram_stars_shop_bot/docs/DESIGN_ASSISTANT_WRITE_TOOLS_2026-08-02.md` — **не ship** |
| **Weekly web hygiene (Nuclei + ZAP)** | `docs/security/web/ZAP_NUCLEI_RUNBOOK_RU.md` · `./scripts/security/web/run_weekly_web_hygiene.sh` · reports in `docs/security/web/reports/` |
| **OpenAPI snapshot / drift** | `python3 scripts/openapi_snapshot_diff.py` → `docs/openapi-snapshots/` |

**Отложено (не вызывать по умолчанию):** `council`, `santa-method`, `mcp-server-patterns`.

### ALADDIN instincts (батч 8)

| Skill | Когда |
|-------|-------|
| `aladdin-no-mock-bypass` | bypass, parental, family API |
| `aladdin-server-deploy` | SSH, деплой `/opt/aladdin-backend` |
| `aladdin-telegram-bot-ops` | бот Stars/Premium/VPN |
| `aladdin-figma-ios-sync` | синхронизация OB_* Figma ↔ iOS |
| `aladdin-ios-release` | релизный коммит iOS |
| `aladdin-clean-backup` | бэкап iOS и бота раздельно |
| `aladdin-principal-ios-architect` | базовая роль эксперта (дублирует always-on rule) |

Доменные `.mdc` остаются каноном; skills — быстрый вход для агента.

---

## ECC (установлено, curated)

Скрипт: `./scripts/apply_ecc_aladdin_curated.sh`  
Состояние: `.cursor/ecc-install-state.json`

### Skills (`.cursor/skills/`)

- `security-review`, `security-scan` — аудит безопасности
- `verification-loop` — чеклист перед релизом
- `tdd-workflow` — TDD-цикл
- `swiftui-patterns`, `swift-actor-persistence`, `swift-concurrency-6-2`, `swift-protocol-di-testing` — Swift/iOS

### Agents (`.cursor/agents/`)

- `swift-reviewer.md`, `swift-build-resolver.md`
- `security-reviewer.md`, `build-error-resolver.md`, `e2e-runner.md`

### Rules (добавлены ECC, не трогают доменные)

- `swift-*.mdc`, `common-security.mdc`, `common-testing.mdc`

### Доменные rules (приоритет выше ECC)

`prod-no-mock-bypass`, `aladdin-server-connection`, `figma-*`, `companion-*`, `no-telegram-bot-in-ios-release`, `aladdin-clean-backup`, `wellness-platform-expert`, `onboarding-ob03-figma-spec`

---

## Hooks (батч 5 — minimal)

Конфиг: `.cursor/hooks.json`

| Hook | Назначение |
|------|------------|
| `sessionStart` | Ветка, корень репо, прошлый summary из `.cursor/session/last-summary.md` |
| `stop` | Сохраняет ветку и `git status` в `last-summary.md` |
| `beforeReadFile` | Предупреждение при чтении `.env`, ключей |
| `beforeSubmitPrompt` | Предупреждение при секретах в промпте |

`last-summary.md` в `.gitignore` — локальная память между чатами.

---

## Три продукта в одном репо

| Продукт | Путь | Прод на сервере |
|---------|------|-----------------|
| **iOS app** | корень `ALADDIN_iOS` | — |
| **Backend API** | файлы в репо + `/opt/aladdin-backend` | `:8002` |
| **Telegram bot** | `telegram_stars_shop_bot/` | `/opt/aladdin-telegram-shop-bot`, Partner API `:8090` |

Бот и iOS **раздельные бэкапы и коммиты**.

---

## Onboarding (кратко)

При hero-иллюстрациях `OnboardingHero_00`…`07`:

- Не рефакторить `languageStepView` / `onboardingPage` без ТЗ
- QA: `docs/ONBOARDING_MASTER_IMPLEMENTATION_PLAN.md` §4.1
- Политика: `docs/ONBOARDING_MAIN_HERO_HANDOFF.md` §1.8, §8

---

## Откат ECC / hooks

Бэкап до ECC: `BACKUPS/.cursor_pre_ecc_20260607_132607/`
