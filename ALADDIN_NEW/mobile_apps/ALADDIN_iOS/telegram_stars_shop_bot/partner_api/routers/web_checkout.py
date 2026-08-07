"""
Public web-checkout for AiMonkeyVPN (get.aladdin-ai.ru).

No partner API key — rate-limited public routes under /v1/web/.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Annotated, Any, Dict, List, Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel, Field

from bot.brand_constants import SHOP_BOT_USERNAME, VPN_PRODUCT_NAME
from bot.config import Settings
from bot.db.database import connect
from bot.services import accounts_repo, orders_repo, vpn_admin_support_repo, vpn_api_client, vpn_referral_repo
from bot.services.catalog import load_products
from bot.services.lava_api import create_invoice_payment_meta, lava_checkout_configured
from partner_api.deps import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["web-checkout"])
public_router = APIRouter(tags=["web-public"])

_STATIC_DIR = Path(__file__).resolve().parents[1] / "static" / "web"

# Simple in-memory rate limit: IP → timestamps
_checkout_hits: dict[str, deque[float]] = defaultdict(deque)
_CHECKOUT_LIMIT = 8
_CHECKOUT_WINDOW_SEC = 600.0


def _client_ip(request: Request) -> str:
    xff = (request.headers.get("x-forwarded-for") or "").split(",")[0].strip()
    if xff:
        return xff
    if request.client:
        return request.client.host or "0.0.0.0"
    return "0.0.0.0"


def _rate_ok(ip: str) -> bool:
    now = time.time()
    q = _checkout_hits[ip]
    while q and now - q[0] > _CHECKOUT_WINDOW_SEC:
        q.popleft()
    if len(q) >= _CHECKOUT_LIMIT:
        return False
    q.append(now)
    return True


def _settings_dep(request: Request) -> Settings:
    return get_settings(request)


class CheckoutBody(BaseModel):
    product_id: str = Field(..., min_length=3, max_length=64)
    ref_code: Optional[str] = Field(default=None, max_length=32)
    legal_accepted: bool = False
    account_id: Optional[str] = Field(default=None, max_length=64)
    session_secret: Optional[str] = Field(default=None, max_length=128)
    nickname: Optional[str] = Field(default=None, max_length=32)


class NicknameBody(BaseModel):
    account_id: str = Field(..., min_length=8, max_length=64)
    session_secret: str = Field(..., min_length=8, max_length=128)
    nickname: str = Field(..., min_length=3, max_length=24)


class LoginBody(BaseModel):
    nickname: str = Field(..., min_length=3, max_length=24)
    access_code: str = Field(..., min_length=6, max_length=48)


class LinkStartBody(BaseModel):
    account_id: str = Field(..., min_length=8, max_length=64)
    session_secret: str = Field(..., min_length=8, max_length=128)


class SessionEnsureBody(BaseModel):
    """Create or keep a web session without payment (for referral link / later TG link)."""

    account_id: Optional[str] = Field(default=None, max_length=64)
    session_secret: Optional[str] = Field(default=None, max_length=128)
    ref_code: Optional[str] = Field(default=None, max_length=32)


class WebDevicesAuth(BaseModel):
    account_id: str = Field(..., min_length=8, max_length=64)
    session_secret: str = Field(..., min_length=8, max_length=128)


class WebDevicesCreateBody(WebDevicesAuth):
    display_name: Optional[str] = Field(default=None, max_length=64)


class WebDevicesRenameBody(WebDevicesAuth):
    device_id: int = Field(..., ge=1)
    display_name: str = Field(..., min_length=1, max_length=64)


class WebDevicesRevokeBody(WebDevicesAuth):
    device_id: int = Field(..., ge=1)


class WebOrderCancelBody(WebDevicesAuth):
    order_id: int = Field(..., ge=1)


async def _web_account_or_401(
    conn,
    *,
    account_id: str,
    session_secret: str,
) -> Dict[str, Any]:
    aid = (account_id or "").strip()
    secret = (session_secret or "").strip()
    if not aid or not secret:
        raise HTTPException(status_code=401, detail={"code": "unauthorized"})
    if not await accounts_repo.verify_session_secret(conn, aid, secret):
        raise HTTPException(status_code=401, detail={"code": "unauthorized"})
    acc = await accounts_repo.get_account_by_id(conn, aid)
    if not acc:
        raise HTTPException(status_code=404, detail={"code": "account_missing"})
    return dict(acc)


async def _vpn_tid_for_account(settings: Settings, acc: Dict[str, Any]) -> int:
    """VPN subject used for devices API (synthetic or linked Telegram)."""
    vpn_subject = int(acc["vpn_subject_id"])
    real_tg = acc.get("telegram_user_id")
    vpath = settings.resolved_vpn_db_path()
    if vpath is not None:
        row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, vpn_subject)
        if row:
            return vpn_subject
        if real_tg:
            row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, int(real_tg))
            if row:
                return int(real_tg)
    return int(real_tg or vpn_subject)


def _public_devices_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """Never leak raw opaque_token to the browser."""
    devices_out = []
    for d in list(data.get("devices") or []):
        if not isinstance(d, dict):
            continue
        devices_out.append(
            {
                "id": int(d.get("id") or 0),
                "display_name": str(d.get("display_name") or "Устройство"),
                "device_kind": str(d.get("device_kind") or "unknown"),
                "status": str(d.get("status") or "awaiting"),
                "first_connected_at": d.get("first_connected_at"),
                "last_seen_at": d.get("last_seen_at"),
                "created_at": d.get("created_at"),
                "included_in_plan": bool(d.get("included_in_plan")),
                "subscription_url": d.get("subscription_url"),
            }
        )
    return {
        "ok": True,
        "used": int(data.get("used") or 0),
        "max": int(data.get("max") or 1),
        "can_add": bool(data.get("can_add")),
        "devices": devices_out,
    }


def _vpn_products(settings: Settings) -> List[Dict[str, Any]]:
    products = load_products(settings.products_path)
    out: List[Dict[str, Any]] = []
    for p in products:
        if str(getattr(p, "kind", "") or "").lower() != "vpn":
            continue
        days = int(getattr(p, "vpn_subscription_days", 0) or 0)
        rub = float(getattr(p, "price_rub", 0) or 0)
        if days <= 0 or rub <= 0:
            continue
        out.append(
            {
                "id": p.id,
                "title": p.title,
                "days": days,
                "price_rub": rub,
            }
        )
    out.sort(key=lambda x: int(x["days"]))
    return out


def _sub_url(settings: Settings, opaque: str) -> str:
    origin = (settings.vpn_public_https_origin or "https://aimonkeystars.ru").rstrip("/")
    return f"{origin}/sub/{opaque}"


def _web_origin(settings: Settings) -> str:
    return (settings.web_checkout_public_origin or "https://aimonkeystars.ru").rstrip("/")


def _support_url(settings: Settings) -> str:
    """Public support link for web SPA (no PII). Prefer SUPPORT_URL, else bot."""
    raw = (settings.support_url or "").strip()
    if raw:
        return raw
    un = (settings.support_username or "").strip().lstrip("@")
    if un:
        return f"https://t.me/{un}"
    bot = (settings.shop_bot_username or SHOP_BOT_USERNAME).lstrip("@")
    return f"https://t.me/{bot}" if bot else "https://t.me/AiMonkeyStars_bot"


@router.get("/web/health")
async def web_health(settings: Annotated[Settings, Depends(_settings_dep)]) -> dict[str, Any]:
    return {
        "status": "ok",
        "enabled": bool(settings.web_checkout_enabled),
        "product": VPN_PRODUCT_NAME,
        "support_url": _support_url(settings),
    }


@router.get("/web/products")
async def web_products(settings: Annotated[Settings, Depends(_settings_dep)]) -> dict[str, Any]:
    if not settings.web_checkout_enabled:
        raise HTTPException(status_code=503, detail={"code": "disabled"})
    return {
        "products": _vpn_products(settings),
        "brand": VPN_PRODUCT_NAME,
        "support_url": _support_url(settings),
    }


@router.post("/web/checkout")
async def web_checkout(
    body: CheckoutBody,
    request: Request,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> dict[str, Any]:
    if not settings.web_checkout_enabled:
        raise HTTPException(status_code=503, detail={"code": "disabled"})
    if not body.legal_accepted:
        raise HTTPException(status_code=400, detail={"code": "legal_required"})
    ip = _client_ip(request)
    if not _rate_ok(ip):
        raise HTTPException(status_code=429, detail={"code": "rate_limited"})
    if not lava_checkout_configured(settings):
        raise HTTPException(status_code=503, detail={"code": "payments_unavailable"})

    products = {p["id"]: p for p in _vpn_products(settings)}
    prod = products.get(body.product_id.strip())
    if not prod:
        raise HTTPException(status_code=400, detail={"code": "unknown_product"})

    from bot.services.web_nickname import normalize_nickname, validate_nickname

    nick_in = normalize_nickname(body.nickname or "")
    nick_err = validate_nickname(nick_in) if nick_in else "required"
    # Existing session may already have nickname — allow checkout without retyping.
    # We'll resolve below after loading/creating account.

    conn = await connect(settings.database_path)
    try:
        referrer_tid: int | None = None
        ref_code = (body.ref_code or "").strip()
        if ref_code:
            owner = await vpn_referral_repo.resolve_code_owner(conn, ref_code)
            if owner is not None:
                referrer_tid = int(owner)
            else:
                logger.info("web_checkout ref_code unresolved code=%s", ref_code[:32])
        else:
            # Cookie fallback if SPA forgot localStorage but browser kept aim_ref.
            cookie_ref = (request.cookies.get("aim_ref") or "").strip()
            if cookie_ref:
                owner = await vpn_referral_repo.resolve_code_owner(conn, cookie_ref)
                if owner is not None:
                    referrer_tid = int(owner)
                    logger.info("web_checkout ref from cookie aim_ref owner=%s", referrer_tid)

        acc = None
        if body.account_id and body.session_secret:
            if await accounts_repo.verify_session_secret(
                conn, body.account_id, body.session_secret
            ):
                acc = await accounts_repo.get_account_by_id(conn, body.account_id)

        session_secret = accounts_repo.new_access_token()
        access_code_once: str | None = None
        if acc is None:
            if nick_err:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "nickname_required" if nick_err == "required" else nick_err,
                        "message": nick_err,
                    },
                )
            acc = await accounts_repo.create_web_account(
                conn, referrer_telegram_id=referrer_tid
            )
            await accounts_repo.set_session_secret(conn, str(acc["account_id"]), session_secret)
            try:
                nick_saved, access_code_once = await accounts_repo.set_nickname_with_access_code(
                    conn, account_id=str(acc["account_id"]), nickname=nick_in
                )
            except ValueError as e:
                raise HTTPException(
                    status_code=400, detail={"code": str(e) or "nickname_invalid"}
                ) from e
            acc = await accounts_repo.get_account_by_id(conn, str(acc["account_id"])) or acc
        else:
            # Refresh session secret for cookie continuity
            await accounts_repo.set_session_secret(conn, str(acc["account_id"]), session_secret)
            if referrer_tid and not acc.get("referrer_telegram_id"):
                await conn.execute(
                    "UPDATE accounts SET referrer_telegram_id = ? WHERE account_id = ?",
                    (referrer_tid, acc["account_id"]),
                )
                await conn.commit()
            existing_nick = (acc.get("nickname") or "").strip()
            if not existing_nick:
                if nick_err:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "code": "nickname_required" if nick_err == "required" else nick_err,
                            "message": nick_err,
                        },
                    )
                try:
                    _, access_code_once = await accounts_repo.set_nickname_with_access_code(
                        conn, account_id=str(acc["account_id"]), nickname=nick_in
                    )
                except ValueError as e:
                    raise HTTPException(
                        status_code=400, detail={"code": str(e) or "nickname_invalid"}
                    ) from e
                acc = await accounts_repo.get_account_by_id(conn, str(acc["account_id"])) or acc
            nick_saved = (acc.get("nickname") or "").strip()

        # Prefer account-level referrer
        ref_for_order = referrer_tid or (
            int(acc["referrer_telegram_id"]) if acc.get("referrer_telegram_id") else None
        )
        buyer_nick = (acc.get("nickname") or nick_in or "").strip() or None

        order_id = await orders_repo.create_web_order(
            conn,
            account_id=str(acc["account_id"]),
            vpn_subject_id=int(acc["vpn_subject_id"]),
            product_id=str(prod["id"]),
            product_title=str(prod["title"]),
            rub_after=float(prod["price_rub"]),
            referrer_id=ref_for_order,
            vpn_subscription_days=int(prod["days"]),
            buyer_nickname=buyer_nick,
        )
        # Один активный счёт на web-аккаунт: старые pending закрываем.
        if bool(getattr(settings, "auto_expire_other_pending_payment_orders", True)):
            try:
                await orders_repo.expire_other_pending_payment_orders_for_account(
                    conn,
                    account_id=str(acc["account_id"]),
                    keep_order_id=int(order_id),
                )
            except Exception:
                logger.exception("web_checkout expire_other_pending order=%s", order_id)

        access = await accounts_repo.issue_order_access_token(
            conn, order_id=order_id, account_id=str(acc["account_id"])
        )
        success_path = f"{_web_origin(settings)}/o/{access}"

        lava = await create_invoice_payment_meta(
            settings,
            order_id=order_id,
            sum_rub=float(prod["price_rub"]),
            comment=f"{VPN_PRODUCT_NAME} {prod['days']}d #{order_id}",
            include_service=["sbp", "card"],
            success_url=success_path,
        )
        if not lava.pay_url:
            raise HTTPException(
                status_code=502,
                detail={"code": "invoice_failed", "message": lava.error or "lava"},
            )
        await orders_repo.set_invoice_provider_metadata(
            conn,
            order_id=order_id,
            provider="lava",
            external_id=lava.external_id or "",
            pay_url=lava.pay_url,
            lava_attempt=int(lava.lava_attempt or 1),
        )
        return {
            "order_id": order_id,
            "account_id": acc["account_id"],
            "session_secret": session_secret,
            "pay_url": lava.pay_url,
            "qr_url": lava.qr_url,
            "access_token": access,
            "success_url": success_path,
            "amount_rub": float(prod["price_rub"]),
            "nickname": buyer_nick,
            "access_code": access_code_once,
        }
    finally:
        await conn.close()


@router.get("/web/order/{access_token}")
async def web_order_status(
    access_token: str,
    settings: Annotated[Settings, Depends(_settings_dep)],
    account_id: Optional[str] = None,
    session_secret: Optional[str] = None,
    aim_account: Annotated[Optional[str], Cookie(alias="aim_account")] = None,
    aim_session: Annotated[Optional[str], Cookie(alias="aim_session")] = None,
) -> dict[str, Any]:
    if not settings.web_checkout_enabled:
        raise HTTPException(status_code=503, detail={"code": "disabled"})
    raw = (access_token or "").strip()
    if len(raw) < 16:
        raise HTTPException(status_code=400, detail={"code": "bad_token"})
    conn = await connect(settings.database_path)
    try:
        tok = await accounts_repo.resolve_order_access_token(conn, raw)
        if not tok:
            raise HTTPException(status_code=404, detail={"code": "not_found"})
        order = await orders_repo.get_order(conn, int(tok["order_id"]))
        if order is None:
            raise HTTPException(status_code=404, detail={"code": "order_missing"})
        account_id_tok = str(tok["account_id"])
        acc = await accounts_repo.get_account_by_id(conn, account_id_tok)
        vpn_subject = int(acc["vpn_subject_id"]) if acc else int(order["user_id"])
        sub_url = None
        paid_until = None
        vpn_status = None
        vpath = settings.resolved_vpn_db_path()
        if vpath is not None:
            row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, vpn_subject)
            if row:
                opaque = (row.get("opaque_token") or "").strip()
                paid_until = row.get("paid_until")
                vpn_status = row.get("status")
                # whapp-10 / wux-05: не отдавать /sub/, пока peer-up не сделал vpn_active.
                if opaque and str(vpn_status or "") == "vpn_active":
                    sub_url = _sub_url(settings, opaque)
        tg_linked = bool(acc and acc.get("telegram_user_id"))
        bot = (settings.shop_bot_username or SHOP_BOT_USERNAME).lstrip("@")
        pay_url = None
        try:
            raw_pay = order["invoice_last_pay_url"] if "invoice_last_pay_url" in order.keys() else None
            pay_url = (str(raw_pay).strip() if raw_pay else None) or None
        except Exception:
            pay_url = None
        status_l = str(order["status"] or "").lower()
        pending = status_l in {
            "pending_payment",
            "pending",
            "created",
            "awaiting_payment",
        }
        paidish = status_l in {"paid", "completed"} or bool(sub_url)
        vpn_ready = bool(sub_url) and str(vpn_status or "") == "vpn_active"
        vpn_preparing = bool(paidish and not pending and not vpn_ready)

        # SEC: reveal /sub with session of same account, or grace window after token issue
        # (Lava redirect may not send cookies — grace keeps payment UX working).
        aid = (account_id or aim_account or "").strip()
        secret = (session_secret or aim_session or "").strip()
        session_ok = False
        if aid and secret and aid == account_id_tok:
            session_ok = await accounts_repo.verify_session_secret(conn, aid, secret)
        age_h = accounts_repo.order_access_token_age_hours(tok)
        grace_ok = age_h is not None and age_h <= 48.0
        subscription_locked = False
        if sub_url and paidish and not pending and not (session_ok or grace_ok):
            subscription_locked = True
            sub_url = None
            vpn_ready = False

        return {
            "order_id": int(order["id"]),
            "status": str(order["status"]),
            "product_id": str(order["product_id"]),
            "product_title": str(order["product_title"]),
            "amount_rub": float(order["rub_after_discounts"] or 0),
            "account_id": account_id_tok,
            "subscription_url": sub_url,
            "subscription_locked": subscription_locked,
            "paid_until": paid_until,
            "vpn_status": vpn_status,
            "vpn_ready": vpn_ready,
            "vpn_preparing": vpn_preparing and not subscription_locked,
            "telegram_linked": tg_linked,
            "bot_username": bot,
            "brand": VPN_PRODUCT_NAME,
            "pay_url": pay_url if pending else None,
            "support_url": _support_url(settings),
            "buyer_nickname": (
                (order["buyer_nickname"] if "buyer_nickname" in order.keys() else None)
                or (acc.get("nickname") if acc else None)
            ),
            "nickname": (acc.get("nickname") if acc else None),
        }
    finally:
        await conn.close()


@router.post("/web/link/start")
async def web_link_start(
    body: LinkStartBody,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> dict[str, Any]:
    if not settings.web_checkout_enabled:
        raise HTTPException(status_code=503, detail={"code": "disabled"})
    conn = await connect(settings.database_path)
    try:
        if not await accounts_repo.verify_session_secret(
            conn, body.account_id, body.session_secret
        ):
            raise HTTPException(status_code=401, detail={"code": "unauthorized"})
        acc = await accounts_repo.get_account_by_id(conn, body.account_id)
        if not acc:
            raise HTTPException(status_code=404, detail={"code": "account_missing"})
        if acc.get("telegram_user_id"):
            return {
                "already_linked": True,
                "telegram_user_id": int(acc["telegram_user_id"]),
            }
        code = await accounts_repo.issue_link_token(conn, account_id=body.account_id)
        bot = (settings.shop_bot_username or SHOP_BOT_USERNAME).lstrip("@")
        return {
            "already_linked": False,
            "deep_link": f"https://t.me/{bot}?start=link_{code}",
            "code": code,
            "expires_minutes": 30,
        }
    finally:
        await conn.close()


@router.post("/web/session/ensure")
async def web_session_ensure(
    request: Request,
    body: SessionEnsureBody,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> dict[str, Any]:
    """
    Guest can get a site session + referral /r/CODE without buying VPN.
    Optional: attach aim_ref / body.ref_code as first referrer (first-write-wins).
    """
    if not settings.web_checkout_enabled:
        raise HTTPException(status_code=503, detail={"code": "disabled"})
    conn = await connect(settings.database_path)
    try:
        aid = (body.account_id or "").strip()
        secret_in = (body.session_secret or "").strip()
        acc = None
        session_secret = secret_in
        created = False
        if aid and secret_in and await accounts_repo.verify_session_secret(conn, aid, secret_in):
            acc = await accounts_repo.get_account_by_id(conn, aid)

        referrer_tid: int | None = None
        ref_code = (body.ref_code or "").strip()
        if not ref_code:
            ref_code = (request.cookies.get("aim_ref") or "").strip()
        if ref_code:
            owner = await vpn_referral_repo.resolve_code_owner(conn, ref_code)
            if owner:
                referrer_tid = int(owner)

        if acc is None:
            acc = await accounts_repo.create_web_account(
                conn, referrer_telegram_id=referrer_tid
            )
            session_secret = accounts_repo.new_access_token()
            await accounts_repo.set_session_secret(
                conn, str(acc["account_id"]), session_secret
            )
            created = True
        else:
            if referrer_tid and not acc.get("referrer_telegram_id"):
                await conn.execute(
                    "UPDATE accounts SET referrer_telegram_id = ? WHERE account_id = ?",
                    (referrer_tid, acc["account_id"]),
                )
                await conn.commit()

        owner_tg = acc.get("telegram_user_id")
        owner_key = int(owner_tg) if owner_tg else int(acc["vpn_subject_id"])
        code = await vpn_referral_repo.ensure_my_vpn_referral_code(conn, owner_key)
        return {
            "account_id": str(acc["account_id"]),
            "session_secret": session_secret,
            "created": created,
            "telegram_linked": bool(owner_tg),
            "referral": {
                "code": code,
                "url": f"{_web_origin(settings)}/r/{code}",
            },
        }
    finally:
        await conn.close()


@router.post("/web/nickname")
async def web_set_nickname(
    body: NicknameBody,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> dict[str, Any]:
    if not settings.web_checkout_enabled:
        raise HTTPException(status_code=503, detail={"code": "disabled"})
    conn = await connect(settings.database_path)
    try:
        if not await accounts_repo.verify_session_secret(
            conn, body.account_id, body.session_secret
        ):
            raise HTTPException(status_code=401, detail={"code": "unauthorized"})
        try:
            nick, code_once = await accounts_repo.set_nickname_with_access_code(
                conn, account_id=body.account_id, nickname=body.nickname
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail={"code": str(e)}) from e
        return {
            "nickname": nick,
            "access_code": code_once,
            "locked": code_once is None,
        }
    finally:
        await conn.close()


@router.post("/web/login")
async def web_login_nickname(
    body: LoginBody,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> dict[str, Any]:
    if not settings.web_checkout_enabled:
        raise HTTPException(status_code=503, detail={"code": "disabled"})
    conn = await connect(settings.database_path)
    try:
        try:
            acc, secret = await accounts_repo.login_with_nickname_code(
                conn, nickname=body.nickname, access_code=body.access_code
            )
        except ValueError:
            raise HTTPException(
                status_code=401, detail={"code": "invalid_credentials"}
            ) from None
        return {
            "account_id": acc["account_id"],
            "session_secret": secret,
            "nickname": acc.get("nickname"),
        }
    finally:
        await conn.close()


@router.get("/web/me")
async def web_me(
    settings: Annotated[Settings, Depends(_settings_dep)],
    account_id: Optional[str] = None,
    session_secret: Optional[str] = None,
    aim_account: Annotated[Optional[str], Cookie(alias="aim_account")] = None,
    aim_session: Annotated[Optional[str], Cookie(alias="aim_session")] = None,
) -> Dict[str, Any]:
    if not settings.web_checkout_enabled:
        raise HTTPException(status_code=503, detail={"code": "disabled"})
    aid = (account_id or aim_account or "").strip()
    secret = (session_secret or aim_session or "").strip()
    if not aid or not secret:
        raise HTTPException(status_code=401, detail={"code": "unauthorized"})
    conn = await connect(settings.database_path)
    try:
        if not await accounts_repo.verify_session_secret(conn, aid, secret):
            raise HTTPException(status_code=401, detail={"code": "unauthorized"})
        acc = await accounts_repo.get_account_by_id(conn, aid)
        if not acc:
            raise HTTPException(status_code=404, detail={"code": "account_missing"})
        orders = await orders_repo.list_orders_for_account(conn, aid, limit=20)
        vpn_subject = int(acc["vpn_subject_id"])
        sub_url = paid_until = vpn_status = None
        vpath = settings.resolved_vpn_db_path()
        if vpath is not None:
            row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, vpn_subject)
            real_tg = acc.get("telegram_user_id")
            if row is None and real_tg:
                row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(
                    vpath, int(real_tg)
                )
            if row:
                opaque = (row.get("opaque_token") or "").strip()
                paid_until = row.get("paid_until")
                vpn_status = row.get("status")
                if opaque and str(vpn_status or "") == "vpn_active":
                    sub_url = _sub_url(settings, opaque)

        ref_code = None
        ref_stats = {"invited": 0, "with_purchase": 0, "bonus_days": 0}
        qualified_vpn = 0
        owner_tg = acc.get("telegram_user_id")
        owner_for_level = int(owner_tg) if owner_tg else int(vpn_subject)
        if owner_tg:
            try:
                ref_code = await vpn_referral_repo.ensure_my_vpn_referral_code(conn, int(owner_tg))
                ref_stats = await vpn_referral_repo.user_vpn_referral_stats(conn, int(owner_tg))
                owner_for_level = int(owner_tg)
            except Exception:
                logger.exception("web_me referral")
        else:
            # Web-only: code keyed by vpn_subject placeholder user
            try:
                ref_code = await vpn_referral_repo.ensure_my_vpn_referral_code(conn, vpn_subject)
                ref_stats = await vpn_referral_repo.user_vpn_referral_stats(conn, vpn_subject)
            except Exception:
                pass
        try:
            from bot.services.referral_partner import (
                count_qualified_vpn_referrals,
                level_for_qualified_count,
                progress_to_next_level,
            )

            qualified_vpn = await count_qualified_vpn_referrals(conn, owner_for_level)
            lvl = level_for_qualified_count(qualified_vpn)
            cur_q, need_q = progress_to_next_level(qualified_vpn)
            level_payload = {
                "id": lvl["id"],
                "label": lvl["label"],
                "vpn_first_percent": float(lvl["vpn_first_percent"]),
                "stars_premium_percent": float(lvl["stars_premium_percent"]),
                "qualified_vpn": int(qualified_vpn),
                "progress_current": int(cur_q),
                "progress_need": int(need_q) if need_q is not None else None,
            }
        except Exception:
            logger.exception("web_me level")
            level_payload = {
                "id": "start",
                "label": "Старт",
                "vpn_first_percent": 15.0,
                "stars_premium_percent": 1.0,
                "qualified_vpn": 0,
                "progress_current": 0,
                "progress_need": 5,
            }

        ref_balance = 0.0
        try:
            from bot.services import balance_repo

            bal_uid = owner_for_level
            ref_balance = float(await balance_repo.get_ref_balance(conn, bal_uid) or 0)
        except Exception:
            ref_balance = 0.0

        return {
            "account_id": aid,
            "nickname": (acc.get("nickname") or None),
            "has_access_code": bool(acc.get("access_code_hash")),
            "telegram_linked": bool(acc.get("telegram_user_id")),
            "telegram_user_id": acc.get("telegram_user_id"),
            "subscription_url": sub_url,
            "paid_until": paid_until,
            "vpn_status": vpn_status,
            "orders": [
                {
                    "id": int(o["id"]),
                    "status": str(o["status"]),
                    "product_title": str(o["product_title"]),
                    "amount_rub": float(o["rub_after_discounts"] or 0),
                    "source": str(o["source"] or ""),
                    "buyer_nickname": (
                        str(o["buyer_nickname"])
                        if "buyer_nickname" in o.keys() and o["buyer_nickname"]
                        else None
                    ),
                    "created_at": str(o["created_at"] if "created_at" in o.keys() else ""),
                }
                for o in orders
            ],
            "referral": {
                "code": ref_code,
                "url": f"{_web_origin(settings)}/r/{ref_code}" if ref_code else None,
                "level": level_payload,
                "ref_balance_rub": round(ref_balance, 2),
                "stats": {
                    "invited": int(
                        ref_stats.get("vpn_referral_invited")
                        or ref_stats.get("invited")
                        or 0
                    ),
                    "with_purchase": int(ref_stats.get("vpn_referral_buyers") or 0),
                    "bonus_days": int(ref_stats.get("vpn_referral_days_earned") or 0),
                    "qualified_vpn": int(qualified_vpn),
                },
            },
            "brand": VPN_PRODUCT_NAME,
            "support_url": _support_url(settings),
        }
    finally:
        await conn.close()


@router.post("/web/orders/cancel")
async def web_order_cancel(
    body: WebOrderCancelBody,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> Dict[str, Any]:
    """Отменить неоплаченный счёт (pending_payment → expired)."""
    if not settings.web_checkout_enabled:
        raise HTTPException(status_code=503, detail={"code": "disabled"})
    conn = await connect(settings.database_path)
    try:
        await _web_account_or_401(
            conn, account_id=body.account_id, session_secret=body.session_secret
        )
        code = await orders_repo.cancel_account_pending_order(
            conn,
            order_id=int(body.order_id),
            account_id=body.account_id,
        )
        if code == "not_found":
            raise HTTPException(status_code=404, detail={"code": "order_not_found"})
        if code == "wrong_account":
            raise HTTPException(status_code=403, detail={"code": "forbidden"})
        if code == "wrong_status":
            raise HTTPException(status_code=409, detail={"code": "not_pending"})
        return {"ok": True, "order_id": int(body.order_id), "status": "expired"}
    finally:
        await conn.close()


@router.get("/web/devices")
async def web_devices_list_get(
    settings: Annotated[Settings, Depends(_settings_dep)],
    account_id: Optional[str] = None,
    session_secret: Optional[str] = None,
    aim_account: Annotated[Optional[str], Cookie(alias="aim_account")] = None,
    aim_session: Annotated[Optional[str], Cookie(alias="aim_session")] = None,
) -> Dict[str, Any]:
    if not settings.web_checkout_enabled:
        raise HTTPException(status_code=503, detail={"code": "disabled"})
    aid = (account_id or aim_account or "").strip()
    secret = (session_secret or aim_session or "").strip()
    conn = await connect(settings.database_path)
    try:
        acc = await _web_account_or_401(conn, account_id=aid, session_secret=secret)
        tid = await _vpn_tid_for_account(settings, acc)
        ok, data = await vpn_api_client.post_devices_list(settings, telegram_user_id=tid)
        if not ok or not isinstance(data, dict):
            raise HTTPException(
                status_code=502,
                detail={"code": "vpn_devices_unavailable", "message": str(data)[:300]},
            )
        return _public_devices_payload(data)
    finally:
        await conn.close()


@router.post("/web/devices/create")
async def web_devices_create(
    body: WebDevicesCreateBody,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> Dict[str, Any]:
    if not settings.web_checkout_enabled:
        raise HTTPException(status_code=503, detail={"code": "disabled"})
    conn = await connect(settings.database_path)
    try:
        acc = await _web_account_or_401(
            conn, account_id=body.account_id, session_secret=body.session_secret
        )
        tid = await _vpn_tid_for_account(settings, acc)
        ok, data = await vpn_api_client.post_devices_create(
            settings,
            telegram_user_id=tid,
            display_name=body.display_name,
            idempotency_key=f"web-dev-add-{body.account_id}-{int(time.time())}",
        )
        if not ok:
            detail = str(data)
            if "device_limit_reached" in detail:
                raise HTTPException(status_code=409, detail={"code": "device_limit_reached"})
            raise HTTPException(
                status_code=502,
                detail={"code": "vpn_devices_create_failed", "message": detail[:300]},
            )
        assert isinstance(data, dict)
        device = data.get("device") if isinstance(data.get("device"), dict) else {}
        return {
            "ok": True,
            "used": int(data.get("used") or 0),
            "max": int(data.get("max") or 1),
            "can_add": bool(data.get("can_add")),
            "device": {
                "id": int(device.get("id") or 0),
                "display_name": str(device.get("display_name") or "Устройство"),
                "device_kind": str(device.get("device_kind") or "unknown"),
                "status": str(device.get("status") or "awaiting"),
                "subscription_url": device.get("subscription_url"),
            },
        }
    finally:
        await conn.close()


@router.post("/web/devices/rename")
async def web_devices_rename(
    body: WebDevicesRenameBody,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> Dict[str, Any]:
    if not settings.web_checkout_enabled:
        raise HTTPException(status_code=503, detail={"code": "disabled"})
    conn = await connect(settings.database_path)
    try:
        acc = await _web_account_or_401(
            conn, account_id=body.account_id, session_secret=body.session_secret
        )
        tid = await _vpn_tid_for_account(settings, acc)
        ok, msg = await vpn_api_client.post_devices_rename(
            settings,
            telegram_user_id=tid,
            device_id=int(body.device_id),
            display_name=body.display_name,
        )
        if not ok:
            raise HTTPException(
                status_code=502,
                detail={"code": "vpn_devices_rename_failed", "message": str(msg)[:300]},
            )
        return {"ok": True, "device_id": int(body.device_id), "display_name": body.display_name.strip()}
    finally:
        await conn.close()


@router.post("/web/devices/revoke")
async def web_devices_revoke(
    body: WebDevicesRevokeBody,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> Dict[str, Any]:
    if not settings.web_checkout_enabled:
        raise HTTPException(status_code=503, detail={"code": "disabled"})
    conn = await connect(settings.database_path)
    try:
        acc = await _web_account_or_401(
            conn, account_id=body.account_id, session_secret=body.session_secret
        )
        tid = await _vpn_tid_for_account(settings, acc)
        ok, data = await vpn_api_client.post_devices_revoke(
            settings,
            telegram_user_id=tid,
            device_id=int(body.device_id),
            idempotency_key=f"web-dev-rev-{body.account_id}-{body.device_id}-{int(time.time())}",
        )
        if not ok:
            raise HTTPException(
                status_code=502,
                detail={"code": "vpn_devices_revoke_failed", "message": str(data)[:300]},
            )
        assert isinstance(data, dict)
        return {
            "ok": True,
            "device_id": int(body.device_id),
            "used": int(data.get("used") or 0),
            "max": int(data.get("max") or 1),
            "can_add": bool(data.get("can_add")),
        }
    finally:
        await conn.close()


def _spa_html() -> HTMLResponse:
    index = _STATIC_DIR / "index.html"
    if not index.exists():
        return HTMLResponse("<h1>Web checkout SPA missing</h1>", status_code=500)
    # Always fresh HTML — иначе пользователи видят старый текст «Бонусы» из кэша.
    return HTMLResponse(
        index.read_text(encoding="utf-8"),
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
        },
    )


@router.get("/web/app", response_class=HTMLResponse)
@router.get("/web/", response_class=HTMLResponse)
@router.get("/web", response_class=HTMLResponse)
async def web_spa_index(settings: Annotated[Settings, Depends(_settings_dep)]) -> HTMLResponse:
    return _spa_html()


@router.get("/web/assets/{name}")
async def web_assets(name: str) -> FileResponse:
    safe = Path(name).name
    path = _STATIC_DIR / safe
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(path)


_ALLOWED_STORM_MEDIA = frozenset(
    {
        "hero-storm.webm",
        "hero-storm.mp4",
        "hero-storm-poster.jpg",
    }
)


@public_router.get("/media/{name}")
async def public_storm_media(name: str) -> FileResponse:
    """Aladdin-style storm background assets for checkout SPA."""
    safe = Path(name).name
    if safe not in _ALLOWED_STORM_MEDIA:
        raise HTTPException(status_code=404)
    path = _STATIC_DIR / "media" / safe
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(
        path,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@public_router.get("/")
@public_router.get("/app")
@public_router.get("/devices")
async def public_spa_root() -> HTMLResponse:
    return _spa_html()


@public_router.get("/o/{access_token}")
async def public_order_page(access_token: str) -> HTMLResponse:
    """Success / status page — SPA reads token from path."""
    _ = access_token
    return _spa_html()
