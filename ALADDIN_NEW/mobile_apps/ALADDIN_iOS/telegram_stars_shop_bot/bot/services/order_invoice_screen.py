"""Экран «Счёт перед оплатой» для Stars, Premium, VPN, gift."""

from __future__ import annotations

from bot.brand_constants import VPN_PRODUCT_NAME
from bot.config import Settings
from bot.services.catalog import Product
from bot.services.checkout_client_copy import invoice_brief_html
from bot.services.vpn_invoice_screen import invoice_pay_deadline_msk, vpn_invoice_screen_html
from bot.util_html import esc


async def order_invoice_screen_html(
    settings: Settings,
    conn,
    *,
    order_id: int,
    rub_due: float,
    product: Product,
    telegram_user_id: int,
    payment_method: str,
    balance_applied: float = 0.0,
    recipient_note: str = "",
) -> str:
    kind = (product.kind or "").strip().lower()
    if kind == "vpn":
        return await vpn_invoice_screen_html(
            settings,
            conn,
            order_id=order_id,
            rub_due=rub_due,
            product=product,
            telegram_user_id=telegram_user_id,
            payment_method=payment_method,
            balance_applied=balance_applied,
        )

    pm = (payment_method or "").strip().lower()
    pay_crypto = pm in ("crypto", "mix_crypto", "mixcr")
    deadline = invoice_pay_deadline_msk(settings, payment_method=payment_method)
    title = f"{product.emoji} {product.title}".strip()
    usd = float(getattr(product, "price_usd", 0) or 0)
    # Prefer live equiv from rub
    return invoice_brief_html(
        settings,
        title=title,
        rub=float(rub_due),
        catalog_usd=usd,
        recipient=(recipient_note or "").strip(),
        deadline=deadline,
        balance_applied=float(balance_applied or 0),
        pay_crypto=pay_crypto,
    )
