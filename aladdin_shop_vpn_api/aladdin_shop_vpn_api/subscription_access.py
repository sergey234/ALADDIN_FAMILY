"""Проверка доступа к GET /sub/<opaque> и выдаче WG — только активная оплаченная подписка."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException

_STATUS_ACTIVE = "vpn_active"


def parse_paid_until_utc(raw: str | None) -> datetime | None:
    if not raw or not str(raw).strip():
        return None
    s = str(raw).strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.replace(microsecond=0)
    except ValueError:
        return None


def assert_subscription_active(*, status: str | None, paid_until: str | None) -> None:
    """
    Разрешить выдачу подписки Xray только при vpn_active и paid_until в будущем.
    Согласовано с POST /internal/v1/wg/conf (vpn-абуз P0).
    """
    st = (status or "").strip()
    if st == "vpn_expired":
        raise HTTPException(status_code=403, detail="subscription expired")
    if st != _STATUS_ACTIVE:
        raise HTTPException(status_code=403, detail=f"vpn not active ({st or 'unknown'})")

    end = parse_paid_until_utc(paid_until)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    if end is None or end < now:
        raise HTTPException(status_code=403, detail="subscription ended")
