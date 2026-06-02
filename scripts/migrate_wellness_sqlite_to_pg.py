#!/usr/bin/env python3
"""
One-shot Wellness SQLite → Postgres migration (p3-11).

Usage:
  cd /opt/aladdin-backend
  export WELLNESS_PG_DSN='postgresql://wellness:pass@127.0.0.1:5433/wellness'
  PYTHONPATH=. python3 scripts/migrate_wellness_sqlite_to_pg.py --dry-run
  PYTHONPATH=. python3 scripts/migrate_wellness_sqlite_to_pg.py

Requires: psycopg2-binary (`pip install psycopg2-binary`)
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime
from typing import Any, Dict, List

ROOT = os.environ.get("ALADDIN_BACKEND_ROOT", os.getcwd())
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

TABLES_COPY = [
    ("wellness_checkins", "SELECT * FROM wellness_checkins ORDER BY user_id, day"),
    ("wellness_assessments", "SELECT * FROM wellness_assessments ORDER BY id"),
    ("wellness_exercises", "SELECT * FROM wellness_exercises ORDER BY id"),
    ("wellness_outcomes", "SELECT * FROM wellness_outcomes ORDER BY id"),
    ("wellness_dreams", "SELECT * FROM wellness_dreams ORDER BY id"),
    ("wellness_crisis_log", "SELECT * FROM wellness_crisis_log ORDER BY id"),
]


def _sqlite_path() -> str:
    for rel in (
        "data/companion_store.db",
        "data/companion_platform.db",
        "companion_store.db",
        "companion_platform.db",
    ):
        p = os.path.join(ROOT, rel)
        if os.path.isfile(p):
            return p
    raise FileNotFoundError(
        "companion_store.db / companion_platform.db not found under data/"
    )


def _pg():
    from security.services.ai_platform.wellness_store_postgres import (
        WellnessPostgresStore,
        ensure_schema,
    )

    if not ensure_schema():
        raise RuntimeError("Postgres schema apply failed — check WELLNESS_PG_DSN")
    import psycopg2  # type: ignore
    import psycopg2.extras  # type: ignore

    dsn = os.environ.get("WELLNESS_PG_DSN") or os.environ.get("DATABASE_URL")
    if not dsn:
        raise RuntimeError("WELLNESS_PG_DSN not set")
    return psycopg2.connect(dsn, cursor_factory=psycopg2.extras.RealDictCursor), WellnessPostgresStore()


def _migrate_settings(sqlite: sqlite3.Connection, pg_conn, store, *, dry_run: bool) -> int:
    rows = sqlite.execute("SELECT * FROM wellness_settings").fetchall()
    n = 0
    for row in rows:
        d = dict(row)
        if dry_run:
            n += 1
            continue
        store.upsert_settings_row(d)
        n += 1
    return n


def _migrate_table(
    sqlite: sqlite3.Connection,
    pg_conn,
    store: Any,
    table: str,
    query: str,
    *,
    dry_run: bool,
) -> int:
    rows = [dict(r) for r in sqlite.execute(query).fetchall()]
    if dry_run:
        return len(rows)
    if not rows:
        return 0
    cols = list(rows[0].keys())
    placeholders = ", ".join(["%s"] * len(cols))
    col_list = ", ".join(cols)
    updates = ", ".join(f"{c}=EXCLUDED.{c}" for c in cols if c not in ("user_id", "day", "id"))
    sql = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"
    if table == "wellness_checkins":
        sql += " ON CONFLICT (user_id, day) DO UPDATE SET " + updates
    with pg_conn:
        with pg_conn.cursor() as cur:
            for row in rows:
                if table == "wellness_checkins" and row.get("notes"):
                    row["notes"] = store.encrypt_field(str(row["notes"]))
                cur.execute(sql, [row[c] for c in cols])
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    sqlite_path = _sqlite_path()
    print(f"SQLite: {sqlite_path}")
    sqlite = sqlite3.connect(sqlite_path)
    sqlite.row_factory = sqlite3.Row
    pg_conn, store = _pg()
    total = 0
    try:
        for table, query in TABLES_COPY:
            try:
                n = _migrate_table(sqlite, pg_conn, store, table, query, dry_run=args.dry_run)
                print(f"  {table}: {n} rows")
                total += n
            except Exception as exc:
                print(f"  {table}: SKIP ({exc})")
        nset = _migrate_settings(sqlite, pg_conn, store, dry_run=args.dry_run)
        print(f"  wellness_settings: {nset} rows")
        total += nset
    finally:
        sqlite.close()
        pg_conn.close()
    print(f"Done {'(dry-run)' if args.dry_run else ''} — {total} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
