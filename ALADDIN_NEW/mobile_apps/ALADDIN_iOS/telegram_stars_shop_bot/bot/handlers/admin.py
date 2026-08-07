from __future__ import annotations

import asyncio
import json
import secrets
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.config import Settings
from bot.keyboards.shop_kb import admin_order_kb, admin_topup_kb
from bot.services import (
    admin_audit_repo,
    admin_charts,
    admin_stats_repo,
    analytics_repo,
    balance_repo,
    contest_repo,
    marketing,
    orders_repo,
    promo_repo,
    users_repo,
    vpn_admin_support_repo,
    vpn_api_client,
)
from bot.services.exec_report import build_exec_report_text
from bot.services import admin_ux
from bot.services.admin_command_catalog import (
    admin_dashboard_help_row,
    admin_help_hub_html,
    admin_help_hub_kb,
    admin_help_section_html,
    admin_help_section_kb,
    section_by_key,
)
from bot.services.admin_crypto_paid_gate import crypto_manual_paid_gate_applies
from bot.services.admin_order_ff import ff_context_from_order_row, format_fulfillment_admin_block
from bot.services.alerts import send_alert
from bot.states.admin_cmd import AdminCmdStates
from bot.services.contest_dates import normalize_contest_date
from bot.services.buyer_order_notify import buyer_message_admin_status_change
from bot.services.istar_order_finalize import schedule_post_order_completed_notifications
from bot.services.order_flow import apply_completed_side_effects
from bot.services.partner_outbound import emit_order_status_changed
from bot.services.profit_compute import admin_profit_breakdown_html
from bot.util_html import esc

router = Router(name="admin")


def _is_admin(user_id: int, settings: Settings) -> bool:
    return user_id in settings.parsed_admin_ids()


_ADMIN_DENY_HTML = "⛔ Команда только для поддержки магазина."


async def _require_admin_message(message: Message, settings: Settings) -> bool:
    """True если админ. Иначе короткий отказ (не тишина)."""
    if _is_admin(message.from_user.id, settings):
        return True
    await message.answer(_ADMIN_DENY_HTML)
    return False


class _AdminCbMessage:
    """Прокси Message: from_user = админ (кнопка), answer идёт в чат cb.message."""

    def __init__(self, message: Message, admin_user) -> None:
        object.__setattr__(self, "_m", message)
        object.__setattr__(self, "from_user", admin_user)

    def __getattr__(self, item: str):
        return getattr(self._m, item)

    async def answer(self, *args, **kwargs):
        return await self._m.answer(*args, **kwargs)

    async def reply(self, *args, **kwargs):
        return await self._m.reply(*args, **kwargs)


def _cmd_obj(command: str, args: str | None = None) -> CommandObject:
    return CommandObject(prefix="/", command=command, mention=None, args=args)


# Команды, которые запускаются сразу (без ручного /cmd). Значение = args или None.
_CMDRUN_INSTANT: dict[str, str | None] = {
    "admqueue": None,
    "admdeliveries": None,
    "admin_help": None,
    "admin_fin_show": None,
    "admin_vpn": None,
    "admin_vpn_notices": None,
    "channel_checkout_pin": None,
    "admin_ref_withdraw": "list",
    "admin_promo": "list",
    "contest": "list",
    "admin_broadcast": None,
    "admin_broadcast_stats": "",
}

# Команды с аргументами: бот сам просит ввод, затем выполняет.
_CMDRUN_ASK: dict[str, tuple[str, str]] = {
    "admin_cogs": (
        "admin_cogs",
        "Себестоимость заказа.\nВведите: <code>ORDER_ID COGS_RUB</code>\nПример: <code>104 120</code>\nОтмена: /cancel",
    ),
    "admin_fin_set": (
        "admin_fin_set",
        "Комиссии / Fragment.\nВведите: <code>KEY VALUE</code> или <code>KEY clear</code>\n"
        "Пример: <code>fragment_1m 11.99</code> · <code>fee_sbp 3.4</code>\n"
        "Сначала покажу текущие настройки.\nОтмена: /cancel",
    ),
    "admin_recalc_profit": (
        "admin_recalc_profit",
        "Пересчёт прибыли.\nВведите <code>ORDER_ID</code> или "
        "<code>vpn</code>/<code>stars</code>/<code>premium</code>/<code>all</code>\nОтмена: /cancel",
    ),
    "admin_vpn_status": (
        "admin_vpn_status",
        "Статус VPN.\nВведите <code>TELEGRAM_ID</code>\nОтмена: /cancel",
    ),
    "admin_vpn_devices": (
        "admin_vpn_devices",
        "Устройства VPN.\nВведите <code>TELEGRAM_ID</code>\nОтмена: /cancel",
    ),
    "admin_vpn_trial_status": (
        "admin_vpn_trial_status",
        "Trial VPN.\nВведите <code>TELEGRAM_ID</code>\nОтмена: /cancel",
    ),
    "admin_vpn_revoke": (
        "admin_vpn_revoke",
        "Отключить VPN.\nВведите: <code>TELEGRAM_ID [причина]</code>\nОтмена: /cancel",
    ),
    "admin_vpn_extend": (
        "admin_vpn_extend",
        "Продлить VPN.\nВведите: <code>TELEGRAM_ID ДАТА_ISO [order_id]</code>\nОтмена: /cancel",
    ),
    "admin_vpn_finalize": (
        "admin_vpn_finalize",
        "Finalize VPN.\nВведите <code>ORDER_ID</code> или <code>stuck</code>\nОтмена: /cancel",
    ),
    "admin_ref_partner": (
        "admin_ref_partner",
        "Партнёрский %.\nВведите: <code>USER_ID [PCT|off]</code>\nОтмена: /cancel",
    ),
    "admin_vpn_announce": (
        "admin_vpn_announce",
        "Announce.\nВведите: <code>preset 4g</code> · <code>set текст</code> · <code>clear</code>\nОтмена: /cancel",
    ),
    "admin_order": (
        "admin_order",
        "Найти заказ.\nВведите номер заказа: <code>12345</code>\nОтмена: /cancel",
    ),
    "admin_user": (
        "admin_user",
        "Найти пользователя.\nВведите TG ID / @username / ник\nОтмена: /cancel",
    ),
}


async def _invoke_admin_command(
    *,
    proxy: _AdminCbMessage,
    settings: Settings,
    conn,
    state: FSMContext | None,
    cmd: str,
    args: str | None,
) -> None:
    """Вызвать существующий Command-handler от имени админа."""
    co = _cmd_obj(cmd, args)
    if cmd == "admqueue":
        await cmd_admqueue(proxy, settings, conn)  # type: ignore[arg-type]
    elif cmd == "admdeliveries":
        await cmd_adm_deliveries(proxy, settings, conn)  # type: ignore[arg-type]
    elif cmd == "admin_help":
        await cmd_admin_help(proxy, settings)  # type: ignore[arg-type]
    elif cmd == "admin_fin_show":
        await cmd_admin_fin_show(proxy, settings, conn)  # type: ignore[arg-type]
    elif cmd == "admin_fin_set":
        await cmd_admin_fin_set(proxy, co, settings, conn)  # type: ignore[arg-type]
    elif cmd == "admin_cogs":
        await cmd_admin_cogs(proxy, co, settings, conn)  # type: ignore[arg-type]
    elif cmd == "admin_recalc_profit":
        await cmd_admin_recalc_profit(proxy, co, settings, conn)  # type: ignore[arg-type]
    elif cmd == "admin_vpn":
        await cmd_admin_vpn(proxy, settings)  # type: ignore[arg-type]
    elif cmd == "admin_vpn_notices":
        await cmd_admin_vpn_notices(proxy, co, settings, conn)  # type: ignore[arg-type]
    elif cmd == "admin_vpn_status":
        await cmd_admin_vpn_status(proxy, co, settings, conn)  # type: ignore[arg-type]
    elif cmd == "admin_vpn_devices":
        await cmd_admin_vpn_devices(proxy, co, settings, conn)  # type: ignore[arg-type]
    elif cmd == "admin_vpn_trial_status":
        await cmd_admin_vpn_trial_status(proxy, co, settings, conn)  # type: ignore[arg-type]
    elif cmd == "admin_vpn_revoke":
        await cmd_admin_vpn_revoke(proxy, co, settings, conn)  # type: ignore[arg-type]
    elif cmd == "admin_vpn_extend":
        await cmd_admin_vpn_extend(proxy, co, settings, conn)  # type: ignore[arg-type]
    elif cmd == "admin_vpn_finalize":
        await cmd_admin_vpn_finalize(proxy, co, settings, conn)  # type: ignore[arg-type]
    elif cmd == "admin_vpn_announce":
        await cmd_admin_vpn_announce(proxy, co, settings, conn)  # type: ignore[arg-type]
    elif cmd == "channel_checkout_pin":
        await cmd_channel_checkout_pin(proxy, settings)  # type: ignore[arg-type]
    elif cmd == "admin_ref_withdraw":
        await cmd_admin_ref_withdraw(proxy, co, settings, conn)  # type: ignore[arg-type]
    elif cmd == "admin_ref_partner":
        await cmd_admin_ref_partner(proxy, co, settings, conn)  # type: ignore[arg-type]
    elif cmd == "admin_promo":
        await cmd_admin_promo(proxy, co, settings, conn)  # type: ignore[arg-type]
    elif cmd == "contest":
        await cmd_contest(proxy, co, settings, conn)  # type: ignore[arg-type]
    elif cmd == "admin_order":
        await cmd_admin_order(proxy, co, settings, conn)  # type: ignore[arg-type]
    elif cmd == "admin_user":
        await cmd_admin_user(proxy, co, settings, conn)  # type: ignore[arg-type]
    elif cmd == "admin_broadcast":
        from bot.handlers.broadcast import cmd_admin_broadcast

        if state is None:
            await proxy.answer("Нет FSM — напишите /admin_broadcast")
            return
        await cmd_admin_broadcast(proxy, settings, state)  # type: ignore[arg-type]
    elif cmd == "admin_broadcast_stats":
        from bot.handlers.broadcast import cmd_admin_broadcast_stats

        await cmd_admin_broadcast_stats(proxy, co, settings, conn)  # type: ignore[arg-type]
    else:
        await proxy.answer(f"Команда <code>/{esc(cmd)}</code> пока без автозапуска.")


async def _audit_admin(conn, admin_id: int, action: str, **parts: object) -> None:
    payload = json.dumps(parts, ensure_ascii=False) if parts else None
    await admin_audit_repo.append_admin_action(
        conn, admin_user_id=admin_id, action=action, payload_json=payload
    )


def _admin_order_message_text(
    order_row,
    order_id: int,
    settings: Settings,
    *,
    status_for_header: str | None = None,
) -> str:
    lbl = status_for_header or str(order_row["status"])
    amt = float(order_row["rub_after_discounts"])
    profit_block = ""
    if str(order_row["status"] or "").strip().lower() == "completed":
        try:
            profit_block = admin_profit_breakdown_html(
                order_row,
                payment_gateway_fee_percent=settings.payment_gateway_fee_percent,
            )
        except (KeyError, TypeError, ValueError):
            pass
    return (
        f"<b>#{esc(order_id)}</b> → <code>{esc(lbl)}</code>\n\n"
        f"{esc(order_row['product_title'])}\n"
        f"user: <code>{esc(order_row['user_id'])}</code>\n"
        f"сумма: <b>{esc(f'{amt:.2f}')} ₽</b>"
        f"{format_fulfillment_admin_block(order_row)}"
        f"{profit_block}"
    )


def _period_arg_to_days(arg: str) -> int | None:
    a = (arg or "").strip().lower()
    if a in ("all", "*", "full"):
        return None
    if a in ("today", "0d", "day"):
        return -1
    return int(a)


def _period_human(days: int | None) -> str:
    if days is None:
        return "всё время"
    if days in (-1, 0):
        return "сегодня"
    return f"{days} дн."


async def _vpn_admin_dashboard_extras(
    conn,
    settings: Settings,
    *,
    days: int | None,
) -> tuple[dict[str, float | int], dict[str, float | int], str | None]:
    vpn_rm = await admin_stats_repo.vpn_referral_metrics(conn, days=days)
    vpn_rm["vpn_ref_cfg_referrer_days"] = int(settings.vpn_referral_referrer_days)
    vpn_rm["vpn_ref_cfg_friend_days"] = int(settings.vpn_referral_friend_days)
    vpn_cp = await admin_stats_repo.fetch_vpn_controlplane_metrics(settings.resolved_vpn_db_path())
    vpn_health_html: str | None = None
    if (settings.vpn_api_base_url or "").strip():
        from bot.services.vpn_ops_health import collect_vpn_ops_health

        snap = await collect_vpn_ops_health(settings)
        vpn_health_html = snap.summary_html()
    return vpn_rm, vpn_cp, vpn_health_html


def _admin_stats_main_kb() -> InlineKeyboardMarkup:
    """Legacy full-report keyboard (tech). Prefer admin_ux.hub_keyboard for business UI."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Сегодня", callback_data="ast:d:today"),
                InlineKeyboardButton(text="7 дн.", callback_data="ast:d:7"),
            ],
            [
                InlineKeyboardButton(text="30 дн.", callback_data="ast:d:30"),
                InlineKeyboardButton(text="Всё время", callback_data="ast:d:all"),
            ],
            [
                InlineKeyboardButton(text="Продажи (7д)", callback_data="ast:sales:7"),
                InlineKeyboardButton(text="Продажи (30д)", callback_data="ast:sales:30"),
            ],
            [
                InlineKeyboardButton(text="Топ по прибыли", callback_data="ast:top:30"),
                InlineKeyboardButton(text="Динамика 14д", callback_data="ast:dyn:14"),
            ],
            [
                InlineKeyboardButton(text="График 30д", callback_data="ast:chart:30"),
                InlineKeyboardButton(text="Недели 12", callback_data="ast:week:12"),
            ],
            [
                InlineKeyboardButton(text="CSV 30д", callback_data="ast:csv:30"),
                InlineKeyboardButton(text="CSV всё", callback_data="ast:csv:all"),
            ],
            [
                InlineKeyboardButton(text="❤️ Состояние VPN (подробно)", callback_data="ast:vpn_health"),
            ],
            [
                InlineKeyboardButton(text="👻 Bridge зомби", callback_data="ast:vpn_zombies"),
            ],
            [
                InlineKeyboardButton(text="Последние выдачи", callback_data="ast:deliveries"),
            ],
            [
                InlineKeyboardButton(text="📊 Отчёт для руководителя", callback_data="ast:exec:7"),
            ],
            [
                InlineKeyboardButton(text="👑 Бизнес-панель", callback_data="aux:d:7"),
            ],
            admin_dashboard_help_row(),
        ]
    )


_ORDER_STATUS_HUMAN = {
    "pending_payment": "⏳ Ожидает оплаты",
    "paid": "🟢 Оплачен",
    "processing": "🔄 В обработке",
    "completed": "✅ Выдан",
    "cancelled": "🚫 Отменён",
    "expired": "⚪ Истёк",
    "refunded": "↩️ Возврат",
    "payment_disputed": "⚠️ Спор",
}


async def _count_pending_payment(conn) -> int:
    cur = await conn.execute(
        "SELECT COUNT(*) AS c FROM orders WHERE status = 'pending_payment'"
    )
    row = await cur.fetchone()
    if row is None:
        return 0
    try:
        return int(row["c"] or 0)
    except (KeyError, TypeError, IndexError):
        return int(row[0] or 0)

async def _vpn_status_only(settings: Settings) -> str | None:
    try:
        from bot.services.vpn_ops_health import collect_vpn_ops_health

        snap = await collect_vpn_ops_health(settings)
        return str(snap.status)
    except Exception:
        return None


async def _build_business_admin_message(
    conn,
    settings: Settings,
    *,
    days: int | None,
    period_token: str,
) -> tuple[str, InlineKeyboardMarkup]:
    label = admin_ux.period_label(days, token=period_token)
    # aggregate_dashboard: None = всё время / с запуска; иначе окно дней
    days_arg: int | None
    if days is None:
        days_arg = None
    elif days == 1:
        days_arg = 1
    else:
        days_arg = days
    agg = await admin_stats_repo.aggregate_dashboard(conn, days=days_arg)
    delta_rev = delta_net = None
    if days_arg is not None:
        prev = await admin_stats_repo.aggregate_dashboard(
            conn, days=days_arg, previous_period=True
        )
        delta_rev = admin_stats_repo.pct_delta(agg.revenue_rub, prev.revenue_rub)
        delta_net = admin_stats_repo.pct_delta(agg.net_profit_rub, prev.net_profit_rub)
    rm = await admin_stats_repo.referral_metrics(conn, days=days_arg)
    pending_ff = await admin_stats_repo.pending_fulfillment_metrics(conn, days=days_arg)
    _vpn_rm, vpn_cp, _vh = await _vpn_admin_dashboard_extras(
        conn, settings, days=days_arg if days_arg is not None else 3650
    )
    pending = await _count_pending_payment(conn)
    vpn_st = await _vpn_status_only(settings)
    rent_m = float(getattr(settings, "vpn_rent_monthly_rub", 0) or 0)
    rent_p = admin_ux.rent_estimate_rub(monthly_rub=rent_m, days=days)
    text = admin_ux.format_business_dashboard(
        period_label_s=label,
        agg=agg,
        rm=rm,
        vpn_cp=vpn_cp,
        vpn_status=vpn_st,
        pending_payment=pending,
        withdraw_pending=0,
        pending_fulfill_count=int(pending_ff.get("pending_fulfill_count", 0) or 0),
        pending_fulfill_rub=float(pending_ff.get("pending_fulfill_rub", 0) or 0),
        rent_monthly_rub=rent_m,
        rent_period_rub=rent_p,
        delta_revenue_pct=delta_rev,
        delta_net_pct=delta_net,
        usd_rub_rate=float(getattr(settings, "usd_rub_rate", 0) or 0),
    )
    return text, admin_ux.hub_keyboard(period_token=period_token)


async def _build_legacy_admin_message(
    conn,
    settings: Settings,
    *,
    days: int,
    period_label: str,
) -> tuple[str, InlineKeyboardMarkup]:
    agg = await admin_stats_repo.aggregate_dashboard(conn, days=days)
    top = await admin_stats_repo.top_referrers(conn, days=days, limit=3)
    rm = await admin_stats_repo.referral_metrics(conn, days=days)
    funnel = await admin_stats_repo.funnel_metrics(conn, days=days)
    pay_funnel = (
        await admin_stats_repo.payment_funnel_metrics(conn, days=days)
        if settings.feature_split_metrics_enabled
        else None
    )
    webhook_sla = (
        await admin_stats_repo.webhook_sla_metrics(conn, days=days)
        if settings.feature_split_metrics_enabled
        else None
    )
    cross_sell = (
        await admin_stats_repo.cross_sell_metrics(conn, days=days, window_days=30)
        if settings.feature_split_metrics_enabled
        else None
    )
    retention = (
        await admin_stats_repo.retention_metrics(conn, days=days)
        if settings.feature_split_metrics_enabled
        else None
    )
    acquisition = (
        await admin_stats_repo.acquisition_metrics(conn, days=days)
        if settings.feature_split_metrics_enabled
        else None
    )
    feedback = (
        await admin_stats_repo.feedback_metrics(conn, days=days)
        if settings.feature_feedback_metrics_enabled
        else None
    )
    vpn_rm, vpn_cp, vpn_h = await _vpn_admin_dashboard_extras(conn, settings, days=days)
    try:
        web_metrics = await admin_stats_repo.web_checkout_metrics(conn, days=days)
    except Exception:
        web_metrics = None
    dash = _format_dashboard_html(
        period_label=period_label,
        agg=agg,
        top_refs=top,
        rm=rm,
        funnel=funnel,
        pay_funnel=pay_funnel,
        webhook_sla=webhook_sla,
        cross_sell=cross_sell,
        retention=retention,
        acquisition=acquisition,
        feedback=feedback,
        vpn_rm=vpn_rm,
        vpn_cp=vpn_cp,
        vpn_health_html=vpn_h,
        web_metrics=web_metrics,
    )
    rows = await orders_repo.list_recent_orders(conn, limit=8)
    recent_lines = ["\n<b>Последние заказы</b>\n"]
    if not rows:
        recent_lines.append("<i>нет</i>")
    else:
        for r in rows:
            amt = float(r["rub_after_discounts"])
            st = _ORDER_STATUS_HUMAN.get(str(r["status"]), str(r["status"]))
            recent_lines.append(
                f"#{esc(r['id'])} {esc(r['product_title'])} · {esc(st)} · "
                f"<b>{esc(f'{amt:.2f}')} ₽</b>"
            )
    foot = (
        "\n\n<i>Справка: /admin_help · Это полный тех.отчёт (legacy).</i>"
        "\n<i>Бизнес-панель: кнопка «👑 Бизнес-панель» или /admin</i>"
    )
    if settings.admin_roles_restricted():
        foot += "\n<i>Роли: финансы и «Выдан» — SUPER_ADMIN_IDS.</i>"
    return dash + "\n".join(recent_lines) + foot, _admin_stats_main_kb()


def _format_dashboard_html(
    *,
    period_label: str,
    agg: admin_stats_repo.DashboardAgg,
    top_refs: list,
    rm: dict[str, float | int],
    funnel: dict[str, float | int] | None = None,
    pay_funnel: dict[str, float | int] | None = None,
    webhook_sla: dict[str, float | int] | None = None,
    cross_sell: dict[str, float | int] | None = None,
    retention: dict[str, float | int] | None = None,
    acquisition: dict[str, float | int] | None = None,
    feedback: dict[str, float | int] | None = None,
    vpn_rm: dict[str, float | int] | None = None,
    vpn_cp: dict[str, float | int] | None = None,
    vpn_health_html: str | None = None,
    web_metrics: dict[str, float | int] | None = None,
) -> str:
    avg = (agg.revenue_rub / agg.orders_count) if agg.orders_count else 0.0
    ref_bonus_total = float(rm.get("total_referral_bonus_rub", 0))
    lines = [
        f"<b>Дашборд</b> <i>({esc(period_label)})</i>\n",
        f"Выручка: <b>{esc(f'{agg.revenue_rub:.2f}')} ₽</b>",
        f"Заказов (выдано): <b>{esc(str(agg.orders_count))}</b>",
        f"Чистая прибыль: <b>{esc(f'{agg.net_profit_rub:.2f}')} ₽</b>",
        f"Средний чек: <b>{esc(f'{avg:.2f}')} ₽</b>\n",
        "<b>Stars</b> (штуки / ₽): "
        f"<code>{esc(str(agg.stars_units_sold))}</code> / "
        f"<b>{esc(f'{agg.stars_revenue_rub:.2f}')} ₽</b>",
        "<b>Premium</b> (покупок / ₽): "
        f"<code>{esc(str(agg.premium_units_sold))}</code> / "
        f"<b>{esc(f'{agg.premium_revenue_rub:.2f}')} ₽</b>",
        "<b>VPN</b> (покупок / ₽): "
        f"<code>{esc(str(agg.vpn_units_sold))}</code> / "
        f"<b>{esc(f'{agg.vpn_revenue_rub:.2f}')} ₽</b>\n",
        f"ARPPU: <b>{esc(f'{agg.arppu_rub:.2f}')} ₽</b> · VPN share: <b>{esc(f'{agg.vpn_revenue_share_pct:.2f}')}%</b>\n",
        f"Уникальных рефереров (с выданными): <code>{esc(str(agg.distinct_referrers))}</code>",
    ]
    if web_metrics is not None:
        lines.append(
            "\n<b>Web-checkout</b>\n"
            f"• paid/completed VPN (source=web): <code>{esc(str(web_metrics.get('web_vpn_completed', 0)))}</code>\n"
            f"• linked accounts (TG): <code>{esc(str(web_metrics.get('accounts_with_telegram', 0)))}</code>"
        )
    if funnel is not None:
        fv = int(funnel.get("funnel_visitors", 0) or 0)
        fc = int(funnel.get("funnel_converted", 0) or 0)
        fp = funnel.get("funnel_conversion_pct", 0)
        if fv > 0:
            lines.append(
                f"Воронка: визиты — <code>{esc(str(fv))}</code>, покупка после визита — "
                f"<code>{esc(str(fc))}</code> (<b>{esc(str(fp))}%</b>)"
            )
        else:
            lines.append("<i>Воронка: нет событий входа (/start, /menu) за период.</i>")
    if pay_funnel is not None:
        cr = int(pay_funnel.get("funnel_created_orders", 0) or 0)
        pd = int(pay_funnel.get("funnel_paid_orders", 0) or 0)
        cd = int(pay_funnel.get("funnel_completed_orders", 0) or 0)
        lines.append(
            "\n<b>Payment funnel</b>\n"
            f"• created: <code>{esc(str(cr))}</code> · paid: <code>{esc(str(pd))}</code> · completed: <code>{esc(str(cd))}</code>\n"
            f"• paid rate: <b>{esc(str(pay_funnel.get('funnel_paid_rate_pct', 0)))}%</b> · "
            f"completed/paid: <b>{esc(str(pay_funnel.get('funnel_completed_from_paid_pct', 0)))}%</b>"
        )
    if webhook_sla is not None:
        lines.append(
            "\n<b>Webhook SLA</b>\n"
            f"• success: <b>{esc(str(webhook_sla.get('webhook_success_rate_pct', 0)))}%</b> · "
            f"retry: <code>{esc(str(webhook_sla.get('webhook_retry_rate_pct', 0)))}%</code>\n"
            f"• p50/p95: <code>{esc(str(webhook_sla.get('webhook_latency_p50_sec', -1.0)))}</code> / "
            f"<code>{esc(str(webhook_sla.get('webhook_latency_p95_sec', -1.0)))}</code> sec · "
            f"backlog: <code>{esc(str(webhook_sla.get('webhook_backlog', 0)))}</code>"
        )
    if cross_sell is not None:
        lines.append(
            "\n<b>Cross-sell (30d)</b>\n"
            f"• Stars/Premium → VPN: <code>{esc(str(cross_sell.get('cross_sell_sp_to_vpn_n', 0)))}</code> "
            f"из <code>{esc(str(cross_sell.get('cross_sell_sp_base', 0)))}</code> "
            f"(<b>{esc(str(cross_sell.get('cross_sell_sp_to_vpn_pct', 0)))}%</b>)\n"
            f"• VPN → Stars/Premium: <code>{esc(str(cross_sell.get('cross_sell_vpn_to_sp_n', 0)))}</code> "
            f"из <code>{esc(str(cross_sell.get('cross_sell_vpn_base', 0)))}</code> "
            f"(<b>{esc(str(cross_sell.get('cross_sell_vpn_to_sp_pct', 0)))}%</b>)"
        )
    if retention is not None:
        lines.append(
            "\n<b>Retention</b>\n"
            f"• Cohort: <code>{esc(str(retention.get('retention_cohort_size', 0)))}</code>\n"
            f"• D7: <code>{esc(str(retention.get('retention_d7_n', 0)))}</code> "
            f"(<b>{esc(str(retention.get('retention_d7_pct', 0)))}%</b>) · "
            f"D30: <code>{esc(str(retention.get('retention_d30_n', 0)))}</code> "
            f"(<b>{esc(str(retention.get('retention_d30_pct', 0)))}%</b>)"
        )
    if acquisition is not None:
        spend_s = f"{float(acquisition.get('acq_spend_rub', 0.0)):.2f}"
        cac_s = f"{float(acquisition.get('acq_cac_rub', 0.0)):.2f}"
        lines.append(
            "\n<b>Acquisition</b>\n"
            f"• spend: <code>{esc(spend_s)}</code> ₽ · "
            f"paid users: <code>{esc(str(acquisition.get('acq_paid_users', 0)))}</code> · "
            f"CAC: <b>{esc(cac_s)}</b> ₽\n"
            f"• CTR: <code>{esc(str(acquisition.get('acq_ctr_pct', 0)))}%</code> · "
            f"CR: <code>{esc(str(acquisition.get('acq_cr_pct', 0)))}%</code>"
        )
    if feedback is not None:
        lines.append(
            "\n<b>NPS / CSAT</b>\n"
            f"• NPS: <b>{esc(str(feedback.get('nps_score', 0)))}%</b> · "
            f"avg: <code>{esc(str(feedback.get('nps_avg', 0)))} / 10</code> · "
            f"responses: <code>{esc(str(feedback.get('nps_responses', 0)))}</code>\n"
            f"• CSAT: <b>{esc(str(feedback.get('csat_pct', 0)))}%</b> · "
            f"avg: <code>{esc(str(feedback.get('csat_avg', 0)))} / 5</code> · "
            f"responses: <code>{esc(str(feedback.get('csat_responses', 0)))}</code>"
        )
    if vpn_rm is not None:
        vst = int(vpn_rm.get("vpn_ref_starts", 0) or 0)
        gnt = int(vpn_rm.get("vpn_ref_grants", 0) or 0)
        rd_sum = int(vpn_rm.get("vpn_ref_referrer_days", 0) or 0)
        fd_sum = int(vpn_rm.get("vpn_ref_friend_days", 0) or 0)
        okf = int(vpn_rm.get("vpn_ref_api_friend_ok", 0) or 0)
        okr = int(vpn_rm.get("vpn_ref_api_referrer_ok", 0) or 0)
        pnd_f = int(vpn_rm.get("vpn_ref_pending_friend_api", 0) or 0)
        pnd_r = int(vpn_rm.get("vpn_ref_pending_referrer_api", 0) or 0)
        ret_f = int(vpn_rm.get("vpn_ref_pending_friend_retried", 0) or 0)
        ret_r = int(vpn_rm.get("vpn_ref_pending_referrer_retried", 0) or 0)
        cfg_rr = int(vpn_rm.get("vpn_ref_cfg_referrer_days", 0) or 0)
        cfg_fr = int(vpn_rm.get("vpn_ref_cfg_friend_days", 0) or 0)
        c_pct = round(100.0 * gnt / vst, 1) if vst else 0.0
        lines.append(
            "\n<b>VPN-рефералка</b> (период)\n"
            f"• Env N/M дней: реферер <code>{esc(str(cfg_rr))}</code> · друг <code>{esc(str(cfg_fr))}</code>\n"
            f"• Входы по ссылке <code>r-</code>: <code>{esc(str(vst))}</code>\n"
            f"• Первых выданных VPN с бонусом: <code>{esc(str(gnt))}</code> "
            f"(конверсия от входа: <b>{esc(str(c_pct))}%</b>)\n"
            f"• Дней начислено реферерам / друзьям: <b>{esc(str(rd_sum))}</b> / <b>{esc(str(fd_sum))}</b>\n"
            f"• Подтверждённо API (друг / реферер): <code>{esc(str(okf))}</code> / <code>{esc(str(okr))}</code>\n"
            f"• Без OK API (друг / реферер): <code>{esc(str(pnd_f))}</code> / <code>{esc(str(pnd_r))}</code> "
            f"(из них после ошибки: <code>{esc(str(ret_f))}</code> / <code>{esc(str(ret_r))}</code>)"
        )
    if vpn_cp is not None and int(vpn_cp.get("vpn_cp_available", 0) or 0) == 1:
        tot_a = int(vpn_cp.get("vpn_cp_accounts_total", 0) or 0)
        tot_j = int(vpn_cp.get("vpn_cp_jobs_total", 0) or 0)
        pend_j = int(vpn_cp.get("vpn_cp_jobs_pending", 0) or 0)
        fail_j = int(vpn_cp.get("vpn_cp_jobs_failed", 0) or 0)
        p95 = vpn_cp.get("vpn_cp_p95_provision_sec", -1.0)
        p95_s = "—" if p95 is None or float(p95) < 0 else esc(f"{float(p95):.2f}")
        samp = int(vpn_cp.get("vpn_cp_provision_done_sample_n", 0) or 0)
        act = int(vpn_cp.get("vpn_cp_accounts_vpn_active", 0) or 0)
        prov = int(vpn_cp.get("vpn_cp_accounts_vpn_provisioning", 0) or 0)
        fail_acc = int(vpn_cp.get("vpn_cp_accounts_vpn_failed", 0) or 0)
        mo_acc = int(vpn_cp.get("vpn_cp_accounts_vpn_manual_override", 0) or 0)
        exp_acc = int(vpn_cp.get("vpn_cp_accounts_vpn_expired", 0) or 0)
        lines.append(
            "\n<b>VPN control plane</b> (<code>vpn.db</code>)\n"
            f"• Аккаунты всего: <code>{esc(str(tot_a))}</code> "
            f"(active <code>{esc(str(act))}</code>, provisioning <code>{esc(str(prov))}</code>, "
            f"failed <code>{esc(str(fail_acc))}</code>, "
            f"<code>vpn_manual_override</code> <code>{esc(str(mo_acc))}</code>, "
            f"expired <code>{esc(str(exp_acc))}</code>)\n"
            f"• Jobs всего: <code>{esc(str(tot_j))}</code> · pending <code>{esc(str(pend_j))}</code> · failed "
            f"<code>{esc(str(fail_j))}</code>\n"
            f"• p95 времени job <code>provision</code>→done: <b>{p95_s}</b> с "
            f"(выборка <code>{esc(str(samp))}</code>)"
        )
    elif vpn_cp is not None and int(vpn_cp.get("vpn_cp_available", 0) or 0) < 0:
        lines.append("\n<i>VPN control plane: ошибка чтения vpn.db (см. лог).</i>")
    if vpn_health_html:
        lines.append(f"\n{vpn_health_html}")
    lines += [
        f"Реф. скидка в заказах: <code>{esc(str(rm.get('orders_with_ref_discount', 0)))}</code> "
        f"из <code>{esc(str(rm.get('completed_orders', 0)))}</code> "
        f"({esc(str(rm.get('ref_discount_pct', 0)))}%)",
        f"Бонусы реферерам (начислено в заказах): <b>{esc(f'{ref_bonus_total:.2f}')} ₽</b>\n",
        "<b>Топ рефереров</b> (по сумме бонуса):",
    ]
    if not top_refs:
        lines.append("<i>нет данных</i>")
    else:
        for i, r in enumerate(top_refs[:3], start=1):
            rid = int(r["rid"])
            bonus = float(r["bonus_rub"] or 0)
            lines.append(f"{i}. <code>{esc(str(rid))}</code> — <b>{esc(f'{bonus:.2f}')} ₽</b>")
    return "\n".join(lines)


async def _build_sales_report_html(conn, days: int | None) -> str:
    stars = await admin_stats_repo.stars_by_package(conn, days=days)
    prem = await admin_stats_repo.premium_by_term(conn, days=days)
    label = _period_human(days)
    lines = [f"<b>Продажи</b> <i>({esc(label)})</i>\n", "<b>Stars / подарки</b> (пакет ⭐ → шт / ₽):"]
    if not stars:
        lines.append("<i>нет</i>")
    else:
        for r in stars:
            pack = int(r["pack"] or 0)
            n = int(r["n"] or 0)
            rev = float(r["rev"] or 0)
            lines.append(f"· <code>{esc(str(pack))}</code> ⭐: <b>{esc(str(n))}</b> × {esc(f'{rev:.2f}')} ₽")
    lines.append("\n<b>Premium</b> (месяцы → шт / ₽):")
    if not prem:
        lines.append("<i>нет</i>")
    else:
        for r in prem:
            m = int(r["months"] or 0)
            n = int(r["n"] or 0)
            rev = float(r["rev"] or 0)
            lines.append(f"· <code>{esc(str(m))}</code> мес: <b>{esc(str(n))}</b> × {esc(f'{rev:.2f}')} ₽")
    return "\n".join(lines)


async def _build_dyn_html(conn, days: int) -> str:
    rows = await admin_stats_repo.sales_by_day(conn, days=days)
    lines = [f"<b>По дням</b> (последние {esc(str(days))} дн., оплаченные)\n"]
    if not rows:
        lines.append("<i>нет данных</i>")
    else:
        for r in rows:
            d = str(r["d"] or "")
            n = int(r["n"] or 0)
            rev = float(r["rev"] or 0)
            netp = float(r["netp"] or 0)
            lines.append(
                f"<code>{esc(d)}</code>: {esc(str(n))} зак. · "
                f"{esc(f'{rev:.2f}')} ₽ · прибыль {esc(f'{netp:.2f}')} ₽"
            )
    return "\n".join(lines)


async def _build_week_html(conn, weeks: int) -> str:
    w = max(2, min(52, int(weeks)))
    rows = await admin_stats_repo.sales_by_week(conn, days=w * 7)
    lines = [f"<b>По неделям</b> (≈{esc(str(w))} нед., оплаченные)\n"]
    if not rows:
        lines.append("<i>нет данных</i>")
    else:
        for r in rows:
            wlabel = str(r["wk"] or "")
            n = int(r["n"] or 0)
            rev = float(r["rev"] or 0)
            netp = float(r["netp"] or 0)
            lines.append(
                f"<code>{esc(wlabel)}</code>: {esc(str(n))} зак. · "
                f"{esc(f'{rev:.2f}')} ₽ · прибыль {esc(f'{netp:.2f}')} ₽"
            )
    return "\n".join(lines)


@router.callback_query(F.data.startswith("adm:ff"))
async def admin_fulfill_controls(cb: CallbackQuery, settings: Settings, conn) -> None:
    """Ручной override автовыдачи и сброс полей (план 37-6). Должен быть до обработчика `adm:paid` и т.д."""
    if not _is_admin(cb.from_user.id, settings):
        await cb.answer("Нет доступа", show_alert=True)
        return
    parts = cb.data.split(":")
    if len(parts) != 3 or parts[0] != "adm":
        await cb.answer()
        return
    action, oid_s = parts[1], parts[2]
    if action not in ("ffman", "ffauto", "ffrst") or not oid_s.isdigit():
        await cb.answer()
        return
    order_id = int(oid_s)

    order = await orders_repo.get_order(conn, order_id)
    if not order:
        await cb.answer("Заказ не найден", show_alert=True)
        return

    st = str(order["status"] or "").strip().lower()
    if st in ("completed", "expired", "refunded", "payment_disputed"):
        await cb.answer("Заказ уже завершён или в споре.", show_alert=True)
        return
    if st not in ("paid", "processing"):
        await cb.answer("Действие только для оплаченных / в работе.", show_alert=True)
        return

    if action == "ffman":
        ok = await orders_repo.set_order_fulfillment_mode(conn, order_id, mode="manual_only")
        if not ok:
            await cb.answer("Не удалось обновить режим.", show_alert=True)
            return
        await _audit_admin(conn, cb.from_user.id, "adm:ffman", order_id=order_id)
    elif action == "ffauto":
        if not settings.is_super_admin(cb.from_user.id):
            await cb.answer("Только супер-админ включает авто снова.", show_alert=True)
            return
        ok = await orders_repo.set_order_fulfillment_mode(conn, order_id, mode="auto")
        if not ok:
            await cb.answer("Не удалось обновить режим.", show_alert=True)
            return
        await _audit_admin(conn, cb.from_user.id, "adm:ffauto", order_id=order_id)
    elif action == "ffrst":
        if not settings.is_super_admin(cb.from_user.id):
            await cb.answer("Только супер-админ сбрасывает поля авто-выдачи.", show_alert=True)
            return
        if st == "processing":
            ok = await orders_repo.revert_failed_processing_to_paid_for_retry(conn, order_id)
            if not ok:
                await cb.answer(
                    "Сброс processing только при зафиксированной ошибке выдачи.",
                    show_alert=True,
                )
                return
        elif st == "paid":
            ok = await orders_repo.super_reset_paid_auto_fulfill_fields(conn, order_id)
            if not ok:
                await cb.answer("Сброс не применён (проверьте статус заказа).", show_alert=True)
                return
        else:
            await cb.answer("Сброс только для «Оплачен» / «В работе» с ошибкой.", show_alert=True)
            return
        await _audit_admin(conn, cb.from_user.id, "adm:ffrst", order_id=order_id)
    else:
        await cb.answer()
        return

    order2 = await orders_repo.get_order(conn, order_id)
    await cb.message.edit_text(
        _admin_order_message_text(order2, order_id, settings),
        reply_markup=admin_order_kb(
            order_id,
            settings=settings,
            actor_id=cb.from_user.id,
            order_ff=ff_context_from_order_row(order2),
        ),
    )
    await cb.answer("OK")


async def _build_user_card_message(
    conn,
    settings: Settings,
    *,
    user_id: int,
    period_token: str = "7",
) -> tuple[str, InlineKeyboardMarkup]:
    u = await users_repo.get_user(conn, user_id)
    stats = await users_repo.user_stats(conn, user_id)
    products = await users_repo.user_product_counts(conn, user_id)
    vpn_status = vpn_until = vpn_kind = None
    vpath = settings.resolved_vpn_db_path()
    if vpath is not None:
        snap = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, user_id)
        if snap:
            vpn_status = snap.get("status") or None
            vpn_until = snap.get("paid_until") or None
            vpn_kind = snap.get("account_kind") or None
    text = admin_ux.format_user_card(
        user_id=user_id,
        username=(str(u["username"]) if u and u["username"] else None),
        first_name=(str(u["first_name"]) if u and u["first_name"] else None),
        created_at=(str(u["created_at"]) if u and u["created_at"] else None),
        referrer_id=(int(u["referrer_id"]) if u and u["referrer_id"] is not None else None),
        stats=stats,
        products=products,
        vpn_status=vpn_status,
        vpn_until=vpn_until,
        vpn_kind=vpn_kind,
    )
    return text, admin_ux.user_card_kb(user_id=user_id, period_token=period_token)


@router.message(Command("admin"))
async def cmd_admin(message: Message, settings: Settings, conn) -> None:
    if not await _require_admin_message(message, settings):
        return
    text, kb = await _build_business_admin_message(
        conn, settings, days=7, period_token="7"
    )
    await message.answer(text, reply_markup=kb)


@router.message(Command("admin_order"))
async def cmd_admin_order(
    message: Message, command: CommandObject, settings: Settings, conn
) -> None:
    """🔎 Найти заказ по id — карточка + adm:ff / status actions."""
    if not await _require_admin_message(message, settings):
        return
    raw = (command.args or "").strip().split()
    if not raw:
        await message.answer(
            "Использование: <code>/admin_order 12345</code>\n"
            "Или из меню: 💰 Продажи → 🔎 Найти заказ."
        )
        return
    try:
        order_id = int(raw[0].lstrip("#"))
    except ValueError:
        await message.answer("Номер заказа должен быть числом.")
        return
    order = await orders_repo.get_order(conn, order_id)
    if order is None:
        await message.answer(f"Заказ <code>#{esc(order_id)}</code> не найден.")
        return
    ff = ff_context_from_order_row(order)
    text = _admin_order_message_text(order, order_id, settings)
    actions = admin_order_kb(
        order_id,
        settings=settings,
        actor_id=message.from_user.id,
        order_ff=ff,
    )
    kb = admin_ux.merge_inline_kb(
        actions,
        admin_ux.order_card_back_kb(
            period_token="7",
            user_id=int(order["user_id"]),
        ),
    )
    await message.answer(text, reply_markup=kb)


@router.message(Command("admin_user"))
async def cmd_admin_user(
    message: Message, command: CommandObject, settings: Settings, conn
) -> None:
    """👥 Карточка пользователя: TG id / @username / #заказ / ref / ник."""
    if not await _require_admin_message(message, settings):
        return
    raw = (command.args or "").strip()
    if not raw:
        await message.answer(
            "Использование:\n"
            "<code>/admin_user 123456789</code>\n"
            "<code>/admin_user @username</code>\n"
            "<code>/admin_user #104</code>\n"
            "Или меню: 👥 Пользователи → 🔎 Найти."
        )
        return
    uid, how = await users_repo.resolve_admin_user_query(conn, raw)
    if uid is None:
        await message.answer(
            f"Не найдено: <code>{esc(raw)}</code>\n"
            f"(попытка: {esc(how)})\n"
            "Ник сайта: <code>/admin_find_nick …</code>"
        )
        return
    text, kb = await _build_user_card_message(
        conn, settings, user_id=uid, period_token="7"
    )
    note = "" if how in ("tg_id", "tg_id_raw") else f"\n<i>найдено по: {esc(how)}</i>"
    await message.answer(text + note, reply_markup=kb)


@router.callback_query(F.data.startswith("aux:"))
async def admin_ux_callbacks(
    cb: CallbackQuery, settings: Settings, conn, state: FSMContext
) -> None:
    """Business admin hub (ТЗ UX). Does not remove legacy ast:/adm: handlers."""
    if not _is_admin(cb.from_user.id, settings):
        await cb.answer("Нет доступа", show_alert=True)
        return
    raw = (cb.data or "").strip()
    parts = raw.split(":")
    if len(parts) < 2:
        await cb.answer()
        return
    action = parts[1]

    async def _edit(text: str, kb: InlineKeyboardMarkup) -> None:
        try:
            await cb.message.edit_text(text, reply_markup=kb)
        except Exception:
            await cb.message.answer(text, reply_markup=kb)

    if action == "d" and len(parts) >= 3:
        token = parts[2]
        days = admin_ux.days_from_token(token)
        # normalize token for keyboard
        if token in ("today", "1"):
            ptok = "today"
        elif token in ("all", "0"):
            ptok = "all"
        elif token in ("start", "since", "launch"):
            ptok = "start"
        else:
            ptok = token
        text, kb = await _build_business_admin_message(
            conn, settings, days=days, period_token=ptok
        )
        await _edit(text, kb)
        await cb.answer()
        return

    if action == "legacy" and len(parts) >= 3:
        token = parts[2]
        days = admin_ux.days_from_token(token) or 7
        if days is None:
            days = 3650
        text, kb = await _build_legacy_admin_message(
            conn, settings, days=int(days), period_label=admin_ux.period_label(days if days < 3650 else None)
        )
        await _edit(text, kb)
        await cb.answer()
        return

    period_token = "7"
    kind_token = "all"
    product_kind: str | None = None
    if action in ("user", "user_orders", "user_vpn") and len(parts) >= 4:
        period_token = parts[3]
    elif action == "order" and len(parts) >= 4:
        period_token = parts[3]
    elif action == "vpn_health_simple" and len(parts) >= 3:
        period_token = parts[2]
    elif action in ("pending", "finance", "sales") and len(parts) >= 3:
        period_token, product_kind = admin_ux.parse_period_kind(parts[2:])
        kind_token = admin_ux.kind_token(product_kind)
    elif (
        action
        in (
            "stats",
            "orders",
            "find_order",
            "users",
            "find_user",
            "vpn",
            "ref",
            "withdraw",
            "promo",
            "promo_list",
            "contest",
            "contest_list",
            "mkt",
            "export",
            "sys",
            "settings",
            "attention",
            "expired_vpn",
        )
        and len(parts) >= 3
    ):
        period_token = parts[2]
    elif action == "withdraw_list" and len(parts) >= 4:
        period_token = parts[3]
    elif action == "export_run" and len(parts) >= 3:
        period_token = "7"

    def _ux_days_arg(days: int | None) -> int | None:
        if days is None:
            return None
        if days == 1:
            return 1
        return days

    if action == "sales":
        days = admin_ux.days_from_token(period_token)
        days_arg = _ux_days_arg(days)
        agg = await admin_stats_repo.aggregate_dashboard(
            conn, days=days_arg, product_kind=product_kind
        )
        status_counts = await admin_stats_repo.order_status_counts(
            conn, days=days_arg, product_kind=product_kind
        )
        text = admin_ux.format_sales_screen(
            period_label_s=admin_ux.period_label(days, token=period_token),
            agg=agg,
            status_counts=status_counts,
            kind_label_s=admin_ux.kind_label(product_kind),
        )
        await _edit(
            text,
            admin_ux.sales_section_kb(period_token=period_token, kind_token=kind_token),
        )
        await cb.answer()
        return

    if action == "orders":
        rows = await orders_repo.list_recent_orders(conn, limit=12)
        lines = ["📦 <b>Последние заказы</b>\n"]
        order_ids: list[int] = []
        if not rows:
            lines.append("<i>нет</i>")
        else:
            for r in rows:
                oid = int(r["id"])
                order_ids.append(oid)
                amt = float(r["rub_after_discounts"])
                st = _ORDER_STATUS_HUMAN.get(str(r["status"]), str(r["status"]))
                lines.append(
                    f"#{esc(oid)} · {esc(r['product_title'])} · "
                    f"{esc(f'{amt:.2f}')} ₽ · {esc(st)}"
                )
            lines.append("\nНажмите номер заказа ниже → карточка и действия.")
        await _edit(
            "\n".join(lines),
            admin_ux.orders_list_kb(order_ids, period_token=period_token),
        )
        await cb.answer()
        return

    if action == "find_order":
        await state.set_state(AdminCmdStates.waiting_args)
        await state.update_data(admin_cmd="admin_order", period_token=period_token)
        await _edit(
            "🔎 <b>Найти заказ</b>\n\n"
            "Введите номер заказа (бот сам откроет карточку):\n"
            "<code>12345</code>\n\n"
            "Отмена: /cancel",
            InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="📦 Последние заказы",
                            callback_data=f"aux:orders:{period_token}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="🔙 К продажам",
                            callback_data=f"aux:sales:{period_token}",
                        )
                    ],
                ]
            ),
        )
        await cb.answer()
        return

    if action == "order" and len(parts) >= 3:
        try:
            order_id = int(parts[2])
        except ValueError:
            await cb.answer("Некорректный id", show_alert=True)
            return
        order = await orders_repo.get_order(conn, order_id)
        if order is None:
            await cb.answer("Заказ не найден", show_alert=True)
            return
        ff = ff_context_from_order_row(order)
        text = _admin_order_message_text(order, order_id, settings)
        actions = admin_order_kb(
            order_id,
            settings=settings,
            actor_id=cb.from_user.id,
            order_ff=ff,
        )
        kb = admin_ux.merge_inline_kb(
            actions,
            admin_ux.order_card_back_kb(
                period_token=period_token,
                user_id=int(order["user_id"]),
            ),
        )
        await _edit(text, kb)
        await cb.answer()
        return

    if action == "users":
        await _edit(
            admin_ux.format_users_hub(),
            admin_ux.users_section_kb(period_token=period_token),
        )
        await cb.answer()
        return

    if action == "find_user":
        await state.set_state(AdminCmdStates.waiting_args)
        await state.update_data(admin_cmd="admin_user", period_token=period_token)
        await _edit(
            "🔎 <b>Найти пользователя</b>\n\n"
            "Введите TG ID / @username / #заказ / ник / ref_…\n"
            "Бот сам откроет карточку.\n\n"
            "Отмена: /cancel",
            InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔙 К пользователям",
                            callback_data=f"aux:users:{period_token}",
                        )
                    ]
                ]
            ),
        )
        await cb.answer()
        return

    if action in ("user", "user_orders", "user_vpn") and len(parts) >= 3:
        try:
            uid = int(parts[2])
        except ValueError:
            await cb.answer("Некорректный id", show_alert=True)
            return
        if action == "user_orders":
            rows = await orders_repo.list_user_orders(conn, uid, limit=12)
            lines = [f"📦 <b>Заказы</b> пользователя <code>{esc(uid)}</code>\n"]
            order_ids: list[int] = []
            if not rows:
                lines.append("<i>нет</i>")
            else:
                for r in rows:
                    oid = int(r["id"])
                    order_ids.append(oid)
                    amt = float(r["rub_after_discounts"])
                    st = _ORDER_STATUS_HUMAN.get(str(r["status"]), str(r["status"]))
                    lines.append(
                        f"#{esc(oid)} · {esc(r['product_title'])} · "
                        f"{esc(f'{amt:.2f}')} ₽ · {esc(st)}"
                    )
            # reuse orders_list_kb but back to user card
            rows_kb: list[list[InlineKeyboardButton]] = []
            row_btns: list[InlineKeyboardButton] = []
            for oid in order_ids[:12]:
                row_btns.append(
                    InlineKeyboardButton(
                        text=f"#{oid}",
                        callback_data=f"aux:order:{oid}:{period_token}",
                    )
                )
                if len(row_btns) >= 3:
                    rows_kb.append(row_btns)
                    row_btns = []
            if row_btns:
                rows_kb.append(row_btns)
            rows_kb.append(
                [
                    InlineKeyboardButton(
                        text="👤 К карточке",
                        callback_data=f"aux:user:{uid}:{period_token}",
                    )
                ]
            )
            await _edit("\n".join(lines), InlineKeyboardMarkup(inline_keyboard=rows_kb))
            await cb.answer()
            return
        if action == "user_vpn":
            vpath = settings.resolved_vpn_db_path()
            if vpath is None:
                await cb.answer("VPN_DB_PATH не задан", show_alert=True)
                return
            snap = await vpn_admin_support_repo.fetch_vpn_account_admin_snapshot(vpath, uid)
            if snap is None:
                txt = "vpn.db недоступна"
            else:
                txt = vpn_admin_support_repo.format_vpn_admin_snapshot_html(snap)
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="👤 К карточке",
                            callback_data=f"aux:user:{uid}:{period_token}",
                        )
                    ]
                ]
            )
            await _edit(txt, kb)
            await cb.answer()
            return
        # user card
        text, kb = await _build_user_card_message(
            conn, settings, user_id=uid, period_token=period_token
        )
        await _edit(text, kb)
        await cb.answer()
        return

    if action == "vpn":
        days = admin_ux.days_from_token(period_token)
        days_arg: int | None = None if days is None else days
        agg = await admin_stats_repo.aggregate_dashboard(conn, days=days_arg)
        _rm, vpn_cp, _ = await _vpn_admin_dashboard_extras(
            conn, settings, days=days_arg if days_arg is not None else 3650
        )
        vpn_st = await _vpn_status_only(settings)
        text = admin_ux.format_vpn_hub(
            period_label_s=admin_ux.period_label(days, token=period_token),
            vpn_status=vpn_st,
            vpn_cp=vpn_cp,
            vpn_units_sold=int(agg.vpn_units_sold or 0),
            vpn_revenue_rub=float(agg.vpn_revenue_rub or 0),
            vpn_net_profit_rub=float(getattr(agg, "vpn_net_profit_rub", 0) or 0),
        )
        await _edit(text, admin_ux.vpn_section_kb(period_token=period_token))
        await cb.answer()
        return

    if action == "vpn_health_simple":
        st = await _vpn_status_only(settings)
        days = admin_ux.days_from_token(period_token)
        days_arg: int | None = None if days is None else days
        _rm, vpn_cp, _ = await _vpn_admin_dashboard_extras(
            conn, settings, days=days_arg if days_arg is not None else 7
        )
        pending_jobs = int((vpn_cp or {}).get("vpn_cp_jobs_pending", 0) or 0)
        failed_jobs = int((vpn_cp or {}).get("vpn_cp_jobs_failed", 0) or 0)
        p95 = float((vpn_cp or {}).get("vpn_cp_p95_provision_sec", -1) or -1)
        icon = {"ok": "🟢", "degraded": "🟡", "critical": "🔴"}.get((st or "").lower(), "⚪")
        lines = [
            "❤️ <b>Состояние VPN</b>",
            f"{icon} Сервис: <b>{esc(st or 'н/д')}</b>",
            f"Очередь jobs: {'🟢 пусто' if pending_jobs == 0 else '🟡 ' + str(pending_jobs)}",
            f"Ошибки jobs: {'🟢 нет' if failed_jobs == 0 else '🔴 ' + str(failed_jobs)}",
        ]
        if p95 >= 0:
            lines.append(f"📦 Среднее время выдачи VPN: ~<b>{esc(f'{p95:.0f}')}</b> сек")
        lines.append("\n🔧 Подробности (RTT/CF/swap) — кнопка ниже.")
        await _edit("\n".join(lines), admin_ux.vpn_section_kb(period_token=period_token))
        await cb.answer()
        return

    if action == "finance":
        from bot.services import fin_settings_repo

        days = admin_ux.days_from_token(period_token)
        days_arg: int | None = None if days is None else days
        agg = await admin_stats_repo.aggregate_dashboard(
            conn, days=days_arg, product_kind=product_kind
        )
        delta_rev = delta_net = None
        if days_arg is not None:
            prev = await admin_stats_repo.aggregate_dashboard(
                conn, days=days_arg, previous_period=True, product_kind=product_kind
            )
            delta_rev = admin_stats_repo.pct_delta(agg.revenue_rub, prev.revenue_rub)
            delta_net = admin_stats_repo.pct_delta(agg.net_profit_rub, prev.net_profit_rub)
        pending_ff = await admin_stats_repo.pending_fulfillment_metrics(
            conn, days=days_arg, product_kind=product_kind
        )
        ov = await fin_settings_repo.get_all(conn)
        fin_s = fin_settings_repo.apply_overrides(settings, ov)
        rent_m = float(getattr(fin_s, "vpn_rent_monthly_rub", 0) or 0)
        rent_p = admin_ux.rent_estimate_rub(monthly_rub=rent_m, days=days)
        text = admin_ux.format_finance_hub(
            period_label_s=admin_ux.period_label(days, token=period_token),
            agg=agg,
            pending_fulfill_count=int(pending_ff.get("pending_fulfill_count", 0) or 0),
            pending_fulfill_rub=float(pending_ff.get("pending_fulfill_rub", 0) or 0),
            rent_monthly_rub=rent_m,
            rent_period_rub=rent_p,
            fee_lava_card=float(getattr(fin_s, "fee_lava_card_percent", 6) or 6),
            fee_sbp=float(getattr(fin_s, "fee_sbp_percent", 3.4) or 3.4),
            fee_crypto=float(getattr(fin_s, "fee_crypto_bot_percent", 3) or 3),
            fee_xrocket=float(getattr(fin_s, "fee_xrocket_percent", 1.5) or 1.5),
            fragment_star=float(getattr(fin_s, "fragment_star_usdt", 0.015) or 0.015),
            fragment_1m=float(getattr(fin_s, "fragment_premium_1m_usdt", 0) or 0),
            fragment_3m=float(getattr(fin_s, "fragment_premium_3m_usdt", 11.99) or 11.99),
            fragment_6m=float(getattr(fin_s, "fragment_premium_6m_usdt", 15.99) or 15.99),
            fragment_12m=float(getattr(fin_s, "fragment_premium_12m_usdt", 28.99) or 28.99),
            delta_revenue_pct=delta_rev,
            delta_net_pct=delta_net,
            override_keys=set(ov.keys()),
            usd_rub_rate=float(getattr(fin_s, "usd_rub_rate", 0) or 0),
            kind_label_s=admin_ux.kind_label(product_kind),
        )
        await _edit(
            text,
            admin_ux.finance_section_kb(period_token=period_token, kind_token=kind_token),
        )
        await cb.answer()
        return

    if action == "ref":
        from bot.services import ref_withdraw_repo

        days = admin_ux.days_from_token(period_token)
        days_arg: int | None = None if days is None else days
        rm = await admin_stats_repo.referral_metrics(conn, days=days_arg)
        vpn_rm = await admin_stats_repo.vpn_referral_metrics(conn, days=days_arg)
        top = await admin_stats_repo.top_referrers(conn, days=days_arg, limit=5)
        wsum = await ref_withdraw_repo.withdraw_status_summary(conn)
        cur_bal = await conn.execute(
            "SELECT COALESCE(SUM(ref_balance_rub), 0) AS s FROM users WHERE ref_balance_rub > 0.009"
        )
        bal_row = await cur_bal.fetchone()
        available = float(bal_row["s"] or 0) if bal_row else 0.0
        text = admin_ux.format_ref_hub(
            period_label_s=admin_ux.period_label(days, token=period_token),
            rm=rm,
            vpn_rm=vpn_rm,
            top_refs=list(top),
            available_bonus_rub=available,
            withdraw_pending_count=int(wsum.get("pending_count", 0) or 0),
            withdraw_pending_rub=float(wsum.get("pending_rub", 0) or 0),
            cfg_referrer_days=int(settings.vpn_referral_referrer_days),
            cfg_friend_days=int(settings.vpn_referral_friend_days),
        )
        await _edit(text, admin_ux.ref_section_kb(period_token=period_token))
        await cb.answer()
        return

    if action == "withdraw":
        from bot.services import ref_withdraw_repo

        wsum = await ref_withdraw_repo.withdraw_status_summary(conn)
        text = admin_ux.format_withdraw_hub(summary=wsum)
        await _edit(text, admin_ux.withdraw_section_kb(period_token=period_token))
        await cb.answer()
        return

    if action == "withdraw_list" and len(parts) >= 3:
        from bot.services import ref_withdraw_repo

        st = (parts[2] or "pending").strip().lower()
        if st not in ("pending", "paid", "rejected"):
            st = "pending"
        rows = await ref_withdraw_repo.list_by_status(conn, status=st, limit=15)
        title = {"pending": "⏳ Заявки", "paid": "✅ Выплаченные", "rejected": "🚫 Отклонённые"}.get(
            st, st
        )
        lines = [f"{title}\n"]
        if not rows:
            lines.append("<i>пусто</i>")
        else:
            for r in rows:
                amt = float(r["amount_rub"] or 0)
                uid = int(r["user_id"])
                label = ref_withdraw_repo.format_withdraw_method_label(r)
                lines.append(
                    f"#{esc(r['id'])} user=<code>{esc(uid)}</code> "
                    f"<b>{esc(f'{amt:.2f}')} ₽</b> · {esc(label)}"
                )
        if st == "pending":
            lines.append(
                "\n<code>/admin_ref_withdraw paid ID</code>\n"
                "<code>/admin_ref_withdraw reject ID [причина]</code>"
            )
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="💳 К выводам",
                        callback_data=f"aux:withdraw:{period_token}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔙 К рефералам",
                        callback_data=f"aux:ref:{period_token}",
                    )
                ],
            ]
        )
        await _edit("\n".join(lines), kb)
        await cb.answer()
        return

    if action == "stats":
        days = admin_ux.days_from_token(period_token)
        days_arg: int | None = None if days is None else days
        agg = await admin_stats_repo.aggregate_dashboard(conn, days=days_arg)
        pay = None
        ret = None
        cross = None
        if settings.feature_split_metrics_enabled:
            pay = await admin_stats_repo.payment_funnel_metrics(conn, days=days_arg)
            ret = await admin_stats_repo.retention_metrics(conn, days=days_arg)
            cross = await admin_stats_repo.cross_sell_metrics(
                conn, days=days_arg, window_days=30
            )
        lines = [
            f"📊 <b>Статистика</b> · {esc(admin_ux.period_label(days, token=period_token))}",
            f"💰 Выручка: <b>{esc(f'{agg.revenue_rub:.2f}')} ₽</b>",
            f"🛒 Продаж: <b>{esc(str(agg.orders_count))}</b>",
            f"Средний чек (ARPPU): <b>{esc(f'{agg.arppu_rub:.2f}')} ₽</b>",
            f"🌐 Доля VPN в выручке: <b>{esc(f'{agg.vpn_revenue_share_pct:.1f}')}%</b>",
        ]
        if pay:
            lines.append(
                f"💳 Конверсия в оплату: <b>{esc(str(pay.get('funnel_paid_rate_pct', 0)))}%</b>"
            )
            lines.append(
                f"📦 Выдано после оплаты: <b>{esc(str(pay.get('funnel_completed_from_paid_pct', 0)))}%</b>"
            )
        if ret:
            lines.append(
                f"🔁 Возврат D7: <b>{esc(str(ret.get('retention_d7_pct', 0)))}%</b> · "
                f"D30: <b>{esc(str(ret.get('retention_d30_pct', 0)))}%</b>"
            )
        if cross:
            lines.append(
                f"🔀 Cross-sell Stars/Prem→VPN: "
                f"<b>{esc(str(cross.get('cross_sell_sp_to_vpn_pct', 0)))}%</b>"
            )
        lines.append("\nТех.детали — только в полном отчёте.")

        def _sl(token: str, base: str) -> str:
            return f"· {base} ·" if token == period_token else base

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_sl("today", "📅 Сегодня"), callback_data="aux:stats:today"
                    ),
                    InlineKeyboardButton(text=_sl("7", "7 дней"), callback_data="aux:stats:7"),
                ],
                [
                    InlineKeyboardButton(text=_sl("30", "30 дней"), callback_data="aux:stats:30"),
                    InlineKeyboardButton(text=_sl("all", "Всё"), callback_data="aux:stats:all"),
                ],
                [
                    InlineKeyboardButton(
                        text=_sl("start", "📈 С запуска"), callback_data="aux:stats:start"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="📊 Отчёт для руководителя", callback_data="ast:exec:7"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📋 Полный тех.отчёт",
                        callback_data=f"aux:legacy:{period_token}",
                    )
                ],
                [InlineKeyboardButton(text="🔙 Назад", callback_data=f"aux:d:{period_token}")],
            ]
        )
        await _edit("\n".join(lines), kb)
        await cb.answer()
        return

    if action == "promo":
        rows = await promo_repo.list_promos(conn, limit=20)
        active_n = sum(1 for r in rows if int(r["is_active"] or 0) == 1)
        preview: list[str] = []
        for r in rows[:6]:
            act = "✅" if int(r["is_active"] or 0) else "○"
            lim = r["max_activations"]
            lim_s = "∞" if lim is None else str(lim)
            preview.append(
                f"{act} <code>#{esc(r['id'])}</code> <b>{esc(r['code'])}</b> · "
                f"{esc(r['discount_type'])} {esc(r['discount_value'])} · "
                f"{esc(r['activation_count'])}/{esc(lim_s)}"
            )
        text = admin_ux.format_promo_hub(
            active_n=active_n, total_n=len(rows), preview_lines=preview
        )
        await _edit(text, admin_ux.promo_section_kb(period_token=period_token))
        await cb.answer()
        return

    if action == "promo_list":
        rows = await promo_repo.list_promos(conn, limit=25)
        lines = ["🎁 <b>Все промокоды</b>\n"]
        if not rows:
            lines.append("<i>пусто</i>")
        else:
            for r in rows:
                act = "✅" if int(r["is_active"] or 0) else "○"
                lim = r["max_activations"]
                lim_s = "∞" if lim is None else str(lim)
                lines.append(
                    f"{act} <code>#{esc(r['id'])}</code> <b>{esc(r['code'])}</b> · "
                    f"{esc(r['discount_type'])} {esc(r['discount_value'])} · "
                    f"{esc(r['scope'])} · {esc(r['activation_count'])}/{esc(lim_s)}"
                )
        lines.append(
            "\nВкл/выкл: <code>/admin_promo on ID</code> · <code>/admin_promo off ID</code>"
        )
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 К промо", callback_data=f"aux:promo:{period_token}"
                    )
                ]
            ]
        )
        await _edit("\n".join(lines), kb)
        await cb.answer()
        return

    if action == "contest":
        rows = await contest_repo.list_contests(conn, limit=15)
        active = await contest_repo.get_active_contest(conn)
        active_title = str(active["title"]) if active is not None else None
        preview_c: list[str] = []
        for r in rows[:6]:
            on = "✅" if int(r["is_active"] or 0) else "○"
            preview_c.append(
                f"{on} <code>#{esc(r['id'])}</code> {esc(str(r['title'] or '')[:40])}"
            )
        text = admin_ux.format_contest_hub(
            active_title=active_title, total_n=len(rows), preview_lines=preview_c
        )
        await _edit(text, admin_ux.contest_section_kb(period_token=period_token))
        await cb.answer()
        return

    if action == "contest_list":
        rows = await contest_repo.list_contests(conn, limit=20)
        lines = ["🏆 <b>Конкурсы</b>\n"]
        if not rows:
            lines.append("<i>пусто</i>")
        else:
            for r in rows:
                on = "✅" if int(r["is_active"] or 0) else "○"
                lines.append(
                    f"{on} <code>#{esc(r['id'])}</code> <b>{esc(str(r['title'] or ''))}</b>\n"
                    f"   {esc(str(r['starts_at'] or ''))} → {esc(str(r['ends_at'] or ''))}"
                )
        lines.append(
            "\n<code>/contest activate ID</code> · <code>/contest deactivate_all</code>"
        )
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 К конкурсам",
                        callback_data=f"aux:contest:{period_token}",
                    )
                ]
            ]
        )
        await _edit("\n".join(lines), kb)
        await cb.answer()
        return

    if action == "mkt":
        days = admin_ux.days_from_token(period_token)
        days_arg: int | None = None if days is None else days
        acq = None
        if settings.feature_split_metrics_enabled:
            acq = await admin_stats_repo.acquisition_metrics(conn, days=days_arg)
        text = admin_ux.format_mkt_hub(
            acq=acq,
            period_label_s=admin_ux.period_label(days, token=period_token),
        )
        await _edit(text, admin_ux.mkt_section_kb(period_token=period_token))
        await cb.answer()
        return

    if action == "export":
        await _edit(
            admin_ux.format_export_hub(),
            admin_ux.export_section_kb(period_token=period_token),
        )
        await cb.answer()
        return

    if action == "export_run" and len(parts) >= 3:
        arg = parts[2]
        if arg == "all":
            days_ex: int | None = None
        else:
            try:
                days_ex = int(arg)
            except ValueError:
                days_ex = 30
        data = await admin_stats_repo.export_completed_csv(conn, days=days_ex)
        tag = "all" if days_ex is None else f"{days_ex}d"
        await cb.message.answer_document(
            BufferedInputFile(data, filename=f"orders_completed_{tag}.csv"),
            caption=f"Выданные заказы ({admin_ux.period_label(days_ex)})",
        )
        await cb.answer("CSV отправлен")
        return

    if action == "sys":
        await _edit(
            admin_ux.format_sys_hub(),
            admin_ux.sys_section_kb(period_token=period_token),
        )
        await cb.answer()
        return

    if action == "settings":
        await _edit(
            admin_ux.format_settings_hub(),
            admin_ux.settings_section_kb(period_token=period_token),
        )
        await cb.answer()
        return

    if action == "attention":
        await _edit(
            admin_ux.format_attention_hub(),
            admin_ux.attention_section_kb(period_token=period_token),
        )
        await cb.answer()
        return

    if action == "pending":
        days = admin_ux.days_from_token(period_token)
        days_arg: int | None = None if days is None else days
        rows = await admin_stats_repo.list_pending_fulfillment_orders(
            conn, days=days_arg, limit=25, product_kind=product_kind
        )
        metrics = await admin_stats_repo.pending_fulfillment_metrics(
            conn, days=days_arg, product_kind=product_kind
        )
        text = admin_ux.format_pending_fulfillment_list(
            rows,
            period_label_s=(
                f"{admin_ux.period_label(days, token=period_token)}"
                f" · {admin_ux.kind_label(product_kind)}"
            ),
            total_rub=float(metrics.get("pending_fulfill_rub", 0) or 0),
        )
        order_ids = [int(r["id"]) for r in rows]
        await _edit(
            text,
            admin_ux.orders_list_kb(
                order_ids,
                period_token=period_token,
                back_callback=admin_ux.aux_cb("finance", period_token, kind_token),
            ),
        )
        await cb.answer()
        return

    if action == "expired_vpn":
        vpn_cp_path = settings.resolved_vpn_db_path()
        rows = await admin_stats_repo.list_paid_expired_vpn_accounts(
            vpn_cp_path, limit=25
        )
        text = admin_ux.format_expired_vpn_list(rows)
        tids = [int(r["telegram_user_id"]) for r in rows if int(r.get("telegram_user_id") or 0)]
        await _edit(
            text,
            admin_ux.expired_vpn_list_kb(tids, period_token=period_token),
        )
        await cb.answer()
        return

    if action in ("cmdrun", "cmdhint") and len(parts) >= 3:
        cmd = parts[2].strip()
        proxy = _AdminCbMessage(cb.message, cb.from_user)

        if cmd == "admin_recalc_profit":
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="♻️ VPN",
                            callback_data="aux:cmdexec:admin_recalc_profit:vpn",
                        ),
                        InlineKeyboardButton(
                            text="♻️ Stars",
                            callback_data="aux:cmdexec:admin_recalc_profit:stars",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="♻️ Premium",
                            callback_data="aux:cmdexec:admin_recalc_profit:premium",
                        ),
                        InlineKeyboardButton(
                            text="♻️ Все",
                            callback_data="aux:cmdexec:admin_recalc_profit:all",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="📦 Один заказ…",
                            callback_data="aux:cmdask:admin_recalc_profit",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="🔙 Назад",
                            callback_data=f"aux:finance:{period_token}",
                        )
                    ],
                ]
            )
            await _edit(
                "♻️ <b>Пересчёт прибыли</b>\n"
                "Только <code>completed</code>. Выберите товар:",
                kb,
            )
            await cb.answer()
            return

        if cmd == "admin_vpn_finalize":
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔧 stuck",
                            callback_data="aux:cmdexec:admin_vpn_finalize:stuck",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="📦 По order_id…",
                            callback_data="aux:cmdask:admin_vpn_finalize",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="🔙 Назад",
                            callback_data=f"aux:vpn:{period_token}",
                        )
                    ],
                ]
            )
            await _edit("🔧 <b>VPN finalize</b>\nВыберите:", kb)
            await cb.answer()
            return

        if cmd in _CMDRUN_INSTANT:
            await cb.answer("Запускаю…")
            await _invoke_admin_command(
                proxy=proxy,
                settings=settings,
                conn=conn,
                state=state,
                cmd=cmd,
                args=_CMDRUN_INSTANT[cmd],
            )
            return

        if cmd in _CMDRUN_ASK:
            await cb.answer()
            if cmd == "admin_fin_set":
                await _invoke_admin_command(
                    proxy=proxy,
                    settings=settings,
                    conn=conn,
                    state=state,
                    cmd="admin_fin_show",
                    args=None,
                )
            await state.set_state(AdminCmdStates.waiting_args)
            await state.update_data(admin_cmd=cmd, period_token=period_token)
            await proxy.answer(_CMDRUN_ASK[cmd][1])
            return

        await cb.answer("Неизвестная команда", show_alert=True)
        return

    if action == "cmdexec" and len(parts) >= 4:
        cmd = parts[2].strip()
        args = ":".join(parts[3:]).strip()
        proxy = _AdminCbMessage(cb.message, cb.from_user)
        await cb.answer("Запускаю…")
        await _invoke_admin_command(
            proxy=proxy,
            settings=settings,
            conn=conn,
            state=state,
            cmd=cmd,
            args=args,
        )
        return

    if action == "cmdask" and len(parts) >= 3:
        cmd = parts[2].strip()
        if cmd not in _CMDRUN_ASK:
            await cb.answer("Нет формы ввода", show_alert=True)
            return
        await state.set_state(AdminCmdStates.waiting_args)
        await state.update_data(admin_cmd=cmd, period_token=period_token)
        await cb.answer()
        await cb.message.answer(_CMDRUN_ASK[cmd][1])
        return

    await cb.answer("Неизвестно", show_alert=False)



@router.message(Command("cancel"), AdminCmdStates.waiting_args)
async def admin_cmd_cancel(message: Message, settings: Settings, state: FSMContext) -> None:
    if not await _require_admin_message(message, settings):
        return
    await state.clear()
    await message.answer("Отменено.")


@router.message(AdminCmdStates.waiting_args, F.text)
async def admin_cmd_args_received(
    message: Message, settings: Settings, conn, state: FSMContext
) -> None:
    if not await _require_admin_message(message, settings):
        return
    data = await state.get_data()
    cmd = str(data.get("admin_cmd") or "").strip()
    raw = (message.text or "").strip()
    if not cmd:
        await state.clear()
        await message.answer("Сессия сброшена. Откройте /admin снова.")
        return
    if raw.lower() in ("/cancel", "cancel", "отмена"):
        await state.clear()
        await message.answer("Отменено.")
        return
    await state.clear()
    proxy = _AdminCbMessage(message, message.from_user)
    await _invoke_admin_command(
        proxy=proxy,
        settings=settings,
        conn=conn,
        state=state,
        cmd=cmd,
        args=raw,
    )


@router.message(Command("admin_help", "ah"))
async def cmd_admin_help(message: Message, settings: Settings) -> None:
    if not await _require_admin_message(message, settings):
        return
    await message.answer(admin_help_hub_html(), reply_markup=admin_help_hub_kb())


@router.callback_query(F.data.startswith("ahelp:"))
async def admin_help_callbacks(cb: CallbackQuery, settings: Settings, conn) -> None:
    if not _is_admin(cb.from_user.id, settings):
        await cb.answer("Нет доступа", show_alert=True)
        return
    data = (cb.data or "").strip()
    if data == "ahelp:hub":
        await cb.message.edit_text(admin_help_hub_html(), reply_markup=admin_help_hub_kb())
        await cb.answer()
        return
    if data == "ahelp:open_admin":
        await cb.answer()
        # Запускаем дашборд сразу, без просьбы вручную слать /admin
        text, kb = await _build_business_admin_message(
            conn, settings, days=7, period_token="7"
        )
        await cb.message.answer(text, reply_markup=kb)
        return
    if data.startswith("ahelp:cat:"):
        key = data.split(":", 2)[-1]
        sec = section_by_key(key)
        if sec is None:
            await cb.answer("Раздел не найден", show_alert=True)
            return
        await cb.message.edit_text(
            admin_help_section_html(sec),
            reply_markup=admin_help_section_kb(),
        )
        await cb.answer()
        return
    await cb.answer()


@router.callback_query(F.data.startswith("ast:"))
async def admin_stats_callbacks(cb: CallbackQuery, settings: Settings, conn) -> None:
    if not _is_admin(cb.from_user.id, settings):
        await cb.answer("Нет доступа", show_alert=True)
        return
    if cb.data == "ast:deliveries":
        rows = await orders_repo.list_recent_completed_orders(conn, limit=15)
        if not rows:
            await cb.message.answer("<b>Последние выдачи</b>\n\nПока нет выданных заказов.")
        else:
            lines = ["<b>Последние выдачи</b> (15 заказов)\n"]
            for r in rows:
                oid = int(r["id"])
                title = esc(str(r["product_title"] or ""))[:50]
                rcpt = esc(str(r["user_note"] or "")[:36])
                when = esc(str(r["fulfillment_applied_at"] or r["updated_at"] or "")[:19])
                amt = float(r["rub_after_discounts"] or 0)
                lines.append(
                    f"#{esc(str(oid))} · {title}\n"
                    f"  {esc(f'{amt:.2f}')} ₽ → <code>{rcpt}</code> · <i>{when}</i>\n"
                )
            await cb.message.answer("\n".join(lines))
        await cb.answer()
        return
    if cb.data == "ast:vpn_health":
        await cb.answer("Собираю…")
        from bot.services.vpn_ops_health import collect_vpn_ops_health

        snap = await collect_vpn_ops_health(settings)
        text = snap.summary_html()
        if len(text) > 4000:
            text = text[:3900] + "\n…\n<i>обрезано</i>"
        await cb.message.answer(text)
        return
    if cb.data == "ast:vpn_zombies":
        await cb.answer("Собираю…")
        from bot.services.vpn_bridge_zombie_metrics import (
            collect_bridge_zombie_metrics,
            format_bridge_zombies_html,
        )

        path = (settings.vpn_bridge_peers_status_path or "").strip() or None
        max_age = int(settings.vpn_bridge_status_max_age_sec or 10800)
        m = collect_bridge_zombie_metrics(path, max_age_sec=max_age)
        text = format_bridge_zombies_html(m)
        if len(text) > 4000:
            text = text[:3900] + "\n…\n<i>обрезано</i>"
        await cb.message.answer(text)
        return
    parts = cb.data.split(":")
    if len(parts) < 3:
        await cb.answer()
        return
    _, kind, arg = parts[0], parts[1], parts[2]
    try:
        if kind == "d":
            days = _period_arg_to_days(arg)
            agg = await admin_stats_repo.aggregate_dashboard(conn, days=days)
            top = await admin_stats_repo.top_referrers(conn, days=days, limit=3)
            rm = await admin_stats_repo.referral_metrics(conn, days=days)
            funnel = await admin_stats_repo.funnel_metrics(conn, days=days)
            pay_funnel = (
                await admin_stats_repo.payment_funnel_metrics(conn, days=days)
                if settings.feature_split_metrics_enabled
                else None
            )
            webhook_sla = (
                await admin_stats_repo.webhook_sla_metrics(conn, days=days)
                if settings.feature_split_metrics_enabled
                else None
            )
            cross_sell = (
                await admin_stats_repo.cross_sell_metrics(conn, days=days, window_days=30)
                if settings.feature_split_metrics_enabled
                else None
            )
            retention = (
                await admin_stats_repo.retention_metrics(conn, days=days)
                if settings.feature_split_metrics_enabled
                else None
            )
            acquisition = (
                await admin_stats_repo.acquisition_metrics(conn, days=days)
                if settings.feature_split_metrics_enabled
                else None
            )
            feedback = await admin_stats_repo.feedback_metrics(conn, days=days)
            vpn_rm, vpn_cp, vpn_h = await _vpn_admin_dashboard_extras(conn, settings, days=days)
            top_prof = await admin_stats_repo.top_products_by_profit(conn, days=days, limit=5)
            tlines = ["\n<b>Топ товаров по прибыли</b>\n"]
            if not top_prof:
                tlines.append("<i>нет</i>")
            else:
                for r in top_prof:
                    netp_v = float(r["netp"] or 0)
                    n_v = int(r["n"] or 0)
                    tlines.append(
                        f"· {esc(str(r['product_title'] or '')[:40])} — "
                        f"<b>{esc(f'{netp_v:.2f}')} ₽</b> ({esc(str(n_v))} шт.)"
                    )
            text = (
                _format_dashboard_html(
                    period_label=_period_human(days),
                    agg=agg,
                    top_refs=top,
                    rm=rm,
                    funnel=funnel,
                    pay_funnel=pay_funnel,
                    webhook_sla=webhook_sla,
                    cross_sell=cross_sell,
                    retention=retention,
                    acquisition=acquisition,
                    feedback=feedback if settings.feature_feedback_metrics_enabled else None,
                    vpn_rm=vpn_rm,
                    vpn_cp=vpn_cp,
                    vpn_health_html=vpn_h,
                )
                + "\n".join(tlines)
            )
            await cb.message.edit_text(text, reply_markup=_admin_stats_main_kb())
            await cb.answer()
            return
        if kind == "sales":
            days = int(arg) if arg.isdigit() else 7
            rep = await _build_sales_report_html(conn, days=days)
            await cb.message.edit_text(rep + "\n\n<i>Назад: выберите период дашборда.</i>", reply_markup=_admin_stats_main_kb())
            await cb.answer()
            return
        if kind == "top":
            days = int(arg) if arg.isdigit() else 30
            rows = await admin_stats_repo.top_products_by_profit(conn, days=days, limit=12)
            lines = [f"<b>Топ по чистой прибыли</b> ({esc(_period_human(days))})\n"]
            if not rows:
                lines.append("<i>нет данных</i>")
            else:
                for i, r in enumerate(rows, start=1):
                    netp_v = float(r["netp"] or 0)
                    n_v = int(r["n"] or 0)
                    lines.append(
                        f"{i}. {esc(str(r['product_title'] or '')[:44])}\n"
                        f"   прибыль <b>{esc(f'{netp_v:.2f}')} ₽</b> · "
                        f"{esc(str(n_v))} шт."
                    )
            await cb.message.edit_text("\n".join(lines), reply_markup=_admin_stats_main_kb())
            await cb.answer()
            return
        if kind == "dyn":
            d = int(arg) if arg.isdigit() else 14
            txt = await _build_dyn_html(conn, days=max(1, min(90, d)))
            await cb.message.edit_text(txt, reply_markup=_admin_stats_main_kb())
            await cb.answer()
            return
        if kind == "chart":
            days_c = int(arg) if arg.isdigit() else 30
            days_c = max(7, min(120, days_c))
            daily = await admin_stats_repo.sales_by_day(conn, days=days_c)
            weekly = await admin_stats_repo.sales_by_week(conn, days=max(56, days_c))
            png = admin_charts.sales_trend_charts_png(
                daily_rows=list(daily),
                weekly_rows=list(weekly),
                title_suffix=f"{days_c} дн.",
            )
            if png:
                await cb.message.answer_photo(
                    BufferedInputFile(png, filename="sales_trend.png"),
                    caption=f"Выручка (оплачено): по дням и по неделям · окно {days_c} дн.",
                )
                await cb.answer("График отправлен")
            else:
                await cb.answer("Matplotlib недоступен на сервере", show_alert=True)
            return
        if kind == "week":
            wk = int(arg) if arg.isdigit() else 12
            txt = await _build_week_html(conn, weeks=wk)
            await cb.message.edit_text(txt + "\n\n<i>PNG: кнопка «График».</i>", reply_markup=_admin_stats_main_kb())
            await cb.answer()
            return
        if kind == "csv":
            if arg in ("all", "full"):
                days = None
            else:
                days = int(arg) if arg.isdigit() else 30
            raw = await admin_stats_repo.export_completed_csv(conn, days=days)
            tag = "all" if days is None else f"{days}d"
            await cb.message.answer_document(
                BufferedInputFile(raw, filename=f"orders_completed_{tag}.csv"),
                caption=f"Выданные заказы ({esc(_period_human(days))})",
            )
            await cb.answer("Файл отправлен")
            return
        if kind == "exec":
            short_days = int(arg) if arg.isdigit() else 7
            short_days = max(1, min(90, short_days))
            long_days = max(short_days, 30)
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
                conn, settings.resolved_vpn_db_path(), exclude_user_ids=excl
            )
            mix_kw = {"days": short_days, **kw}
            vpn_summary = await admin_stats_repo.product_sales_summary(conn, kind="vpn", **mix_kw)
            vpn_mix = await admin_stats_repo.vpn_by_term(conn, **mix_kw)
            stars_summary = await admin_stats_repo.product_sales_summary(conn, kind="stars", **mix_kw)
            stars_mix = await admin_stats_repo.stars_by_package(conn, **mix_kw)
            premium_summary = await admin_stats_repo.product_sales_summary(
                conn, kind="premium", **mix_kw
            )
            premium_mix = await admin_stats_repo.premium_by_term(conn, **mix_kw)
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
                active_paid_vpn=active_vpn,
                vpn_summary=vpn_summary,
                vpn_mix=vpn_mix,
                stars_summary=stars_summary,
                stars_mix=stars_mix,
                premium_summary=premium_summary,
                premium_mix=premium_mix,
            )
            await cb.message.edit_text(text, reply_markup=_admin_stats_main_kb())
            await cb.answer()
            return
    except Exception:
        await cb.answer("Ошибка", show_alert=True)
        raise
    await cb.answer()


@router.message(Command("admin_ref_partner"))
async def cmd_admin_ref_partner(
    message: Message, command: CommandObject, settings: Settings, conn
) -> None:
    """/admin_ref_partner USER_ID [PCT|off] — статус партнёра и override % (до 30)."""
    if not await _require_admin_message(message, settings):
        return
    parts = (command.args or "").split()
    if not parts:
        await message.answer(
            "Пример:\n"
            "<code>/admin_ref_partner 123456789 25</code> — партнёр, 25%\n"
            "<code>/admin_ref_partner 123456789 off</code> — сброс на базовый 15%"
        )
        return
    try:
        uid = int(parts[0])
    except ValueError:
        await message.answer("USER_ID должен быть числом.")
        return
    await users_repo.upsert_user(conn, user_id=uid, username=None, first_name=None)
    if len(parts) == 1:
        row = await users_repo.get_user(conn, uid)
        st = "basic"
        ov = None
        if row is not None:
            try:
                st = str(row["ref_partner_status"] or "basic")
                ov = row["ref_commission_override_pct"]
            except (KeyError, IndexError):
                pass
        await message.answer(
            f"user <code>{uid}</code>\nstatus=<code>{esc(st)}</code>\noverride=<code>{esc(str(ov))}</code>"
        )
        return
    arg = parts[1].strip().lower()
    if arg in ("off", "basic", "reset", "0"):
        await conn.execute(
            """
            UPDATE users
            SET ref_partner_status = 'basic', ref_commission_override_pct = NULL
            WHERE user_id = ?
            """,
            (uid,),
        )
        await conn.commit()
        await message.answer(f"✅ user <code>{uid}</code> → basic (глобальный %)")
        return
    try:
        pct = float(arg.replace(",", "."))
    except ValueError:
        await message.answer("PCT — число, например 20 / 25 / 30")
        return
    if pct < 15 or pct > 30:
        await message.answer("Допустимо 15…30 %")
        return
    await conn.execute(
        """
        UPDATE users
        SET ref_partner_status = 'partner', ref_commission_override_pct = ?
        WHERE user_id = ?
        """,
        (pct, uid),
    )
    await conn.commit()
    await message.answer(f"✅ user <code>{uid}</code> → partner, override <b>{pct:.0f}%</b>")


@router.message(Command("admin_ref_withdraw"))
async def cmd_admin_ref_withdraw(
    message: Message, command: CommandObject, settings: Settings, conn
) -> None:
    """/admin_ref_withdraw list | paid ID | reject ID [причина…]"""
    if not await _require_admin_message(message, settings):
        return
    from bot.services import balance_repo, ref_withdraw_repo
    from bot.services.referral_partner import (
        count_qualified_vpn_referrals,
        level_for_qualified_count,
        user_has_own_paid_vpn_min_days,
    )

    parts = (command.args or "").split()
    if not parts or parts[0].lower() == "list":
        rows = await ref_withdraw_repo.list_pending(conn, limit=20)
        if not rows:
            await message.answer("Нет pending-заявок на вывод.")
            return
        lines = ["<b>Заявки на вывод (pending)</b>\n"]
        for r in rows:
            amt = float(r["amount_rub"] or 0)
            uid = int(r["user_id"])
            label = ref_withdraw_repo.format_withdraw_method_label(r)
            target = ""
            try:
                target = str(r["payout_target"] or "").strip()
            except (KeyError, IndexError, TypeError):
                target = str(r["details"] or "").strip()
            target_s = f" · <code>{esc(target)}</code>" if target else ""
            qn = await count_qualified_vpn_referrals(conn, uid)
            lvl = level_for_qualified_count(qn)
            own = await user_has_own_paid_vpn_min_days(conn, uid)
            own_mark = "✅" if own else "❌"
            lines.append(
                f"#{esc(r['id'])} user=<code>{esc(uid)}</code> "
                f"<b>{esc(f'{amt:.2f}')} ₽</b> · {esc(label)}{target_s}\n"
                f"   🏆 {esc(str(lvl['label']))} · VPN≥30д друзей: <b>{qn}</b> · "
                f"свой VPN≥30д: {own_mark} · {esc(r['created_at'])}"
            )
        lines.append(
            "\n<code>/admin_ref_withdraw paid ID</code> — списать бонус и закрыть "
            "(карту/крипту переведите вручную)\n"
            "<code>/admin_ref_withdraw reject ID [причина]</code>"
        )
        await message.answer("\n".join(lines))
        return
    action = parts[0].lower()
    if action not in ("paid", "reject") or len(parts) < 2:
        await message.answer(
            "Пример: <code>/admin_ref_withdraw paid 12</code>\n"
            "<code>/admin_ref_withdraw reject 12 причина</code>"
        )
        return
    try:
        rid = int(parts[1])
    except ValueError:
        await message.answer("ID заявки — число.")
        return
    row = await ref_withdraw_repo.get_withdraw(conn, rid)
    if row is None:
        await message.answer("Заявка не найдена.")
        return
    if str(row["status"]) != "pending":
        await message.answer(f"Статус уже <code>{esc(row['status'])}</code>")
        return
    uid = int(row["user_id"])
    amount = float(row["amount_rub"] or 0)
    if action == "reject":
        reason = " ".join(parts[2:]).strip()[:500] if len(parts) > 2 else ""
        await ref_withdraw_repo.set_withdraw_status(
            conn, request_id=rid, status="rejected", admin_note=reason or "rejected_by_admin"
        )
        qn = await count_qualified_vpn_referrals(conn, uid)
        lvl = level_for_qualified_count(qn)
        reason_line = f"\nПричина: {esc(reason)}" if reason else ""
        await message.answer(
            f"Заявка #{rid} отклонена (user <code>{uid}</code>, "
            f"уровень {esc(str(lvl['label']))}, VPN≥30д друзей: {qn})."
            f"{reason_line}"
        )
        return
    # paid: debit current bonus up to request amount (or available)
    await conn.execute("BEGIN IMMEDIATE")
    try:
        bal = await balance_repo.get_ref_balance(conn, uid)
        debit = round(min(bal, amount), 2)
        if debit < 0.01:
            await conn.rollback()
            await message.answer("На реферальном балансе нет средств — сначала reject или проверьте.")
            return
        await balance_repo.debit_bonus_in_txn(
            conn,
            user_id=uid,
            amount=debit,
            kind="bonus_withdraw",
            ref_type="ref_withdraw",
            ref_id=rid,
        )
        method_label = ref_withdraw_repo.format_withdraw_method_label(row)
        target = ""
        try:
            target = str(row["payout_target"] or "").strip()
        except (KeyError, IndexError, TypeError):
            target = str(row["details"] or "").strip()
        await conn.execute(
            """
            UPDATE ref_withdraw_requests
            SET status = 'paid', amount_rub = ?, admin_note = ?, updated_at = datetime('now')
            WHERE id = ? AND status = 'pending'
            """,
            (debit, f"paid_by_admin debit={debit} method={method_label}", rid),
        )
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise
    await message.answer(
        f"✅ Заявка #{rid}: списано <b>{debit:.2f} ₽</b> с бонуса user <code>{uid}</code>.\n"
        f"Способ: <b>{esc(method_label)}</b>"
        + (f"\nРеквизиты: <code>{esc(target)}</code>" if target else "")
        + "\nПереведите вручную (карта / USDT / CryptoBot)."
    )


@router.message(Command("admin_export"))
async def cmd_admin_export(message: Message, command: CommandObject, settings: Settings, conn) -> None:
    if not await _require_admin_message(message, settings):
        return
    raw = (command.args or "").strip().lower()
    if raw in ("", "all", "*", "full"):
        days = None
    else:
        try:
            days = int(raw)
        except ValueError:
            await message.answer("Пример: <code>/admin_export 30</code> или <code>/admin_export all</code>")
            return
    data = await admin_stats_repo.export_completed_csv(conn, days=days)
    tag = "all" if days is None else f"{days}d"
    await message.answer_document(
        BufferedInputFile(data, filename=f"orders_completed_{tag}.csv"),
        caption=f"Выданные заказы ({_period_human(days)})",
    )


@router.message(Command("admin_cogs"))
async def cmd_admin_cogs(message: Message, command: CommandObject, settings: Settings, conn) -> None:
    if not await _require_admin_message(message, settings):
        return
    if not settings.is_super_admin(message.from_user.id):
        await message.answer("Только супер-админ может править себестоимость.")
        return
    parts = (command.args or "").split()
    if len(parts) != 2:
        await message.answer(
            "Укажите: <code>/admin_cogs ORDER_ID COGS_RUB</code>\n"
            "Пересчитает чистую прибыль для заказа в статусе <code>completed</code>."
        )
        return
    try:
        oid = int(parts[0])
        amt = float(parts[1].replace(",", "."))
    except ValueError:
        await message.answer("Некорректные числа.")
        return
    ok = await orders_repo.set_manual_cogs_and_recalc(conn, oid, settings, manual_cogs_rub=amt)
    await message.answer("Обновлено." if ok else "Заказ не найден или не выдан (completed).")


@router.message(Command("admin_fin_show"))
async def cmd_admin_fin_show(message: Message, settings: Settings, conn) -> None:
    from bot.services import fin_settings_repo

    if not await _require_admin_message(message, settings):
        return
    ov = await fin_settings_repo.get_all(conn)
    fin_s = fin_settings_repo.apply_overrides(settings, ov)
    prem1 = float(getattr(fin_s, "fragment_premium_1m_usdt", 0) or 0)
    prem1_s = "не задано (TBD)" if prem1 <= 0.000001 else f"{prem1:g} USDT"
    lines = [
        "⚙️ <b>FIN настройки</b> (env + ✎ override)",
        f"🏦 Lava/card: <b>{float(fin_s.fee_lava_card_percent):g}%</b>",
        f"📲 СБП: <b>{float(fin_s.fee_sbp_percent):g}%</b>",
        f"🪙 Crypto: <b>{float(fin_s.fee_crypto_bot_percent):g}%</b>",
        f"🪙 Xrocket: <b>{float(fin_s.fee_xrocket_percent):g}%</b>",
        f"⭐ 1★: <b>{float(fin_s.fragment_star_usdt):g}</b> USDT",
        f"💎 1м: <b>{esc(prem1_s)}</b>",
        f"💎 3/6/12м: <b>{float(fin_s.fragment_premium_3m_usdt):g}</b> / "
        f"<b>{float(fin_s.fragment_premium_6m_usdt):g}</b> / "
        f"<b>{float(fin_s.fragment_premium_12m_usdt):g}</b>",
    ]
    if ov:
        lines.append("✎ overrides: " + ", ".join(f"{k}={v:g}" for k, v in sorted(ov.items())))
    else:
        lines.append("<i>overrides нет — только env</i>")
    lines.append(fin_settings_repo.format_keys_help())
    await message.answer("\n".join(lines))


@router.message(Command("admin_fin_set"))
async def cmd_admin_fin_set(message: Message, command: CommandObject, settings: Settings, conn) -> None:
    from bot.services import fin_settings_repo

    if not await _require_admin_message(message, settings):
        return
    if not settings.is_super_admin(message.from_user.id):
        await message.answer("Только супер-админ.")
        return
    parts = (command.args or "").split()
    if len(parts) < 2:
        await message.answer(
            "Укажите: <code>/admin_fin_set KEY VALUE</code>\n" + fin_settings_repo.format_keys_help()
        )
        return
    key_raw, val_raw = parts[0], parts[1]
    try:
        if val_raw.strip().lower() in ("clear", "reset", "env", "-"):
            canon = await fin_settings_repo.clear_key(conn, key_raw)
            if not canon:
                await message.answer("Неизвестный ключ.\n" + fin_settings_repo.format_keys_help())
                return
            await message.answer(f"Сброшен override <code>{esc(canon)}</code> → env.")
            return
        val = float(val_raw.replace(",", "."))
        if val < 0:
            raise ValueError("neg")
        canon = await fin_settings_repo.set_value(
            conn, key_raw, val, updated_by=int(message.from_user.id)
        )
    except ValueError:
        await message.answer(
            "Некорректный ключ или число.\n" + fin_settings_repo.format_keys_help()
        )
        return
    note = ""
    if canon == "fragment_1m" and val <= 0.000001:
        note = "\n⚠️ Premium 1м = 0 → в UI «не задано (TBD)»."
    await message.answer(
        f"OK: <code>{esc(canon)}</code> = <b>{esc(f'{val:g}')}</b>. "
        f"Только для <b>новых</b> заказов (старые snapshot не трогаем).{note}"
    )

@router.message(Command("admin_recalc_profit"))
async def cmd_admin_recalc_profit(message: Message, command: CommandObject, settings: Settings, conn) -> None:
    if not await _require_admin_message(message, settings):
        return
    if not settings.is_super_admin(message.from_user.id):
        await message.answer("Только супер-админ.")
        return
    arg = (command.args or "").strip().lower()
    if arg in ("vpn", "stars", "premium"):
        n = await orders_repo.recalc_completed_profit_snapshots(
            conn, settings, product_kind=arg
        )
        await message.answer(
            f"Пересчитано <b>{esc(arg)}</b>: <b>{esc(str(n))}</b> completed."
        )
        return
    if arg in ("all", "*"):
        n = await orders_repo.recalc_completed_profit_snapshots(conn, settings)
        await message.answer(f"Пересчитано все completed: <b>{esc(str(n))}</b>.")
        return
    if not arg.isdigit():
        await message.answer(
            "Укажите: <code>/admin_recalc_profit ORDER_ID</code> или "
            "<code>vpn</code> / <code>stars</code> / <code>premium</code> / <code>all</code>"
        )
        return
    n = await orders_repo.recalc_completed_profit_snapshots(conn, settings, order_id=int(arg))
    await message.answer("Пересчитано." if n else "Заказ не найден или не completed.")


@router.message(Command("channel_checkout_pin"))
async def cmd_channel_checkout_pin(message: Message, settings: Settings) -> None:
    """HTML для закрепля в канале: чеклист оплаты по ссылке bc (копировать / переслать в канал)."""
    if not await _require_admin_message(message, settings):
        return
    await message.answer(marketing.channel_pin_bc_checkout_html(settings), disable_web_page_preview=True)


@router.message(Command("admqueue"))
async def cmd_admqueue(message: Message, settings: Settings, conn) -> None:
    """Список заказов для ручного внимания: paid с ошибкой выдачи или долго processing (гибрид G+)."""
    if not await _require_admin_message(message, settings):
        return
    idle = max(1, int(settings.operator_queue_processing_idle_minutes))
    rows = await orders_repo.list_orders_operator_attention_queue(
        conn, processing_idle_minutes=idle, limit=25
    )
    if not rows:
        await message.answer(
            "<b>Очередь внимания</b>\n\n"
            "Нет заказов в статусе «оплачен с ошибкой выдачи» или «в работе» дольше "
            f"<code>{idle}</code> мин. без обновления."
        )
        return
    lines = [
        "<b>Очередь внимания</b> (до 25 заказов)\n",
        f"<i>processing без движения: &gt; {esc(str(idle))} мин.</i>\n",
    ]
    for r in rows:
        oid = int(r["id"])
        st = esc(str(r["status"] or ""))
        title = esc(str(r["product_title"] or ""))[:60]
        err_raw = str(r["fulfillment_last_error"] or "").strip()
        err = esc(err_raw[:120]) if err_raw else " - "
        note = esc(str(r["user_note"] or "")[:40])
        lines.append(
            f"#{esc(str(oid))} <code>{st}</code> {title}\n"
            f"  получ.: <code>{note}</code>\n"
            f"  err: <code>{err}</code>\n"
        )
    lines.append(
        "\n<i>Откройте карточку из уведомления о заказе или найдите номер в админ-чате; "
        "кнопки статусов - там же.</i>"
    )
    await message.answer("\n".join(lines))


@router.message(Command("admdeliveries"))
async def cmd_adm_deliveries(message: Message, settings: Settings, conn) -> None:
    if not await _require_admin_message(message, settings):
        return
    rows = await orders_repo.list_recent_completed_orders(conn, limit=15)
    if not rows:
        await message.answer("<b>Последние выдачи</b>\n\nПока нет выданных заказов.")
        return
    lines = ["<b>Последние выдачи</b> (15 заказов)\n"]
    for r in rows:
        oid = int(r["id"])
        title = esc(str(r["product_title"] or ""))[:50]
        rcpt = esc(str(r["user_note"] or "")[:36])
        when = esc(str(r["fulfillment_applied_at"] or r["updated_at"] or "")[:19])
        amt = float(r["rub_after_discounts"] or 0)
        lines.append(
            f"#{esc(str(oid))} · {title}\n"
            f"  {esc(f'{amt:.2f}')} ₽ → <code>{rcpt}</code> · <i>{when}</i>\n"
        )
    await message.answer("\n".join(lines))


def _parse_admin_vpn_paid_until(raw: str) -> str | None:
    s = (raw or "").strip().replace("Z", "+00:00")
    if len(s) < 10:
        return None
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


@router.message(Command("admin_find_nick", "find_nick"))
async def cmd_admin_find_nick(message: Message, command: CommandObject, settings: Settings, conn) -> None:
    """Поиск аккаунта/заказов по нику сайта."""
    if not await _require_admin_message(message, settings):
        return
    from bot.services import accounts_repo
    from bot.util_html import esc

    nick = (command.args or "").strip()
    if len(nick) < 2:
        await message.answer(
            "Пример: <code>/admin_find_nick familyHero2024</code>\n"
            "или <code>/find_nick familyHero2024</code>"
        )
        return
    data = await accounts_repo.find_accounts_orders_by_nickname(conn, nick, limit=15)
    acc = data.get("account")
    orders = data.get("orders") or []
    lines = [f"<b>Поиск ника</b> <code>{esc(nick)}</code>"]
    if acc:
        lines.append(
            f"Аккаунт: <code>{esc(str(acc.get('account_id')))}</code>\n"
            f"vpn_subject: <code>{esc(str(acc.get('vpn_subject_id')))}</code>\n"
            f"TG: <code>{esc(str(acc.get('telegram_user_id') or '—'))}</code>\n"
            f"ник: <b>@{esc(str(acc.get('nickname') or ''))}</b>"
        )
    else:
        lines.append("Аккаунт с таким ником не найден (ищем ещё по buyer_nickname в заказах).")
    if orders:
        lines.append("<b>Заказы:</b>")
        for o in orders[:12]:
            bn = o.get("buyer_nickname") or ""
            lines.append(
                f"#{int(o['id'])} · {esc(str(o.get('status')))} · "
                f"{esc(str(o.get('product_id')))} · {esc(str(o.get('source')))}"
                + (f" · @{esc(str(bn))}" if bn else "")
            )
    else:
        lines.append("Заказов не найдено.")
    await message.answer("\n".join(lines))


@router.message(Command("admin_vpn_finalize"))
async def cmd_admin_vpn_finalize(
    message: Message, command: CommandObject, settings: Settings, conn
) -> None:
    """Дожать VPN paid→completed (+ реф). /admin_vpn_finalize ORDER_ID | stuck"""
    if not await _require_admin_message(message, settings):
        return
    from bot.services.vpn_order_finalize import finalize_vpn_order_completed
    from bot.services.vpn_referral_repo import is_vpn_order_row

    raw = (command.args or "").strip().lower()
    if not raw:
        await message.answer(
            "Пример:\n"
            "<code>/admin_vpn_finalize 104</code>\n"
            "<code>/admin_vpn_finalize stuck</code> — все VPN в paid/processing"
        )
        return
    ids: list[int] = []
    if raw == "stuck":
        cur = await conn.execute(
            """
            SELECT id FROM orders
            WHERE status IN ('paid', 'processing')
              AND (
                LOWER(COALESCE(product_kind, '')) = 'vpn'
                OR LOWER(COALESCE(product_id, '')) LIKE 'vpn%'
              )
            ORDER BY id ASC
            """
        )
        ids = [int(r["id"]) for r in await cur.fetchall()]
    else:
        try:
            ids = [int(raw)]
        except ValueError:
            await message.answer("ORDER_ID — число или stuck")
            return
    if not ids:
        await message.answer("Нечего финализировать.")
        return
    ok_n = 0
    lines: list[str] = []
    for oid in ids:
        order = await orders_repo.get_order(conn, oid)
        if order is None or not is_vpn_order_row(order):
            lines.append(f"#{oid}: skip (не VPN / нет)")
            continue
        ok = await finalize_vpn_order_completed(settings, oid)
        order2 = await orders_repo.get_order(conn, oid)
        st = str(order2["status"] if order2 else "?")
        comm = float(order2["commission_rub"] or 0) if order2 else 0
        if ok:
            ok_n += 1
        lines.append(f"#{oid}: {'OK' if ok else 'FAIL'} → {esc(st)} · comm={comm:.2f}")
    await message.answer(
        f"<b>VPN finalize</b> ok={ok_n}/{len(ids)}\n" + "\n".join(lines[:40])
    )


@router.message(Command("admin_vpn"))
async def cmd_admin_vpn(message: Message, settings: Settings) -> None:
    if not await _require_admin_message(message, settings):
        return
    await message.answer(
        "<b>VPN — команды для поддержки</b>\n\n"
        "<code>/admin_vpn_status &lt;telegram_id&gt;</code> — статус подписки и ссылка (нужен "
        "<code>VPN_DB_PATH</code>).\n"
        "<code>/admin_vpn_finalize &lt;order_id|stuck&gt;</code> — paid→completed для VPN (+реф).\n"
        "<code>/admin_vpn_revoke &lt;telegram_id&gt; [причина]</code> — отключить VPN.\n"
        "<code>/admin_vpn_extend &lt;telegram_id&gt; &lt;дата_ISO&gt; [order_id]</code> — продлить; "
        "без order_id — последний VPN-заказ в магазине.\n"
        "<code>/admin_vpn_health</code> / <code>/vpn_health</code> — API + jobs + "
        "path-метрики + <b>живые/зомби</b> на RU-bridge.\n"
        "<code>/vpn_zombies</code> / <code>/admin_vpn_zombies</code> — оплаченные+trial и зомби "
        "(без ссылок друзьям).\n"
        "<code>/admin_vpn_announce</code> — статус-инцидент в Happ announce.\n"
        "<code>/admin_vpn_devices &lt;telegram_id&gt;</code> — список устройств.\n"
        "<code>/admin_vpn_device_revoke &lt;tid&gt; &lt;device_id&gt;</code> — отвязать устройство (ссылка умрёт).\n"
        "<code>/admin_vpn_device_reset &lt;telegram_id&gt;</code> — сброс HWID (смена телефона).\n"
        "<code>/admin_vpn_trial_status &lt;telegram_id&gt;</code> — trial_used_at, device binding.\n"
        "<code>/admin_vpn_notices</code> — последние напоминания подписки (TG).\n"
        "  <code>… preset 4g</code> · <code>… set текст</code> · <code>… clear</code>\n\n"
        "Для revoke/extend на сервере должны быть настроены VPN API. "
        "В дашборде <code>/admin</code> блок <b>VPN health</b> обновляется при открытии."
    )


@router.message(Command("admin_vpn_health", "vpn_health"))
async def cmd_admin_vpn_health(message: Message, settings: Settings) -> None:
    if not await _require_admin_message(message, settings):
        return
    from bot.services.vpn_ops_health import collect_vpn_ops_health

    snap = await collect_vpn_ops_health(settings)
    text = snap.summary_html()
    # Telegram message limit ~4096
    if len(text) > 4000:
        text = text[:3900] + "\n…"
    await message.answer(text)


@router.message(Command("admin_vpn_zombies", "vpn_zombies"))
async def cmd_admin_vpn_zombies(message: Message, settings: Settings) -> None:
    """Отчёт по зомби UUID на RU-bridge (после expire + Happ cache)."""
    if not await _require_admin_message(message, settings):
        return
    from bot.services.vpn_bridge_zombie_metrics import (
        collect_bridge_zombie_metrics,
        format_bridge_zombies_html,
    )

    path = (settings.vpn_bridge_peers_status_path or "").strip() or None
    max_age = int(settings.vpn_bridge_status_max_age_sec or 10800)
    m = collect_bridge_zombie_metrics(path, max_age_sec=max_age)
    text = format_bridge_zombies_html(m)
    if len(text) > 4000:
        text = text[:3900] + "\n…"
    await message.answer(text)


async def _post_vpn_status_channel(message: Message, settings: Settings, text: str) -> None:
    ch = (settings.vpn_status_channel_post_id or "").strip()
    if not ch or not text.strip():
        return
    try:
        await message.bot.send_message(
            int(ch),
            f"⚠️ <b>AiMonkey VPN</b>\n{esc(text.strip())}",
            disable_web_page_preview=True,
        )
    except Exception:
        pass


@router.message(Command("admin_vpn_announce"))
async def cmd_admin_vpn_announce(message: Message, command: CommandObject, settings: Settings, conn) -> None:
    if not await _require_admin_message(message, settings):
        return
    from bot.services.vpn_status_incident import PRESET_4G, resolve_preset

    if not (settings.vpn_api_base_url or "").strip():
        await message.answer("Нужен <code>VPN_API_BASE_URL</code> на боте.")
        return

    args = (command.args or "").strip()
    parts = args.split(maxsplit=1) if args else []
    sub = parts[0].lower() if parts else ""

    if not sub:
        ok, text = await vpn_api_client.get_status_announce(settings)
        if not ok:
            await message.answer("Не удалось прочитать announce с VPN API.")
            return
        if text:
            await message.answer(
                f"<b>Активный announce</b>\n{esc(text)}\n\n"
                "<code>/admin_vpn_announce clear</code> — сбросить."
            )
        else:
            await message.answer(
                "Инцидентный announce <b>не задан</b> (обычный текст из env).\n"
                f"Пресет 4G: <code>/admin_vpn_announce preset 4g</code>\n"
                f"Свой текст: <code>/admin_vpn_announce set …</code>"
            )
        return

    if sub == "clear":
        ok, msg = await vpn_api_client.clear_status_announce(settings)
        await _audit_admin(conn, message.from_user.id, "vpn:announce_clear", ok=ok, detail=msg[:200])
        await conn.commit()
        if ok:
            await message.answer("✅ Announce сброшен. Happ подтянет после обновления подписки.")
            await _post_vpn_status_channel(message, settings, "✅ Инцидент закрыт, VPN в штатном режиме.")
        else:
            await message.answer(f"Ошибка: {esc(msg)}")
        return

    if sub == "preset":
        preset_name = parts[1].strip() if len(parts) > 1 else "4g"
        text = resolve_preset(preset_name) or PRESET_4G
    elif sub == "set":
        if len(parts) < 2 or not parts[1].strip():
            await message.answer("Пример: <code>/admin_vpn_announce set Временные проблемы на 4G…</code>")
            return
        text = parts[1].strip()
    else:
        await message.answer(
            "Команды:\n"
            "<code>/admin_vpn_announce</code> — текущий статус\n"
            "<code>/admin_vpn_announce preset 4g</code>\n"
            "<code>/admin_vpn_announce set текст</code>\n"
            "<code>/admin_vpn_announce clear</code>"
        )
        return

    ok, msg = await vpn_api_client.post_status_announce(settings, text=text)
    await _audit_admin(
        conn,
        message.from_user.id,
        "vpn:announce_set",
        ok=ok,
        detail=text[:200],
    )
    await conn.commit()
    if ok:
        await message.answer(
            "✅ Announce установлен.\n"
            f"{esc(text)}\n\n"
            "<i>Пользователи увидят в Happ после обновления подписки 🔄</i>"
        )
        await _post_vpn_status_channel(message, settings, text)
    else:
        await message.answer(f"Ошибка: {esc(msg)}")


@router.message(Command("admin_vpn_status"))
async def cmd_admin_vpn_status(message: Message, command: CommandObject, settings: Settings, conn) -> None:
    if not await _require_admin_message(message, settings):
        return
    parts = (command.args or "").split()
    if len(parts) != 1 or not parts[0].isdigit():
        await message.answer("Пример: <code>/admin_vpn_status 123456789</code>")
        return
    tid = int(parts[0])
    vpath = settings.resolved_vpn_db_path()
    if vpath is None:
        await message.answer("Не задан <code>VPN_DB_PATH</code> — база VPN недоступна с бота.")
        return
    snap = await vpn_admin_support_repo.fetch_vpn_account_admin_snapshot(vpath, tid)
    if snap is None:
        await message.answer(f"Файл vpn.db не найден или недоступен: <code>{esc(str(vpath))}</code>")
        return
    txt = vpn_admin_support_repo.format_vpn_admin_snapshot_html(snap)
    await _audit_admin(conn, message.from_user.id, "vpn:admin_status", telegram_user_id=tid)
    await conn.commit()
    await message.answer(txt)


@router.message(Command("admin_vpn_devices"))
async def cmd_admin_vpn_devices(
    message: Message, command: CommandObject, settings: Settings, conn
) -> None:
    if not await _require_admin_message(message, settings):
        return
    parts = (command.args or "").split()
    if len(parts) != 1 or not parts[0].isdigit():
        await message.answer("Пример: <code>/admin_vpn_devices 123456789</code>")
        return
    tid = int(parts[0])
    if not (settings.vpn_api_base_url or "").strip():
        await message.answer("Нужен <code>VPN_API_BASE_URL</code> на боте.")
        return
    ok, data = await vpn_api_client.post_devices_list(settings, telegram_user_id=tid)
    await _audit_admin(
        conn,
        message.from_user.id,
        "vpn:admin_devices",
        telegram_user_id=tid,
        ok=ok,
        detail=str(data)[:200] if not ok else "",
    )
    await conn.commit()
    if not ok or not isinstance(data, dict):
        await message.answer(f"<b>Ошибка</b> devices/list:\n<pre>{esc(str(data)[:400])}</pre>")
        return
    used = int(data.get("used") or 0)
    maximum = int(data.get("max") or 1)
    devices = list(data.get("devices") or [])
    lines = [
        f"<b>Устройства</b> tid=<code>{tid}</code>",
        f"Занято <b>{used} из {maximum}</b>",
        "",
    ]
    if not devices:
        lines.append("<i>Нет активных устройств.</i>")
    for d in devices:
        did = int(d.get("id") or 0)
        name = esc(str(d.get("display_name") or "Устройство"))
        st = esc(str(d.get("status") or "—"))
        kind = esc(str(d.get("device_kind") or "unknown"))
        url = str(d.get("subscription_url") or "").strip()
        lines.append(f"• id=<code>{did}</code> <b>{name}</b> ({kind}) — {st}")
        if url:
            lines.append(f"  <code>{esc(url)}</code>")
    lines.append("")
    lines.append(
        "Отвязать: <code>/admin_vpn_device_revoke "
        f"{tid} DEVICE_ID</code>"
    )
    lines.append(f"Сброс HWID: <code>/admin_vpn_device_reset {tid}</code>")
    await message.answer("\n".join(lines), disable_web_page_preview=True)


@router.message(Command("admin_vpn_device_revoke"))
async def cmd_admin_vpn_device_revoke(
    message: Message, command: CommandObject, settings: Settings, conn
) -> None:
    if not await _require_admin_message(message, settings):
        return
    parts = (command.args or "").split()
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        await message.answer(
            "Пример: <code>/admin_vpn_device_revoke 123456789 42</code>\n"
            "Сначала: <code>/admin_vpn_devices 123456789</code>"
        )
        return
    tid = int(parts[0])
    device_id = int(parts[1])
    if not (settings.vpn_api_base_url or "").strip():
        await message.answer("Нужен <code>VPN_API_BASE_URL</code> на боте.")
        return
    ikey = f"admin-dev-rev:{message.from_user.id}:{tid}:{device_id}:{secrets.token_hex(4)}"
    ok, data = await vpn_api_client.post_devices_revoke(
        settings,
        telegram_user_id=tid,
        device_id=device_id,
        idempotency_key=ikey,
    )
    await _audit_admin(
        conn,
        message.from_user.id,
        "vpn:admin_device_revoke",
        telegram_user_id=tid,
        ok=ok,
        detail=f"device_id={device_id} {str(data)[:200]}",
    )
    await conn.commit()
    if not ok:
        await message.answer(f"<b>Ошибка</b> revoke:\n<pre>{esc(str(data)[:400])}</pre>")
        return
    await message.answer(
        f"✅ Устройство <code>{device_id}</code> отвязано у <code>{tid}</code>. "
        "Ссылка /sub больше не действует."
    )
    try:
        await message.bot.send_message(
            tid,
            (
                "<b>Устройство отвязано поддержкой</b>\n\n"
                "Старая ссылка Happ больше не работает.\n"
                "Подключить новое устройство можно в разделе «Мои устройства»."
            ),
        )
    except Exception:
        pass


@router.message(Command("admin_vpn_device_reset"))
async def cmd_admin_vpn_device_reset(
    message: Message, command: CommandObject, settings: Settings, conn
) -> None:
    if not await _require_admin_message(message, settings):
        return
    parts = (command.args or "").split()
    if len(parts) != 1 or not parts[0].isdigit():
        await message.answer("Пример: <code>/admin_vpn_device_reset 123456789</code>")
        return
    tid = int(parts[0])
    if not (settings.vpn_api_base_url or "").strip():
        await message.answer("Нужен <code>VPN_API_BASE_URL</code> на боте.")
        return
    ikey = f"admin-device-reset:{message.from_user.id}:{tid}:{secrets.token_hex(6)}"
    ok, msg = await vpn_api_client.post_device_reset(
        settings,
        telegram_user_id=tid,
        reason="admin_support",
        idempotency_key=ikey,
    )
    await _audit_admin(
        conn,
        message.from_user.id,
        "vpn:admin_device_reset",
        telegram_user_id=tid,
        ok=ok,
        detail=msg[:300],
    )
    await conn.commit()
    if not ok:
        await message.answer(f"<b>Ошибка</b> device_reset:\n<pre>{esc(msg)}</pre>")
        return
    await message.answer(f"✅ HWID сброшен для <code>{tid}</code>.")
    try:
        await message.bot.send_message(
            tid,
            (
                "<b>📱 Смена устройства</b>\n\n"
                "Привязка телефона (HWID) сброшена поддержкой.\n"
                "Откройте Happ на новом телефоне → обновите подписку → вставьте ссылку из бота."
            ),
        )
    except Exception:
        await message.answer(f"HWID сброшен, но не удалось написать пользователю <code>{tid}</code>.")


@router.message(Command("admin_vpn_trial_status"))
async def cmd_admin_vpn_trial_status(
    message: Message, command: CommandObject, settings: Settings, conn
) -> None:
    if not await _require_admin_message(message, settings):
        return
    parts = (command.args or "").split()
    if len(parts) != 1 or not parts[0].isdigit():
        await message.answer("Пример: <code>/admin_vpn_trial_status 123456789</code>")
        return
    tid = int(parts[0])
    vpath = settings.resolved_vpn_db_path()
    if vpath is None:
        await message.answer("Не задан <code>VPN_DB_PATH</code>.")
        return
    snap = await vpn_admin_support_repo.fetch_vpn_trial_admin_snapshot(vpath, tid)
    if snap is None:
        await message.answer(f"vpn.db недоступен: <code>{esc(str(vpath))}</code>")
        return
    txt = vpn_admin_support_repo.format_vpn_trial_status_html(snap)
    await _audit_admin(conn, message.from_user.id, "vpn:admin_trial_status", telegram_user_id=tid)
    await conn.commit()
    await message.answer(txt)


@router.message(Command("admin_vpn_notices"))
async def cmd_admin_vpn_notices(
    message: Message, command: CommandObject, settings: Settings, conn
) -> None:
    if not await _require_admin_message(message, settings):
        return
    from bot.services import vpn_expiry_notify_repo

    await vpn_expiry_notify_repo.ensure_vpn_expiry_notices_table(conn)
    limit = 30
    parts = (command.args or "").split()
    if parts and parts[0].isdigit():
        limit = max(1, min(int(parts[0]), 100))
    rows = await vpn_expiry_notify_repo.list_recent_notices(conn, limit=limit)
    await _audit_admin(conn, message.from_user.id, "vpn:admin_notices")
    await conn.commit()
    if not rows:
        await message.answer("Лог напоминаний пуст.")
        return
    lines = ["<b>VPN notices</b> (последние):"]
    for r in rows:
        err = esc((r.get("last_error") or "")[:80])
        lines.append(
            f"• <code>{r['telegram_user_id']}</code> <b>{esc(r['kind'])}</b> "
            f"{esc(r['status'])}×{r['attempts']} {esc(r['channel'])} "
            f"<i>{esc(r['sent_at'])}</i>"
            + (f" err={err}" if err else "")
        )
    await message.answer("\n".join(lines)[:3900])


@router.message(Command("admin_vpn_revoke"))
async def cmd_admin_vpn_revoke(message: Message, command: CommandObject, settings: Settings, conn) -> None:
    if not await _require_admin_message(message, settings):
        return
    parts = (command.args or "").split(maxsplit=1)
    if not parts or not parts[0].isdigit():
        await message.answer("Пример: <code>/admin_vpn_revoke 123456789 abuse</code>")
        return
    tid = int(parts[0])
    reason = parts[1].strip() if len(parts) > 1 else "admin_revoke"
    if not reason:
        reason = "admin_revoke"
    ikey = f"admin-revoke:{message.from_user.id}:{tid}:{secrets.token_hex(6)}"
    ok, msg = await vpn_api_client.post_revoke(
        settings, telegram_user_id=tid, reason=reason, idempotency_key=ikey
    )
    await _audit_admin(
        conn,
        message.from_user.id,
        "vpn:admin_revoke",
        telegram_user_id=tid,
        reason=reason[:200],
        ok=ok,
        detail=msg[:300],
    )
    await conn.commit()
    if ok:
        await message.answer(f"Отключение VPN поставлено в очередь.\n<pre>{esc(msg)}</pre>")
    else:
        await message.answer(f"<b>Ошибка</b> revoke:\n<pre>{esc(msg)}</pre>")


@router.message(Command("admin_vpn_extend"))
async def cmd_admin_vpn_extend(message: Message, command: CommandObject, settings: Settings, conn) -> None:
    if not await _require_admin_message(message, settings):
        return
    raw = (command.args or "").strip()
    parts = raw.split()
    if len(parts) < 2:
        await message.answer(
            "Пример: <code>/admin_vpn_extend 123456789 2026-12-31T23:59:59+00:00</code>\n"
            "или с заказом: <code>/admin_vpn_extend 123456789 2026-12-31T23:59:59+00:00 555</code>"
        )
        return
    if not parts[0].isdigit():
        await message.answer("Некорректный <code>telegram_user_id</code>.")
        return
    tid = int(parts[0])
    paid_iso = _parse_admin_vpn_paid_until(parts[1])
    if not paid_iso:
        await message.answer("Некорректная дата <code>paid_until</code> (ожидается ISO8601, UTC предпочтителен).")
        return
    order_id: int | None = None
    if len(parts) >= 3:
        if not parts[2].isdigit():
            await message.answer("Некорректный <code>order_id</code>.")
            return
        order_id = int(parts[2])
    else:
        order_id = await orders_repo.last_vpn_order_id_for_user(conn, tid)
        if order_id is None:
            await message.answer(
                "Не найден VPN-заказ для этого пользователя — укажите <code>order_id</code> явно "
                "(из карточки заказа)."
            )
            return
    ikey = f"admin-extend:{message.from_user.id}:{tid}:{secrets.token_hex(6)}"
    ok, msg = await vpn_api_client.post_extend(
        settings,
        telegram_user_id=tid,
        order_id=int(order_id),
        paid_until=paid_iso,
        idempotency_key=ikey,
    )
    await _audit_admin(
        conn,
        message.from_user.id,
        "vpn:admin_extend",
        telegram_user_id=tid,
        order_id=int(order_id),
        paid_until=paid_iso,
        ok=ok,
        detail=msg[:300],
    )
    await conn.commit()
    if ok:
        await message.answer(
            f"Extend поставлен в очередь, order_id=<code>{esc(str(order_id))}</code>, "
            f"<code>{esc(ikey)}</code>.\n<pre>{esc(msg)}</pre>"
        )
    else:
        await message.answer(f"<b>Ошибка</b> extend:\n<pre>{esc(msg)}</pre>")


@router.message(Command("contest"))
async def cmd_contest(message: Message, command: CommandObject, settings: Settings, conn) -> None:
    if not await _require_admin_message(message, settings):
        return
    raw = (command.args or "").strip()
    if not raw:
        await message.answer(
            "<b>Конкурсы партнёров</b>\n\n"
            "<code>/contest list</code> - список\n"
            "<code>/contest new Заголовок | Текст приза | YYYY-MM-DD | YYYY-MM-DD [on]</code>\n"
            "  последний аргумент <code>on</code> - сразу сделать единственным активным\n"
            "<code>/contest activate ID</code>\n"
            "<code>/contest deactivate_all</code>",
        )
        return
    parts = raw.split()
    cmd = parts[0].lower()
    if cmd == "list":
        rows = await contest_repo.list_contests(conn, limit=15)
        if not rows:
            await message.answer("<b>Конкурсы</b>: записей нет.")
            return
        lines = ["<b>Конкурсы</b>\n"]
        for r in rows:
            act = "✅" if int(r["is_active"] or 0) else "○"
            lines.append(
                f"{act} <code>#{r['id']}</code> {esc(r['title'])} · {esc(r['starts_at'])} → {esc(r['ends_at'])}"
            )
        await message.answer("\n".join(lines))
        return
    if cmd == "deactivate_all":
        if not settings.is_super_admin(message.from_user.id):
            await message.answer("Только супер-админ может деактивировать все конкурсы.")
            return
        await contest_repo.deactivate_all(conn)
        await _audit_admin(conn, message.from_user.id, "contest:deactivate_all")
        await message.answer("<b>Конкурсы</b>: все деактивированы.")
        return
    if cmd == "activate" and len(parts) >= 2:
        if not settings.is_super_admin(message.from_user.id):
            await message.answer("Только супер-админ может активировать конкурс.")
            return
        try:
            cid = int(parts[1])
        except ValueError:
            await message.answer("Некорректный ID.")
            return
        ok = await contest_repo.set_contest_active(conn, cid, active=True)
        if ok:
            await _audit_admin(conn, message.from_user.id, "contest:activate", contest_id=cid)
        await message.answer("Активирован." if ok else "Не найдено.")
        return
    if cmd == "new":
        if not settings.is_super_admin(message.from_user.id):
            await message.answer("Только супер-админ может создавать конкурс.")
            return
        body = raw.removeprefix("new").strip()
        if not body:
            await message.answer("Укажите поля через | после <code>new</code>.")
            return
        seg = [x.strip() for x in body.split("|")]
        if len(seg) < 4:
            await message.answer("Нужно 4 поля: Заголовок | Приз | дата начала | дата конца")
            return
        title, prize, ds, de = seg[:4]
        activate = len(seg) >= 5 and seg[4].lower() in ("on", "1", "yes", "true")
        try:
            s_norm = normalize_contest_date(ds, end_of_day=False)
            e_norm = normalize_contest_date(de, end_of_day=True)
        except Exception:
            await message.answer("Ошибка дат. Формат: YYYY-MM-DD")
            return
        oid = await contest_repo.create_contest(
            conn,
            title=title,
            prize_text=prize,
            starts_at=s_norm,
            ends_at=e_norm,
            activate=activate,
        )
        await _audit_admin(
            conn,
            message.from_user.id,
            "contest:new",
            contest_id=oid,
            title=title,
            activate=activate,
        )
        await message.answer(f"<b>Создан конкурс</b> <code>#{oid}</code>." + (" Активен." if activate else ""))
        return
    await message.answer("Неизвестная подкоманда. См. /contest")


@router.message(Command("admin_promo"))
async def cmd_admin_promo(message: Message, command: CommandObject, settings: Settings, conn) -> None:
    if not await _require_admin_message(message, settings):
        return
    raw = (command.args or "").strip()
    if not raw:
        await message.answer(
            "<b>Промокоды</b>\n\n"
            "<code>/admin_promo list</code>\n"
            "<code>/admin_promo off ID</code>\n"
            "<code>/admin_promo on ID</code>\n"
            "<code>/admin_promo new CODE | percent|rub | VALUE | scope | "
            "YYYY-MM-DD | YYYY-MM-DD | maxN|0 | once|multi | [uids] | [new]</code>\n\n"
            "scope: <code>all</code> / <code>stars</code> / <code>premium</code> / <code>vpn</code>\n"
            "maxN=0 — без лимита активаций · <code>new</code> — только новым\n"
            "uids — telegram id через запятую (персональный)\n"
            "Пример: <code>/admin_promo new SUMMER10 | percent | 10 | all | "
            "2026-07-01 | 2026-08-31 | 100 | once</code>",
        )
        return
    parts = raw.split(maxsplit=1)
    cmd = parts[0].lower()
    if cmd == "list":
        rows = await promo_repo.list_promos(conn, limit=20)
        if not rows:
            await message.answer("<b>Промокоды</b>: пусто.")
            return
        lines = ["<b>Промокоды</b>\n"]
        for r in rows:
            act = "✅" if int(r["is_active"] or 0) else "○"
            lim = r["max_activations"]
            lim_s = "∞" if lim is None else str(lim)
            lines.append(
                f"{act} <code>#{r['id']}</code> <b>{esc(r['code'])}</b> · "
                f"{esc(r['discount_type'])} {esc(r['discount_value'])} · "
                f"{esc(r['scope'])} · {esc(r['activation_count'])}/{esc(lim_s)}"
            )
        await message.answer("\n".join(lines))
        return
    if cmd in ("on", "off") and len(parts) >= 2:
        if not settings.is_super_admin(message.from_user.id):
            await message.answer("Только супер-админ.")
            return
        try:
            pid = int(parts[1].strip().split()[0])
        except ValueError:
            await message.answer("Некорректный ID.")
            return
        ok = await promo_repo.set_promo_active(conn, pid, active=(cmd == "on"))
        await _audit_admin(conn, message.from_user.id, f"promo:{cmd}", promo_id=pid)
        await message.answer("OK." if ok else "Не найдено.")
        return
    if cmd == "new":
        if not settings.is_super_admin(message.from_user.id):
            await message.answer("Только супер-админ может создавать промокоды.")
            return
        body = raw.removeprefix("new").strip()
        seg = [x.strip() for x in body.split("|")]
        if len(seg) < 7:
            await message.answer(
                "Нужно: CODE | percent|rub | VALUE | scope | start | end | maxN|0 | once|multi …"
            )
            return
        code, dtype, dval_s, scope, ds, de, max_s = seg[:7]
        once = True
        if len(seg) >= 8 and seg[7].lower() in ("multi", "many", "0"):
            once = False
        uids = seg[8] if len(seg) >= 9 else ""
        new_only = any(x.lower() == "new" for x in seg[8:])
        try:
            dval = float(dval_s.replace(",", "."))
        except ValueError:
            await message.answer("VALUE должно быть числом.")
            return
        try:
            max_n = int(max_s)
        except ValueError:
            await message.answer("maxN — целое (0 = без лимита).")
            return
        max_activations = None if max_n <= 0 else max_n
        try:
            s_norm = normalize_contest_date(ds, end_of_day=False) if ds else None
            e_norm = normalize_contest_date(de, end_of_day=True) if de else None
        except Exception:
            await message.answer("Ошибка дат. Формат: YYYY-MM-DD")
            return
        try:
            oid = await promo_repo.create_promo(
                conn,
                code=code,
                title=code,
                discount_type=dtype,
                discount_value=dval,
                scope=scope,
                starts_at=s_norm,
                ends_at=e_norm,
                max_activations=max_activations,
                once_per_user=once,
                new_users_only=new_only,
                allowed_user_ids=uids if uids.lower() != "new" else "",
            )
        except Exception as exc:
            await message.answer(f"<b>Ошибка</b>: {esc(exc)}")
            return
        await _audit_admin(conn, message.from_user.id, "promo:new", promo_id=oid, code=code)
        await message.answer(f"<b>Промокод создан</b> <code>#{oid}</code> · <b>{esc(code.upper())}</b>")
        return
    await message.answer("Неизвестная подкоманда. См. /admin_promo")


@router.callback_query(F.data.startswith("adm:"))
async def admin_set_status(cb: CallbackQuery, settings: Settings, conn) -> None:
    if not _is_admin(cb.from_user.id, settings):
        await cb.answer("Нет доступа", show_alert=True)
        return
    _, action, oid_s = cb.data.split(":", 2)
    order_id = int(oid_s)
    mapping = {
        "paid": "paid",
        "paidbg": "paid",
        "proc": "processing",
        "done": "completed",
        "refund": "refunded",
        "disp": "payment_disputed",
        "dispok": "paid",
    }
    new_status = mapping.get(action)
    if not new_status:
        await cb.answer()
        return

    if new_status in ("refunded", "payment_disputed") and not settings.is_super_admin(cb.from_user.id):
        await cb.answer("Только супер-админ: сторно / спор по заказу.", show_alert=True)
        return

    if new_status in ("paid", "completed") and not settings.is_super_admin(cb.from_user.id):
        await cb.answer("Только супер-админ отмечает «Оплачен» или «Выдан».", show_alert=True)
        return

    order = await orders_repo.get_order(conn, order_id)
    if not order:
        await cb.answer("Заказ не найден", show_alert=True)
        return

    prev_status = str(order["status"])
    if action == "dispok" and prev_status != "payment_disputed":
        await cb.answer("«Снять спор» только из статуса спора.", show_alert=True)
        return
    if new_status == "paid" and prev_status == "pending_payment":
        applies = crypto_manual_paid_gate_applies(order, settings)
        if action == "paid" and applies:
            await cb.answer(
                "Заказ в ожидании оплаты через Crypto Pay / xRocket: дождитесь вебхука. "
                "Ручное «Оплачен» здесь отключено. Если вебхук невозможен - кнопка break-glass в карточке заказа.",
                show_alert=True,
            )
            return
        if action == "paidbg":
            if not applies:
                await cb.answer(
                    "Break-glass только для заказов в ожидании оплаты с крипто-счётом "
                    "(включён Crypto Pay или xRocket). Иначе используйте «Оплачен».",
                    show_alert=True,
                )
                return
    break_glass_payload: dict[str, object] | None = None
    if action == "paidbg":
        amount = float(order["rub_after_discounts"] or 0.0)
        super_admin_count = len(
            [x for x in settings.parsed_admin_ids() if settings.is_super_admin(x)]
        )
        two_eyes_threshold = float(settings.break_glass_two_eyes_threshold_rub or 0.0)
        two_eyes_required = bool(two_eyes_threshold > 0 and amount >= two_eyes_threshold and super_admin_count >= 2)
        break_glass_payload = {
            "reason_code": "webhook_unavailable_manual_paid",
            "provider": str(order["invoice_last_provider"] or order["payment_method"] or "unknown"),
            "external_invoice_id": str(order["invoice_last_external_id"] or ""),
            "evidence_ref": f"order:{order_id}",
            "two_eyes_required": two_eyes_required,
            "two_eyes_threshold_rub": two_eyes_threshold,
            "order_amount_rub": amount,
        }

    try:
        await orders_repo.update_status(conn, order_id, new_status)
    except ValueError as exc:
        if "invalid_order_transition" in str(exc) or "order_not_found" in str(exc):
            cur_st = str(order["status"])
            hint = {
                "completed": "Заказ уже «Выдан» — кнопка «Оплачен» не нужна.",
                "expired": "Заказ истёк. Сначала «Оплачен», если оплата была.",
                "refunded": "Заказ: возврат оформлен.",
                "processing": "Заказ уже в автовыдаче. Дождитесь «Выдан» или проверьте ошибку.",
            }.get(cur_st, f"Сейчас статус «{cur_st}» — этот переход невозможен.")
            await cb.answer(hint, show_alert=True)
            return
        raise

    if new_status == "paid":
        from bot.services.paid_order_hooks import schedule_post_paid_order_hooks

        schedule_post_paid_order_hooks(settings, order_id)
        try:
            await analytics_repo.log_event(
                conn,
                user_id=int(order["user_id"]),
                event_type="checkout_paid",
                meta={"order_id": order_id, "payment_method": str(order["payment_method"] or "")},
            )
        except Exception:
            pass

    if new_status == "completed" and prev_status != "completed":
        await apply_completed_side_effects(conn, order_id, settings)
        try:
            await analytics_repo.log_event(
                conn,
                user_id=int(order["user_id"]),
                event_type="order_completed",
                meta={"order_id": order_id, "payment_method": str(order["payment_method"] or "")},
            )
        except Exception:
            pass

    audit_action = "adm:paid_break_glass" if action == "paidbg" else f"adm:{action}"
    await _audit_admin(
        conn,
        cb.from_user.id,
        audit_action,
        order_id=order_id,
        from_status=prev_status,
        to_status=new_status,
        **(break_glass_payload or {}),
    )
    if action == "paidbg" and break_glass_payload is not None:
        amount = float(break_glass_payload["order_amount_rub"])
        await send_alert(
            settings=settings,
            severity="warning",
            title="break-glass paid applied",
            body=(
                f"order_id={order_id} admin_id={cb.from_user.id} amount_rub={amount:.2f} "
                f"provider={break_glass_payload['provider']} "
                f"external_invoice_id={break_glass_payload['external_invoice_id']} "
                f"evidence_ref={break_glass_payload['evidence_ref']} "
                f"two_eyes_required={break_glass_payload['two_eyes_required']}"
            ),
            dedupe_key=f"break_glass_paid:{order_id}",
        )

    order2 = await orders_repo.get_order(conn, order_id)
    text = _admin_order_message_text(order2, order_id, settings, status_for_header=new_status)
    await cb.message.edit_text(
        text,
        reply_markup=admin_order_kb(
            order_id,
            settings=settings,
            actor_id=cb.from_user.id,
            order_ff=ff_context_from_order_row(order2),
        ),
    )

    buyer_text = buyer_message_admin_status_change(order_id=order_id, new_status=new_status)
    if new_status == "completed" and prev_status != "completed":
        schedule_post_order_completed_notifications(
            settings,
            order_id=order_id,
            user_id=int(order2["user_id"]),
            source="admin",
        )
    elif buyer_text:
        try:
            await cb.bot.send_message(int(order2["user_id"]), buyer_text)
        except Exception:
            pass
    asyncio.create_task(
        emit_order_status_changed(
            db_path=settings.database_path,
            order_id=order_id,
            previous_status=prev_status,
            new_status=new_status,
        )
    )
    await cb.answer("OK")


@router.callback_query(F.data.startswith("top:ok:"))
async def admin_topup_ok(cb: CallbackQuery, settings: Settings, conn) -> None:
    if not _is_admin(cb.from_user.id, settings):
        await cb.answer("Нет доступа", show_alert=True)
        return
    if not settings.is_super_admin(cb.from_user.id):
        await cb.answer("Только супер-админ может зачислить топап.", show_alert=True)
        return
    tid = int(cb.data.split(":")[-1])
    row = await balance_repo.get_topup(conn, tid)
    if not row:
        await cb.answer("Не найдено", show_alert=True)
        return
    uid = int(row["user_id"])
    ok = await balance_repo.approve_topup(conn, tid)
    if not ok:
        await cb.answer("Уже обработано", show_alert=True)
        return
    await _audit_admin(conn, cb.from_user.id, "top:ok", topup_id=tid, user_id=uid)
    await cb.message.edit_text(
        f"<b>Пополнение #{esc(tid)}</b>\nПользователь <code>{esc(uid)}</code>\n<b>✅ Зачислено</b>",
    )
    try:
        await cb.bot.send_message(uid, f"<b>Баланс пополнен</b> по заявке <code>#{esc(tid)}</code>.")
    except Exception:
        pass
    await cb.answer()
