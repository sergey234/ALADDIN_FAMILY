import uuid
from datetime import datetime, timedelta, timezone

from ..config import settings


class MockPaymentProvider:
    @staticmethod
    async def create_payment(amount: int, currency: str = "RUB") -> dict:
        payment_id = f"psp_{uuid.uuid4().hex[:12]}"
        return {
            "payment_id": payment_id,
            "redirect_url": f"{settings.psp_mock_redirect_url}?payment_id={payment_id}",
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=5),
        }


provider = MockPaymentProvider()



