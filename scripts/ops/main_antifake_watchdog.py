#!/usr/bin/env python3
"""External watchdog for MAIN :8002 Antifake — runs on Brain, alerts via Telegram from Brain.

Alerts go to the ALADDIN bot (ALADDIN_FEEDBACK_TELEGRAM_* in /etc/aladdin-ops/main-watchdog.env, 0600),
same split as aladdin_shop_vpn_api/deploy/scripts/fix_alertmanager_telegram_split.py.

Why off-box: Telegram Bot API POST times out from MAIN (Russia), so on-box alerts never arrived
(incident 2026-11-06), and an on-box monitor cannot report MAIN itself being down.

Cron on Brain (every 5 min):
  */5 * * * * /usr/bin/python3 /opt/aladdin-ops/main_antifake_watchdog.py >> /var/log/aladdin-main-watchdog.log 2>&1

Exit: 0 healthy · 2 degraded · 1 config error. Stdlib only.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple

BASE = os.environ.get("MAIN_WATCHDOG_BASE", "http://149.154.65.180:8002").rstrip("/")
STATE_FILE = Path(os.environ.get("MAIN_WATCHDOG_STATE", "/var/lib/aladdin/main_antifake_watchdog.json"))
# ALADDIN channel only (@AladdinChatAI_bot). Never ALERT_TELEGRAM_* / BOT_TOKEN — that is AiMonkey shop.
ENV_FILE = Path(os.environ.get("MAIN_WATCHDOG_ENV", "/etc/aladdin-ops/main-watchdog.env"))
TOKEN_KEY = "ALADDIN_FEEDBACK_TELEGRAM_BOT_TOKEN"
CHAT_KEY = "ALADDIN_FEEDBACK_TELEGRAM_CHAT_ID"
FAILS_BEFORE_ALERT = int(os.environ.get("MAIN_WATCHDOG_FAILS_BEFORE_ALERT", "2"))
REALERT_SEC = int(os.environ.get("MAIN_WATCHDOG_REALERT_SEC", "3600"))
TIMEOUT_SEC = 10


def _get_json(path: str) -> Tuple[bool, Dict]:
    try:
        with urllib.request.urlopen(BASE + path, timeout=TIMEOUT_SEC) as resp:
            return resp.status == 200, json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:
        return False, {"http": exc.code}
    except Exception as exc:
        return False, {"error": type(exc).__name__}


def probe() -> List[str]:
    problems: List[str] = []
    ok, body = _get_json("/api/health")
    if not ok or body.get("status") != "ok":
        problems.append(f"api_health_down {body}")
        return problems
    ok, body = _get_json("/api/antifake/pipeline-health")
    if not ok:
        problems.append(f"pipeline_health_unreachable {body}")
    elif body.get("status") != "ok":
        problems.extend(str(p) for p in body.get("problems") or ["degraded"])
    return problems


def _load_env(path: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def notify(text: str) -> bool:
    env = _load_env(ENV_FILE)
    token = env.get(TOKEN_KEY)
    chat_id = env.get(CHAT_KEY)
    if not token or not chat_id:
        print(f"ERROR: {TOKEN_KEY} / {CHAT_KEY} missing in {ENV_FILE}", file=sys.stderr)
        return False
    body = urllib.parse.urlencode(
        {"chat_id": chat_id, "text": text[:4000], "disable_web_page_preview": "true"}
    ).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=body, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15):
            return True
    except Exception as exc:
        print(f"ERROR: telegram send failed: {type(exc).__name__}", file=sys.stderr)
        return False


def _load_state() -> Dict:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"fails": 0, "alerted_at": 0.0, "alerting": False}


def _save_state(state: Dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state), encoding="utf-8")


def step(state: Dict, problems: List[str], now: float) -> Tuple[Dict, str]:
    """Pure transition: returns (new_state, message_to_send or "")."""
    state = dict(state)
    if not problems:
        message = "✅ ALADDIN MAIN Antifake восстановлен — проверки снова проходят" if state.get("alerting") else ""
        return {"fails": 0, "alerted_at": 0.0, "alerting": False}, message
    state["fails"] = int(state.get("fails", 0)) + 1
    due = now - float(state.get("alerted_at", 0.0)) >= REALERT_SEC
    if state["fails"] >= FAILS_BEFORE_ALERT and (not state.get("alerting") or due):
        state["alerting"] = True
        state["alerted_at"] = now
        return state, (
            "🚨 ALADDIN MAIN (…180) Antifake: проверки у пользователей не работают\n"
            f"Проблемы: {', '.join(problems)}\n"
            f"Подряд провалов: {state['fails']}\n"
            "Runbook: docs/ops-memory/incidents/2026-11-06__antifake_worker_no_env__media_jobs_dead.md"
        )
    return state, ""


def main() -> int:
    problems = probe()
    state, message = step(_load_state(), problems, time.time())
    if message and not notify(message):
        state["alerted_at"] = 0.0  # retry on next run instead of waiting REALERT_SEC
    _save_state(state)
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print(f"{stamp} {'OK' if not problems else 'DEGRADED ' + ', '.join(problems)} fails={state['fails']}")
    return 0 if not problems else 2


if __name__ == "__main__":
    raise SystemExit(main())
