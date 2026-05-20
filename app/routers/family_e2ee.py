# -*- coding: utf-8 -*-
"""
E1.2 — Family Chat E2EE: public key directory (Signal-compatible material).
Server never stores private keys; only public key bundles and opaque distribution blobs.
"""

from __future__ import annotations

import base64
import binascii
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.auth.auth import get_current_user

try:
    from app.database.database import get_db as get_postgres_db
except ImportError:
    get_postgres_db = None

from app.routers.family import (
    _actor_belongs_to_family,
    _resolve_user_id_from_claim,
)

router = APIRouter(prefix="/api/family/chat/e2ee", tags=["family-e2ee"])

_e2ee_schema_ready = False


def _iso_utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _b64decode(field_name: str, value: str) -> bytes:
    raw = (value or "").strip()
    if not raw:
        raise HTTPException(status_code=400, detail=f"{field_name} is required")
    try:
        return base64.b64decode(raw, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"invalid base64 for {field_name}") from exc


def _b64encode(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _ensure_e2ee_schema(db) -> None:
    global _e2ee_schema_ready
    if _e2ee_schema_ready:
        return

    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS family_e2ee_devices (
                id TEXT PRIMARY KEY,
                family_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                registration_id BIGINT NOT NULL,
                identity_key_public BYTEA NOT NULL,
                signed_prekey_id BIGINT NOT NULL,
                signed_prekey_public BYTEA NOT NULL,
                signed_prekey_signature BYTEA NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                last_seen_at TIMESTAMPTZ,
                revoked_at TIMESTAMPTZ,
                UNIQUE (family_id, user_id, id)
            )
            """
        )
    )
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS family_e2ee_one_time_prekeys (
                id SERIAL PRIMARY KEY,
                device_id TEXT NOT NULL REFERENCES family_e2ee_devices(id) ON DELETE CASCADE,
                prekey_id BIGINT NOT NULL,
                prekey_public BYTEA NOT NULL,
                consumed_at TIMESTAMPTZ,
                UNIQUE (device_id, prekey_id)
            )
            """
        )
    )
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS family_e2ee_sender_key_distribution (
                id TEXT PRIMARY KEY,
                family_id TEXT NOT NULL,
                sender_device_id TEXT NOT NULL,
                distribution_message BYTEA NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
    )
    db.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_e2ee_devices_family ON family_e2ee_devices (family_id) WHERE revoked_at IS NULL"
        )
    )
    db.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_e2ee_otpk_device ON family_e2ee_one_time_prekeys (device_id) WHERE consumed_at IS NULL"
        )
    )
    db.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_e2ee_skd_family_time
            ON family_e2ee_sender_key_distribution (family_id, created_at DESC)
            """
        )
    )

    # Prepare messages table for E1.3 (columns only; v2 enforcement later)
    db.execute(
        text(
            """
            ALTER TABLE family_chat_messages
                ADD COLUMN IF NOT EXISTS envelope_version SMALLINT NOT NULL DEFAULT 1
            """
        )
    )
    db.execute(
        text(
            """
            ALTER TABLE family_chat_messages
                ADD COLUMN IF NOT EXISTS sender_device_id TEXT
            """
        )
    )
    db.execute(
        text(
            """
            ALTER TABLE family_chat_messages
                ADD COLUMN IF NOT EXISTS ciphertext BYTEA
            """
        )
    )
    db.execute(
        text(
            """
            ALTER TABLE family_chat_messages
                ADD COLUMN IF NOT EXISTS ciphertext_content_type SMALLINT DEFAULT 0
            """
        )
    )

    # Migrate INT → BIGINT (Signal-style ids can exceed 2^31-1; iOS UInt32 endian bug caused 500s).
    for ddl in (
        "ALTER TABLE family_e2ee_devices ALTER COLUMN registration_id TYPE BIGINT",
        "ALTER TABLE family_e2ee_devices ALTER COLUMN signed_prekey_id TYPE BIGINT",
        "ALTER TABLE family_e2ee_one_time_prekeys ALTER COLUMN prekey_id TYPE BIGINT",
    ):
        try:
            db.execute(text(ddl))
        except Exception:
            pass

    _e2ee_schema_ready = True


def _require_db():
    if not get_postgres_db:
        raise HTTPException(status_code=503, detail="Database not configured")


def _verify_family_access(db, user_id: int, family_id: str) -> str:
    fid = (family_id or "").strip()
    if not fid:
        raise HTTPException(status_code=400, detail="family_id is required")
    if not _actor_belongs_to_family(db, user_id, fid):
        raise HTTPException(status_code=403, detail="Not a member of this family")
    return fid


# --- Pydantic models ---


class OneTimePreKeyIn(BaseModel):
    id: int
    public: str = Field(..., description="base64 encoded prekey")


class SignedPreKeyIn(BaseModel):
    id: int
    public: str
    signature: str


class RegisterE2EEDeviceRequest(BaseModel):
    family_id: str
    device_id: Optional[str] = None
    registration_id: int
    identity_key_public: str
    signed_prekey: SignedPreKeyIn
    one_time_prekeys: List[OneTimePreKeyIn] = Field(default_factory=list)


class RegisterE2EEDeviceResponse(BaseModel):
    success: bool = True
    device_id: str
    family_id: str


class DeviceListItem(BaseModel):
    device_id: str
    user_id: int
    registration_id: int
    identity_key_public: str
    signed_prekey_id: int
    signed_prekey_public: str
    signed_prekey_signature: str
    one_time_prekey_count: int


class DeviceListResponse(BaseModel):
    family_id: str
    devices: List[DeviceListItem]


class DeviceBundleResponse(BaseModel):
    family_id: str
    device_id: str
    user_id: int
    registration_id: int
    identity_key_public: str
    signed_prekey_id: int
    signed_prekey_public: str
    signed_prekey_signature: str
    one_time_prekeys: List[OneTimePreKeyIn]


class DistributeSenderKeyRequest(BaseModel):
    family_id: str
    sender_device_id: str
    distribution_message: str = Field(..., description="base64 opaque blob")


class DistributeSenderKeyResponse(BaseModel):
    success: bool = True
    distribution_id: str


class SenderKeyDistributionItem(BaseModel):
    id: str
    sender_device_id: str
    distribution_message: str
    created_at: str


class SenderKeyDistributionListResponse(BaseModel):
    family_id: str
    items: List[SenderKeyDistributionItem]


class RevokeE2EEDeviceRequest(BaseModel):
    family_id: str
    device_id: Optional[str] = None


class RevokeE2EEDeviceResponse(BaseModel):
    success: bool = True
    device_id: str
    family_id: str


# --- Endpoints ---


@router.post("/keys/revoke", response_model=RevokeE2EEDeviceResponse)
async def revoke_e2ee_device(
    payload: RevokeE2EEDeviceRequest,
    current_user: dict = Depends(get_current_user),
):
    """Revoke device keys (logout / lost device)."""
    _require_db()
    user_id = _resolve_user_id_from_claim(current_user)
    device_id = (payload.device_id or "").strip()
    if not device_id:
        raise HTTPException(status_code=400, detail="device_id is required")

    def work() -> RevokeE2EEDeviceResponse:
        gen = get_postgres_db()
        db = next(gen)
        try:
            _ensure_e2ee_schema(db)
            fid = _verify_family_access(db, user_id, payload.family_id)
            owner = db.execute(
                text(
                    """
                    SELECT 1 FROM family_e2ee_devices
                    WHERE id = :device_id AND family_id = :family_id AND user_id = :uid
                    LIMIT 1
                    """
                ),
                {"device_id": device_id, "family_id": fid, "uid": user_id},
            ).fetchone()
            if not owner:
                raise HTTPException(status_code=403, detail="device not owned by user")
            db.execute(
                text(
                    """
                    UPDATE family_e2ee_devices
                    SET revoked_at = NOW(), last_seen_at = NOW()
                    WHERE id = :device_id AND family_id = :family_id
                    """
                ),
                {"device_id": device_id, "family_id": fid},
            )
            db.commit()
            return RevokeE2EEDeviceResponse(device_id=device_id, family_id=fid)
        finally:
            gen.close()

    import asyncio

    return await asyncio.to_thread(work)


@router.post("/keys/register", response_model=RegisterE2EEDeviceResponse)
async def register_e2ee_device(
    payload: RegisterE2EEDeviceRequest,
    current_user: dict = Depends(get_current_user),
):
    """Upload public identity + prekeys for this device (idempotent upsert)."""
    _require_db()
    user_id = _resolve_user_id_from_claim(current_user)
    device_id = (payload.device_id or "").strip() or str(uuid.uuid4())

    identity = _b64decode("identity_key_public", payload.identity_key_public)
    spk_pub = _b64decode("signed_prekey.public", payload.signed_prekey.public)
    spk_sig = _b64decode("signed_prekey.signature", payload.signed_prekey.signature)

    if len(payload.one_time_prekeys) > 100:
        raise HTTPException(status_code=400, detail="too many one_time_prekeys (max 100)")

    def work() -> RegisterE2EEDeviceResponse:
        gen = get_postgres_db()
        db = next(gen)
        try:
            _ensure_e2ee_schema(db)
            family_id = _verify_family_access(db, user_id, payload.family_id)
            now = _iso_utc_now()

            db.execute(
                text(
                    """
                    INSERT INTO family_e2ee_devices (
                        id, family_id, user_id, registration_id,
                        identity_key_public, signed_prekey_id, signed_prekey_public,
                        signed_prekey_signature, created_at, last_seen_at, revoked_at
                    ) VALUES (
                        :id, :family_id, :user_id, :registration_id,
                        :identity_key_public, :signed_prekey_id, :signed_prekey_public,
                        :signed_prekey_signature, NOW(), NOW(), NULL
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        family_id = EXCLUDED.family_id,
                        user_id = EXCLUDED.user_id,
                        registration_id = EXCLUDED.registration_id,
                        identity_key_public = EXCLUDED.identity_key_public,
                        signed_prekey_id = EXCLUDED.signed_prekey_id,
                        signed_prekey_public = EXCLUDED.signed_prekey_public,
                        signed_prekey_signature = EXCLUDED.signed_prekey_signature,
                        last_seen_at = NOW(),
                        revoked_at = NULL
                    """
                ),
                {
                    "id": device_id,
                    "family_id": family_id,
                    "user_id": user_id,
                    "registration_id": payload.registration_id,
                    "identity_key_public": identity,
                    "signed_prekey_id": payload.signed_prekey.id,
                    "signed_prekey_public": spk_pub,
                    "signed_prekey_signature": spk_sig,
                },
            )

            db.execute(
                text("DELETE FROM family_e2ee_one_time_prekeys WHERE device_id = :device_id"),
                {"device_id": device_id},
            )
            for otpk in payload.one_time_prekeys:
                db.execute(
                    text(
                        """
                        INSERT INTO family_e2ee_one_time_prekeys (device_id, prekey_id, prekey_public)
                        VALUES (:device_id, :prekey_id, :prekey_public)
                        ON CONFLICT (device_id, prekey_id) DO UPDATE SET
                            prekey_public = EXCLUDED.prekey_public,
                            consumed_at = NULL
                        """
                    ),
                    {
                        "device_id": device_id,
                        "prekey_id": otpk.id,
                        "prekey_public": _b64decode("one_time_prekeys.public", otpk.public),
                    },
                )

            db.commit()
            return RegisterE2EEDeviceResponse(device_id=device_id, family_id=family_id)
        finally:
            gen.close()

    import asyncio

    return await asyncio.to_thread(work)


@router.get("/keys", response_model=DeviceListResponse)
async def list_e2ee_devices(
    family_id: str = Query(..., description="Family id"),
    current_user: dict = Depends(get_current_user),
):
    """List active devices with public material (no private keys)."""
    _require_db()
    user_id = _resolve_user_id_from_claim(current_user)

    def work() -> DeviceListResponse:
        gen = get_postgres_db()
        db = next(gen)
        try:
            _ensure_e2ee_schema(db)
            fid = _verify_family_access(db, user_id, family_id)
            rows = db.execute(
                text(
                    """
                    SELECT d.id, d.user_id, d.registration_id,
                           d.identity_key_public, d.signed_prekey_id,
                           d.signed_prekey_public, d.signed_prekey_signature,
                           (
                             SELECT COUNT(*) FROM family_e2ee_one_time_prekeys o
                             WHERE o.device_id = d.id AND o.consumed_at IS NULL
                           ) AS otpk_count
                    FROM family_e2ee_devices d
                    WHERE d.family_id = :family_id AND d.revoked_at IS NULL
                    ORDER BY d.created_at ASC
                    """
                ),
                {"family_id": fid},
            ).fetchall()

            devices: List[DeviceListItem] = []
            for row in rows:
                devices.append(
                    DeviceListItem(
                        device_id=row[0],
                        user_id=int(row[1]),
                        registration_id=int(row[2]),
                        identity_key_public=_b64encode(bytes(row[3])),
                        signed_prekey_id=int(row[4]),
                        signed_prekey_public=_b64encode(bytes(row[5])),
                        signed_prekey_signature=_b64encode(bytes(row[6])),
                        one_time_prekey_count=int(row[7] or 0),
                    )
                )
            return DeviceListResponse(family_id=fid, devices=devices)
        finally:
            gen.close()

    import asyncio

    return await asyncio.to_thread(work)


@router.get("/keys/device/{device_id}", response_model=DeviceBundleResponse)
async def get_e2ee_device_bundle(
    device_id: str,
    family_id: str = Query(...),
    current_user: dict = Depends(get_current_user),
):
    """Fetch prekey bundle for X3DH with a specific device."""
    _require_db()
    user_id = _resolve_user_id_from_claim(current_user)
    did = device_id.strip()
    if not did:
        raise HTTPException(status_code=400, detail="device_id is required")

    def work() -> DeviceBundleResponse:
        gen = get_postgres_db()
        db = next(gen)
        try:
            _ensure_e2ee_schema(db)
            fid = _verify_family_access(db, user_id, family_id)
            dev = db.execute(
                text(
                    """
                    SELECT user_id, registration_id, identity_key_public,
                           signed_prekey_id, signed_prekey_public, signed_prekey_signature
                    FROM family_e2ee_devices
                    WHERE id = :device_id AND family_id = :family_id AND revoked_at IS NULL
                    LIMIT 1
                    """
                ),
                {"device_id": did, "family_id": fid},
            ).fetchone()
            if not dev:
                raise HTTPException(status_code=404, detail="Device not found")

            otpk_rows = db.execute(
                text(
                    """
                    SELECT prekey_id, prekey_public FROM family_e2ee_one_time_prekeys
                    WHERE device_id = :device_id AND consumed_at IS NULL
                    ORDER BY prekey_id ASC
                    LIMIT 20
                    """
                ),
                {"device_id": did},
            ).fetchall()

            one_time = [
                OneTimePreKeyIn(id=int(r[0]), public=_b64encode(bytes(r[1])))
                for r in otpk_rows
            ]

            return DeviceBundleResponse(
                family_id=fid,
                device_id=did,
                user_id=int(dev[0]),
                registration_id=int(dev[1]),
                identity_key_public=_b64encode(bytes(dev[2])),
                signed_prekey_id=int(dev[3]),
                signed_prekey_public=_b64encode(bytes(dev[4])),
                signed_prekey_signature=_b64encode(bytes(dev[5])),
                one_time_prekeys=one_time,
            )
        finally:
            gen.close()

    import asyncio

    return await asyncio.to_thread(work)


@router.post("/sender-keys/distribute", response_model=DistributeSenderKeyResponse)
async def distribute_sender_key(
    payload: DistributeSenderKeyRequest,
    current_user: dict = Depends(get_current_user),
):
    """Store opaque Sender Key distribution message (server cannot decrypt)."""
    _require_db()
    user_id = _resolve_user_id_from_claim(current_user)
    blob = _b64decode("distribution_message", payload.distribution_message)
    sender_device_id = payload.sender_device_id.strip()
    if not sender_device_id:
        raise HTTPException(status_code=400, detail="sender_device_id is required")

    def work() -> DistributeSenderKeyResponse:
        gen = get_postgres_db()
        db = next(gen)
        try:
            _ensure_e2ee_schema(db)
            fid = _verify_family_access(db, user_id, payload.family_id)
            owner = db.execute(
                text(
                    """
                    SELECT 1 FROM family_e2ee_devices
                    WHERE id = :device_id AND family_id = :family_id AND user_id = :uid
                      AND revoked_at IS NULL
                    LIMIT 1
                    """
                ),
                {"device_id": sender_device_id, "family_id": fid, "uid": user_id},
            ).fetchone()
            if not owner:
                raise HTTPException(status_code=403, detail="sender_device_id not owned by user")

            dist_id = f"SKD_{uuid.uuid4().hex[:16].upper()}"
            db.execute(
                text(
                    """
                    INSERT INTO family_e2ee_sender_key_distribution
                        (id, family_id, sender_device_id, distribution_message)
                    VALUES (:id, :family_id, :sender_device_id, :distribution_message)
                    """
                ),
                {
                    "id": dist_id,
                    "family_id": fid,
                    "sender_device_id": sender_device_id,
                    "distribution_message": blob,
                },
            )
            db.commit()
            return DistributeSenderKeyResponse(distribution_id=dist_id)
        finally:
            gen.close()

    import asyncio

    return await asyncio.to_thread(work)


@router.get("/sender-keys", response_model=SenderKeyDistributionListResponse)
async def list_sender_key_distributions(
    family_id: str = Query(...),
    since: Optional[str] = Query(None, description="ISO timestamp; return rows created after"),
    current_user: dict = Depends(get_current_user),
):
    """Fetch sender-key distribution messages for devices in the family."""
    _require_db()
    user_id = _resolve_user_id_from_claim(current_user)

    def work() -> SenderKeyDistributionListResponse:
        gen = get_postgres_db()
        db = next(gen)
        try:
            _ensure_e2ee_schema(db)
            fid = _verify_family_access(db, user_id, family_id)
            params: dict = {"family_id": fid}
            sql = """
                SELECT id, sender_device_id, distribution_message, created_at
                FROM family_e2ee_sender_key_distribution
                WHERE family_id = :family_id
            """
            if since and since.strip():
                sql += " AND created_at > CAST(:since AS TIMESTAMPTZ)"
                params["since"] = since.strip()
            sql += " ORDER BY created_at ASC LIMIT 200"

            rows = db.execute(text(sql), params).fetchall()
            items = [
                SenderKeyDistributionItem(
                    id=row[0],
                    sender_device_id=row[1],
                    distribution_message=_b64encode(bytes(row[2])),
                    created_at=row[3].isoformat() if hasattr(row[3], "isoformat") else str(row[3]),
                )
                for row in rows
            ]
            return SenderKeyDistributionListResponse(family_id=fid, items=items)
        finally:
            gen.close()

    import asyncio

    return await asyncio.to_thread(work)
