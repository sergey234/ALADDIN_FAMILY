#!/usr/bin/env python3
"""Family ops alerts — journal errors + stale prod smoke timestamp.

Cron (see deploy_family_backend.sh):
  python3 scripts/family_ops_alerts.py --check-all

Exit: 0 OK · 2 ALERT · 1 usage error
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

JOURNAL_WINDOW = os.environ.get("FAMILY_ALERT_JOURNAL_MIN", "20")
STALE_SMOKE_MIN = int(os.environ.get("FAMILY_ALERT_STALE_SMOKE_MIN", "45"))
TIMESTAMP_FILE = Path(
    os.environ.get(
        "FAMILY_SMOKE_TIMESTAMP_FILE",
        "/var/lib/aladdin/family_smoke_last_success.timestamp",
    )
)
COOLDOWN_FILE = Path(os.environ.get("FAMILY_ALERT_COOLDOWN_FILE", "/var/lib/aladdin/family_alert_cooldown.json"))
COOLDOWN_SEC = int(os.environ.get("FAMILY_ALERT_COOLDOWN_SEC", "3600"))
ENV_FILE = Path(os.environ.get("ALADDIN_ENV", "/opt/aladdin-telegram-shop-bot/shared/.env"))


def _load_env(path: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def _journal_matches(pattern: str) -> List[str]:
    cmd = [
        "journalctl",
        "-u",
        "aladdin-backend",
        "--since",
        f"{JOURNAL_WINDOW} minutes ago",
        "--no-pager",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [f"journalctl failed: {exc}"]
    lines = []
    for line in (proc.stdout or "").splitlines():
        if pattern in line:
            lines.append(line.strip())
    return lines


def check_family_create_errors() -> Tuple[bool, str, Dict[str, Any]]:
    err_lines = _journal_matches("family_create_error")
    overflow_lines = _journal_matches("integer out of range")
    combined = err_lines + [l for l in overflow_lines if l not in err_lines]
    detail = {"matches": combined[-5:], "count": len(combined)}
    if combined:
        return False, f"ALERT: {len(combined)} family_create/overflow lines in last {JOURNAL_WINDOW}m", detail
    return True, f"OK: no family_create_error in last {JOURNAL_WINDOW}m", detail


def check_smoke_freshness() -> Tuple[bool, str, Dict[str, Any]]:
    if not TIMESTAMP_FILE.is_file():
        return False, f"ALERT: smoke timestamp missing ({TIMESTAMP_FILE})", {"path": str(TIMESTAMP_FILE)}
    raw = TIMESTAMP_FILE.read_text(encoding="utf-8").strip()
    try:
        ts = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
    except ValueError:
        return False, f"ALERT: invalid smoke timestamp {raw!r}", {"path": str(TIMESTAMP_FILE)}
    age_min = (datetime.now(timezone.utc) - ts.astimezone(timezone.utc)).total_seconds() / 60.0
    detail = {"last_success": raw, "age_minutes": round(age_min, 1), "stale_after_min": STALE_SMOKE_MIN}
    if age_min > STALE_SMOKE_MIN:
        return False, f"ALERT: family smoke stale {age_min:.0f}m > {STALE_SMOKE_MIN}m", detail
    return True, f"OK: family smoke fresh ({age_min:.0f}m ago)", detail


def _cooldown_active(key: str) -> bool:
    if not COOLDOWN_FILE.is_file():
        return False
    try:
        data = json.loads(COOLDOWN_FILE.read_text(encoding="utf-8"))
        last = float(data.get(key, 0))
        return (datetime.now(timezone.utc).timestamp() - last) < COOLDOWN_SEC
    except (json.JSONDecodeError, TypeError, ValueError):
        return False


def _mark_cooldown(key: str) -> None:
    COOLDOWN_FILE.parent.mkdir(parents=True, exist_ok=True)
    data: Dict[str, float] = {}
    if COOLDOWN_FILE.is_file():
        try:
            data = json.loads(COOLDOWN_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
    data[key] = datetime.now(timezone.utc).timestamp()
    COOLDOWN_FILE.write_text(json.dumps(data), encoding="utf-8")


def _telegram_notify(text: str) -> None:
    env = _load_env(ENV_FILE)
    token = env.get("ALERT_TELEGRAM_BOT_TOKEN") or env.get("BOT_TOKEN")
    chat_id = env.get("ALERT_TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("WARN: Telegram alert skipped (no ALERT_TELEGRAM_* in env)", file=sys.stderr)
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = urllib.parse.urlencode(
        {"chat_id": chat_id, "text": text[:4000], "disable_web_page_preview": "true"}
    ).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    with urllib.request.urlopen(req, timeout=15):
        pass


def run_checks(which: str, notify: bool) -> int:
    checks: List[Tuple[str, Any]] = []
    if which in ("all", "journal"):
        checks.append(("family_create_journal", check_family_create_errors))
    if which in ("all", "smoke"):
        checks.append(("family_smoke_freshness", check_smoke_freshness))

    results: Dict[str, Any] = {"checks": {}, "pass": True}
    exit_code = 0
    alert_messages: List[str] = []

    for name, fn in checks:
        ok, msg, detail = fn()
        results["checks"][name] = {"ok": ok, "message": msg, "detail": detail}
        print(f"{'OK' if ok else 'ALERT'}  {msg}")
        if not ok:
            results["pass"] = False
            exit_code = 2
            alert_messages.append(msg)

    print(json.dumps(results, ensure_ascii=False, indent=2))

    if alert_messages and notify and not _cooldown_active("family_ops"):
        try:
            _telegram_notify("ALADDIN family ops\n" + "\n".join(alert_messages))
            _mark_cooldown("family_ops")
        except Exception as exc:
            print(f"WARN: telegram notify failed: {exc}", file=sys.stderr)

    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description="Family ops alerts")
    parser.add_argument("--check-all", action="store_true")
    parser.add_argument("--check-journal", action="store_true")
    parser.add_argument("--check-smoke", action="store_true")
    parser.add_argument("--notify", action="store_true", help="Send Telegram on ALERT (respects cooldown)")
    args = parser.parse_args()

    if args.check_journal:
        which = "journal"
    elif args.check_smoke:
        which = "smoke"
    elif args.check_all:
        which = "all"
    else:
        parser.print_help()
        return 1

    return run_checks(which, notify=args.notify)


if __name__ == "__main__":
    raise SystemExit(main())
