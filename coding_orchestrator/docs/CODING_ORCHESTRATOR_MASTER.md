# Coding Orchestrator — ЕДИНЫЙ МАСТЕР-ФАЙЛ (владелец + ML)

**Глобальный роутер всего репо:** [`docs/ML_SYSTEM_START_HERE.md`](../../docs/ML_SYSTEM_START_HERE.md).  
**Это один канонический документ по Orch.** Для задач оркестратора другой ML-системе достаточно начать отсюда.  
Остальные файлы — детали по ссылкам ниже; при конфликте приоритет у **этого файла** + registry задач.

| Поле | Значение |
|------|----------|
| **Дата** | 2026-09-19 (обновлено: UX Control Plane v2 + Launchpad) |
| **Статус плана** | **115 / 115 ✅** |
| **Проверки** | pytest 39 · `orch e2e` PASS · `orch chaos` PASS · `.app` в Launchpad |
| **Корень** | `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/coding_orchestrator/` |
| **Приложение Mac** | `~/Applications/Coding Orchestrator.app` |
| **SSOT задач** | [`.cursor/CODING_ORCHESTRATOR_TASK_REGISTRY.md`](../../.cursor/CODING_ORCHESTRATOR_TASK_REGISTRY.md) (`orch-*`) |
| **Asmadey / Cursor skills** | [`.cursor/ASMADY_SKILLS_TASK_REGISTRY.md`](../../.cursor/ASMADY_SKILLS_TASK_REGISTRY.md) (`asm-*`) — **не** в этом дереве orch |

---

## Asmadey / Cursor skills (кратко)

Внешние skills (github.com/Asmadey/skills) живут в **Cursor** (`.cursor/skills/aladdin-*`), не как каталог внутри `coding_orchestrator/`.

| Делать | Не делать |
|--------|-----------|
| Thin `aladdin-*` после sandbox + skillspector + GO | Vendoring всего Asmadey в `coding_orchestrator/` или iOS release |
| Короткие GATES в `firstmate/skills/orch-basics` | Dark Factory / auto-merge |
| Orch = runtime (ветки, Approve, night, Telegram) | Подмена ALADDIN rules чужой «конституцией» |

Песочница: `.cursor/skills_sandbox/`. Аудит: rule `external-skill-audit.mdc`.  
Deferred+GO: diy-mcp (`asm-50`), agent-reach (`asm-51`).  
Handoff другой ML: [`.cursor/ASMADY_SKILLS_ML_HANDOFF.md`](../../.cursor/ASMADY_SKILLS_ML_HANDOFF.md) · остатки: [`ASMADY_SKILLS_REMAINING_PLAN.md`](../../.cursor/ASMADY_SKILLS_REMAINING_PLAN.md).

---

## Оглавление

1. [Карта всех ссылок](#1-карта-всех-ссылок)
2. [Что это и зачем](#2-что-это-и-зачем)
3. [Жёсткие правила для ML](#3-жёсткие-правила-для-ml)
4. [Агенты, токены, подключение (просто)](#4-агенты-токены-подключение-просто)
5. [Как открыть на Mac (Launchpad)](#5-как-открыть-на-mac-launchpad)
6. [Куда нажимать в окне и menu bar](#6-куда-нажимать-в-окне-и-menu-bar)
7. [Русский язык задач](#7-русский-язык-задач)
8. [Telegram](#8-telegram)
9. [Ночь / утро](#9-ночь--утро)
10. [CLI и HTTP API](#10-cli-и-http-api)
11. [Профили](#11-профили)
12. [Архитектура](#12-архитектура)
13. [Карта файлов кода](#13-карта-файлов-кода)
14. [115 задач — план/факт](#14-115-задач--планфакт)
15. [UX Control Plane v2](#15-ux-control-plane-v2)
16. [Чеклист следующей ML-системы](#16-чеклист-следующей-ml-системы)
17. [Мини-шпаргалка каждый день](#17-мини-шпаргалка-каждый-день)
18. [Out of scope / честные границы](#18-out-of-scope--честные-границы)

---

## 1. Карта всех ссылок

### Для владельца (ежедневно)

| Документ | Зачем |
|----------|--------|
| **Этот файл** | Вся правда в одном месте |
| [`CONTROL_PANEL_RU.md`](CONTROL_PANEL_RU.md) | Короткая шпаргалка «куда кликать» |
| [`USER_GUIDE.md`](USER_GUIDE.md) | Краткий user guide |
| `~/Applications/Coding Orchestrator.app` | Иконка Launchpad |
| [`../scripts/orch_open.command`](../scripts/orch_open.command) | One-click → открыть `.app` |
| [`../scripts/install_launchpad_app.sh`](../scripts/install_launchpad_app.sh) | Установка/обновление в Launchpad |
| [`../Makefile`](../Makefile) | `make install-app` · `make open` · `make test` |

### Для ML-системы (канон)

| Документ | Зачем |
|----------|--------|
| [`.cursor/CODING_ORCHESTRATOR_TASK_REGISTRY.md`](../../.cursor/CODING_ORCHESTRATOR_TASK_REGISTRY.md) | SSOT 115 задач `orch-*` |
| [`.cursor/ASMADY_SKILLS_TASK_REGISTRY.md`](../../.cursor/ASMADY_SKILLS_TASK_REGISTRY.md) | Asmadey × Cursor `asm-*` (не dump в orch) |
| [`.cursor/rules/coding-orchestrator-todo-ssot.mdc`](../../.cursor/rules/coding-orchestrator-todo-ssot.mdc) | Правила TodoWrite orch |
| [`.cursor/rules/asmadey-skills-todo-ssot.mdc`](../../.cursor/rules/asmadey-skills-todo-ssot.mdc) | Правила TodoWrite asm |
| [`.cursor/rules/external-skill-audit.mdc`](../../.cursor/rules/external-skill-audit.mdc) | sandbox → audit → GO |
| [`V1_CONTRACT.md`](V1_CONTRACT.md) | Freeze CLI/HTTP — не ломать без v2 |
| [`ADR_001_STACK.md`](ADR_001_STACK.md) | Решение по стеку |
| [`THREAT_MODEL.md`](THREAT_MODEL.md) | Угрозы и митигации |
| [`BUDGET_POLICY.md`](BUDGET_POLICY.md) | Лимиты $ / kill switch |
| [`NAMING.md`](NAMING.md) | Словарь терминов |
| [`OPS_LINUX_RUNNER.md`](OPS_LINUX_RUNNER.md) | Linux worker / Docker |
| [`SPIKES_REFERENCE.md`](SPIKES_REFERENCE.md) | Что взяли из SwarmClaw/OMA/… |
| [`OWNER_SIGNOFF_PENDING.md`](OWNER_SIGNOFF_PENDING.md) | Sign-off 115/115 COMPLETE |
| [`../PROGRESS_CHECKLIST.md`](../PROGRESS_CHECKLIST.md) | Чеклист прогресса |
| [`../AGENTS.md`](../AGENTS.md) | Правила для агентов в репо |
| [`../README.md`](../README.md) | Короткий README продукта |
| [`../.env.example`](../.env.example) | Шаблон env (секреты не в git) |
| [`../ui/macos/README.md`](../ui/macos/README.md) | OrchMac |
| [`../profiles/`](../profiles/) | YAML-профили доменов |
| [`../sandbox/`](../sandbox/) | Песочница e2e (не прод) |

### Старый handoff (устарел как SSOT)

Файл [`ML_SYSTEM_HANDOFF_CODING_ORCHESTRATOR_100.md`](ML_SYSTEM_HANDOFF_CODING_ORCHESTRATOR_100.md) — **редирект**: содержимое перенесено сюда. Новые правки — только в **этом MASTER**.

---

## 2. Что это и зачем

**Coding Orchestrator** — локальный ИИ-менеджер разработки на вашем Mac:

1. Вы описываете задачу (можно по-русски).  
2. Система дробит работу на роли (Coder / Reviewer / QA…).  
3. Каждая роль работает в **отдельной git-ветке** (worktree), не в `main`.  
4. Авто-ревью + QA + HTML-отчёт.  
5. В основную ветку — **только после вашей кнопки «Разрешить merge»**.

**Зачем:** безопасно делегировать рутину агентам днём и ночью, с лимитом бюджета, без утечки секретов и без смешивания Telegram-бота в iOS-релиз ALADDIN.

**Это отдельный продукт** в папке `coding_orchestrator/`. **Не часть App Store релиза iOS.**

---

## 3. Жёсткие правила для ML

1. Не коммитить в `main` / `master` / `release/*` без human ApproveGate.  
2. Не читать и не вставлять в чат: `.env`, VPN handoff §32, токены, ключи.  
3. Не класть `telegram_stars_shop_bot/**` в iOS-релизные коммиты (профиль `aladdin`).  
4. Prod / OAuth mass / трата лимитов подписок — только **явный GO владельца**.  
5. Эксперименты — в [`../sandbox/`](../sandbox/), не в прод ALADDIN.  
6. Todo `orch-*` — только `TodoWrite merge: true`; не затирать `af-*` / `jam-*`.  
7. API только `127.0.0.1`. Не открывать наружу без ops-решения.  
8. Не запускать голый `swift run OrchMac` для пользователя — только `.app` / Launchpad (иначе segfault menu bar).  
9. Ломать v1 API/CLI — только через bump `v2` ([`V1_CONTRACT.md`](V1_CONTRACT.md)).

---

## 4. Агенты, токены, подключение (просто)

### Откуда «подключение к агентам»

Всё на **вашем Mac**, не «облако чужих агентов»:

```
Вы (Launchpad / Telegram / CLI)
        ↓
  orch serve  (:8765, localhost)
        ↓
  Роли: Manager → Coder / Reviewer / QA / Docs
        ↓
  Harness = программы на Mac: claude / codex / ollama / …
        ↓
  Работа в git worktree (отдельная ветка)
        ↓
  HTML-отчёт → ваш Approve
```

Пока на Mac не установлены и не залогинены CLI (`claude`, `codex`, …) — реальной генерации кода от облачных моделей не будет (останется каркас/планирование).

### Откуда токены / ключи

**В оркестраторе токены не хранятся** (и не должны быть в git).

| Канал | Откуда доступ |
|-------|----------------|
| Claude | Уже установленный **Claude Code** + ваша подписка/логин на Mac |
| Codex | CLI **Codex** + аккаунт OpenAI |
| Ollama | Локально, без облачных токенов |
| CLIProxy (опция) | Sidecar `ORCH_CLIPROXY_URL` — ротация API-ключей, если сами подключите |
| Telegram-бот | Только `ORCH_TG_BOT_TOKEN` в локальном `.env` (не в git) |

Бюджет и kill switch: [`BUDGET_POLICY.md`](BUDGET_POLICY.md), `config/budget.yaml`, полоски в UI.

### Что за агенты (роли)

| Роль | Простыми словами | Делает | Не делает |
|------|------------------|--------|-----------|
| **Manager** | Бригадир | Планирует, дробит | Не коммитит в protected |
| **Coder** | Программист | Код в своей ветке | Не merge в main без вас |
| **Reviewer** | Ревьюер | Смотрит diff | Не merge |
| **QA** | Тестировщик | Тесты/smoke | Не merge |
| **Docs** | Документатор | Docs в своей ветке | Не трогает секреты |

Словарь: [`NAMING.md`](NAMING.md). Правила: [`../AGENTS.md`](../AGENTS.md).

### Что агенты могут / не могут

**Могут:** писать в worktree, ревью/QA, HTML-отчёт, ночная очередь, ждать Approve.  
**Не могут:** сами в `main`, прод-деплой без GO, читать VPN/`.env`, класть bot в iOS-релиз, «делать всё в мире» вне политики.

---

## 5. Как открыть на Mac (Launchpad)

### Один раз установить

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/coding_orchestrator
python3.12 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
make install-app
```

Или двойной клик: [`../scripts/orch_open.command`](../scripts/orch_open.command) (сам поставит `.app`, если нет).

### Каждый день

1. **Launchpad** (щипок / F4) → **Coding Orchestrator**  
2. Или Finder → `~/Applications` → **Coding Orchestrator**  
3. Справа вверху появится иконка **Orch** (menu bar)  
4. Откроется окно пульта  

Путь приложения: `~/Applications/Coding Orchestrator.app`

> **Нельзя:** `swift run OrchMac` без бандла — MenuBarExtra падает (segfault). Всегда `.app`.

---

## 6. Куда нажимать в окне и menu bar

### Полоска сверху

| Состояние | Значение | Действие |
|-----------|----------|----------|
| Свободен | Можно задачу | Пишите текст → «Сделать сейчас» |
| Работает | Агенты заняты | Ждите / смотрите отчёт |
| Ждёт вас | Нужен Approve | «Разрешить merge» / «Отклонить» |
| Движок выключен | API не отвечает | Снова открыть приложение, 2–3 сек |

### Окно

| Цель | Куда нажать |
|------|-------------|
| Задача сейчас | «Что сделать?» → Профиль → **Сделать сейчас** |
| На ночь | Текст → **На ночь** |
| Approve | **Разрешить merge** |
| Reject | **Отклонить** |
| Отчёт | Слева сессия / отчёт |
| Обновить | ↻ или ⌘R |

### Menu bar (иконка Orch справа вверху)

- Открыть окно Orch  
- Разрешить merge / Отклонить merge  
- Обновить / Выйти  

Если иконки нет — приложение не запущено.

Краткая копия: [`CONTROL_PANEL_RU.md`](CONTROL_PANEL_RU.md).

---

## 7. Русский язык задач

**Да, пишите по-русски.** Текст уходит в промпт модели.  
Лучше конкретно: что сломано, где, что считать «готово».

Пример: «Почини падающий тест в sandbox и приложи краткий отчёт».

---

## 8. Telegram (текст → кнопка Подтвердить → статус)

**Рекомендуемый путь (с телефона):**

1. Скопировать [`../.env.example`](../.env.example) → `.env` (не в git).  
2. `ORCH_TG_ALLOWLIST=<ваш telegram user id>`  
3. `ORCH_TG_BOT_TOKEN=<токен бота от @BotFather>`  
4. Launchpad → **Coding Orchestrator** (движок)  
5. В терминале:
   ```bash
   source .venv/bin/activate
   orch telegram bot
   ```
6. В Telegram боту напишите по-русски: «почини тесты в sandbox»  
7. Нажмите **Подтвердить** (или **Отменить**)  
8. Бот ответит «В очереди» → на Mac: отчёт → **Разрешить merge**

Команды в чате: `/help` · `/status` · голос (нужен `ORCH_STT_CMD` для распознавания).

**CLI (запасной путь):**
```bash
orch telegram propose --user-id ID --chat-id ID --title "почини тесты"
orch telegram confirm --user-id ID --id <pending_id>
```

Без allowlist — отказ (fail-closed). Без confirm — задача не стартует.  
Merge из Telegram **нельзя** — только OrchMac.  
Код: `engine/orch/telegram_inbox.py` · `orch telegram bot`.

---

## 9. Ночь / утро

| Когда | Что |
|-------|-----|
| Вечер | В окне: задача → **На ночь** (или `orch night enqueue --title "…"`) |
| Утро | Блок «Ночная очередь» + отчёт → **Разрешить merge** |
| CLI | `orch night digest` |

E2E sleep→morning: `orch e2e`.

---

## 10. CLI и HTTP API

### CLI (контракт v1 — не переименовывать)

`orch status|start|review|context|approve|serve|night|telegram|voice|worker|report|chaos|e2e`

Примеры:

```bash
source .venv/bin/activate
orch serve
orch start "починить тесты" --profile aladdin
orch review sandbox
orch approve merge --by owner
orch night digest
orch report
orch e2e
orch chaos
```

### HTTP (только 127.0.0.1)

Полная таблица: [`V1_CONTRACT.md`](V1_CONTRACT.md).

| Method | Path | Зачем |
|--------|------|--------|
| GET | `/health` | Жив ли движок |
| GET | `/v1/status` | sessions, budget, reports, night_queue, **attention** |
| GET | `/v1/profiles` | Список профилей |
| GET | `/v1/reports/{name}.html` | HTML |
| GET | `/v1/digest` | Утренний digest |
| POST | `/v1/start` | `{title, profile?}` |
| POST | `/v1/approve` | `{kind, by, approved}` |
| POST | `/v1/night/enqueue` | Ночная задача |
| POST | `/v1/budget/spend` | Учёт $ |

`attention`: `none` | `approve_merge` | `busy` (`offline` — только на клиенте).

---

## 11. Профили

Папка: [`../profiles/`](../profiles/). Поле **Профиль** в UI или `--profile` в CLI.

| Имя | Когда |
|-----|--------|
| `aladdin` | Работа рядом с ALADDIN — жёсткие deny (bot≠iOS, секреты) |
| `software-dev` | Обычные фичи/фиксы |
| `qa` / `code-review` / `devops` / `techdebt` / `docs` | По домену |
| `research` / `onboarding` / `agency` / `content` | … |
| `data-etl` / `security-defensive` / `triage` / `i18n` | … |
| `creative` / `science` / `internal-tools` / `night-factory` | … |

Эталон ALADDIN: [`../profiles/aladdin.yaml`](../profiles/aladdin.yaml).

---

## 12. Архитектура

```
Владелец: Launchpad OrchMac · Menu bar · Telegram · CLI
                    ↓
              orch serve :8765
                    ↓
         OrchestrationEngine
           SessionStore / resume / DAG / roles
           Worktree + Graft + MergeGate
           Context + Memory
           Reviewer + QA + SecurityPass + HTML
           Budget + NightQueue + TelegramInbox + Worker
                    ↓
         HarnessAdapter → Claude / Codex / Ollama / …
                    ↓ (опционально)
         CLIProxyAPI sidecar (ротация ключей)
```

Стек: [`ADR_001_STACK.md`](ADR_001_STACK.md) · Угрозы: [`THREAT_MODEL.md`](THREAT_MODEL.md) · Spikes: [`SPIKES_REFERENCE.md`](SPIKES_REFERENCE.md).

Гибрид каналов:

| Канал | Роль |
|-------|------|
| OrchMac + Menu bar | Главный пульт владельца |
| Telegram | Удалённый inbox + confirm |
| CLI | ML, автоматизация, debug |

---

## 13. Карта файлов кода

| Путь | Назначение |
|------|------------|
| `engine/orch/engine.py` | Ядро lifecycle |
| `engine/orch/cli.py` | CLI |
| `engine/orch/api_server.py` | HTTP для UI |
| `engine/orch/worktree.py` / `graft.py` | Git isolation |
| `engine/orch/reviewer.py` / `qa_agent.py` / `merge_gate.py` | Review→QA→gate |
| `engine/orch/security/*` | deny_main, redact, budget, approve, audit |
| `engine/orch/night_queue.py` / `resume.py` | Ночь + resume |
| `engine/orch/telegram_inbox.py` | TG ACL+confirm |
| `engine/orch/remote_worker.py` | Linux worker |
| `adapters/*` | Harness CLI |
| `ui/macos/` | OrchMac SwiftUI |
| `profiles/*.yaml` | Домены |
| `sandbox/` | E2E git |
| `tests/` | pytest |
| `scripts/install_launchpad_app.sh` | `.app` → Launchpad |
| `scripts/orch_open.command` | One-click open |
| `data/` | Runtime (sessions, reports, queue) — обычно gitignore |

Linux: [`OPS_LINUX_RUNNER.md`](OPS_LINUX_RUNNER.md) · `Dockerfile` в корне продукта.

---

## 14. 115 задач — план/факт

**Итог: 115 / 115 ✅** (2026-09-19). Полные строки: [registry](../../.cursor/CODING_ORCHESTRATOR_TASK_REGISTRY.md).

| Фаза | Тема | Кол-во | Статус |
|------|------|--------|--------|
| P0 | Meta / docs | 7 | ✅ |
| P1 | Security | 6 | ✅ |
| P2 | Engine | 8 | ✅ |
| P3 | Worktree / graft | 6 | ✅ |
| P4 | Context / memory | 5 | ✅ |
| P5 | Harnesses | 9 | ✅ |
| P6 | Proxy / limits | 8 | ✅ |
| P7 | Review / QA / HTML | 6 | ✅ |
| P8 | Skills / plugins | 5 | ✅ |
| P9 | macOS UI | 7 | ✅ |
| P10 | Night | 5 | ✅ |
| P11 | Telegram / voice | 4 | ✅ |
| P12 | Linux / Docker | 5 | ✅ |
| P13 | Domain profiles | 18 | ✅ |
| P14 | Spikes | 8 | ✅ |
| P15 | Acceptance | 8 | ✅ |

Sign-off: [`OWNER_SIGNOFF_PENDING.md`](OWNER_SIGNOFF_PENDING.md).

---

## 15. UX Control Plane v2

Сделано после 115/115, чтобы владельцу было удобно:

| Артефакт | Зачем |
|----------|--------|
| `~/Applications/Coding Orchestrator.app` | Launchpad, стабильный menu bar |
| `scripts/install_launchpad_app.sh` | Сборка/установка |
| `scripts/orch_open.command` | Открыть `.app` |
| RU UI + banner attention | Понятные состояния |
| Profile picker | Из `GET /v1/profiles` |
| Menu bar Orch | Approve без окна |
| `CONTROL_PANEL_RU.md` | Короткая шпаргалка |

Причина старого краша: голый `swift run` + MenuBarExtra без Info.plist `.app` → segfault. Лечится только бандлом.

---

## 16. Чеклист следующей ML-системы

1. Прочитать **этот MASTER** + [registry](../../.cursor/CODING_ORCHESTRATOR_TASK_REGISTRY.md) + [`V1_CONTRACT.md`](V1_CONTRACT.md).  
2. Не ломать localhost API без v2.  
3. Перед OAuth/тратой подписок — спросить GO владельца.  
4. Новые фичи → новый `orch-*` в registry + `TodoWrite merge: true`.  
5. Регрессия: `pytest -q` && `orch e2e` && `orch chaos` && `make install-app` (если трогали UI).  
6. iOS-релиз ALADDIN — не мешать с orch/bot без явной просьбы.  
7. Кнопки UI канон (RU): Сделать сейчас · На ночь · Разрешить merge · Отклонить · Обновить.  
8. Пользователю для запуска рекомендовать **Launchpad**, не `swift run`.

---

## 17. Мини-шпаргалка каждый день

```
Launchpad → Coding Orchestrator
→ написать задачу по-русски → Сделать сейчас
→ слева открыть отчёт
→ когда «Ждёт вас» → Разрешить merge
```

Быстро без окна: иконка **Orch** справа вверху → Разрешить merge / Открыть окно.

Обновить приложение после правок UI:

```bash
cd coding_orchestrator && make install-app
```

---

## 18. Out of scope / честные границы

**Отложено намеренно (не баг):**

- Ruflo как ядро  
- 60 OAuth-аккаунтов сразу  
- Auto-deploy prod без human GO  
- Полноценный чат-агент «переписывайся с ИИ в Telegram» (есть задача→кнопка→очередь; не Cursor)  
- VibeProxy / EasyCLI как основа  

**Честно сейчас:**

| Вопрос | Ответ |
|--------|--------|
| Подключение агентов? | Локально Mac → CLI harness |
| Токены? | Из логинов Claude/Codex/… (+ опц. CLIProxy); не из репо Orch |
| Telegram легко? | Да: текст/голос → кнопка Подтвердить → статус (`orch telegram bot`) |
| Русский? | Да |
| Агенты всё могут? | Нет — ветки + отчёт + ваш Approve на Mac |

---

**Вердикт:** продукт 115/115 + пульт Launchpad готов к ежедневному использованию на Mac.  
Единая точка входа для людей и ML: **этот файл**.
