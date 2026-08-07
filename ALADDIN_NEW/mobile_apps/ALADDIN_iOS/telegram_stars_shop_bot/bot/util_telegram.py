"""Telegram API helpers (benign errors, safe edits)."""

from __future__ import annotations

import logging

from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

_log = logging.getLogger(__name__)


def is_message_not_modified_error(exc: BaseException) -> bool:
    return isinstance(exc, TelegramBadRequest) and "message is not modified" in str(exc).lower()


def _is_uneditable_message_error(exc: BaseException) -> bool:
    if not isinstance(exc, TelegramBadRequest):
        return False
    low = str(exc).lower()
    needles = (
        "message to edit not found",
        "message can't be edited",
        "message is not modified",
        "there is no text in the message to edit",
        "message to delete not found",
    )
    return any(n in low for n in needles)


async def answer_callback_safe(cb: CallbackQuery, *args: object, **kwargs: object) -> None:
    """Снять «часики» у кнопки; повторный answer не падает."""
    try:
        await cb.answer(*args, **kwargs)
    except TelegramBadRequest:
        pass
    except TelegramNetworkError:
        _log.warning("answer_callback_network_timeout", exc_info=True)


async def safe_edit_text(
    message: Message,
    text: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
    **kwargs: object,
) -> bool:
    """edit_text без шума в логах при повторном нажатии той же кнопки."""
    try:
        await message.edit_text(text, reply_markup=reply_markup, **kwargs)
        return True
    except TelegramBadRequest as exc:
        if is_message_not_modified_error(exc):
            return False
        raise


async def safe_edit_or_send(
    message: Message,
    text: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
    force_new: bool = False,
    **kwargs: object,
) -> bool:
    """
    Правит сообщение; если нельзя (удалили капчу / фото / timeout) — шлёт новое в чат.
    Так оплата не «висит» с крутилкой после капчи или сбоев Telegram.
    force_new / медиа-сообщение: сразу answer (без edit_text на фото капчи).
    """
    is_media = bool(
        getattr(message, "photo", None)
        or getattr(message, "document", None)
        or getattr(message, "animation", None)
        or getattr(message, "video", None)
        or getattr(message, "sticker", None)
    )
    if not force_new and not is_media:
        try:
            await message.edit_text(text, reply_markup=reply_markup, **kwargs)
            return True
        except TelegramBadRequest as exc:
            if is_message_not_modified_error(exc):
                return True
            if not _is_uneditable_message_error(exc):
                _log.warning("safe_edit_bad_request: %s", exc)
        except TelegramNetworkError:
            _log.warning("safe_edit_network_timeout", exc_info=True)
    try:
        await message.answer(text, reply_markup=reply_markup, **kwargs)
        return True
    except Exception:
        _log.exception("safe_edit_or_send_answer_failed")
        return False
