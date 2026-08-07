#!/usr/bin/env python3
"""Merge autofulfill keys into shared/.env (idempotent). Run on server."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

ENV_PATH = Path("/opt/aladdin-telegram-shop-bot/shared/.env")
TEMPLATE_SRC = Path("/opt/aladdin-telegram-shop-bot/current_app/docs/env.autofulfill.prod.template")
TEMPLATE_DST = Path("/opt/aladdin-telegram-shop-bot/shared/env.autofulfill.prod.template")

MERGE = {
    "AUTO_FULFILL_ENABLED": "false",
    "AUTO_FULFILL_STARS_ENABLED": "false",
    "AUTO_FULFILL_PREMIUM_ENABLED": "false",
    "AUTO_FULFILL_MAX_ORDER_RUB": "50000",
    "AUTO_FULFILL_MAX_ATTEMPTS": "5",
    "AUTO_FULFILL_POLL_INTERVAL_SECONDS": "60",
    "AUTO_FULFILL_FAILURE_ALERTS_ENABLED": "true",
    "ISTAR_API_KEY": "",
    "ISTAR_API_BASE": "https://v1.fragmentapi.com/api/v1/partner",
    "ISTAR_WALLET_TYPE": "TON",
    "ISTAR_WEBHOOK_SECRET": "",
    "ISTAR_MIN_TON_BALANCE_ALERT": "0",
    "STUCK_PAID_ALERT_HOURS": "24",
    "STUCK_PAID_CHECK_INTERVAL_SECONDS": "3600",
    "STUCK_PROCESSING_ALERT_MINUTES": "30",
    "OPERATOR_QUEUE_PROCESSING_IDLE_MINUTES": "30",
}
OVERRIDE = {"STUCK_PROCESSING_ALERT_MINUTES"}


def main() -> None:
    text = ENV_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    existing: dict[str, int] = {}
    for i, line in enumerate(lines):
        if "=" in line and not line.strip().startswith("#"):
            k, _, _ = line.partition("=")
            existing[k.strip()] = i

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = ENV_PATH.with_name(".env.bak_" + ts)
    bak.write_text(text, encoding="utf-8")

    added: list[str] = []
    updated: list[str] = []
    for k, v in MERGE.items():
        if k in existing:
            if k in OVERRIDE:
                lines[existing[k]] = f"{k}={v}"
                updated.append(k)
        else:
            lines.append(f"{k}={v}")
            added.append(k)

    if "# --- Автовыдача iStar" not in text:
        lines.extend(["", "# --- Автовыдача iStar (шаблон docs/env.autofulfill.prod.template) ---"])

    ENV_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    if TEMPLATE_SRC.exists():
        TEMPLATE_DST.write_text(TEMPLATE_SRC.read_text(encoding="utf-8"), encoding="utf-8")

    print("backup:", bak)
    print("added:", added)
    print("updated:", updated)


if __name__ == "__main__":
    main()
