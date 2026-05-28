"""Тарифы AiMonkeyVPN: фиксированные ₽ из products.yaml + подписи для кнопок и экрана."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.brand_constants import VPN_PRODUCT_NAME
from bot.config import Settings
from bot.services.catalog import Product, sort_for_display
from bot.services.pricing import quote_product
from bot.util_html import esc

# Ориентир «помесячно» для строки экономии (30 дней = 290 ₽).
VPN_BASELINE_MONTH_RUB = 290.0

_VPN_PERIOD_LABEL: dict[int, str] = {
    30: "30 дней",
    90: "3 мес",
    180: "6 мес",
    270: "9 мес",
    365: "12 мес",
}


def list_vpn_products(products: list[Product]) -> list[Product]:
    items = [
        p
        for p in products
        if (p.kind or "").strip().lower() == "vpn" and (p.vpn_subscription_days or 0) > 0
    ]
    return sort_for_display(items)


def _period_label(days: int) -> str:
    return _VPN_PERIOD_LABEL.get(days, f"{days} дн.")


def vpn_tariff_savings_rub(*, days: int, rub_total: float, baseline_month_rub: float = VPN_BASELINE_MONTH_RUB) -> float:
    months = max(days / 30.0, 1.0)
    baseline_total = baseline_month_rub * months
    return round(max(0.0, baseline_total - rub_total), 2)


def vpn_tariff_button_label(product: Product, settings: Settings) -> str:
    """Короткая подпись инлайн-кнопки (базовая цена без персональных скидок)."""
    days = int(product.vpn_subscription_days or 30)
    q = quote_product(product, settings, is_first_order=False)
    label = _period_label(days)
    rub = int(round(q.rub_list))
    if days <= 31:
        return f"{product.emoji} {label} — {rub} ₽"
    months = max(days / 30.0, 1.0)
    per_m = int(round(q.rub_list / months))
    save = int(vpn_tariff_savings_rub(days=days, rub_total=q.rub_list))
    if save > 0:
        return f"{product.emoji} {label} — {rub} ₽ ({per_m} ₽/мес, −{save} ₽)"
    return f"{product.emoji} {label} — {rub} ₽ ({per_m} ₽/мес)"


def vpn_referral_blurb_html(settings: Settings) -> str:
    """Приглашение друзей на экране VPN — та же программа, что Stars/Premium."""
    p = esc(VPN_PRODUCT_NAME)
    rf = int(settings.vpn_referral_referrer_days)
    ff = int(settings.vpn_referral_friend_days)
    rb = int(round(float(settings.ref_buyer_discount_percent)))
    lines = [
        "\n<b>👥 Приглашение друзей</b>",
        "• Та же ссылка, что в «Мой профиль» (<code>ref_…</code>).",
        f"• Друг может купить Stars, Premium или {p} — скидка <b>{rb}%</b> на первую "
        "<b>выданную</b> покупку в боте.",
    ]
    if ff > 0 or rf > 0:
        parts = []
        if ff > 0:
            parts.append(f"ему <b>+{ff}</b> дн.")
        if rf > 0:
            parts.append(f"вам <b>+{rf}</b> дн.")
        lines.append(
            f"• Если он <b>впервые получит</b> {p} — дополнительно {' и '.join(parts)} "
            "(один раз на друга)."
        )
    lines.append(
        "• Кнопка «👥 Скопировать приглашение» ниже — при активной подписке. "
        "Это ссылка <b>в бот</b>, не конфиг VPN. Не путать с «запасной подпиской»."
    )
    return "\n".join(lines)


def _vpn_tariff_price_lines(settings: Settings, products: list[Product]) -> list[str]:
    """Строки цен для блока тарифов (без заголовка)."""
    vpn_items = list_vpn_products(products)
    best_save = -1.0
    best_days = 0
    for p in vpn_items:
        days = int(p.vpn_subscription_days or 30)
        q = quote_product(p, settings, is_first_order=False)
        save = vpn_tariff_savings_rub(days=days, rub_total=q.rub_list)
        if save > best_save:
            best_save = save
            best_days = days

    lines: list[str] = []
    for p in vpn_items:
        days = int(p.vpn_subscription_days or 30)
        q = quote_product(p, settings, is_first_order=False)
        rub = int(round(q.rub_list))
        label = esc(_period_label(days))
        star = "⭐ " if days == best_days and best_save > 0 else ""
        if days <= 31:
            lines.append(f"• {star}{label} — <b>{rub} ₽</b>")
            continue
        months = max(days / 30.0, 1.0)
        per_m = int(round(q.rub_list / months))
        save = int(vpn_tariff_savings_rub(days=days, rub_total=q.rub_list))
        extra = f", экономия {save} ₽ к {int(VPN_BASELINE_MONTH_RUB)} ₽/мес" if save > 0 else ""
        lines.append(f"• {star}{label} — <b>{rub} ₽</b> <i>({per_m} ₽/мес{extra})</i>")
    return lines


def vpn_tariffs_html(settings: Settings, products: list[Product]) -> str:
    """Компактный блок тарифов (пульт VPN)."""
    head = "<b>💳 Тарифы</b> <i>(чем дольше срок — тем ниже ₽/мес)</i>"
    body = _vpn_tariff_price_lines(settings, products)
    if not body:
        return f"{head}\n<i>Тарифы временно недоступны.</i>"
    return head + "\n" + "\n".join(body)


_VPN_CARD_RULE = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"


def vpn_tariffs_card_html(settings: Settings, products: list[Product]) -> str:
    """
    Выделенная «карточка» тарифов для экрана 🟢 Оплата (уровень 2).
    Сверху экрана — над галочками политики и соглашения.
    """
    body = _vpn_tariff_price_lines(settings, products)
    if not body:
        inner = "<i>Тарифы временно недоступны — напишите в поддержку.</i>"
    else:
        inner = (
            "<i>Нажмите кнопку срока ниже — затем отметьте документы.</i>\n\n"
            + "\n".join(body)
        )
    p = esc(VPN_PRODUCT_NAME)
    return (
        f"{_VPN_CARD_RULE}\n"
        f"<blockquote><b>💳 Тарифы и оплата {p}</b>\n{inner}</blockquote>\n"
        f"{_VPN_CARD_RULE}"
    )


def append_vpn_tariff_buy_rows(b: InlineKeyboardBuilder, products: list[Product], settings: Settings) -> None:
    for p in list_vpn_products(products):
        b.row(
            InlineKeyboardButton(
                text=vpn_tariff_button_label(p, settings),
                callback_data=f"buy:{p.id}",
            )
        )
