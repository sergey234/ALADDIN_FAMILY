from __future__ import annotations

import asyncio
from pathlib import Path
from typing import AsyncIterator

import aiosqlite

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS vpn_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id INTEGER NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'vpn_provisioning',
    paid_until TEXT,
    wg_client_public_key TEXT,
    wg_client_tunnel_ip TEXT,
    opaque_token TEXT UNIQUE,
    last_error TEXT,
    provision_attempts INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    idempotency_key TEXT UNIQUE,
    attempts INTEGER NOT NULL DEFAULT 0,
    next_run_at TEXT NOT NULL,
    last_error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_jobs_status_next ON jobs(status, next_run_at);

CREATE TABLE IF NOT EXISTS nonce_cache (
    nonce TEXT PRIMARY KEY,
    expires_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_nonce_expires ON nonce_cache(expires_at);

CREATE TABLE IF NOT EXISTS idempotency_ledger (
    idempotency_key TEXT PRIMARY KEY,
    route TEXT NOT NULL,
    response_status INTEGER NOT NULL,
    response_body TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


_db_init_lock = asyncio.Lock()


async def ensure_db_path(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)


async def _ensure_columns(db: aiosqlite.Connection) -> None:
    cur = await db.execute("PRAGMA table_info(vpn_accounts)")
    rows = await cur.fetchall()
    names = {str(r[1]) for r in rows}
    if "wg_client_tunnel_ip" not in names:
        await db.execute("ALTER TABLE vpn_accounts ADD COLUMN wg_client_tunnel_ip TEXT")
    if "preferred_location_slug" not in names:
        await db.execute("ALTER TABLE vpn_accounts ADD COLUMN preferred_location_slug TEXT")
    if "xray_client_uuid" not in names:
        await db.execute("ALTER TABLE vpn_accounts ADD COLUMN xray_client_uuid TEXT")


async def init_schema(db_path: Path) -> None:
    async with _db_init_lock:
        await ensure_db_path(db_path)
        async with aiosqlite.connect(db_path) as db:
            await db.executescript(SCHEMA_SQL)
            await _ensure_columns(db)
            await db.commit()


async def connect(db_path: Path) -> AsyncIterator[aiosqlite.Connection]:
    await init_schema(db_path)
    async with aiosqlite.connect(db_path) as conn:
        conn.row_factory = aiosqlite.Row
        yield conn
