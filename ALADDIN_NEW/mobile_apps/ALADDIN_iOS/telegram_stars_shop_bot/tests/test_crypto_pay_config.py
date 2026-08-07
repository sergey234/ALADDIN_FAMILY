from __future__ import annotations

from bot.config import Settings


def _minimal(**kwargs: object) -> Settings:
    base = dict(
        BOT_TOKEN="9:x",
        ADMIN_IDS="1",
        API_KEY_PEPPER="k" * 32,
    )
    base.update(kwargs)
    return Settings(**base)  # type: ignore[arg-type]


def test_crypto_pay_api_origin_mainnet_default() -> None:
    s = _minimal()
    assert s.crypto_pay_api_origin() == "https://pay.crypt.bot"


def test_crypto_pay_api_origin_testnet() -> None:
    s = _minimal(CRYPTO_PAY_TESTNET=True)
    assert s.crypto_pay_api_origin() == "https://testnet-pay.crypt.bot"


def test_crypto_pay_api_origin_host_only_override() -> None:
    s = _minimal(CRYPTO_PAY_API_HOST="pay.example.invalid")
    assert s.crypto_pay_api_origin() == "https://pay.example.invalid"


def test_crypto_pay_api_origin_full_url_override() -> None:
    s = _minimal(CRYPTO_PAY_API_HOST="https://edge.example.com/v99/")
    assert s.crypto_pay_api_origin() == "https://edge.example.com/v99"


def test_crypto_pay_defaults() -> None:
    s = _minimal()
    assert s.crypto_pay_enabled is False
    assert s.crypto_pay_api_token == ""
    assert s.crypto_pay_default_asset == "USDT"
    assert s.crypto_pay_invoice_expire_seconds == 3600
    assert s.crypto_pay_paid_btn_url == ""
    assert s.crypto_pay_wallet_fallback is False
    assert s.xrocket_pay_enabled is False
    assert s.xrocket_pay_api_key == ""
    assert "xrocket.exchange" in s.xrocket_pay_api_base
    assert s.crypto_show_ton_manual is True
    assert s.auto_fulfill_enabled is False
    assert s.auto_fulfill_stars_enabled is False
    assert s.auto_fulfill_premium_enabled is False
    assert s.auto_fulfill_max_order_rub == 0.0
    assert s.auto_fulfill_max_attempts == 5
    assert s.auto_fulfill_poll_interval_seconds == 60
    assert s.auto_fulfill_failure_alerts_enabled is True
    assert s.auto_fulfill_master_on() is False
    assert s.stuck_processing_alert_minutes == 0
    assert s.operator_queue_processing_idle_minutes == 30
