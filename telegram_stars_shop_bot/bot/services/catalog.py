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
            )
        )
    return items


def products_by_id(products: list[Product]) -> dict[str, Product]:
    return {p.id: p for p in products}


def sort_for_display(items: list[Product]) -> list[Product]:
    """Сначала featured, затем sort_order, затем id."""
    return sorted(items, key=lambda p: (not p.featured, p.sort_order, p.id))
