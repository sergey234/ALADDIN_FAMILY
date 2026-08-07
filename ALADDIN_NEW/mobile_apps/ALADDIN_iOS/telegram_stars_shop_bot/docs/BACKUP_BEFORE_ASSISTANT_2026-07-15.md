# Бэкап перед Помощником AiMonkey — 2026-07-15

**Цель:** зафиксировать рабочее состояние до трека `as-*`.  
**Канон:** `IMPLEMENTATION_PLAN_AND_TASKS.md` §1 + `BOT_SINGLE_INSTANCE_CANON.md`

---

## Архитектура (важно!)

| Роль | Хост | Что критично |
|------|------|----------------|
| **Polling + SSOT shop.db** | Contabo `185.225.233.150` | `aladdin-telegram-bot` **active**, маркер `SHOP_BOT_POLLING_HOST`, `data/shop.db` |
| **Partner API / webhooks** | MAIN `149.154.65.180` | `partner-api` + `webhook-worker`; бот **не** поллит |
| **Код разработки** | Mac `ALADDIN_iOS/telegram_stars_shop_bot` | много незакоммиченных правок — бэкап кода обязателен |

---

## Что сделано сегодня

### A) Локально (Mac)

| Артефакт | Путь |
|----------|------|
| Clean script ZIP | `BACKUPS/BACKUP_TELEGRAM_BOT_CLEAN_20260715_1244.zip` (4.4M) |
| Folder copy | `BACKUPS/TELEGRAM_STARS_SHOP_BOT_20260715_124459/` |
| tar.gz код | `BACKUPS/telegram_shop_bot/telegram_stars_shop_bot_code_20260715-124502.tar.gz` |
| git status | `BACKUPS/telegram_shop_bot/git_status_bot_20260715-124502.txt` |
| git HEAD | `BACKUPS/telegram_shop_bot/git_head_20260715-124502.txt` |

Исключено: `.env`, `data/`, venv.

### B) Contabo polling `185.225.233.150` — **главный снимок**

Каталог `/root/shop_bot_backups/` · TS **`20260715-104605`**:

- `shared.env.bak_20260715-104605` (11K)
- `shop.db.bak_20260715-104605` (**832K**, integrity `ok`, ~38 users / ~96 orders)
- `vpn.db.bak_20260715-104605` (648K)
- `current_app_deref_shared_20260715-104605.tar.gz` (4.8M)
- Release на момент снимка: `releases/20260715-112509`
- Bot: **active** + `SHOP_BOT_POLLING_HOST`

### C) MAIN `149.154.65.180` — API-хост

`/root/shop_bot_backups/` · TS **`20260715-114504`**:

- `shared.env.bak_*`, `shop.db.bak_*` (364K — копия MAIN, **не** SSOT Contabo)
- `vpn.db.bak_*` из `/opt/aladdin-shop-vpn-api/var/vpn.db`
- `current_app_deref_shared_*.tar.gz`
- Partner API: `{"status":"ok"}`; polling unit **inactive** (так и должно)

---

## Как откатить

1. **Contabo код:** из tar или симлинк на `releases/20260715-112509`.  
2. **Contabo БД:** stop bot → `cp shop.db.bak_* → data/shop.db` → start.  
3. **`.env`:** из `shared.env.bak_*`.  
4. **Mac:** распаковать ZIP/tar из `BACKUPS/`.  
5. **Никогда** не включать polling на MAIN.

---

## Перед `as-*`

- [x] Локальный бэкап кода  
- [x] Contabo (polling) env + shop.db + vpn.db + код  
- [x] MAIN env + db + код + vpn.db  
- [ ] Деплой assistant только с `--exclude data --exclude .env`  
- [ ] Сначала `ASSISTANT_ENABLED=0` / ADMIN_ONLY на Contabo  

**rsync никогда не должен затирать prod `data/` и `shared/.env`.**

---

## D) Железобетон VPN API — добавлено 2026-07-15 (только копии, сервисы не трогали)

### Contabo `185.225.233.150` — TS `20260715-105439`

Путь: `/root/shop_bot_backups/vpn_api_ironclad_20260715-105439/`  
Архив: `/root/shop_bot_backups/vpn_api_ironclad_20260715-105439.tar.gz` (348K pack / 2.2M folder)

Содержимое:
- `env` (5969 байт, match live YES)
- `var/vpn.db` integrity **ok**
- `var/wg-keys` (2 файла = live)
- `var/ovpn-profiles` (2 файла = live)
- bridge/cdn/journal JSON + uuid
- код API без venv: `vpn_api_code_no_venv_*.tar.gz`
- unit dump `aladdin-shop-vpn-api.service.txt`
- старые `vpn.bak-safety-*.db`

После: `aladdin-telegram-bot` = **active**, `aladdin-shop-vpn-api` = **active**.

### MAIN `149.154.65.180` — TS `20260715-115439`

Путь: `/root/shop_bot_backups/vpn_api_ironclad_20260715-115439/`  
Архив: `…/vpn_api_ironclad_20260715-115439.tar.gz`

Содержимое: `env` (2804, match YES), `vpn.db` ok, wg-keys, ovpn-profiles, код без venv, dumps partner-api/webhook (+ nginx site если был).

После: partner-api / webhook-worker = **active** (не останавливали).
