from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class ErrorBody(BaseModel):
    code: str
    message: str
    request_id: Optional[str] = None


class OrderCreateBody(BaseModel):
    product_id: str = Field(..., min_length=1, max_length=128)
    recipient: str = Field(..., min_length=3, max_length=64)
    payment_method: Literal["fiat", "crypto"] = "fiat"
    external_ref: Optional[str] = Field(default=None, max_length=256)

    @field_validator("recipient")
    @classmethod
    def strip_recipient(cls, v: str) -> str:
        return v.strip()


class OrderCreateResponse(BaseModel):
    order_id: int
    created: bool
    status: str
    rub_after_discounts: float
    balance_applied_rub: float
    amount_due_external_rub: float
    recipient_normalized: str
    payment_method: str


class OrderOut(BaseModel):
    id: int
    status: str
    product_id: str
    product_title: str
    payment_method: str
    rub_after_discounts: float
    balance_applied_rub: float
    amount_due_external_rub: float
    user_note: Optional[str]
    source: str
    external_ref: Optional[str]
    created_at: str
    updated_at: str


class OrderListOut(BaseModel):
    items: List[OrderOut]
    next_offset: Optional[int] = None


class UserProfileOut(BaseModel):
    owner_user_id: int
    balance_rub: float
    ref_balance_rub: float
    scopes: List[str]


class TopupCreateBody(BaseModel):
    amount_rub: float = Field(..., ge=100, le=500_000)


class TopupCreateResponse(BaseModel):
    topup_id: int
    status: str
    amount_rub: float


class TopupOut(BaseModel):
    id: int
    amount_rub: float
    status: str
    created_at: str


class TopupListOut(BaseModel):
    items: List[TopupOut]


class WebhookSubscriptionGetOut(BaseModel):
    webhook_url: Optional[str] = None
    has_signing_secret: bool = False


class WebhookSubscriptionPutBody(BaseModel):
    """webhook_url: null/пустая строка — отключить; поле опущено — не менять URL (удобно для rotate_secret)."""

    webhook_url: Optional[str] = Field(default=None, max_length=2048)
    rotate_secret: bool = False


class WebhookSubscriptionPutOut(BaseModel):
    webhook_url: Optional[str] = None
    has_signing_secret: bool = False
    signing_secret: Optional[str] = Field(
        default=None,
        description="Показывается один раз при первой настройке или rotate_secret",
    )
