from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message

from bot.config import Settings
from bot.handlers.hub import orders_first_page_html, profile_body_html
from bot.keyboards.shop_kb import (
    channel_member_open_menu_kb,
    channel_subscribe_kb,
    hub_menu_kb,
    onboarding_language_kb,
)
from bot.services import branding_media, captcha_repo, onboarding_gate, users_repo
from bot.services.channel_gate import channel_gate_enabled, user_is_channel_member
from bot.services.marketing import (
    CHANNEL_GATE_PHOTO_CAPTION_MAX,
    channel_hard_wall_html,
    channel_subscribe_after_greeting_html,
)
from bot.services import analytics_repo
from bot.ui_copy import LANGUAGE_SELECTION_CAPTION_HTML, ONBOARDING_SCREEN_2

router = Router(name="common")


async def _send_channel_gate_to_chat(chat_id: int, bot, settings: Settings, *, compact_after_greeting: bool = False) -> None:
    """Экран подписки в чат (message.answer* или bot.send_*)."""
    text = channel_subscribe_after_greeting_html(settings) if compact_after_greeting else channel_hard_wall_html(settings)
    kb = channel_subscribe_kb(settings)
    photo = branding_media.hero_photo_input(settings)
    if photo is not None and len(text) <= CHANNEL_GATE_PHOTO_CAPTION_MAX:
        await bot.send_photo(chat_id, photo, caption=text, reply_markup=kb)
        return
    if photo is not None:
        await bot.send_photo(chat_id, photo)
    await bot.send_message(chat_id, text, reply_markup=kb)


async def _send_channel_gate_screen(message: Message, settings: Settings, *, compact_after_greeting: bool = False) -> None:
    """Экран подписки: полный или компактный (после отдельного приветствия на /start)."""
    await _send_channel_gate_to_chat(message.chat.id, message.bot, settings, compact_after_greeting=compact_after_greeting)


async def _send_language_pick(message: Message, settings: Settings) -> None:
    """Шаг 0: язык; основное фото — брендовый лого-файл из assets/branding."""
    kb = onboarding_language_kb()
    caption = LANGUAGE_SELECTION_CAPTION_HTML
    photo = branding_media.hero_photo_input(settings)
    if photo is not None and len(caption) <= CHANNEL_GATE_PHOTO_CAPTION_MAX:
        await message.answer_photo(photo, caption=caption, reply_markup=kb)
        return
    await message.answer(caption, reply_markup=kb)


async def ensure_shop_access(message: Message, settings: Settings, conn) -> bool:
    """Онбординг завершён и (если включено) есть подписка на канал."""
    uid = message.from_user.id
    if not await users_repo.is_onboarding_completed(conn, uid):
        await onboarding_gate.resume_onboarding_pipeline(message.bot, message.chat.id, uid, settings, conn)
        return False
    if not channel_gate_enabled(settings):
        return True
    if await user_is_channel_member(message.bot, settings, uid):
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
    if not await users_repo.throttle_start_allowed(
        conn, message.from_user.id, int(settings.start_command_min_interval_seconds)
    ):
        await message.answer("Подождите секунду перед следующим /start.")
        return
    try:
        await analytics_repo.log_event(
            conn,
            user_id=message.from_user.id,
            event_type="bot_entry",
            meta={"via": "start"},
        )
    except Exception:
        pass
    payload = (command.args or "").strip()
    if payload.startswith("ref_"):
        raw = payload.removeprefix("ref_")
        try:
            ref_id = int(raw)
            await users_repo.set_referrer_if_empty(conn, user_id=message.from_user.id, referrer_id=ref_id)
        except ValueError:
            pass
    if await users_repo.get_locale(conn, message.from_user.id) is None:
        await _send_language_pick(message, settings)
        return
    await onboarding_gate.resume_onboarding_pipeline(
        message.bot,
        message.chat.id,
        message.from_user.id,
        settings,
        conn,
    )


@router.callback_query(F.data.startswith("onb:lang:"))
async def onboarding_language_chosen(cb: CallbackQuery, settings: Settings, conn) -> None:
    code = (cb.data or "").split(":")[-1].strip().lower()
    if code not in ("ru", "en"):
        await cb.answer()
        return
    await users_repo.set_locale(conn, cb.from_user.id, code)
    await cb.answer()
    try:
        await cb.message.delete()
    except Exception:
        pass
    await onboarding_gate.resume_onboarding_pipeline(
        cb.bot,
        cb.message.chat.id,
        cb.from_user.id,
        settings,
        conn,
    )


@router.callback_query(F.data == "onb:terms:yes")
async def onboarding_terms_yes(cb: CallbackQuery, settings: Settings, conn) -> None:
    await users_repo.accept_terms(conn, cb.from_user.id)
    await cb.answer()
    try:
        await cb.message.delete()
    except Exception:
        pass
    await onboarding_gate.resume_onboarding_pipeline(
        cb.bot,
        cb.message.chat.id,
        cb.from_user.id,
        settings,
        conn,
    )


@router.callback_query(F.data == "onb:terms:no")
async def onboarding_terms_no(cb: CallbackQuery) -> None:
    await cb.answer(
        "Без согласия нельзя пользоваться магазином. Если передумаете — отправьте /start.",
        show_alert=True,
    )


@router.callback_query(F.data == "onb:ch:check")
async def onboarding_channel_check(cb: CallbackQuery, settings: Settings, conn) -> None:
    if channel_gate_enabled(settings) and not await user_is_channel_member(
        cb.bot, settings, cb.from_user.id
    ):
        await cb.answer(
            "Подписка не видна. Откройте канал по кнопке, подпишитесь и нажмите проверку снова.",
            show_alert=True,
        )
        return
    await cb.answer()
    try:
        await cb.message.delete()
    except Exception:
        pass
    await onboarding_gate.resume_onboarding_pipeline(
        cb.bot,
        cb.message.chat.id,
        cb.from_user.id,
        settings,
        conn,
    )


@router.callback_query(F.data.startswith("onb:c:"))
async def onboarding_captcha_pick(cb: CallbackQuery, settings: Settings, conn) -> None:
    parts = (cb.data or "").split(":")
    if len(parts) != 4:
        await cb.answer()
        return
    try:
        cid = int(parts[2])
        idx = int(parts[3])
    except ValueError:
        await cb.answer()
        return
    ok = await captcha_repo.take_challenge_if_correct(
        conn,
        challenge_id=cid,
        user_id=cb.from_user.id,
        purpose="onboarding",
        picked_idx=idx,
    )
    if not ok:
        await cb.answer("Попробуйте другой вариант.", show_alert=True)
        return
    await users_repo.complete_onboarding(conn, cb.from_user.id)
    await cb.answer()
    try:
        await cb.message.delete()
    except Exception:
        pass
    await onboarding_gate.send_hub_welcome(cb.bot, cb.message.chat.id, settings)


@router.callback_query(F.data.startswith("chk:c:"))
async def checkout_captcha_pick(cb: CallbackQuery, settings: Settings, conn) -> None:
    parts = (cb.data or "").split(":")
    if len(parts) != 4:
        await cb.answer()
        return
    try:
        cid = int(parts[2])
        idx = int(parts[3])
    except ValueError:
        await cb.answer()
        return
    ok = await captcha_repo.take_challenge_if_correct(
        conn,
        challenge_id=cid,
        user_id=cb.from_user.id,
        purpose="checkout",
        picked_idx=idx,
    )
    if not ok:
        await cb.answer("Попробуйте другой вариант.", show_alert=True)
        return
    await users_repo.extend_checkout_captcha(
        conn, cb.from_user.id, int(settings.checkout_captcha_ttl_seconds)
    )
    await cb.answer("Готово! Нажмите «Подтвердить заказ» ещё раз.")
    try:
        await cb.message.delete()
    except Exception:
        pass


@router.message(Command("my"))
async def cmd_my(message: Message, settings: Settings, conn) -> None:
    if not await ensure_shop_access(message, settings, conn):
        return
    text = await profile_body_html(message.bot, settings, conn, message.from_user.id)
    await message.answer(text, reply_markup=hub_menu_kb(settings))


@router.message(Command("orders"))
async def cmd_orders(message: Message, settings: Settings, conn) -> None:
    if not await ensure_shop_access(message, settings, conn):
        return
    text = await orders_first_page_html(conn, message.from_user.id)
    await message.answer(text, reply_markup=hub_menu_kb(settings))


@router.message(Command("menu"))
async def cmd_menu(message: Message, settings: Settings, conn) -> None:
    """Открывает главный хаб (как после успешной проверки подписки на канал)."""
    if not await ensure_shop_access(message, settings, conn):
        return
    try:
        await analytics_repo.log_event(
            conn,
            user_id=message.from_user.id,
            event_type="bot_entry",
            meta={"via": "menu"},
        )
    except Exception:
        pass
    await message.answer(ONBOARDING_SCREEN_2, reply_markup=hub_menu_kb(settings))
