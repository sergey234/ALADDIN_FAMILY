# Deploy day note — 2026-07-14

**Release:** `20260714-161852`  
**Hosts:** Contabo `185.225.233.150` (poller) · MAIN `149.154.65.180` (API/worker, bot blocked)

## P0

- getMe Contabo: **OK** HTTP 200 ~0.11–0.15s · `@AiMonkeyStars_bot`
- Decision: getMe OK → deploy + restart allowed. Fail-path remains: **no** restart-storm (smart-restart gated in `telegram_bot_api_health.sh`).

## Deploy

- Contabo `current_app` → `…/releases/20260714-161852/telegram_stars_shop_bot`
- MAIN synced same release; `SHOP_BOT_POLLING_HOST` **absent**; bot unit inactive
- `REF_BONUS_VPN_ONLY=true` in Contabo `shared/.env`
- Bot log: `Start polling` / `Run polling for bot @AiMonkeyStars_bot` — **no traceback**
- `verify_single_bot.sh` → **ALL OK**
- Health timer enabled: `telegram-bot-api-health.timer` (dry-run OK getMe=200)

## Not in this release

- Separate Bot API IP / SOCKS (`br-x1`) — out of scope
- Token rotation (`br-d4`) — token not rotated; still only in `shared/.env` (0600). Rotate only if leak confirmed.

## Manual smoke (operator in Telegram)

See remaining Cursor ids: `br-a5`, `br-e3`, `rb-r6-smoke`, `cc-4/5`, `pf-4/5`, `ha-5`.
