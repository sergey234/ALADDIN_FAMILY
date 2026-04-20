from __future__ import annotations

import aiosqlite
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    referrer_id INTEGER,
    first_order_completed INTEGER NOT NULL DEFAULT 0,
    ref_balance_rub REAL NOT NULL DEFAULT 0,
    balance_rub REAL NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id TEXT NOT NULL,
    product_title TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL,
    usd_base REAL NOT NULL,
    rub_before_discounts REAL NOT NULL,
    rub_after_discounts REAL NOT NULL,
    referral_discount_rub REAL NOT NULL DEFAULT 0,
    wholesale_discount_rub REAL NOT NULL DEFAULT 0,
    referrer_id INTEGER,
    commission_rub REAL NOT NULL DEFAULT 0,
    commission_paid INTEGER NOT NULL DEFAULT 0,
    user_note TEXT,
    admin_note TEXT,
    balance_applied_rub REAL NOT NULL DEFAULT 0,
    source TEXT NOT NULL DEFAULT 'telegram',
    api_client_id INTEGER,
    idempotency_key TEXT,
    external_ref TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

CREATE TABLE IF NOT EXISTS api_clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_user_id INTEGER NOT NULL,
    key_hash TEXT NOT NULL UNIQUE,
    key_prefix TEXT NOT NULL,
    scopes TEXT NOT NULL DEFAULT 'orders:write,orders:read,profile:read,topups:read,topups:write',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    revoked_at TEXT,
    last_used_at TEXT,
    label TEXT
);
CREATE INDEX IF NOT EXISTS idx_api_clients_owner ON api_clients(owner_user_id);

CREATE TABLE IF NOT EXISTS ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount_rub REAL NOT NULL,
    balance_after REAL NOT NULL,
    kind TEXT NOT NULL,
    ref_type TEXT,
    ref_id INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS topup_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount_rub REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sell_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    stars INTEGER NOT NULL,
    rub_offer REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'new',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS api_key_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    contact TEXT NOT NULL,
    comment TEXT,
    status TEXT NOT NULL DEFAULT 'new',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS outbound_webhook_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_client_id INTEGER NOT NULL,
    order_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    target_url TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 5,
    next_attempt_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_error TEXT,
    delivered_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_outbound_webhooks_pending
ON outbound_webhook_events(status, next_attempt_at);
"""


async def _ensure_column(conn: aiosqlite.Connection, table: str, column: str, ddl: str) -> None:
    cur = await conn.execute(f"PRAGMA table_info({table})")
    rows = await cur.fetchall()
    names = {r[1] for r in rows}
    if column not in names:
        await conn.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")


async def migrate_legacy(conn: aiosqlite.Connection) -> None:
    """Добавляет колонки/таблицы к старым БД без balance_rub и т.д."""
    await _ensure_column(conn, "users", "balance_rub", "balance_rub REAL NOT NULL DEFAULT 0")
    await _ensure_column(conn, "orders", "balance_applied_rub", "balance_applied_rub REAL NOT NULL DEFAULT 0")
    await _ensure_column(conn, "orders", "source", "source TEXT NOT NULL DEFAULT 'telegram'")
    await _ensure_column(conn, "orders", "api_client_id", "api_client_id INTEGER")
    await _ensure_column(conn, "orders", "idempotency_key", "idempotency_key TEXT")
    await _ensure_column(conn, "orders", "external_ref", "external_ref TEXT")
    await conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount_rub REAL NOT NULL,
            balance_after REAL NOT NULL,
            kind TEXT NOT NULL,
            ref_type TEXT,
            ref_id INTEGER,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS topup_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount_rub REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS sell_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            stars INTEGER NOT NULL,
            rub_offer REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'new',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS api_key_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            contact TEXT NOT NULL,
            comment TEXT,
            status TEXT NOT NULL DEFAULT 'new',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS api_clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_user_id INTEGER NOT NULL,
            key_hash TEXT NOT NULL UNIQUE,
            key_prefix TEXT NOT NULL,
            scopes TEXT NOT NULL DEFAULT 'orders:write,orders:read,profile:read,topups:read,topups:write',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            revoked_at TEXT,
            last_used_at TEXT,
            label TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_api_clients_owner ON api_clients(owner_user_id);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_api_idempotency
        ON orders(api_client_id, idempotency_key)
        WHERE idempotency_key IS NOT NULL AND api_client_id IS NOT NULL;
        CREATE TABLE IF NOT EXISTS payment_provider_events (
            idempotency_key TEXT NOT NULL PRIMARY KEY,
            order_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS outbound_webhook_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_client_id INTEGER NOT NULL,
            order_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            target_url TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            attempts INTEGER NOT NULL DEFAULT 0,
            max_attempts INTEGER NOT NULL DEFAULT 5,
            next_attempt_at TEXT NOT NULL DEFAULT (datetime('now')),
            last_error TEXT,
            delivered_at TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_outbound_webhooks_pending
        ON outbound_webhook_events(status, next_attempt_at);
        """
    )
    await _ensure_column(conn, "api_clients", "webhook_url", "webhook_url TEXT")
    await _ensure_column(conn, "api_clients", "webhook_secret", "webhook_secret TEXT")
    await conn.commit()


async def connect(db_path: Path) -> aiosqlite.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(db_path)
    conn.row_factory = aiosqlite.Row
    await conn.executescript(SCHEMA)
    await conn.commit()
    await migrate_legacy(conn)
    return conn
