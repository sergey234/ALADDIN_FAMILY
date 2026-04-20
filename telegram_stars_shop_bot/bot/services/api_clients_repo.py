from __future__ import annotations

import hashlib
import secrets
from typing import TYPE_CHECKING

import aiosqlite

if TYPE_CHECKING:
    pass


def hash_api_key(raw_secret: str, pepper: str) -> str:
    if not pepper:
        raise ValueError("API_KEY_PEPPER is not configured")
    payload = f"{pepper}\x1e{raw_secret}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def generate_api_secret() -> str:
    """Одноразово показываемый секрет (сырое значение для заголовка X-API-KEY)."""
    return f"ak_live_{secrets.token_urlsafe(32)}"


async def revoke_all_active_for_owner(conn: aiosqlite.Connection, owner_user_id: int) -> None:
    await conn.execute(
        """
        UPDATE api_clients SET revoked_at = datetime('now')
        WHERE owner_user_id = ? AND revoked_at IS NULL
        """,
        (owner_user_id,),
    )


async def create_api_client(
    conn: aiosqlite.Connection,
    *,
    owner_user_id: int,
    pepper: str,
    label: str | None = None,
    revoke_previous: bool = True,
) -> tuple[int, str]:
    """
    Создаёт новый ключ. Возвращает (id, raw_secret) — raw_secret показать пользователю один раз.
    """
    if revoke_previous:
        await revoke_all_active_for_owner(conn, owner_user_id)
    raw = generate_api_secret()
    kh = hash_api_key(raw, pepper)
    prefix = raw[:14] + "…"
    cur = await conn.execute(
        """
        INSERT INTO api_clients (owner_user_id, key_hash, key_prefix, label)
        VALUES (?, ?, ?, ?)
        """,
        (owner_user_id, kh, prefix, label),
    )
    await conn.commit()
    return int(cur.lastrowid), raw


async def get_active_by_secret(
    conn: aiosqlite.Connection,
    raw_secret: str,
    pepper: str,
) -> aiosqlite.Row | None:
    kh = hash_api_key(raw_secret.strip(), pepper)
    cur = await conn.execute(
        """
        SELECT * FROM api_clients
        WHERE key_hash = ? AND revoked_at IS NULL
        """,
        (kh,),
    )
    return await cur.fetchone()


async def touch_last_used(conn: aiosqlite.Connection, client_id: int) -> None:
    await conn.execute(
        "UPDATE api_clients SET last_used_at = datetime('now') WHERE id = ?",
        (client_id,),
    )
    await conn.commit()


async def get_by_id(conn: aiosqlite.Connection, client_id: int) -> aiosqlite.Row | None:
    cur = await conn.execute("SELECT * FROM api_clients WHERE id = ?", (client_id,))
    return await cur.fetchone()


async def set_partner_webhook(
    conn: aiosqlite.Connection,
    *,
    client_id: int,
    webhook_url: str | None,
    webhook_secret: str | None,
) -> None:
    await conn.execute(
        """
        UPDATE api_clients
        SET webhook_url = ?, webhook_secret = ?
        WHERE id = ? AND revoked_at IS NULL
        """,
        (webhook_url, webhook_secret, client_id),
    )
    await conn.commit()


async def get_active_prefix_for_owner(conn: aiosqlite.Connection, owner_user_id: int) -> str | None:
    cur = await conn.execute(
        """
        SELECT key_prefix FROM api_clients
        WHERE owner_user_id = ? AND revoked_at IS NULL
        ORDER BY id DESC LIMIT 1
        """,
        (owner_user_id,),
    )
    row = await cur.fetchone()
    return str(row["key_prefix"]) if row else None
