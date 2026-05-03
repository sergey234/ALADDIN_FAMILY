"""Цепочка онбординга: оферта → канал → капча → главное меню."""

from __future__ import annotations

from bot.config import Settings
from bot.keyboards.shop_kb import hub_menu_kb, onboarding_channel_kb, onboarding_terms_kb
from bot.services import branding_media, emoji_captcha, users_repo
from bot.services.channel_gate import channel_gate_enabled, user_is_channel_member
from bot.services.marketing import CHANNEL_GATE_PHOTO_CAPTION_MAX, onboarding_channel_caption_html, onboarding_terms_caption_html
from bot.ui_copy import ONBOARDING_SCREEN_2


async def send_hub_welcome(bot, chat_id: int, settings: Settings) -> None:
    fid2 = (settings.start_photo_file_id_2 or "").strip()
    if fid2:
        await bot.send_photo(chat_id, fid2)
    await bot.send_message(chat_id, ONBOARDING_SCREEN_2, reply_markup=hub_menu_kb(settings))


async def send_terms_screen(bot, chat_id: int, settings: Settings) -> None:
    cap = onboarding_terms_caption_html(settings)
    kb = onboarding_terms_kb()
    photo = branding_media.hero_photo_input(settings)
    if photo is not None and len(cap) <= CHANNEL_GATE_PHOTO_CAPTION_MAX:
        await bot.send_photo(chat_id, photo, caption=cap, reply_markup=kb)
    else:
        await bot.send_message(chat_id, cap, reply_markup=kb)


async def send_channel_onboarding_screen(bot, chat_id: int, settings: Settings) -> None:
    cap = onboarding_channel_caption_html(settings)
    kb = onboarding_channel_kb(settings)
    photo = branding_media.hero_photo_input(settings)
    if photo is not None and len(cap) <= CHANNEL_GATE_PHOTO_CAPTION_MAX:
        await bot.send_photo(chat_id, photo, caption=cap, reply_markup=kb)
    else:
        await bot.send_message(chat_id, cap, reply_markup=kb)


async def resume_onboarding_pipeline(bot, chat_id: int, user_id: int, settings: Settings, conn) -> None:
    """Продолжить с текущего шага до хаба или показать следующий экран."""
    if not await users_repo.has_terms_accepted(conn, user_id):
        await send_terms_screen(bot, chat_id, settings)
        return
    if channel_gate_enabled(settings):
        if not await user_is_channel_member(bot, settings, user_id):
            await send_channel_onboarding_screen(bot, chat_id, settings)
            return
    if not await users_repo.is_onboarding_completed(conn, user_id):
        await emoji_captcha.send_onboarding_captcha_photo(
            bot, chat_id, conn=conn, settings=settings, user_id=user_id
        )
        return
    await send_hub_welcome(bot, chat_id, settings)
