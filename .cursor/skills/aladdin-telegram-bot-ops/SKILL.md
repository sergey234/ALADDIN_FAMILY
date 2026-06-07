---
name: aladdin-telegram-bot-ops
description: Telegram Stars/Premium/VPN shop bot — deploy, security, smoke. Use for bot tasks only; never mix into iOS release commits.
origin: ALADDIN
---

# ALADDIN Telegram Shop Bot

**Canonical source:** `telegram_stars_shop_bot/`  
**Prod:** `/opt/aladdin-telegram-shop-bot` (NOT `/opt/aladdin-backend`)  
**Partner API:** `127.0.0.1:8090` on server

## When to use

- Deploy bot, Stars, Premium, VPN flows
- `partner_api` rate limits, webhooks, `.env` on server
- Security review of bot Python code

## When NOT to use

- iOS app screens, Swift, Xcode release — use iOS rules/skills instead

## Security checklist

- [ ] Never commit `.env` or `shared/.env` secrets
- [ ] `partner_api/rate_limit_middleware.py` — 429 on flood
- [ ] Webhooks: idempotency, no raw secrets in logs
- [ ] VPN `.conf` delivery only after `vpn_active` — see `bot/services/vpn_post_purchase_delivery.py`
- [ ] `ADMIN_IDS` / `SUPER_ADMIN_IDS` for financial ops

## Deploy (summary)

Rule: `.cursor/rules/telegram-shop-bot-deploy.mdc`  
Handoff: `telegram_stars_shop_bot/docs/ML_SYSTEM_HANDOFF_FINAL.md`

1. `curl http://149.154.65.180:8002/api/health` (main API, not bot)
2. `./scripts/create_telegram_bot_backup.sh` before big changes
3. `rsync` bot → `releases/<TS>/telegram_stars_shop_bot/` (exclude `.env`, `data`, venv)
4. Restart: `aladdin-telegram-bot`, `aladdin-partner-api`, `aladdin-webhook-worker`
5. `curl http://127.0.0.1:8090/health` on server

## Smoke

- VPN UX: `telegram_stars_shop_bot/docs/VPN_UX_SMOKE_CHECKLIST.md`
- Tests: `cd telegram_stars_shop_bot && pytest tests/test_vpn_legal_gate.py tests/test_bot_domain_suite.py -q`

## iOS commit guard

```bash
git diff --cached --name-only | grep -E '^telegram_stars_shop_bot/|^\.env$' && echo STOP || echo OK
```
