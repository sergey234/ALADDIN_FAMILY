"""Видимость карточек меню: флаги .env + обход для админов (VPN)."""

from __future__ import annotations

from bot.config import Settings


def is_shop_admin(user_id: int, settings: Settings) -> bool:
    return user_id in settings.parsed_admin_ids()


def vpn_menu_visible(user_id: int, settings: Settings) -> bool:
    """Кнопка VPN в меню: UI_SHOW_VPN=true для всех, иначе только ADMIN_IDS."""
    if settings.ui_show_vpn:
        return True
    return is_shop_admin(user_id, settings)


def vpn_feature_allowed(user_id: int, settings: Settings) -> bool:
    """Доступ к разделу VPN (/vpn, nav:vpn): флаг или admin-bypass."""
    if settings.ui_show_vpn:
        return True
    return is_shop_admin(user_id, settings)


def gifts_menu_visible(settings: Settings) -> bool:
    return bool(settings.ui_show_gifts)
