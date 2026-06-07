# Rive: Cadet (rive.app) vs RiveMCP (Cursor) — статус 2026-06-04

## Два разных продукта

| | **Rive Cadet** (вы оплатили) | **RiveMCP** (Cursor MCP) |
|--|------------------------------|---------------------------|
| Сайт | [rive.app](https://rive.app) | [rivemcp.stunning.gg](https://rivemcp.stunning.gg) |
| Цена | ~$17/мес | ~$10/мес отдельно |
| Для ALADDIN | **Основной путь:** unlimited export в **Rive.app** | Черновики SM из чата; не рисует OB-art 1:1 |
| Статус | ✅ Cadet активен | Free trial **3/3** исчерпан на Mac |

**HERO-3-07 production:** делайте export в **Rive Editor** (Cadet), не ждите RiveMCP.

---

## RiveMCP в Cursor (если нужен снова)

1. `Cmd+Shift+P` → **Developer: Reload Window**
2. **Settings → Tools & MCP** → `rivemcp` → **Connected** (зелёный)
3. В Agent должны появиться tools `user-rivemcp-*` (~139)

Конфиг уже есть: `~/.cursor/mcp.json` и `ALADDIN_iOS/.cursor/mcp.json`:

```json
"rivemcp": {
  "command": "/usr/local/bin/rivemcp",
  "args": [],
  "env": {}
}
```

**Export через MCP** (опционально): ключ с stunning.gg →

```json
"env": { "RIVEMCP_LICENSE_KEY": "..." }
```

Сброс кэша после покупки: `rivemcp --reset-license-cache`

---

## Сейчас в репо

| Файл | Размер | Статус |
|------|--------|--------|
| `unicorn.riv` | ~158 KB | ✅ production |
| `aladdin.riv` | ~15 KB | ⏳ placeholder |
| `genie.riv` | ~15 KB | ⏳ placeholder |
| `aladdin_work_in_progress.riv` | копия unicorn SM | открыть в Rive → заменить арт → Save as `aladdin.riv` |

---

## Команды после export в Rive.app

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
python3 scripts/companion_riv_size_gate.py --dir Resources/Companion --min-kb 25
./scripts/verify_companion_rive_ios_bundle.sh
```

Написать в чат: **«aladdin готов»** → ML прогонит gate и откроет genie.

---

## Журнал для следующей ML (сессия 2026-06-04)

### Контекст

Пользователь оплатил **Rive Cadet** на rive.app ($17/мес). Запрос: «подключись к Rive».

### Что проверила ML в терминале

| Действие | Результат |
|----------|-----------|
| `node --version` | v26 ✅ |
| `rivemcp --version` | 1.3.6 ✅ |
| `~/.cursor/mcp.json` | `rivemcp` прописан ✅ |
| `CallMcpTool` rivemcp | ❌ в **этой** сессии tools не смонтированы (нужен Reload Window) |
| `printf … \| rivemcp` (probe) | `Free trial exhausted (3/3 exports used)` |

### Что сделала ML (без RiveMCP export)

1. **`cp unicorn.riv → aladdin_work_in_progress.riv`** — скопирован **готовый** State Machine единорога (13 triggers + `mouth_open`), чтобы не собирать SM с нуля для Аладдина.
2. **`open -a Rive aladdin_work_in_progress.riv`** + **`open` PNG** `docs/assets/aladdin_master_OB01_crop_360x480.png` — открыть Editor и референс art.
3. Док **`COMPANION_RIVE_CADET_MCP_STATUS.md`** — различие Cadet vs RiveMCP.
4. Gate script: добавлен `--min-kb 25` (production vs placeholder).
5. Batch: **`COMPANION_RIVE_HERO307_CURSOR_BATCH.md`**.

### Что НЕ делала эта ML

- Не тратила RiveMCP export (лимит уже 0 с 28.05).
- Не заливала production `aladdin.riv` / `genie.riv` (ждёт ручной export в Rive.app с Cadet).

### RiveMCP 3/3 — кто и когда (см. TRACKER §2026-05-28)

Исчерпано **предыдущей** ML-сессией при настройке Node+MCP, не в чате 2026-06-04. См. раздел «Анализ 3/3» в [COMPANION_ML_HANDOFF_2026-05-28.md](./COMPANION_ML_HANDOFF_2026-05-28.md).
