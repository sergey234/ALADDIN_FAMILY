"""Идентификаторы платежей LAVA: ORDER (заказы) и TOPUP (пополнение баланса)."""

from __future__ import annotations

import re
from typing import Literal

from bot.services.lava_api import parse_lava_shop_order_id

PaymentKind = Literal["order", "topup"]

_TOPUP_LAVA_RE = re.compile(r"^TOPUP(\d+)(?:-r\d+)?$", re.IGNORECASE)


def lava_topup_provider_order_id(topup_id: int, attempt: int = 1) -> str:
    att = max(1, int(attempt))
    tid = int(topup_id)
    if att <= 1:
        return f"TOPUP{tid}"
    return f"TOPUP{tid}-r{att}"


def parse_lava_payment_reference(raw: object) -> tuple[PaymentKind, int] | None:
    """«59», «59-r2» → order; «TOPUP12», «TOPUP12-r2» → topup."""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    m = _TOPUP_LAVA_RE.match(s)
    if m:
        return ("topup", int(m.group(1)))
    oid = parse_lava_shop_order_id(raw)
    if oid is not None:
        return ("order", oid)
    return None
