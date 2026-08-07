"""Нижние 4 reply-кнопки не должны больше выдаваться."""

from __future__ import annotations

from aiogram.types import ReplyKeyboardRemove

from bot.keyboards.shop_kb import (
    LEGACY_REPLY_BUTTON_TEXTS,
    hub_menu_kb,
    reply_keyboard_remove,
)


def test_reply_keyboard_remove_type() -> None:
    kb = reply_keyboard_remove()
    assert isinstance(kb, ReplyKeyboardRemove)
    assert kb.remove_keyboard is True


def test_no_main_reply_kb_exported() -> None:
    import bot.keyboards.shop_kb as sk

    assert not hasattr(sk, "main_reply_kb")


def test_legacy_texts_cover_old_four_buttons() -> None:
    assert "🏠 Меню" in LEGACY_REPLY_BUTTON_TEXTS
    assert "👤 Профиль" in LEGACY_REPLY_BUTTON_TEXTS
    assert "👥 Друзья" in LEGACY_REPLY_BUTTON_TEXTS
    assert "❓ Помощь" in LEGACY_REPLY_BUTTON_TEXTS


def test_hub_menu_is_inline_not_reply() -> None:
    from types import SimpleNamespace

    settings = SimpleNamespace(
        ui_show_vpn=True,
        ui_show_gifts=False,
        ui_show_api=False,
        ui_show_contest=False,
        assistant_enabled=False,
        news_channel_page_url="",
        required_channel_invite_url="",
        official_channel_invite_url="",
        parsed_admin_ids=lambda: set(),
    )
    markup = hub_menu_kb(settings, user_id=1)
    # InlineKeyboardMarkup has inline_keyboard; Reply would have keyboard
    assert hasattr(markup, "inline_keyboard")
    assert not hasattr(markup, "keyboard") or markup.keyboard is None
