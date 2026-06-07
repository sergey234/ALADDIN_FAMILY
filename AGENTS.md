# ALADDIN iOS — руководство для AI/ML агентов

Рабочий корень (единственный):

`/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`

Перед любыми правками:

1. `git rev-parse --show-toplevel` — должен совпадать с путём выше
2. `git branch --show-current`
3. `git status --short`

---

## Как пользоваться (авто vs вручную)

### Работает автоматически (ничего не нажимать)

| Что | Когда срабатывает |
|-----|-------------------|
| **`aladdin-principal-ios-architect.mdc`** | Каждый чат в этом репо — роль principal iOS + UX/архитектура |
| **`ios-working-root.mdc`** | Напоминает правильный корень репозитория |
| **Hooks** (`hooks.json`) | Старт чата → ветка и прошлый summary; конец → сохранение в `.cursor/session/`; предупреждения при `.env` и секретах в промпте |
| **`.cursorignore`** | Cursor не индексирует 35k backup-файлов — быстрый поиск |
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
| Любая iOS-работа | Rules `aladdin-principal-ios-architect.mdc` + `ios-working-root.mdc` |
| Parental bypass, anti-mock API | Rule `prod-no-mock-bypass.mdc` + skill `security-review` + agent `security-reviewer` |
| Изменения `.swift` | Rules `swift-*.mdc` + agent `swift-reviewer` |
| Ошибки сборки Xcode | Agent `swift-build-resolver` или `build-error-resolver` |
| Деплой backend `149.154.65.180` | Rule `aladdin-server-connection.mdc` + `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md` |
| Деплой Telegram-бота | Rule `telegram-shop-bot-deploy.mdc` — **не** в iOS-коммиты (`no-telegram-bot-in-ios-release.mdc`) |
| Figma ↔ iOS онбординг | Rules `figma-mcp-onboarding-main.mdc`, `onboarding-figma-ios-sync-mandatory.mdc` + skill `figma-use` (prerequisite) |
| Перед релизом / merge | Skill `verification-loop` + smoke на сервере |
| Security audit `.cursor/` | `npx ecc-agentshield scan -p .cursor --supply-chain` |
| Чистый бэкап iOS | `./scripts/create_clean_mobile_backup.sh` + rule `aladdin-clean-backup.mdc` |
| Бэкап бота (отдельно) | `./scripts/create_telegram_bot_backup.sh` |

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
