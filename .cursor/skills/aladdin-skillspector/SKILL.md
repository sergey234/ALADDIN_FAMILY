---
name: aladdin-skillspector
description: Audit an external Cursor skill before install. Use before adding any Asmadey or third-party SKILL.md.
---

# Aladdin Skillspector (thin)

Перед установкой внешнего skill ответь **PASS/FAIL** по каждому пункту.

## Чеклист

| # | Проверка | PASS? |
|---|----------|-------|
| 1 | Нет секретов, токенов, VPN handoff, `.env` | |
| 2 | Нет auto-merge / force-push / Dark Factory | |
| 3 | Не обходит ALADDIN: no-mock, bot≠iOS, ask-before-ops | |
| 4 | Не навязывает RN / shadcn / MagicUI / GSAP как стек app | |
| 5 | Не требует публичный egress без политики | |
| 6 | Не дублирует слепо то, что уже есть (Repowise, orch Approve) | |
| 7 | Лицензия / ToS приемлемы для владельца | |
| 8 | Размер: thin идея, не «весь репо Asmadey» | |

## Вердикт

- **FAIL** любой пункт → не ставить; сообщить владельцу.
- **PASS все** → ждать **GO владельца**, затем thin `aladdin-*` wrapper.

## Песочница

Только `.cursor/skills_sandbox/` или `BACKUPS/skills_sandbox/`.
