from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

from bot.config import Settings
from bot.handlers.hub import orders_first_page_html, profile_body_html
from bot.keyboards.shop_kb import (
    channel_member_open_menu_kb,
    channel_subscribe_kb,
    hub_menu_kb,
    onboarding_step1_kb,
)
from bot.services.channel_gate import channel_gate_enabled, user_is_channel_member
from bot.services.marketing import (
    CHANNEL_GATE_PHOTO_CAPTION_MAX,
    channel_hard_wall_html,
    channel_subscribe_after_greeting_html,
    channel_start_member_ack_html,
    onboarding_screen_1_html,
)
from bot.services import users_repo
from bot.ui_copy import ONBOARDING_SCREEN_2

router = Router(name="common")


async def _send_channel_gate_screen(message: Message, settings: Settings, *, compact_after_greeting: bool = False) -> None:
    """Экран подписки: полный или компактный (после отдельного приветствия на /start)."""
    text = channel_subscribe_after_greeting_html(settings) if compact_after_greeting else channel_hard_wall_html(settings)
    kb = channel_subscribe_kb(settings)
    fid = (settings.start_photo_file_id or "").strip()
    if fid and len(text) <= CHANNEL_GATE_PHOTO_CAPTION_MAX:
        await message.answer_photo(fid, caption=text, reply_markup=kb)
        return
    if fid:
        await message.answer_photo(fid)
    await message.answer(text, reply_markup=kb)


async def _reply_channel_gate_or_none(message: Message, settings: Settings) -> bool:
    """True = пользователь в канале или гейт выключен. False = отправили экран подписки."""
    if not channel_gate_enabled(settings):
        return True
    if await user_is_channel_member(message.bot, settings, message.from_user.id):
        return True
    await _send_channel_gate_screen(message, settings)
    return False


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, settings: Settings, conn) -> None:
    await users_repo.upsert_user(
        conn,
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )
    payload = (command.args or "").strip()
    if payload.startswith("ref_"):
        raw = payload.removeprefix("ref_")
        try:
            ref_id = int(raw)
            await users_repo.set_referrer_if_empty(conn, user_id=message.from_user.id, referrer_id=ref_id)
        except ValueError:
            pass
    if channel_gate_enabled(settings):
        # Старт: одна hero-карточка + проверка подписки/доступа к меню.
        cap = onboarding_screen_1_html(settings)
        fid = (settings.start_photo_file_id or "").strip()
        if fid:
            await message.answer_photo(fid, caption=cap)
        else:
            await message.answer(cap)
        if not await user_is_channel_member(message.bot, settings, message.from_user.id):
            await _send_channel_gate_screen(message, settings, compact_after_greeting=True)
            return
        seen_ack = await users_repo.has_seen_channel_member_ack(conn, message.from_user.id)
        if not seen_ack:
            await message.answer(
                channel_start_member_ack_html(settings),
                reply_markup=channel_member_open_menu_kb(settings),
            )
            await users_repo.mark_channel_member_ack_seen(conn, message.from_user.id)
            return
        await message.answer(ONBOARDING_SCREEN_2, reply_markup=hub_menu_kb())
        return
    cap = onboarding_screen_1_html(settings)
    fid = (settings.start_photo_file_id or "").strip()
    kb = onboarding_step1_kb(settings)
    if fid:
        await message.answer_photo(fid, caption=cap, reply_markup=kb)
    else:
        await message.answer(cap, reply_markup=kb)


@router.message(Command("my"))
async def cmd_my(message: Message, settings: Settings, conn) -> None:
    if not await _reply_channel_gate_or_none(message, settings):
        return
    text = await profile_body_html(message.bot, settings, conn, message.from_user.id)
    await message.answer(text, reply_markup=hub_menu_kb())


@router.message(Command("orders"))
async def cmd_orders(message: Message, settings: Settings, conn) -> None:
    if not await _reply_channel_gate_or_none(message, settings):
        return
    text = await orders_first_page_html(conn, message.from_user.id)
    await message.answer(text, reply_markup=hub_menu_kb())


@router.message(Command("menu"))
async def cmd_menu(message: Message, settings: Settings) -> None:
    """Открывает главный хаб (как после успешной проверки подписки на канал)."""
    if not await _reply_channel_gate_or_none(message, settings):
        return
    await message.answer(ONBOARDING_SCREEN_2, reply_markup=hub_menu_kb())
