"""Startup checks for auto-fulfill / iStar configuration."""

from __future__ import annotations

import logging

from bot.config import Settings
from bot.services.istar_fulfill_client import IstarFulfillClient

_log = logging.getLogger(__name__)


def log_auto_fulfill_startup_warnings(settings: Settings) -> None:
    """Логирует предупреждения при включённой автовыдаче без полной настройки iStar."""
    if not settings.auto_fulfill_enabled:
        return
    if not IstarFulfillClient.is_configured(settings):
        _log.warning(
            "AUTO_FULFILL_ENABLED=true, но ISTAR_API_KEY пуст — воркер не сможет выдавать заказы. "
            "Заполните ISTAR_* в shared/.env (см. docs/FRAGMENT_AUTO_FULFILL_ML_HANDOFF.md)."
        )
    if not (settings.istar_webhook_secret or "").strip():
        _log.warning(
            "AUTO_FULFILL_ENABLED=true, но ISTAR_WEBHOOK_SECRET пуст — вебхук iStar не проверяет подпись. "
            "Задайте секрет в .env и в кабинете iStar."
        )
    if not settings.auto_fulfill_stars_enabled and not settings.auto_fulfill_premium_enabled:
        _log.warning(
            "AUTO_FULFILL_ENABLED=true, но AUTO_FULFILL_STARS_ENABLED и AUTO_FULFILL_PREMIUM_ENABLED выключены — "
            "воркер не возьмёт ни один тип товара."
        )
    threshold = float(settings.istar_min_ton_balance_alert or 0.0)
    if threshold > 0:
        _log.info(
            "AUTO_FULFILL: порог TON ISTAR_MIN_TON_BALANCE_ALERT=%.4f — ниже воркер пропускает batch.",
            threshold,
        )
    else:
        _log.info(
            "AUTO_FULFILL: ISTAR_MIN_TON_BALANCE_ALERT=0 — проверка баланса TON перед batch отключена."
        )
