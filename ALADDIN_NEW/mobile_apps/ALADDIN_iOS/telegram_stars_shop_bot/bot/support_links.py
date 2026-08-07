from __future__ import annotations

from urllib.parse import quote

from bot import brand_constants as brand
from bot.config import Settings


def telegram_support_base(settings: Settings) -> str | None:
    """База для ссылок в Telegram: SUPPORT_URL или https://t.me/SUPPORT_USERNAME."""
    raw = (settings.support_url or "").strip()
    if raw:
        return raw.rstrip("/")
    un = (settings.support_username or "").strip().lstrip("@")
    if un:
        return f"https://t.me/{un}"
    return None


def is_telegram_contact(base: str) -> bool:
    b = base.lower()
    return "t.me/" in b


def support_url_is_shop_bot_loop(settings: Settings) -> bool:
    """
    True если SUPPORT_* ведёт на сам магазинный бот (петля для Lava/клиента).
    В этом случае обращения принимаем внутри бота → тикет только админам.
    """
    base = telegram_support_base(settings)
    if not base:
        return True
    b = base.lower().rstrip("/")
    shop = brand.SHOP_BOT_USERNAME.lower()
    if shop in b:
        return True
    un = (settings.support_username or "").strip().lstrip("@").lower()
    if un and un == shop:
        return True
    return False


def external_human_support_url(settings: Settings) -> str | None:
    """Внешний URL человека/инбокса — только если это не петля на shop-бот."""
    if support_url_is_shop_bot_loop(settings):
        return None
    base = telegram_support_base(settings)
    if not base:
        return None
    return base


def support_prefill_url(settings: Settings, text: str) -> str | None:
    """Ссылка с префиллом текста (только для внешнего t.me, не shop-бот)."""
    base = external_human_support_url(settings)
    if not base or not is_telegram_contact(base):
        return None
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}text={quote(text)}"


def support_order_question_url(settings: Settings, order_id: int) -> str | None:
    return support_prefill_url(settings, f"Вопрос по заказу #{order_id}")
