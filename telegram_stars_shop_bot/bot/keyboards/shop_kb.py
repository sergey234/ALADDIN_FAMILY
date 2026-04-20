from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import Settings
from bot.services.catalog import Product


def onboarding_step1_kb(settings: Settings) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    inv = (settings.required_channel_invite_url or "").strip()
    if inv and (settings.required_channel_id or "").strip():
        b.row(InlineKeyboardButton(text="📢 Подписаться на канал", url=inv))
    b.row(InlineKeyboardButton(text="Далее »", callback_data="start:hub"))
    return b.as_markup()


def hub_menu_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="⭐ Купить Stars", callback_data="nav:buy_stars"),
        InlineKeyboardButton(text="💸 Продать Stars", callback_data="nav:sell_stars"),
    )
    b.row(
        InlineKeyboardButton(text="🎁 Купить подарки", callback_data="nav:gifts"),
        InlineKeyboardButton(text="💎 Купить Premium", callback_data="nav:premium"),
    )
    b.row(
        InlineKeyboardButton(text="🤝 Партнёрам", callback_data="nav:partners"),
        InlineKeyboardButton(text="🏆 Конкурс", callback_data="nav:contest"),
    )
    b.row(
        InlineKeyboardButton(text="🧾 Чеки", callback_data="nav:receipts"),
        InlineKeyboardButton(text="🔌 Наш API", callback_data="nav:api"),
    )
    b.row(
        InlineKeyboardButton(text="👤 Мой профиль", callback_data="nav:profile"),
        InlineKeyboardButton(text="💳 Пополнить баланс", callback_data="nav:topup"),
    )
    b.row(
        InlineKeyboardButton(text="📜 Мои заказы", callback_data="nav:orders:0"),
        InlineKeyboardButton(text="🛟 Поддержка", callback_data="nav:supp"),
    )
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
    b.row(InlineKeyboardButton(text="💳 СБП / карта", callback_data=f"pay:fiat:{product_id}"))
    b.row(InlineKeyboardButton(text="₿ TON / крипта", callback_data=f"pay:crypto:{product_id}"))
    b.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"buy:{product_id}"))
    return b.as_markup()


def lava_payment_kb(pay_url: str) -> InlineKeyboardMarkup:
    """Кнопка на страницу оплаты LAVA (СБП, карты и др. по тарифам магазина)."""
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="💳 Оплатить (LAVA — СБП / карта)", url=pay_url))
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


def admin_order_kb(order_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="✅ Оплачен", callback_data=f"adm:paid:{order_id}"),
        InlineKeyboardButton(text="⚙️ В работе", callback_data=f"adm:proc:{order_id}"),
    )
    b.row(InlineKeyboardButton(text="🎁 Выдан", callback_data=f"adm:done:{order_id}"))
    return b.as_markup()


def admin_topup_kb(topup_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="✅ Зачислить баланс", callback_data=f"top:ok:{topup_id}"))
    return b.as_markup()


def admin_sell_kb(sell_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="📎 В работе", callback_data=f"sel:proc:{sell_id}"),
        InlineKeyboardButton(text="✅ Завершено", callback_data=f"sel:done:{sell_id}"),
    )
    b.row(InlineKeyboardButton(text="❌ Отмена", callback_data=f"sel:can:{sell_id}"))
    return b.as_markup()


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
