#!/usr/bin/env python3
"""One-shot on prod: Alertmanager + Prometheus alerting → Telegram (ops chat)."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

BOT_ENV = Path("/opt/aladdin-telegram-shop-bot/shared/.env")
PROM = Path("/etc/prometheus/prometheus.yml")
AM = Path("/etc/prometheus/alertmanager.yml")
AM_DEFAULT = Path("/etc/default/prometheus-alertmanager")


def load_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def main() -> int:
    env = load_env(BOT_ENV)
    token = env.get("ALERT_TELEGRAM_BOT_TOKEN", "")
    chat = env.get("ALERT_TELEGRAM_CHAT_ID", "")
    if not token or not chat:
        print("ERROR: set ALERT_TELEGRAM_BOT_TOKEN and ALERT_TELEGRAM_CHAT_ID in shared/.env", file=sys.stderr)
        return 1

    AM.write_text(
        f"""global:
  resolve_timeout: 5m

route:
  receiver: telegram-ops
  group_by: [alertname, service]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 6h

inhibit_rules:
  - source_matchers: [severity="critical"]
    target_matchers: [severity="warning"]
    equal: [alertname, service]

receivers:
  - name: telegram-ops
    telegram_configs:
      - bot_token: '{token}'
        chat_id: {chat}
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
        "# ALADDIN single-node Alertmanager\n"
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
    print("OK: alertmanager + prometheus alerting")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
