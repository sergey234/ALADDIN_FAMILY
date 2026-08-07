"""Маршрутизация фиатной оплаты: LAVA, Ckassa BC, Cardlink."""

from __future__ import annotations

from bot.config import Settings
from bot.services.ckassa_api import ckassa_checkout_configured
from bot.services.lava_api import lava_checkout_configured


def fiat_bc_universal_url_active(settings: Settings) -> str:
    """
    URL универсальной страницы Ckassa (сумма вручную), если её нужно показывать покупателю.
    При настроенной LAVA без Ckassa Shop API BC не используется (основной поток — счёт LAVA).
    """
    u = (getattr(settings, "ckassa_bc_universal_payment_url", "") or "").strip()
    if not u:
        return ""
    if lava_checkout_configured(settings) and not ckassa_checkout_configured(settings):
        if not bool(getattr(settings, "fiat_parallel_ckassa_and_lava", False)):
            return ""
    return u


def fiat_primary_provider_label(settings: Settings) -> str:
    """Название основного фиатного провайдера для текстов в боте."""
    if lava_checkout_configured(settings):
        return "LAVA"
    if ckassa_checkout_configured(settings):
        return "Ckassa"
    if fiat_bc_universal_url_active(settings):
        return "Ckassa"
    return "онлайн-оплата"
