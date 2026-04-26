from __future__ import annotations

from dataclasses import dataclass

from bot.config import Settings
from bot.services.catalog import Product, products_by_id
from bot.util_html import esc


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
    # is_first_order: True пока у пользователя нет ни одного completed-заказа (реф. скидка на «первую выдачу»).
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
    """Комиссия рефереру за первый выданный (completed) заказ приглашённого; % от суммы заказа в ₽."""
    return round(rub_paid * (settings.ref_commission_percent / 100.0), 2)


def rub_per_100_stars_display(products: list[Product], settings: Settings, *, is_first_order: bool) -> float | None:
    """Цена пакета 100 ⭐ в ₽ после скидок - для подзаголовка экрана Stars."""
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


def format_rub_usd_html(rub: float, usd: float, *, rub_decimals: int = 2, usd_decimals: int = 2) -> str:
    """Суммы по заказам из БД: ₽ + номинал USD из заказа (снимок каталога на момент оформления)."""
    return f"{esc(f'{rub:.{rub_decimals}f}')} ₽ (~{esc(f'{usd:.{usd_decimals}f}')} USD)"


def format_shop_quote_money_html(
    settings: Settings,
    rub: float,
    catalog_usd: float,
    *,
    rub_decimals: int = 2,
    usd_decimals: int = 2,
) -> str:
    """
    Живая витрина / чекаут: ₽ согласованы с курсом магазина; USD - эквивалент rub/USD_RUB_RATE
    и отдельно номинал из каталога (products.yaml), чтобы не путать со скидками.
    """
    rate = float(settings.usd_rub_rate)
    if rate <= 0:
        return format_rub_usd_html(rub, catalog_usd, rub_decimals=rub_decimals, usd_decimals=usd_decimals)
    shop_usd = rub / rate
    ru = esc(f"{rub:.{rub_decimals}f}")
    su = esc(f"{shop_usd:.{usd_decimals}f}")
    r = esc(f"{rate:.2f}")
    cat = esc(f"{catalog_usd:.{usd_decimals}f}")
    return (
        f"{ru} ₽ (~{su} USD по курсу магазина <code>{r}</code> ₽/USD; "
        f"номинал в каталоге ~{cat} USD)"
    )
