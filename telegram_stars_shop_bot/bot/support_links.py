from __future__ import annotations

from urllib.parse import quote

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


def support_prefill_url(settings: Settings, text: str) -> str | None:
    """Ссылка с префиллом текста (только для t.me)."""
    base = telegram_support_base(settings)
    if not base or not is_telegram_contact(base):
        return None
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}text={quote(text)}"


def support_order_question_url(settings: Settings, order_id: int) -> str | None:
    return support_prefill_url(settings, f"Вопрос по заказу #{order_id}")
