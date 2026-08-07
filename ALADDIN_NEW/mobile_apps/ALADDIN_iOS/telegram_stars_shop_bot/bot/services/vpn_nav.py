"""Сборка экрана «AiMonkeyVPN — подключение» для навигации и shop (без циклических импортов handlers)."""

from __future__ import annotations

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup

from bot.config import Settings
from bot.services.catalog import Product

VPN_FLOW_MAIN_CALLBACK = "vpn:flow:main"


async def build_vpn_main_screen(
    bot: Bot,
    settings: Settings,
    conn,
    products: list[Product],
    user_id: int,
) -> tuple[str, InlineKeyboardMarkup]:
    from bot.handlers.vpn import (  # noqa: PLC0415 — избегаем import cycle shop↔vpn на уровне модуля
        build_vpn_root_kb,
        vpn_main_block_html,
    )

    body = await vpn_main_block_html(settings, products, user_id)
    return body, await build_vpn_root_kb(bot, settings, conn, products, user_id)
