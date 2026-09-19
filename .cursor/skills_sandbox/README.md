# Skills sandbox (песочница внешних skills)

**Канон:** внешние skills (Asmadey и др.) сначала сюда, **не** сразу в `.cursor/skills/aladdin-*`.

## Пути

| Путь | Назначение |
|------|------------|
| `.cursor/skills_sandbox/` | Рабочая песочница (в git только README + gitignore) |
| `BACKUPS/skills_sandbox/` | Опционально; весь `BACKUPS/` уже в `.gitignore` |

## Порядок

1. `git clone` / copy skill → `skills_sandbox/<name>/`
2. Аудит по `aladdin-skillspector`
3. GO владельца
4. Создать thin `.cursor/skills/aladdin-<name>/SKILL.md` (свои формулировки + ссылка на идею)

## Не делать

- Коммитить чужой полный каталог Asmadey
- Класть sandbox-копии с секретами
- Ставить в `coding_orchestrator/` дерево Asmadey
