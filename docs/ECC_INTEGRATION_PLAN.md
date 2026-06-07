# План интеграции ECC в ALADDIN iOS

> Репозиторий ECC: https://github.com/affaan-m/ECC  
> Рабочий корень: `ALADDIN_iOS`  
> Конфиг установки: `ecc-install.json`  
> Игнор для агентов: `.cursorignore`

## Цель

Взять из ECC только то, что делает ALADDIN **надёжнее** (безопасность, тесты, anti-mock), **функциональнее** (агенты для Swift/Python) и **удобнее в разработке** (память сессий, quality gates) — без захламления 10+ языками и маркетинговыми skills.

## Что НЕ ставим

- DeFi, crypto, NestJS, investor-outreach, article-writing
- Правила для Java/Kotlin/Go (если не трогаем эти стеки)
- Полный профиль `full` (229+ операций копирования)
- Перезапись доменных `.mdc`: `prod-no-mock-bypass`, Figma, server-connection, telegram-deploy

## Батчи (порядок работ)

| Батч | Название | Результат |
|------|----------|-----------|
| 0 | Скорость агентов | `.cursorignore` — поиск без 35k backup-файлов |
| 1 | База ECC | Клон ECC + dry-run `install-plan` + `ecc-install.json` |
| 2 | Swift-качество | Правила Swift + агенты `swift-reviewer`, `swift-build-resolver` |
| 3 | Безопасность | `security-review`, AgentShield, усиление anti-mock |
| 4 | **Только `verification-loop`** | Чеклист перед релизом; `council` / `santa-method` — только крупные релизы, не каждый коммит |
| 5 | ✅ Память сессий | `hooks.json` + `aladdin-session-start/stop` → `.cursor/session/last-summary.md` |
| 6 | ✅ Telegram-бот | Skill `aladdin-telegram-bot-ops` + pytest subset 31 passed |
| 7 | **Только аудит `mcp.json`** | AgentShield/ручной разбор; `mcp-server-patterns` — когда добавим 2+ MCP |
| 8 | ✅ Instincts | 6 skills: no-mock, server-deploy, bot-ops, figma-sync, ios-release, clean-backup |

## Установка (батчи 1–3 — curated, июнь 2026)

Официальный `profile minimal` тянет **212+ файлов** (golang/java/php rules). Для ALADDIN используем **curated install**:

```bash
git clone --depth 1 https://github.com/affaan-m/ECC.git /tmp/ECC
cd /tmp/ECC && npm install --no-audit --no-fund

cd /path/to/ALADDIN_iOS
# Dry-run
./scripts/apply_ecc_aladdin_curated.sh --dry-run
# Apply (не трогает aladdin-*.mdc, prod-no-mock, figma-*)
./scripts/apply_ecc_aladdin_curated.sh

# Официальный plan (справочно, 212 ops — не apply без фильтра)
node /tmp/ECC/scripts/install-plan.js --config ecc-install.json

npx ecc-agentshield scan .cursor
```

Откат: `BACKUPS/.cursor_pre_ecc_<timestamp>/`

## Конфликты rules — как решать

| Файл ALADDIN | Действие |
|--------------|----------|
| `prod-no-mock-bypass.mdc` | **Оставить**, приоритет выше `common-security` |
| `ios-working-root.mdc` | **Оставить** |
| `aladdin-server-connection.mdc` | **Оставить** |
| `figma-*.mdc`, `companion-*.mdc` | **Оставить** |
| `common-git-workflow.mdc` (ECC) | **Не ставить** или отключить — конфликт с вашим git-протоколом |
| `swift-*.mdc` (ECC) | **Merge** — дополняют, не заменяют |

## Критерии готовности (Definition of Done) — июнь 2026

- [x] Доменные `.mdc` не перезаписаны (13 ALADDIN + 7 ECC swift/common)
- [x] `npx ecc-agentshield scan -p .cursor` — **0 critical** (grade B)
- [x] `.cursorignore` — ускорение поиска
- [x] `AGENTS.md` — карта задач
- [x] ALADDIN instincts skills (батч 8)
- [x] `aladdin-telegram-bot-ops` + bot pytest subset
- [ ] Полный smoke на сервере (`tools/smoke_plan_cards_driving_ai.py`) — по запросу перед релизом

### Батчи 4 и 7 — урезанный scope (зафиксировано)

- **4:** только `verification-loop` (без council/santa/e2e-testing)
- **7:** только аудит `mcp.json` (без `mcp-server-patterns`)
