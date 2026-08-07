"""
Web↔bot identity layer: shop.accounts.

- account_id: UUID (canonical)
- vpn_subject_id: int used as orders.user_id / vpn_accounts.telegram_user_id
  (real Telegram id for bot-born accounts; negative synthetic for web-only)
- telegram_user_id: nullable until optional link
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timezone
from typing import Any

import aiosqlite

# Synthetic VPN/order subject ids for web-only accounts (never collide with real TG > 0).
_SYNTHETIC_FLOOR = -1_900_000_000_000


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def new_account_id() -> str:
    return str(uuid.uuid4())


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def new_access_token() -> str:
    return secrets.token_urlsafe(32)


def new_link_code() -> str:
    return secrets.token_urlsafe(12).replace("-", "").replace("_", "")[:16]


async def ensure_accounts_schema(conn: aiosqlite.Connection) -> None:
    """Idempotent — also called from migrate_legacy."""
    await conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            account_id TEXT PRIMARY KEY,
            telegram_user_id INTEGER UNIQUE,
            vpn_subject_id INTEGER NOT NULL UNIQUE,
            created_via TEXT NOT NULL DEFAULT 'telegram',
            created_at TEXT NOT NULL,
            session_secret_hash TEXT,
            referrer_telegram_id INTEGER,
            merged_into_account_id TEXT,
            nickname TEXT,
            access_code_hash TEXT,
            nickname_set_at TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_accounts_tg ON accounts(telegram_user_id);
        CREATE INDEX IF NOT EXISTS idx_accounts_vpn_subject ON accounts(vpn_subject_id);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_accounts_nickname_unique
            ON accounts(nickname) WHERE nickname IS NOT NULL AND TRIM(nickname) != '';

        CREATE TABLE IF NOT EXISTS order_access_tokens (
            token_hash TEXT PRIMARY KEY,
            order_id INTEGER NOT NULL,
            account_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_order_access_order ON order_access_tokens(order_id);

        CREATE TABLE IF NOT EXISTS link_tokens (
            code_hash TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used_at TEXT,
            used_by_telegram_id INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_link_tokens_account ON link_tokens(account_id);
        """
    )
    # Soft migrations for existing DBs (CREATE TABLE IF NOT EXISTS won't add cols).
    for col, ddl in (
        ("nickname", "nickname TEXT"),
        ("access_code_hash", "access_code_hash TEXT"),
        ("nickname_set_at", "nickname_set_at TEXT"),
    ):
        try:
            await conn.execute(f"ALTER TABLE accounts ADD COLUMN {ddl}")
        except Exception:
            pass
    try:
        await conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_accounts_nickname_unique
            ON accounts(nickname) WHERE nickname IS NOT NULL AND TRIM(nickname) != ''
            """
        )
    except Exception:
        pass
    await conn.commit()


async def _next_synthetic_vpn_subject(conn: aiosqlite.Connection) -> int:
    cur = await conn.execute(
        "SELECT MIN(vpn_subject_id) AS m FROM accounts WHERE vpn_subject_id < 0"
    )
    row = await cur.fetchone()
    m = row["m"] if row and row["m"] is not None else None
    if m is None or int(m) >= 0:
        return _SYNTHETIC_FLOOR
    return int(m) - 1


async def get_account_by_id(conn: aiosqlite.Connection, account_id: str) -> dict[str, Any] | None:
    cur = await conn.execute(
        "SELECT * FROM accounts WHERE account_id = ? AND merged_into_account_id IS NULL",
        (account_id,),
    )
    row = await cur.fetchone()
    return dict(row) if row else None


async def get_account_by_telegram(
    conn: aiosqlite.Connection, telegram_user_id: int
) -> dict[str, Any] | None:
    cur = await conn.execute(
        "SELECT * FROM accounts WHERE telegram_user_id = ? AND merged_into_account_id IS NULL",
        (int(telegram_user_id),),
    )
    row = await cur.fetchone()
    return dict(row) if row else None


async def get_account_by_vpn_subject(
    conn: aiosqlite.Connection, vpn_subject_id: int
) -> dict[str, Any] | None:
    cur = await conn.execute(
        "SELECT * FROM accounts WHERE vpn_subject_id = ? AND merged_into_account_id IS NULL",
        (int(vpn_subject_id),),
    )
    row = await cur.fetchone()
    return dict(row) if row else None


async def ensure_account_for_telegram(
    conn: aiosqlite.Connection,
    *,
    telegram_user_id: int,
    created_via: str = "telegram",
) -> dict[str, Any]:
    """Bot path: vpn_subject_id == telegram_user_id."""
    tid = int(telegram_user_id)
    existing = await get_account_by_telegram(conn, tid)
    if existing:
        return existing
    by_subj = await get_account_by_vpn_subject(conn, tid)
    if by_subj:
        if by_subj.get("telegram_user_id") is None:
            await conn.execute(
                "UPDATE accounts SET telegram_user_id = ? WHERE account_id = ?",
                (tid, by_subj["account_id"]),
            )
            await conn.commit()
            return (await get_account_by_id(conn, str(by_subj["account_id"]))) or by_subj
        return by_subj
    aid = new_account_id()
    now = _utc_now()
    await conn.execute(
        """
        INSERT INTO accounts (
            account_id, telegram_user_id, vpn_subject_id, created_via, created_at
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (aid, tid, tid, created_via, now),
    )
    await conn.commit()
    return (await get_account_by_id(conn, aid)) or {
        "account_id": aid,
        "telegram_user_id": tid,
        "vpn_subject_id": tid,
        "created_via": created_via,
    }


async def create_web_account(
    conn: aiosqlite.Connection,
    *,
    referrer_telegram_id: int | None = None,
) -> dict[str, Any]:
    """Web checkout without Telegram: synthetic vpn_subject_id + placeholder users row."""
    from bot.services import users_repo

    aid = new_account_id()
    subj = await _next_synthetic_vpn_subject(conn)
    now = _utc_now()
    await conn.execute(
        """
        INSERT INTO accounts (
            account_id, telegram_user_id, vpn_subject_id, created_via, created_at,
            referrer_telegram_id
        ) VALUES (?, NULL, ?, 'web', ?, ?)
        """,
        (aid, subj, now, referrer_telegram_id),
    )
    # Placeholder user so orders.user_id FK / legacy paths work.
    await users_repo.upsert_user(conn, user_id=subj, username=None, first_name="web")
    if referrer_telegram_id:
        try:
            await users_repo.set_referrer_if_empty(
                conn, user_id=subj, referrer_id=int(referrer_telegram_id)
            )
        except Exception:
            pass
    await conn.commit()
    return (await get_account_by_id(conn, aid)) or {
        "account_id": aid,
        "vpn_subject_id": subj,
        "created_via": "web",
    }


async def backfill_accounts_from_users(conn: aiosqlite.Connection) -> int:
    cur = await conn.execute("SELECT user_id FROM users WHERE user_id > 0")
    rows = await cur.fetchall()
    n = 0
    for r in rows:
        tid = int(r["user_id"])
        before = await get_account_by_telegram(conn, tid)
        if before:
            continue
        await ensure_account_for_telegram(conn, telegram_user_id=tid, created_via="telegram")
        n += 1
    # Stamp orders.account_id where missing
    cur2 = await conn.execute(
        """
        SELECT o.id, o.user_id FROM orders o
        WHERE o.account_id IS NULL OR TRIM(COALESCE(o.account_id, '')) = ''
        """
    )
    for r in await cur2.fetchall():
        uid = int(r["user_id"])
        acc = await get_account_by_vpn_subject(conn, uid) or await get_account_by_telegram(conn, uid)
        if not acc and uid > 0:
            acc = await ensure_account_for_telegram(conn, telegram_user_id=uid)
        if acc:
            await conn.execute(
                "UPDATE orders SET account_id = ? WHERE id = ?",
                (acc["account_id"], int(r["id"])),
            )
    await conn.commit()
    return n


async def issue_order_access_token(
    conn: aiosqlite.Connection,
    *,
    order_id: int,
    account_id: str,
    ttl_days: int = 14,
) -> str:
    from datetime import timedelta

    raw = new_access_token()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    exp = now + timedelta(days=max(1, int(ttl_days)))
    await conn.execute(
        """
        INSERT INTO order_access_tokens (token_hash, order_id, account_id, created_at, expires_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (hash_token(raw), int(order_id), account_id, now.isoformat(), exp.isoformat()),
    )
    await conn.commit()
    return raw


async def resolve_order_access_token(
    conn: aiosqlite.Connection, raw_token: str
) -> dict[str, Any] | None:
    cur = await conn.execute(
        "SELECT * FROM order_access_tokens WHERE token_hash = ?",
        (hash_token(raw_token),),
    )
    row = await cur.fetchone()
    if not row:
        return None
    exp_raw = row["expires_at"] if "expires_at" in row.keys() else None
    if exp_raw:
        try:
            exp = datetime.fromisoformat(str(exp_raw).replace("Z", "+00:00"))
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > exp:
                return None
        except Exception:
            pass
    return dict(row)


def order_access_token_age_hours(tok: dict[str, Any]) -> float | None:
    """Hours since token created_at; None if unknown."""
    raw = tok.get("created_at") if isinstance(tok, dict) else None
    if not raw:
        return None
    try:
        created = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        return max(0.0, (datetime.now(timezone.utc) - created).total_seconds() / 3600.0)
    except Exception:
        return None


async def issue_link_token(conn: aiosqlite.Connection, *, account_id: str, ttl_minutes: int = 30) -> str:
    from datetime import timedelta

    raw = new_link_code()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    exp = now + timedelta(minutes=max(5, int(ttl_minutes)))
    await conn.execute(
        """
        INSERT INTO link_tokens (code_hash, account_id, created_at, expires_at)
        VALUES (?, ?, ?, ?)
        """,
        (hash_token(raw), account_id, now.isoformat(), exp.isoformat()),
    )
    await conn.commit()
    return raw


async def consume_link_token(
    conn: aiosqlite.Connection,
    *,
    code: str,
    telegram_user_id: int,
) -> tuple[str, str, int | None]:
    """
    Bind telegram to web account.
    Returns (status, message_or_account_id, from_vpn_subject).
    status: ok|expired|used|conflict|not_found|merged
    """
    from bot.services import users_repo

    cur = await conn.execute(
        "SELECT * FROM link_tokens WHERE code_hash = ?",
        (hash_token(code),),
    )
    tok = await cur.fetchone()
    if not tok:
        return "not_found", "Код привязки не найден или устарел.", None
    if tok["used_at"]:
        return "used", "Этот код уже использован.", None
    now = datetime.now(timezone.utc).replace(microsecond=0)
    try:
        exp = datetime.fromisoformat(str(tok["expires_at"]).replace("Z", "+00:00"))
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if now > exp:
            return "expired", "Срок кода истёк. Создайте новый в личном кабинете на сайте.", None
    except Exception:
        return "expired", "Срок кода истёк.", None

    account_id = str(tok["account_id"])
    web_acc = await get_account_by_id(conn, account_id)
    if not web_acc:
        return "not_found", "Аккаунт сайта не найден.", None

    tid = int(telegram_user_id)
    from_subject = int(web_acc["vpn_subject_id"])
    existing_tg = await get_account_by_telegram(conn, tid)

    await users_repo.upsert_user(conn, user_id=tid, username=None, first_name=None)

    if existing_tg and str(existing_tg["account_id"]) != account_id:
        winner = str(existing_tg["account_id"])
        await conn.execute(
            """
            UPDATE accounts SET merged_into_account_id = ?, telegram_user_id = NULL
            WHERE account_id = ?
            """,
            (winner, account_id),
        )
        await conn.execute(
            "UPDATE orders SET account_id = ? WHERE account_id = ?",
            (winner, account_id),
        )
        await conn.execute(
            """
            UPDATE link_tokens SET used_at = ?, used_by_telegram_id = ?
            WHERE code_hash = ?
            """,
            (now.isoformat(), tid, hash_token(code)),
        )
        await conn.commit()
        try:
            from bot.services.vpn_referral_repo import reassign_referral_owner_on_telegram_link

            await reassign_referral_owner_on_telegram_link(
                conn, from_subject_id=from_subject, to_telegram_user_id=tid
            )
        except Exception:
            pass
        return "merged", winner, from_subject

    await conn.execute(
        "UPDATE accounts SET telegram_user_id = ?, created_via = 'link' WHERE account_id = ?",
        (tid, account_id),
    )
    await conn.execute(
        """
        UPDATE link_tokens SET used_at = ?, used_by_telegram_id = ?
        WHERE code_hash = ?
        """,
        (now.isoformat(), tid, hash_token(code)),
    )
    await conn.commit()
    try:
        from bot.services.vpn_referral_repo import reassign_referral_owner_on_telegram_link

        await reassign_referral_owner_on_telegram_link(
            conn, from_subject_id=from_subject, to_telegram_user_id=tid
        )
    except Exception:
        pass
    return "ok", account_id, from_subject


async def set_session_secret(conn: aiosqlite.Connection, account_id: str, raw_secret: str) -> None:
    await conn.execute(
        "UPDATE accounts SET session_secret_hash = ? WHERE account_id = ?",
        (hash_token(raw_secret), account_id),
    )
    await conn.commit()


async def verify_session_secret(conn: aiosqlite.Connection, account_id: str, raw_secret: str) -> bool:
    acc = await get_account_by_id(conn, account_id)
    if not acc or not acc.get("session_secret_hash"):
        return False
    return str(acc["session_secret_hash"]) == hash_token(raw_secret)


async def get_account_by_nickname(conn: aiosqlite.Connection, nickname: str) -> dict[str, Any] | None:
    from bot.services.web_nickname import normalize_nickname

    nick = normalize_nickname(nickname)
    if not nick:
        return None
    cur = await conn.execute(
        """
        SELECT * FROM accounts
        WHERE lower(nickname) = lower(?) AND merged_into_account_id IS NULL
        LIMIT 1
        """,
        (nick,),
    )
    row = await cur.fetchone()
    return dict(row) if row else None


async def set_nickname_with_access_code(
    conn: aiosqlite.Connection,
    *,
    account_id: str,
    nickname: str,
) -> tuple[str, str | None]:
    """
    Set nickname once (immutable after set). Returns (nickname, access_code_once).
    access_code_once is only returned when first setting (hash was empty).
    """
    from bot.services.web_nickname import (
        hash_access_code,
        new_access_code,
        normalize_nickname,
        validate_nickname,
    )

    nick = normalize_nickname(nickname)
    err = validate_nickname(nick)
    if err:
        raise ValueError(err)
    acc = await get_account_by_id(conn, account_id)
    if not acc:
        raise ValueError("account_missing")
    existing = (acc.get("nickname") or "").strip()
    if existing:
        if existing.lower() != nick.lower():
            raise ValueError("nickname_locked")
        return existing, None
    taken = await get_account_by_nickname(conn, nick)
    if taken and str(taken["account_id"]) != account_id:
        raise ValueError("nickname_taken")
    code = new_access_code()
    now = _utc_now()
    await conn.execute(
        """
        UPDATE accounts
        SET nickname = ?, access_code_hash = ?, nickname_set_at = ?
        WHERE account_id = ? AND (nickname IS NULL OR TRIM(nickname) = '')
        """,
        (nick, hash_access_code(code), now, account_id),
    )
    await conn.commit()
    return nick, code


async def login_with_nickname_code(
    conn: aiosqlite.Connection,
    *,
    nickname: str,
    access_code: str,
) -> tuple[dict[str, Any], str]:
    """Returns (account, new_session_secret)."""
    from bot.services.web_nickname import access_code_matches, normalize_nickname

    nick = normalize_nickname(nickname)
    acc = await get_account_by_nickname(conn, nick)
    if not acc:
        raise ValueError("invalid_credentials")
    if not access_code_matches(access_code, acc.get("access_code_hash")):
        raise ValueError("invalid_credentials")
    secret = new_access_token()
    await set_session_secret(conn, str(acc["account_id"]), secret)
    fresh = await get_account_by_id(conn, str(acc["account_id"]))
    return fresh or acc, secret


async def find_accounts_orders_by_nickname(
    conn: aiosqlite.Connection, nickname: str, *, limit: int = 20
) -> dict[str, Any]:
    from bot.services.web_nickname import normalize_nickname

    nick = normalize_nickname(nickname)
    acc = await get_account_by_nickname(conn, nick)
    orders: list[dict[str, Any]] = []
    if acc:
        cur = await conn.execute(
            """
            SELECT id, status, product_id, product_title, rub_after_discounts, source,
                   account_id, user_id, buyer_nickname, created_at, referrer_id
            FROM orders
            WHERE lower(COALESCE(buyer_nickname,'')) = lower(?)
               OR account_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (nick, str(acc["account_id"]), int(limit)),
        )
    else:
        cur = await conn.execute(
            """
            SELECT id, status, product_id, product_title, rub_after_discounts, source,
                   account_id, user_id, buyer_nickname, created_at, referrer_id
            FROM orders
            WHERE lower(COALESCE(buyer_nickname,'')) = lower(?)
            ORDER BY id DESC
            LIMIT ?
            """,
            (nick, int(limit)),
        )
    rows = await cur.fetchall()
    for r in rows:
        orders.append(dict(r))
    return {"account": acc, "orders": orders}
