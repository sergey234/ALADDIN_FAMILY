from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from bot.config import Settings, load_settings
from bot.services import catalog, marketing
from bot.services import channel_gate as cg
from bot.services.fx_display import effective_usdt_rub_rate, fx_payment_hints_html
from bot.services.pricing import commission_for_first_order, list_price_rub, quote_product, rub_per_100_stars_display
from bot.handlers.vpn import vpn_marketing_html
from bot.services.vpn_tariffs import vpn_referral_blurb_html, vpn_tariffs_html
from partner_api.main import create_app

_REPO_BOT = Path(__file__).resolve().parents[1] / "bot"
PRODUCTS_YAML = _REPO_BOT / "products.yaml"


def test_products_yaml_loads_and_has_stars_and_premium() -> None:
    items = catalog.load_products(PRODUCTS_YAML)
    assert len(items) >= 4
    by_id = catalog.products_by_id(items)
    assert "stars_100" in by_id
    vpn_ids = {"vpn_30d", "vpn_90d", "vpn_180d", "vpn_270d", "vpn_365d"}
    assert vpn_ids <= set(by_id)
    assert by_id["vpn_30d"].price_rub == 290.0
    assert by_id["vpn_365d"].price_rub == 1200.0
    assert by_id["stars_100"].kind == "stars"
    assert (by_id["stars_100"].stars or 0) == 100
    premium = [p for p in items if p.kind == "premium"]
    assert premium, "expected at least one premium product"
    assert by_id["premium_1"].hide_from_menu is True
    menu_premium = [p for p in items if p.kind == "premium" and not p.hide_from_menu]
    menu_ids = {p.id for p in menu_premium}
    assert "premium_1" not in menu_ids
    assert {"premium_3", "premium_6", "premium_12"} <= menu_ids


def test_sort_for_display_orders_stars_by_quantity() -> None:
    a = catalog.Product(
        id="a", kind="stars", title="A", emoji="⭐", price_usd=1.0, stars=10, featured=False, sort_order=5
    )
    b = catalog.Product(
        id="b", kind="stars", title="B", emoji="⭐", price_usd=2.0, stars=20, featured=True, sort_order=9
    )
    out = catalog.sort_for_display([a, b])
    assert [x.id for x in out] == ["a", "b"]


def test_vpn_referral_blurb_uses_env_percents(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:vpn-ref")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "v" * 32)
    monkeypatch.setenv("REF_BUYER_FIRST_ORDER_DISCOUNT_PERCENT", "10")
    monkeypatch.setenv("REF_REFERRER_COMMISSION_FIRST_ORDER_PERCENT", "15")
    monkeypatch.setenv("VPN_REFERRAL_FRIEND_DAYS", "7")
    monkeypatch.setenv("VPN_REFERRAL_REFERRER_DAYS", "14")
    s = load_settings()
    html = vpn_referral_blurb_html(s)
    assert "Приглашение" in html
    assert "Мой профиль" in html
    assert "ref_" in html
    assert "AiMonkeyVPN" in html


def test_vpn_tariffs_html_lists_fixed_rub(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:vpn-t")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "t" * 32)
    monkeypatch.setenv("USD_RUB_RATE", "80")
    s = load_settings()
    items = catalog.load_products(PRODUCTS_YAML)
    html = vpn_tariffs_html(s, items)
    assert "290" in html
    assert "750" in html
    assert "экономия" in html


def test_vpn_marketing_welcome_copy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:vpn-mkt")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "m" * 32)
    monkeypatch.setenv("VPN_DOCS_PUBLIC_BASE", "https://aladdin-ai.ru/v1/legal")
    s = load_settings()
    html = vpn_marketing_html(s)
    assert "Привет! Я AiMonkeyVPN" in html
    assert "10 Гбит/с" in html
    assert "не храним" in html
    assert "не продаём" in html
    assert "Telegram" in html
    assert "Политика конфиденциальности" in html
    assert "Пользовательское соглашение" in html
    assert "legal/vpn-data" in html
    assert "legal/vpn-terms" in html


def test_vpn_price_rub_fixed_against_usd_rate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:vpn-rub")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "vpn_rub_test_pepper_minimum_32_chars")
    monkeypatch.setenv("USD_RUB_RATE", "200")
    s = load_settings()
    items = catalog.load_products(PRODUCTS_YAML)
    p = catalog.products_by_id(items)["vpn_90d"]
    assert list_price_rub(p, s) == 750.0
    q = quote_product(p, s, is_first_order=True)
    assert q.rub_list == 750.0
    assert q.rub_referral_discount == 75.0
    assert q.rub_final == 675.0
    assert q.usd == pytest.approx(3.75)  # 750 / USD_RUB_RATE 200


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
    s = Settings(BOT_TOKEN="9:x", ADMIN_IDS="1", API_KEY_PEPPER="k" * 32, USD_RUB_RATE=75.237)
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


def test_fx_payment_hints_contains_usdt_rub_only() -> None:
    s = Settings(
        BOT_TOKEN="9:x",
        ADMIN_IDS="1",
        API_KEY_PEPPER="k" * 32,
        USD_RUB_RATE=100.0,
        USDT_RUB_RATE=100.0,
    )
    html = fx_payment_hints_html(s, rub_final=1000.0, usd_base=10.0)
    assert "USDT" in html
    assert "TRC20" in html
    assert "UAH" not in html and "BYN" not in html


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
    assert "Telegram Stars и Premium" in html
    assert "быстро и выгодно" in html
    assert "пару кликов" in html
    assert "Надёжно. Удобно. Быстро." in html
    assert "Почему мы" in marketing.why_us_block_html(s)


def test_channel_hard_wall_html_display_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:m")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "m" * 32)
    monkeypatch.setenv("REQUIRED_CHANNEL_ID", "@shop")
    monkeypatch.setenv("REQUIRED_CHANNEL_DISPLAY_NAME", "AIMonkey Stars | Premium")
    monkeypatch.setenv("REQUIRED_CHANNEL_GATE_MARKETING", "full")
    s = load_settings()
    html = marketing.channel_hard_wall_html(s)
    assert "AIMonkey Stars" in html and "Premium" in html
    assert "меню бота" in html
    assert "Почему мы" in html
    assert "Telegram Stars и Premium" in html


def test_channel_start_member_ack_contains_display_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:m")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "m" * 32)
    monkeypatch.setenv("REQUIRED_CHANNEL_ID", "@shop")
    monkeypatch.setenv("REQUIRED_CHANNEL_DISPLAY_NAME", "Monkey Test")
    s = load_settings()
    h = marketing.channel_start_member_ack_html(s)
    assert "Monkey Test" in h
    assert "закрепе" in h




@pytest.mark.asyncio
async def test_channel_member_ack_seen_flag_roundtrip(conn) -> None:
    from bot.services import users_repo

    uid = 777001
    await users_repo.upsert_user(conn, user_id=uid, username="u", first_name="n")
    assert await users_repo.has_seen_channel_member_ack(conn, uid) is False
    await users_repo.mark_channel_member_ack_seen(conn, uid)
    assert await users_repo.has_seen_channel_member_ack(conn, uid) is True

def test_channel_hard_wall_gate_marketing_modes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:m")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "m" * 32)
    monkeypatch.setenv("REQUIRED_CHANNEL_ID", "@shop")
    monkeypatch.setenv("REQUIRED_CHANNEL_DISPLAY_NAME", "X")
    monkeypatch.setenv("REQUIRED_CHANNEL_GATE_MARKETING", "short")
    s = load_settings()
    h = marketing.channel_hard_wall_html(s)
    assert "Почему мы" not in h
    assert "AIMonkeyStars" in h
    assert "@AiMonkeyStars_bot" in h
    assert "закрепе канала" in h
    assert "7" in h or "47" in h  # проценты из дефолтных настроек теста
    monkeypatch.setenv("REQUIRED_CHANNEL_GATE_MARKETING", "title_only")
    s2 = load_settings()
    h2 = marketing.channel_hard_wall_html(s2)
    assert "Почему мы" not in h2
    assert "Stars, Premium" in h2


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


def test_legal_static_pages(partner_api_http_client: TestClient) -> None:
    r = partner_api_http_client.get("/v1/legal/privacy")
    assert r.status_code == 200
    assert "07 мая 2026" in r.text
    assert "AiMonkeyStars_bot" in r.text
    assert "ИП «AiMonkeyStars»" in r.text
    r2 = partner_api_http_client.get("/v1/legal/terms")
    assert r2.status_code == 200
    assert "Пользовательское соглашение" in r2.text
    assert "Республики Казахстан" in r2.text
    assert "AiMonkeyStars_bot" in r2.text


def test_privacy_screen_includes_policy_links(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:leg")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "leg_test_pepper_minimum_32_chars_____")
    monkeypatch.setenv(
        "PRIVACY_POLICY_URL",
        "https://aladdin-ai.ru/v1/legal/privacy",
    )
    monkeypatch.setenv(
        "TERMS_OF_SERVICE_URL",
        "https://aladdin-ai.ru/v1/legal/terms",
    )
    s = load_settings()
    html = marketing.privacy_screen_html(s)
    assert "legal/privacy" in html
    assert "legal/terms" in html
    assert "Поддержка" in html


def test_payment_faq_no_env_jargon(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:pfq")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "pfq_test_pepper_minimum_32_chars_____")
    s = load_settings()
    html = marketing.payment_faq_html(s)
    assert "Stars" in html or "Premium" in html
    assert "ORDER" in html  # memo code for users
    assert ".env" not in html
    assert "USDT_RUB" not in html
    assert "ORDER_PENDING" not in html


def test_payment_faq_universal_block_when_bc_url_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:uni")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "uni_test_pepper_minimum_32_chars_____")
    monkeypatch.setenv("CKASSA_BC_UNIVERSAL_PAYMENT_URL", "https://bc.ckassa.ru/demo")
    s = load_settings()
    html = marketing.payment_faq_html(s)
    assert "Оплата по ссылке Ckassa" in html
    assert ".env" not in html


def test_channel_pin_bc_checkout_html_when_url_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:pin")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "pin_test_pepper_minimum_32_chars_____")
    monkeypatch.setenv("CKASSA_BC_UNIVERSAL_PAYMENT_URL", "https://bc.ckassa.ru/x")
    s = load_settings()
    html = marketing.channel_pin_bc_checkout_html(s)
    assert "минимум" in html.lower() or "50" in html
    assert "ORDER" in html


def test_fiat_checkout_options_kb_urls_and_home() -> None:
    from bot.keyboards.shop_kb import fiat_checkout_options_kb

    m = fiat_checkout_options_kb(
        universal_url="https://bc.example/x",
        ckassa_shop_url="https://shop.ckassa.example/p",
        lava_url="https://lava.example/i",
        bc_claim_order_id=42,
        support_order_url="https://t.me/support?text=order42",
    )
    assert len(m.inline_keyboard) == 6
    assert m.inline_keyboard[-1][0].callback_data == "nav:hub"
    assert m.inline_keyboard[-2][0].url == "https://t.me/support?text=order42"
    assert m.inline_keyboard[-3][0].callback_data == "pay:bcc:42"
    assert m.inline_keyboard[0][0].url == "https://bc.example/x"


def test_faq_comprehensive_uses_referral_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:faq")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "faq_test_pepper_minimum_32_chars_____")
    monkeypatch.setenv("REF_REFERRER_COMMISSION_FIRST_ORDER_PERCENT", "10")
    monkeypatch.setenv("REF_BUYER_FIRST_ORDER_DISCOUNT_PERCENT", "5")
    s = load_settings()
    html = marketing.faq_comprehensive_html(s)
    assert "Частые вопросы" in html
    assert "10.0%" in html
    assert "5.0%" in html
    assert "Unverified token" in html


@pytest.mark.asyncio
async def test_database_has_orders_and_payment_events_tables(conn) -> None:
    cur = await conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    names = {row[0] for row in await cur.fetchall()}
    assert "orders" in names
    assert "users" in names
    assert "payment_provider_events" in names
