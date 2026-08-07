from __future__ import annotations

from io import BytesIO
from typing import Any


def sales_trend_charts_png(
    *,
    daily_rows: list[Any],
    weekly_rows: list[Any],
    title_suffix: str = "",
) -> bytes | None:
    """
    Два графика: выручка по дням и по неделям (выданные заказы).
    Возвращает PNG или None, если matplotlib недоступен.
    """
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    fig, (ax_day, ax_week) = plt.subplots(2, 1, figsize=(10, 7.5), dpi=110)
    ttl = "Продажи (выдано, ₽)"
    if title_suffix:
        ttl = f"{ttl} · {title_suffix}"
    fig.suptitle(ttl, fontsize=12)

    if daily_rows:
        xd = [str(r["d"] or "") for r in daily_rows]
        yd = [float(r["rev"] or 0) for r in daily_rows]
        ax_day.bar(xd, yd, color="steelblue", alpha=0.85)
        ax_day.set_ylabel("₽ / день")
        ax_day.tick_params(axis="x", rotation=55, labelsize=8)
        ax_day.grid(axis="y", alpha=0.3)
    else:
        ax_day.text(0.5, 0.5, "Нет данных по дням", ha="center", va="center")
        ax_day.set_axis_off()

    if weekly_rows:
        xw = [str(r["wk"] or "") for r in weekly_rows]
        yw = [float(r["rev"] or 0) for r in weekly_rows]
        ax_week.bar(xw, yw, color="darkseagreen", alpha=0.9)
        ax_week.set_ylabel("₽ / неделя")
        ax_week.tick_params(axis="x", rotation=45, labelsize=8)
        ax_week.grid(axis="y", alpha=0.3)
    else:
        ax_week.text(0.5, 0.5, "Нет данных по неделям", ha="center", va="center")
        ax_week.set_axis_off()

    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()
