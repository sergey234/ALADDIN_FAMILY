"""Handlers: Помощник AiMonkey — входы, сессия, действия."""

from __future__ import annotations

import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.assistant.access import (
    assistant_disabled_user_html,
    assistant_feature_allowed,
)
from bot.assistant import repo as as_repo
from bot.assistant.keyboards import (
    CHECKOUT_BLOCK_HTML,
    MEDIA_REJECT_HTML,
    WELCOME_HTML,
    disabled_kb,
    session_kb,
    topics_kb,
)
from bot.assistant.orchestrator import escalate_user_button, handle_user_message
from bot.assistant.policy import TOPIC_PROMPTS
from bot.config import Settings
from bot.keyboards.shop_kb import hub_menu_kb
from bot.services import analytics_repo, orders_repo
from bot.services.vpn_user_status import vpn_user_status_block_html
from bot.states.assistant import AssistantStates
from bot.util_html import esc

logger = logging.getLogger(__name__)
router = Router(name="assistant")

_BLOCKING_STATE_PREFIXES = (
    "CheckoutStates:",
    "BuyStarsCustomStates:",
    "TopupStates:",
    "ApiKeyStates:",
    "FeedbackStates:",
)


def _is_blocking_shop_fsm(state_name: str | None) -> bool:
    if not state_name:
        return False
    return any(state_name.startswith(p) for p in _BLOCKING_STATE_PREFIXES)


async def _open_assistant_ui(
    *,
    message: Message,
    settings: Settings,
    conn,
    state: FSMContext,
    user_id: int,
    edit: bool = False,
) -> None:
    cur = await state.get_state()
    if _is_blocking_shop_fsm(cur):
        html = CHECKOUT_BLOCK_HTML
        kb = session_kb(settings)  # still offer human? better hub
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton

        b = InlineKeyboardBuilder()
        b.row(InlineKeyboardButton(text="⬅️ В меню", callback_data="nav:hub"))
        kb = b.as_markup()
        if edit and message:
            try:
                await message.edit_text(html, reply_markup=kb)
            except Exception:
                await message.answer(html, reply_markup=kb)
        else:
            await message.answer(html, reply_markup=kb)
        return

    await as_repo.get_or_create_session(
        conn,
        user_id,
        ttl_min=int(settings.assistant_session_ttl_min or 30),
        max_turns=int(settings.assistant_session_max_turns or 20),
    )
    await state.set_state(AssistantStates.active)
    try:
        await analytics_repo.log_event(
            conn, user_id=user_id, event_type="assistant_open", meta={"via": "entry"}
        )
    except Exception:
        pass
    kb = session_kb(settings)
    if edit:
        try:
            await message.edit_text(WELCOME_HTML, reply_markup=kb)
            return
        except Exception:
            pass
    await message.answer(WELCOME_HTML, reply_markup=kb)


@router.callback_query(F.data == "nav:assistant")
async def nav_assistant(cb: CallbackQuery, settings: Settings, conn, state: FSMContext) -> None:
    from bot.util_telegram import answer_callback_safe

    await answer_callback_safe(cb)
    if not cb.message:
        return
    uid = int(cb.from_user.id)
    if not assistant_feature_allowed(uid, settings):
        await cb.message.edit_text(
            assistant_disabled_user_html(),
            reply_markup=disabled_kb(settings),
        )
        return
    await _open_assistant_ui(
        message=cb.message,
        settings=settings,
        conn=conn,
        state=state,
        user_id=uid,
        edit=True,
    )


@router.message(Command("help_ai", "assistant"))
async def cmd_help_ai(message: Message, settings: Settings, conn, state: FSMContext) -> None:
    uid = int(message.from_user.id)
    if not assistant_feature_allowed(uid, settings):
        await message.answer(assistant_disabled_user_html(), reply_markup=disabled_kb(settings))
        return
    await _open_assistant_ui(
        message=message,
        settings=settings,
        conn=conn,
        state=state,
        user_id=uid,
        edit=False,
    )


@router.message(AssistantStates.active, F.text)
async def assistant_text(
    message: Message,
    settings: Settings,
    conn,
    state: FSMContext,
    bot: Bot,
) -> None:
    uid = int(message.from_user.id)
    if not assistant_feature_allowed(uid, settings):
        await state.clear()
        await message.answer(assistant_disabled_user_html(), reply_markup=disabled_kb(settings))
        return
    cur = await state.get_state()
    # Defense: if FSM was overwritten somehow
    if cur != AssistantStates.active.state:
        return

    try:
        result = await handle_user_message(
            conn,
            settings,
            user_id=uid,
            text=message.text or "",
            username=message.from_user.username,
            bot=bot,
        )
    except Exception as e:
        logger.exception("assistant_orchestrator_failed: %s", e)
        await message.answer(
            "Не удалось обработать вопрос. Нажмите «Человек» или откройте Поддержку.",
            reply_markup=session_kb(settings),
        )
        return

    await message.answer(
        result.html,
        reply_markup=session_kb(settings, support_url=result.support_url),
        disable_web_page_preview=True,
    )


@router.message(
    AssistantStates.active,
    F.photo
    | F.voice
    | F.video
    | F.sticker
    | F.document
    | F.audio
    | F.video_note
    | F.animation,
)
async def assistant_media_reject(message: Message, settings: Settings) -> None:
    await message.answer(MEDIA_REJECT_HTML, reply_markup=session_kb(settings))


@router.callback_query(F.data == "as:act:close")
async def as_close(cb: CallbackQuery, settings: Settings, conn, state: FSMContext) -> None:
    await cb.answer()
    uid = int(cb.from_user.id)
    await as_repo.end_user_sessions(conn, uid)
    await state.clear()
    if not cb.message:
        return
    from bot.ui_copy import ONBOARDING_SCREEN_2
    from bot.util_telegram import safe_edit_or_send

    await safe_edit_or_send(
        cb.message,
        ONBOARDING_SCREEN_2,
        reply_markup=hub_menu_kb(settings, user_id=uid),
    )


@router.callback_query(F.data == "as:act:back")
async def as_back(cb: CallbackQuery, settings: Settings, state: FSMContext) -> None:
    await cb.answer()
    await state.set_state(AssistantStates.active)
    if cb.message:
        await cb.message.edit_text(WELCOME_HTML, reply_markup=session_kb(settings))


@router.callback_query(F.data == "as:act:topics")
async def as_topics(cb: CallbackQuery) -> None:
    await cb.answer()
    if cb.message:
        await cb.message.edit_text("<b>📖 Темы</b>\nВыберите вопрос:", reply_markup=topics_kb())


@router.callback_query(F.data.startswith("as:topic:"))
async def as_topic(
    cb: CallbackQuery,
    settings: Settings,
    conn,
    state: FSMContext,
    bot: Bot,
) -> None:
    await cb.answer()
    uid = int(cb.from_user.id)
    if not assistant_feature_allowed(uid, settings):
        return
    key = (cb.data or "").split(":")[-1]
    prompt = TOPIC_PROMPTS.get(key)
    if not prompt:
        return
    await state.set_state(AssistantStates.active)
    if cb.message:
        await cb.message.answer(f"<i>{esc(prompt)}</i>")
    result = await handle_user_message(
        conn,
        settings,
        user_id=uid,
        text=prompt,
        username=cb.from_user.username,
        bot=bot,
        topic_hint=key,
    )
    if cb.message:
        await cb.message.answer(
            result.html,
            reply_markup=session_kb(settings, support_url=result.support_url),
            disable_web_page_preview=True,
        )


@router.callback_query(F.data == "as:act:orders")
async def as_orders(cb: CallbackQuery, settings: Settings, conn, state: FSMContext) -> None:
    await cb.answer()
    uid = int(cb.from_user.id)
    await state.set_state(AssistantStates.active)
    rows = await orders_repo.list_user_orders(conn, uid, limit=5)
    if not rows:
        text = "<b>Мои заказы</b>\n\nПока заказов нет."
    else:
        lines = ["<b>Мои заказы</b> (из базы):\n"]
        for r in rows:
            amt = float(r["rub_after_discounts"] or 0)
            lines.append(
                f"#{esc(r['id'])} — {esc(r['product_title'])} — "
                f"<b>{esc(r['status'])}</b> — {esc(f'{amt:.2f}')} ₽"
            )
        text = "\n".join(lines)
    if cb.message:
        await cb.message.answer(text, reply_markup=session_kb(settings))


@router.callback_query(F.data == "as:act:vpn")
async def as_vpn(cb: CallbackQuery, settings: Settings, state: FSMContext) -> None:
    await cb.answer()
    uid = int(cb.from_user.id)
    await state.set_state(AssistantStates.active)
    block = await vpn_user_status_block_html(settings, uid, inactive_variant="vpn_section")
    if cb.message:
        await cb.message.answer(
            f"<b>Мой VPN</b>\n\n{block}\n\n"
            "<i>Ссылку /sub/ откройте кнопкой «Моя VPN-ссылка».</i>",
            reply_markup=session_kb(settings),
        )


@router.callback_query(F.data == "as:act:vpn_link")
async def as_vpn_link(cb: CallbackQuery, settings: Settings, state: FSMContext) -> None:
    await cb.answer()
    await state.set_state(AssistantStates.active)
    if not cb.message:
        return
    # Reuse existing VPN delivery path (masked in chat UI as dedicated message).
    from bot.handlers.vpn import _send_subscription_link_message

    await _send_subscription_link_message(cb.message, settings, int(cb.from_user.id))
    await cb.message.answer("Сессия помощника активна — можете задать ещё вопрос.", reply_markup=session_kb(settings))


@router.callback_query(F.data == "as:act:human")
async def as_human(
    cb: CallbackQuery,
    settings: Settings,
    conn,
    state: FSMContext,
    bot: Bot,
) -> None:
    await cb.answer()
    uid = int(cb.from_user.id)
    await state.set_state(AssistantStates.active)
    result = await escalate_user_button(
        conn,
        settings,
        user_id=uid,
        username=cb.from_user.username,
        bot=bot,
    )
    if cb.message:
        await cb.message.answer(
            result.html,
            reply_markup=session_kb(settings, support_url=result.support_url),
            disable_web_page_preview=True,
        )


@router.callback_query(F.data.in_({"as:csat:up", "as:csat:down"}))
async def as_csat(cb: CallbackQuery, conn) -> None:
    uid = int(cb.from_user.id)
    score = "up" if cb.data == "as:csat:up" else "down"
    try:
        await analytics_repo.log_event(
            conn, user_id=uid, event_type="assistant_csat", meta={"via": score}
        )
    except Exception:
        pass
    await cb.answer("Спасибо за оценку!" if score == "up" else "Спасибо, передадим улучшать.")
