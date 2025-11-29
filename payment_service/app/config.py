import hmac
import hashlib
# ПРИЧИНА: В Pydantic 1.x BaseSettings в pydantic, в 2.x - в pydantic-settings
try:
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        from pydantic import BaseSettings
    except ImportError:
        raise ImportError("Не удалось импортировать BaseSettings. Установите pydantic или pydantic-settings.")
from pydantic import Field

# Загрузка переменных из .env файла (если установлен python-dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv не установлен - используем только переменные окружения
    pass


class Settings(BaseSettings):
    database_url: str = Field(
        "sqlite+aiosqlite:///./payments.db",
        description="SQLAlchemy DB URL"
    )
    api_key_public: str = Field("PUBLIC_CLIENT_KEY", description="Key expected from landing form")
    frontend_url: str = Field("http://localhost:8080", description="Frontend landing page URL for success redirects")
    psp_mock_redirect_url: str = Field("https://pay.aladdin.family/mock-checkout", description="Mock PSP checkout URL")
    webhook_secret: str = Field("WEBHOOK_SECRET_KEY_CHANGE_IN_PRODUCTION", description="Secret for webhook signature verification")
    admin_key: str = Field("ADMIN_SECRET_KEY_CHANGE_IN_PRODUCTION", description="Admin API key for manual payment confirmation")
    rate_limit_retrieve_max: int = Field(5, description="Max requests per minute for /activation/retrieve")
    rate_limit_retrieve_window: int = Field(60, description="Rate limit window in seconds")
    card_number: str = Field("", description="Card number for manual transfers (format: XXXX XXXX XXXX XXXX)")
    card_holder_name: str = Field("", description="Card holder name for manual transfers")
    
    # ✅ Управление видимостью методов оплаты
    # Видимые методы (ТОП-5): СБП, SberPay, Банковские карты, Tinkoff Pay, Ручной перевод
    visible_payment_methods: str = Field(
        "qr_sbp,sberpay,card_sber,card_tinkoff,card_alfa,card_vtb,card_gpb,card_psb,card_rosselkhoz,card_uralsib,card_mkb,card_rosbank,card_homecredit,card_mts,card_otkritie,card_rencredit,card_rsb,card_sinara,card_trust,tinkoff_pay,manual_transfer",
        description="Список видимых методов оплаты (через запятую). Остальные методы будут скрыты, но не удалены."
    )

    class Config:
        env_prefix = "PAYMENT_"
        case_sensitive = False


settings = Settings()


def verify_webhook_signature(payload_body: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature using HMAC-SHA256."""
    if not signature:
        return False
    expected_signature = hmac.new(
        secret.encode(),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)

