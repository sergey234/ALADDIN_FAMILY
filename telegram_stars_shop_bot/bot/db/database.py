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
    channel_member_ack_shown INTEGER NOT NULL DEFAULT 0,
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
    fulfillment_applied_at TEXT,
    fulfillment_mode TEXT NOT NULL DEFAULT 'auto',
    fulfillment_attempt_count INTEGER NOT NULL DEFAULT 0,
    fulfillment_last_error TEXT,
    fulfillment_last_attempt_at TEXT,
    fulfillment_provider_ref TEXT,
    invoice_last_requested_at TEXT,
    invoice_last_provider TEXT,
    invoice_last_external_id TEXT,
    user_note TEXT,
    admin_note TEXT,
    balance_applied_rub REAL NOT NULL DEFAULT 0,
    source TEXT NOT NULL DEFAULT 'telegram',
    api_client_id INTEGER,
    idempotency_key TEXT,
    external_ref TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    buyer_username TEXT,
    product_kind TEXT NOT NULL DEFAULT '',
    stars_qty INTEGER,
    premium_months INTEGER,
    completed_at TEXT,
    payment_gateway_fee_rub REAL NOT NULL DEFAULT 0,
    cogs_rub REAL NOT NULL DEFAULT 0,
    manual_cogs_rub REAL,
    net_profit_rub REAL NOT NULL DEFAULT 0,
    profit_snapshot_at TEXT,
    referral_discount_percent REAL NOT NULL DEFAULT 0,
    usd_rub_rate_snapshot REAL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

CREATE TABLE IF NOT EXISTS admin_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    admin_user_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    payload_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_admin_audit_created ON admin_audit_log(created_at);

CREATE TABLE IF NOT EXISTS analytics_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    meta_json TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_analytics_user_time ON analytics_events(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_analytics_type_time ON analytics_events(event_type, created_at);

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


async def _ensure_column(conn: aiosqlite.Connection, table: str, column: str, ddl: str) -> bool:
    cur = await conn.execute(f"PRAGMA table_info({table})")
    rows = await cur.fetchall()
    names = {r[1] for r in rows}
    if column not in names:
        await conn.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")
        return True
    return False


async def _backfill_orders_product_fields(conn: aiosqlite.Connection) -> None:
    """Проставить product_kind / stars_qty / premium_months и completed_at для старых строк."""
    try:
        from bot.services.catalog import load_products, products_by_id
    except Exception:
        return
    yaml_path = Path(__file__).resolve().parents[1] / "products.yaml"
    if not yaml_path.exists():
        return
    try:
        pmap = products_by_id(load_products(yaml_path))
    except Exception:
        return
    cur = await conn.execute(
        "SELECT id, product_id FROM orders WHERE TRIM(COALESCE(product_kind, '')) = ''"
    )
    rows = await cur.fetchall()
    for r in rows:
        p = pmap.get(str(r["product_id"]))
        if not p:
            continue
        kind = str(p.kind or "").strip().lower()
        sq = int(p.stars) if kind in ("stars", "gift") and p.stars is not None else None
        pm = int(p.duration_months) if kind == "premium" and p.duration_months is not None else None
        await conn.execute(
            "UPDATE orders SET product_kind = ?, stars_qty = ?, premium_months = ? WHERE id = ?",
            (kind, sq, pm, int(r["id"])),
        )
    await conn.execute(
        """
        UPDATE orders SET completed_at = COALESCE(fulfillment_applied_at, updated_at)
        WHERE status = 'completed' AND completed_at IS NULL
        """
    )


async def migrate_legacy(conn: aiosqlite.Connection) -> None:
    """Добавляет колонки/таблицы к старым БД без balance_rub и т.д."""
    await _ensure_column(conn, "users", "balance_rub", "balance_rub REAL NOT NULL DEFAULT 0")
    ack_col_added = await _ensure_column(
        conn,
        "users",
        "channel_member_ack_shown",
        "channel_member_ack_shown INTEGER NOT NULL DEFAULT 0",
    )
    if ack_col_added:
        # Старым пользователям не показываем повторно служебный экран «доступ уже есть».
        await conn.execute("UPDATE users SET channel_member_ack_shown = 1")
    locale_added = await _ensure_column(conn, "users", "locale", "locale TEXT")
    if locale_added:
        # Уже существовавшие на момент миграции пользователи — без повторного выбора языка.
        await conn.execute("UPDATE users SET locale = 'ru' WHERE locale IS NULL")
    terms_added = await _ensure_column(conn, "users", "terms_accepted_at", "terms_accepted_at TEXT")
    onboard_added = await _ensure_column(conn, "users", "onboarding_completed_at", "onboarding_completed_at TEXT")
    await _ensure_column(conn, "users", "checkout_captcha_ok_until", "checkout_captcha_ok_until INTEGER")
    await _ensure_column(conn, "users", "last_start_command_at", "last_start_command_at INTEGER")
    await _ensure_column(conn, "users", "vpn_privacy_accepted_at", "vpn_privacy_accepted_at TEXT")
    await _ensure_column(conn, "users", "vpn_terms_accepted_at", "vpn_terms_accepted_at TEXT")
    if terms_added or onboard_added:
        await conn.execute(
            "UPDATE users SET terms_accepted_at = COALESCE(terms_accepted_at, datetime('now')) WHERE terms_accepted_at IS NULL"
        )
        await conn.execute(
            "UPDATE users SET onboarding_completed_at = COALESCE(onboarding_completed_at, datetime('now')) WHERE onboarding_completed_at IS NULL"
        )
    await conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS captcha_challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            purpose TEXT NOT NULL,
            correct_idx INTEGER NOT NULL,
            options_json TEXT NOT NULL,
            expires_at INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_captcha_challenges_user ON captcha_challenges(user_id);
        """
    )
    await _ensure_column(conn, "orders", "balance_applied_rub", "balance_applied_rub REAL NOT NULL DEFAULT 0")
    await _ensure_column(conn, "orders", "source", "source TEXT NOT NULL DEFAULT 'telegram'")
    await _ensure_column(conn, "orders", "api_client_id", "api_client_id INTEGER")
    await _ensure_column(conn, "orders", "idempotency_key", "idempotency_key TEXT")
    await _ensure_column(conn, "orders", "external_ref", "external_ref TEXT")
    await _ensure_column(conn, "orders", "fulfillment_applied_at", "fulfillment_applied_at TEXT")
    await _ensure_column(
        conn, "orders", "fulfillment_mode", "fulfillment_mode TEXT NOT NULL DEFAULT 'auto'"
    )
    await _ensure_column(
        conn,
        "orders",
        "fulfillment_attempt_count",
        "fulfillment_attempt_count INTEGER NOT NULL DEFAULT 0",
    )
    await _ensure_column(conn, "orders", "fulfillment_last_error", "fulfillment_last_error TEXT")
    await _ensure_column(
        conn, "orders", "fulfillment_last_attempt_at", "fulfillment_last_attempt_at TEXT"
    )
    await _ensure_column(
        conn, "orders", "fulfillment_provider_ref", "fulfillment_provider_ref TEXT"
    )
    await _ensure_column(conn, "orders", "invoice_last_requested_at", "invoice_last_requested_at TEXT")
    await _ensure_column(conn, "orders", "invoice_last_provider", "invoice_last_provider TEXT")
    await _ensure_column(conn, "orders", "invoice_last_external_id", "invoice_last_external_id TEXT")
    await _ensure_column(conn, "orders", "bc_payment_claim_at", "bc_payment_claim_at TEXT")
    await conn.execute(
        """
        UPDATE orders
        SET fulfillment_applied_at = COALESCE(updated_at, datetime('now'))
        WHERE status = 'completed'
          AND fulfillment_applied_at IS NULL
          AND commission_paid = 1
        """
    )
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
        CREATE TABLE IF NOT EXISTS admin_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            admin_user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            payload_json TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_admin_audit_created ON admin_audit_log(created_at);
        """
    )
    await _ensure_column(conn, "api_clients", "webhook_url", "webhook_url TEXT")
    await _ensure_column(conn, "api_clients", "webhook_secret", "webhook_secret TEXT")

    await _ensure_column(conn, "orders", "buyer_username", "buyer_username TEXT")
    await _ensure_column(conn, "orders", "product_kind", "product_kind TEXT NOT NULL DEFAULT ''")
    await _ensure_column(conn, "orders", "stars_qty", "stars_qty INTEGER")
    await _ensure_column(conn, "orders", "premium_months", "premium_months INTEGER")
    await _ensure_column(conn, "orders", "completed_at", "completed_at TEXT")
    await _ensure_column(conn, "orders", "payment_gateway_fee_rub", "payment_gateway_fee_rub REAL NOT NULL DEFAULT 0")
    await _ensure_column(conn, "orders", "cogs_rub", "cogs_rub REAL NOT NULL DEFAULT 0")
    await _ensure_column(conn, "orders", "manual_cogs_rub", "manual_cogs_rub REAL")
    await _ensure_column(conn, "orders", "net_profit_rub", "net_profit_rub REAL NOT NULL DEFAULT 0")
    await _ensure_column(conn, "orders", "profit_snapshot_at", "profit_snapshot_at TEXT")
    await _ensure_column(
        conn, "orders", "referral_discount_percent", "referral_discount_percent REAL NOT NULL DEFAULT 0"
    )
    await _ensure_column(conn, "orders", "usd_rub_rate_snapshot", "usd_rub_rate_snapshot REAL")

    await conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS analytics_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            meta_json TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_analytics_user_time ON analytics_events(user_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_analytics_type_time ON analytics_events(event_type, created_at);
        """
    )
    await conn.execute(
        """
        UPDATE orders
        SET referral_discount_percent = ROUND(
            100.0 * referral_discount_rub / NULLIF(rub_before_discounts, 0), 4
        )
        WHERE referral_discount_rub > 0.009
          AND rub_before_discounts > 0.009
          AND referral_discount_percent <= 0
        """
    )

    await _backfill_orders_product_fields(conn)
    await conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS partner_contests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            prize_text TEXT NOT NULL,
            starts_at TEXT NOT NULL,
            ends_at TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_partner_contests_active
        ON partner_contests(is_active, starts_at, ends_at);

        CREATE TABLE IF NOT EXISTS vpn_referral_codes (
            user_id INTEGER PRIMARY KEY,
            code TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_vpn_referral_codes_code ON vpn_referral_codes(code);

        CREATE TABLE IF NOT EXISTS vpn_referral_grants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referred_user_id INTEGER NOT NULL UNIQUE,
            referrer_user_id INTEGER NOT NULL,
            order_id INTEGER NOT NULL UNIQUE,
            friend_days INTEGER NOT NULL,
            referrer_days INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            api_friend_ok INTEGER NOT NULL DEFAULT 0,
            api_referrer_ok INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_vpn_referral_grants_referrer ON vpn_referral_grants(referrer_user_id);
        CREATE INDEX IF NOT EXISTS idx_vpn_referral_grants_created ON vpn_referral_grants(created_at);
        """
    )
    await _ensure_column(
        conn, "vpn_referral_grants", "api_friend_attempts", "api_friend_attempts INTEGER NOT NULL DEFAULT 0"
    )
    await _ensure_column(
        conn, "vpn_referral_grants", "api_referrer_attempts", "api_referrer_attempts INTEGER NOT NULL DEFAULT 0"
    )
    await _ensure_column(conn, "vpn_referral_grants", "api_friend_last_error", "api_friend_last_error TEXT")
    await _ensure_column(conn, "vpn_referral_grants", "api_referrer_last_error", "api_referrer_last_error TEXT")
    await conn.commit()


async def connect(db_path: Path) -> aiosqlite.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(db_path)
    conn.row_factory = aiosqlite.Row
    await conn.executescript(SCHEMA)
    await conn.commit()
    await migrate_legacy(conn)
    return conn
