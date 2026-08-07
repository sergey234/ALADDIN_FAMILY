"""FIN F8: runtime overrides for fee% / Fragment USDT (DB), без правки shared/.env.

Приоритет: значение из `fin_settings` → иначе env/Settings.
Смена % влияет только на **новые** snapshot (write_profit_snapshot без force).
"""

from __future__ import annotations

from typing import Any

import aiosqlite

from bot.config import Settings

# short_key → Settings attribute
FIN_ATTR_BY_KEY: dict[str, str] = {
    "fee_lava_card": "fee_lava_card_percent",
    "fee_sbp": "fee_sbp_percent",
    "fee_crypto": "fee_crypto_bot_percent",
    "fee_xrocket": "fee_xrocket_percent",
    "fragment_star": "fragment_star_usdt",
    "fragment_1m": "fragment_premium_1m_usdt",
    "fragment_3m": "fragment_premium_3m_usdt",
    "fragment_6m": "fragment_premium_6m_usdt",
    "fragment_12m": "fragment_premium_12m_usdt",
    "rent_monthly": "vpn_rent_monthly_rub",
}

# aliases accepted by /admin_fin_set
_ALIASES: dict[str, str] = {
    "lava": "fee_lava_card",
    "lava_card": "fee_lava_card",
    "sbp": "fee_sbp",
    "crypto": "fee_crypto",
    "crypto_bot": "fee_crypto",
    "xrocket": "fee_xrocket",
    "star": "fragment_star",
    "stars": "fragment_star",
    "1m": "fragment_1m",
    "prem1m": "fragment_1m",
    "premium_1m": "fragment_1m",
    "3m": "fragment_3m",
    "6m": "fragment_6m",
    "12m": "fragment_12m",
    "rent": "rent_monthly",
}


def normalize_fin_key(raw: str) -> str | None:
    t = (raw or "").strip().lower().replace("-", "_").replace("%", "")
    if t in FIN_ATTR_BY_KEY:
        return t
    return _ALIASES.get(t)


async def ensure_fin_settings_table(conn: aiosqlite.Connection) -> None:
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS fin_settings (
            key TEXT PRIMARY KEY NOT NULL,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_by INTEGER
        )
        """
    )
    await conn.commit()


async def get_all(conn: aiosqlite.Connection) -> dict[str, float]:
    await ensure_fin_settings_table(conn)
    cur = await conn.execute("SELECT key, value FROM fin_settings")
    rows = await cur.fetchall()
    out: dict[str, float] = {}
    for r in rows:
        k = str(r[0] if not hasattr(r, "keys") else r["key"]).strip().lower()
        if k not in FIN_ATTR_BY_KEY:
            continue
        try:
            out[k] = float(r[1] if not hasattr(r, "keys") else r["value"])
        except (TypeError, ValueError):
            continue
    return out


async def set_value(
    conn: aiosqlite.Connection,
    key: str,
    value: float,
    *,
    updated_by: int | None = None,
) -> str:
    """Set override. Returns canonical key. Raises ValueError on bad key."""
    canon = normalize_fin_key(key)
    if canon is None:
        raise ValueError(f"unknown_key:{key}")
    await ensure_fin_settings_table(conn)
    await conn.execute(
        """
        INSERT INTO fin_settings(key, value, updated_at, updated_by)
        VALUES (?, ?, datetime('now'), ?)
        ON CONFLICT(key) DO UPDATE SET
          value = excluded.value,
          updated_at = excluded.updated_at,
          updated_by = excluded.updated_by
        """,
        (canon, str(float(value)), updated_by),
    )
    await conn.commit()
    return canon


async def clear_key(conn: aiosqlite.Connection, key: str) -> str | None:
    """Remove override → fall back to env. Returns canon key or None."""
    canon = normalize_fin_key(key)
    if canon is None:
        return None
    await ensure_fin_settings_table(conn)
    await conn.execute("DELETE FROM fin_settings WHERE key = ?", (canon,))
    await conn.commit()
    return canon


def apply_overrides(settings: Settings, overrides: dict[str, float]) -> Settings:
    if not overrides:
        return settings
    update: dict[str, Any] = {}
    for k, v in overrides.items():
        attr = FIN_ATTR_BY_KEY.get(k)
        if attr:
            update[attr] = float(v)
    if not update:
        return settings
    return settings.model_copy(update=update)


async def settings_with_overrides(conn: aiosqlite.Connection, settings: Settings) -> Settings:
    return apply_overrides(settings, await get_all(conn))


def premium_1m_cogs_unset(settings: Any) -> bool:
    """True если закуп Premium 1м не задан (TBD)."""
    try:
        return float(getattr(settings, "fragment_premium_1m_usdt", 0) or 0) <= 0.000001
    except (TypeError, ValueError):
        return True


def format_keys_help() -> str:
    keys = ", ".join(sorted(FIN_ATTR_BY_KEY.keys()))
    return (
        f"Ключи: <code>{keys}</code>\n"
        "Примеры:\n"
        "<code>/admin_fin_set fee_sbp 3.4</code>\n"
        "<code>/admin_fin_set fragment_1m 4.99</code>\n"
        "<code>/admin_fin_set fragment_1m clear</code> — сброс на env\n"
        "<code>/admin_fin_show</code>"
    )
