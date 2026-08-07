"""Feature flag / admin-only gate (R12)."""

from __future__ import annotations

from bot.config import Settings


def assistant_feature_allowed(user_id: int, settings: Settings) -> bool:
    """True если пользователь может пользоваться помощником."""
    if not bool(getattr(settings, "assistant_enabled", False)):
        return False
    if bool(getattr(settings, "assistant_admin_only", True)):
        return int(user_id) in settings.parsed_admin_ids()
    return True


def assistant_menu_visible(user_id: int | None, settings: Settings | None) -> bool:
    """Кнопка «Помощник» в меню: только при flag ON (+ admin gate)."""
    if settings is None or user_id is None:
        return False
    return assistant_feature_allowed(int(user_id), settings)


def assistant_disabled_user_html() -> str:
    return (
        "<b>🤖 AI Помощник</b>\n\n"
        "Сейчас помощник недоступен. Откройте раздел <b>Поддержка</b> "
        "или напишите человеку через кнопку ниже."
    )
