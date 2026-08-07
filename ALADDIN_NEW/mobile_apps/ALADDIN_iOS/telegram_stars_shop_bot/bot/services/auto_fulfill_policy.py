"""
Политика авто-выдачи (план 37): только правила «можно ли брать заказ в автоматическую выдачу».

Воркер авто-выдачи и смена статусов - в отдельных задачах; здесь чистая логика для тестов и будущего worker.
"""

from __future__ import annotations

from typing import Any, Mapping

from bot.config import Settings


def _mode(order: Mapping[str, Any]) -> str:
    raw = order.get("fulfillment_mode")
    if raw is None:
        return "auto"
    s = str(raw).strip().lower()
    return s if s in ("auto", "manual_only") else "auto"


def _attempts(order: Mapping[str, Any]) -> int:
    try:
        return int(order.get("fulfillment_attempt_count") or 0)
    except (TypeError, ValueError):
        return 0


def auto_fulfill_type_enabled(settings: Settings, *, product_kind: str) -> bool:
    """Включён ли авто-пайплайн для kind каталога (premium | stars | gift)."""
    if not settings.auto_fulfill_enabled:
        return False
    k = (product_kind or "").strip().lower()
    if k == "premium":
        return bool(settings.auto_fulfill_premium_enabled)
    if k in ("stars", "gift"):
        return bool(settings.auto_fulfill_stars_enabled)
    return False


def auto_fulfill_order_eligible(
    order: Mapping[str, Any],
    settings: Settings,
    *,
    product_kind: str,
    stars: int | None = None,
    duration_months: int | None = None,
) -> tuple[bool, str]:
    """
    Можно ли ставить заказ в очередь авто-выдачи (ещё без вызова внешнего API выдачи).

    Возвращает (eligible, reason_if_false) - reason для логов/метрик.
    """
    st = str(order.get("status") or "").strip().lower()
    if st != "paid":
        return False, "not_paid"

    if _mode(order) == "manual_only":
        return False, "manual_only"

    if not auto_fulfill_type_enabled(settings, product_kind=product_kind):
        return False, "type_or_master_disabled"

    k = (product_kind or "").strip().lower()
    if k == "gift" and stars is None:
        return False, "gift_no_stars_quantity"
    if k in ("stars", "gift"):
        try:
            q = int(stars) if stars is not None else 0
        except (TypeError, ValueError):
            q = 0
        if q < 50:
            return False, "stars_quantity_below_minimum"
    if k == "premium":
        m = duration_months
        # 1 / 3 / 6 / 12 — по каталогу; iStar API может принять только 3/6/12 (см. docs), для 1 мес. — fallback оператору.
        if m not in (1, 3, 6, 12):
            return False, "premium_months_invalid"

    cap = float(settings.auto_fulfill_max_order_rub or 0.0)
    if cap > 0:
        try:
            rub = float(order.get("rub_after_discounts") or 0.0)
        except (TypeError, ValueError):
            rub = 0.0
        if rub > cap + 1e-6:
            return False, "over_rub_cap"

    max_att = max(1, int(settings.auto_fulfill_max_attempts or 5))
    if _attempts(order) >= max_att:
        return False, "max_attempts"

    return True, "ok"
