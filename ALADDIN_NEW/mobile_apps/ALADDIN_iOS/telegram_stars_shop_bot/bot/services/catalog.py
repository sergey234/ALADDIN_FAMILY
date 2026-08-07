from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Product:
    id: str
    kind: str  # premium | stars | gift | vpn
    title: str
    emoji: str
    price_usd: float
    # Фиксированная витринная цена в ₽ (VPN); Stars/Premium — только price_usd × USD_RUB_RATE.
    price_rub: float | None = None
    duration_months: int | None = None
    stars: int | None = None
    # Для kind=vpn: срок подписки в днях (→ paid_until при оплате через vpn-11).
    vpn_subscription_days: int | None = None
    featured: bool = False
    sort_order: int = 0
    # Скрыть из инлайн-витрины бота (Partner API / YAML id по-прежнему доступны).
    hide_from_menu: bool = False


def load_products(path: Path) -> list[Product]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    items: list[Product] = []
    for row in data.get("products", []):
        vsd = row.get("vpn_subscription_days")
        pr = row.get("price_rub")
        items.append(
            Product(
                id=str(row["id"]),
                kind=str(row["kind"]),
                title=str(row["title"]),
                emoji=str(row.get("emoji") or "🛍️"),
                price_usd=float(row["price_usd"]),
                price_rub=float(pr) if pr is not None else None,
                duration_months=row.get("duration_months"),
                stars=row.get("stars"),
                vpn_subscription_days=int(vsd) if vsd is not None else None,
                featured=bool(row.get("featured", False)),
                sort_order=int(row.get("sort_order", 0)),
                hide_from_menu=bool(row.get("hide_from_menu", False)),
            )
        )
    return items


def products_by_id(products: list[Product]) -> dict[str, Product]:
    return {p.id: p for p in products}


def product_order_columns(product: Product) -> tuple[str, int | None, int | None]:
    """Поля для строки заказа: kind, количество Stars (для stars/gift), срок Premium в месяцах (vpn — без stars/months)."""
    kind = str(product.kind or "").strip().lower()
    stars = int(product.stars) if kind in ("stars", "gift") and product.stars is not None else None
    months = int(product.duration_months) if kind == "premium" and product.duration_months is not None else None
    return kind, stars, months


def sort_for_display(items: list[Product]) -> list[Product]:
    """
    Сортировка для витрины без «прыжков»:
    - stars/gift со stars: по количеству звёзд (возрастание),
    - premium: по длительности (возрастание),
    - затем цена и стабильный fallback.
    """

    def _price_key(p: Product) -> float:
        if p.price_rub is not None and p.price_rub > 0:
            return float(p.price_rub)
        return float(p.price_usd)

    def _key(p: Product) -> tuple[int, int, float, int, str]:
        kind = (p.kind or "").strip().lower()
        pk = _price_key(p)
        if kind in ("stars", "gift") and p.stars is not None:
            qty = int(p.stars)
            return (0, qty, pk, int(p.sort_order), p.id)
        if kind == "premium" and p.duration_months is not None:
            months = int(p.duration_months)
            return (1, months, pk, int(p.sort_order), p.id)
        if kind == "vpn" and p.vpn_subscription_days is not None:
            return (2, int(p.vpn_subscription_days), pk, int(p.sort_order), p.id)
        return (3, 0, pk, int(p.sort_order), p.id)

    return sorted(items, key=_key)
