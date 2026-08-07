from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import Settings
from bot.handlers.hub import orders_first_page_html, profile_body_html
from bot.handlers.shop import AWAITING_CHECKOUT_AFTER_CAPTCHA, finalize_checkout_order
from bot.keyboards.shop_kb import (
    LEGACY_REPLY_BUTTON_TEXTS,
    REPLY_BTN_PROFILE,
    REPLY_BTN_PROFILE_ALT,
    channel_member_open_menu_kb,
    channel_subscribe_kb,
    feedback_wishes_kb,
    hub_menu_kb,
    onboarding_language_kb,
    profile_inline_kb_rows_prefix,
    reply_keyboard_remove,
)
from bot.services import (
    acquisition_repo,
    analytics_repo,
    branding_media,
    captcha_repo,
    feedback_repo,
    onboarding_gate,
    users_repo,
    vpn_referral_repo,
)
from bot.services.post_order_feedback import (
    NEGATIVE_PROMPT_TEXT,
    WISHES_PROMPT_TEXT,
    feedback_order_scope,
)
from bot.services.feedback_ops_notify import notify_ops_user_feedback
from bot.services.catalog import Product
from bot.states.checkout import CheckoutStates, FeedbackStates
from bot.services.channel_gate import channel_gate_enabled, user_is_channel_member
from bot.services.marketing import (
    CHANNEL_GATE_PHOTO_CAPTION_MAX,
    channel_hard_wall_html,
    channel_subscribe_after_greeting_html,
)
from bot.ui_copy import LANGUAGE_SELECTION_CAPTION_HTML, ONBOARDING_SCREEN_2

router = Router(name="common")
logger = logging.getLogger(__name__)


async def strip_sticky_reply_keyboard(message: Message) -> None:
    """Снять залипшую нижнюю ReplyKeyboard (Меню/Профиль/Друзья/Помощь). Больше её не показываем."""
    try:
        ghost = await message.answer("\u200b", reply_markup=reply_keyboard_remove())
        try:
            await ghost.delete()
        except Exception:
            pass
    except Exception:
        logger.debug("strip_sticky_reply_keyboard failed", exc_info=True)


def _schedule_strip_sticky_reply_keyboard(message: Message) -> None:
    """Не блокировать TTFB первого /start двумя Telegram RTT."""
    try:
        asyncio.create_task(strip_sticky_reply_keyboard(message))
    except Exception:
        logger.debug("schedule strip_sticky_reply_keyboard failed", exc_info=True)


async def _send_channel_gate_to_chat(chat_id: int, bot, settings: Settings, *, compact_after_greeting: bool = False) -> None:
    """Экран подписки в чат (message.answer* или bot.send_*)."""
    text = channel_subscribe_after_greeting_html(settings) if compact_after_greeting else channel_hard_wall_html(settings)
    kb = channel_subscribe_kb(settings)
    photo = branding_media.hero_photo_input(settings)
    if photo is not None and len(text) <= CHANNEL_GATE_PHOTO_CAPTION_MAX:
        sent = await bot.send_photo(chat_id, photo, caption=text, reply_markup=kb)
        branding_media.remember_hero_file_id_from_message(sent)
        return
    if photo is not None:
        sent = await bot.send_photo(chat_id, photo)
        branding_media.remember_hero_file_id_from_message(sent)
    await bot.send_message(chat_id, text, reply_markup=kb)


async def _send_channel_gate_screen(message: Message, settings: Settings, *, compact_after_greeting: bool = False) -> None:
    """Экран подписки: полный или компактный (после отдельного приветствия на /start)."""
    await _send_channel_gate_to_chat(message.chat.id, message.bot, settings, compact_after_greeting=compact_after_greeting)


async def _send_language_pick(message: Message, settings: Settings) -> None:
    """Шаг 0: язык; фото — file_id / кэш / локальный лого."""
    kb = onboarding_language_kb()
    caption = LANGUAGE_SELECTION_CAPTION_HTML
    photo = branding_media.hero_photo_input(settings)
    if photo is not None and len(caption) <= CHANNEL_GATE_PHOTO_CAPTION_MAX:
        sent = await message.answer_photo(photo, caption=caption, reply_markup=kb)
        branding_media.remember_hero_file_id_from_message(sent)
        return
    await message.answer(caption, reply_markup=kb)


async def _start_side_effects(
    conn,
    settings: Settings,
    *,
    user_id: int,
    payload: str,
) -> None:
    """Analytics / account / acquisition — не на критическом пути до UI."""
    try:
        await analytics_repo.log_event(
            conn,
            user_id=user_id,
            event_type="bot_entry",
            meta={"via": "start"},
        )
    except Exception:
        pass

    try:
        from bot.services import accounts_repo as _acc_repo

        await _acc_repo.ensure_account_for_telegram(
            conn, telegram_user_id=user_id, created_via="telegram"
        )
    except Exception:
        pass

    acq_meta = acquisition_repo.parse_start_payload(payload)
    if payload.startswith("ref_"):
        acq_meta["source"] = "referral"
        acq_meta["product_hint"] = acq_meta.get("product_hint") or "shop"
    elif payload.startswith("r_") or payload.startswith("r-"):
        acq_meta["source"] = "referral"
        acq_meta["product_hint"] = acq_meta.get("product_hint") or "vpn"
    try:
        await acquisition_repo.touch_user_acquisition(
            conn,
            user_id=user_id,
            source=acq_meta.get("source", "unknown"),
            campaign=acq_meta.get("campaign", ""),
            creative=acq_meta.get("creative", ""),
        )
    except Exception:
        pass
    try:
        await analytics_repo.log_event(
            conn,
            user_id=user_id,
            event_type="offer_impression",
            meta=acq_meta,
        )
    except Exception:
        pass
    if payload.startswith("ref_"):
        raw = payload.removeprefix("ref_")
        try:
            ref_id = int(raw)
            await users_repo.set_referrer_if_empty(conn, user_id=user_id, referrer_id=ref_id)
        except ValueError:
            pass
    elif payload.startswith("r_") or payload.startswith("r-"):
        sep = "r_" if payload.startswith("r_") else "r-"
        code = payload[len(sep) :].strip()
        if code:
            owner = await vpn_referral_repo.resolve_code_owner(conn, code)
            if owner is not None:
                await users_repo.set_referrer_if_empty(conn, user_id=user_id, referrer_id=owner)
                try:
                    await analytics_repo.log_event(
                        conn,
                        user_id=user_id,
                        event_type="vpn_ref_link_open",
                        meta={"code": code[:32]},
                    )
                except Exception:
                    pass


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
    # Не блокируем первый UI: strip в фоне (2 Telegram RTT).
    _schedule_strip_sticky_reply_keyboard(message)
    payload = (command.args or "").strip()

    # Web→Telegram account link (get.aladdin-ai.ru) — before /start throttle.
    if payload.startswith("link_"):
        from bot.services import accounts_repo, vpn_api_client

        code = payload.removeprefix("link_").strip()
        logger.info(
            "web_link_start user_id=%s code_len=%s",
            message.from_user.id,
            len(code),
        )
        status_code, detail, from_subject = await accounts_repo.consume_link_token(
            conn, code=code, telegram_user_id=message.from_user.id
        )
        await accounts_repo.ensure_account_for_telegram(
            conn, telegram_user_id=message.from_user.id, created_via="telegram"
        )
        logger.info(
            "web_link_consume user_id=%s status=%s detail=%s from_subject=%s",
            message.from_user.id,
            status_code,
            detail,
            from_subject,
        )
        if status_code in ("ok", "merged"):
            bind_ok = True
            bind_msg = ""
            try:
                if from_subject is not None:
                    bind_ok, bind_msg = await vpn_api_client.post_bind_telegram(
                        settings,
                        shop_account_id=str(detail),
                        from_telegram_user_id=int(from_subject),
                        to_telegram_user_id=int(message.from_user.id),
                    )
            except Exception:
                bind_ok = False
                bind_msg = "exception"
                logger.exception(
                    "web_link_bind_telegram_failed user_id=%s account=%s from_subject=%s",
                    message.from_user.id,
                    detail,
                    from_subject,
                )
            if not bind_ok:
                logger.warning(
                    "web_link_bind_telegram_not_ok user_id=%s account=%s msg=%s",
                    message.from_user.id,
                    detail,
                    bind_msg,
                )
                await message.answer(
                    "✅ Аккаунт сайта привязан к этому Telegram.\n"
                    "⚠️ Синхронизация VPN ещё не завершилась — откройте VPN в боте "
                    "или напишите в поддержку, если ссылка не появится."
                )
            else:
                await message.answer(
                    "✅ Аккаунт сайта привязан к этому Telegram.\n"
                    "Подписка VPN и история покупок теперь общие с ботом."
                )
        else:
            await message.answer(f"Не удалось привязать: {detail}")
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
        return

    if not await users_repo.throttle_start_allowed(
        conn, message.from_user.id, int(settings.start_command_min_interval_seconds)
    ):
        await message.answer("Подождите секунду перед следующим /start.")
        return

    # Новый пользователь: сразу язык, bookkeeping после UI.
    if await users_repo.get_locale(conn, message.from_user.id) is None:
        await _send_language_pick(message, settings)
        await _start_side_effects(
            conn,
            settings,
            user_id=message.from_user.id,
            payload=payload,
        )
        return

    await _start_side_effects(
        conn,
        settings,
        user_id=message.from_user.id,
        payload=payload,
    )
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
    """Проверка подписки = согласие с документами (один стартовый экран)."""
    if channel_gate_enabled(settings) and not await user_is_channel_member(
        cb.bot, settings, cb.from_user.id
    ):
        await cb.answer(
            "Подписка не видна. Откройте канал по кнопке, подпишитесь и нажмите «✅ Проверить и продолжить» снова.",
            show_alert=True,
        )
        return
    if not await users_repo.has_terms_accepted(conn, cb.from_user.id):
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


def _parse_captcha_callback(data: str | None) -> tuple[int, int | None, str | None] | None:
    """Поддержка chk:c:{id}:{emoji_hex} и старого chk:c:{id}:{idx}."""
    parts = (data or "").split(":")
    if len(parts) != 4:
        return None
    try:
        cid = int(parts[2])
    except ValueError:
        return None
    token = parts[3]
    if token.isdigit() and len(token) <= 2:
        return cid, int(token), None
    emoji = captcha_repo.emoji_from_token(token)
    if emoji is None:
        return None
    return cid, None, emoji


@router.callback_query(F.data.startswith("onb:c:"))
async def onboarding_captcha_pick(cb: CallbackQuery, settings: Settings, conn) -> None:
    from bot.services.emoji_captcha import WORD_BY_EMOJI

    parsed = _parse_captcha_callback(cb.data)
    if parsed is None:
        await cb.answer()
        return
    cid, idx, emoji = parsed
    res = await captcha_repo.take_challenge(
        conn,
        challenge_id=cid,
        user_id=cb.from_user.id,
        purpose="onboarding",
        picked_idx=idx,
        picked_emoji=emoji,
        word_by_emoji=WORD_BY_EMOJI,
    )
    if res.status == "wrong":
        hint = res.hint_word or "нужный эмодзи"
        await cb.answer(f"Неверно. Нажмите: {hint}.", show_alert=True)
        return
    if res.status != "ok":
        await cb.answer("Проверка устарела. Нажмите /start ещё раз.", show_alert=True)
        return
    await users_repo.complete_onboarding(conn, cb.from_user.id)
    await cb.answer()
    try:
        await cb.message.delete()
    except Exception:
        pass
    await onboarding_gate.send_hub_welcome(cb.bot, cb.message.chat.id, settings, user_id=cb.from_user.id)


@router.callback_query(F.data.startswith("chk:c:"))
async def checkout_captcha_pick(
    cb: CallbackQuery,
    state: FSMContext,
    settings: Settings,
    conn,
    products: list[Product],
    bot: Bot,
) -> None:
    from bot.services.emoji_captcha import WORD_BY_EMOJI, prompt_checkout_captcha
    from bot.util_telegram import answer_callback_safe

    parsed = _parse_captcha_callback(cb.data)
    if parsed is None:
        await cb.answer()
        return
    cid, idx, emoji = parsed
    res = await captcha_repo.take_challenge(
        conn,
        challenge_id=cid,
        user_id=cb.from_user.id,
        purpose="checkout",
        picked_idx=idx,
        picked_emoji=emoji,
        word_by_emoji=WORD_BY_EMOJI,
    )
    if res.status == "wrong":
        hint = res.hint_word or "нужный эмодзи из текста"
        await cb.answer(f"Неверно. Нажмите именно: {hint}.", show_alert=True)
        return
    if res.status != "ok":
        # Устарела/двойной клик/кнопка со старого сообщения.
        if await users_repo.checkout_captcha_valid(conn, cb.from_user.id):
            await cb.answer("Уже принято.")
            return
        data = await state.get_data()
        current_state = await state.get_state()
        if data.get(AWAITING_CHECKOUT_AFTER_CAPTCHA) and current_state == CheckoutStates.waiting_confirm.state:
            await prompt_checkout_captcha(cb, conn, settings)
            await cb.answer("Проверка устарела — новая ниже.", show_alert=True)
            return
        await cb.answer("Проверка устарела. Оформите заказ заново.", show_alert=True)
        return

    data = await state.get_data()
    current_state = await state.get_state()
    if (
        not data.get(AWAITING_CHECKOUT_AFTER_CAPTCHA)
        or current_state != CheckoutStates.waiting_confirm.state
    ):
        await state.update_data(**{AWAITING_CHECKOUT_AFTER_CAPTCHA: False})
        await cb.answer("Сессия устарела. Вернитесь к оформлению заказа.", show_alert=True)
        return

    # Сначала снять «загрузку» и оформить счёт; капчу удалить после — иначе edit падает на удалённом фото.
    await answer_callback_safe(cb)
    await users_repo.extend_checkout_captcha(
        conn, cb.from_user.id, int(settings.checkout_captcha_ttl_seconds)
    )
    await finalize_checkout_order(cb, state, products, settings, conn, bot)
    try:
        msg = cb.message
        if msg and (msg.photo or msg.document or msg.animation or msg.video):
            await msg.delete()
    except Exception:
        pass


@router.message(Command("my"))
async def cmd_my(message: Message, settings: Settings, conn) -> None:
    if not await ensure_shop_access(message, settings, conn):
        return
    from bot.services.vpn_user_links import append_vpn_copy_link_rows

    text = await profile_body_html(message.bot, settings, conn, message.from_user.id)
    b = InlineKeyboardBuilder()
    for row in profile_inline_kb_rows_prefix():
        b.row(*row)
    await append_vpn_copy_link_rows(b, settings=settings, user_id=int(message.from_user.id))
    b.row(InlineKeyboardButton(text="🔔 Уведомления", callback_data="nav:notify"))
    b.row(InlineKeyboardButton(text="⬅️ В меню", callback_data="nav:hub"))
    await message.answer(text, reply_markup=b.as_markup())


@router.message(Command("vpnlink"))
async def cmd_vpnlink(message: Message, settings: Settings, conn) -> None:
    if not await ensure_shop_access(message, settings, conn):
        return
    from bot.handlers.vpn import _send_subscription_link_message

    if not settings.ui_show_vpn:
        await message.answer("VPN временно недоступен.")
        return
    await _send_subscription_link_message(message, settings, int(message.from_user.id))


@router.message(Command("orders"))
async def cmd_orders(message: Message, settings: Settings, conn) -> None:
    if not await ensure_shop_access(message, settings, conn):
        return
    text = await orders_first_page_html(conn, message.from_user.id)
    await message.answer(text, reply_markup=hub_menu_kb(settings, user_id=message.from_user.id))


@router.message(Command("menu"))
async def cmd_menu(message: Message, settings: Settings, conn) -> None:
    """Открывает главный хаб (как после успешной проверки подписки на канал)."""
    if not await ensure_shop_access(message, settings, conn):
        return
    await strip_sticky_reply_keyboard(message)
    try:
        await analytics_repo.log_event(
            conn,
            user_id=message.from_user.id,
            event_type="bot_entry",
            meta={"via": "menu"},
        )
    except Exception:
        pass
    await message.answer(ONBOARDING_SCREEN_2, reply_markup=hub_menu_kb(settings, user_id=message.from_user.id))


@router.message(F.text.in_(LEGACY_REPLY_BUTTON_TEXTS))
async def legacy_reply_buttons(message: Message, settings: Settings, conn) -> None:
    """Старые нижние 4 кнопки больше не используем: снимаем их и открываем хаб через Start-меню."""
    await strip_sticky_reply_keyboard(message)
    if not await ensure_shop_access(message, settings, conn):
        return
    text = (message.text or "").strip()
    if text in (REPLY_BTN_PROFILE, REPLY_BTN_PROFILE_ALT):
        await cmd_my(message, settings, conn)
        return
    await message.answer(ONBOARDING_SCREEN_2, reply_markup=hub_menu_kb(settings, user_id=message.from_user.id))


@router.callback_query(F.data.startswith("fb:n:"))
async def feedback_nps_order_callback(
    cb: CallbackQuery, settings: Settings, conn, state: FSMContext
) -> None:
    """NPS 0–10 сразу после выдачи заказа (fb:n:{order_id}:{score})."""
    if not settings.feature_feedback_collection_enabled:
        await cb.answer("Опросы временно отключены.")
        return
    parts = (cb.data or "").split(":")
    if len(parts) != 4:
        await cb.answer()
        return
    try:
        order_id = int(parts[2])
        score = int(parts[3])
    except ValueError:
        await cb.answer()
        return
    if score < 0 or score > 10:
        await cb.answer()
        return
    scope = feedback_order_scope(order_id)
    if score > 6:
        await feedback_repo.save_feedback(
            conn,
            user_id=cb.from_user.id,
            kind="nps",
            score=score,
            product_scope=scope,
        )
        try:
            await analytics_repo.log_event(
                conn,
                user_id=cb.from_user.id,
                event_type="feedback_nps_submitted",
                meta={"order_id": order_id, "score": score},
            )
        except Exception:
            pass
        await notify_ops_user_feedback(
            settings,
            user_id=cb.from_user.id,
            username=cb.from_user.username,
            kind="nps",
            score=score,
            comment="Высокая оценка — ждём пожелания (опционально)",
            order_id=order_id,
        )
    if score <= 6:
        await notify_ops_user_feedback(
            settings,
            user_id=cb.from_user.id,
            username=cb.from_user.username,
            kind="nps_low",
            score=score,
            comment="Пользователь оценил ≤6 — ждём комментарий",
            order_id=order_id,
        )
        await state.set_state(FeedbackStates.waiting_negative_comment)
        await state.update_data(feedback_order_id=order_id, feedback_nps_score=score)
        await cb.message.answer(NEGATIVE_PROMPT_TEXT)
        await cb.answer("Спасибо")
        return
    await cb.message.answer(WISHES_PROMPT_TEXT, reply_markup=feedback_wishes_kb(order_id))
    await cb.answer("Спасибо!")


@router.callback_query(F.data.startswith("fb:w:"))
async def feedback_wishes_start(cb: CallbackQuery, settings: Settings, state: FSMContext) -> None:
    if not settings.feature_feedback_collection_enabled:
        await cb.answer()
        return
    try:
        order_id = int((cb.data or "").split(":")[2])
    except (ValueError, IndexError):
        await cb.answer()
        return
    await state.set_state(FeedbackStates.waiting_suggestion)
    await state.update_data(feedback_order_id=order_id)
    await cb.message.answer(
        "<b>Мы стремимся стать лучше.</b>\n"
        "Напишите одним сообщением ваши <b>пожелания и рекомендации</b> — мы читаем каждый отзыв."
    )
    await cb.answer()


@router.callback_query(F.data.startswith("fb:sk:"))
async def feedback_wishes_skip(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb.message.answer("Спасибо! Будем рады видеть вас снова.")
    await cb.answer()


@router.message(FeedbackStates.waiting_negative_comment, F.text)
async def feedback_negative_comment(
    message: Message, settings: Settings, conn, state: FSMContext
) -> None:
    data = await state.get_data()
    order_id = int(data.get("feedback_order_id") or 0)
    score = int(data.get("feedback_nps_score") or 0)
    text = (message.text or "").strip()[:800]
    if not text:
        await message.answer("Напишите, пожалуйста, что именно не понравилось.")
        return
    scope = feedback_order_scope(order_id) if order_id else "shop"
    await feedback_repo.save_feedback(
        conn,
        user_id=message.from_user.id,
        kind="nps",
        score=score,
        product_scope=scope,
        comment=text,
    )
    try:
        await analytics_repo.log_event(
            conn,
            user_id=message.from_user.id,
            event_type="feedback_nps_submitted",
            meta={"order_id": order_id, "score": score},
        )
    except Exception:
        pass
    await notify_ops_user_feedback(
        settings,
        user_id=message.from_user.id,
        username=message.from_user.username,
        kind="nps",
        score=score,
        comment=text,
        order_id=order_id or None,
    )
    await state.clear()
    await message.answer("Спасибо, что поделились. Мы учтём это и постараемся стать лучше.")


@router.message(FeedbackStates.waiting_suggestion, F.text)
async def feedback_suggestion_comment(
    message: Message, settings: Settings, conn, state: FSMContext
) -> None:
    data = await state.get_data()
    order_id = int(data.get("feedback_order_id") or 0)
    text = (message.text or "").strip()[:800]
    if not text:
        await message.answer("Напишите пожелания или нажмите «Пропустить» в предыдущем сообщении.")
        return
    scope = feedback_order_scope(order_id) if order_id else "shop"
    await feedback_repo.save_feedback(
        conn,
        user_id=message.from_user.id,
        kind="suggestion",
        score=0,
        product_scope=scope,
        comment=text,
    )
    await notify_ops_user_feedback(
        settings,
        user_id=message.from_user.id,
        username=message.from_user.username,
        kind="suggestion",
        score=0,
        comment=text,
        order_id=order_id or None,
    )
    await state.clear()
    await message.answer("Спасибо за рекомендации! Мы стремимся стать лучше.")


@router.callback_query(F.data.startswith("fb:nps:"))
async def feedback_nps_callback(cb: CallbackQuery, settings: Settings, conn) -> None:
    """Фоновый NPS (без заказа). CSAT 1–5 после него отключён — дубль путал пользователей."""
    if not settings.feature_feedback_collection_enabled:
        await cb.answer("Опросы временно отключены.")
        return
    raw = (cb.data or "").split(":")
    if len(raw) != 3:
        await cb.answer()
        return
    try:
        score = int(raw[2])
    except ValueError:
        await cb.answer()
        return
    if score < 0 or score > 10:
        await cb.answer()
        return
    await feedback_repo.save_feedback(
        conn,
        user_id=cb.from_user.id,
        kind="nps",
        score=score,
        product_scope="shop",
    )
    await cb.message.answer("Спасибо за оценку! Это помогает улучшать сервис.")
    await cb.answer("NPS сохранен")


@router.callback_query(F.data.startswith("fb:csat:"))
async def feedback_csat_callback(cb: CallbackQuery, settings: Settings, conn) -> None:
    """Legacy CSAT 1–5: больше не собираем (оставлен ответ на старые кнопки в чате)."""
    _ = settings, conn
    await cb.message.answer("Спасибо! Достаточно оценки NPS — дополнительный опрос больше не нужен.")
    await cb.answer()
