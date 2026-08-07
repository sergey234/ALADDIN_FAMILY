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
from bot.services import admin_stats_repo
from bot.services.alerts import send_alert

_STATE_FILE = Path("/tmp/aladdin_ops_watchdog_state.json")
_SERVICE_NAMES = (
    "aladdin-telegram-bot.service",
    "aladdin-partner-api.service",
    "aladdin-webhook-worker.service",
)


def _watchdog_service_names(settings: Settings) -> tuple[str, ...]:
    """На MAIN без polling не проверяем telegram-bot (иначе ложный CRITICAL и риск «починить» вторым инстансом)."""
    if settings.shop_bot_polling_enabled:
        return _SERVICE_NAMES
    return tuple(s for s in _SERVICE_NAMES if s != "aladdin-telegram-bot.service")


_ERROR_PATTERNS = (
    re.compile(r"ERROR:", re.IGNORECASE),
)
_TG_TIMEOUT_PATTERNS = (
    re.compile(r"TelegramNetworkError", re.IGNORECASE),
    re.compile(r"Request timeout", re.IGNORECASE),
)
_BENIGN_ERROR_MARKERS = (
    "message is not modified",
)


def _is_benign_log_line(line: str) -> bool:
    low = line.lower()
    return any(marker in low for marker in _BENIGN_ERROR_MARKERS)


def _count_recent_errors(log_path: Path, lines_to_scan: int) -> int:
    if not log_path.exists():
        return 0
    lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()[-max(10, lines_to_scan) :]
    cnt = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        low = line.lower()
        if "cause exception while process update" in low:
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            if _is_benign_log_line(nxt):
                i += 2
                while i < len(lines) and not re.match(
                    r"^(INFO|WARNING|ERROR|DEBUG):", lines[i], re.IGNORECASE
                ):
                    i += 1
                continue
        if _is_benign_log_line(line):
            i += 1
            continue
        if any(p.search(line) for p in _ERROR_PATTERNS):
            cnt += 1
        i += 1
    return cnt


def _count_telegram_timeouts(log_path: Path, lines_to_scan: int) -> int:
    """Отдельный счётчик TelegramNetworkError / Request timeout (br-d2)."""
    if not log_path.exists():
        return 0
    lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()[-max(10, lines_to_scan) :]
    return sum(1 for line in lines if any(p.search(line) for p in _TG_TIMEOUT_PATTERNS))


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


def _evaluate_kpi_thresholds(
    *,
    settings: Settings,
    days: int,
    payment: dict[str, float | int],
    webhook: dict[str, float | int],
    retention: dict[str, float | int],
    acquisition: dict[str, float | int],
) -> dict[str, tuple[bool, str, str]]:
    checks: dict[str, tuple[bool, str, str]] = {}

    created_n = int(payment.get("funnel_created_orders", 0) or 0)
    paid_rate = float(payment.get("funnel_paid_rate_pct", 0.0) or 0.0)
    payment_problem = (
        created_n >= max(1, int(settings.ops_alert_payment_min_created_orders))
        and paid_rate < float(settings.ops_alert_payment_success_min_pct)
    )
    checks["kpi_payment_success_rate"] = (
        payment_problem,
        (
            f"payment success low: paid_rate={paid_rate:.2f}% "
            f"threshold={float(settings.ops_alert_payment_success_min_pct):.2f}% "
            f"created={created_n} window={days}d"
        ),
        f"payment success recovered: paid_rate={paid_rate:.2f}% created={created_n} window={days}d",
    )

    webhook_total = int(webhook.get("webhook_total", 0) or 0)
    webhook_success = float(webhook.get("webhook_success_rate_pct", 0.0) or 0.0)
    webhook_p95 = float(webhook.get("webhook_latency_p95_sec", -1.0) or -1.0)
    webhook_problem = False
    if webhook_total >= max(1, int(settings.ops_alert_webhook_min_events)):
        if webhook_success < float(settings.ops_alert_webhook_success_min_pct):
            webhook_problem = True
        p95_max = float(settings.ops_alert_webhook_p95_max_sec)
        if p95_max > 0 and webhook_p95 >= 0 and webhook_p95 > p95_max:
            webhook_problem = True
    checks["kpi_webhook_sla"] = (
        webhook_problem,
        (
            f"webhook SLA degraded: success={webhook_success:.2f}% "
            f"(min {float(settings.ops_alert_webhook_success_min_pct):.2f}%), "
            f"p95={webhook_p95:.3f}s (max {float(settings.ops_alert_webhook_p95_max_sec):.3f}s), "
            f"events={webhook_total} window={days}d"
        ),
        (
            f"webhook SLA recovered: success={webhook_success:.2f}% "
            f"p95={webhook_p95:.3f}s events={webhook_total} window={days}d"
        ),
    )

    cohort_n = int(retention.get("retention_cohort_size", 0) or 0)
    d7 = float(retention.get("retention_d7_pct", 0.0) or 0.0)
    retention_problem = (
        cohort_n >= max(1, int(settings.ops_alert_retention_min_cohort))
        and d7 < float(settings.ops_alert_retention_d7_min_pct)
    )
    checks["kpi_retention_d7"] = (
        retention_problem,
        (
            f"retention D7 low: d7={d7:.2f}% "
            f"threshold={float(settings.ops_alert_retention_d7_min_pct):.2f}% "
            f"cohort={cohort_n} window={days}d"
        ),
        f"retention D7 recovered: d7={d7:.2f}% cohort={cohort_n} window={days}d",
    )

    cac_max = float(settings.ops_alert_cac_max_rub)
    paid_users = int(acquisition.get("acq_paid_users", 0) or 0)
    cac = float(acquisition.get("acq_cac_rub", 0.0) or 0.0)
    cac_problem = (
        cac_max > 0
        and paid_users >= max(1, int(settings.ops_alert_cac_min_paid_users))
        and cac > cac_max
    )
    checks["kpi_cac"] = (
        cac_problem,
        (
            f"CAC high: cac={cac:.2f} ₽ threshold={cac_max:.2f} ₽ "
            f"paid_users={paid_users} window={days}d"
        ),
        f"CAC recovered: cac={cac:.2f} ₽ paid_users={paid_users} window={days}d",
    )
    return checks


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

    for svc in _watchdog_service_names(settings):
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

    tg_timeout_cnt = _count_telegram_timeouts(bot_log_path, log_lines)
    await _emit_problem_or_recovery(
        settings,
        state,
        check_name="telegram_network_timeout_burst",
        is_problem_now=tg_timeout_cnt >= burst_threshold,
        severity_problem="warning",
        problem_body=(
            f"TelegramNetworkError/timeout burst in bot.log: count={tg_timeout_cnt} "
            f"scan_lines={log_lines} (see also getMe health timer)"
        ),
        recovery_body=f"telegram timeout burst recovered: count={tg_timeout_cnt}",
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

    kpi_days = int(settings.ops_watchdog_kpi_days)
    if kpi_days > 0 and settings.database_path.exists():
        try:
            async with aiosqlite.connect(settings.database_path) as kpi_conn:
                kpi_conn.row_factory = aiosqlite.Row
                payment = await admin_stats_repo.payment_funnel_metrics(kpi_conn, days=kpi_days)
                webhook = await admin_stats_repo.webhook_sla_metrics(kpi_conn, days=kpi_days)
                retention = await admin_stats_repo.retention_metrics(kpi_conn, days=kpi_days)
                acquisition = await admin_stats_repo.acquisition_metrics(kpi_conn, days=kpi_days)
            kpi_checks = _evaluate_kpi_thresholds(
                settings=settings,
                days=kpi_days,
                payment=payment,
                webhook=webhook,
                retention=retention,
                acquisition=acquisition,
            )
            for check_name, (is_problem, problem_body, recovery_body) in kpi_checks.items():
                await _emit_problem_or_recovery(
                    settings,
                    state,
                    check_name=check_name,
                    is_problem_now=is_problem,
                    severity_problem="warning",
                    problem_body=problem_body,
                    recovery_body=recovery_body,
                )
        except Exception:
            await _emit_problem_or_recovery(
                settings,
                state,
                check_name="kpi_metrics_fetch",
                is_problem_now=True,
                severity_problem="warning",
                problem_body=f"failed to collect KPI metrics for watchdog window={kpi_days}d",
                recovery_body="KPI metrics collection restored",
            )
    else:
        state.setdefault("problems", {})["kpi_metrics_fetch"] = False

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
