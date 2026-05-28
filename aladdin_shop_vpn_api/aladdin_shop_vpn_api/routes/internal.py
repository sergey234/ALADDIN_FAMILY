from __future__ import annotations

import json
import secrets
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated, Optional

import aiosqlite
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from pydantic import ValidationError

from aladdin_shop_vpn_api import egress_nodes_util, hmac_auth, locations_util
from aladdin_shop_vpn_api.deps import get_db, get_settings
from aladdin_shop_vpn_api.schemas import (
    AddSubscriptionDaysBody,
    ExtendBody,
    ProvisionBody,
    RevokeBody,
    LocationSelectBody,
    OvpnConfBody,
    WgConfBody,
)
from aladdin_shop_vpn_api.settings import Settings

router = APIRouter(prefix="/internal/v1", tags=["internal"])


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _add_days_to_subscription(*, current_paid_until: str | None, days: int) -> str:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    cur_end = now
    if current_paid_until:
        raw = str(current_paid_until).strip().replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(raw)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            cur_end = parsed
        except ValueError:
            cur_end = now
    base = max(now, cur_end)
    new_end = base + timedelta(days=int(days))
    return new_end.isoformat()


def _verify_hmac_only(request: Request, settings: Settings, body: bytes) -> None:
    ts = request.headers.get("x-timestamp") or request.headers.get("X-Timestamp") or ""
    nonce = request.headers.get("x-nonce") or request.headers.get("X-Nonce") or ""
    sig = request.headers.get("x-signature") or request.headers.get("X-Signature") or ""
    path = request.url.path
    ok, err = hmac_auth.verify_signature(
        settings.vpn_api_hmac_secret,
        method=request.method,
        path=path,
        timestamp=ts,
        nonce=nonce,
        body=body,
        signature_hex=sig,
    )
    if not ok:
        raise HTTPException(status_code=401, detail=err)


async def _idempotency_response(
    db: aiosqlite.Connection,
    *,
    idempotency_key: Optional[str],
) -> Optional[Response]:
    if not (idempotency_key or "").strip():
        raise HTTPException(status_code=400, detail="Idempotency-Key header required")
    key = idempotency_key.strip()
    hit = await hmac_auth.idempotency_lookup(db, key)
    if hit is None:
        return None
    status, body = hit
    return Response(content=body, status_code=status, media_type="application/json")


async def _nonce_guard(db: aiosqlite.Connection, request: Request) -> None:
    nonce = request.headers.get("x-nonce") or request.headers.get("X-Nonce") or ""
    if not await hmac_auth.consume_nonce(db, nonce=nonce):
        raise HTTPException(status_code=401, detail="nonce replay")


async def _remember_idempotent(
    db: aiosqlite.Connection,
    *,
    key: str,
    route: str,
    response_status: int,
    response_body: str,
) -> None:
    await hmac_auth.idempotency_store(
        db,
        key=key,
        route=route,
        response_status=response_status,
        response_body=response_body,
    )


@router.post("/provision")
async def provision(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[aiosqlite.Connection, Depends(get_db)],
    idempotency_key: Annotated[Optional[str], Header(alias="Idempotency-Key")] = None,
) -> Response:
    body = await request.body()
    _verify_hmac_only(request, settings, body)

    cached = await _idempotency_response(db, idempotency_key=idempotency_key)
    if cached is not None:
        return cached

    await _nonce_guard(db, request)

    try:
        parsed = ProvisionBody.model_validate_json(body)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=json.loads(e.json())) from e

    now = _utc_now_iso()
    opaque = secrets.token_urlsafe(24)

    cur = await db.execute(
        "SELECT id, opaque_token FROM vpn_accounts WHERE telegram_user_id = ?",
        (parsed.telegram_user_id,),
    )
    row = await cur.fetchone()
    if row is None:
        await db.execute(
            """
            INSERT INTO vpn_accounts (
                telegram_user_id, status, paid_until, opaque_token, created_at, updated_at
            ) VALUES (?, 'vpn_provisioning', ?, ?, ?, ?)
            """,
            (parsed.telegram_user_id, parsed.paid_until, opaque, now, now),
        )
        cur2 = await db.execute("SELECT last_insert_rowid()", ())
        account_id = int((await cur2.fetchone())[0])
    else:
        account_id = int(row["id"])
        await db.execute(
            """
            UPDATE vpn_accounts
            SET paid_until = ?, status = 'vpn_provisioning', updated_at = ?, last_error = NULL
            WHERE id = ?
            """,
            (parsed.paid_until, now, account_id),
        )
        if not row["opaque_token"]:
            await db.execute(
                "UPDATE vpn_accounts SET opaque_token = ? WHERE id = ?",
                (opaque, account_id),
            )

    payload = json.dumps(
        {
            "telegram_user_id": parsed.telegram_user_id,
            "order_id": parsed.order_id,
            "paid_until": parsed.paid_until,
            "account_id": account_id,
        }
    )
    await db.execute(
        """
        INSERT INTO jobs (job_type, payload_json, status, idempotency_key, next_run_at, created_at, updated_at)
        VALUES ('provision', ?, 'pending', ?, ?, ?, ?)
        """,
        (payload, idempotency_key.strip(), now, now, now),
    )
    await db.commit()

    cur3 = await db.execute("SELECT last_insert_rowid()", ())
    job_id = int((await cur3.fetchone())[0])
    out = json.dumps({"job_id": job_id, "account_id": account_id, "status": "enqueued"})
    await _remember_idempotent(
        db,
        key=idempotency_key.strip(),
        route="provision",
        response_status=202,
        response_body=out,
    )
    return Response(content=out, status_code=202, media_type="application/json")


@router.post("/extend")
async def extend(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[aiosqlite.Connection, Depends(get_db)],
    idempotency_key: Annotated[Optional[str], Header(alias="Idempotency-Key")] = None,
) -> Response:
    body = await request.body()
    _verify_hmac_only(request, settings, body)

    cached = await _idempotency_response(db, idempotency_key=idempotency_key)
    if cached is not None:
        return cached

    await _nonce_guard(db, request)

    try:
        parsed = ExtendBody.model_validate_json(body)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=json.loads(e.json())) from e

    now = _utc_now_iso()
    payload = json.dumps(
        {
            "telegram_user_id": parsed.telegram_user_id,
            "order_id": parsed.order_id,
            "paid_until": parsed.paid_until,
        }
    )
    await db.execute(
        """
        INSERT INTO jobs (job_type, payload_json, status, idempotency_key, next_run_at, created_at, updated_at)
        VALUES ('extend', ?, 'pending', ?, ?, ?, ?)
        """,
        (payload, idempotency_key.strip(), now, now, now),
    )
    await db.commit()
    cur = await db.execute("SELECT last_insert_rowid()", ())
    job_id = int((await cur.fetchone())[0])
    out = json.dumps({"job_id": job_id, "status": "enqueued"})
    await _remember_idempotent(
        db,
        key=idempotency_key.strip(),
        route="extend",
        response_status=202,
        response_body=out,
    )
    return Response(content=out, status_code=202, media_type="application/json")


@router.post("/add-subscription-days")
async def add_subscription_days(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[aiosqlite.Connection, Depends(get_db)],
    idempotency_key: Annotated[Optional[str], Header(alias="Idempotency-Key")] = None,
) -> Response:
    """Нарастить paid_until на N дней; при отсутствии аккаунта создаёт строку (как бонус до первого provision)."""
    body = await request.body()
    _verify_hmac_only(request, settings, body)

    cached = await _idempotency_response(db, idempotency_key=idempotency_key)
    if cached is not None:
        return cached

    await _nonce_guard(db, request)

    try:
        parsed = AddSubscriptionDaysBody.model_validate_json(body)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=json.loads(e.json())) from e

    now = _utc_now_iso()
    cur = await db.execute(
        "SELECT id, paid_until, opaque_token FROM vpn_accounts WHERE telegram_user_id = ?",
        (parsed.telegram_user_id,),
    )
    row = await cur.fetchone()
    new_until = _add_days_to_subscription(current_paid_until=str(row["paid_until"]) if row else None, days=parsed.days)
    opaque = secrets.token_urlsafe(24)
    if row is None:
        await db.execute(
            """
            INSERT INTO vpn_accounts (
                telegram_user_id, status, paid_until, opaque_token, created_at, updated_at
            ) VALUES (?, 'vpn_active', ?, ?, ?, ?)
            """,
            (parsed.telegram_user_id, new_until, opaque, now, now),
        )
    else:
        acc_id = int(row["id"])
        fix_opaque = (str(row["opaque_token"] or "").strip()) or opaque
        await db.execute(
            """
            UPDATE vpn_accounts
            SET paid_until = ?, status = 'vpn_active', updated_at = ?, last_error = NULL,
                opaque_token = ?
            WHERE id = ?
            """,
            (new_until, now, fix_opaque, acc_id),
        )

    payload = json.dumps(
        {
            "telegram_user_id": parsed.telegram_user_id,
            "order_id": parsed.order_id,
            "paid_until": new_until,
            "reason": parsed.reason,
        }
    )
    await db.execute(
        """
        INSERT INTO jobs (job_type, payload_json, status, idempotency_key, next_run_at, created_at, updated_at)
        VALUES ('extend', ?, 'pending', ?, ?, ?, ?)
        """,
        (payload, f"add-days:{idempotency_key.strip()}", now, now, now),
    )
    await db.commit()
    cur2 = await db.execute("SELECT last_insert_rowid()", ())
    job_id = int((await cur2.fetchone())[0])
    out = json.dumps(
        {
            "job_id": job_id,
            "status": "enqueued",
            "paid_until": new_until,
            "telegram_user_id": parsed.telegram_user_id,
        }
    )
    await _remember_idempotent(
        db,
        key=idempotency_key.strip(),
        route="add-subscription-days",
        response_status=202,
        response_body=out,
    )
    return Response(content=out, status_code=202, media_type="application/json")


@router.post("/revoke")
async def revoke(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[aiosqlite.Connection, Depends(get_db)],
    idempotency_key: Annotated[Optional[str], Header(alias="Idempotency-Key")] = None,
) -> Response:
    body = await request.body()
    _verify_hmac_only(request, settings, body)

    cached = await _idempotency_response(db, idempotency_key=idempotency_key)
    if cached is not None:
        return cached

    await _nonce_guard(db, request)

    try:
        parsed = RevokeBody.model_validate_json(body)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=json.loads(e.json())) from e

    now = _utc_now_iso()
    payload = json.dumps({"telegram_user_id": parsed.telegram_user_id, "reason": parsed.reason})
    await db.execute(
        """
        INSERT INTO jobs (job_type, payload_json, status, idempotency_key, next_run_at, created_at, updated_at)
        VALUES ('revoke', ?, 'pending', ?, ?, ?, ?)
        """,
        (payload, idempotency_key.strip(), now, now, now),
    )
    await db.commit()
    cur = await db.execute("SELECT last_insert_rowid()", ())
    job_id = int((await cur.fetchone())[0])
    out = json.dumps({"job_id": job_id, "status": "enqueued"})
    await _remember_idempotent(
        db,
        key=idempotency_key.strip(),
        route="revoke",
        response_status=202,
        response_body=out,
    )
    return Response(content=out, status_code=202, media_type="application/json")


@router.post("/wg/conf")
async def wg_conf(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[aiosqlite.Connection, Depends(get_db)],
) -> Response:
    """Клиентский WireGuard `.conf` (HMAC + nonce). Idempotency-Key не требуется."""
    body = await request.body()
    _verify_hmac_only(request, settings, body)
    await _nonce_guard(db, request)

    try:
        parsed = WgConfBody.model_validate_json(body)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=json.loads(e.json())) from e

    tid = int(parsed.telegram_user_id)
    cur = await db.execute(
        """
        SELECT status, paid_until, wg_client_tunnel_ip, preferred_location_slug
        FROM vpn_accounts WHERE telegram_user_id = ?
        """,
        (tid,),
    )
    row = await cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="unknown telegram_user_id")
    st = str(row["status"] or "")
    if st != "vpn_active":
        raise HTTPException(status_code=403, detail=f"vpn not active ({st})")
    raw_pu = row["paid_until"]
    if raw_pu:
        s = str(raw_pu).strip().replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if dt < datetime.now(timezone.utc).replace(microsecond=0):
                raise HTTPException(status_code=403, detail="subscription ended")
        except ValueError:
            pass

    tip = str(row["wg_client_tunnel_ip"] or "").strip()
    if not tip:
        raise HTTPException(
            status_code=503,
            detail="wg_client_tunnel_ip missing; ensure VPN_WG_POST_PROVISION_SCRIPT ran",
        )

    keys_dir = (settings.wg_keys_dir or "").strip() or "/opt/aladdin-shop-vpn-api/var/wg-keys"
    pk_path = Path(keys_dir) / f"{tid}.key"
    if not pk_path.is_file():
        raise HTTPException(status_code=503, detail="client private key file missing on server")

    pub_path = Path((settings.vpn_wg_server_public_key_path or "").strip() or "/etc/wireguard/server_public.key")
    if not pub_path.is_file():
        raise HTTPException(status_code=503, detail="server public key file missing")

    pref = str(row["preferred_location_slug"] or "").strip() or None
    host = locations_util.resolve_wg_endpoint_host(settings, pref)
    if not host:
        raise HTTPException(status_code=503, detail="VPN_WG_ENDPOINT_HOST not configured")

    priv = pk_path.read_text(encoding="utf-8").strip()
    pub = pub_path.read_text(encoding="utf-8").strip()
    port = int(settings.vpn_wg_listen_port or 51820)

    mtu = max(1280, min(int(settings.vpn_wg_client_mtu or 1280), 1500))
    conf = (
        "[Interface]\n"
        f"PrivateKey = {priv}\n"
        f"Address = {tip}/32\n"
        f"MTU = {mtu}\n"
        "DNS = 1.1.1.1, 2606:4700:4700::1111\n"
        "\n"
        "[Peer]\n"
        f"PublicKey = {pub}\n"
        f"Endpoint = {host}:{port}\n"
        "AllowedIPs = 0.0.0.0/0\n"
        "PersistentKeepalive = 25\n"
    )
    return Response(content=conf, status_code=200, media_type="text/plain; charset=utf-8")


@router.get("/locations/catalog")
async def locations_catalog(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[aiosqlite.Connection, Depends(get_db)],
) -> Response:
    """Каталог строк «локации» для бота (HMAC + nonce; без Idempotency-Key)."""
    body = b""
    _verify_hmac_only(request, settings, body)
    await _nonce_guard(db, request)
    payload = json.dumps(locations_util.catalog_payload_from_settings(settings))
    return Response(content=payload, status_code=200, media_type="application/json")


@router.get("/egress/catalog")
async def egress_catalog(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[aiosqlite.Connection, Depends(get_db)],
) -> Response:
    """Egress-ноды (VPN_EGRESS_NODES_JSON) для бота и админки."""
    body = b""
    _verify_hmac_only(request, settings, body)
    await _nonce_guard(db, request)
    payload = json.dumps(egress_nodes_util.egress_catalog_payload(settings))
    return Response(content=payload, status_code=200, media_type="application/json")


@router.post("/locations/select")
async def location_select(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[aiosqlite.Connection, Depends(get_db)],
) -> Response:
    """Сохранить предпочитаемую локацию (slug) для endpoint в WG .conf."""
    body = await request.body()
    _verify_hmac_only(request, settings, body)
    await _nonce_guard(db, request)
    try:
        parsed = LocationSelectBody.model_validate_json(body)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=json.loads(e.json())) from e

    slug = parsed.location_slug.strip()
    known = {it.slug for it in locations_util.catalog_items_from_settings(settings)}
    if slug not in known:
        raise HTTPException(status_code=400, detail="unknown location_slug")

    tid = int(parsed.telegram_user_id)
    now = _utc_now_iso()
    cur = await db.execute("SELECT status FROM vpn_accounts WHERE telegram_user_id = ?", (tid,))
    row = await cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="unknown telegram_user_id")
    if str(row["status"] or "") != "vpn_active":
        raise HTTPException(status_code=403, detail=f"vpn not active ({row['status']})")

    await db.execute(
        """
        UPDATE vpn_accounts SET preferred_location_slug = ?, updated_at = ?
        WHERE telegram_user_id = ?
        """,
        (slug, now, tid),
    )
    await db.commit()
    host = locations_util.resolve_wg_endpoint_host(settings, slug)
    out = json.dumps({"ok": True, "location_slug": slug, "wg_endpoint_host": host})
    return Response(content=out, status_code=200, media_type="application/json")


@router.post("/ovpn/conf")
async def ovpn_conf(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[aiosqlite.Connection, Depends(get_db)],
) -> Response:
    """Клиентский OpenVPN .ovpn из шаблона (vpn-10)."""
    body = await request.body()
    _verify_hmac_only(request, settings, body)
    await _nonce_guard(db, request)
    try:
        parsed = OvpnConfBody.model_validate_json(body)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=json.loads(e.json())) from e

    tid = int(parsed.telegram_user_id)
    cur = await db.execute("SELECT status, paid_until FROM vpn_accounts WHERE telegram_user_id = ?", (tid,))
    row = await cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="unknown telegram_user_id")
    if str(row["status"] or "") != "vpn_active":
        raise HTTPException(status_code=403, detail=f"vpn not active ({row['status']})")

    profiles_dir = (settings.vpn_ovpn_profiles_dir or "").strip() or "/opt/aladdin-shop-vpn-api/var/ovpn-profiles"
    profile_path = Path(profiles_dir) / f"{tid}.ovpn"
    if not profile_path.is_file():
        issue_script = (settings.vpn_ovpn_client_issue_script or "").strip()
        if not issue_script:
            raise HTTPException(
                status_code=503,
                detail="ovpn profile missing; set VPN_OVPN_CLIENT_ISSUE_SCRIPT",
            )
        try:
            subprocess.run([issue_script, str(tid)], timeout=120, check=True)
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            raise HTTPException(status_code=503, detail="ovpn client issue failed") from e
    if not profile_path.is_file():
        raise HTTPException(status_code=503, detail="ovpn profile not found after issue")
    text = profile_path.read_text(encoding="utf-8")
    return Response(content=text, status_code=200, media_type="application/x-openvpn-profile")
