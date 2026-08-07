# Agent rules: Contabo My Machines / mobile

- Work only in this repo checkout. Do NOT edit `/opt/aladdin-telegram-shop-bot/current_app`.
- Do NOT read or modify `/opt/aladdin-telegram-shop-bot/shared/.env`.
- Do NOT run destructive DB commands (DELETE/DROP/UPDATE without where).
- Do NOT `rm -rf`, reformat disks, or change firewall.
- Do NOT `systemctl stop/restart` production services unless user says exactly: GO DEPLOY.
- Default mode: branch + PR only. Prod is read-only until GO DEPLOY.
- SSH hops: `vpn-entry` (37.46.134.98), `vpn-spare` (149.154.65.180) — prefer read-only diagnostics.
