from __future__ import annotations

from dataclasses import dataclass

from bot.config import Settings
from bot.services.catalog import Product, products_by_id


@dataclass(frozen=True)
class PriceQuote:
    usd: float
    rub_list: float
    rub_referral_discount: float
    rub_wholesale_discount: float
    rub_final: float


def quote_product(
    product: Product,
    settings: Settings,
    *,
    is_first_order: bool,
) -> PriceQuote:
    usd = product.price_usd
    rub_list = round(usd * settings.usd_rub_rate, 2)

    ref_disc = 0.0
    if is_first_order:
        ref_disc = round(rub_list * (settings.ref_buyer_discount_percent / 100.0), 2)

    wholesale_disc = 0.0
    if product.kind == "stars" and (product.stars or 0) >= settings.stars_wholesale_threshold:
        wholesale_disc = round(rub_list * (settings.stars_wholesale_discount_percent / 100.0), 2)

    rub_after = max(0.0, rub_list - ref_disc - wholesale_disc)
    return PriceQuote(
        usd=usd,
        rub_list=rub_list,
        rub_referral_discount=ref_disc,
        rub_wholesale_discount=wholesale_disc,
        rub_final=round(rub_after, 2),
    )


def commission_for_first_order(rub_paid: float, settings: Settings) -> float:
    return round(rub_paid * (settings.ref_commission_percent / 100.0), 2)


def rub_per_100_stars_display(products: list[Product], settings: Settings, *, is_first_order: bool) -> float | None:
    """Цена пакета 100 ⭐ в ₽ после скидок — для подзаголовка экрана Stars."""
    pmap = products_by_id(products)
    p = pmap.get("stars_100")
    if not p:
        for x in products:
            if x.kind == "stars" and (x.stars or 0) == 100:
                p = x
                break
    if not p:
        return None
    q = quote_product(p, settings, is_first_order=is_first_order)
    return q.rub_final
