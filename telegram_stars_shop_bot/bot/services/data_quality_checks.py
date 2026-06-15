from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path

import aiosqlite

from bot.config import Settings, load_settings
from bot.services.alerts import send_alert

logger = logging.getLogger(__name__)

_STATE_FILE = Path("/tmp/aladdin_data_quality_state.json")


def _load_state() -> dict:
    if not _STATE_FILE.exists():
        return {"problems": {}}
    try:
        return json.loads(_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"problems": {}}


def _save_state(state: dict) -> None:
    _STATE_FILE.write_text(json.dumps(state, ensure_ascii=True), encoding="utf-8")


async def _emit_problem_or_recovery(
    settings: Settings,
    state: dict,
    *,
    check_name: str,
    is_problem_now: bool,
    problem_body: str,
    recovery_body: str,
) -> None:
    prev = bool(state.get("problems", {}).get(check_name, False))
    if is_problem_now and not prev:
        await send_alert(
            settings=settings,
            severity="warning",
            title=f"PROBLEM: data_quality:{check_name}",
            body=problem_body,
            dedupe_key=f"dq_problem:{check_name}",
        )
    elif (not is_problem_now) and prev:
        await send_alert(
            settings=settings,
            severity="info",
            title=f"RECOVERY: data_quality:{check_name}",
            body=recovery_body,
            dedupe_key=f"dq_recovery:{check_name}",
        )
    state.setdefault("problems", {})[check_name] = is_problem_now


async def _query_snapshot(conn: aiosqlite.Connection, days: int) -> dict[str, float | int]:
    p = (f"-{max(1, int(days))} days",)
    cur = await conn.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN status='completed' AND TRIM(COALESCE(product_kind,''))='' THEN 1 ELSE 0 END),0) AS missing_kind,
            COALESCE(SUM(CASE WHEN status='completed' AND profit_snapshot_at IS NULL THEN 1 ELSE 0 END),0) AS missing_profit,
            COALESCE(SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END),0) AS completed_total
        FROM orders
        WHERE date(COALESCE(completed_at, updated_at)) >= date('now', ?)
        """,
        p,
    )
    a = await cur.fetchone()
    cur = await conn.execute(
        """
        SELECT
            COUNT(*) AS all_n,
            COALESCE(SUM(CASE WHEN meta_json LIKE '%"schema_version":"v2"%' THEN 1 ELSE 0 END),0) AS v2_n
        FROM analytics_events
        WHERE date(created_at) >= date('now', ?)
          AND event_type IN ('offer_impression','offer_click','checkout_start','checkout_paid','order_completed','order_created')
        """,
        p,
    )
    b = await cur.fetchone()
    cur = await conn.execute(
        """
        SELECT
            COUNT(DISTINCT o.user_id) AS paid_users_total,
            COALESCE(SUM(
                CASE
                    WHEN COALESCE(NULLIF(TRIM(ua.first_source), ''), 'unknown') = 'unknown' THEN 1
                    ELSE 0
                END
            ), 0) AS paid_users_unknown_source
        FROM (
            SELECT DISTINCT user_id
            FROM orders
            WHERE status='completed'
              AND date(COALESCE(completed_at, updated_at)) >= date('now', ?)
        ) o
        LEFT JOIN user_acquisition ua ON ua.user_id = o.user_id
        """,
        p,
    )
    c = await cur.fetchone()
    all_n = int(b["all_n"] or 0)
    v2_n = int(b["v2_n"] or 0)
    paid_total = int(c["paid_users_total"] or 0)
    paid_unknown = int(c["paid_users_unknown_source"] or 0)
    return {
        "missing_kind": int(a["missing_kind"] or 0),
        "missing_profit": int(a["missing_profit"] or 0),
        "completed_total": int(a["completed_total"] or 0),
        "events_all": all_n,
        "events_v2": v2_n,
        "events_v2_pct": round(100.0 * v2_n / all_n, 2) if all_n else 100.0,
        "paid_users_total": paid_total,
        "paid_users_unknown_source": paid_unknown,
        "paid_unknown_pct": round(100.0 * paid_unknown / paid_total, 2) if paid_total else 0.0,
    }


def _evaluate_thresholds(settings: Settings, snap: dict[str, float | int]) -> dict[str, tuple[bool, str, str]]:
    mk = int(snap["missing_kind"])
    mp = int(snap["missing_profit"])
    v2 = float(snap["events_v2_pct"])
    up = float(snap["paid_unknown_pct"])
    return {
        "orders_missing_kind": (
            mk > int(settings.data_quality_max_orders_missing_kind),
            f"orders missing product_kind={mk} threshold={int(settings.data_quality_max_orders_missing_kind)}",
            f"orders missing product_kind recovered={mk}",
        ),
        "orders_missing_profit_snapshot": (
            mp > int(settings.data_quality_max_orders_missing_profit_snapshot),
            (
                f"completed orders missing profit_snapshot={mp} "
                f"threshold={int(settings.data_quality_max_orders_missing_profit_snapshot)}"
            ),
            f"profit_snapshot coverage recovered missing={mp}",
        ),
        "analytics_schema_v2": (
            v2 < float(settings.data_quality_min_event_schema_v2_pct),
            (
                f"analytics schema_v2 coverage low={v2:.2f}% "
                f"threshold={float(settings.data_quality_min_event_schema_v2_pct):.2f}%"
            ),
            f"analytics schema_v2 coverage recovered={v2:.2f}%",
        ),
        "unattributed_paid_users": (
            up > float(settings.data_quality_max_unattributed_paid_pct),
            (
                f"unattributed paid users high={up:.2f}% "
                f"threshold={float(settings.data_quality_max_unattributed_paid_pct):.2f}%"
            ),
            f"unattributed paid users recovered={up:.2f}%",
        ),
    }


async def run_data_quality_checks_once(settings: Settings) -> None:
    if not settings.database_path.exists():
        return
    state = _load_state()
    try:
        async with aiosqlite.connect(settings.database_path) as conn:
            conn.row_factory = aiosqlite.Row
            snap = await _query_snapshot(conn, int(settings.data_quality_lookback_days))
        checks = _evaluate_thresholds(settings, snap)
        for check_name, (is_problem, problem_body, recovery_body) in checks.items():
            await _emit_problem_or_recovery(
                settings,
                state,
                check_name=check_name,
                is_problem_now=is_problem,
                problem_body=problem_body,
                recovery_body=recovery_body,
            )
    except Exception:
        logger.exception("data_quality_checks_failed")
        await _emit_problem_or_recovery(
            settings,
            state,
            check_name="internal_error",
            is_problem_now=True,
            problem_body="data quality check internal error",
            recovery_body="data quality check internal error recovered",
        )
    _save_state(state)


async def data_quality_checks_loop(settings: Settings) -> None:
    interval = max(300, int(settings.data_quality_checks_interval_seconds))
    while True:
        await run_data_quality_checks_once(settings)
        await asyncio.sleep(interval)


async def _main() -> None:
    settings = load_settings()
    if not settings.data_quality_checks_enabled:
        return
    await run_data_quality_checks_once(settings)


if __name__ == "__main__":
    asyncio.run(_main())
