from __future__ import annotations

from typing import Any, Mapping

from bot.config import Settings
from bot.services.ckassa_api import ckassa_checkout_configured


def _pm(order: Mapping[str, Any]) -> str:
    return str(order.get("payment_method") or "").strip().lower()


def is_crypto_channel_payment_method(payment_method: str | None) -> bool:
    """Заказ оформлен через ветку «крипта» (счёт Crypto/xRocket или mix с крипто-доплатой)."""
    pm = (payment_method or "").strip().lower()
    return pm in ("crypto", "mixcr", "mix_crypto")


def is_fiat_webhook_channel_payment_method(payment_method: str | None) -> bool:
    """Фиат с ожидаемым server-side callback (Ckassa)."""
    pm = (payment_method or "").strip().lower()
    return pm in ("fiat", "mix_fiat")


def crypto_invoice_providers_enabled(settings: Settings) -> bool:
    return bool(settings.crypto_pay_enabled or settings.xrocket_pay_enabled)


def crypto_manual_paid_gate_applies(order: Mapping[str, Any], settings: Settings) -> bool:
    """
    True — обычную кнопку «Оплачен» (adm:paid) для pending_payment нужно блокировать:
    ждём вебхук провайдера; ручной paid только через break-glass (adm:paidbg).
    """
    st = str(order.get("status") or "").strip().lower()
    if st != "pending_payment":
        return False
    pm = _pm(order)
    if crypto_invoice_providers_enabled(settings) and is_crypto_channel_payment_method(pm):
        return True
    if ckassa_checkout_configured(settings) and is_fiat_webhook_channel_payment_method(pm):
        return True
    return False
