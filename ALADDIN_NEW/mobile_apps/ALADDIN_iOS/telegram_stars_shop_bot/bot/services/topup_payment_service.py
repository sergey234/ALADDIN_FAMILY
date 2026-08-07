"""Оформление оплаты пополнения баланса (LAVA / крипта)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import aiosqlite

from bot.config import Settings
from bot.services import balance_repo
from bot.services.crypto_pay_api import crypto_pay_invoice_api_ready
from bot.services.lava_api import create_topup_invoice_payment_meta, lava_checkout_configured, lava_invoice_user_message
from bot.services.topup_crypto_payload import encode_topup_crypto_payload
from bot.services.xrocket_pay_api import xrocket_invoice_api_ready

TopupPayMethod = Literal["lava", "crypto"]


@dataclass(frozen=True)
class TopupPayUrl:
    label: str
    url: str
    provider: str


@dataclass(frozen=True)
class TopupCheckoutResult:
    topup_id: int
    amount_rub: float
    method: TopupPayMethod
    pay_urls: list[TopupPayUrl]
    error: str | None = None


def topup_lava_available(settings: Settings) -> bool:
    return lava_checkout_configured(settings)


def topup_crypto_available(settings: Settings) -> bool:
    return crypto_pay_invoice_api_ready(settings) or xrocket_invoice_api_ready(settings)


def topup_payment_methods(settings: Settings) -> list[TopupPayMethod]:
    out: list[TopupPayMethod] = []
    if topup_lava_available(settings):
        out.append("lava")
    if topup_crypto_available(settings):
        out.append("crypto")
    return out


async def begin_topup_checkout(
    conn: aiosqlite.Connection,
    settings: Settings,
    *,
    user_id: int,
    amount_rub: float,
    method: TopupPayMethod,
) -> TopupCheckoutResult:
    amt = round(float(amount_rub), 2)
    tid = await balance_repo.create_topup_request(conn, user_id=user_id, amount_rub=amt, settings=settings)

    if method == "lava":
        row = await balance_repo.get_topup(conn, tid)
        ext = str(row["external_invoice_id"] or "").strip() if row else ""
        pay_stored = str(row["pay_url"] or "").strip() if row else ""
        attempt = int(row["lava_attempt"] or 1) if row else 1
        res = await create_topup_invoice_payment_meta(
            settings,
            topup_id=tid,
            sum_rub=amt,
            existing_invoice_id=ext or None,
            stored_pay_url=pay_stored or None,
            lava_attempt=attempt,
        )
        if not res.pay_url:
            await balance_repo.cancel_topup(conn, tid, user_id)
            return TopupCheckoutResult(tid, amt, method, [], error=res.error or "lava_invoice_unavailable")
        await balance_repo.attach_topup_payment_meta(
            conn,
            tid,
            payment_method="fiat",
            payment_provider="lava",
            external_invoice_id=res.external_id,
            pay_url=res.pay_url,
            lava_attempt=res.lava_attempt,
        )
        return TopupCheckoutResult(
            tid,
            amt,
            method,
            [TopupPayUrl("💳 Оплатить (СБП / карта)", res.pay_url, "lava")],
        )

    pay_urls: list[TopupPayUrl] = []
    desc = f"Пополнение баланса #{tid}"
    payload = encode_topup_crypto_payload(topup_id=tid, due_rub=amt)
    ext_primary: str | None = None

    if crypto_pay_invoice_api_ready(settings):
        u, ext = await _create_topup_crypto_pay_invoice(settings, topup_id=tid, due_rub=amt, description=desc)
        if u:
            pay_urls.append(TopupPayUrl("💎 Crypto Pay (USDT)", u, "crypto_pay"))
            ext_primary = ext

    if xrocket_invoice_api_ready(settings):
        u, ext = await _create_topup_xrocket_invoice(settings, topup_id=tid, due_rub=amt, description=desc)
        if u:
            pay_urls.append(TopupPayUrl("🚀 xRocket (USDT)", u, "xrocket"))
            if not ext_primary:
                ext_primary = ext

    if not pay_urls:
        await balance_repo.cancel_topup(conn, tid, user_id)
        return TopupCheckoutResult(tid, amt, method, [], error="crypto_invoice_unavailable")

    await balance_repo.attach_topup_payment_meta(
        conn,
        tid,
        payment_method="crypto",
        payment_provider=pay_urls[0].provider,
        external_invoice_id=ext_primary,
        pay_url=pay_urls[0].url,
    )
    return TopupCheckoutResult(tid, amt, method, pay_urls)


async def _create_topup_crypto_pay_invoice(
    settings: Settings,
    *,
    topup_id: int,
    due_rub: float,
    description: str,
) -> tuple[str | None, str | None]:
    """Crypto Pay с payload SB1T (topup)."""
    if not crypto_pay_invoice_api_ready(settings):
        return None, None
    from bot.services import crypto_pay_api as cap

    if not cap.crypto_pay_invoice_api_ready(settings):
        return None, None
    rub_per = await cap.resolve_rub_per_usdt(settings)
    if rub_per is None:
        return None, None
    amount_str = cap._due_rub_to_asset_amount_string(due_rub=due_rub, rub_per_unit=rub_per, asset=cap._INVOICE_ASSET)
    if not amount_str:
        return None, None
    payload = encode_topup_crypto_payload(topup_id=topup_id, due_rub=due_rub)
    exp = cap.crypto_invoice_expires_in_seconds(settings)
    params: dict = {
        "asset": cap._INVOICE_ASSET,
        "amount": amount_str,
        "description": description[:1024],
        "payload": payload,
        "expires_in": int(exp),
    }
    paid = (settings.crypto_pay_paid_btn_url or "").strip()
    if paid.startswith(("http://", "https://")):
        params["paid_btn_name"] = "openBot"
        params["paid_btn_url"] = paid
    data = await cap._crypto_pay_get(settings, "createInvoice", params)
    if not data:
        return None, None
    inv = data.get("result")
    if not isinstance(inv, dict):
        return None, None
    url = cap._invoice_pay_url(inv)
    ext = inv.get("invoice_id") or inv.get("id")
    ext_s = str(ext).strip() if ext is not None else None
    return url, ext_s


async def _create_topup_xrocket_invoice(
    settings: Settings,
    *,
    topup_id: int,
    due_rub: float,
    description: str,
) -> tuple[str | None, str | None]:
    if not xrocket_invoice_api_ready(settings):
        return None, None
    from decimal import ROUND_HALF_UP, Decimal

    from bot.services.crypto_pay_api import crypto_invoice_expires_in_seconds, resolve_rub_per_usdt
    from bot.services import xrocket_pay_api as xr

    rub_per = await resolve_rub_per_usdt(settings)
    if rub_per is None or rub_per <= 0:
        return None, None
    due_dec = Decimal(str(round(float(due_rub), 2)))
    rpu = Decimal(str(rub_per))
    amt = float((due_dec / rpu).quantize(Decimal("0.000000001"), rounding=ROUND_HALF_UP))
    if amt <= 0:
        return None, None
    payload = encode_topup_crypto_payload(topup_id=topup_id, due_rub=due_rub)
    exp = min(86400, int(crypto_invoice_expires_in_seconds(settings)))
    body: dict = {
        "amount": amt,
        "numPayments": 1,
        "currency": "USDT",
        "description": description[:1000],
        "payload": payload,
        "expiredIn": exp,
        "commentsEnabled": False,
    }
    raw = await xr._xrocket_post_json(settings, "/tg-invoices", body)
    if not raw or raw.get("success") is not True:
        return None, None
    data = raw.get("data")
    if not isinstance(data, dict):
        return None, None
    link = data.get("link")
    if isinstance(link, str) and link.startswith(("http://", "https://", "tg://")):
        ext = data.get("id")
        return link, (str(ext).strip() if ext is not None else None)
    return None, None


def topup_checkout_error_message(code: str | None) -> str:
    if code and code.startswith("lava"):
        return lava_invoice_user_message(code)
    return {
        "topup_amount_invalid": "Сумма вне допустимого диапазона.",
        "topup_pending_cap": "Слишком много заявок в ожидании. Дождитесь зачисления или отмените старые.",
        "topup_rate_limit": "Подождите немного перед следующей заявкой.",
        "crypto_invoice_unavailable": "Крипто-оплата временно недоступна. Попробуйте LAVA или позже.",
        "lava_invoice_unavailable": "Оплата картой/СБП временно недоступна. Попробуйте крипту или позже.",
    }.get(code or "", "Не удалось создать счёт. Попробуйте позже.")
