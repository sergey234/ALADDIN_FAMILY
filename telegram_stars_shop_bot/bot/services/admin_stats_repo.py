from __future__ import annotations

import csv
import io
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiosqlite

logger = logging.getLogger(__name__)


def _period_clause(days: int | None) -> tuple[str, tuple[Any, ...]]:
    """Фильтр по дате выдачи/обновления (алиас `o`). days=None — всё время; -1 или 0 — календарный сегодня; иначе скользящее окно N дней."""
    if days is None:
        return "", ()
    if days in (-1, 0):
        return (" AND date(COALESCE(o.completed_at, o.updated_at)) = date('now')", ())
    return (
        " AND date(COALESCE(o.completed_at, o.updated_at)) >= date('now', ?)",
        (f"-{int(days)} days",),
    )


def _period_clause_plain(days: int | None) -> tuple[str, tuple[Any, ...]]:
    """То же без алиаса (запросы к `orders` напрямую)."""
    if days is None:
        return "", ()
    if days in (-1, 0):
        return (" AND date(COALESCE(completed_at, updated_at)) = date('now')", ())
    return (
        " AND date(COALESCE(completed_at, updated_at)) >= date('now', ?)",
        (f"-{int(days)} days",),
    )


def _analytics_period_clause(days: int | None) -> tuple[str, tuple[Any, ...]]:
    """Фильтр по `analytics_events.created_at` (те же коды периода, что у заказов)."""
    if days is None:
        return "", ()
    if days in (-1, 0):
        return (" AND date(created_at) = date('now')", ())
    return (" AND date(created_at) >= date('now', ?)", (f"-{int(days)} days",))


@dataclass(frozen=True)
class DashboardAgg:
    revenue_rub: float
    orders_count: int
    net_profit_rub: float
    stars_units_sold: int
    stars_revenue_rub: float
    premium_units_sold: int
    premium_revenue_rub: float
    distinct_referrers: int = 0


async def aggregate_dashboard(
    conn: aiosqlite.Connection,
    *,
    days: int | None,
) -> DashboardAgg:
    clause, params = _period_clause(days)
    sql = f"""
        SELECT
            COALESCE(SUM(o.rub_after_discounts), 0) AS revenue,
            COUNT(*) AS cnt,
            COALESCE(SUM(o.net_profit_rub), 0) AS netp,
            COALESCE(SUM(CASE
                WHEN o.product_kind IN ('stars', 'gift') AND o.stars_qty IS NOT NULL
                THEN o.stars_qty ELSE 0 END), 0) AS stars_u,
            COALESCE(SUM(CASE
                WHEN o.product_kind IN ('stars', 'gift')
                THEN o.rub_after_discounts ELSE 0 END), 0) AS stars_rev,
            COALESCE(SUM(CASE WHEN o.product_kind = 'premium' THEN 1 ELSE 0 END), 0) AS prem_n,
            COALESCE(SUM(CASE
                WHEN o.product_kind = 'premium'
                THEN o.rub_after_discounts ELSE 0 END), 0) AS prem_rev
        FROM orders o
        WHERE o.status = 'completed' {clause}
    """
    cur = await conn.execute(sql, params)
    row = await cur.fetchone()
    cur_dr = await conn.execute(
        f"""
        SELECT COUNT(DISTINCT o.referrer_id) AS c
        FROM orders o
        WHERE o.status = 'completed'
          AND o.referrer_id IS NOT NULL
          {clause}
        """,
        params,
    )
    dr_row = await cur_dr.fetchone()
    distinct_ref = int(dr_row["c"] or 0) if dr_row else 0
    return DashboardAgg(
        revenue_rub=float(row["revenue"] or 0),
        orders_count=int(row["cnt"] or 0),
        net_profit_rub=float(row["netp"] or 0),
        stars_units_sold=int(row["stars_u"] or 0),
        stars_revenue_rub=float(row["stars_rev"] or 0),
        premium_units_sold=int(row["prem_n"] or 0),
        premium_revenue_rub=float(row["prem_rev"] or 0),
        distinct_referrers=distinct_ref,
    )


async def top_referrers(
    conn: aiosqlite.Connection,
    *,
    days: int | None,
    limit: int = 3,
) -> list[aiosqlite.Row]:
    clause, params = _period_clause(days)
    lim = max(1, min(20, int(limit)))
    cur = await conn.execute(
        f"""
        SELECT o.referrer_id AS rid,
               COUNT(*) AS orders_n,
               COALESCE(SUM(o.commission_rub), 0) AS bonus_rub,
               COALESCE(SUM(o.rub_after_discounts), 0) AS vol_rub
        FROM orders o
        WHERE o.status = 'completed'
          AND o.referrer_id IS NOT NULL
          AND COALESCE(o.commission_paid, 0) = 1
          {clause}
        GROUP BY o.referrer_id
        ORDER BY bonus_rub DESC
        LIMIT ?
        """,
        (*params, lim),
    )
    return await cur.fetchall()


async def stars_by_package(
    conn: aiosqlite.Connection,
    *,
    days: int | None,
) -> list[aiosqlite.Row]:
    clause, params = _period_clause(days)
    cur = await conn.execute(
        f"""
        SELECT COALESCE(o.stars_qty, 0) AS pack,
               COUNT(*) AS n,
               COALESCE(SUM(o.rub_after_discounts), 0) AS rev
        FROM orders o
        WHERE o.status = 'completed'
          AND o.product_kind IN ('stars', 'gift')
          {clause}
        GROUP BY pack
        ORDER BY pack ASC
        """,
        params,
    )
    return await cur.fetchall()


async def premium_by_term(
    conn: aiosqlite.Connection,
    *,
    days: int | None,
) -> list[aiosqlite.Row]:
    clause, params = _period_clause(days)
    cur = await conn.execute(
        f"""
        SELECT COALESCE(o.premium_months, 0) AS months,
               COUNT(*) AS n,
               COALESCE(SUM(o.rub_after_discounts), 0) AS rev
        FROM orders o
        WHERE o.status = 'completed'
          AND o.product_kind = 'premium'
          {clause}
        GROUP BY months
        ORDER BY months ASC
        """,
        params,
    )
    return await cur.fetchall()


async def sales_by_day(
    conn: aiosqlite.Connection,
    *,
    days: int = 14,
) -> list[aiosqlite.Row]:
    d = max(1, min(90, int(days)))
    cur = await conn.execute(
        """
        SELECT date(COALESCE(o.completed_at, o.updated_at)) AS d,
               COUNT(*) AS n,
               COALESCE(SUM(o.rub_after_discounts), 0) AS rev,
               COALESCE(SUM(o.net_profit_rub), 0) AS netp
        FROM orders o
        WHERE o.status = 'completed'
          AND date(COALESCE(o.completed_at, o.updated_at)) >= date('now', ?)
        GROUP BY d
        ORDER BY d ASC
        """,
        (f"-{d} days",),
    )
    return await cur.fetchall()


async def sales_by_week(
    conn: aiosqlite.Connection,
    *,
    days: int = 84,
) -> list[aiosqlite.Row]:
    """Агрегация выданных заказов по календарным неделям SQLite (год + Www)."""
    d = max(7, min(730, int(days)))
    cur = await conn.execute(
        """
        SELECT strftime('%Y-W%W', date(COALESCE(completed_at, updated_at))) AS wk,
               COUNT(*) AS n,
               COALESCE(SUM(rub_after_discounts), 0) AS rev,
               COALESCE(SUM(net_profit_rub), 0) AS netp
        FROM orders
        WHERE status = 'completed'
          AND date(COALESCE(completed_at, updated_at)) >= date('now', ?)
        GROUP BY wk
        ORDER BY wk ASC
        """,
        (f"-{d} days",),
    )
    return await cur.fetchall()


async def funnel_metrics(conn: aiosqlite.Connection, *, days: int | None) -> dict[str, float | int]:
    """
    Воронка: посетители = distinct user_id с событием bot_entry за период;
    конверсия = доля тех же пользователей, у кого есть completed заказ за тот же период.
    """
    ac, ap = _analytics_period_clause(days)
    oc, op = _period_clause_plain(days)
    cur_v = await conn.execute(
        f"""
        SELECT COUNT(DISTINCT user_id) AS c
        FROM analytics_events
        WHERE event_type = 'bot_entry' {ac}
        """,
        ap,
    )
    visitors = int((await cur_v.fetchone())["c"] or 0)
    cur_c = await conn.execute(
        f"""
        SELECT COUNT(*) AS c FROM (
            SELECT DISTINCT user_id FROM analytics_events
            WHERE event_type = 'bot_entry' {ac}
            INTERSECT
            SELECT DISTINCT user_id FROM orders
            WHERE status = 'completed' {oc}
        )
        """,
        (*ap, *op),
    )
    converted = int((await cur_c.fetchone())["c"] or 0)
    pct = round(100.0 * converted / visitors, 2) if visitors else 0.0
    return {
        "funnel_visitors": visitors,
        "funnel_converted": converted,
        "funnel_conversion_pct": pct,
    }


async def top_products_by_profit(
    conn: aiosqlite.Connection,
    *,
    days: int | None,
    limit: int = 8,
) -> list[aiosqlite.Row]:
    clause, params = _period_clause(days)
    lim = max(1, min(30, int(limit)))
    cur = await conn.execute(
        f"""
        SELECT o.product_title,
               COALESCE(SUM(o.net_profit_rub), 0) AS netp,
               COUNT(*) AS n
        FROM orders o
        WHERE o.status = 'completed'
          {clause}
        GROUP BY o.product_id, o.product_title
        ORDER BY netp DESC
        LIMIT ?
        """,
        (*params, lim),
    )
    return await cur.fetchall()


async def referral_metrics(conn: aiosqlite.Connection, *, days: int | None) -> dict[str, float | int]:
    clause, params = _period_clause(days)
    cur = await conn.execute(
        f"""
        SELECT
            COUNT(*) AS total_c,
            SUM(CASE WHEN o.referral_discount_rub > 0.009 THEN 1 ELSE 0 END) AS with_ref_disc,
            COALESCE(SUM(CASE
                WHEN o.referrer_id IS NOT NULL AND COALESCE(o.commission_paid, 0) = 1
                THEN o.commission_rub ELSE 0 END), 0) AS ref_bonus_paid
        FROM orders o
        WHERE o.status = 'completed' {clause}
        """,
        params,
    )
    row = await cur.fetchone()
    total = int(row["total_c"] or 0)
    with_disc = int(row["with_ref_disc"] or 0)
    pct = round(100.0 * with_disc / total, 1) if total else 0.0
    return {
        "completed_orders": total,
        "orders_with_ref_discount": with_disc,
        "ref_discount_pct": pct,
        "total_referral_bonus_rub": float(row["ref_bonus_paid"] or 0),
    }


def _period_clause_vpn_grants(days: int | None) -> tuple[str, tuple[Any, ...]]:
    if days is None:
        return "", ()
    if days in (-1, 0):
        return (" AND date(g.created_at) = date('now')", ())
    return (" AND date(g.created_at) >= date('now', ?)", (f"-{int(days)} days",))


async def vpn_referral_metrics(conn: aiosqlite.Connection, *, days: int | None) -> dict[str, float | int]:
    """Сводка VPN-рефералок: гранты в shop.db + входы по deep link (analytics)."""
    gc, gp = _period_clause_vpn_grants(days)
    ac, ap = _analytics_period_clause(days)
    cur = await conn.execute(
        f"""
        SELECT
            COUNT(*) AS n_grants,
            COALESCE(SUM(g.referrer_days), 0) AS sum_ref_days,
            COALESCE(SUM(g.friend_days), 0) AS sum_friend_days,
            COUNT(DISTINCT g.referrer_user_id) AS distinct_refs,
            COALESCE(SUM(CASE WHEN g.api_friend_ok = 1 THEN 1 ELSE 0 END), 0) AS api_friend_ok_n,
            COALESCE(SUM(CASE WHEN g.api_referrer_ok = 1 THEN 1 ELSE 0 END), 0) AS api_ref_ok_n,
            COALESCE(SUM(CASE WHEN g.friend_days > 0 AND g.api_friend_ok = 0 THEN 1 ELSE 0 END), 0) AS pend_friend_api,
            COALESCE(SUM(CASE WHEN g.referrer_days > 0 AND g.api_referrer_ok = 0 THEN 1 ELSE 0 END), 0) AS pend_ref_api,
            COALESCE(SUM(CASE WHEN g.friend_days > 0 AND g.api_friend_ok = 0 AND g.api_friend_attempts > 0 THEN 1 ELSE 0 END), 0) AS pend_friend_retried,
            COALESCE(SUM(CASE WHEN g.referrer_days > 0 AND g.api_referrer_ok = 0 AND g.api_referrer_attempts > 0 THEN 1 ELSE 0 END), 0) AS pend_ref_retried
        FROM vpn_referral_grants g
        WHERE 1=1 {gc}
        """,
        gp,
    )
    row = await cur.fetchone()
    cur2 = await conn.execute(
        f"""
        SELECT COUNT(*) AS c
        FROM analytics_events
        WHERE event_type = 'vpn_ref_link_open' {ac}
        """,
        ap,
    )
    row2 = await cur2.fetchone()
    visits = int(row2["c"] or 0) if row2 else 0
    return {
        "vpn_ref_grants": int(row["n_grants"] or 0) if row else 0,
        "vpn_ref_referrer_days": int(row["sum_ref_days"] or 0) if row else 0,
        "vpn_ref_friend_days": int(row["sum_friend_days"] or 0) if row else 0,
        "vpn_ref_distinct_referrers": int(row["distinct_refs"] or 0) if row else 0,
        "vpn_ref_api_friend_ok": int(row["api_friend_ok_n"] or 0) if row else 0,
        "vpn_ref_api_referrer_ok": int(row["api_ref_ok_n"] or 0) if row else 0,
        "vpn_ref_starts": visits,
        "vpn_ref_pending_friend_api": int(row["pend_friend_api"] or 0) if row else 0,
        "vpn_ref_pending_referrer_api": int(row["pend_ref_api"] or 0) if row else 0,
        "vpn_ref_pending_friend_retried": int(row["pend_friend_retried"] or 0) if row else 0,
        "vpn_ref_pending_referrer_retried": int(row["pend_ref_retried"] or 0) if row else 0,
    }


def _job_duration_seconds(created_at: str | None, updated_at: str | None) -> float | None:
    if not created_at or not updated_at:
        return None
    try:
        a = datetime.fromisoformat(str(created_at).replace("Z", "+00:00"))
        b = datetime.fromisoformat(str(updated_at).replace("Z", "+00:00"))
        if a.tzinfo is None:
            a = a.replace(tzinfo=timezone.utc)
        else:
            a = a.astimezone(timezone.utc)
        if b.tzinfo is None:
            b = b.replace(tzinfo=timezone.utc)
        else:
            b = b.astimezone(timezone.utc)
        dt = (b - a).total_seconds()
        return float(dt) if dt >= 0 else None
    except (TypeError, ValueError, OSError):
        return None


def _percentile_95(values: list[float]) -> float | None:
    if not values:
        return None
    s = sorted(values)
    idx = max(0, min(len(s) - 1, int(round(0.95 * (len(s) - 1)))))
    return float(s[idx])


async def export_completed_csv(conn: aiosqlite.Connection, *, days: int | None) -> bytes:
    clause, params = _period_clause_plain(days)
    cur = await conn.execute(
        f"""
        SELECT id, created_at, COALESCE(completed_at, updated_at) AS done_at,
               user_id, COALESCE(buyer_username,'') AS buyer_username,
               product_kind, product_id, product_title,
               rub_after_discounts, referral_discount_rub, referral_discount_percent,
               referrer_id,
               commission_rub, commission_paid,
               payment_gateway_fee_rub, manual_cogs_rub, cogs_rub, net_profit_rub,
               usd_rub_rate_snapshot,
               stars_qty, premium_months, status
        FROM orders
        WHERE status = 'completed' {clause}
        ORDER BY id ASC
        """,
        params,
    )
    rows = await cur.fetchall()
    buf = io.StringIO()
    w = csv.writer(buf)
    if rows:
        w.writerow(rows[0].keys())
        for r in rows:
            w.writerow(list(r))
    return buf.getvalue().encode("utf-8-sig")


async def fetch_vpn_controlplane_metrics(vpn_db_path: Path | None) -> dict[str, float | int]:
    """
    Снимок vpn.db (aladdin-shop-vpn-api): аккаунты по статусу, очередь jobs, p95 времени done job «provision».
    Путь задаётся VPN_DB_PATH на том же хосте, что shop.db (часто только на проде).
    """
    out: dict[str, float | int] = {"vpn_cp_available": 0}
    if vpn_db_path is None or not vpn_db_path.is_file():
        return out
    try:
        async with aiosqlite.connect(vpn_db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                """
                SELECT status, COUNT(*) AS n
                FROM vpn_accounts
                GROUP BY status
                """
            )
            rows = await cur.fetchall()
            total_acc = 0
            for r in rows:
                n = int(r["n"] or 0)
                total_acc += n
                out[f"vpn_cp_accounts_{str(r['status'] or 'unknown')}"] = n
            out["vpn_cp_accounts_total"] = total_acc

            cur2 = await db.execute(
                """
                SELECT status, COUNT(*) AS n
                FROM jobs
                GROUP BY status
                """
            )
            rows2 = await cur2.fetchall()
            total_jobs = 0
            j_pending = 0
            j_failed = 0
            j_processing = 0
            for r in rows2:
                n = int(r["n"] or 0)
                total_jobs += n
                st = str(r["status"] or "unknown").replace(" ", "_")
                out[f"vpn_cp_jobs_{st}"] = n
                raw_st = str(r["status"] or "")
                if raw_st == "pending":
                    j_pending = n
                elif raw_st == "failed":
                    j_failed = n
                elif raw_st == "processing":
                    j_processing = n
            out["vpn_cp_jobs_total"] = total_jobs
            out["vpn_cp_jobs_pending"] = j_pending
            out["vpn_cp_jobs_failed"] = j_failed
            out["vpn_cp_jobs_processing"] = j_processing

            cur3 = await db.execute(
                """
                SELECT created_at, updated_at
                FROM jobs
                WHERE job_type = 'provision' AND status = 'done'
                ORDER BY id DESC
                LIMIT 400
                """
            )
            jr_rows = await cur3.fetchall()
            durs: list[float] = []
            for jr in jr_rows:
                d = _job_duration_seconds(jr["created_at"], jr["updated_at"])
                if d is not None:
                    durs.append(d)
            p95 = _percentile_95(durs)
            out["vpn_cp_p95_provision_sec"] = round(p95, 2) if p95 is not None else -1.0
            out["vpn_cp_provision_done_sample_n"] = len(durs)
            out["vpn_cp_available"] = 1
    except Exception:
        logger.exception("fetch_vpn_controlplane_metrics failed path=%s", vpn_db_path)
        out["vpn_cp_available"] = -1
    return out


async def count_vpn_stale_pending_jobs(vpn_db_path: Path | None, *, stale_minutes: int = 10) -> int:
    """Jobs в pending, у которых next_run_at старше stale_minutes (воркер не подхватил)."""
    if vpn_db_path is None or not vpn_db_path.is_file():
        return 0
    mins = max(1, int(stale_minutes))
    try:
        async with aiosqlite.connect(vpn_db_path) as db:
            cur = await db.execute(
                """
                SELECT COUNT(*) AS n FROM jobs
                WHERE status = 'pending'
                  AND datetime(next_run_at) < datetime('now', ?)
                """,
                (f"-{mins} minutes",),
            )
            row = await cur.fetchone()
            return int(row[0] or 0) if row else 0
    except Exception:
        logger.exception("count_vpn_stale_pending_jobs path=%s", vpn_db_path)
        return 0
