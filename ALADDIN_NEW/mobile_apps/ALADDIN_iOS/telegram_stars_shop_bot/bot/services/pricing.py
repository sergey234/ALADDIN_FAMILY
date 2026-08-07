from __future__ import annotations

from dataclasses import dataclass

from bot.config import Settings
from bot.services.catalog import Product, products_by_id
from bot.util_html import esc

# Stars / Premium / gift / VPN — только каталожная цена, без реф. и оптовых скидок.
_NO_DISCOUNT_KINDS = frozenset({"stars", "premium", "gift", "vpn"})


def discounts_disabled_for_product_kind(product_kind: str | None) -> bool:
    return (product_kind or "").strip().lower() in _NO_DISCOUNT_KINDS


@dataclass(frozen=True)
class PriceQuote:
    usd: float
    rub_list: float
    rub_referral_discount: float
    rub_wholesale_discount: float
    rub_final: float
    rub_promo_discount: float = 0.0


def list_price_rub(product: Product, settings: Settings) -> float:
    """Витринная цена в ₽: price_rub из каталога (VPN) или price_usd × USD_RUB_RATE (Stars/Premium)."""
    if product.price_rub is not None and product.price_rub > 0:
        return round(float(product.price_rub), 2)
    return round(float(product.price_usd) * float(settings.usd_rub_rate), 2)


def catalog_usd_for_quote(product: Product, settings: Settings, *, rub_list: float) -> float:
    """
    USD-снимок для заказа и подписи в чекауте.
    Stars/Premium: номинал из products.yaml (price_usd).
    VPN с price_rub: эквивалент rub / USD_RUB_RATE на момент расчёта (как у Stars: rub = usd × rate).
    """
    if product.price_rub is not None and product.price_rub > 0:
        rate = float(settings.usd_rub_rate)
        if rate > 0:
            return round(rub_list / rate, 4)
        return float(product.price_usd)
    return float(product.price_usd)


def stars_unit_product(products: list[Product]) -> Product | None:
    """Базовый пакет для расчёта цены за 1 ⭐ (ориентир stars_100)."""
    pmap = products_by_id(products)
    p = pmap.get("stars_100")
    if p:
        return p
    for x in products:
        if x.kind == "stars" and (x.stars or 0) == 100:
            return x
    return None


def quote_custom_stars(
    qty: int,
    products: list[Product],
    settings: Settings,
    *,
    is_first_order: bool,
) -> PriceQuote:
    """Цена произвольного количества Stars от unit price пакета 100 ⭐."""
    unit = stars_unit_product(products)
    if not unit or qty <= 0:
        return PriceQuote(
            usd=0.0,
            rub_list=0.0,
            rub_referral_discount=0.0,
            rub_wholesale_discount=0.0,
            rub_final=0.0,
        )
    rub_per_star = list_price_rub(unit, settings) / 100.0
    usd_per_star = float(unit.price_usd) / 100.0
    rub_list = round(rub_per_star * qty, 2)
    usd = round(usd_per_star * qty, 4)

    ref_disc = 0.0
    wholesale_disc = 0.0
    rub_after = rub_list
    return PriceQuote(
        usd=usd,
        rub_list=rub_list,
        rub_referral_discount=ref_disc,
        rub_wholesale_discount=wholesale_disc,
        rub_final=round(rub_after, 2),
    )


def quote_product(
    product: Product,
    settings: Settings,
    *,
    is_first_order: bool,
) -> PriceQuote:
    rub_list = list_price_rub(product, settings)
    usd = catalog_usd_for_quote(product, settings, rub_list=rub_list)

    ref_disc = 0.0
    wholesale_disc = 0.0
    if not discounts_disabled_for_product_kind(product.kind):
        if is_first_order:
            ref_disc = round(rub_list * (settings.ref_buyer_discount_percent / 100.0), 2)
        if product.kind == "stars" and (product.stars or 0) >= settings.stars_wholesale_threshold:
            wholesale_disc = round(rub_list * (settings.stars_wholesale_discount_percent / 100.0), 2)

    rub_after = max(0.0, rub_list - ref_disc - wholesale_disc)
    return PriceQuote(
        usd=usd,
        rub_list=rub_list,
        rub_referral_discount=ref_disc,
        rub_wholesale_discount=wholesale_disc,
        rub_final=round(rub_after, 2),
        rub_promo_discount=0.0,
    )


def apply_promo_to_quote(
    q: PriceQuote,
    *,
    product_kind: str,
    promo,
) -> PriceQuote:
    """Накладывает активный промокод на уже посчитанный quote (без изменения checkout)."""
    if promo is None:
        return q
    from bot.services.promo_repo import PromoOffer, compute_promo_discount_rub

    if not isinstance(promo, PromoOffer):
        return q
    disc = compute_promo_discount_rub(
        rub_list=q.rub_list,
        rub_after_other=q.rub_final,
        product_kind=product_kind,
        promo=promo,
    )
    if disc <= 0:
        return q
    return PriceQuote(
        usd=q.usd,
        rub_list=q.rub_list,
        rub_referral_discount=q.rub_referral_discount,
        rub_wholesale_discount=q.rub_wholesale_discount,
        rub_promo_discount=disc,
        rub_final=round(max(0.0, q.rub_final - disc), 2),
    )


def referral_discount_percent_snapshot(*, rub_list: float, rub_referral_discount: float) -> float:
    """Доля реф. скидки от базовой цены в ₽ до скидок (для снимка в БД)."""
    base = max(0.0, float(rub_list))
    if base <= 1e-9:
        return 0.0
    return round(100.0 * max(0.0, float(rub_referral_discount)) / base, 4)


def commission_for_first_order(
    rub_paid: float,
    settings: Settings,
    *,
    override_percent: float | None = None,
) -> float:
    """Комиссия рефереру за первый выданный заказ; % от суммы заказа в ₽ (override партнёра опционален)."""
    pct = float(settings.ref_commission_percent)
    if override_percent is not None:
        try:
            ov = float(override_percent)
            if ov > 0:
                pct = ov
        except (TypeError, ValueError):
            pass
    return round(float(rub_paid) * (pct / 100.0), 2)


def rub_per_100_stars_display(products: list[Product], settings: Settings, *, is_first_order: bool) -> float | None:
    """Цена пакета 100 ⭐ в ₽ (каталог) — для подзаголовка экрана Stars."""
    _ = is_first_order
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
    # Stars/Premium: rub = price_usd × rate → shop_usd ≈ catalog_usd. VPN (price_rub): то же после catalog_usd_for_quote.
    if abs(shop_usd - float(catalog_usd)) < 0.05:
        return f"{ru} ₽ (~{su} USD, курс магазина <code>{r}</code> ₽/USD)"
    return (
        f"{ru} ₽ (~{su} USD по курсу магазина <code>{r}</code> ₽/USD; "
        f"номинал в каталоге ~{cat} USD)"
    )
