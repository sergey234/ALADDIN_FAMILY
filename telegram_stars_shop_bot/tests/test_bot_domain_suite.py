from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from bot.config import Settings, load_settings
from bot.services import catalog, marketing
from bot.services import channel_gate as cg
from bot.services.fx_display import effective_usdt_rub_rate, fx_payment_hints_html
from bot.services.pricing import commission_for_first_order, quote_product, rub_per_100_stars_display
from partner_api.main import create_app

_REPO_BOT = Path(__file__).resolve().parents[1] / "bot"
PRODUCTS_YAML = _REPO_BOT / "products.yaml"


def test_products_yaml_loads_and_has_stars_and_premium() -> None:
    items = catalog.load_products(PRODUCTS_YAML)
    assert len(items) >= 4
    by_id = catalog.products_by_id(items)
    assert "stars_100" in by_id
    assert by_id["stars_100"].kind == "stars"
    assert (by_id["stars_100"].stars or 0) == 100
    premium = [p for p in items if p.kind == "premium"]
    assert premium, "expected at least one premium product"


def test_sort_for_display_orders_featured_first() -> None:
    a = catalog.Product(
        id="a", kind="stars", title="A", emoji="⭐", price_usd=1.0, stars=10, featured=False, sort_order=5
    )
    b = catalog.Product(
        id="b", kind="stars", title="B", emoji="⭐", price_usd=2.0, stars=20, featured=True, sort_order=9
    )
    out = catalog.sort_for_display([a, b])
    assert out[0].id == "b"


def test_quote_first_order_discount_and_wholesale(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:quote-test")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "quote_test_pepper_minimum_32_chars____")
    monkeypatch.setenv("USD_RUB_RATE", "100")
    monkeypatch.setenv("REF_BUYER_FIRST_ORDER_DISCOUNT_PERCENT", "10")
    monkeypatch.setenv("STARS_WHOLESALE_THRESHOLD", "500")
    monkeypatch.setenv("STARS_WHOLESALE_DISCOUNT_PERCENT", "5")
    s = load_settings()
    p100 = catalog.Product(
        id="stars_100", kind="stars", title="100", emoji="⭐", price_usd=1.0, stars=100
    )
    q_first = quote_product(p100, s, is_first_order=True)
    assert q_first.rub_list == 100.0
    assert q_first.rub_referral_discount == 10.0
    assert q_first.rub_final == 90.0
    q_next = quote_product(p100, s, is_first_order=False)
    assert q_next.rub_referral_discount == 0.0
    assert q_next.rub_final == 100.0
    big = catalog.Product(
        id="stars_5000", kind="stars", title="5k", emoji="⭐", price_usd=50.0, stars=5000
    )
    qw = quote_product(big, s, is_first_order=False)
    assert qw.rub_wholesale_discount > 0


def test_commission_for_first_order(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:x")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "k" * 32)
    monkeypatch.setenv("REF_REFERRER_COMMISSION_FIRST_ORDER_PERCENT", "12")
    s = load_settings()
    assert commission_for_first_order(1000.0, s) == pytest.approx(120.0)


def test_rub_per_100_stars_display() -> None:
    s = Settings(BOT_TOKEN="9:x", ADMIN_IDS="1", API_KEY_PEPPER="k" * 32, USD_RUB_RATE=97.5)
    pmap = catalog.products_by_id(catalog.load_products(PRODUCTS_YAML))
    products = list(pmap.values())
    v = rub_per_100_stars_display(products, s, is_first_order=False)
    assert v is not None and v > 0


def test_effective_usdt_rub_rate_fallback() -> None:
    s = Settings(
        BOT_TOKEN="9:x",
        ADMIN_IDS="1",
        API_KEY_PEPPER="k" * 32,
        USD_RUB_RATE=90.0,
        USDT_RUB_RATE=0.0,
    )
    assert effective_usdt_rub_rate(s) == 90.0
    s2 = Settings(
        BOT_TOKEN="9:x",
        ADMIN_IDS="1",
        API_KEY_PEPPER="k" * 32,
        USD_RUB_RATE=90.0,
        USDT_RUB_RATE=88.0,
    )
    assert effective_usdt_rub_rate(s2) == 88.0


def test_fx_payment_hints_contains_usdt_and_optional_uah() -> None:
    s = Settings(
        BOT_TOKEN="9:x",
        ADMIN_IDS="1",
        API_KEY_PEPPER="k" * 32,
        USD_RUB_RATE=100.0,
        USDT_RUB_RATE=100.0,
        DISPLAY_USD_UAH_RATE=42.0,
        DISPLAY_USD_BYN_RATE=0.0,
    )
    html = fx_payment_hints_html(s, rub_final=1000.0, usd_base=10.0)
    assert "USDT" in html
    assert "UAH" in html


def test_channel_gate_flags() -> None:
    off = Settings(BOT_TOKEN="9:x", ADMIN_IDS="1", API_KEY_PEPPER="k" * 32, REQUIRED_CHANNEL_ID="")
    assert cg.channel_gate_enabled(off) is False
    assert cg.normalized_channel_id(off) is None
    on = Settings(
        BOT_TOKEN="9:x",
        ADMIN_IDS="1",
        API_KEY_PEPPER="k" * 32,
        REQUIRED_CHANNEL_ID="@shop",
        REQUIRED_CHANNEL_INVITE_URL="https://t.me/+test",
    )
    assert cg.channel_gate_enabled(on) is True
    assert cg.normalized_channel_id(on) == "@shop"


def test_marketing_onboarding_contains_config_percents(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:m")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "m" * 32)
    monkeypatch.setenv("MARKETING_MAX_DISCOUNT_PERCENT", "40")
    monkeypatch.setenv("REF_BUYER_FIRST_ORDER_DISCOUNT_PERCENT", "8")
    monkeypatch.setenv("REF_REFERRER_COMMISSION_FIRST_ORDER_PERCENT", "14")
    s = load_settings()
    html = marketing.onboarding_screen_1_html(s)
    assert "40" in html and "8" in html and "14" in html
    assert "Почему мы" in marketing.why_us_block_html(s)


def test_channel_hint_empty_without_channel(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:m")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "m" * 32)
    monkeypatch.delenv("REQUIRED_CHANNEL_ID", raising=False)
    s = load_settings()
    assert marketing.channel_hint_html(s) == ""


def test_settings_parsed_admin_ids_and_lava_services(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:x")
    monkeypatch.setenv("ADMIN_IDS", "1; 2 , 3")
    monkeypatch.setenv("API_KEY_PEPPER", "k" * 32)
    monkeypatch.setenv("LAVA_INCLUDE_SERVICES", "card; sbp")
    s = load_settings()
    assert s.parsed_admin_ids() == {1, 2, 3}
    assert s.lava_include_services_list() == ["card", "sbp"]


@pytest.fixture
def partner_api_http_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "api_smoke.db"))
    monkeypatch.setenv("BOT_TOKEN", "9:api-smoke")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "api_smoke_test_pepper_minimum_32_chars_")
    with TestClient(create_app()) as client:
        yield client


def test_partner_api_health_and_openapi(partner_api_http_client: TestClient) -> None:
    r = partner_api_http_client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"
    r2 = partner_api_http_client.get("/openapi.json")
    assert r2.status_code == 200
    data = r2.json()
    assert "paths" in data
    assert any("/v1/orders" in p for p in data["paths"])


@pytest.mark.asyncio
async def test_database_has_orders_and_payment_events_tables(conn) -> None:
    cur = await conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    names = {row[0] for row in await cur.fetchall()}
    assert "orders" in names
    assert "users" in names
    assert "payment_provider_events" in names
