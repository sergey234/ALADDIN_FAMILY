#!/usr/bin/env python3
"""Shop ops: ALERT_TELEGRAM_* = BOT_TOKEN (@AiMonkeyStars_bot). Alertmanager split — fix_alertmanager_telegram_split.py."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

BOT_ENV = Path("/opt/aladdin-telegram-shop-bot/shared/.env")
FIX_AM = Path("/opt/aladdin-shop-vpn-api/deploy/scripts/fix_alertmanager_telegram.py")


def main() -> int:
    if not BOT_ENV.is_file():
        print(f"ERROR: missing {BOT_ENV}", file=sys.stderr)
        return 1

    lines = BOT_ENV.read_text(encoding="utf-8").splitlines()
    env: dict[str, str] = {}
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

    shop = env.get("BOT_TOKEN", "").strip()
    alert = env.get("ALERT_TELEGRAM_BOT_TOKEN", "").strip()
    chat = env.get("ALERT_TELEGRAM_CHAT_ID", "").strip()

    if not shop:
        print("ERROR: BOT_TOKEN empty in shared/.env", file=sys.stderr)
        return 1
    if not chat:
        print("ERROR: ALERT_TELEGRAM_CHAT_ID empty — set your Telegram user/group id once", file=sys.stderr)
        return 1

    if shop == alert:
        print("OK: ALERT_TELEGRAM_BOT_TOKEN already matches BOT_TOKEN")
    else:
        out: list[str] = []
        replaced = False
        for line in lines:
            if line.strip().startswith("ALERT_TELEGRAM_BOT_TOKEN="):
                out.append(f"ALERT_TELEGRAM_BOT_TOKEN={shop}")
                replaced = True
            else:
                out.append(line)
        if not replaced:
            out.append(f"ALERT_TELEGRAM_BOT_TOKEN={shop}")
        backup = BOT_ENV.with_suffix(f".env.bak.sync-alert.{subprocess.check_output(['date', '+%Y%m%d_%H%M%S'], text=True).strip()}")
        backup.write_text(BOT_ENV.read_text(encoding="utf-8"), encoding="utf-8")
        BOT_ENV.write_text("\n".join(out) + "\n", encoding="utf-8")
        print(f"OK: ALERT_TELEGRAM_BOT_TOKEN synced from BOT_TOKEN (backup {backup.name})")

    split = Path("/opt/aladdin-shop-vpn-api/deploy/scripts/fix_alertmanager_telegram_split.py")
    if split.is_file():
        subprocess.run([sys.executable, str(split)], check=True)
    elif FIX_AM.is_file():
        subprocess.run([sys.executable, str(FIX_AM)], check=True)
    else:
        print("WARN: fix_alertmanager_telegram_split.py not found", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
