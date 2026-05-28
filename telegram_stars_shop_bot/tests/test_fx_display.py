from __future__ import annotations

from bot.config import Settings
from bot.services.fx_display import effective_usdt_rub_rate, fx_payment_hints_html
from bot.services.pricing import format_shop_quote_money_html


def test_effective_usdt_falls_back_to_usd_rate(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:test")
    monkeypatch.setenv("USD_RUB_RATE", "100")
    monkeypatch.setenv("USDT_RUB_RATE", "0")
    s = Settings()
    assert effective_usdt_rub_rate(s) == 100.0


def test_effective_usdt_explicit(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:test")
    monkeypatch.setenv("USD_RUB_RATE", "100")
    monkeypatch.setenv("USDT_RUB_RATE", "99")
    s = Settings()
    assert effective_usdt_rub_rate(s) == 99.0


def test_format_shop_quote_money_matches_rate(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:test")
    monkeypatch.setenv("USD_RUB_RATE", "80")
    monkeypatch.setenv("USDT_RUB_RATE", "0")
    s = Settings()
    html = format_shop_quote_money_html(s, 3200.0, 40.0)
    assert "3200" in html
    assert "40.00" in html
    assert "80" in html
    assert "курс магазина" in html
    assert "номинал в каталоге" not in html


def test_fx_hints_usdt_only(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:test")
    monkeypatch.setenv("USD_RUB_RATE", "100")
    monkeypatch.setenv("USDT_RUB_RATE", "100")
    s = Settings()
    html = fx_payment_hints_html(s, rub_final=1000.0, usd_base=10.0)
    assert "USDT" in html
    assert "TRC20" in html
    assert "10" in html or "10.0" in html
    assert "провайдер" in html.lower() or "платёж" in html.lower() or "Crypto Pay" in html
    assert "UAH" not in html
    assert "BYN" not in html


def test_fx_hints_no_legacy_uah_env(monkeypatch) -> None:
    """Старые переменные UAH в .env не подхватываются — только ₽ и USDT."""
    monkeypatch.setenv("BOT_TOKEN", "1:test")
    monkeypatch.setenv("USD_RUB_RATE", "100")
    monkeypatch.setenv("USDT_RUB_RATE", "100")
    monkeypatch.setenv("DISPLAY_USD_UAH_RATE", "99")
    s = Settings()
    html = fx_payment_hints_html(s, rub_final=1000.0, usd_base=10.0)
    assert "UAH" not in html
