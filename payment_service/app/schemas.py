from pydantic import BaseModel
from typing import Optional


class PaymentCreateRequest(BaseModel):
    tariff_id: str
    user_alias: str
    pin: str
    payment_method: str
    period_months: int
    amount: float
    personal_data_consent: bool  # ✅ Согласие на обработку ПДн
    consent_timestamp: Optional[str] = None  # ✅ Время согласия (ISO format)
    consent_ip: Optional[str] = None  # ✅ IP адрес клиента
    referral_code: Optional[str] = None  # Реферальный код
