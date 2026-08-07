from __future__ import annotations

from bot.config import Settings
from bot.keyboards.shop_kb import news_channel_url


def test_news_prefers_official_channel_not_aladdin_site() -> None:
    s = Settings(
        BOT_TOKEN="x",
        VPN_API_HMAC_SECRET="sec",
        NEWS_CHANNEL_PAGE_URL="https://aladdin-ai.ru/news.html",
        OFFICIAL_CHANNEL_INVITE_URL="https://t.me/+xwj4zZo4bNphZjVi",
        REQUIRED_CHANNEL_INVITE_URL="https://t.me/+xwj4zZo4bNphZjVi",
    )
    u = news_channel_url(s)
    assert u.startswith("https://t.me/")
    assert "aladdin-ai.ru" not in u


def test_news_empty_falls_to_required() -> None:
    s = Settings(
        BOT_TOKEN="x",
        VPN_API_HMAC_SECRET="sec",
        NEWS_CHANNEL_PAGE_URL="",
        OFFICIAL_CHANNEL_INVITE_URL="",
        REQUIRED_CHANNEL_INVITE_URL="https://t.me/+testchannel",
    )
    assert news_channel_url(s) == "https://t.me/+testchannel"
