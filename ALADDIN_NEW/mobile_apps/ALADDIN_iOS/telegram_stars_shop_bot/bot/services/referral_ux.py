"""Тексты и клавиатуры реферального раздела (канон 2026-07-28)."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import Settings
from bot.services.ref_withdraw_repo import MIN_WITHDRAW_RUB
from bot.services.referral_partner import (
    QUALIFY_VPN_MIN_DAYS,
    WITHDRAW_MIN_QUALIFIED_VPN,
    WithdrawEligibility,
    eligibility_checklist_html,
    level_for_qualified_count,
    progress_to_next_level,
)
from bot.support_links import support_prefill_url
from bot.util_html import esc

PARTNER_VPN_THRESHOLD = WITHDRAW_MIN_QUALIFIED_VPN
PARTNER_MAX_PCT_HINT = 30


def _fmt_pct(v: float) -> str:
    x = float(v)
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return f"{x:.1f}".rstrip("0").rstrip(".")


def referral_home_html(
    *,
    ref_link: str,
    invited: int,
    buyers: int,
    earned_rub: float,
    settings: Settings,
    qualified_vpn: int = 0,
    level: dict | None = None,
    web_ref_link: str | None = None,
) -> str:
    lvl = level or level_for_qualified_count(qualified_vpn)
    vpn_pct = esc(_fmt_pct(float(lvl["vpn_first_percent"])))
    sp_pct = esc(_fmt_pct(float(lvl["stars_premium_percent"])))
    label = esc(str(lvl["label"]))
    vpn_days = max(0, int(settings.vpn_referral_referrer_days or 0))
    vpn_line = (
        f"📅 За нового пользователя с VPN — ещё <b>+{vpn_days} дн.</b> к вашей подписке.\n"
        if vpn_days > 0
        else ""
    )
    web = (web_ref_link or "").strip()
    links_block = (
        f"🔗 <b>Telegram:</b>\n<code>{esc(ref_link)}</code>\n"
        + (f"🌐 <b>Сайт (оплата без бота):</b>\n<code>{esc(web)}</code>\n" if web else "")
        + "\n"
    )
    return (
        "<b>👥 Пригласить друга</b>\n\n"
        f"🏆 <b>Уровень:</b> {label}\n"
        f"💯 <b>VPN</b> (первая покупка друга): <b>{vpn_pct}%</b>\n"
        f"⭐ <b>Stars и Premium</b> (каждая покупка): <b>{sp_pct}%</b>\n"
        f"{vpn_line}"
        "🎁 <b>Реферальный баланс:</b> VPN, Stars и Premium; "
        f"вывод от <b>{esc(f'{MIN_WITHDRAW_RUB:.0f}')} ₽</b> "
        "(карта или крипта).\n\n"
        "<b>Как это работает:</b>\n"
        "1️⃣ Отправьте ссылку другу (сайт или Telegram)\n"
        "2️⃣ Друг сделает покупку у нас\n"
        f"3️⃣ VPN — <b>{vpn_pct}%</b> один раз с первой покупки друга\n"
        f"4️⃣ Stars и Premium — <b>{sp_pct}%</b> с каждой выданной покупки"
        + (f"\n5️⃣ Плюс <b>+{vpn_days} дн.</b> VPN вам" if vpn_days > 0 else "")
        + "\n\n"
        f"{links_block}"
        f"📊 Приглашено: <b>{int(invited)}</b>\n"
        f"💳 С выданной покупкой: <b>{int(buyers)}</b>\n"
        f"🌐 VPN ≥{QUALIFY_VPN_MIN_DAYS} дн.: <b>{int(qualified_vpn)}</b>\n"
        f"🎁 Накоплено на реферальном: <b>{esc(f'{float(earned_rub):.2f}')} ₽</b>"
    )


def referral_stats_html(
    stats: dict[str, float | int],
    settings: Settings,
    *,
    qualified_vpn: int | None = None,
) -> str:
    invited = int(stats.get("referral_invited_count", 0) or 0)
    buyers = int(stats.get("referral_buyers_completed_count", 0) or 0)
    vpn_n = int(stats.get("referral_vpn_buyers_completed_count", 0) or 0)
    earned = float(stats.get("referral_commission_earned_rub", 0) or 0)
    bal = float(stats.get("ref_balance_rub", 0) or 0)
    q = int(qualified_vpn) if qualified_vpn is not None else vpn_n
    lvl = level_for_qualified_count(q)
    cur, need = progress_to_next_level(q)
    if need is None:
        prog = f"{cur} (максимум)"
    else:
        prog = f"{cur} → следующий с {need}"
    _ = settings
    return (
        "<b>📊 Моя статистика</b>\n\n"
        f"🏆 <b>Уровень:</b> {esc(str(lvl['label']))}\n"
        f"📈 <b>Прогресс:</b> {esc(prog)}\n"
        f"💯 <b>VPN</b> (1-я покупка друга): <b>{esc(_fmt_pct(float(lvl['vpn_first_percent'])))}%</b>\n"
        f"⭐ <b>Stars и Premium</b> (каждая): <b>{esc(_fmt_pct(float(lvl['stars_premium_percent'])))}%</b>\n\n"
        f"👥 Всего приглашено: <b>{invited}</b>\n"
        f"💳 С выданной покупкой: <b>{buyers}</b>\n"
        f"🌐 Любой VPN (выдано): <b>{vpn_n}</b>\n"
        f"🏅 VPN ≥{QUALIFY_VPN_MIN_DAYS} дн. (для уровня и вывода): <b>{q}</b>\n"
        f"💰 Накоплено всего: <b>{esc(f'{earned:.2f}')} ₽</b>\n"
        f"🎁 Сейчас на реферальном балансе: <b>{esc(f'{bal:.2f}')} ₽</b>"
    )


def referral_boost_html(stats: dict[str, float | int], *, qualified_vpn: int = 0) -> str:
    """Экран уровней: вертикально, как профиль; проценты без слэша (иначе Telegram делает команду)."""
    _ = stats
    q = int(qualified_vpn)
    lvl = level_for_qualified_count(q)
    _cur, need = progress_to_next_level(q)
    label = esc(str(lvl["label"]))
    vpn_pct = esc(_fmt_pct(float(lvl["vpn_first_percent"])))
    sp_pct = esc(_fmt_pct(float(lvl["stars_premium_percent"])))

    if need is None:
        progress_block = (
            f"📈 <b>Прогресс:</b> максимум достигнут\n"
            f"🏅 Друзей с VPN от {QUALIFY_VPN_MIN_DAYS} дн.: <b>{q}</b>\n"
        )
    else:
        left = need - q
        progress_block = (
            f"📈 <b>До следующего уровня:</b> ещё <b>{left}</b> "
            f"(сейчас <b>{q}</b> друзей с VPN от {QUALIFY_VPN_MIN_DAYS} дн.)\n"
        )

    # Каждая строка уровня отдельно — без слэшей между процентами.
    table = (
        "<b>Таблица уровней</b>\n"
        "▫️ <b>Старт</b> · 0–4 друзей\n"
        "   VPN <b>15%</b> · Stars и Premium <b>1%</b>\n"
        "▫️ <b>Бронза</b> · 5–14 друзей\n"
        "   VPN <b>20%</b> · Stars и Premium <b>2%</b>\n"
        "▫️ <b>Серебро</b> · 15–29 друзей\n"
        "   VPN <b>25%</b> · Stars и Premium <b>2.5%</b>\n"
        "▫️ <b>Золото</b> · 30+ друзей\n"
        "   VPN <b>30%</b> · Stars и Premium <b>3%</b>"
    )

    return (
        "<b>🚀 Уровни партнёра</b>\n\n"
        f"🏆 <b>Ваш уровень:</b> {label}\n"
        f"💯 <b>VPN</b> (первая покупка друга): <b>{vpn_pct}%</b>\n"
        f"⭐ <b>Stars и Premium</b> (каждая покупка): <b>{sp_pct}%</b>\n"
        f"{progress_block}\n"
        f"{table}\n\n"
        f"<i>Уровень считается по друзьям с VPN от {QUALIFY_VPN_MIN_DAYS} дней "
        "(7 дней и пробник не считаются). Проценты обновляются сами.</i>"
    )


def referral_withdraw_html(
    *,
    balance: float,
    pending: bool,
    eligibility: WithdrawEligibility | None = None,
) -> str:
    lines = [
        "<b>💸 Вывод реферального баланса</b>\n",
        f"Доступно на реферальном балансе: <b>{esc(f'{balance:.2f}')} ₽</b>\n",
        "Вывод обрабатывается <b>вручную</b> администрацией после проверки.",
        f"Минимум заявки: <b>{esc(f'{MIN_WITHDRAW_RUB:.0f}')} ₽</b>.\n",
        "Способы: <b>карта</b> или <b>крипта</b> (USDT TRC20 или CryptoBot).\n",
    ]
    if eligibility is not None:
        lines.append("<b>Условия вывода:</b>")
        lines.append(eligibility_checklist_html(eligibility, min_withdraw_rub=MIN_WITHDRAW_RUB))
    if pending:
        lines.append("\n⏳ У вас уже есть <b>заявка в обработке</b>. Дождитесь ответа.")
    elif eligibility is not None and not eligibility.ok:
        lines.append("\nКогда все пункты ✅ — появится кнопка вывода.")
    elif balance + 1e-6 < MIN_WITHDRAW_RUB:
        lines.append(
            f"\nЧтобы подать заявку, накопите минимум "
            f"<b>{esc(f'{MIN_WITHDRAW_RUB:.0f}')} ₽</b> на реферальном."
        )
    else:
        lines.append("\nВыберите способ вывода ниже.")
    return "\n".join(lines)


def referral_withdraw_method_html(*, balance: float) -> str:
    return (
        "<b>💸 Способ вывода</b>\n\n"
        f"Сумма заявки: <b>{esc(f'{balance:.2f}')} ₽</b> (весь доступный реферальный баланс).\n\n"
        "💳 <b>Карта</b> — перевод на вашу карту вручную.\n"
        "💎 <b>Крипта</b> — USDT TRC20 или через @CryptoBot."
    )


def referral_withdraw_crypto_channel_html() -> str:
    return (
        "<b>💎 Крипто-вывод</b>\n\n"
        "Выберите канал:\n"
        "• <b>USDT TRC20</b> — адрес кошелька Tron (начинается с T)\n"
        "• <b>CryptoBot</b> — ваш @username в Telegram для перевода через @CryptoBot\n\n"
        "Курс USDT на момент выплаты определяет администрация."
    )


def referral_withdraw_crypto_prompt_html(*, channel: str) -> str:
    if channel == "usdt_trc20":
        return (
            "<b>USDT TRC20</b>\n\n"
            "Отправьте <b>адрес кошелька</b> одним сообщением "
            "(обычно 34 символа, начинается с <code>T</code>).\n\n"
            "Для отмены — /cancel или кнопка «Назад»."
        )
    return (
        "<b>CryptoBot</b>\n\n"
        "Отправьте ваш Telegram <b>@username</b> одним сообщением "
        "(например <code>@username</code>).\n\n"
        "Для отмены — /cancel или кнопка «Назад»."
    )


def referral_home_kb(
    ref_url: str, settings: Settings, *, web_ref_url: str | None = None
) -> InlineKeyboardMarkup:
    from bot.services.vpn_user_links import append_referral_action_rows

    b = InlineKeyboardBuilder()
    append_referral_action_rows(b, ref_url)
    web = (web_ref_url or "").strip()
    if web.startswith("https://"):
        b.row(InlineKeyboardButton(text="🌐 Ссылка на сайт", url=web))
    b.row(InlineKeyboardButton(text="📊 Моя статистика", callback_data="nav:refstats"))
    b.row(InlineKeyboardButton(text="🚀 Уровни партнёра", callback_data="nav:refboost"))
    b.row(InlineKeyboardButton(text="💸 Вывести", callback_data="nav:refwithdraw"))
    b.row(InlineKeyboardButton(text="📖 Подробнее", callback_data="nav:reffaq"))
    b.row(InlineKeyboardButton(text="⬅️ В меню", callback_data="nav:hub"))
    _ = settings
    return b.as_markup()


def referral_stats_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🚀 Уровни партнёра", callback_data="nav:refboost"))
    b.row(InlineKeyboardButton(text="👥 Пригласить друга", callback_data="nav:ref"))
    b.row(InlineKeyboardButton(text="⬅️ В меню", callback_data="nav:hub"))
    return b.as_markup()


def referral_boost_kb(settings: Settings, *, can_apply: bool) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    if can_apply:
        url = support_prefill_url(
            settings,
            "Вопрос по уровням реферальной программы / индивидуальный %. Готов приложить статистику.",
        )
        if url:
            b.row(InlineKeyboardButton(text="📩 Написать администрации", url=url))
        else:
            b.row(InlineKeyboardButton(text="📩 Написать администрации", callback_data="nav:supp"))
    b.row(InlineKeyboardButton(text="📊 Моя статистика", callback_data="nav:refstats"))
    b.row(InlineKeyboardButton(text="👥 Пригласить друга", callback_data="nav:ref"))
    b.row(InlineKeyboardButton(text="⬅️ В меню", callback_data="nav:hub"))
    return b.as_markup()


def referral_withdraw_kb(*, can_request: bool) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    if can_request:
        b.row(InlineKeyboardButton(text="💳 На карту", callback_data="ref:wd:card"))
        b.row(InlineKeyboardButton(text="💎 В крипту", callback_data="ref:wd:crypto"))
    b.row(InlineKeyboardButton(text="👥 Пригласить друга", callback_data="nav:ref"))
    b.row(InlineKeyboardButton(text="⬅️ В меню", callback_data="nav:hub"))
    return b.as_markup()


def referral_withdraw_crypto_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="USDT TRC20", callback_data="ref:wd:crypto:trc20"))
    b.row(InlineKeyboardButton(text="CryptoBot @user", callback_data="ref:wd:crypto:bot"))
    b.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="nav:refwithdraw"))
    return b.as_markup()


def referral_withdraw_cancel_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="⬅️ Отмена", callback_data="nav:refwithdraw"))
    return b.as_markup()
