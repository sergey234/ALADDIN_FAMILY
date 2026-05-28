# RiveMCP — установка и проверка (ALADDIN)

> **Полный гайд (Editor + Node + MCP + пайплайн):** [COMPANION_RIVE_CONNECT_NODE_MCP.md](./COMPANION_RIVE_CONNECT_NODE_MCP.md)

**Статус на Mac (2026-05-28):** Node **v26** · `rivemcp` **1.3.6** · бинарник `/usr/local/bin/rivemcp` · **MCP подключён** (tools `user-rivemcp-*` в Cursor)

**Пробный черновик (RiveMCP):**

| Файл | Назначение |
|------|------------|
| `Resources/Companion/unicorn_mcp_draft.riv` | runtime (388 B, SM без layers — доработка) |
| `Resources/Companion/unicorn_mcp_draft.rev` | открыть в **Rive.app** → import PNG, states |

Осталось **1 бесплатный export** на этой машине (из 3). Production `unicorn.riv` **не перезаписывали**.

---

## Что установлено

| Компонент | Путь / версия |
|-----------|----------------|
| Node (Homebrew) | `/usr/local/bin/node` · v26.0.0 |
| npm | `/usr/local/bin/npm` · 11.x |
| RiveMCP | `/usr/local/bin/rivemcp` · 1.3.6 |

**MCP config (Cursor):**

- Глобально: `~/.cursor/mcp.json`
- Проект: `ALADDIN_NEW/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "rivemcp": {
      "command": "/usr/local/bin/rivemcp",
      "args": []
    }
  }
}
```

Полный путь к бинарнику — чтобы Cursor не зависел от `PATH` (раньше `npx` не находился).

---

## Ваши 3 шага в Cursor (обязательно)

1. **Reload Window:** `Cmd+Shift+P` → **Developer: Reload Window**
2. **Settings → Tools & MCP** → сервер **`rivemcp`** должен быть **зелёным** (Connected), tools ~139
3. В **новом чате** Agent попросите, например:

   > Создай черновик `unicorn.riv`: artboard 360×480, State Machine с 13 triggers (idle…alert) и Number `mouth_open`, сохрани в `Resources/Companion/unicorn_mcp_draft.riv`

   Не перезаписывайте production `unicorn.riv`, пока не проверили в Rive Editor.

---

## Лицензия RiveMCP

- **3 бесплатных export** на машину (fingerprint).
- Дальше: ключ на [rivemcp.stunning.gg](https://rivemcp.stunning.gg)

```bash
export RIVEMCP_LICENSE_KEY="ваш-ключ"
```

Добавить в `mcp.json` → `"env": { "RIVEMCP_LICENSE_KEY": "..." }` (не коммитить ключ в git).

Сброс кэша лицензии: `rivemcp --reset-license-cache`

---

## Проверка в Терминале

```bash
/usr/local/bin/node --version    # v26.x
/usr/local/bin/rivemcp --version # rivemcp
/usr/local/bin/rivemcp --help
```

Если `command not found` в обычном терминале:

```bash
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

---

## Честно про ALADDIN

| RiveMCP может | RiveMCP не может |
|---------------|------------------|
| Скелет SM, 13 triggers, `mouth_open` | Ваш OB-art из Figma 1:1 |
| Простые движения, export `.riv` / `.rev` | Заменить ручной polish в Rive Editor |
| Открыть/править существующий `.riv` | Обойти лимит 3 export без ключа |

**Рабочий пайплайн:** RiveMCP → черновик `.riv` или `.rev` → **Rive.app** (import PNG, доработка) → production export → `Resources/Companion/`.

См. также: [COMPANION_RIVE_EDITOR_5_STEPS.md](./COMPANION_RIVE_EDITOR_5_STEPS.md)

---

## Если MCP красный в Cursor

1. Проверить: `ls -la /usr/local/bin/rivemcp`
2. macOS quarantine (если ставили binary вручную): `xattr -d com.apple.quarantine /path/to/rivemcp`
3. Логи: Settings → MCP → rivemcp → View logs
4. Fallback в `mcp.json`:

```json
"command": "/usr/local/bin/npx",
"args": ["-y", "rivemcp"]
```
