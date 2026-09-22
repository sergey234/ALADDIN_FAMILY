# Tailscale admin — шаги 2–5 (2026-09-21)

**Статус:** ✅ Mac + MAIN + Brain в одном tailnet · dual-path SSH · продукт цел

## Узлы

| Имя Tailscale | Роль | TS IP | Старый вход |
|---------------|------|-------|-------------|
| `macbook-pro` | ваш Mac | `100.119.32.51` | — |
| `aladdin-main` | 🇷🇺 MAIN Аладдин | `100.124.156.3` | `ssh aladdin-server` |
| `aladdin-contabo` | 🇩🇪 Brain бот/касса | `100.102.195.8` | `ssh aladdin-contabo` |

## Как входить теперь

| Путь | Команда |
|------|---------|
| Через Tailscale (новый) | `ssh aladdin-server-ts` / `ssh aladdin-contabo-ts` |
| Через IP (как раньше, break-glass) | `ssh aladdin-server` / `ssh aladdin-contabo` |

Оба пути: тот же ключ `~/.ssh/aladdin_server`, без пароля.

## Что не меняли

- Phase 0 `PasswordAuthentication no`
- API `:8002`, vpn-api `:8091`, бот units
- UFW / закрытие public 22 — **не делали**
- `wg-bridge` — не трогали
- prefs: `--accept-routes=false --accept-dns=false --ssh=false`

## Smoke ✅

- ping TS MAIN OK  
- SSH TS + SSH IP OK  
- health `{"status":"ok"}` · vpn-api 200  

## Дальше (отдельный GO)

- Не закрывать public SSH ≥7 дней dual-path  
- Aperture / FetchLite / Bonsai — другие треки  
