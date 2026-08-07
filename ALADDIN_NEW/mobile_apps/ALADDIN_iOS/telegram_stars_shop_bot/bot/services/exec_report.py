from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aiogram import Bot

from bot.config import Settings
from bot.db.database import connect
from bot.services import admin_stats_repo
from bot.services.ops_chat import send_ops_chat_html
from bot.util_html import esc

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExecCadence:
    """Один канал отчёта: окно метрик + как часто слать."""

    key: str
    title_ru: str
    title_en: str
    days: int
    interval_seconds: int


# Канон: 1д каждый день → 7д → 30д → 90д квартал → 150д полугодие.
DEFAULT_EXEC_CADENCES: tuple[ExecCadence, ...] = (
    ExecCadence("daily", "Ежедневный", "Daily", 1, 86_400),
    ExecCadence("weekly", "Недельный", "Weekly", 7, 604_800),
    ExecCadence("monthly", "Месячный", "Monthly", 30, 2_592_000),
    ExecCadence("quarterly", "Квартальный", "Quarterly", 90, 7_776_000),
    ExecCadence("semi", "Полугодовой", "Semi-annual", 150, 12_960_000),
)

_CADENCE_BY_KEY = {c.key: c for c in DEFAULT_EXEC_CADENCES}


def _delta_pct(cur: float, prev: float) -> float:
    if abs(prev) < 1e-9:
        return 0.0
    return round((cur - prev) * 100.0 / prev, 2)


def _fmt(v: float) -> str:
    return f"{v:.2f}"


METRIC_GLOSS_RU: dict[str, str] = {
    "cac": "Стоимость привлечения 1 платящего пользователя",
    "revenue": "Сколько денег пришло за период (только реальные оплаты с выдачей)",
    "vpn_share": "Какая доля выручки приходится на VPN",
    "arppu": "Средний чек одного платящего пользователя",
    "d7_retention": "Сколько % купивших вернулись с покупкой за 7 дней",
    "vpn_churn": "Сколько % VPN-клиентов «отвалилось» (пока оценка / заглушка)",
    "cross_sp_vpn": "Какая доля купивших Stars/Premium потом купила VPN",
    "cross_vpn_sp": "Какая доля купивших VPN потом купила Stars/Premium",
    "payment_success": "Какая доля созданных заказов дошла до оплаты",
    "webhook_sla": "Насколько вовремя и успешно приходят уведомления об оплате",
    "active_paid_vpn": "Сколько людей реально оплатили VPN и сейчас пользуются ключом",
    "vpn_sales_mix": "Продажи VPN за период: какие тарифы берут чаще и на какую сумму",
    "stars_sales": "Реальные продажи Stars/подарков: покупатели, заказы, популярные пакеты ⭐",
    "premium_sales": "Реальные продажи Premium: покупатели, заказы, популярные сроки (мес.)",
    "crypto_sales": "Оплаты криптой (USDT): заказы, выручка и доля от всей реальной выручки",
}


def parse_exec_cadences(raw: str | None) -> list[ExecCadence]:
    """
    CSV ключей: daily,weekly,monthly,quarterly,semi.
    Пусто / all → все канонические.
    """
    text = (raw or "").strip().lower()
    if not text or text in ("all", "*", "default"):
        return list(DEFAULT_EXEC_CADENCES)
    out: list[ExecCadence] = []
    seen: set[str] = set()
    for part in text.split(","):
        key = part.strip()
        if not key or key in seen:
            continue
        c = _CADENCE_BY_KEY.get(key)
        if c is None:
            logger.warning("exec_report_unknown_cadence key=%s", key)
            continue
        seen.add(key)
        out.append(c)
    return out or list(DEFAULT_EXEC_CADENCES)


def exec_report_state_path(settings: Settings, cadence_key: str = "weekly") -> Path:
    """Файл last_sent рядом с shop.db (отдельный на каждый cadence)."""
    parent = Path(settings.database_path).expanduser().resolve().parent
    key = (cadence_key or "weekly").strip().lower() or "weekly"
    if key == "weekly":
        # Совместимость со старым одним файлом.
        legacy = parent / "exec_report_last_sent.txt"
        named = parent / f"exec_report_last_sent_{key}.txt"
        if legacy.exists() and not named.exists():
            return legacy
        return named
    return parent / f"exec_report_last_sent_{key}.txt"


def read_exec_report_last_sent(path: Path) -> float | None:
    try:
        raw = path.read_text(encoding="utf-8").strip()
        if not raw:
            return None
        ts = float(raw.split()[0])
        if ts <= 0:
            return None
        return ts
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as e:
        logger.warning("exec_report_last_sent_read_failed path=%s err=%s", path, e)
        return None


def write_exec_report_last_sent(path: Path, ts: float | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    value = float(time.time() if ts is None else ts)
    path.write_text(f"{value:.3f}\n", encoding="utf-8")


def _summary_line(summary: dict[str, float | int] | None) -> str:
    s = summary or {}
    buyers = int(s.get("unique_buyers", 0) or 0)
    orders = int(s.get("orders", 0) or 0)
    rev = float(s.get("revenue_rub", 0.0) or 0.0)
    return f"уник. покупателей: {buyers} · заказов: {orders} · выручка: {_fmt(rev)} ₽"


def _mix_lines_stars(rows: list[Any] | None) -> list[str]:
    if not rows:
        return ["<i>нет продаж за период</i>"]
    out: list[str] = []
    for r in rows:
        pack = int(r["pack"] or 0)
        n = int(r["n"] or 0)
        rev = float(r["rev"] or 0)
        out.append(f"· <code>{esc(str(pack))}</code> ⭐ — {n} зак. · {_fmt(rev)} ₽")
    return out


def _mix_lines_premium(rows: list[Any] | None) -> list[str]:
    if not rows:
        return ["<i>нет продаж за период</i>"]
    out: list[str] = []
    for r in rows:
        months = int(r["months"] or 0)
        n = int(r["n"] or 0)
        rev = float(r["rev"] or 0)
        out.append(f"· <code>{esc(str(months))}</code> мес — {n} зак. · {_fmt(rev)} ₽")
    return out


def _mix_lines_vpn(rows: list[Any] | None) -> list[str]:
    if not rows:
        return ["<i>нет продаж за период</i>"]
    out: list[str] = []
    for r in rows:
        title = str(r["title"] or r["product_id"] or "VPN")
        n = int(r["n"] or 0)
        rev = float(r["rev"] or 0)
        out.append(f"· {esc(title)} — {n} зак. · {_fmt(rev)} ₽")
    return out


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
    active_paid_vpn: int | None = None,
    vpn_summary: dict[str, float | int] | None = None,
    vpn_mix: list[Any] | None = None,
    stars_summary: dict[str, float | int] | None = None,
    stars_mix: list[Any] | None = None,
    premium_summary: dict[str, float | int] | None = None,
    premium_mix: list[Any] | None = None,
    crypto_short: dict[str, float | int] | None = None,
    report_title: str = "Weekly Executive Report",
) -> str:
    g = METRIC_GLOSS_RU
    if active_paid_vpn is None or active_paid_vpn < 0:
        vpn11 = "н/д (нет VPN_DB_PATH)"
    else:
        vpn11 = str(int(active_paid_vpn))
    crypto = crypto_short or {}
    crypto_orders = int(crypto.get("orders", 0) or 0)
    crypto_buyers = int(crypto.get("unique_buyers", 0) or 0)
    crypto_rev = float(crypto.get("revenue_rub", 0.0) or 0.0)
    crypto_share = float(crypto.get("share_pct", 0.0) or 0.0)
    lines = [
        f"<b>{esc(report_title)}</b> <i>{generated_at}</i>",
        f"Период: {short_days}д vs {long_days}д",
        "<i>Только реальные оплаты с выдачей; без админов и служебных тестовых аккаунтов</i>",
        "",
        "<b>1) CAC (общий)</b>",
        f"<i>{g['cac']}</i>",
        f"{_fmt(float(acq_short.get('acq_cac_rub', 0.0)))} ₽",
        "",
        "<b>2) Выручка (short)</b>",
        f"<i>{g['revenue']}</i>",
        f"{_fmt(agg_short.revenue_rub)} ₽ ({_delta_pct(agg_short.revenue_rub, agg_long.revenue_rub)}% vs long)",
        "",
        "<b>3) VPN share</b>",
        f"<i>{g['vpn_share']}</i>",
        f"{_fmt(agg_short.vpn_revenue_share_pct)}%",
        "",
        "<b>4) ARPPU</b>",
        f"<i>{g['arppu']}</i>",
        f"{_fmt(agg_short.arppu_rub)} ₽",
        "",
        "<b>5) D7 retention</b>",
        f"<i>{g['d7_retention']}</i>",
        f"{_fmt(float(ret_short.get('retention_d7_pct', 0.0)))}%",
        "",
        "<b>6) VPN churn (proxy)</b>",
        f"<i>{g['vpn_churn']}</i>",
        "требует vpn.db cohort (в текущем слое не рассчитывается отдельно)",
        "",
        "<b>7) Cross-sell SP→VPN</b>",
        f"<i>{g['cross_sp_vpn']}</i>",
        f"{_fmt(float(cross_short.get('cross_sell_sp_to_vpn_pct', 0.0)))}%",
        "",
        "<b>8) Cross-sell VPN→SP</b>",
        f"<i>{g['cross_vpn_sp']}</i>",
        f"{_fmt(float(cross_short.get('cross_sell_vpn_to_sp_pct', 0.0)))}%",
        "",
        "<b>9) Payment success</b>",
        f"<i>{g['payment_success']}</i>",
        f"{_fmt(float(pay_short.get('funnel_paid_rate_pct', 0.0)))}%",
        "",
        "<b>10) Webhook SLA</b>",
        f"<i>{g['webhook_sla']}</i>",
        f"success {_fmt(float(webhook_short.get('webhook_success_rate_pct', 0.0)))}% · "
        f"p95 {_fmt(float(webhook_short.get('webhook_latency_p95_sec', -1.0)))}s",
        "",
        "<b>11) Активные платные VPN</b>",
        f"<i>{g['active_paid_vpn']}</i>",
        vpn11,
        f"<i>{g['vpn_sales_mix']} ({short_days}д)</i>",
        _summary_line(vpn_summary),
        *_mix_lines_vpn(vpn_mix),
        "",
        "<b>12) Stars (продажи)</b>",
        f"<i>{g['stars_sales']} ({short_days}д)</i>",
        _summary_line(stars_summary),
        *_mix_lines_stars(stars_mix),
        "",
        "<b>13) Premium (продажи)</b>",
        f"<i>{g['premium_sales']} ({short_days}д)</i>",
        _summary_line(premium_summary),
        *_mix_lines_premium(premium_mix),
        "",
        "<b>14) Крипта (USDT)</b>",
        f"<i>{g['crypto_sales']} ({short_days}д)</i>",
        (
            f"уник. покупателей: {crypto_buyers} · заказов: {crypto_orders} · "
            f"выручка: {_fmt(crypto_rev)} ₽ · доля: {_fmt(crypto_share)}%"
        ),
    ]
    return "\n".join(lines)


def _compare_days(primary_days: int) -> int:
    """Окно сравнения: 2× основной период (не меньше primary)."""
    d = max(1, int(primary_days))
    return max(d, d * 2)


async def _gather_exec_metrics(
    conn,
    settings: Settings,
    *,
    primary_days: int,
) -> tuple:
    short_days = max(1, int(primary_days))
    long_days = _compare_days(short_days)
    excl = settings.resolved_exec_metrics_exclude_user_ids()
    kw = {"real_paid_only": True, "exclude_user_ids": excl}
    agg_short = await admin_stats_repo.aggregate_dashboard(conn, days=short_days, **kw)
    agg_long = await admin_stats_repo.aggregate_dashboard(conn, days=long_days, **kw)
    pay_short = await admin_stats_repo.payment_funnel_metrics(conn, days=short_days, **kw)
    webhook_short = await admin_stats_repo.webhook_sla_metrics(conn, days=short_days)
    cross_short = await admin_stats_repo.cross_sell_metrics(
        conn, days=short_days, window_days=30, **kw
    )
    ret_short = await admin_stats_repo.retention_metrics(conn, days=short_days, **kw)
    acq_short = await admin_stats_repo.acquisition_metrics(conn, days=short_days, **kw)
    active_vpn = await admin_stats_repo.count_active_paid_vpn_subscribers(
        conn,
        settings.resolved_vpn_db_path(),
        exclude_user_ids=excl,
    )
    mix_kw = {"days": short_days, **kw}
    vpn_summary = await admin_stats_repo.product_sales_summary(conn, kind="vpn", **mix_kw)
    vpn_mix = await admin_stats_repo.vpn_by_term(conn, **mix_kw)
    stars_summary = await admin_stats_repo.product_sales_summary(conn, kind="stars", **mix_kw)
    stars_mix = await admin_stats_repo.stars_by_package(conn, **mix_kw)
    premium_summary = await admin_stats_repo.product_sales_summary(conn, kind="premium", **mix_kw)
    premium_mix = await admin_stats_repo.premium_by_term(conn, **mix_kw)
    crypto_short = await admin_stats_repo.crypto_payment_metrics(conn, **mix_kw)
    return (
        short_days,
        long_days,
        agg_short,
        agg_long,
        pay_short,
        webhook_short,
        cross_short,
        ret_short,
        acq_short,
        active_vpn,
        vpn_summary,
        vpn_mix,
        stars_summary,
        stars_mix,
        premium_summary,
        premium_mix,
        crypto_short,
    )


def _resolve_cadence(settings: Settings, cadence: ExecCadence | str | None) -> ExecCadence:
    if isinstance(cadence, ExecCadence):
        return cadence
    if isinstance(cadence, str) and cadence.strip():
        key = cadence.strip().lower()
        if key in _CADENCE_BY_KEY:
            return _CADENCE_BY_KEY[key]
    # Legacy: EXEC_REPORT_DAYS_SHORT как weekly-окно.
    days = max(1, int(settings.exec_report_days_short or 7))
    if days == 1:
        return _CADENCE_BY_KEY["daily"]
    if days <= 7:
        return _CADENCE_BY_KEY["weekly"]
    if days <= 30:
        return _CADENCE_BY_KEY["monthly"]
    if days <= 90:
        return _CADENCE_BY_KEY["quarterly"]
    return _CADENCE_BY_KEY["semi"]


async def send_exec_report_once(
    bot: Bot,
    settings: Settings,
    cadence: ExecCadence | str | None = None,
) -> None:
    c = _resolve_cadence(settings, cadence)
    conn = await connect(settings.database_path)
    try:
        (
            short_days,
            long_days,
            agg_short,
            agg_long,
            pay_short,
            webhook_short,
            cross_short,
            ret_short,
            acq_short,
            active_vpn,
            vpn_summary,
            vpn_mix,
            stars_summary,
            stars_mix,
            premium_summary,
            premium_mix,
            crypto_short,
        ) = await _gather_exec_metrics(conn, settings, primary_days=c.days)
    finally:
        await conn.close()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    title = f"{c.title_en} Executive Report ({c.title_ru}, {c.days}д)"
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
        active_paid_vpn=active_vpn,
        vpn_summary=vpn_summary,
        vpn_mix=vpn_mix,
        stars_summary=stars_summary,
        stars_mix=stars_mix,
        premium_summary=premium_summary,
        premium_mix=premium_mix,
        crypto_short=crypto_short,
        report_title=title,
    )
    await send_ops_chat_html(settings, text)


async def exec_report_loop(bot: Bot, settings: Settings) -> None:
    """
    Несколько cadence параллельно (daily/weekly/monthly/quarterly/semi).
    При старте не спамим: каждый канал сначала «arm», потом ждёт свой interval.
    """
    cadences = parse_exec_cadences(getattr(settings, "exec_report_cadences", None))
    poll_s = 300
    logger.info(
        "exec_report_loop_start cadences=%s",
        ",".join(c.key for c in cadences),
    )
    while True:
        now = time.time()
        sleep_for = float(poll_s)
        for c in cadences:
            interval = max(300, int(c.interval_seconds))
            path = exec_report_state_path(settings, c.key)
            last = read_exec_report_last_sent(path)
            if last is None:
                write_exec_report_last_sent(path, now)
                logger.info(
                    "exec_report_armed_no_send cadence=%s path=%s wait_s=%s",
                    c.key,
                    path,
                    interval,
                )
                sleep_for = min(sleep_for, float(interval))
                continue
            due_in = interval - (now - last)
            if due_in > 0:
                sleep_for = min(sleep_for, max(1.0, due_in))
                continue
            try:
                await send_exec_report_once(bot, settings, cadence=c)
            except Exception:
                logger.exception("exec_report_loop_iteration_failed cadence=%s", c.key)
            write_exec_report_last_sent(path, time.time())
            sleep_for = min(sleep_for, float(interval))
        await asyncio.sleep(max(1.0, sleep_for))
