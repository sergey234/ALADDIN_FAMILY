#!/usr/bin/env python3
"""
Alertmanager: два Telegram receiver (Shop vs ALADDIN iOS).

Shop + VPN API  → ALERT_TELEGRAM_* (@AiMonkeyStars_bot)
ALADDIN gateway  → ALADDIN_FEEDBACK_TELEGRAM_* (@AladdinChatAI_bot / AladdinAi_bot)
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SHOP_ENV = Path("/opt/aladdin-telegram-shop-bot/shared/.env")
ALADDIN_ENV = Path("/etc/aladdin-backend/feedback-telegram.env")
PROM = Path("/etc/prometheus/prometheus.yml")
AM = Path("/etc/prometheus/alertmanager.yml")
AM_DEFAULT = Path("/etc/default/prometheus-alertmanager")


def load_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def main() -> int:
    shop = load_env(SHOP_ENV)
    aladdin = load_env(ALADDIN_ENV)

    shop_token = shop.get("ALERT_TELEGRAM_BOT_TOKEN") or shop.get("BOT_TOKEN", "")
    shop_chat = shop.get("ALERT_TELEGRAM_CHAT_ID", "")

    aladdin_token = (
        aladdin.get("ALADDIN_FEEDBACK_TELEGRAM_BOT_TOKEN")
        or aladdin.get("ALADDIN_ALERT_TELEGRAM_BOT_TOKEN")
        or aladdin.get("ALADDIN_AI_BOT_TOKEN", "")
    )
    aladdin_chat = (
        aladdin.get("ALADDIN_FEEDBACK_TELEGRAM_CHAT_ID")
        or aladdin.get("ALADDIN_ALERT_TELEGRAM_CHAT_ID")
        or shop_chat
    )

    if not shop_token or not shop_chat:
        print("ERROR: shop ALERT_TELEGRAM_BOT_TOKEN / CHAT_ID missing", file=sys.stderr)
        return 1
    if not aladdin_token or not aladdin_chat:
        print(
            "ERROR: ALADDIN bot token missing "
            "(set ALADDIN_FEEDBACK_TELEGRAM_BOT_TOKEN in feedback-telegram.env)",
            file=sys.stderr,
        )
        return 1

    AM.write_text(
        f"""global:
  resolve_timeout: 5m

route:
  receiver: telegram-aladdin
  group_by: [alertname, service, domain]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 6h
  routes:
    - matchers:
        - alertname=~"AladdinShopVpn.*"
      receiver: telegram-shop
      continue: false
    - matchers:
        - service="aladdin-shop-vpn-api"
      receiver: telegram-shop
      continue: false
    - matchers:
        - alertname=~"AladdinNoFreshData.*|AladdinAPILatency.*|Aladdin5xx.*"
      receiver: telegram-aladdin
      continue: false
    - matchers:
        - job="gateway"
      receiver: telegram-aladdin
      continue: false

inhibit_rules:
  - source_matchers: [severity="critical"]
    target_matchers: [severity="warning"]
    equal: [alertname, service]

receivers:
  - name: telegram-shop
    telegram_configs:
      - bot_token: '{shop_token}'
        chat_id: {shop_chat}
        send_resolved: true
        parse_mode: HTML
  - name: telegram-aladdin
    telegram_configs:
      - bot_token: '{aladdin_token}'
        chat_id: {aladdin_chat}
        send_resolved: true
        parse_mode: HTML
""",
        encoding="utf-8",
    )

    text = PROM.read_text(encoding="utf-8")
    if "alerting:" not in text:
        out: list[str] = []
        inserted = False
        for line in text.splitlines():
            out.append(line)
            if not inserted and line.strip() == "scrape_interval: 15s":
                out.extend(
                    [
                        "",
                        "alerting:",
                        "  alertmanagers:",
                        "    - static_configs:",
                        '        - targets: ["127.0.0.1:9093"]',
                    ]
                )
                inserted = True
        PROM.write_text("\n".join(out) + "\n", encoding="utf-8")

    AM_DEFAULT.write_text(
        "# ALADDIN split Alertmanager (shop + aladdin iOS)\n"
        'ARGS="--config.file=/etc/prometheus/alertmanager.yml '
        "--storage.path=/var/lib/prometheus/alertmanager "
        "--web.listen-address=127.0.0.1:9093 "
        '--cluster.listen-address="\n',
        encoding="utf-8",
    )

    subprocess.run(["promtool", "check", "config", str(PROM)], check=True)
    subprocess.run(["amtool", "check-config", str(AM)], check=True)
    subprocess.run(["systemctl", "reset-failed", "prometheus-alertmanager.service"], check=False)
    subprocess.run(["systemctl", "restart", "prometheus-alertmanager.service"], check=True)
    subprocess.run(["systemctl", "restart", "prometheus.service"], check=True)
    print("OK: alertmanager split (telegram-shop + telegram-aladdin)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
