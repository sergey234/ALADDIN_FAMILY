"""
Вызовы HTTPS Crypto Pay API (createInvoice, getExchangeRates).

GET {origin}/api/{method} + заголовок Crypto-Pay-API-Token - как в открытых SDK под @CryptoBot.
"""

from __future__ import annotations

import asyncio
import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Mapping

import httpx

from bot.config import Settings
from bot.services.crypto_pay_payload import (
    crypto_invoice_expires_in_seconds,
    encode_crypto_invoice_payload,
)

_log = logging.getLogger(__name__)

# В продукте для оплаты через провайдеров - только USDT (Crypto Pay / xRocket; сеть выбирает счёт).
_INVOICE_ASSET = "USDT"

_MIN_ASSET_AMOUNTS: dict[str, Decimal] = {
    "USDT": Decimal("0.01"),
    "TON": Decimal("0.01"),
    "BTC": Decimal("0.00001"),
    "ETH": Decimal("0.0001"),
    "USDC": Decimal("0.01"),
    "BUSD": Decimal("0.01"),
}


def crypto_pay_invoice_api_ready(settings: Settings) -> bool:
    """True - можно вызывать createInvoice (включено в .env и задан токен)."""
    if not settings.crypto_pay_enabled:
        return False
    return bool((settings.crypto_pay_api_token or "").strip())


def _fallback_rub_per_usdt(settings: Settings) -> float | None:
    if settings.usdt_rub_rate and float(settings.usdt_rub_rate) > 0:
        return float(settings.usdt_rub_rate)
    if settings.usd_rub_rate and float(settings.usd_rub_rate) > 0:
        return float(settings.usd_rub_rate)
    return None


def _maybe_warn_crypto_pay_token(settings: Settings) -> None:
    """Частая ошибка: в CRYPTO_PAY_API_TOKEN кладут BOT_TOKEN вида 123456:AA… - это не Crypto Pay."""
    if not settings.crypto_pay_enabled:
        return
    t = (settings.crypto_pay_api_token or "").strip()
    if ":" not in t:
        return
    left, _, right = t.partition(":")
    if left.isdigit() and len(right) >= 25:
        _log.warning(
            "CRYPTO_PAY_API_TOKEN похож на Telegram BOT_TOKEN (формат id:secret). "
            "Для @CryptoBot нужен API-токен приложения Crypto Pay (Crypto Pay → Create App, команда /pay), не BOT_TOKEN."
        )
    da = (settings.crypto_pay_default_asset or "").strip().upper()
    if da and da != _INVOICE_ASSET:
        _log.warning(
            "CRYPTO_PAY_DEFAULT_ASSET=%s игнорируется: в магазине для счетов используется только USDT.",
            da,
        )


async def resolve_rub_per_usdt(settings: Settings) -> float | None:
    """
    Сколько ₽ за 1 USDT: сначала getExchangeRates Crypto Pay (если задан CRYPTO_PAY_API_TOKEN),
    иначе / при отсутствии пары - USDT_RUB_RATE или USD_RUB_RATE.
    """
    rates = await crypto_pay_get_exchange_rates(settings)
    r = rub_per_asset_unit_from_rates(rates, "USDT")
    if r:
        return r
    return _fallback_rub_per_usdt(settings)


def rub_per_asset_unit_from_rates(rates: list[Mapping[str, Any]], asset: str) -> float | None:
    """
    Сколько ₽ за 1 единицу актива (например курс из getExchangeRates для USDT→RUB), если в списке есть прямой курс к RUB.
    """
    want = asset.strip().upper()
    for row in rates:
        src = str(row.get("source") or row.get("Source") or "").strip().upper()
        tgt = str(row.get("target") or row.get("Target") or "").strip().upper()
        raw = row.get("rate") if "rate" in row else row.get("Rate")
        if raw is None:
            continue
        try:
            rate = float(raw)
        except (TypeError, ValueError):
            continue
        if rate <= 0:
            continue
        if src == want and tgt == "RUB":
            return rate
        if src == "RUB" and tgt == want:
            return 1.0 / rate
    return None


def _format_asset_amount_decimal(amount: Decimal) -> str:
    q = amount.quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
    s = format(q, "f").rstrip("0").rstrip(".")
    return s or "0"


def _due_rub_to_asset_amount_string(*, due_rub: float, rub_per_unit: float, asset: str) -> str | None:
    if rub_per_unit <= 0 or due_rub < 0.01:
        return None
    due_dec = Decimal(str(round(float(due_rub), 2)))
    rpu = Decimal(str(rub_per_unit))
    raw_amt = due_dec / rpu
    floor_amt = _MIN_ASSET_AMOUNTS.get(asset.upper(), Decimal("0.00000001"))
    amt = raw_amt if raw_amt >= floor_amt else floor_amt
    return _format_asset_amount_decimal(amt)


def _invoice_pay_url(inv: Mapping[str, Any]) -> str | None:
    for k in (
        "pay_url",
        "bot_invoice_url",
        "mini_app_invoice_url",
        "PayUrl",
        "BotInvoiceUrl",
        "MiniAppInvoiceUrl",
    ):
        v = inv.get(k)
        if isinstance(v, str) and v.startswith(("http://", "https://", "tg://")):
            return v
    return None


def _normalize_rates_list(data: dict[str, Any]) -> list[dict[str, Any]]:
    res = data.get("result")
    if isinstance(res, list):
        return [x for x in res if isinstance(x, dict)]
    return []


async def _crypto_pay_get(
    settings: Settings,
    method: str,
    params: dict[str, Any],
) -> dict[str, Any] | None:
    token = (settings.crypto_pay_api_token or "").strip()
    if not token:
        return None
    origin = settings.crypto_pay_api_origin()
    url = f"{origin}/api/{method}"
    headers = {"Crypto-Pay-API-Token": token, "Accept": "application/json"}
    qp = {k: v for k, v in params.items() if v is not None}
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(url, params=qp, headers=headers)
        except Exception:
            _log.exception("crypto_pay_http_error method=%s attempt=%s", method, attempt)
            if attempt == 2:
                return None
            await asyncio.sleep(0.4 * (attempt + 1))
            continue
        if r.status_code == 200:
            try:
                data = r.json()
            except Exception:
                _log.warning("crypto_pay_invalid_json method=%s", method)
                return None
            if isinstance(data, dict) and data.get("ok") is True:
                return data
            _log.warning("crypto_pay_not_ok method=%s body=%s", method, str(data)[:500])
            return None
        if r.status_code in (429, 502, 503, 504) or r.status_code >= 500:
            _log.warning(
                "crypto_pay_retryable method=%s status=%s attempt=%s",
                method,
                r.status_code,
                attempt,
            )
            if attempt < 2:
                await asyncio.sleep(0.5 * (attempt + 1))
                continue
        _log.warning("crypto_pay_bad_status method=%s status=%s body=%s", method, r.status_code, r.text[:400])
        return None
    return None


async def crypto_pay_get_exchange_rates(settings: Settings) -> list[dict[str, Any]]:
    data = await _crypto_pay_get(settings, "getExchangeRates", {})
    if not data:
        return []
    return _normalize_rates_list(data)


async def create_crypto_pay_invoice_checkout_url(
    settings: Settings,
    *,
    order_id: int,
    due_rub: float,
    description: str | None = None,
) -> str | None:
    url, _ = await create_crypto_pay_invoice_checkout_meta(
        settings,
        order_id=order_id,
        due_rub=due_rub,
        description=description,
    )
    return url


async def create_crypto_pay_invoice_checkout_meta(
    settings: Settings,
    *,
    order_id: int,
    due_rub: float,
    description: str | None = None,
) -> tuple[str | None, str | None]:
    """
    Создаёт счёт Crypto Pay и возвращает URL для кнопки (pay_url / bot_invoice_url).
    """
    if not crypto_pay_invoice_api_ready(settings):
        return None, None
    _maybe_warn_crypto_pay_token(settings)
    rub_per = await resolve_rub_per_usdt(settings)
    if rub_per is None:
        _log.warning("crypto_pay_no_rub_rate asset=%s order_id=%s", _INVOICE_ASSET, order_id)
        return None, None
    amount_str = _due_rub_to_asset_amount_string(
        due_rub=due_rub, rub_per_unit=rub_per, asset=_INVOICE_ASSET
    )
    if not amount_str:
        _log.warning("crypto_pay_amount_too_small order_id=%s due=%s", order_id, due_rub)
        return None, None
    desc = (description or f"Order #{order_id}").strip()
    if len(desc) > 1024:
        desc = desc[:1021] + "..."
    payload = encode_crypto_invoice_payload(order_id=order_id, due_rub=due_rub)
    exp = crypto_invoice_expires_in_seconds(settings)
    params: dict[str, Any] = {
        "asset": _INVOICE_ASSET,
        "amount": amount_str,
        "description": desc,
        "payload": payload,
        "expires_in": int(exp),
    }
    paid = (settings.crypto_pay_paid_btn_url or "").strip()
    if paid.startswith("http://") or paid.startswith("https://"):
        params["paid_btn_name"] = "openBot"
        params["paid_btn_url"] = paid
    data = await _crypto_pay_get(settings, "createInvoice", params)
    if not data:
        return None, None
    inv = data.get("result")
    if not isinstance(inv, dict):
        _log.warning("crypto_pay_create_invoice_no_result order_id=%s raw=%s", order_id, str(data)[:400])
        return None, None
    url = _invoice_pay_url(inv)
    if not url:
        _log.warning("crypto_pay_create_invoice_no_url order_id=%s keys=%s", order_id, list(inv.keys()))
        return None, None
    ext = inv.get("invoice_id") or inv.get("id")
    ext_s = str(ext).strip() if ext is not None else None
    return url, (ext_s or None)
