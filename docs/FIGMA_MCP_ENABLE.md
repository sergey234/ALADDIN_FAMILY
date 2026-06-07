# Figma MCP — как «раньше» (1 мин)

**Проблема:** в чате нет `get_metadata` / `whoami` → агент не видит Figma.

**Решение (оба пункта):**

1. **Cursor → Settings → MCP** — сервер **figma** (`https://mcp.figma.com/mcp`) → **Connect** (OAuth).
2. **Figma Desktop** на Mac — открыт файл [Companion-Heroes](https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM/Companion-Heroes).

В репо уже добавлено в `.cursor/mcp.json` и `~/.cursor/mcp.json`.

После Connect: **Reload Window** (`Cmd+Shift+P` → Developer: Reload Window) или **новый чат**.

Проверка в чате: «проверь 02b figma» — агент вызовет `get_metadata` fileKey `vwKcGPUUEZjgayEHNn0BJM`.

**Запасной путь:** Personal Access Token в `docs/FIGMA_COMPANION.env` → `python3 scripts/audit_companion_figma_02b.py`
