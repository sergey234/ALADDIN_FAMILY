from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Product:
    id: str
    kind: str  # premium | stars | gift
    title: str
    emoji: str
    price_usd: float
    duration_months: int | None = None
    stars: int | None = None
    featured: bool = False
    sort_order: int = 0
    # Скрыть из инлайн-витрины бота (Partner API / YAML id по-прежнему доступны).
    hide_from_menu: bool = False


def load_products(path: Path) -> list[Product]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    items: list[Product] = []
    for row in data.get("products", []):
        items.append(
            Product(
                id=str(row["id"]),
                kind=str(row["kind"]),
                title=str(row["title"]),
                emoji=str(row.get("emoji") or "🛍️"),
                price_usd=float(row["price_usd"]),
                duration_months=row.get("duration_months"),
                stars=row.get("stars"),
                featured=bool(row.get("featured", False)),
                sort_order=int(row.get("sort_order", 0)),
                hide_from_menu=bool(row.get("hide_from_menu", False)),
            )
        )
    return items


def products_by_id(products: list[Product]) -> dict[str, Product]:
    return {p.id: p for p in products}


def sort_for_display(items: list[Product]) -> list[Product]:
    """
    Сортировка для витрины без «прыжков»:
    - stars/gift со stars: по количеству звёзд (возрастание),
    - premium: по длительности (возрастание),
    - затем цена и стабильный fallback.
    """

    def _key(p: Product) -> tuple[int, int, float, int, str]:
        kind = (p.kind or "").strip().lower()
        if kind in ("stars", "gift") and p.stars is not None:
            qty = int(p.stars)
            return (0, qty, float(p.price_usd), int(p.sort_order), p.id)
        if kind == "premium" and p.duration_months is not None:
            months = int(p.duration_months)
            return (1, months, float(p.price_usd), int(p.sort_order), p.id)
        return (2, 0, float(p.price_usd), int(p.sort_order), p.id)

    return sorted(items, key=_key)
