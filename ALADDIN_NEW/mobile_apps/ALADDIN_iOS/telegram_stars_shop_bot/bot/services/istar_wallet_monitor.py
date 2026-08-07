"""Мониторинг баланса ApiFragment перед автовыдачей Stars/Premium."""

from __future__ import annotations

import logging
import re

from bot.config import Settings
from bot.services.alerts import send_alert
from bot.services.istar_fulfill_client import IstarFulfillClient, IstarFulfillError
from bot.services.istar_fulfill_errors import istar_error_is_server_http  # noqa: F401 — re-export

_log = logging.getLogger(__name__)

# Алерт «закончился/низкий баланс» — не чаще раза в 8 часов.
_LOW_BALANCE_ALERT_COOLDOWN_SEC = 8 * 60 * 60

_INSUFFICIENT_FUNDS = re.compile(
    r"insufficient|not\s+enough|low\s+balance|balance\s+too\s+low|недостаточно",
    re.IGNORECASE,
)


def istar_error_looks_like_insufficient_funds(exc: BaseException) -> bool:
    text = str(exc)
    body = getattr(exc, "body", None)
    if isinstance(body, str) and body:
        text = f"{text} {body}"
    return bool(_INSUFFICIENT_FUNDS.search(text))


async def notify_ops_istar_low_ton_balance(
    settings: Settings,
    *,
    balance_ton: float,
    threshold_ton: float,
) -> None:
    if not settings.auto_fulfill_failure_alerts_enabled:
        return
    try:
        await send_alert(
            settings,
            severity="warning",
            title="ApiFragment: низкий баланс TON",
            body=(
                f"balance_ton={balance_ton:.4f} threshold_ton={threshold_ton:.4f} — "
                "автовыдача Stars/Premium пропущена. Пополните кошелёк ApiFragment "
                "(кабинет https://apifragment.online)."
            ),
            dedupe_key="apifragment_low_ton",
            cooldown_seconds=_LOW_BALANCE_ALERT_COOLDOWN_SEC,
        )
    except Exception:
        _log.exception("apifragment_low_ton_alert_failed")


async def notify_ops_istar_insufficient_on_create(
    settings: Settings,
    *,
    order_id: int,
    exc: BaseException,
) -> None:
    if not settings.auto_fulfill_failure_alerts_enabled:
        return
    if not istar_error_looks_like_insufficient_funds(exc):
        return
    try:
        await send_alert(
            settings,
            severity="warning",
            title="ApiFragment: недостаточно средств на выдачу",
            body=f"order_id={order_id} err={str(exc)[:500]}",
            dedupe_key="apifragment_insufficient_funds",
            cooldown_seconds=_LOW_BALANCE_ALERT_COOLDOWN_SEC,
        )
    except Exception:
        _log.exception("apifragment_insufficient_alert_failed order=%s", order_id)


async def notify_ops_istar_search_http_error(
    settings: Settings,
    *,
    order_id: int,
    username: str,
    exc: BaseException,
) -> None:
    """Ops-алерт при 5xx на resolve_user / ApiFragment недоступен."""
    if not settings.auto_fulfill_failure_alerts_enabled:
        return
    if not istar_error_is_server_http(exc):
        return
    status = getattr(exc, "status_code", None)
    try:
        await send_alert(
            settings,
            severity="warning",
            title="ApiFragment API 5xx on resolve_user",
            body=(
                f"order_id={order_id} recipient=@{username} "
                f"status={status} err={str(exc)[:500]}"
            ),
            dedupe_key="apifragment_resolve_http_5xx",
        )
    except Exception:
        _log.exception("apifragment_resolve_5xx_alert_failed order=%s", order_id)


async def check_istar_ton_balance_for_auto_fulfill(
    settings: Settings,
    istar: IstarFulfillClient,
) -> tuple[bool, float | None]:
    """
    True — можно брать заказы в авто.
    False — баланс ниже порога или не удалось прочитать (при заданном пороге).
    """
    threshold = float(settings.istar_min_ton_balance_alert or 0.0)
    if threshold <= 0:
        return True, None
    try:
        balance = await istar.get_wallet_balance_ton()
    except IstarFulfillError as exc:
        _log.warning("apifragment_wallet_balance_fetch_failed err=%s", exc)
        return True, None
    if balance + 1e-9 < threshold:
        await notify_ops_istar_low_ton_balance(
            settings, balance_ton=balance, threshold_ton=threshold
        )
        return False, balance
    return True, balance
