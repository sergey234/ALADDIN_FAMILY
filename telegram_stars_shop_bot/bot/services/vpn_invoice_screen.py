"""Экран «Счёт перед оплатой» для заказов AiMonkeyVPN."""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from bot.brand_constants import VPN_PRODUCT_NAME
from bot.config import Settings
from bot.services.catalog import Product
from bot.services.vpn_legal_gate import vpn_privacy_and_terms_urls
from bot.services.vpn_subscription_dates import (
    compute_paid_until_after_purchase,
    format_paid_until_display_msk,
    preview_paid_until_iso,
)
from bot.util_html import esc

_MSK = ZoneInfo("Europe/Moscow")


def invoice_pay_deadline_msk(settings: Settings, *, payment_method: str) -> str:
    pm = (payment_method or "").strip().lower()
    if pm in ("crypto", "mix_crypto", "mixcr"):
        minutes = 60
    else:
        minutes = max(1, min(int(settings.lava_invoice_expire_minutes), 43200))
    dt = datetime.now(_MSK) + timedelta(minutes=minutes)
    return dt.strftime("%H:%M:%S") + " МСК"


async def vpn_invoice_screen_html(
    settings: Settings,
    conn,
    *,
    order_id: int,
    rub_due: float,
    product: Product,
    telegram_user_id: int,
    payment_method: str,
    balance_applied: float = 0.0,
) -> str:
    days = int(product.vpn_subscription_days or 30)
    current_until = await preview_paid_until_iso(settings, telegram_user_id)
    until_iso = compute_paid_until_after_purchase(current_paid_until=current_until, days=days)
    until_disp = format_paid_until_display_msk(until_iso)

    pu, tu = vpn_privacy_and_terms_urls(settings)
    legal = ""
    if pu and tu:
        legal = (
            f'\n\nОплачивая, вы принимаете '
            f'<a href="{esc(pu)}">Политику конфиденциальности</a> и '
            f'<a href="{esc(tu)}">Пользовательское соглашение</a> {esc(VPN_PRODUCT_NAME)}.'
        )
    elif pu or tu:
        one = pu or tu
        legal = f'\n\nОплачивая, вы принимаете <a href="{esc(one)}">документы сервиса</a>.'

    rub_s = esc(f"{float(rub_due):.2f}")
    oid_s = esc(str(order_id))
    deadline = esc(invoice_pay_deadline_msk(settings, payment_method=payment_method))

    balance_block = ""
    if balance_applied > 0.01:
        balance_block = (
            f"\nС баланса уже: <b>{esc(f'{balance_applied:.2f}')} ₽</b>"
        )

    from bot.services.vpn_payment_copy import vpn_invoice_fiat_methods_hint_html

    pm = (payment_method or "").strip().lower()
    if pm in ("crypto", "mix_crypto", "mixcr"):
        pay_hint = "Ниже — оплата <b>криптой (USDT)</b>."
    else:
        pay_hint = vpn_invoice_fiat_methods_hint_html(settings, payment_method=pm)

    return (
        f"<b>Счёт на оплату {esc(VPN_PRODUCT_NAME)} создан</b>\n"
        f"Заказ <code>{oid_s}</code>{balance_block}\n\n"
        f"💵 <b>К оплате: {rub_s} ₽</b>\n"
        f"🕘 <b>Подписка до:</b> {esc(until_disp)}\n"
        f"⏰ <b>Оплатите до:</b> {deadline}\n\n"
        "<i>Если подписка уже активна — оставшиеся дни сохранятся, срок продлится.</i>\n"
        "<i>Одна подписка: телефон, планшет и ПК — один ключ в WireGuard.</i>\n\n"
        f"{pay_hint}"
        f"{legal}\n\n"
        "<i>Сохраните квитанцию из банка или кошелька.</i>"
    )


def vpn_invoice_fiat_channel_tail_html(*, channel_label: str) -> str:
    """Устарело: используйте vpn_payment_copy.vpn_invoice_*_checkout_html."""
    return (
        f"\n\n<b>{esc(channel_label)}</b>\n"
        "Нажмите кнопку оплаты ниже. "
        "<i>Другой способ (СБП/карта) не нажимайте — достаточно одной оплаты.</i>"
    )
