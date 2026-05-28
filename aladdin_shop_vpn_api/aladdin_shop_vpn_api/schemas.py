from __future__ import annotations

from pydantic import BaseModel, Field


class ProvisionBody(BaseModel):
    telegram_user_id: int = Field(..., ge=1)
    order_id: int = Field(..., ge=1)
    paid_until: str = Field(..., min_length=10, description="ISO8601 UTC")


class ExtendBody(BaseModel):
    telegram_user_id: int = Field(..., ge=1)
    order_id: int = Field(..., ge=1)
    paid_until: str = Field(..., min_length=10)


class RevokeBody(BaseModel):
    telegram_user_id: int = Field(..., ge=1)
    reason: str = Field(default="admin_revoke", max_length=256)


class AddSubscriptionDaysBody(BaseModel):
    """Нарастить срок подписки на N календарных дней от max(now, paid_until)."""

    telegram_user_id: int = Field(..., ge=1)
    order_id: int = Field(..., ge=1)
    days: int = Field(..., ge=1, le=3660)
    reason: str = Field(default="referral", max_length=128)


class WgConfBody(BaseModel):
    """Выдача клиентского WireGuard .conf (только HMAC + nonce; без Idempotency-Key)."""

    telegram_user_id: int = Field(..., ge=1)


class LocationSelectBody(BaseModel):
    telegram_user_id: int = Field(..., ge=1)
    location_slug: str = Field(..., min_length=1, max_length=48)


class OvpnConfBody(BaseModel):
    telegram_user_id: int = Field(..., ge=1)
