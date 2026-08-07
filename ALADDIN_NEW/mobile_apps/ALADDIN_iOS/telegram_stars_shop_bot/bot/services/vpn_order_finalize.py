"""
Закрытие VPN-заказа: paid → completed + реф/профит side-effects.

Раньше vpn_payment_hook делал provision, но оставлял status=paid навсегда —
из-за этого не начислялся реф-бонус и статистика «с покупкой» оставалась 0.
"""

from __future__ import annotations

import logging

from bot.config import Settings
from bot.db.database import connect
from bot.services import orders_repo
from bot.services.order_flow import apply_completed_side_effects
from bot.services.vpn_referral_repo import is_vpn_order_row

logger = logging.getLogger(__name__)


async def finalize_vpn_order_completed(settings: Settings, order_id: int) -> bool:
    """
    Идемпотентно: если VPN-заказ ещё paid/processing → completed + side-effects.
    Возвращает True, если заказ стал/уже был completed с применёнными эффектами.
    """
    conn = await connect(settings.database_path)
    try:
        order = await orders_repo.get_order(conn, order_id)
        if order is None:
            return False
        if not is_vpn_order_row(order):
            return False
        st = str(order["status"] or "").strip().lower()
        if st == "completed":
            # Side-effects могли не пройти (старый баг) — дожимаем.
            if order["fulfillment_applied_at"] is None:
                await apply_completed_side_effects(conn, order_id, settings)
            return True
        if st not in ("paid", "processing"):
            logger.info(
                "vpn_finalize_skip order=%s status=%s",
                order_id,
                st,
            )
            return False
        await orders_repo.update_status(conn, order_id, "completed")
        await apply_completed_side_effects(conn, order_id, settings)
        logger.info("vpn_finalize_completed order=%s", order_id)
        return True
    except Exception:
        logger.exception("vpn_finalize_failed order=%s", order_id)
        return False
    finally:
        await conn.close()
