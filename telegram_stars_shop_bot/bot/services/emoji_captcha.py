"""Генерация inline emoji-капчи (эталон: выберите нужный эмодзи в ряду из трёх)."""

from __future__ import annotations

import json
import random

from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.config import Settings
from bot.services import branding_media, captcha_repo
from bot.services.marketing import CHANNEL_GATE_PHOTO_CAPTION_MAX

# (emoji, слово в инструкции)
_CAPTCHA_TARGETS: list[tuple[str, str]] = [
    ("🍌", "банан"),
    ("🥕", "морковь"),
    ("🌹", "розу"),
    ("⭐", "звезду"),
    ("💎", "алмаз"),
    ("🍎", "яблоко"),
]


def _pick_triple() -> tuple[str, str, list[str], int]:
    target_emoji, word = random.choice(_CAPTCHA_TARGETS)
    pool = [e for e, _ in _CAPTCHA_TARGETS if e != target_emoji]
    random.shuffle(pool)
    distractors = pool[:2]
    options = [target_emoji, distractors[0], distractors[1]]
    order = list(range(3))
    random.shuffle(order)
    shuffled = [options[i] for i in order]
    correct_idx = shuffled.index(target_emoji)
    return target_emoji, word, shuffled, correct_idx


def captcha_caption_html(*, word: str, kind: str) -> str:
    _ = kind
    w = word.strip()
    return (
        "<b>🔒 Небольшая проверочка 😃</b>\n\n"
        f"Выберите <b>{w}</b> ниже 👇"
    )


def captcha_keyboard(*, challenge_id: int, purpose_prefix: str, emojis: list[str]) -> InlineKeyboardMarkup:
    """purpose_prefix: «onb» или «chk» → callback {prefix}:c:{id}:{0..2}."""
    row = [
        InlineKeyboardButton(
            text=e,
            callback_data=f"{purpose_prefix}:c:{challenge_id}:{i}",
        )
        for i, e in enumerate(emojis)
    ]
    return InlineKeyboardMarkup(inline_keyboard=[row])


async def create_onboarding_captcha_ui(conn, user_id: int) -> tuple[str, InlineKeyboardMarkup]:
    _, word, emojis, correct_idx = _pick_triple()
    cid = await captcha_repo.create_challenge(
        conn,
        user_id=user_id,
        purpose="onboarding",
        correct_idx=correct_idx,
        options_json=json.dumps(emojis, ensure_ascii=False),
    )
    cap = captcha_caption_html(word=word, kind="onboarding")
    kb = captcha_keyboard(challenge_id=cid, purpose_prefix="onb", emojis=emojis)
    return cap, kb


async def create_checkout_captcha_ui(conn, user_id: int) -> tuple[str, InlineKeyboardMarkup]:
    _, word, emojis, correct_idx = _pick_triple()
    cid = await captcha_repo.create_challenge(
        conn,
        user_id=user_id,
        purpose="checkout",
        correct_idx=correct_idx,
        options_json=json.dumps(emojis, ensure_ascii=False),
    )
    cap = captcha_caption_html(word=word, kind="checkout")
    kb = captcha_keyboard(challenge_id=cid, purpose_prefix="chk", emojis=emojis)
    return cap, kb


async def send_onboarding_captcha_photo(
    bot,
    chat_id: int,
    *,
    conn,
    settings: Settings,
    user_id: int,
) -> None:
    cap, kb = await create_onboarding_captcha_ui(conn, user_id)
    photo = branding_media.hero_photo_input(settings)
    if photo is not None and len(cap) <= CHANNEL_GATE_PHOTO_CAPTION_MAX:
        await bot.send_photo(chat_id, photo, caption=cap, reply_markup=kb)
    else:
        await bot.send_message(chat_id, cap, reply_markup=kb)


async def prompt_checkout_captcha(cb: CallbackQuery, conn, settings: Settings) -> None:
    cap, kb = await create_checkout_captcha_ui(conn, cb.from_user.id)
    photo = branding_media.hero_photo_input(settings)
    if photo is not None and len(cap) <= CHANNEL_GATE_PHOTO_CAPTION_MAX:
        await cb.message.answer_photo(photo, caption=cap, reply_markup=kb)
    else:
        await cb.message.answer(cap, reply_markup=kb)
