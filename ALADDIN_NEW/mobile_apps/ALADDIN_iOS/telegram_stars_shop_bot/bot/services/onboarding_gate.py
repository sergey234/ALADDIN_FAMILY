"""Цепочка онбординга: канал+согласие → капча → главное меню."""

from __future__ import annotations

from bot.config import Settings
from bot.keyboards.shop_kb import hub_menu_kb, onboarding_combined_kb
from bot.services import emoji_captcha, users_repo
from bot.services.channel_gate import channel_gate_enabled, user_is_channel_member
from bot.services.marketing import onboarding_combined_caption_html
from bot.ui_copy import ONBOARDING_SCREEN_2


async def send_hub_welcome(bot, chat_id: int, settings: Settings, *, user_id: int) -> None:
    fid2 = (settings.start_photo_file_id_2 or "").strip()
    if fid2:
        await bot.send_photo(chat_id, fid2)
    await bot.send_message(
        chat_id,
        ONBOARDING_SCREEN_2,
        reply_markup=hub_menu_kb(settings, user_id=user_id),
    )


async def send_combined_onboarding_screen(bot, chat_id: int, settings: Settings) -> None:
    """Один экран без фото: подписка на канал + согласие (ссылки в тексте)."""
    await bot.send_message(
        chat_id,
        onboarding_combined_caption_html(settings),
        reply_markup=onboarding_combined_kb(settings),
        disable_web_page_preview=True,
    )


async def resume_onboarding_pipeline(bot, chat_id: int, user_id: int, settings: Settings, conn) -> None:
    """Продолжить с текущего шага до хаба или показать следующий экран."""
    terms_ok = await users_repo.has_terms_accepted(conn, user_id)
    need_channel = False
    if channel_gate_enabled(settings):
        need_channel = not await user_is_channel_member(bot, settings, user_id)
    if not terms_ok or need_channel:
        await send_combined_onboarding_screen(bot, chat_id, settings)
        return
    if not await users_repo.is_onboarding_completed(conn, user_id):
        await emoji_captcha.send_onboarding_captcha_photo(
            bot, chat_id, conn=conn, settings=settings, user_id=user_id
        )
        return
    await send_hub_welcome(bot, chat_id, settings, user_id=user_id)
