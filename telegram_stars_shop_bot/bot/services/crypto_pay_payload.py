"""
Поле payload для Crypto Pay createInvoice: привязка счёта к заказу и сумме к доплате в ₽.

Канон строки: SB1|<order_id>|<due_kop>  (due_kop = копейки, целое от round(due_rub, 2) * 100).

Для payment_method crypto - due = весь заказ в ₽ после скидок; для mix_crypto - внешняя часть
(как orders_repo.amount_due_external: rub_after_discounts − balance_applied_rub).
"""

from __future__ import annotations

from dataclasses import dataclass

import aiosqlite

from bot.config import Settings
from bot.services import orders_repo

# SB1 - метка версии 1 формата строки payload (см. docs/CRYPTO_PAY_SPEC.md). При смене формата - SB2 и парсер по версии.
_PAYLOAD_MAGIC = "SB1"
_PAYLOAD_SEP = "|"
_MAX_PAYLOAD_LEN = 512


@dataclass(frozen=True)
class DecodedCryptoInvoicePayload:
    version: int
    order_id: int
    """Копейки суммы к оплате через Crypto Pay (как в encode), для сверки с БД."""
    due_kop: int

    @property
    def due_rub(self) -> float:
        return self.due_kop / 100.0


def encode_crypto_invoice_payload(*, order_id: int, due_rub: float) -> str:
    """
    Строка для параметра createInvoice.payload (ASCII, короткая).

    due_rub - сумма в ₽ к оплате через Crypto Pay (полный заказ или внешняя часть при mix).
    """
    if order_id < 1:
        raise ValueError("invalid_order_id")
    due = round(max(0.0, float(due_rub)), 2)
    if due < 0.01:
        raise ValueError("invalid_due_rub")
    kop = int(round(due * 100))
    raw = f"{_PAYLOAD_MAGIC}{_PAYLOAD_SEP}{order_id}{_PAYLOAD_SEP}{kop}"
    if len(raw) > _MAX_PAYLOAD_LEN:
        raise ValueError("payload_too_long")
    return raw


def decode_crypto_invoice_payload(raw: str) -> DecodedCryptoInvoicePayload:
    s = (raw or "").strip()
    parts = s.split(_PAYLOAD_SEP)
    if len(parts) != 3 or parts[0] != _PAYLOAD_MAGIC:
        raise ValueError("invalid_crypto_payload")
    try:
        oid = int(parts[1], 10)
        kop = int(parts[2], 10)
    except ValueError as e:
        raise ValueError("invalid_crypto_payload_fields") from e
    if oid < 1 or kop < 1:
        raise ValueError("invalid_crypto_payload_fields")
    return DecodedCryptoInvoicePayload(version=1, order_id=oid, due_kop=kop)


def order_supports_crypto_pay_invoice(order: aiosqlite.Row) -> bool:
    pm = str(order["payment_method"] or "")
    return pm in ("crypto", "mix_crypto")


def verify_decoded_payload_against_order(
    payload: DecodedCryptoInvoicePayload,
    order: aiosqlite.Row,
) -> None:
    """Сверка с текущей строкой заказа (статус pending_payment и т.д. - на вызывающем)."""
    oid = int(order["id"])
    if payload.order_id != oid:
        raise ValueError("crypto_payload_order_mismatch")
    if not order_supports_crypto_pay_invoice(order):
        raise ValueError("crypto_payload_payment_method")
    due = round(max(0.0, orders_repo.amount_due_external(order)), 2)
    expected_kop = int(round(due * 100))
    if payload.due_kop != expected_kop:
        raise ValueError("crypto_payload_due_mismatch")


def crypto_invoice_expires_in_seconds(settings: Settings) -> int:
    """
    Секунды для expires_in счёта Crypto Pay: не дольше окна «ожидает оплаты» заказа.

    Если ORDER_PENDING_PAYMENT_EXPIRE_MINUTES = 0 (TTL выкл.), берём только CRYPTO_PAY_INVOICE_EXPIRE_SECONDS.
    Минимум 60 с - разумный нижний порог для стороннего API.
    """
    inv = max(60, int(settings.crypto_pay_invoice_expire_seconds))
    om = int(settings.order_pending_payment_expire_minutes)
    if om <= 0:
        return inv
    cap = om * 60
    return min(inv, cap)
