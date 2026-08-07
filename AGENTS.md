# Agent Operating Contract (Mac-first, Safe Mode)

This repository is used with Cursor Cloud Agents and My Machines.
Follow these rules for every task unless the user explicitly overrides them.

## 1) Scope of edits

- Edit code only inside repository working copies.
- Do **not** edit live production directories directly.
- Expected bot project path (when present in this repo):
  - `ALADDIN_NEW/mobile_apps/ALADDIN_iOS/telegram_stars_shop_bot/`

## 2) Production safety boundaries

- Treat this path as **read-only** context:
  - `/opt/aladdin-telegram-shop-bot/current_app`
- Never read or modify production secrets:
  - `/opt/aladdin-telegram-shop-bot/shared/.env`
- Never run destructive DB operations on production DB:
  - `/opt/aladdin-telegram-shop-bot/data/shop.db`

## 3) Forbidden actions without explicit approval

Do not run these unless the user sends explicit approval text:

- `rm -rf` (any target)
- SQL destructive operations (`DROP`, `DELETE`, destructive migrations)
- `systemctl stop`, `systemctl restart`, `docker compose down`
- Any deploy command that changes production runtime

Required deployment approval phrase:

- `GO DEPLOY`

If this phrase is missing, stay in "code + tests + PR only" mode.

## 4) Git workflow

- Work from a feature branch only.
- Open/update a PR for each change set.
- Do not merge to `main` from agent tasks.
- Keep commits scoped and reversible.

## 5) Secrets and config

- Never commit secrets, tokens, `.env` values, private keys, or credentials.
- Use placeholders in docs and examples.
- If a secret is required, ask user to provide it locally on their machine.

## 6) Preferred execution mode

- Mac-first workflow is default.
- Contabo worker setup is a later step and must run as `cursor-agent` user, never as `root`.

## 7) Infrastructure map (project facts)

Known servers:

1. `185.225.233.150` (Contabo): bot, partner-api, `shop.db`, vpn-api
2. `37.46.134.98`: VPN entry (RU)
3. `149.154.65.180`: backup/legacy entry

Important access note:

- SSH aliases on the user's Mac (for example `aladdin-contabo`, `aladdin-server`) are local to that Mac.
- They are **not** automatically available to cloud agents.

## 8) Access model expectations

Capability matrix:

- Cloud Agent + GitHub only:
  - can modify code and open PRs
  - cannot directly access Contabo
  - cannot access all 3 servers
- My Machines / Remote Control on Mac (Mac already has SSH):
  - can work with bot code
  - can access Contabo through Mac
  - can access all 3 servers if Mac SSH is configured for all 3
- Worker on Contabo:
  - can work in clone on that host
  - can manage that host only
  - cannot access servers #2 and #3 until SSH from Contabo is configured

## 9) Privilege model (least privilege mandatory)

- Do not use broad root access for routine agent work.
- Prefer dedicated SSH key(s) for automation and restrict scope per host.
- Use `cursor-agent` OS user for operational actions; avoid `root` sessions for edits.
- Grant only minimal required sudo commands (allow-list), not full sudo.
- Treat deployment as a controlled step gated by `GO DEPLOY` and explicit human confirmation.
