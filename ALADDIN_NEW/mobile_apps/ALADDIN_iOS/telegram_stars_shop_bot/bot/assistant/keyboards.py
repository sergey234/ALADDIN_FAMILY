"""Keyboards and welcome copy for Помощник."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import Settings
from bot.support_links import support_prefill_url, telegram_support_base


WELCOME_HTML = (
    "<b>🤖 AI Помощник AiMonkey</b>\n\n"
    "Напишите вопрос текстом в этот чат — я отвечу сообщением.\n"
    "Помогу с VPN, оплатой, Stars/Premium и приглашениями.\n\n"
    "<i>Ответы готовит ИИ-помощник; факты заказа и VPN берутся из нашей базы. "
    "В любой момент можно нажать «Человек».</i>\n\n"
    "Примеры:\n"
    "• Как подключить Happ на Android?\n"
    "• Оплатил заказ #78 — где статус?\n"
    "• Можно ли купить Stars с реферального баланса?"
)

MEDIA_REJECT_HTML = (
    "Пока умею только текст. Опишите проблему словами "
    "или нажмите <b>👨‍💼 Человек</b>."
)

CHECKOUT_BLOCK_HTML = (
    "<b>Сначала завершите или отмените оплату</b>\n\n"
    "Сейчас открыто оформление заказа / капча. "
    "Помощник не принимает текст в этом режиме, чтобы не сбить оплату.\n"
    "Завершите шаги или нажмите отмену — затем снова откройте Помощника."
)


def session_kb(settings: Settings, *, support_url: str | None = None) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="📋 Мои заказы", callback_data="as:act:orders"),
        InlineKeyboardButton(text="🛡️ Мой VPN", callback_data="as:act:vpn"),
    )
    b.row(
        InlineKeyboardButton(text="🔗 Моя VPN-ссылка", callback_data="as:act:vpn_link"),
        InlineKeyboardButton(text="📖 Темы", callback_data="as:act:topics"),
    )
    human = InlineKeyboardButton(text="👨‍💼 Человек", callback_data="as:act:human")
    if support_url:
        b.row(human, InlineKeyboardButton(text="💬 Поддержка URL", url=support_url))
    else:
        b.row(human)
    b.row(
        InlineKeyboardButton(text="👍", callback_data="as:csat:up"),
        InlineKeyboardButton(text="👎", callback_data="as:csat:down"),
        InlineKeyboardButton(text="⬅️ В меню", callback_data="as:act:close"),
    )
    return b.as_markup()


def topics_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="Happ Android", callback_data="as:topic:happ_android"))
    b.row(InlineKeyboardButton(text="Happ iOS", callback_data="as:topic:happ_ios"))
    b.row(InlineKeyboardButton(text="Оплата / статус", callback_data="as:topic:pay_status"))
    b.row(InlineKeyboardButton(text="Рефералка", callback_data="as:topic:ref"))
    b.row(InlineKeyboardButton(text="Капча / checkout", callback_data="as:topic:captcha"))
    b.row(InlineKeyboardButton(text="VPN не работает", callback_data="as:topic:vpn_down"))
    b.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="as:act:back"))
    return b.as_markup()


def disabled_kb(settings: Settings) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    base = telegram_support_base(settings)
    url = support_prefill_url(settings, "Нужна помощь (помощник выкл)") or base
    if url:
        b.row(InlineKeyboardButton(text="💬 Поддержка", url=url))
    b.row(InlineKeyboardButton(text="⬅️ В меню", callback_data="nav:hub"))
    return b.as_markup()
