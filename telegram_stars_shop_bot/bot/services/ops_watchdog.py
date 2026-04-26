from __future__ import annotations

import asyncio
import json
import re
import subprocess
import time
from pathlib import Path

import aiosqlite
import httpx

from bot.config import Settings, load_settings
from bot.services.alerts import send_alert

_STATE_FILE = Path("/tmp/aladdin_ops_watchdog_state.json")
_SERVICE_NAMES = (
    "aladdin-telegram-bot.service",
    "aladdin-partner-api.service",
    "aladdin-webhook-worker.service",
)
_ERROR_PATTERNS = (
    re.compile(r"Traceback", re.IGNORECASE),
    re.compile(r"TelegramBadRequest", re.IGNORECASE),
    re.compile(r"ERROR:", re.IGNORECASE),
    re.compile(r"Cause exception while process update", re.IGNORECASE),
)
_REDIS_FALLBACK_MARKERS = (
    "rate_limit_redis_connect_failed_fallback_memory",
    "rate_limit_redis_runtime_failed_fallback_memory",
)


def _load_state() -> dict:
    if not _STATE_FILE.exists():
        return {"problems": {}, "last_heartbeat_ts": 0.0}
    try:
        return json.loads(_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"problems": {}, "last_heartbeat_ts": 0.0}


def _save_state(state: dict) -> None:
    _STATE_FILE.write_text(json.dumps(state, ensure_ascii=True), encoding="utf-8")


def _systemd_active(service_name: str) -> bool:
    proc = subprocess.run(
        ["systemctl", "is-active", service_name],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode == 0 and proc.stdout.strip() == "active"


async def _health_ok() -> tuple[bool, str]:
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.get("http://127.0.0.1:8090/health")
        if r.status_code != 200:
            return False, f"status={r.status_code}"
        body = r.text.strip()
        if '"status":"ok"' not in body.replace(" ", ""):
            return False, f"unexpected_body={body[:200]}"
        return True, "ok"
    except Exception as e:
        return False, f"exception={type(e).__name__}:{e}"


def _count_recent_errors(log_path: Path, lines_to_scan: int) -> int:
    if not log_path.exists():
        return 0
    lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()[-max(10, lines_to_scan) :]
    cnt = 0
    for line in lines:
        if any(p.search(line) for p in _ERROR_PATTERNS):
            cnt += 1
    return cnt


def _has_recent_redis_fallback(partner_log_path: Path, lines_to_scan: int) -> bool:
    if not partner_log_path.exists():
        return False
    lines = partner_log_path.read_text(encoding="utf-8", errors="ignore").splitlines()[-max(10, lines_to_scan) :]
    return any(any(marker in line for marker in _REDIS_FALLBACK_MARKERS) for line in lines)


async def _webhook_backlog_count(db_path: Path) -> int:
    if not db_path.exists():
        return 0
    try:
        async with aiosqlite.connect(db_path) as conn:
            cur = await conn.execute(
                "SELECT COUNT(*) FROM outbound_webhook_events WHERE status IN ('pending','failed')"
            )
            row = await cur.fetchone()
            return int(row[0] if row else 0)
    except Exception:
        return 0


async def _emit_problem_or_recovery(
    settings: Settings,
    state: dict,
    *,
    check_name: str,
    is_problem_now: bool,
    severity_problem: str,
    problem_body: str,
    recovery_body: str,
) -> None:
    prev = bool(state.get("problems", {}).get(check_name, False))
    if is_problem_now and not prev:
        await send_alert(
            settings=settings,
            severity=severity_problem,
            title=f"PROBLEM: {check_name}",
            body=problem_body,
            dedupe_key=f"watchdog_problem:{check_name}",
        )
    elif (not is_problem_now) and prev:
        await send_alert(
            settings=settings,
            severity="info",
            title=f"RECOVERY: {check_name}",
            body=recovery_body,
            dedupe_key=f"watchdog_recovery:{check_name}",
        )
    state.setdefault("problems", {})[check_name] = is_problem_now


async def run_watchdog_once(settings: Settings) -> None:
    state = _load_state()
    log_lines = max(50, int(settings.ops_watchdog_log_scan_lines))
    burst_threshold = max(1, int(settings.ops_watchdog_error_burst_threshold))
    backlog_warn = max(1, int(settings.ops_watchdog_webhook_backlog_warn))
    heartbeat_every = max(300, int(settings.ops_heartbeat_interval_seconds))

    for svc in _SERVICE_NAMES:
        ok = _systemd_active(svc)
        await _emit_problem_or_recovery(
            settings,
            state,
            check_name=f"service:{svc}",
            is_problem_now=not ok,
            severity_problem="critical",
            problem_body=f"{svc} is NOT active",
            recovery_body=f"{svc} is active again",
        )

    health_ok, health_info = await _health_ok()
    await _emit_problem_or_recovery(
        settings,
        state,
        check_name="partner_api_health",
        is_problem_now=not health_ok,
        severity_problem="critical",
        problem_body=f"/health failed: {health_info}",
        recovery_body="/health is healthy again",
    )

    bot_log_path = settings.database_path.parent / "logs" / "bot.log"
    if not bot_log_path.exists():
        bot_log_path = Path("/opt/aladdin-telegram-shop-bot/logs/bot.log")
    error_cnt = _count_recent_errors(bot_log_path, log_lines)
    await _emit_problem_or_recovery(
        settings,
        state,
        check_name="bot_log_error_burst",
        is_problem_now=error_cnt >= burst_threshold,
        severity_problem="warning",
        problem_body=f"error burst in bot.log: errors={error_cnt} scan_lines={log_lines}",
        recovery_body=f"bot.log error burst recovered: errors={error_cnt}",
    )

    partner_log_path = settings.database_path.parent / "logs" / "partner_api.log"
    if not partner_log_path.exists():
        partner_log_path = Path("/opt/aladdin-telegram-shop-bot/logs/partner_api.log")
    redis_fb = _has_recent_redis_fallback(partner_log_path, log_lines)
    await _emit_problem_or_recovery(
        settings,
        state,
        check_name="redis_fallback_memory",
        is_problem_now=redis_fb,
        severity_problem="warning",
        problem_body="rate-limit redis fallback to memory detected in recent logs",
        recovery_body="no recent redis fallback markers",
    )

    backlog = await _webhook_backlog_count(settings.database_path)
    await _emit_problem_or_recovery(
        settings,
        state,
        check_name="webhook_backlog",
        is_problem_now=backlog >= backlog_warn,
        severity_problem="warning",
        problem_body=f"outbound webhook backlog high: count={backlog} threshold={backlog_warn}",
        recovery_body=f"outbound webhook backlog recovered: count={backlog}",
    )

    any_problem = any(bool(v) for v in state.get("problems", {}).values())
    now = time.time()
    last_hb = float(state.get("last_heartbeat_ts", 0.0) or 0.0)
    if (not any_problem) and (now - last_hb >= heartbeat_every):
        await send_alert(
            settings=settings,
            severity="info",
            title="OK: ops heartbeat",
            body=(
                "services=active; partner_api_health=ok; "
                f"bot_log_errors={error_cnt}; webhook_backlog={backlog}"
            ),
            dedupe_key="watchdog_heartbeat_ok",
        )
        state["last_heartbeat_ts"] = now

    _save_state(state)


async def _main() -> None:
    settings = load_settings()
    if not settings.ops_watchdog_enabled:
        return
    await run_watchdog_once(settings)


if __name__ == "__main__":
    asyncio.run(_main())
