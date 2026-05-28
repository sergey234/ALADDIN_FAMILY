from __future__ import annotations

import hashlib
import hmac
import time
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, Tuple

import aiosqlite

if TYPE_CHECKING:
    from pathlib import Path


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def signing_base(*, method: str, path: str, timestamp: str, nonce: str, body: bytes) -> bytes:
    body_hash = hashlib.sha256(body or b"").hexdigest()
    msg = f"{method.upper()}\n{path}\n{timestamp}\n{nonce}\n{body_hash}"
    return msg.encode("utf-8")


def compute_signature(secret: str, *, method: str, path: str, timestamp: str, nonce: str, body: bytes) -> str:
    digest = hmac.new(
        secret.encode("utf-8"),
        signing_base(method=method, path=path, timestamp=timestamp, nonce=nonce, body=body),
        hashlib.sha256,
    ).hexdigest()
    return digest


def verify_signature(
    secret: str,
    *,
    method: str,
    path: str,
    timestamp: str,
    nonce: str,
    body: bytes,
    signature_hex: str,
    skew_seconds: int = 120,
) -> tuple[bool, str]:
    if not signature_hex or not timestamp or not nonce:
        return False, "missing auth headers"
    try:
        ts = int(timestamp)
    except ValueError:
        return False, "bad timestamp"
    now = int(time.time())
    if abs(now - ts) > skew_seconds:
        return False, "timestamp out of window"
    expected = compute_signature(secret, method=method, path=path, timestamp=timestamp, nonce=nonce, body=body)
    if not hmac.compare_digest(expected, signature_hex):
        return False, "bad signature"
    return True, ""


async def consume_nonce(db: aiosqlite.Connection, *, nonce: str, ttl_seconds: int = 300) -> bool:
    """Return True if nonce is new and stored; False if replay."""
    now = int(time.time())
    expires_at = now + ttl_seconds
    await db.execute("DELETE FROM nonce_cache WHERE expires_at < ?", (now,))
    try:
        await db.execute(
            "INSERT INTO nonce_cache (nonce, expires_at) VALUES (?, ?)",
            (nonce, expires_at),
        )
        await db.commit()
        return True
    except aiosqlite.IntegrityError:
        await db.rollback()
        return False


async def idempotency_lookup(db: aiosqlite.Connection, key: str) -> Optional[Tuple[int, str]]:
    cur = await db.execute(
        "SELECT response_status, response_body FROM idempotency_ledger WHERE idempotency_key = ?",
        (key,),
    )
    row = await cur.fetchone()
    if row is None:
        return None
    return int(row[0]), str(row[1])


async def idempotency_store(
    db: aiosqlite.Connection, *, key: str, route: str, response_status: int, response_body: str
) -> None:
    await db.execute(
        """
        INSERT INTO idempotency_ledger (idempotency_key, route, response_status, response_body, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (key, route, response_status, response_body, _utc_now_iso()),
    )
    await db.commit()


async def open_db(db_path: "Path") -> aiosqlite.Connection:
    from pathlib import Path as P

    from aladdin_shop_vpn_api.db import init_schema

    p = P(db_path)
    await init_schema(p)
    conn = await aiosqlite.connect(p)
    conn.row_factory = aiosqlite.Row
    return conn
