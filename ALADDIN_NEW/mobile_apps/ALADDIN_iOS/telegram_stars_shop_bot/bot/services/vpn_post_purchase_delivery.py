"""
После оплаты VPN: дождаться vpn_active, отправить ссылку /sub/ + Happ в Telegram.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Literal

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BufferedInputFile, InlineKeyboardButton, InlineKeyboardMarkup

from bot.brand_constants import VPN_PRODUCT_NAME
from bot.config import Settings
from bot.services import vpn_admin_support_repo
from bot.services.vpn_connect_copy import (
    vpn_happ_auto_update_html,
    vpn_happ_stub_troubleshoot_html,
    vpn_post_payment_three_steps_html,
    vpn_sub_url_block_html,
    vpn_trial_after_delivery_html,
)
from bot.services.vpn_happ_constants import HAPP_APP_NAME
from bot.services.vpn_screen_nav import HAPP_PLUS_BTN, VPN_CHECK_BTN, VPN_HAPP_INSTALL_VIDEO, VPN_NAV_MAIN
from bot.services.vpn_user_links import (
    COPY_SUB_LINK_BTN,
    VPN_QR_CONNECT_BTN,
    resolve_backup_subscription_url,
    subscription_copy_button,
)
from bot.services.wg_qr_util import pay_url_qr_png_bytes
from bot.util_html import esc

_log = logging.getLogger(__name__)


def vpn_paid_ack_html(*, order_id: int) -> str:
    p = esc(VPN_PRODUCT_NAME)
    return (
        f"<b>✅ Оплата {p} получена</b>\n"
        f"Заказ <code>{esc(order_id)}</code>.\n\n"
        f"В <b>этот чат</b> придёт <b>ссылка VPN</b> для <b>{esc(HAPP_APP_NAME)}</b> — "
        "обычно <b>от 2 до 5 минут</b>.\n"
        "<i>Добавьте подписку один раз → включите автообновление в Happ.</i>"
    )


async def vpn_paid_summary_html(
    settings: Settings,
    *,
    order_id: int,
    rub: float,
    telegram_user_id: int,
    vpn_days: int,
) -> str:
    from bot.services.vpn_subscription_dates import (
        compute_paid_until_after_purchase,
        format_paid_until_display_msk,
        preview_paid_until_iso,
    )

    current_until = await preview_paid_until_iso(settings, telegram_user_id)
    until_iso = compute_paid_until_after_purchase(
        current_paid_until=current_until,
        days=int(vpn_days or 30),
    )
    from bot.services.vpn_subscription_notify_ux import format_until_msk, referral_bonus_days

    until_full = esc(format_until_msk(until_iso))
    p = esc(VPN_PRODUCT_NAME)
    rub_s = esc(f"{float(rub):.2f}")
    days = referral_bonus_days(settings)
    ref = f" Можно пригласить друга (+{days} дн.)." if days > 0 else ""
    _ = format_paid_until_display_msk  # keep import used for invoice screens
    return (
        f"<b>✅ Оплата {p} получена</b>\n"
        f"Заказ <code>{esc(order_id)}</code> · <b>{rub_s} ₽</b>\n"
        f"Подписка оформлена до <b>{until_full}</b>.\n"
        f"Напомним за 3 дня до окончания.{ref}\n\n"
        f"В этот чат придёт <b>ссылка VPN</b> ({esc(HAPP_APP_NAME)}) — обычно <b>2–5 минут</b>.\n"
        f"Установите {esc(HAPP_APP_NAME)} из App Store → вставьте ссылку из чата.\n"
        "Откройте «Управление VPN» ниже."
    )


def vpn_paid_summary_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌐 AiMonkeyVPN", callback_data=VPN_NAV_MAIN)],
        ]
    )


def vpn_delivery_failed_html(*, order_id: int) -> str:
    p = esc(VPN_PRODUCT_NAME)
    return (
        f"<b>⚠️ {p}: настройки задерживаются</b>\n"
        f"Заказ <code>{esc(order_id)}</code> оплачен.\n\n"
        "Через 2–3 минуты откройте 👤 Личный кабинет → "
        f"<b>{COPY_SUB_LINK_BTN}</b> или <b>{VPN_QR_CONNECT_BTN}</b>. "
        "Если не помогло — поддержка с номером заказа."
    )


def _delivery_followup_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌐 AiMonkeyVPN", callback_data="nav:vpn")],
            [InlineKeyboardButton(text=VPN_CHECK_BTN, callback_data="vpn:check")],
        ]
    )


def _post_payment_copy_kb(*, sub_url: str) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    sub = (sub_url or "").strip()
    if sub:
        copy_btn = subscription_copy_button(sub)
        if copy_btn:
            rows.append([copy_btn])
    rows.append([InlineKeyboardButton(text=HAPP_PLUS_BTN, callback_data=VPN_HAPP_INSTALL_VIDEO)])
    rows.append([InlineKeyboardButton(text="🌐 AiMonkeyVPN", callback_data=VPN_NAV_MAIN)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _wait_for_subscription_url(
    settings: Settings,
    telegram_user_id: int,
) -> str | None:
    timeout = max(30, int(settings.vpn_provision_delivery_timeout_seconds))
    interval = max(1, int(settings.vpn_provision_delivery_poll_seconds))
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        sub_url = await resolve_backup_subscription_url(settings, telegram_user_id)
        if sub_url:
            return sub_url
        await asyncio.sleep(interval)
    return None


async def deliver_happ_sub_after_paid(
    settings: Settings,
    *,
    telegram_user_id: int,
    order_id: int,
    delivery_kind: Literal["paid", "trial"] = "paid",
) -> None:
    """Ссылка + QR + Happ — одним блоком после оплаты или trial."""
    if not settings.vpn_auto_send_happ_after_paid:
        return
    if not (settings.vpn_api_base_url or "").strip():
        return

    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        sub_url = await _wait_for_subscription_url(settings, telegram_user_id)
        if not sub_url:
            _log.warning("vpn_happ_delivery_no_url order=%s user=%s", order_id, telegram_user_id)
            return

        kb = _post_payment_copy_kb(sub_url=sub_url)

        if delivery_kind == "trial":
            intro = vpn_trial_after_delivery_html()
            steps = vpn_post_payment_three_steps_html()
            html = (
                f"{intro}\n\n{vpn_sub_url_block_html(sub_url)}\n\n{steps}\n\n"
                f"{vpn_happ_stub_troubleshoot_html()}"
            )
        else:
            html = (
                f"{vpn_sub_url_block_html(sub_url)}\n\n"
                f"{vpn_post_payment_three_steps_html()}\n\n"
                f"{vpn_happ_stub_troubleshoot_html()}"
            )
        await bot.send_message(int(telegram_user_id), html, reply_markup=kb)

        png = pay_url_qr_png_bytes(sub_url)
        await bot.send_photo(
            int(telegram_user_id),
            BufferedInputFile(png, filename="aimonkey-vpn-sub-qr.png"),
            caption=(
                "<b>📷 QR-код для подключения</b>\n"
                "Happ → «+» → Добавить подписку → скан QR.\n"
                f"Или «{COPY_SUB_LINK_BTN}» выше."
            ),
            reply_markup=kb,
        )

        await bot.send_message(
            int(telegram_user_id),
            vpn_happ_auto_update_html(),
            reply_markup=_delivery_followup_kb(),
        )
        _log.info("vpn_happ_delivery_ok order=%s user=%s", order_id, telegram_user_id)
        # Сброс цикла напоминаний + welcome kind после выдачи ссылки.
        try:
            from bot.db.database import connect as shop_connect
            from bot.services import vpn_expiry_notify_repo
            from bot.services.vpn_subscription_notify_ux import (
                KIND_TRIAL_WELCOME,
                KIND_WELCOME,
                message_for_paid_kind,
                message_for_trial_kind,
                subscription_notify_kb,
            )

            shop = await shop_connect(settings.database_path)
            try:
                await vpn_expiry_notify_repo.ensure_vpn_expiry_notices_table(shop)
                await vpn_expiry_notify_repo.clear_notices_for_user(
                    shop, telegram_user_id=int(telegram_user_id)
                )
                # paid_until после provision
                from bot.services import vpn_admin_support_repo

                vpath = settings.resolved_vpn_db_path()
                paid = ""
                if vpath is not None:
                    row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(
                        vpath, int(telegram_user_id)
                    )
                    paid = str((row or {}).get("paid_until") or "")
                if paid:
                    if delivery_kind == "trial":
                        wtext = message_for_trial_kind(
                            kind=KIND_TRIAL_WELCOME, paid_until=paid, settings=settings
                        )
                        wkind = KIND_TRIAL_WELCOME
                    else:
                        wtext = message_for_paid_kind(
                            kind=KIND_WELCOME, paid_until=paid, settings=settings
                        )
                        wkind = KIND_WELCOME
                    if wtext and not await vpn_expiry_notify_repo.notice_already_sent(
                        shop, telegram_user_id=int(telegram_user_id), kind=wkind
                    ):
                        await bot.send_message(
                            int(telegram_user_id),
                            wtext,
                            reply_markup=subscription_notify_kb(),
                        )
                        await vpn_expiry_notify_repo.mark_notice_sent(
                            shop, telegram_user_id=int(telegram_user_id), kind=wkind
                        )
            finally:
                await shop.close()
        except Exception:
            _log.exception("vpn_welcome_notify order=%s user=%s", order_id, telegram_user_id)

        # Дожим completed, если provision уже был, а статус завис на paid.
        if delivery_kind == "paid":
            from bot.services.vpn_order_finalize import finalize_vpn_order_completed

            await finalize_vpn_order_completed(settings, order_id)
    except Exception:
        _log.exception("vpn_happ_delivery_crash order=%s user=%s", order_id, telegram_user_id)
    finally:
        await bot.session.close()


def schedule_vpn_happ_delivery_after_paid(
    settings: Settings,
    *,
    order_id: int,
    telegram_user_id: int,
    delivery_kind: Literal["paid", "trial"] = "paid",
) -> None:
    async def _run() -> None:
        try:
            await deliver_happ_sub_after_paid(
                settings,
                telegram_user_id=telegram_user_id,
                order_id=order_id,
                delivery_kind=delivery_kind,
            )
        except Exception:
            _log.exception("vpn_happ_delivery_task order=%s", order_id)

    asyncio.create_task(_run())


async def deliver_wg_conf_after_paid(
    settings: Settings,
    *,
    telegram_user_id: int,
    order_id: int,
) -> None:
    """WG авто-выдача отключена в Happ-only UX (VPN_AUTO_SEND_WG_AFTER_PAID=false)."""
    if not settings.vpn_auto_send_wg_after_paid:
        return
    _log.warning(
        "vpn_wg_auto_delivery_skipped order=%s user=%s — use Happ Plus UX",
        order_id,
        telegram_user_id,
    )


def schedule_vpn_wg_delivery_after_paid(
    settings: Settings,
    *,
    order_id: int,
    telegram_user_id: int,
) -> None:
    if not settings.vpn_auto_send_wg_after_paid:
        return

    async def _run() -> None:
        try:
            await deliver_wg_conf_after_paid(
                settings,
                telegram_user_id=telegram_user_id,
                order_id=order_id,
            )
        except Exception:
            _log.exception("vpn_delivery_task order=%s", order_id)

    asyncio.create_task(_run())


def schedule_vpn_paid_ack(settings: Settings, *, order_id: int, telegram_user_id: int) -> None:
    from bot.db.database import connect
    from bot.services import orders_repo
    from bot.services.buyer_order_notify import send_buyer_html
    from bot.services.catalog import load_products, products_by_id

    async def _run() -> None:
        conn = await connect(settings.database_path)
        try:
            order = await orders_repo.get_order(conn, order_id)
            rub = float(order["rub_after_discounts"]) if order else 0.0
            pmap = products_by_id(load_products(settings.products_path))
            prod = pmap.get(str(order["product_id"] or "")) if order else None
            days = int(prod.vpn_subscription_days) if prod and prod.vpn_subscription_days else 30
            html = await vpn_paid_summary_html(
                settings,
                order_id=order_id,
                rub=rub,
                telegram_user_id=telegram_user_id,
                vpn_days=days,
            )
        except Exception:
            _log.warning("vpn_paid_summary_failed order=%s", order_id, exc_info=True)
            html = vpn_paid_ack_html(order_id=order_id)
        finally:
            await conn.close()
        try:
            await send_buyer_html(settings, telegram_user_id, html)
        except Exception:
            _log.warning("vpn_paid_notify_failed order=%s", order_id, exc_info=True)

    asyncio.create_task(_run())
