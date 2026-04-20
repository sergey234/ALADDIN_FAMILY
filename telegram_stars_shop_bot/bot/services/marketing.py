from __future__ import annotations

from bot.config import Settings
from bot.util_html import esc


def onboarding_screen_1_html(settings: Settings) -> str:
    """Единый источник цифр: маркетинг подтягивает реальные % из настроек."""
    md = esc(settings.marketing_max_discount_percent)
    rb = esc(settings.ref_buyer_discount_percent)
    rc = esc(settings.ref_commission_percent)
    return (
        f"<b>Telegram Stars</b> без KYC — скидка до <b>{md}%</b> на условиях сервиса.\n"
        f"Быстро купить звёзды прямо в Telegram.\n\n"
        f"Оплата: <b>СБП</b>, <b>карта</b>, <b>TON</b> / крипта.\n\n"
        f"Рефералка: друг получает <b>−{rb}%</b> на первый заказ, "
        f"вам <b>+{rc}%</b> от суммы его первой покупки на баланс в ₽."
    )


def referral_faq_html(settings: Settings) -> str:
    rb = esc(settings.ref_buyer_discount_percent)
    rc = esc(settings.ref_commission_percent)
    return (
        "<b>Как работает рефералка</b>\n\n"
        f"• По вашей ссылке друг открывает бота и делает <b>первый</b> заказ — "
        f"на него действует скидка <b>{rb}%</b>.\n"
        f"• После того как этот заказ переведён в статус «выдан», на ваш баланс "
        f"начисляется <b>{rc}%</b> от суммы заказа в ₽.\n"
        "• Самоприглашения и повторные начисления за того же человека не учитываются.\n\n"
        "<b>Внутренний баланс</b> (в ₽) можно тратить на новые заказы — кнопка «С баланса» при выборе оплаты. "
        "Реферальный баланс начисляется отдельно (см. профиль)."
    )
