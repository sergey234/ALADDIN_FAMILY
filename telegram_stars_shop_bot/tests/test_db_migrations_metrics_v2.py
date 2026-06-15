from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from bot.db.database import connect


REQUIRED_TABLES = (
    "marketing_spend_daily",
    "user_acquisition",
    "metrics_daily",
    "user_feedback",
    "support_tickets",
)


def _table_exists(db_path: Path, table: str) -> bool:
    con = sqlite3.connect(db_path)
    try:
        row = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
            (table,),
        ).fetchone()
        return row is not None
    finally:
        con.close()


def _index_exists(db_path: Path, index: str) -> bool:
    con = sqlite3.connect(db_path)
    try:
        row = con.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name = ?",
            (index,),
        ).fetchone()
        return row is not None
    finally:
        con.close()


@pytest.mark.asyncio
async def test_connect_creates_metrics_v2_tables(temp_db_path: Path) -> None:
    conn = await connect(temp_db_path)
    await conn.close()

    for table in REQUIRED_TABLES:
        assert _table_exists(temp_db_path, table), f"missing table: {table}"

    assert _index_exists(temp_db_path, "idx_marketing_spend_date")
    assert _index_exists(temp_db_path, "idx_user_acq_first_source_campaign")
    assert _index_exists(temp_db_path, "idx_metrics_daily_key_scope")
    assert _index_exists(temp_db_path, "idx_user_feedback_kind_time")
    assert _index_exists(temp_db_path, "idx_support_tickets_status_time")


@pytest.mark.asyncio
async def test_connect_migrates_legacy_db_and_preserves_rows(temp_db_path: Path) -> None:
    con = sqlite3.connect(temp_db_path)
    try:
        con.execute(
            """
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                referrer_id INTEGER,
                first_order_completed INTEGER NOT NULL DEFAULT 0,
                ref_balance_rub REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        con.execute(
            """
            CREATE TABLE orders (
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
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        con.execute(
            "INSERT INTO users (user_id, username, first_name) VALUES (?,?,?)",
            (101, "legacy_user", "Legacy"),
        )
        con.commit()
    finally:
        con.close()

    conn = await connect(temp_db_path)
    await conn.close()

    for table in REQUIRED_TABLES:
        assert _table_exists(temp_db_path, table), f"missing migrated table: {table}"

    con = sqlite3.connect(temp_db_path)
    try:
        row = con.execute("SELECT username FROM users WHERE user_id = 101").fetchone()
        assert row is not None
        assert row[0] == "legacy_user"
    finally:
        con.close()
