"""Admin UX screens — business-facing views (ТЗ админ-панели).

Does not change payment/VPN/referral business logic; only HTML + keyboards.
Legacy full dashboard remains in handlers.admin._format_dashboard_html.
"""

from __future__ import annotations

from typing import Any

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.services.admin_stats_repo import DashboardAgg
from bot.util_html import esc


def period_label(days: int | None, *, token: str | None = None) -> str:
    t = (token or "").strip().lower()
    if t in ("start", "since", "launch"):
        return "с запуска"
    if days is None:
        return "всё время"
    if days <= 1:
        return "сегодня"
    if days == 7:
        return "7 дней"
    if days == 30:
        return "30 дней"
    return f"{days} дн."


def days_from_token(token: str) -> int | None:
    t = (token or "").strip().lower()
    if t in ("today", "1"):
        return 1
    if t in ("7", "7d"):
        return 7
    if t in ("30", "30d"):
        return 30
    if t in ("all", "0", "start", "since", "launch"):
        return None
    try:
        n = int(t)
        return None if n <= 0 else n
    except ValueError:
        return 7


def kind_from_token(token: str | None) -> str | None:
    """all/empty → None (все товары); vpn|stars|premium → kind."""
    t = (token or "").strip().lower()
    if not t or t in ("all", "any", "*"):
        return None
    if t in ("vpn", "stars", "premium"):
        return t
    return None


def kind_token(kind: str | None) -> str:
    return (kind or "all").strip().lower() or "all"


def kind_label(kind: str | None) -> str:
    kk = kind_from_token(kind_token(kind))
    return {
        None: "Все",
        "vpn": "VPN",
        "stars": "Stars",
        "premium": "Premium",
    }.get(kk, "Все")


def aux_cb(action: str, period: str, kind: str | None = None) -> str:
    """aux:finance:7 or aux:finance:7:vpn"""
    p = (period or "7").strip() or "7"
    k = kind_token(kind)
    if k == "all":
        return f"aux:{action}:{p}"
    return f"aux:{action}:{p}:{k}"


def parse_period_kind(parts: list[str], *, default_period: str = "7") -> tuple[str, str | None]:
    """From aux parts after action: [period] or [period, kind] → (period_token, kind|None)."""
    period = parts[0] if parts else default_period
    kind = kind_from_token(parts[1]) if len(parts) >= 2 else None
    # if first token is actually a kind (legacy), ignore
    if period in ("vpn", "stars", "premium", "all") and len(parts) == 1:
        return default_period, kind_from_token(period)
    return period, kind


def rent_estimate_rub(*, monthly_rub: float, days: int | None) -> float:
    """Доля месячной аренды за период (дни/30). days=None → как 365д (~год)."""
    m = max(0.0, float(monthly_rub))
    if m <= 0:
        return 0.0
    d = 365 if days is None else max(1, int(days))
    return round(m * (d / 30.0), 2)


def _traffic(status: str | None) -> str:
    s = (status or "").lower()
    if s in ("ok", "green", "healthy"):
        return "🟢"
    if s in ("degraded", "yellow", "warn"):
        return "🟡"
    if s in ("critical", "red", "down"):
        return "🔴"
    return "⚪"


def format_attention_block(
    *,
    pending_payment: int = 0,
    vpn_ending_hint: int = 0,
    withdraw_pending: int = 0,
    vpn_status: str | None = None,
) -> str:
    lines = ["🚨 <b>Требует внимания</b>"]
    n = 0
    if pending_payment > 0:
        lines.append(f"🔴 Ожидают оплаты: <b>{esc(str(pending_payment))}</b>")
        n += 1
    if vpn_ending_hint > 0:
        lines.append(f"🟡 VPN истекших (paid): <b>{esc(str(vpn_ending_hint))}</b>")
        n += 1
    if withdraw_pending > 0:
        lines.append(f"🟡 Заявки на вывод: <b>{esc(str(withdraw_pending))}</b>")
        n += 1
    icon = _traffic(vpn_status)
    if vpn_status:
        label = {"ok": "работает", "degraded": "есть проблема", "critical": "срочно"}.get(
            (vpn_status or "").lower(), vpn_status
        )
        lines.append(f"{icon} VPN: <b>{esc(str(label))}</b>")
    if n == 0 and (not vpn_status or (vpn_status or "").lower() == "ok"):
        lines.append("🟢 Критичных задач нет")
    return "\n".join(lines)


def format_money_rub_usdt(*, rub: float, usd_rub_rate: float) -> str:
    """Админ-only: «12.34 ₽ / 0.14 USDT». Курс 0 → только ₽."""
    r = float(rub or 0)
    rate = float(usd_rub_rate or 0)
    if rate > 0.009:
        u = round(r / rate, 2)
        return f"{r:.2f} ₽ / {u:.2f} USDT"
    return f"{r:.2f} ₽"


def format_delta_line(*, revenue_pct: float | None, net_pct: float | None) -> str | None:
    """D5: human Δ к прошлому периоду. None → не показывать."""
    if revenue_pct is None and net_pct is None:
        return None

    def _fmt(v: float | None, label: str) -> str | None:
        if v is None:
            return None
        sign = "+" if v > 0 else ""
        return f"{label} {sign}{v:g}%"

    parts = [p for p in (_fmt(revenue_pct, "выр."), _fmt(net_pct, "чистая")) if p]
    if not parts:
        return None
    return "📈 к прошлому: " + " · ".join(parts)


def format_business_dashboard(
    *,
    period_label_s: str,
    agg: DashboardAgg,
    rm: dict[str, Any],
    vpn_cp: dict[str, Any] | None = None,
    vpn_status: str | None = None,
    pending_payment: int = 0,
    withdraw_pending: int = 0,
    pending_fulfill_count: int = 0,
    pending_fulfill_rub: float = 0.0,
    rent_monthly_rub: float = 0.0,
    rent_period_rub: float = 0.0,
    delta_revenue_pct: float | None = None,
    delta_net_pct: float | None = None,
    usd_rub_rate: float = 0.0,
) -> str:
    """Short business dashboard (ТЗ §5 + KPI §5.1) — no p50/RTT/CF/swap."""
    vpn_cp = vpn_cp or {}
    # Prefer paid-only counters (D1); fall back to legacy keys if absent.
    active = int(
        vpn_cp.get(
            "vpn_cp_paid_accounts_vpn_active",
            vpn_cp.get("vpn_cp_accounts_vpn_active", 0),
        )
        or 0
    )
    expired = int(
        vpn_cp.get(
            "vpn_cp_paid_accounts_vpn_expired",
            vpn_cp.get(
                "vpn_cp_accounts_vpn_expired",
                vpn_cp.get("vpn_cp_accounts_expired", 0),
            ),
        )
        or 0
    )
    total_acc = int(
        vpn_cp.get(
            "vpn_cp_paid_accounts_total",
            vpn_cp.get("vpn_cp_accounts_total", 0),
        )
        or 0
    )
    ref_bonus = float(rm.get("total_referral_bonus_rub", 0) or 0)
    referrers = int(agg.distinct_referrers or 0)
    gross = float(agg.net_profit_rub or 0)
    fees = float(getattr(agg, "fees_rub", 0) or 0)
    after_rent = round(gross - float(rent_period_rub or 0), 2)
    vpn_net = float(getattr(agg, "vpn_net_profit_rub", 0) or 0)
    stars_net = float(getattr(agg, "stars_net_profit_rub", 0) or 0)
    prem_net = float(getattr(agg, "premium_net_profit_rub", 0) or 0)
    rate = float(usd_rub_rate or 0)
    net_s = format_money_rub_usdt(rub=gross, usd_rub_rate=rate)

    lines = [
        "👑 <b>Ai Monkey Stars</b>",
        f"📅 Период: <b>{esc(period_label_s)}</b>",
        "",
        "💰 <b>Финансы</b>",
        f"💰 Выручка: <b>{esc(f'{agg.revenue_rub:.2f}')} ₽</b>",
        f"💳 Комиссии: <b>{esc(f'{fees:.2f}')} ₽</b>",
        f"📈 Чистая прибыль: <b>{esc(net_s)}</b>",
    ]
    delta_line = format_delta_line(revenue_pct=delta_revenue_pct, net_pct=delta_net_pct)
    if delta_line:
        lines.append(delta_line)
    if float(rent_monthly_rub or 0) > 0.009:
        lines.append(
            f"🏢 После аренды (оценка): <b>{esc(f'{after_rent:.2f}')} ₽</b> "
            f"<i>(−{esc(f'{rent_period_rub:.2f}')} ₽ за период)</i>"
        )
    if pending_fulfill_count > 0:
        lines.append(
            f"⏳ В ожидании: <b>{esc(f'{pending_fulfill_rub:.2f}')} ₽</b> "
            f"({esc(str(pending_fulfill_count))} зак.) — прибыль ещё не посчитана"
        )
    else:
        lines.append("⏳ В ожидании: <b>0</b> — всё посчитано")

    lines.extend(
        [
            "",
            f"🌐 VPN: <b>{esc(f'{vpn_net:.2f}')} ₽</b> прибыли · "
            f"{esc(str(agg.vpn_units_sold))} · {esc(f'{agg.vpn_revenue_rub:.2f}')} ₽ выр.",
            f"⭐ Stars: <b>{esc(f'{stars_net:.2f}')} ₽</b> прибыли · "
            f"{esc(str(agg.stars_units_sold))} · {esc(f'{agg.stars_revenue_rub:.2f}')} ₽ выр.",
            f"💎 Premium: <b>{esc(f'{prem_net:.2f}')} ₽</b> прибыли · "
            f"{esc(str(agg.premium_units_sold))} · {esc(f'{agg.premium_revenue_rub:.2f}')} ₽ выр.",
            "",
            "🌐 <b>VPN сейчас</b> <i>(оплаченные подписки)</i>",
            f"🟢 Активных: <b>{esc(str(active))}</b>",
            f"🔴 Истекли: <b>{esc(str(expired))}</b>",
            f"👥 Всего paid: <code>{esc(str(total_acc))}</code>",
            "",
            "🤝 <b>Рефералы</b>",
            f"👥 С выданными: <b>{esc(str(referrers))}</b>",
            f"💰 Начислено бонусов: <b>{esc(f'{ref_bonus:.2f}')} ₽</b>",
            "",
            format_attention_block(
                pending_payment=pending_payment,
                vpn_ending_hint=expired,
                withdraw_pending=withdraw_pending,
                vpn_status=vpn_status,
            ),
        ]
    )
    return "\n".join(lines)


def format_finance_hub(
    *,
    period_label_s: str,
    agg: DashboardAgg,
    pending_fulfill_count: int = 0,
    pending_fulfill_rub: float = 0.0,
    rent_monthly_rub: float = 0.0,
    rent_period_rub: float = 0.0,
    fee_lava_card: float = 6.0,
    fee_sbp: float = 3.4,
    fee_crypto: float = 3.0,
    fee_xrocket: float = 1.5,
    fragment_star: float = 0.015,
    fragment_1m: float = 0.0,
    fragment_3m: float = 11.99,
    fragment_6m: float = 15.99,
    fragment_12m: float = 28.99,
    delta_revenue_pct: float | None = None,
    delta_net_pct: float | None = None,
    override_keys: set[str] | frozenset[str] | None = None,
    usd_rub_rate: float = 0.0,
    kind_label_s: str = "Все",
) -> str:
    """💳 Финансы — те же KPI + настройки + команды (F8: edit via /admin_fin_set)."""
    gross = float(agg.net_profit_rub or 0)
    fees = float(getattr(agg, "fees_rub", 0) or 0)
    after_rent = round(gross - float(rent_period_rub or 0), 2)
    vpn_net = float(getattr(agg, "vpn_net_profit_rub", 0) or 0)
    stars_net = float(getattr(agg, "stars_net_profit_rub", 0) or 0)
    prem_net = float(getattr(agg, "premium_net_profit_rub", 0) or 0)
    ov = {str(k).strip().lower() for k in (override_keys or ())}
    rate = float(usd_rub_rate or 0)
    net_s = format_money_rub_usdt(rub=gross, usd_rub_rate=rate)

    def _mark(key: str) -> str:
        return " ✎" if key in ov else ""

    lines = [
        "💳 <b>Финансы</b>",
        f"📅 Период: <b>{esc(period_label_s)}</b> · 📦 <b>{esc(kind_label_s)}</b>",
        "",
        f"💰 Выручка: <b>{esc(f'{agg.revenue_rub:.2f}')} ₽</b>",
        f"💳 Комиссии: <b>{esc(f'{fees:.2f}')} ₽</b>",
        f"📈 Чистая прибыль: <b>{esc(net_s)}</b>",
    ]
    delta_line = format_delta_line(revenue_pct=delta_revenue_pct, net_pct=delta_net_pct)
    if delta_line:
        lines.append(delta_line)
    if float(rent_monthly_rub or 0) > 0.009:
        lines.append(
            f"🏢 После аренды (оценка): <b>{esc(f'{after_rent:.2f}')} ₽</b>"
        )
    if pending_fulfill_count > 0:
        lines.append(
            f"⏳ В ожидании: <b>{esc(f'{pending_fulfill_rub:.2f}')} ₽</b> "
            f"({esc(str(pending_fulfill_count))}) — прибыль ещё не посчитана"
        )
    prem_1m_line = (
        f"💎 1м: <b>не задано (TBD)</b>{_mark('fragment_1m')}"
        if float(fragment_1m or 0) <= 0.000001
        else f"💎 1м: <b>{esc(f'{fragment_1m:g}')}</b> USDT{_mark('fragment_1m')}"
    )
    lines.extend(
        [
            "",
            f"🌐 VPN: <b>{esc(f'{vpn_net:.2f}')} ₽</b> прибыли",
            f"⭐ Stars: <b>{esc(f'{stars_net:.2f}')} ₽</b> прибыли",
            f"💎 Premium: <b>{esc(f'{prem_net:.2f}')} ₽</b> прибыли",
            "",
            "⚙️ <b>Комиссии (настройки)</b>",
            f"🏦 Банк/Lava: <b>{esc(f'{fee_lava_card:g}')}%</b>{_mark('fee_lava_card')}",
            f"📲 СБП: <b>{esc(f'{fee_sbp:g}')}%</b>{_mark('fee_sbp')}",
            f"🪙 Crypto Bot: <b>{esc(f'{fee_crypto:g}')}%</b>{_mark('fee_crypto')}",
            f"🪙 Xrocket: <b>{esc(f'{fee_xrocket:g}')}%</b>{_mark('fee_xrocket')}",
            "🌐 VPN: без вычета комиссии (вся сумма в чистую)",
            "",
            "⚙️ <b>Fragment (закуп USDT)</b>",
            f"⭐ 1★: <b>{esc(f'{fragment_star:g}')}</b> USDT{_mark('fragment_star')}",
            prem_1m_line,
            f"💎 3м: <b>{esc(f'{fragment_3m:g}')}</b> · 6м: <b>{esc(f'{fragment_6m:g}')}</b> · "
            f"12м: <b>{esc(f'{fragment_12m:g}')}</b>",
            "",
            "<i>Fragment USDT — только админ (закуп). Пользователю не показываем.</i>",
            "<i>✎ = override в БД (новые заказы). Старые snapshot не двигаются.</i>",
            "<i>Команды:</i> <code>/admin_fin_set</code> · <code>/admin_fin_show</code> · "
            "<code>/admin_cogs</code> · <code>/admin_recalc_profit</code>",
        ]
    )
    return "\n".join(lines)


def hub_keyboard(*, period_token: str = "7") -> InlineKeyboardMarkup:
    """Main admin hub (ТЗ §4)."""
    p = period_token
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 Сегодня", callback_data="aux:d:today"),
                InlineKeyboardButton(text="7 дней", callback_data="aux:d:7"),
            ],
            [
                InlineKeyboardButton(text="30 дней", callback_data="aux:d:30"),
                InlineKeyboardButton(text="Всё время", callback_data="aux:d:all"),
            ],
            [
                InlineKeyboardButton(text="📈 С запуска", callback_data="aux:d:start"),
            ],
            [
                InlineKeyboardButton(text="💰 Продажи", callback_data=f"aux:sales:{p}"),
                InlineKeyboardButton(text="👥 Пользователи", callback_data=f"aux:users:{p}"),
            ],
            [
                InlineKeyboardButton(text="🌐 VPN", callback_data=f"aux:vpn:{p}"),
                InlineKeyboardButton(text="🤝 Рефералы", callback_data=f"aux:ref:{p}"),
            ],
            [
                InlineKeyboardButton(text="👻 Bridge зомби", callback_data="ast:vpn_zombies"),
                InlineKeyboardButton(text="❤️ VPN health", callback_data="ast:vpn_health"),
            ],
            [
                InlineKeyboardButton(text="💳 Финансы", callback_data=f"aux:finance:{p}"),
                InlineKeyboardButton(text="🎁 Промо", callback_data=f"aux:promo:{p}"),
            ],
            [
                InlineKeyboardButton(text="🏆 Конкурсы", callback_data=f"aux:contest:{p}"),
                InlineKeyboardButton(text="📢 Маркетинг", callback_data=f"aux:mkt:{p}"),
            ],
            [
                InlineKeyboardButton(text="📊 Статистика", callback_data=f"aux:stats:{p}"),
                InlineKeyboardButton(text="🛠 Система", callback_data=f"aux:sys:{p}"),
            ],
            [
                InlineKeyboardButton(text="📤 Экспорт", callback_data=f"aux:export:{p}"),
                InlineKeyboardButton(text="⚙️ Настройки", callback_data=f"aux:settings:{p}"),
            ],
            [
                InlineKeyboardButton(text="🚨 Проблемы", callback_data=f"aux:attention:{p}"),
                InlineKeyboardButton(text="🔄 Обновить", callback_data=f"aux:d:{p}"),
            ],
            [
                InlineKeyboardButton(text="⏳ Кто в ожидании", callback_data=f"aux:pending:{p}"),
                InlineKeyboardButton(text="🔴 Кто истёк", callback_data=f"aux:expired_vpn:{p}"),
            ],
            [
                InlineKeyboardButton(
                    text="📋 Полный тех.отчёт (legacy)", callback_data=f"aux:legacy:{p}"
                ),
            ],
        ]
    )


def back_hub_kb(*, period_token: str = "7") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В админ-панель", callback_data=f"aux:d:{period_token}")],
        ]
    )


def finance_section_kb(
    *,
    period_token: str = "7",
    kind_token: str = "all",
) -> InlineKeyboardMarkup:
    """💳 Финансы — товар × период."""
    p = period_token or "7"
    k = kind_token or "all"

    def _pl(token: str, base: str) -> str:
        return f"· {base} ·" if token == p else base

    def _kl(token: str, base: str) -> str:
        return f"· {base} ·" if token == k else base

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_kl("all", "Все"),
                    callback_data=aux_cb("finance", p, "all"),
                ),
                InlineKeyboardButton(
                    text=_kl("vpn", "VPN"),
                    callback_data=aux_cb("finance", p, "vpn"),
                ),
                InlineKeyboardButton(
                    text=_kl("stars", "Stars"),
                    callback_data=aux_cb("finance", p, "stars"),
                ),
                InlineKeyboardButton(
                    text=_kl("premium", "Premium"),
                    callback_data=aux_cb("finance", p, "premium"),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_pl("today", "📅 Сегодня"),
                    callback_data=aux_cb("finance", "today", k),
                ),
                InlineKeyboardButton(
                    text=_pl("7", "7 дней"),
                    callback_data=aux_cb("finance", "7", k),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_pl("30", "30 дней"),
                    callback_data=aux_cb("finance", "30", k),
                ),
                InlineKeyboardButton(
                    text=_pl("all", "Всё время"),
                    callback_data=aux_cb("finance", "all", k),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_pl("start", "📈 С запуска"),
                    callback_data=aux_cb("finance", "start", k),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🤝 Выводы реф",
                    callback_data="aux:cmdrun:admin_ref_withdraw",
                ),
                InlineKeyboardButton(
                    text="🧮 Себестоимость",
                    callback_data="aux:cmdrun:admin_cogs",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="♻️ Пересчёт прибыли",
                    callback_data="aux:cmdrun:admin_recalc_profit",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⏳ Кто в ожидании",
                    callback_data=aux_cb("pending", p, k),
                ),
                InlineKeyboardButton(
                    text="🔴 Кто истёк",
                    callback_data=f"aux:expired_vpn:{p}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Комиссии / Fragment",
                    callback_data="aux:cmdrun:admin_fin_set",
                ),
            ],
            [InlineKeyboardButton(text="🔙 В админ-панель", callback_data=f"aux:d:{p}")],
        ]
    )


def section_hub_text(section: str) -> str:
    """Progressive hubs: point to existing commands (functions preserved)."""
    catalogs = {
        "users": (
            "👥 <b>Пользователи</b>\n\n"
            "Поиск: TG ID, @username, номер заказа, ник сайта, ref-ссылка.\n"
            "Команда: <code>/admin_user …</code>\n"
            "Ник сайта: <code>/admin_find_nick …</code>"
        ),
        "vpn": (
            "🌐 <b>VPN</b>\n\n"
            "❤️ Состояние (кратко) — кнопка ниже.\n"
            "🔧 Подробная диагностика: <code>/admin_vpn_health</code>\n\n"
            "Статус: <code>/admin_vpn_status &lt;tg_id&gt;</code>\n"
            "Устройства: <code>/admin_vpn_devices &lt;tg_id&gt;</code>\n"
            "Продлить: <code>/admin_vpn_extend …</code>\n"
            "Trial: <code>/admin_vpn_trial_status …</code>\n"
            "Сводка: <code>/admin_vpn</code>"
        ),
        "ref": (
            "🤝 <b>Рефералы</b>\n\n"
            "Партнёрка: <code>/admin_ref_partner</code>\n"
            "Выводы: <code>/admin_ref_withdraw</code>"
        ),
        "finance": (
            "💳 <b>Финансы</b>\n\n"
            "Себестоимость заказа: <code>/admin_cogs &lt;order_id&gt;</code>\n"
            "Пересчёт прибыли: <code>/admin_recalc_profit</code>\n"
            "Выводы реф: <code>/admin_ref_withdraw</code>\n"
            "Отчёт руководителю: в «Статистика» → полный отчёт.\n\n"
            "<i>Аренда на дашборде: VPN_RENT_MONTHLY_RUB (оценка, не в snapshot).</i>"
        ),
        "promo": "🎁 <b>Промокоды</b>\n\n<code>/admin_promo</code>",
        "contest": "🏆 <b>Конкурсы</b>\n\n<code>/contest</code>",
        "mkt": (
            "📢 <b>Маркетинг</b>\n\n"
            "Рассылка: <code>/admin_broadcast</code>\n"
            "Статистика рассылок: <code>/admin_broadcast_stats</code>\n"
            "Pin checkout: <code>/channel_checkout_pin</code>"
        ),
        "export": "📤 <b>Экспорт</b>\n\n<code>/admin_export</code>\nТакже CSV в полном отчёте (legacy).",
        "sys": (
            "🛠 <b>Система</b>\n\n"
            "🔧 Подробная диагностика VPN: <code>/admin_vpn_health</code>\n"
            "Справка команд: <code>/admin_help</code>\n"
            "Очередь: <code>/admqueue</code>\n"
            "Выдачи: <code>/admdeliveries</code>"
        ),
        "settings": (
            "⚙️ <b>Настройки</b>\n\n"
            "VPN notices: <code>/admin_vpn_notices</code>\n"
            "Announce: <code>/admin_vpn_announce</code>\n"
            "Справка: <code>/admin_help</code>\n\n"
            "<i>Бизнес-логика и env не меняются из этой панели.</i>"
        ),
        "attention": (
            "🚨 <b>Проблемы</b>\n\n"
            "• Оплаты: смотрите «Продажи» / последние заказы со статусом ожидания\n"
            "• VPN: <code>/admin_vpn_health</code>\n"
            "• Выводы: <code>/admin_ref_withdraw</code>"
        ),
    }
    return catalogs.get(section, "Раздел в разработке. /admin_help")


def format_sales_screen(
    *,
    period_label_s: str,
    agg: DashboardAgg,
    status_counts: dict[str, int] | None = None,
    kind_label_s: str = "Все",
) -> str:
    """💰 Продажи (ТЗ §7) — human KPI."""
    sc = status_counts or {}
    avg = (agg.revenue_rub / agg.orders_count) if agg.orders_count else 0.0
    paid_n = int(sc.get("paid", 0) or 0) + int(sc.get("processing", 0) or 0)
    done_n = int(sc.get("completed", 0) or 0)
    cancel_n = int(sc.get("cancelled", 0) or 0) + int(sc.get("expired", 0) or 0)
    pend_n = int(sc.get("pending_payment", 0) or 0)
    return "\n".join(
        [
            f"💰 <b>Продажи</b> · {esc(period_label_s)} · 📦 {esc(kind_label_s)}",
            "",
            f"💵 Выручка: <b>{esc(f'{agg.revenue_rub:.2f}')} ₽</b>",
            f"🛒 Оплачено/в работе: <b>{esc(str(agg.orders_count))}</b>",
            f"🧾 Средний чек: <b>{esc(f'{avg:.2f}')} ₽</b>",
            "",
            f"✅ Выдано: <b>{esc(str(done_n))}</b>",
            f"🟢 Оплачено (ещё не выдано): <b>{esc(str(paid_n))}</b>",
            f"⏳ Ждут оплаты: <b>{esc(str(pend_n))}</b>",
            f"🚫 Отмена/истёк: <b>{esc(str(cancel_n))}</b>",
            "",
            f"🌐 VPN — <b>{esc(str(agg.vpn_units_sold))}</b> · {esc(f'{agg.vpn_revenue_rub:.2f}')} ₽",
            f"⭐ Stars — <b>{esc(str(agg.stars_units_sold))}</b> · {esc(f'{agg.stars_revenue_rub:.2f}')} ₽",
            f"💎 Premium — <b>{esc(str(agg.premium_units_sold))}</b> · {esc(f'{agg.premium_revenue_rub:.2f}')} ₽",
        ]
    )


def sales_section_kb(*, period_token: str = "7", kind_token: str = "all") -> InlineKeyboardMarkup:
    p = period_token or "7"
    k = kind_token or "all"
    if p in ("all", "start"):
        top_cb = "ast:top:30"
        dyn_cb = "ast:dyn:14"
    elif p == "today":
        top_cb = "ast:top:7"
        dyn_cb = "ast:dyn:7"
    else:
        d = p if p.isdigit() else "7"
        top_cb = f"ast:top:{d}"
        dyn_cb = f"ast:dyn:{d}" if d != "1" else "ast:dyn:7"

    def _kl(token: str, base: str) -> str:
        return f"· {base} ·" if token == k else base

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_kl("all", "Все"), callback_data=aux_cb("sales", p, "all")),
                InlineKeyboardButton(text=_kl("vpn", "VPN"), callback_data=aux_cb("sales", p, "vpn")),
                InlineKeyboardButton(text=_kl("stars", "Stars"), callback_data=aux_cb("sales", p, "stars")),
                InlineKeyboardButton(
                    text=_kl("premium", "Premium"),
                    callback_data=aux_cb("sales", p, "premium"),
                ),
            ],
            [
                InlineKeyboardButton(text="📦 Последние заказы", callback_data=f"aux:orders:{p}"),
                InlineKeyboardButton(text="🔎 Найти заказ", callback_data=f"aux:find_order:{p}"),
            ],
            [
                InlineKeyboardButton(text="📊 По товарам", callback_data=top_cb),
                InlineKeyboardButton(text="📈 Динамика", callback_data=dyn_cb),
            ],
            [
                InlineKeyboardButton(text="⏳ Очередь", callback_data="aux:cmdrun:admqueue"),
                InlineKeyboardButton(text="📤 Выдачи", callback_data="aux:cmdrun:admdeliveries"),
            ],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"aux:d:{p}")],
        ]
    )


def orders_list_kb(
    order_ids: list[int],
    *,
    period_token: str = "7",
    back_callback: str | None = None,
) -> InlineKeyboardMarkup:
    p = period_token or "7"
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for oid in order_ids[:12]:
        row.append(
            InlineKeyboardButton(text=f"#{oid}", callback_data=f"aux:order:{oid}:{p}")
        )
        if len(row) >= 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    back = back_callback or f"aux:sales:{p}"
    back_label = "🔙 Назад"
    if back.startswith("aux:sales"):
        back_label = "🔙 К продажам"
    elif back.startswith("aux:finance"):
        back_label = "🔙 К финансам"
    elif back.startswith("aux:d:"):
        back_label = "🔙 В админ-панель"
    rows.append([InlineKeyboardButton(text=back_label, callback_data=back)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def format_pending_fulfillment_list(
    rows: list[dict[str, Any]],
    *,
    period_label_s: str,
    total_rub: float | None = None,
) -> str:
    lines = [
        "⏳ <b>В ожидании</b>",
        f"📅 {esc(period_label_s)}",
        "<i>paid/processing — прибыли нет, пока не «Выдан».</i>",
        "",
    ]
    if not rows:
        lines.append("<i>Пусто — всё закрыто.</i>")
        return "\n".join(lines)
    s = float(total_rub) if total_rub is not None else sum(
        float(r.get("rub_after_discounts") or 0) for r in rows
    )
    lines.append(f"Итого: <b>{esc(f'{s:.2f}')} ₽</b> · {esc(str(len(rows)))} зак.")
    lines.append("")
    for r in rows[:25]:
        oid = int(r.get("id") or 0)
        kind = esc(str(r.get("product_kind") or ""))
        st = esc(str(r.get("status") or ""))
        title = esc(str(r.get("product_title") or "")[:40])
        amt = float(r.get("rub_after_discounts") or 0)
        note = esc(str(r.get("user_note") or "")[:28])
        lab = " 🧪" if r.get("is_lab") else ""
        err = str(r.get("fulfillment_last_error") or "").strip()
        err_s = f" · err <code>{esc(err[:40])}</code>" if err else ""
        lines.append(
            f"#{esc(str(oid))}{lab} · <code>{st}</code> · {kind}\n"
            f"  {title} · <b>{esc(f'{amt:.2f}')} ₽</b>\n"
            f"  <code>{note or '—'}</code>{err_s}"
        )
    lines.append("\nНажмите номер → карточка (Finalize / Выдан).")
    return "\n".join(lines)


def format_expired_vpn_list(rows: list[dict[str, Any]]) -> str:
    lines = [
        "🔴 <b>Истекли (VPN paid)</b>",
        "<i>без lab 9900* / friend-seed 9901*.</i>",
        "",
    ]
    if not rows:
        lines.append("<i>Нет истёкших paid (или vpn.db недоступна).</i>")
        return "\n".join(lines)
    for r in rows[:25]:
        tid = int(r.get("telegram_user_id") or 0)
        until = esc(str(r.get("paid_until") or "")[:19])
        aid = int(r.get("id") or 0)
        lines.append(
            f"tg <code>{esc(str(tid))}</code> · до <code>{until}</code> · acct #{esc(str(aid))}"
        )
    lines.append("\nСтатус юзера: <code>/admin_vpn_status TID</code>")
    return "\n".join(lines)


def expired_vpn_list_kb(
    tids: list[int],
    *,
    period_token: str = "7",
) -> InlineKeyboardMarkup:
    p = period_token or "7"
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for tid in tids[:12]:
        row.append(
            InlineKeyboardButton(
                text=str(tid)[-6:],
                callback_data=f"aux:user:{int(tid)}:{p}",
            )
        )
        if len(row) >= 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append(
        [InlineKeyboardButton(text="🔙 В админ-панель", callback_data=f"aux:d:{p}")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def order_card_back_kb(
    *,
    period_token: str = "7",
    user_id: int | None = None,
) -> InlineKeyboardMarkup:
    """Navigation under order actions — merge with admin_order_kb."""
    p = period_token or "7"
    rows: list[list[InlineKeyboardButton]] = []
    if user_id is not None:
        rows.append(
            [
                InlineKeyboardButton(
                    text="👤 Пользователь",
                    callback_data=f"aux:user:{int(user_id)}:{p}",
                )
            ]
        )
    rows.append(
        [InlineKeyboardButton(text="📦 К списку заказов", callback_data=f"aux:orders:{p}")]
    )
    rows.append(
        [InlineKeyboardButton(text="🔙 К продажам", callback_data=f"aux:sales:{p}")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def merge_inline_kb(*kbs: InlineKeyboardMarkup) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for kb in kbs:
        rows.extend(list(kb.inline_keyboard or []))
    return InlineKeyboardMarkup(inline_keyboard=rows)


def users_section_kb(*, period_token: str = "7") -> InlineKeyboardMarkup:
    p = period_token or "7"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔎 Найти", callback_data=f"aux:find_user:{p}"),
            ],
            [
                InlineKeyboardButton(
                    text="🌐 VPN статус",
                    callback_data="aux:cmdrun:admin_vpn_status",
                ),
                InlineKeyboardButton(
                    text="📱 Устройства",
                    callback_data="aux:cmdrun:admin_vpn_devices",
                ),
            ],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"aux:d:{p}")],
        ]
    )


def format_users_hub() -> str:
    return "\n".join(
        [
            "👥 <b>Пользователи</b>",
            "",
            "Поиск: TG ID, @username, #заказ, ник сайта, ref-ссылка.",
            "",
            "Команда: <code>/admin_user 123456789</code>",
            "или <code>/admin_user @nick</code> · <code>/admin_user #104</code>",
            "",
            "Ник сайта: <code>/admin_find_nick …</code>",
        ]
    )


def format_ref_hub(
    *,
    period_label_s: str,
    rm: dict[str, Any],
    vpn_rm: dict[str, Any] | None = None,
    top_refs: list[Any] | None = None,
    available_bonus_rub: float = 0.0,
    withdraw_pending_count: int = 0,
    withdraw_pending_rub: float = 0.0,
    cfg_referrer_days: int = 0,
    cfg_friend_days: int = 0,
) -> str:
    """🤝 Рефералы human (ТЗ §12)."""
    vpn_rm = vpn_rm or {}
    bonus = float(rm.get("total_referral_bonus_rub", 0) or 0)
    with_disc = int(rm.get("orders_with_ref_discount", 0) or 0)
    ref_users = int(vpn_rm.get("vpn_ref_distinct_referrers", 0) or 0)
    sum_ref_days = int(vpn_rm.get("vpn_ref_referrer_days", 0) or 0)
    sum_friend_days = int(vpn_rm.get("vpn_ref_friend_days", 0) or 0)
    n_grants = int(vpn_rm.get("vpn_ref_grants", 0) or 0)
    lines = [
        "🤝 <b>Рефералы</b>",
        f"📅 Период: <b>{esc(period_label_s)}</b>",
        "",
        f"💰 Начислено бонусов: <b>{esc(f'{bonus:.2f}')} ₽</b>",
        f"🎁 Доступно к выводу (балансы): <b>{esc(f'{available_bonus_rub:.2f}')} ₽</b>",
        f"⏳ Заявки на вывод: <b>{esc(str(withdraw_pending_count))}</b>"
        f" · {esc(f'{withdraw_pending_rub:.2f}')} ₽",
        f"🛒 Заказов со скидкой реф: <b>{esc(str(with_disc))}</b>",
        "",
        "🌐 <b>VPN-рефералка</b>",
        f"Грантов: <b>{esc(str(n_grants))}</b> · рефереров: <b>{esc(str(ref_users))}</b>",
        f"Дней реферерам: <b>{esc(str(sum_ref_days))}</b>"
        f" · друзьям: <b>{esc(str(sum_friend_days))}</b>",
    ]
    if cfg_referrer_days or cfg_friend_days:
        lines.append(
            f"Настройки: реферер +{esc(str(cfg_referrer_days))}д · "
            f"друг +{esc(str(cfg_friend_days))}д"
        )
    if top_refs:
        lines.append("")
        lines.append("🏆 <b>Топ рефереров</b>")
        for i, r in enumerate(top_refs[:5], 1):
            try:
                rid = int(r["rid"])
                bonus_r = float(r["bonus_rub"] or 0)
                n = int(r["orders_n"] or 0)
            except (KeyError, TypeError, ValueError):
                continue
            lines.append(
                f"{i}. <code>{esc(str(rid))}</code> — "
                f"<b>{esc(f'{bonus_r:.2f}')} ₽</b> ({esc(str(n))} зак.)"
            )
    return "\n".join(lines)


def ref_section_kb(*, period_token: str = "7") -> InlineKeyboardMarkup:
    p = period_token or "7"

    def _lbl(token: str, base: str) -> str:
        return f"· {base} ·" if token == p else base

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_lbl("today", "📅 Сегодня"), callback_data="aux:ref:today"),
                InlineKeyboardButton(text=_lbl("7", "7 дней"), callback_data="aux:ref:7"),
            ],
            [
                InlineKeyboardButton(text=_lbl("30", "30 дней"), callback_data="aux:ref:30"),
                InlineKeyboardButton(text=_lbl("all", "Всё время"), callback_data="aux:ref:all"),
            ],
            [
                InlineKeyboardButton(text=_lbl("start", "📈 С запуска"), callback_data="aux:ref:start"),
            ],
            [
                InlineKeyboardButton(text="💳 Выводы", callback_data=f"aux:withdraw:{p}"),
                InlineKeyboardButton(
                    text="👤 Партнёр",
                    callback_data="aux:cmdrun:admin_ref_partner",
                ),
            ],
            [
                InlineKeyboardButton(text="🔎 Найти пользователя", callback_data=f"aux:find_user:{p}"),
            ],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"aux:d:{p}")],
        ]
    )


def format_withdraw_hub(*, summary: dict[str, Any]) -> str:
    pend_n = int(summary.get("pending_count", 0) or 0)
    pend_rub = float(summary.get("pending_rub", 0) or 0)
    paid_n = int(summary.get("paid_count", 0) or 0)
    paid_rub = float(summary.get("paid_rub", 0) or 0)
    rej_n = int(summary.get("rejected_count", 0) or 0)
    return "\n".join(
        [
            "💳 <b>Выводы рефералов</b>",
            "",
            f"⏳ Ожидают: <b>{esc(str(pend_n))}</b> · {esc(f'{pend_rub:.2f}')} ₽",
            f"✅ Выплачено: <b>{esc(str(paid_n))}</b> · {esc(f'{paid_rub:.2f}')} ₽",
            f"🚫 Отклонено: <b>{esc(str(rej_n))}</b>",
            "",
            "Оплата/отклонение: <code>/admin_ref_withdraw paid ID</code>",
            "<code>/admin_ref_withdraw reject ID [причина]</code>",
        ]
    )


def withdraw_section_kb(*, period_token: str = "7") -> InlineKeyboardMarkup:
    p = period_token or "7"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⏳ Заявки", callback_data=f"aux:withdraw_list:pending:{p}"),
                InlineKeyboardButton(
                    text="✅ Выплаченные", callback_data=f"aux:withdraw_list:paid:{p}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📋 Команда list",
                    callback_data="aux:cmdrun:admin_ref_withdraw",
                ),
            ],
            [
                InlineKeyboardButton(text="🔙 К рефералам", callback_data=f"aux:ref:{p}"),
                InlineKeyboardButton(text="🏠 В панель", callback_data=f"aux:d:{p}"),
            ],
        ]
    )


def format_promo_hub(*, active_n: int, total_n: int, preview_lines: list[str] | None = None) -> str:
    lines = [
        "🎁 <b>Промокоды</b>",
        "",
        f"Активных: <b>{esc(str(active_n))}</b> · всего: <b>{esc(str(total_n))}</b>",
    ]
    if preview_lines:
        lines.append("")
        lines.append("<b>Последние:</b>")
        lines.extend(preview_lines[:8])
    lines.extend(
        [
            "",
            "Создать / вкл / выкл — команда:",
            "<code>/admin_promo</code> · <code>/admin_promo list</code>",
        ]
    )
    return "\n".join(lines)


def promo_section_kb(*, period_token: str = "7") -> InlineKeyboardMarkup:
    p = period_token or "7"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 Список", callback_data=f"aux:promo_list:{p}"),
                InlineKeyboardButton(
                    text="➕ Создать",
                    callback_data="aux:cmdrun:admin_promo",
                ),
            ],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"aux:d:{p}")],
        ]
    )


def format_contest_hub(*, active_title: str | None, total_n: int, preview_lines: list[str] | None = None) -> str:
    cur = active_title or "нет активного"
    lines = [
        "🏆 <b>Конкурсы</b>",
        "",
        f"Сейчас: <b>{esc(cur)}</b>",
        f"Всего записей: <b>{esc(str(total_n))}</b>",
    ]
    if preview_lines:
        lines.append("")
        lines.append("<b>Последние:</b>")
        lines.extend(preview_lines[:8])
    lines.extend(
        [
            "",
            "Управление: <code>/contest</code> · <code>/contest list</code>",
        ]
    )
    return "\n".join(lines)


def contest_section_kb(*, period_token: str = "7") -> InlineKeyboardMarkup:
    p = period_token or "7"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 Список", callback_data=f"aux:contest_list:{p}"),
                InlineKeyboardButton(text="ℹ️ Справка", callback_data="aux:cmdrun:contest"),
            ],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"aux:d:{p}")],
        ]
    )


def format_mkt_hub(*, acq: dict[str, Any] | None = None, period_label_s: str = "7 дней") -> str:
    lines = [
        "📢 <b>Маркетинг</b>",
        f"📅 Период метрик: <b>{esc(period_label_s)}</b>",
        "",
        "Рассылка акций: <code>/admin_broadcast</code>",
        "Стата рассылки: <code>/admin_broadcast_stats</code>",
        "Pin checkout в канал: <code>/channel_checkout_pin</code>",
    ]
    if acq:
        spend = float(acq.get("acq_spend_rub", 0) or 0)
        paid_u = int(acq.get("acq_paid_users", 0) or 0)
        cac = float(acq.get("acq_cac_rub", 0) or 0)
        lines.extend(
            [
                "",
                "📈 <b>Привлечение (human)</b>",
                f"Spend: <b>{esc(f'{spend:.2f}')} ₽</b>",
                f"Платящих юзеров: <b>{esc(str(paid_u))}</b>",
                f"CAC: <b>{esc(f'{cac:.2f}')} ₽</b>",
            ]
        )
    return "\n".join(lines)


def mkt_section_kb(*, period_token: str = "7") -> InlineKeyboardMarkup:
    p = period_token or "7"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📣 Рассылка",
                    callback_data="aux:cmdrun:admin_broadcast",
                ),
                InlineKeyboardButton(
                    text="📊 Стата",
                    callback_data="aux:cmdrun:admin_broadcast_stats",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📌 Pin checkout",
                    callback_data="aux:cmdrun:channel_checkout_pin",
                ),
            ],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"aux:d:{p}")],
        ]
    )


def format_export_hub() -> str:
    return "\n".join(
        [
            "📤 <b>Экспорт</b>",
            "",
            "CSV выданных заказов — кнопки ниже.",
            "Или команда: <code>/admin_export 30</code> · <code>/admin_export all</code>",
            "",
            "Дополнительно CSV — в полном тех.отчёте (legacy).",
        ]
    )


def export_section_kb(*, period_token: str = "7") -> InlineKeyboardMarkup:
    p = period_token or "7"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="CSV 7д", callback_data="aux:export_run:7"),
                InlineKeyboardButton(text="CSV 30д", callback_data="aux:export_run:30"),
            ],
            [
                InlineKeyboardButton(text="CSV всё", callback_data="aux:export_run:all"),
                InlineKeyboardButton(text="CSV (legacy)", callback_data="ast:csv:30"),
            ],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"aux:d:{p}")],
        ]
    )


def format_sys_hub() -> str:
    return "\n".join(
        [
            "🛠 <b>Система</b>",
            "",
            "🔧 Подробная диагностика VPN — кнопка ниже.",
            "❤️ Краткое состояние — в разделе VPN.",
            "",
            "Очередь внимания: <code>/admqueue</code>",
            "Последние выдачи: <code>/admdeliveries</code>",
            "Справка команд: <code>/admin_help</code>",
        ]
    )


def sys_section_kb(*, period_token: str = "7") -> InlineKeyboardMarkup:
    p = period_token or "7"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔧 Подробная диагностика VPN",
                    callback_data="ast:vpn_health",
                ),
            ],
            [
                InlineKeyboardButton(text="⏳ Очередь", callback_data="aux:cmdrun:admqueue"),
                InlineKeyboardButton(
                    text="📤 Выдачи", callback_data="aux:cmdrun:admdeliveries"
                ),
            ],
            [
                InlineKeyboardButton(text="ℹ️ Справка", callback_data="aux:cmdrun:admin_help"),
            ],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"aux:d:{p}")],
        ]
    )


def format_settings_hub() -> str:
    return "\n".join(
        [
            "⚙️ <b>Настройки</b>",
            "",
            "VPN notices: <code>/admin_vpn_notices</code>",
            "Announce: <code>/admin_vpn_announce</code>",
            "FIN fee/Fragment: <code>/admin_fin_show</code> · <code>/admin_fin_set</code>",
            "Справка: <code>/admin_help</code>",
            "",
            "<i>FIN overrides в БД (новые заказы). Env shared/.env — базовые значения.</i>",
        ]
    )


def settings_section_kb(*, period_token: str = "7") -> InlineKeyboardMarkup:
    p = period_token or "7"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔔 Notices",
                    callback_data="aux:cmdrun:admin_vpn_notices",
                ),
                InlineKeyboardButton(
                    text="📢 Announce",
                    callback_data="aux:cmdrun:admin_vpn_announce",
                ),
            ],
            [InlineKeyboardButton(text="ℹ️ Справка", callback_data="aux:cmdrun:admin_help")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"aux:d:{p}")],
        ]
    )


def format_attention_hub() -> str:
    return "\n".join(
        [
            "🚨 <b>Проблемы</b>",
            "",
            "• ⏳ Кто в ожидании — paid/processing без прибыли",
            "• 🔴 Кто истёк — VPN paid_until",
            "• Оплаты / заказы — «Продажи» → последние заказы",
            "• Очередь внимания: <code>/admqueue</code>",
            "• VPN: раздел VPN → ❤️ / 🔧",
            "• Выводы: Рефералы → Выводы",
        ]
    )


def attention_section_kb(*, period_token: str = "7") -> InlineKeyboardMarkup:
    p = period_token or "7"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💰 Продажи", callback_data=f"aux:sales:{p}"),
                InlineKeyboardButton(text="⏳ Очередь", callback_data="aux:cmdrun:admqueue"),
            ],
            [
                InlineKeyboardButton(text="⏳ Кто в ожидании", callback_data=f"aux:pending:{p}"),
                InlineKeyboardButton(text="🔴 Кто истёк", callback_data=f"aux:expired_vpn:{p}"),
            ],
            [
                InlineKeyboardButton(text="🌐 VPN", callback_data=f"aux:vpn:{p}"),
                InlineKeyboardButton(text="💳 Выводы", callback_data=f"aux:withdraw:{p}"),
            ],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"aux:d:{p}")],
        ]
    )


def format_user_card(
    *,
    user_id: int,
    username: str | None,
    first_name: str | None,
    created_at: str | None,
    referrer_id: int | None,
    stats: dict[str, Any],
    products: dict[str, Any],
    vpn_status: str | None = None,
    vpn_until: str | None = None,
    vpn_kind: str | None = None,
) -> str:
    un = f"@{username}" if username else "—"
    name = first_name or "—"
    vpn_line = "нет аккаунта"
    if vpn_status:
        kind = f" · {vpn_kind}" if vpn_kind else ""
        until = f" до {vpn_until}" if vpn_until else ""
        vpn_line = f"{vpn_status}{until}{kind}"
    spent = float(stats.get("spent_rub", 0) or 0)
    completed = int(stats.get("completed_orders", 0) or 0)
    open_n = int(products.get("open_orders", 0) or 0)
    ref_bal = float(stats.get("ref_balance_rub", 0) or 0)
    bal = float(stats.get("balance_rub", 0) or 0)
    vpn_n = int(products.get("vpn_units", 0) or 0)
    vpn_rub = float(products.get("vpn_rub", 0) or 0)
    stars_n = int(products.get("stars_units", 0) or 0)
    stars_rub = float(products.get("stars_rub", 0) or 0)
    prem_n = int(products.get("premium_units", 0) or 0)
    prem_rub = float(products.get("premium_rub", 0) or 0)
    invited = int(stats.get("referral_invited_count", 0) or 0)
    buyers = int(stats.get("referral_buyers_completed_count", 0) or 0)
    comm = float(stats.get("referral_commission_earned_rub", 0) or 0)
    return "\n".join(
        [
            f"👤 <b>Пользователь</b> <code>{esc(str(user_id))}</code>",
            f"{esc(name)} · {esc(un)}",
            f"📅 Регистрация: <b>{esc(created_at or '—')}</b>",
            f"🔗 Реферер: <code>{esc(str(referrer_id) if referrer_id else '—')}</code>",
            "",
            f"💵 Потрачено: <b>{esc(f'{spent:.2f}')} ₽</b>",
            f"🛒 Заказов выдано: <b>{esc(str(completed))}</b>"
            f" · в работе: <b>{esc(str(open_n))}</b>",
            f"🎁 Бонус: <b>{esc(f'{ref_bal:.2f}')} ₽</b>"
            f" · баланс: <b>{esc(f'{bal:.2f}')} ₽</b>",
            "",
            f"🌐 VPN: <b>{esc(vpn_line)}</b>",
            f"   продано: <b>{esc(str(vpn_n))}</b> · {esc(f'{vpn_rub:.2f}')} ₽",
            f"⭐ Stars: <b>{esc(str(stars_n))}</b> · {esc(f'{stars_rub:.2f}')} ₽",
            f"💎 Premium: <b>{esc(str(prem_n))}</b> · {esc(f'{prem_rub:.2f}')} ₽",
            "",
            f"🤝 Приглашено: <b>{esc(str(invited))}</b>"
            f" · купили: <b>{esc(str(buyers))}</b>",
            f"   комиссия начислена: <b>{esc(f'{comm:.2f}')} ₽</b>",
        ]
    )


def user_card_kb(*, user_id: int, period_token: str = "7") -> InlineKeyboardMarkup:
    p = period_token or "7"
    uid = int(user_id)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📦 Заказы",
                    callback_data=f"aux:user_orders:{uid}:{p}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🌐 VPN статус",
                    callback_data=f"aux:user_vpn:{uid}:{p}",
                ),
                InlineKeyboardButton(
                    text="📱 Устройства",
                    callback_data="aux:cmdrun:admin_vpn_devices",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⏰ Продлить VPN",
                    callback_data="aux:cmdrun:admin_vpn_extend",
                ),
            ],
            [InlineKeyboardButton(text="🔙 К пользователям", callback_data=f"aux:users:{p}")],
            [InlineKeyboardButton(text="🏠 В панель", callback_data=f"aux:d:{p}")],
        ]
    )



def format_vpn_hub(
    *,
    period_label_s: str,
    vpn_status: str | None,
    vpn_cp: dict[str, Any] | None,
    vpn_units_sold: int = 0,
    vpn_revenue_rub: float = 0.0,
    vpn_net_profit_rub: float = 0.0,
) -> str:
    """🌐 VPN human hub (ТЗ §10) — без RTT/CF/swap."""
    vpn_cp = vpn_cp or {}
    active = int(
        vpn_cp.get(
            "vpn_cp_paid_accounts_vpn_active",
            vpn_cp.get("vpn_cp_accounts_vpn_active", 0),
        )
        or 0
    )
    expired = int(
        vpn_cp.get(
            "vpn_cp_paid_accounts_vpn_expired",
            vpn_cp.get("vpn_cp_accounts_vpn_expired", 0),
        )
        or 0
    )
    total = int(
        vpn_cp.get(
            "vpn_cp_paid_accounts_total",
            vpn_cp.get("vpn_cp_accounts_total", 0),
        )
        or 0
    )
    pending_jobs = int(vpn_cp.get("vpn_cp_jobs_pending", 0) or 0)
    failed_jobs = int(vpn_cp.get("vpn_cp_jobs_failed", 0) or 0)
    icon = {"ok": "🟢", "degraded": "🟡", "critical": "🔴"}.get(
        (vpn_status or "").lower(), "⚪"
    )
    service = {
        "ok": "Сервис работает",
        "degraded": "Есть предупреждения",
        "critical": "Критично",
    }.get((vpn_status or "").lower(), vpn_status or "н/д")
    lines = [
        "🌐 <b>VPN</b>",
        f"📅 Период продаж: <b>{esc(period_label_s)}</b>",
        "",
        f"{icon} <b>{esc(service)}</b>",
        "",
        "👥 <b>Подписки (оплаченные)</b>",
        f"Всего: <b>{esc(str(total))}</b>",
        f"Активных: <b>{esc(str(active))}</b>",
        f"Истекли: <b>{esc(str(expired))}</b>",
        "",
        f"🛒 Продано за период: <b>{esc(str(vpn_units_sold))}</b>"
        f" · {esc(f'{vpn_revenue_rub:.2f}')} ₽",
        f"📈 Прибыль VPN: <b>{esc(f'{vpn_net_profit_rub:.2f}')} ₽</b>",
        "",
        f"⏳ Очередь выдачи: <b>{esc(str(pending_jobs))}</b>",
        f"⚠️ Ошибки jobs: <b>{esc(str(failed_jobs))}</b>",
    ]
    # Живые (оплач+trial) + зомби RU-bridge — без друзей/лаб.
    try:
        from bot.services.vpn_bridge_zombie_metrics import collect_bridge_zombie_metrics

        bm = collect_bridge_zombie_metrics()
        if bm.get("error") != "status_missing":
            paid = int(bm.get("active_paid_real") or 0)
            trial = int(bm.get("active_trial_real") or 0)
            za = int(bm.get("zombie_after") if bm.get("zombie_after") is not None else -1)
            total_pruned = int(bm.get("zombie_pruned_total") or 0)
            z_icon = "🟢" if za == 0 and not bm.get("stale") else "🔴"
            lines.extend(
                [
                    "",
                    f"{z_icon} <b>Bridge сейчас</b>",
                    f"Живые: <b>{esc(str(paid + trial))}</b>"
                    f" (оплач. {esc(str(paid))} + trial {esc(str(trial))})",
                    f"Зомби на bridge: <b>{esc(str(za))}</b>"
                    f" · отключено всего: <b>{esc(str(total_pruned))}</b>",
                ]
            )
            if bm.get("stale"):
                lines.append("⚠️ Отчёт bridge <b>STALE</b> — проверь cron guard")
    except Exception:
        pass
    return "\n".join(lines)


def vpn_section_kb(*, period_token: str = "7") -> InlineKeyboardMarkup:
    p = period_token or "7"

    def _lbl(token: str, base: str) -> str:
        return f"· {base} ·" if token == p else base

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_lbl("today", "📅 Сегодня"),
                    callback_data="aux:vpn:today",
                ),
                InlineKeyboardButton(
                    text=_lbl("7", "7 дней"),
                    callback_data="aux:vpn:7",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_lbl("30", "30 дней"),
                    callback_data="aux:vpn:30",
                ),
                InlineKeyboardButton(
                    text=_lbl("all", "Всё время"),
                    callback_data="aux:vpn:all",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_lbl("start", "📈 С запуска"),
                    callback_data="aux:vpn:start",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❤️ Состояние",
                    callback_data=f"aux:vpn_health_simple:{p}",
                ),
                InlineKeyboardButton(
                    text="🔧 Подробная диагностика",
                    callback_data="ast:vpn_health",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👻 Bridge зомби",
                    callback_data="ast:vpn_zombies",
                ),
                InlineKeyboardButton(
                    text="📋 /vpn_zombies",
                    callback_data="ast:vpn_zombies",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👤 Статус",
                    callback_data="aux:cmdrun:admin_vpn_status",
                ),
                InlineKeyboardButton(
                    text="📱 Устройства",
                    callback_data="aux:cmdrun:admin_vpn_devices",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⏰ Продлить",
                    callback_data="aux:cmdrun:admin_vpn_extend",
                ),
                InlineKeyboardButton(
                    text="🎁 Trial",
                    callback_data="aux:cmdrun:admin_vpn_trial_status",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔧 Finalize",
                    callback_data="aux:cmdrun:admin_vpn_finalize",
                ),
                InlineKeyboardButton(
                    text="🚫 Revoke",
                    callback_data="aux:cmdrun:admin_vpn_revoke",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ /admin_vpn",
                    callback_data="aux:cmdrun:admin_vpn",
                ),
                InlineKeyboardButton(
                    text="🔎 Найти пользователя",
                    callback_data=f"aux:find_user:{p}",
                ),
            ],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"aux:d:{p}")],
        ]
    )
