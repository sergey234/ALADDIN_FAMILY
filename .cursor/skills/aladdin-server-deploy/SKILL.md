---
name: aladdin-server-deploy
description: Deploy and SSH to ALADDIN production backend 149.154.65.180:8002. Use before any server router or family.py changes.
origin: ALADDIN
---

# ALADDIN Server Deploy

Canonical rule: `.cursor/rules/aladdin-server-connection.mdc`  
Guide: `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md`

## Order (mandatory)

1. `curl -s -S -m 8 http://149.154.65.180:8002/api/health` → `{"status":"ok"}`
2. SSH: `ssh -o IdentitiesOnly=yes -i ~/.ssh/aladdin_server root@149.154.65.180`
3. Backup target file on server → `scp` to `/opt/aladdin-backend/app/routers/`
4. `python3 -m py_compile` changed `.py` → restart per guide §10
5. Health curl again

## Do not mix

- `/opt/aladdin-backend` — main iOS API
- `/opt/aladdin-telegram-shop-bot` — bot only (skill `aladdin-telegram-bot-ops`)

No passwords in repo or chat.
