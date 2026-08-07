# ML Handoff: Telegram Bot API outage / egress (AiMonkey Stars bot)

**Date:** 2026-07-14 (incident window ~2026-07-13 evening CEST)  
**Host (SSOT):** Contabo `root@185.225.233.150`  
**Bot:** `@AiMonkeyStars_bot` (id `8866410048`)  
**Unit:** `aladdin-telegram-bot.service`  
**App path:** `/opt/aladdin-telegram-shop-bot/current_app`  
**Env:** `/opt/aladdin-telegram-shop-bot/shared/.env`  
**SSH key:** `~/.ssh/aladdin_server`  
**Canon:** polling **only Contabo** (marker `SHOP_BOT_POLLING_HOST`); MAIN must **not** run second poller.

---

## 0. Current status (re-checked 2026-07-13 21:19 UTC)

| Check | Result |
|-------|--------|
| `systemctl stop` → probe → `start` | Done |
| `https://api.telegram.org/` | HTTP 302 ~0.1s |
| Fake token `getMe` | HTTP 401 ~0.08s |
| Real `BOT_TOKEN` `getMe` | HTTP **200 ~0.09s** |
| `getUpdates?timeout=0` | HTTP **200** (queue drained) |
| Bot after restart | `Start polling` + **Update id=… handled ~1.3s** |
| Partner API `:8090` / VPN API `:8091` | `{"status":"ok"}` |

**User action now:** open Telegram → `/start` on `@AiMonkeyStars_bot` — should respond.  
**This incident is currently recovered**, but **must not be treated as permanent**. The same failure mode can return because bot egress still shares Contabo VPN-exit IP.

---

## 1. What happened (plain language)

Users pressed **Start**; the bot did not open / did not reply.  
Phone network and VPN API were fine. The shop bot process was often “running”, but it **could not complete Telegram Bot API calls**.

Symptoms while broken:

- Logs: `TelegramNetworkError: HTTP Client says - Request timeout error`
- Aiogram `tryings = 50+`
- Startup hung/crashed on `set_my_commands`
- `curl` to `api.telegram.org/` (root) still fast
- Valid-token `getMe` / `getUpdates` hung (0 bytes, 15–60s timeout)
- Fake token still returned **401 quickly**
- Same valid-token hang also reproduced from MAIN `149.154.65.180` during the outage window
- Local Mac also could not reach Telegram API during that window (environmental / wider)

**Not the root cause:** `/start` handlers, Partner API, VPN `/sub` code bugs.

**Root class:** Contabo ↔ Telegram **Bot API authenticated path** degraded or soft-blocked; long-poll died; bot deaf.

Likely contributing factor: **same public Contabo IP** used for:

1. Mass **VPN user egress** toward Telegram (`149.154.*` via Xray), and  
2. Official **Bot API** polling (`getUpdates` / `sendMessage`).

Telegram may soft-degrade Bot API for such IPs. “Dirty” here means **shared reputation / anti-abuse**, not malware.

Historical extras (noise): `TelegramConflictError` (second poller), `database is locked`, stuck-order false alerts for VPN orders left in `paid`.

---

## 2. Architecture (do not break)

```
Users (Telegram app) → Telegram cloud
                              ↑
Contabo bot (aiogram long-poll / replies) ──► api.telegram.org
Contabo VPN (Xray exit) ───────────────────► same Contabo public IP (problem if shared forever)

MAIN 149.154.65.180 = RU bridge / nginx; bot polling DISABLED (ConditionPathExists SHOP_BOT_POLLING_HOST)
```

**Best permanent fix (recommended):** keep bot **process + DB on Contabo**; put **only Bot API egress** on a **tiny dedicated VPS** (SOCKS/HTTP proxy). Do **not** move whole shop/VPN to a new box as step 1.

---

## 3. Immediate recovery runbook (try first, free)

Run on Contabo:

```bash
ssh -o BatchMode=yes -o IdentitiesOnly=yes -i ~/.ssh/aladdin_server root@185.225.233.150
```

### 3.1 Stop and probe

```bash
systemctl stop aladdin-telegram-bot.service
pkill -9 -f '[b]ot.main' 2>/dev/null || true
sleep 2

TOK=$(grep -m1 '^BOT_TOKEN=' /opt/aladdin-telegram-shop-bot/shared/.env | cut -d= -f2- | tr -d '"' | tr -d "'")

curl -4 -sS -m 8 -o /dev/null -w "root=%{http_code} t=%{time_total}\n" https://api.telegram.org
curl -4 --http1.1 -sS -m 10 -w "\nfake=%{http_code} t=%{time_total}\n" "https://api.telegram.org/bot0:FAKE/getMe"
curl -4 --http1.1 -sS -m 20 -o /tmp/tg_me.json -w "getMe=%{http_code} t=%{time_total}\n" \
  "https://api.telegram.org/bot${TOK}/getMe"
head -c 200 /tmp/tg_me.json; echo
```

**Pass criteria:** real `getMe` → `200` and `t < 2.0` (ideally &lt; 1s).

### 3.2 Start and confirm polling

```bash
systemctl start aladdin-telegram-bot.service
sleep 8
systemctl is-active aladdin-telegram-bot.service
tail -n 50 /opt/aladdin-telegram-shop-bot/logs/bot.log | grep -E 'Start polling|Run polling|Update id=|TelegramNetworkError'
```

**Pass:** `Start polling` + recent `Update id=… is handled` without timeout storm.

### 3.3 If still FAIL

Do **not** keep restarting forever. Go to §4 (dedicated egress). Moving poller to MAIN alone is **not** proven fix (MAIN also timed out during incident).

---

## 4. Best long-term fix: dedicated Bot API egress (mini-VPS)

### 4.1 Goal

```
VPN users     → Contabo public IP → Internet (unchanged)
Shop bot code → Contabo           → SOCKS/HTTP on mini-VPS → api.telegram.org
DB / VPN API  → Contabo (unchanged)
```

### 4.2 Buy / provision mini-VPS

- Size: 1 vCPU / 512MB–1GB RAM enough  
- Region: EU (NL/DE/FI), **not** Contabo, **not** MAIN  
- OS: Ubuntu 22.04/24.04  
- Open only: SSH + SOCKS/HTTP port to Contabo IP (firewall allowlist)

### 4.3 Install proxy on mini-VPS (example: Dante or microsocks / 3proxy)

Requirements:

- SOCKS5 **or** HTTP CONNECT with **user/password**
- Bound to private iface / firewalled to Contabo `185.225.233.150` only
- Verify from Contabo:

```bash
curl -4 --http1.1 -sS -m 10 \
  -x socks5h://USER:PASS@MINI_VPS_IP:PORT \
  -o /tmp/tg_me.json -w "getMe=%{http_code} t=%{time_total}\n" \
  "https://api.telegram.org/bot${TOK}/getMe"
```

**Gate:** `200` and `t < 1.0`.

### 4.4 Wire aiogram to proxy (Contabo)

1. Find how `Bot` / `AiohttpSession` is created in `bot/main.py` (or session factory).  
2. Add settings, e.g.:

```text
TELEGRAM_PROXY_URL=socks5://user:pass@MINI_VPS_IP:PORT
# or http://user:pass@MINI_VPS_IP:PORT
```

3. Pass proxy into aiogram session (aiohttp proxy URL).  
4. Put vars in `/opt/aladdin-telegram-shop-bot/shared/.env` (never commit secrets).  
5. `systemctl restart aladdin-telegram-bot.service`  
6. Confirm polling + `/start` E2E.

### 4.5 What NOT to do as first step

- Do not relocate SQLite shop DB + VPN API “just because”  
- Do not enable second poller on MAIN  
- Do not use free public SOCKS from the internet (token theft)  
- Do not treat webhook-only as full fix without working outbound (replies still need Bot API)

---

## 5. Prevention (so this does not repeat)

| ID | Task | Why |
|----|------|-----|
| P1 | Keep Bot API egress IP **≠** VPN exit IP | Stops shared Telegram reputation |
| P2 | Cron/systemd timer: `getMe` every 60–120s; alert if `t>5s` or non-200 | Detect deaf bot before users |
| P3 | On `getMe` fail streak ≥3: ops Telegram alert + optional auto-failover to backup proxy | Reduce downtime |
| P4 | Enforce **single poller** (existing Contabo-only marker) | Avoid `Conflict: terminated by other getUpdates` |
| P5 | Log metric: consecutive `TelegramNetworkError` count; alert at threshold | Catch slow death |
| P6 | Document runbook link from `VPN_INCIDENT_ANNOUNCE_RUNBOOK.md` / ops chat | Humans know what to do |
| P7 | After any token leak in verbose curl/logs: rotate via BotFather, update `.env`, restart | Security |
| P8 | Optional hot-standby second mini-VPS proxy | Failover |
| P9 | Do not spray Bot API from tools without timeouts / rate limits | Avoid self-inflicted pressure |

---

## 6. TODO checklist (for implementing agent)

### Phase A — Verify live (always first)

- [ ] SSH Contabo OK  
- [ ] Probe root / fake / real `getMe` / `getUpdates`  
- [ ] Restart bot if API healthy but process stuck  
- [ ] Confirm `Start polling` + `Update id=` handled  
- [ ] Ask owner to press `/start` once  

### Phase B — If API still dead from Contabo

- [ ] Confirm MAIN also fails/succeeds (`getMe`) — do not assume MAIN is magic  
- [ ] Provision mini-VPS **or** temporary owner-home SOCKS tunnel (emergency only)  
- [ ] Prove `getMe` via proxy &lt; 1s from Contabo  
- [ ] Implement `TELEGRAM_PROXY_URL` in bot + `.env`  
- [ ] Restart bot; E2E `/start`  
- [ ] Keep VPN on Contabo unchanged  

### Phase C — Hardening (do even if currently recovered)

- [ ] Implement `getMe` watchdog + ops alert (`vpn_ops_alert` / `send_alert`)  
- [ ] Deduplicate alert key e.g. `telegram_bot_api:fail` (cooldown 15–60 min)  
- [ ] Document proxy host inventory (IP, port, firewall, billing)  
- [ ] Rotate `BOT_TOKEN` if it appeared in verbose diagnostics  
- [ ] Re-check: no bot.main on MAIN; Contabo marker present  

### Phase D — Related cleanup (optional, separate)

- [ ] VPN orders 73/79 stuck in `paid` though VPN delivered → mark `completed` after successful provision  
- [ ] Fix `vpn_prod_smoke.py` UUID conflict (`VPN_XRAY_DEFAULT_CLIENT_UUID` empty / shared with admin)  
- [ ] SQLite `database is locked` → WAL / busy_timeout  

---

## 7. Decision tree

```
/start silent?
  → curl getMe Contabo
      → 200 fast: restart bot; check polling logs; test /start
      → timeout / hang: dedicated egress proxy (do not only restart loop)
          → temporary: home SOCKS SSH tunnel
          → durable: mini-VPS proxy + TELEGRAM_PROXY_URL
  → never run second poller on MAIN while Contabo polls
```

---

## 8. Verification commands (copy/paste)

```bash
# Contabo health bundle
systemctl is-active aladdin-telegram-bot.service aladdin-partner-api.service
curl -sS -m 5 http://127.0.0.1:8090/health
curl -sS -m 5 http://127.0.0.1:8091/health
TOK=$(grep -m1 '^BOT_TOKEN=' /opt/aladdin-telegram-shop-bot/shared/.env | cut -d= -f2- | tr -d '"')
curl -4 --http1.1 -sS -m 10 -w "getMe=%{http_code} t=%{time_total}\n" \
  -o /tmp/tg_me.json "https://api.telegram.org/bot${TOK}/getMe"
grep -E 'Start polling|TelegramNetworkError|Update id=' /opt/aladdin-telegram-shop-bot/logs/bot.log | tail -20
```

**Never** log full bot token in chat/tickets; redact.

---

## 9. Options compared (for product owner)

| Option | Speed | Reliability | Cost | Notes |
|--------|-------|-------------|------|-------|
| Restart / wait | Fast | Low | 0 | Worked 2026-07-14; may recur |
| Home SOCKS tunnel | Fast | Low (PC on) | 0 | Emergency only |
| Move poller to MAIN | Medium | Unproven | 0 | Failed during outage probe |
| **Mini-VPS Bot API proxy** | Medium | **High** | Low $/mo | **Recommended durable fix** |
| Full bot+DB migrate | Slow | Mixed | Higher | Overkill as first move |
| Free public SOCKS | Fast | Bad | 0 | Forbidden for prod token |

---

## 10. Message for next ML system

1. Incident = **Bot API egress / Telegram path**, not shop handler bug.  
2. Today bots **recovered after stop/probe/start**; still implement **§4 + §5**.  
3. Best architecture: Contabo keeps brain; mini-VPS is only Telegram mouth.  
4. Prove every change with timed `getMe` and one real `/start`.  
5. Preserve single-instance polling canon.

**Primary owner ask after your deploy:** “Press Start in @AiMonkeyStars_bot — menu comes back?”  

---

## 11. Related docs

- `docs/BOT_SINGLE_INSTANCE_CANON.md`  
- `docs/ML_SYSTEM_HANDOFF_FINAL.md`  
- `docs/VPN_INCIDENT_ANNOUNCE_RUNBOOK.md`  
- `docs/PLAN_TOMORROW_BOT_RESILIENCE_NO_PROXY_2026-07-15.md` — план **без** proxy (день 1)  
- `docs/BOT_RESILIENCE_NO_PROXY_TODO_TRACKER.md` — Cursor TODO SSOT (`br-*`) для дня 1  
- Deploy rule: `.cursor/rules/telegram-shop-bot-deploy.mdc`
