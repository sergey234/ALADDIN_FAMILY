from __future__ import annotations

import os

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import Settings
from bot.services.admin_crypto_paid_gate import crypto_manual_paid_gate_applies
from bot.services.admin_order_ff import AdminOrderFfContext, fulfillment_controls_allowed
from bot.services.catalog import Product


def channel_subscribe_kb(settings: Settings) -> InlineKeyboardMarkup:
    """Кнопки подписки и повторной проверки (жёсткая стена и /menu)."""
    b = InlineKeyboardBuilder()
    inv = (settings.required_channel_invite_url or "").strip()
    if inv:
        b.row(InlineKeyboardButton(text="📢 Подписаться на канал", url=inv))
    b.row(InlineKeyboardButton(text="✅ Я подписался — открыть меню", callback_data="start:hub"))
    return b.as_markup()


def channel_member_open_menu_kb(settings: Settings) -> InlineKeyboardMarkup:
    """/start, когда подписка на канал уже есть: ссылка на канал + вход в хаб (не пускаем «молча»)."""
    b = InlineKeyboardBuilder()
    inv = (settings.required_channel_invite_url or "").strip()
    if inv:
        b.row(InlineKeyboardButton(text="📢 Канал магазина", url=inv))
    b.row(InlineKeyboardButton(text="🚀 Открыть меню", callback_data="start:hub"))
    return b.as_markup()


def onboarding_step1_kb(settings: Settings) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    inv = (settings.required_channel_invite_url or "").strip()
    if inv and (settings.required_channel_id or "").strip():
        b.row(InlineKeyboardButton(text="📢 Подписаться на канал", url=inv))
    b.row(InlineKeyboardButton(text="Далее »", callback_data="start:hub"))
    return b.as_markup()


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    s = raw.strip().lower()
    if s in ("1", "true", "yes", "y", "on"):
        return True
    if s in ("0", "false", "no", "n", "off"):
        return False
    return default


def _ui_card_visible(settings: Settings | None, attr_name: str, env_name: str) -> bool:
    if settings is not None and hasattr(settings, attr_name):
        return bool(getattr(settings, attr_name))
    return _env_bool(env_name, True)


def hub_menu_kb(settings: Settings | None = None) -> InlineKeyboardMarkup:
    """Главное меню MonkeyStars: Stars / Premium / реф-ссылка / заказы / поддержка (без «Продать Stars»)."""
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="⭐ Stars", callback_data="nav:buy_stars"),
        InlineKeyboardButton(text="💎 Premium", callback_data="nav:premium"),
    )
    b.row(
        InlineKeyboardButton(text="🔗 Реф-ссылка", callback_data="nav:ref"),
        InlineKeyboardButton(text="📜 Заказы", callback_data="nav:orders:0"),
    )
    b.row(
        InlineKeyboardButton(text="🏆 Конкурс", callback_data="nav:contest"),
        InlineKeyboardButton(text="👤 Профиль", callback_data="nav:profile"),
    )
    row_topup = [InlineKeyboardButton(text="💳 Пополнить", callback_data="nav:topup")]
    if _ui_card_visible(settings, "ui_show_receipts", "UI_SHOW_RECEIPTS"):
        row_topup.append(InlineKeyboardButton(text="🧾 Выданные", callback_data="nav:receipts"))
    b.row(*row_topup)

    row_partner = []
    if _ui_card_visible(settings, "ui_show_partners", "UI_SHOW_PARTNERS"):
        row_partner.append(InlineKeyboardButton(text="🤝 Партнёрам", callback_data="nav:partners"))
    row_partner.append(InlineKeyboardButton(text="🎁 Подарки", callback_data="nav:gifts"))
    b.row(*row_partner)

    row_contest = [InlineKeyboardButton(text="🛟 Поддержка", callback_data="nav:supp")]
    if _ui_card_visible(settings, "ui_show_api", "UI_SHOW_API"):
        row_contest.append(InlineKeyboardButton(text="🔌 API", callback_data="nav:api"))
    b.row(*row_contest)
    return b.as_markup()


def premium_dest_kb(product_id: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🎁 Подарок другому", callback_data=f"prem:oth:{product_id}"))
    b.row(InlineKeyboardButton(text="👤 На мой аккаунт", callback_data=f"prem:slf:{product_id}"))
    b.row(InlineKeyboardButton(text="⬅️ В главное меню", callback_data="nav:hub"))
    return b.as_markup()


def products_kb(products: list[Product]) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for p in products:
        b.row(
            InlineKeyboardButton(
                text=f"{p.emoji} {p.title}",
                callback_data=f"buy:{p.id}",
            )
        )
    b.row(InlineKeyboardButton(text="⬅️ В главное меню", callback_data="nav:hub"))
    return b.as_markup()


def payment_methods_kb(
    product_id: str,
    *,
    show_full_balance: bool,
    show_partial_mix: bool,
    balance: float,
    rub_final: float,
) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    apply_preview = min(max(0.0, balance), rub_final)
    rem_preview = max(0.0, rub_final - apply_preview)
    if show_full_balance:
        b.row(
            InlineKeyboardButton(
                text=f"💰 С баланса ({rub_final:.0f} ₽)",
                callback_data=f"pay:bal:{product_id}",
            )
        )
    if show_partial_mix and apply_preview > 0 and rem_preview > 0.01:
        b.row(
            InlineKeyboardButton(
                text=f"💰 Баланс + СБП (−{apply_preview:.0f} ₽)",
                callback_data=f"pay:mixfi:{product_id}",
            )
        )
        b.row(
            InlineKeyboardButton(
                text=f"💰 Баланс + крипта (−{apply_preview:.0f} ₽)",
                callback_data=f"pay:mixcr:{product_id}",
            )
        )
    b.row(InlineKeyboardButton(text="💳 Карта / СБП (онлайн)", callback_data=f"pay:fiat:{product_id}"))
    b.row(InlineKeyboardButton(text="₿ USDT (TRC20) / крипта", callback_data=f"pay:crypto:{product_id}"))
    b.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"buy:{product_id}"))
    return b.as_markup()


def lava_payment_kb(pay_url: str) -> InlineKeyboardMarkup:
    """Кнопка на страницу оплаты LAVA (СБП, карты и др. по тарифам магазина)."""
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="💳 Оплатить (LAVA — СБП / карта)", url=pay_url))
    b.row(InlineKeyboardButton(text="🏠 В главное меню", callback_data="nav:hub"))
    return b.as_markup()


def ckassa_payment_kb(pay_url: str) -> InlineKeyboardMarkup:
    """Кнопка на платёжную форму Ckassa (карты, СБП, SberPay и др. по тарифам ЦК)."""
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="💳 Оплатить (Ckassa — ₽, карта / СБП)", url=pay_url))
    b.row(InlineKeyboardButton(text="🏠 В главное меню", callback_data="nav:hub"))
    return b.as_markup()


def crypto_pay_invoice_kb(pay_url: str) -> InlineKeyboardMarkup:
    """Одна ссылка на счёт Crypto Pay (совместимость)."""
    return crypto_providers_kb([("💎 Crypto Pay (USDT TRC20)", pay_url)])


def crypto_providers_kb(url_pairs: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    """Несколько URL-кнопок (Crypto Pay, xRocket, …) + домой."""
    b = InlineKeyboardBuilder()
    for text, url in url_pairs:
        b.row(InlineKeyboardButton(text=text, url=url))
    b.row(InlineKeyboardButton(text="🏠 В главное меню", callback_data="nav:hub"))
    return b.as_markup()


def verify_username_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="✅ Всё верно", callback_data="usr:ok"),
        InlineKeyboardButton(text="✏️ Исправить", callback_data="usr:ed"),
    )
    return b.as_markup()


def confirm_order_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="✅ Создать заказ", callback_data="order:submit"))
    b.row(InlineKeyboardButton(text="⬅️ Отмена", callback_data="order:cancel"))
    return b.as_markup()


def admin_order_kb(
    order_id: int,
    *,
    settings: Settings | None = None,
    actor_id: int | None = None,
    order_ff: AdminOrderFfContext | None = None,
) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    restricted = (
        settings is not None
        and actor_id is not None
        and settings.admin_roles_restricted()
        and not settings.is_super_admin(actor_id)
    )
    if not restricted:
        paid_label = "✅ Оплачен"
        paid_cb = f"adm:paid:{order_id}"
        if (
            settings is not None
            and order_ff is not None
            and order_ff.status == "pending_payment"
            and crypto_manual_paid_gate_applies(
                {
                    "status": order_ff.status,
                    "payment_method": order_ff.payment_method or "",
                },
                settings,
            )
        ):
            paid_label = "⚠️ Оплачен (break-glass)"
            paid_cb = f"adm:paidbg:{order_id}"
        b.row(
            InlineKeyboardButton(text=paid_label, callback_data=paid_cb),
            InlineKeyboardButton(text="⚙️ В работе", callback_data=f"adm:proc:{order_id}"),
        )
        b.row(InlineKeyboardButton(text="🎁 Выдан", callback_data=f"adm:done:{order_id}"))
    else:
        b.row(InlineKeyboardButton(text="⚙️ В работе", callback_data=f"adm:proc:{order_id}"))

    if (
        settings is not None
        and actor_id is not None
        and settings.is_super_admin(actor_id)
        and order_ff is not None
    ):
        st = (order_ff.status or "").strip().lower()
        if st in ("pending_payment", "paid", "processing", "expired"):
            b.row(InlineKeyboardButton(text="💸 Сторно (refunded)", callback_data=f"adm:refund:{order_id}"))
        if st in ("paid", "processing"):
            b.row(InlineKeyboardButton(text="⚖️ Спор", callback_data=f"adm:disp:{order_id}"))
        if st == "payment_disputed":
            b.row(InlineKeyboardButton(text="↩️ Снять спор → оплачен", callback_data=f"adm:dispok:{order_id}"))

    if (
        settings is not None
        and actor_id is not None
        and order_ff is not None
        and fulfillment_controls_allowed(order_ff)
    ):
        manual = str(order_ff.fulfillment_mode_raw or "").strip().lower() == "manual_only"
        if not manual:
            b.row(InlineKeyboardButton(text="🤚 Только вручную", callback_data=f"adm:ffman:{order_id}"))
        elif settings.is_super_admin(actor_id):
            b.row(InlineKeyboardButton(text="🤖 Снова авто", callback_data=f"adm:ffauto:{order_id}"))
        if settings.is_super_admin(actor_id) and order_ff.status == "paid":
            b.row(InlineKeyboardButton(text="🔄 Сброс авто-полей", callback_data=f"adm:ffrst:{order_id}"))
    return b.as_markup()


def admin_topup_kb(
    topup_id: int,
    *,
    settings: Settings | None = None,
    actor_id: int | None = None,
) -> InlineKeyboardMarkup:
    restricted = (
        settings is not None
        and actor_id is not None
        and settings.admin_roles_restricted()
        and not settings.is_super_admin(actor_id)
    )
    if restricted:
        return InlineKeyboardMarkup(inline_keyboard=[])
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="✅ Зачислить баланс", callback_data=f"top:ok:{topup_id}"))
    return b.as_markup()


def admin_sell_kb(
    sell_id: int,
    *,
    settings: Settings | None = None,
    actor_id: int | None = None,
) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    restricted = (
        settings is not None
        and actor_id is not None
        and settings.admin_roles_restricted()
        and not settings.is_super_admin(actor_id)
    )
    if not restricted:
        b.row(
            InlineKeyboardButton(text="📎 В работе", callback_data=f"sel:proc:{sell_id}"),
            InlineKeyboardButton(text="✅ Завершено", callback_data=f"sel:done:{sell_id}"),
        )
        b.row(InlineKeyboardButton(text="❌ Отмена", callback_data=f"sel:can:{sell_id}"))
    else:
        b.row(InlineKeyboardButton(text="📎 В работе", callback_data=f"sel:proc:{sell_id}"))
    return b.as_markup()


def admin_order_reply_markup_for_api(
    order_id: int,
    *,
    settings: Settings,
    actor_id: int,
    order_ff: AdminOrderFfContext | None = None,
) -> dict:
    """Слово `reply_markup` для Telegram Bot API (sendMessage)."""
    m = admin_order_kb(order_id, settings=settings, actor_id=actor_id, order_ff=order_ff)
    dumped = m.model_dump(mode="python", exclude_none=True)
    return {"inline_keyboard": dumped.get("inline_keyboard") or []}


def admin_topup_reply_markup_for_api(topup_id: int, *, settings: Settings, actor_id: int) -> dict | None:
    m = admin_topup_kb(topup_id, settings=settings, actor_id=actor_id)
    dumped = m.model_dump(mode="python", exclude_none=True)
    rows = dumped.get("inline_keyboard") or []
    if not rows:
        return None
    return {"inline_keyboard": rows}


def orders_list_kb(page: int, has_prev: bool, has_next: bool) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    row: list[InlineKeyboardButton] = []
    if has_prev:
        row.append(InlineKeyboardButton(text="◀️", callback_data=f"nav:orders:{page - 1}"))
    row.append(InlineKeyboardButton(text=f"· {page + 1} ·", callback_data="nav:orders:noop"))
    if has_next:
        row.append(InlineKeyboardButton(text="▶️", callback_data=f"nav:orders:{page + 1}"))
    if row:
        b.row(*row)
    b.row(InlineKeyboardButton(text="⬅️ В главное меню", callback_data="nav:hub"))
    return b.as_markup()


def order_detail_kb(order_id: int, support_url: str | None) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    if support_url:
        b.row(InlineKeyboardButton(text="💬 Поддержка по заказу", url=support_url))
    else:
        b.row(InlineKeyboardButton(text="💬 Раздел поддержки", callback_data="nav:supp"))
    b.row(InlineKeyboardButton(text="⬅️ К списку", callback_data="nav:orders:0"))
    b.row(InlineKeyboardButton(text="🏠 В меню", callback_data="nav:hub"))
    return b.as_markup()
