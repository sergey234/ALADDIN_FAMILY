"""Личный кабинет → «🎁 Промокод»."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.services import promo_copy, promo_repo
from bot.states.promo import PromoStates
from bot.util_telegram import answer_callback_safe

router = Router(name="promo")

PROMO_NAV = "nav:promo"
PROMO_ENTER = "promo:enter"


def promo_screen_kb():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="✏️ Ввести промокод", callback_data=PROMO_ENTER))
    b.row(InlineKeyboardButton(text="⬅️ В личный кабинет", callback_data="nav:profile"))
    return b.as_markup()


@router.callback_query(F.data == PROMO_NAV)
async def nav_promo(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await answer_callback_safe(cb)
    if not cb.message:
        return
    await cb.message.answer(promo_copy.promo_screen_html(), reply_markup=promo_screen_kb())


@router.callback_query(F.data == PROMO_ENTER)
async def promo_enter(cb: CallbackQuery, state: FSMContext) -> None:
    await answer_callback_safe(cb)
    await state.set_state(PromoStates.waiting_code)
    if cb.message:
        await cb.message.answer(promo_copy.promo_enter_prompt_html())


@router.message(Command("cancel"), PromoStates.waiting_code)
async def promo_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Ввод промокода отменён.", reply_markup=promo_screen_kb())


@router.message(PromoStates.waiting_code, F.text)
async def promo_code_submitted(message: Message, state: FSMContext, conn) -> None:
    raw = (message.text or "").strip()
    status, payload = await promo_repo.activate_promo(
        conn, user_id=int(message.from_user.id), code=raw
    )
    await state.clear()
    if status == "ok":
        await message.answer(promo_copy.promo_success_html(), reply_markup=promo_screen_kb())
        return
    await message.answer(promo_repo.fail_message(payload), reply_markup=promo_screen_kb())


@router.message(PromoStates.waiting_code)
async def promo_code_non_text(message: Message) -> None:
    await message.answer(promo_copy.promo_empty_html())
