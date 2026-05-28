from __future__ import annotations

import subprocess
from typing import Annotated

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, Response

from aladdin_shop_vpn_api.deps import get_db, get_settings
from aladdin_shop_vpn_api.settings import Settings
from aladdin_shop_vpn_api.sub_access_watch import record_sub_access
from aladdin_shop_vpn_api.subscription_access import assert_subscription_active
from aladdin_shop_vpn_api.subscription_util import build_subscription_body

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    iface = (settings.vpn_wg_interface or "").strip()
    if not iface:
        return {"status": "ready", "wg": "skipped", "detail": "VPN_WG_INTERFACE not set"}
    try:
        r = subprocess.run(
            ["ip", "link", "show", iface],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        raise HTTPException(status_code=503, detail="wg check failed") from None
    if r.returncode != 0:
        raise HTTPException(status_code=503, detail=f"interface {iface} not up")
    return {"status": "ready", "wg": iface}


@router.get("/sub/{opaque_token}")
async def subscription_placeholder(
    opaque_token: str,
    db: Annotated[aiosqlite.Connection, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    cur = await db.execute(
        """
        SELECT id, status, paid_until, xray_client_uuid
        FROM vpn_accounts WHERE opaque_token = ?
        """,
        (opaque_token,),
    )
    row = await cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="unknown token")
    assert_subscription_active(
        status=str(row["status"] or ""),
        paid_until=str(row["paid_until"] or "") if row["paid_until"] is not None else None,
    )
    xray_uuid = str(row["xray_client_uuid"] or "").strip() or None
    body = build_subscription_body(
        settings=settings,
        opaque_token=opaque_token,
        xray_client_uuid=xray_uuid,
    )
    if body:
        threshold = int(getattr(settings, "vpn_sub_access_alert_per_hour", 0) or 0)
        if threshold > 0:
            try:
                await record_sub_access(db, opaque_token=opaque_token)
            except Exception:
                pass
        return Response(
            content=body,
            status_code=200,
            media_type="text/plain; charset=utf-8",
        )
    return Response(
        content=(
            "# Xray subscription not configured "
            "(VPN_SUBSCRIBE_VLESS_TEMPLATE or VPN_SUBSCRIBE_BODY_FILE; vpn-05)\n"
        ),
        status_code=501,
        media_type="text/plain; charset=utf-8",
    )
