from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from aiogram import Bot

from bot.config import Settings
from bot.db.database import connect
from bot.services import admin_stats_repo

logger = logging.getLogger(__name__)


def _delta_pct(cur: float, prev: float) -> float:
    if abs(prev) < 1e-9:
        return 0.0
    return round((cur - prev) * 100.0 / prev, 2)


def _fmt(v: float) -> str:
    return f"{v:.2f}"


def build_exec_report_text(
    *,
    generated_at: str,
    short_days: int,
    long_days: int,
    agg_short: admin_stats_repo.DashboardAgg,
    agg_long: admin_stats_repo.DashboardAgg,
    pay_short: dict[str, float | int],
    webhook_short: dict[str, float | int],
    cross_short: dict[str, float | int],
    ret_short: dict[str, float | int],
    acq_short: dict[str, float | int],
) -> str:
    lines = [
        f"<b>Weekly Executive Report</b> <i>{generated_at}</i>",
        f"Период: {short_days}д vs {long_days}д",
        "",
        "<b>1) CAC (общий)</b>",
        f"{_fmt(float(acq_short.get('acq_cac_rub', 0.0)))} ₽",
        "<b>2) Выручка (short)</b>",
        f"{_fmt(agg_short.revenue_rub)} ₽ ({_delta_pct(agg_short.revenue_rub, agg_long.revenue_rub)}% vs long)",
        "<b>3) VPN share</b>",
        f"{_fmt(agg_short.vpn_revenue_share_pct)}%",
        "<b>4) ARPPU</b>",
        f"{_fmt(agg_short.arppu_rub)} ₽",
        "<b>5) D7 retention</b>",
        f"{_fmt(float(ret_short.get('retention_d7_pct', 0.0)))}%",
        "<b>6) VPN churn (proxy)</b>",
        f"требует vpn.db cohort (в текущем слое не рассчитывается отдельно, см. retention block)",
        "<b>7) Cross-sell SP→VPN</b>",
        f"{_fmt(float(cross_short.get('cross_sell_sp_to_vpn_pct', 0.0)))}%",
        "<b>8) Cross-sell VPN→SP</b>",
        f"{_fmt(float(cross_short.get('cross_sell_vpn_to_sp_pct', 0.0)))}%",
        "<b>9) Payment success</b>",
        f"{_fmt(float(pay_short.get('funnel_paid_rate_pct', 0.0)))}%",
        "<b>10) Webhook SLA</b>",
        f"success {_fmt(float(webhook_short.get('webhook_success_rate_pct', 0.0)))}% · "
        f"p95 {_fmt(float(webhook_short.get('webhook_latency_p95_sec', -1.0)))}s",
    ]
    return "\n".join(lines)


async def send_exec_report_once(bot: Bot, settings: Settings) -> None:
    short_days = max(1, int(settings.exec_report_days_short))
    long_days = max(short_days, int(settings.exec_report_days_long))
    conn = await connect(settings.database_path)
    try:
        agg_short = await admin_stats_repo.aggregate_dashboard(conn, days=short_days)
        agg_long = await admin_stats_repo.aggregate_dashboard(conn, days=long_days)
        pay_short = await admin_stats_repo.payment_funnel_metrics(conn, days=short_days)
        webhook_short = await admin_stats_repo.webhook_sla_metrics(conn, days=short_days)
        cross_short = await admin_stats_repo.cross_sell_metrics(conn, days=short_days, window_days=30)
        ret_short = await admin_stats_repo.retention_metrics(conn, days=short_days)
        acq_short = await admin_stats_repo.acquisition_metrics(conn, days=short_days)
    finally:
        await conn.close()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    text = build_exec_report_text(
        generated_at=now,
        short_days=short_days,
        long_days=long_days,
        agg_short=agg_short,
        agg_long=agg_long,
        pay_short=pay_short,
        webhook_short=webhook_short,
        cross_short=cross_short,
        ret_short=ret_short,
        acq_short=acq_short,
    )
    for admin_id in sorted(settings.parsed_admin_ids()):
        try:
            await bot.send_message(admin_id, text)
        except Exception:
            logger.exception("exec_report_send_failed admin_id=%s", admin_id)


async def exec_report_loop(bot: Bot, settings: Settings) -> None:
    interval = max(300, int(settings.exec_report_interval_seconds))
    while True:
        try:
            await send_exec_report_once(bot, settings)
        except Exception:
            logger.exception("exec_report_loop_iteration_failed")
        await asyncio.sleep(interval)
