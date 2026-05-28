"""
После оплаты VPN: дождаться vpn_active, отправить .conf и подсказки в Telegram.
"""

from __future__ import annotations

import asyncio
import logging
import time

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BufferedInputFile, InlineKeyboardButton, InlineKeyboardMarkup

from bot.brand_constants import VPN_PRODUCT_NAME
from bot.config import Settings
from bot.services import vpn_admin_support_repo, vpn_api_client
from bot.services.vpn_connect_copy import (
    vpn_file_document_caption_html,
    vpn_file_import_html,
    vpn_qr_photo_caption_html,
    vpn_wireguard_next_step_html,
)
from bot.services.wg_qr_util import wg_qr_filename, wg_qr_png_bytes
from bot.util_html import esc

_log = logging.getLogger(__name__)


def wg_conf_filename(telegram_user_id: int) -> str:
    return f"aladdin-wg-{telegram_user_id}.conf"


def vpn_paid_ack_html(*, order_id: int) -> str:
    """Краткий ack (совместимость). Предпочтительно vpn_paid_summary_html."""
    p = esc(VPN_PRODUCT_NAME)
    return (
        f"<b>✅ Оплата {p} получена</b>\n"
        f"Заказ <code>{esc(order_id)}</code>.\n\n"
        "В <b>этот чат</b> придут <b>файл <code>.conf</code></b> и <b>картинка QR</b> — "
        "обычно <b>от 2 до 5 минут</b>."
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
    until_disp = format_paid_until_display_msk(until_iso)
    p = esc(VPN_PRODUCT_NAME)
    rub_s = esc(f"{float(rub):.2f}")
    return (
        f"<b>✅ Оплата {p} получена</b>\n"
        f"Заказ <code>{esc(order_id)}</code> · <b>{rub_s} ₽</b>\n"
        f"🕘 <b>Подписка до:</b> {esc(until_disp)}\n\n"
        "В этот чат придут <b>файл <code>.conf</code></b> и <b>QR</b> — обычно <b>2–5 минут</b>.\n"
        "Откройте пульт VPN ниже."
    )


def vpn_paid_summary_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌐 AiMonkeyVPN", callback_data="vpn:flow:main")],
        ]
    )


def vpn_delivery_failed_html(*, order_id: int) -> str:
    p = esc(VPN_PRODUCT_NAME)
    return (
        f"<b>⚠️ {p}: настройки задерживаются</b>\n"
        f"Заказ <code>{esc(order_id)}</code> оплачен.\n\n"
        "Через 2–3 минуты откройте 🌐 AiMonkeyVPN → "
        "<b>📥 Файл для подключения</b>. Если не помогло — поддержка с номером заказа."
    )


def _delivery_followup_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌐 AiMonkeyVPN", callback_data="nav:vpn")],
            [InlineKeyboardButton(text="🧪 Проверить VPN", callback_data="vpn:check")],
        ]
    )


async def _fetch_conf_when_ready(settings: Settings, telegram_user_id: int) -> tuple[str | None, str | None]:
    """Ждёт vpn_active и запрашивает .conf. Возвращает (conf, error)."""
    timeout = max(30, int(settings.vpn_provision_delivery_timeout_seconds))
    interval = max(1, int(settings.vpn_provision_delivery_poll_seconds))
    deadline = time.monotonic() + timeout
    vpath = settings.resolved_vpn_db_path()
    last_err = ""

    while time.monotonic() < deadline:
        if vpath is not None:
            row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, telegram_user_id)
            if row:
                st = (row.get("status") or "").strip()
                if st == "vpn_failed":
                    return None, "vpn_failed"
                if st not in ("vpn_active", "vpn_provisioning"):
                    return None, f"status:{st}"

        ok, conf, err = await vpn_api_client.post_wg_conf(settings, telegram_user_id=telegram_user_id)
        if ok and conf:
            return conf, None
        last_err = err or "wg/conf not ready"
        await asyncio.sleep(interval)

    return None, last_err or "timeout"


async def deliver_wg_conf_after_paid(
    settings: Settings,
    *,
    telegram_user_id: int,
    order_id: int,
) -> None:
    if not settings.vpn_auto_send_wg_after_paid:
        return
    if not (settings.vpn_api_base_url or "").strip():
        return

    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        conf, err = await _fetch_conf_when_ready(settings, telegram_user_id)
        if not conf:
            _log.warning(
                "vpn_auto_delivery_failed order=%s user=%s err=%s",
                order_id,
                telegram_user_id,
                err,
            )
            await bot.send_message(
                int(telegram_user_id),
                vpn_delivery_failed_html(order_id=order_id),
                reply_markup=_delivery_followup_kb(),
            )
            return

        await bot.send_message(int(telegram_user_id), vpn_file_import_html())
        doc = BufferedInputFile(conf.encode("utf-8"), filename=wg_conf_filename(telegram_user_id))
        await bot.send_document(
            int(telegram_user_id),
            doc,
            caption=vpn_file_document_caption_html(),
            reply_markup=_delivery_followup_kb(),
        )
        await bot.send_message(
            int(telegram_user_id),
            vpn_wireguard_next_step_html(),
            reply_markup=_delivery_followup_kb(),
        )
        if settings.vpn_auto_send_qr_after_paid:
            png = wg_qr_png_bytes(conf)
            photo = BufferedInputFile(png, filename=wg_qr_filename(telegram_user_id))
            await bot.send_photo(
                int(telegram_user_id),
                photo,
                caption=vpn_qr_photo_caption_html(),
                reply_markup=_delivery_followup_kb(),
            )
        _log.info("vpn_auto_delivery_ok order=%s user=%s", order_id, telegram_user_id)
    except Exception:
        _log.exception("vpn_auto_delivery_crash order=%s user=%s", order_id, telegram_user_id)
    finally:
        await bot.session.close()


def schedule_vpn_wg_delivery_after_paid(
    settings: Settings,
    *,
    order_id: int,
    telegram_user_id: int,
) -> None:
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
