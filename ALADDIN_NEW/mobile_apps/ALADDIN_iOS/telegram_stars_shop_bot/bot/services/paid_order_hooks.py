"""Хуки сразу после status=paid: VPN provision + автовыдача Stars/Premium."""

from __future__ import annotations

from bot.config import Settings
from bot.services.admin_order_status_notify import schedule_notify_admins_order_paid
from bot.services.auto_fulfill_trigger import schedule_auto_fulfill_after_paid
from bot.services.vpn_payment_hook import schedule_vpn_provision_after_paid


def schedule_post_paid_order_hooks(settings: Settings, order_id: int) -> None:
    schedule_notify_admins_order_paid(settings, order_id)
    schedule_vpn_provision_after_paid(settings, order_id)
    schedule_auto_fulfill_after_paid(settings, order_id)
