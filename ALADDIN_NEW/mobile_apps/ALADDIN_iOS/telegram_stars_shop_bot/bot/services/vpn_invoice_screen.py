"""Экран «Счёт перед оплатой» для заказов AiMonkeyVPN."""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from bot.brand_constants import VPN_PRODUCT_NAME
from bot.config import Settings
from bot.services.catalog import Product
from bot.services.checkout_client_copy import vpn_invoice_brief_html
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
    _ = order_id
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

    deadline = invoice_pay_deadline_msk(settings, payment_method=payment_method)
    pm = (payment_method or "").strip().lower()
    pay_crypto = pm in ("crypto", "mix_crypto", "mixcr")
    title = f"{product.emoji} {product.title}".strip() or VPN_PRODUCT_NAME
    usd = float(getattr(product, "price_usd", 0) or 0)
    return vpn_invoice_brief_html(
        settings,
        title=title,
        rub=float(rub_due),
        catalog_usd=usd,
        until_disp=until_disp,
        deadline=deadline,
        balance_applied=float(balance_applied or 0),
        pay_crypto=pay_crypto,
        legal_html=legal,
    )


def vpn_invoice_fiat_channel_tail_html(*, channel_label: str) -> str:
    return f"\n\nОплата: <b>{esc(channel_label)}</b> — кнопка ниже."
