"""UX hub compact menu + profile secondary (TZ 2026-07-30)."""

from __future__ import annotations

from types import SimpleNamespace

from bot.keyboards.shop_kb import hub_menu_kb, news_channel_url, profile_inline_kb_rows_prefix


def _settings(**kwargs):
    base = dict(
        ui_show_vpn=True,
        ui_show_partners=False,
        ui_show_api=False,
        ui_show_gifts=False,
        news_channel_page_url="https://t.me/news_test",
        required_channel_invite_url="",
        official_channel_invite_url="",
        vpn_news_channel_url="",
        parsed_admin_ids=lambda: set(),
        assistant_enabled=True,
        assistant_admin_only=False,
    )
    base.update(kwargs)
    return SimpleNamespace(**base)


def test_hub_compact_core_only() -> None:
    s = _settings()
    markup = hub_menu_kb(s, user_id=1)
    texts = [b.text for row in markup.inline_keyboard for b in row]
    assert texts.index("🛡 VPN") < texts.index("⭐ Stars")
    assert "💎 Premium" in texts
    assert "👤 Личный кабинет" in texts
    assert "👥 Пригласить друга" in texts
    for forbidden in (
        "📦 Заказы",
        "🏆 Конкурс",
        "📢 Новости",
        "💳 Пополнить",
        "🤖 AI Помощник",
        "👤 Профиль",
        "🛟 Поддержка",
    ):
        assert forbidden not in texts, forbidden


def test_profile_has_secondary() -> None:
    s = _settings()
    assert news_channel_url(s) == "https://t.me/news_test"
    rows = profile_inline_kb_rows_prefix(s)
    texts = [b.text for row in rows for b in row]
    assert "📦 Мои заказы" in texts
    assert "🏆 Конкурс" in texts
    assert "📢 Новости Бота" in texts
    assert "💳 Пополнить баланс" in texts
    assert "🛟 Поддержка" in texts


def test_vpn_9m_and_7d_hidden_from_list() -> None:
    from bot.services.catalog import Product
    from bot.services.vpn_tariffs import list_vpn_products

    products = [
        Product(
            id="vpn7",
            kind="vpn",
            title="7",
            emoji="🌐",
            price_usd=0.5,
            vpn_subscription_days=7,
            price_rub=50,
        ),
        Product(
            id="vpn30",
            kind="vpn",
            title="30",
            emoji="🌐",
            price_usd=2.0,
            vpn_subscription_days=30,
            price_rub=200,
        ),
        Product(
            id="vpn270",
            kind="vpn",
            title="9m",
            emoji="🌐",
            price_usd=12.0,
            vpn_subscription_days=270,
            price_rub=1200,
        ),
    ]
    shown = list_vpn_products(products)
    assert [p.id for p in shown] == ["vpn30"]
