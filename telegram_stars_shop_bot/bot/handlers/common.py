from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import Settings
from bot.handlers.hub import orders_first_page_html, profile_body_html
from bot.keyboards.shop_kb import hub_menu_kb, onboarding_step1_kb
from bot.services.channel_gate import channel_gate_enabled, user_is_channel_member
from bot.services.marketing import onboarding_screen_1_html
from bot.services import users_repo
from bot.ui_copy import ONBOARDING_SCREEN_2

router = Router(name="common")


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
    cap = onboarding_screen_1_html(settings)
    fid = (settings.start_photo_file_id or "").strip()
    kb = onboarding_step1_kb(settings)
    if fid:
        await message.answer_photo(fid, caption=cap, reply_markup=kb)
    else:
        await message.answer(cap, reply_markup=kb)


@router.message(Command("my"))
async def cmd_my(message: Message, settings: Settings, conn) -> None:
    text = await profile_body_html(message.bot, settings, conn, message.from_user.id)
    await message.answer(text, reply_markup=hub_menu_kb())


@router.message(Command("orders"))
async def cmd_orders(message: Message, conn) -> None:
    text = await orders_first_page_html(conn, message.from_user.id)
    await message.answer(text, reply_markup=hub_menu_kb())


@router.message(Command("menu"))
async def cmd_menu(message: Message, settings: Settings) -> None:
    """Открывает тот же хаб с 10 карточками, что и кнопка «Далее»."""
    if channel_gate_enabled(settings) and not await user_is_channel_member(
        message.bot, settings, message.from_user.id
    ):
        inv = (settings.required_channel_invite_url or "").strip()
        b = InlineKeyboardBuilder()
        if inv:
            b.row(InlineKeyboardButton(text="📢 Подписаться на канал", url=inv))
        b.row(InlineKeyboardButton(text="✅ Я подписался — открыть меню", callback_data="start:hub"))
        await message.answer(
            "<b>Сначала канал магазина</b>\n\n"
            "Подпишитесь на канал — так вы не пропустите акции и конкурсы партнёров. "
            "После подписки нажмите кнопку ниже.",
            reply_markup=b.as_markup(),
        )
        return
    await message.answer(ONBOARDING_SCREEN_2, reply_markup=hub_menu_kb())
