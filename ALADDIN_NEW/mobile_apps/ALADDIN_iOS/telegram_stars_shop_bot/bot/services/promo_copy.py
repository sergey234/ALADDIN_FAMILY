"""Тексты экрана промокодов (ТЗ 2026-07-31)."""

from __future__ import annotations


def promo_screen_html() -> str:
    return (
        "<b>🎁 Промокоды</b>\n\n"
        "Введите промокод, чтобы получить скидку или специальный бонус.\n\n"
        "Если промокод действителен, бонус будет применён автоматически."
    )


def promo_enter_prompt_html() -> str:
    return "✏️ Введите промокод одним сообщением.\n<i>Отмена: /cancel</i>"


def promo_success_html() -> str:
    return (
        "✅ <b>Промокод успешно активирован!</b>\n\n"
        "Ваша скидка будет автоматически применена при оформлении подходящего заказа."
    )


def promo_not_found_html() -> str:
    return "❌ Промокод не найден или уже недействителен."


def promo_already_used_html() -> str:
    return "ℹ️ Вы уже активировали этот промокод."


def promo_limit_html() -> str:
    return "⚠️ Лимит активаций этого промокода исчерпан."


def promo_personal_html() -> str:
    return "❌ Этот промокод предназначен для другого пользователя."


def promo_new_users_only_html() -> str:
    return "❌ Этот промокод только для новых покупателей."


def promo_empty_html() -> str:
    return "❌ Введите промокод текстом."
