"""One last place-signal and one last shared point per family member.

No route. No minute-by-minute track. A new row for the same person replaces the old one.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.database.database import engine
from app.services.antifake_family_store import (
    get_member_role,
    resolve_primary_family_id,
)
from app.services.family_where_phone_rules import map_url_ok, rows_for_viewer

_CREATE = """
CREATE TABLE IF NOT EXISTS family_where_phone_signal (
    family_id VARCHAR(64) NOT NULL,
    member_id VARCHAR(64) NOT NULL,
    user_id BIGINT NOT NULL,
    display_name VARCHAR(80) NOT NULL DEFAULT '',
    place_name VARCHAR(120) NOT NULL,
    is_arrival BOOLEAN NOT NULL,
    happened_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (family_id, member_id)
);
CREATE TABLE IF NOT EXISTS family_where_phone_point (
    family_id VARCHAR(64) NOT NULL,
    member_id VARCHAR(64) NOT NULL,
    user_id BIGINT NOT NULL,
    display_name VARCHAR(80) NOT NULL DEFAULT '',
    map_url VARCHAR(240) NOT NULL,
    happened_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (family_id, member_id)
);
"""


def ensure_tables() -> None:
    with engine.begin() as conn:
        for stmt in _CREATE.strip().split(";"):
            line = stmt.strip()
            if line:
                conn.execute(text(line))


def _member_row(user_id: int, family_id: str) -> Optional[Dict[str, Any]]:
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT id, name
                FROM family_members
                WHERE family_id = :fid AND user_id = :uid
                ORDER BY id DESC
                LIMIT 1
                """
            ),
            {"fid": family_id, "uid": int(user_id)},
        ).mappings().first()
    return dict(row) if row else None


def _clean_name(display_name: str, fallback: str) -> str:
    name = (display_name or "").strip() or (fallback or "").strip() or "Участник"
    return name[:80]


def upsert_signal(
    *,
    user_id: int,
    display_name: str,
    place_name: str,
    is_arrival: bool,
) -> Dict[str, Any]:
    ensure_tables()
    family_id = resolve_primary_family_id(int(user_id))
    if not family_id:
        return {"ok": False, "error": "no_family"}
    member = _member_row(int(user_id), family_id)
    if not member:
        return {"ok": False, "error": "no_member"}

    place = (place_name or "").strip()[:120]
    if not place:
        return {"ok": False, "error": "no_place"}

    now = datetime.now(timezone.utc)
    member_id = str(member["id"])
    name = _clean_name(display_name, str(member.get("name") or ""))
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO family_where_phone_signal (
                    family_id, member_id, user_id, display_name,
                    place_name, is_arrival, happened_at
                ) VALUES (
                    :fid, :mid, :uid, :name, :place, :arrival, :now
                )
                ON CONFLICT (family_id, member_id) DO UPDATE SET
                    display_name = EXCLUDED.display_name,
                    place_name = EXCLUDED.place_name,
                    is_arrival = EXCLUDED.is_arrival,
                    happened_at = EXCLUDED.happened_at
                """
            ),
            {
                "fid": family_id,
                "mid": member_id,
                "uid": int(user_id),
                "name": name,
                "place": place,
                "arrival": bool(is_arrival),
                "now": now,
            },
        )
    return {"ok": True, "member_id": member_id, "family_id": family_id}


def upsert_point(
    *,
    user_id: int,
    display_name: str,
    map_url: str,
) -> Dict[str, Any]:
    if not map_url_ok(map_url):
        return {"ok": False, "error": "bad_map_url"}
    ensure_tables()
    family_id = resolve_primary_family_id(int(user_id))
    if not family_id:
        return {"ok": False, "error": "no_family"}
    member = _member_row(int(user_id), family_id)
    if not member:
        return {"ok": False, "error": "no_member"}

    now = datetime.now(timezone.utc)
    member_id = str(member["id"])
    name = _clean_name(display_name, str(member.get("name") or ""))
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO family_where_phone_point (
                    family_id, member_id, user_id, display_name, map_url, happened_at
                ) VALUES (
                    :fid, :mid, :uid, :name, :url, :now
                )
                ON CONFLICT (family_id, member_id) DO UPDATE SET
                    display_name = EXCLUDED.display_name,
                    map_url = EXCLUDED.map_url,
                    happened_at = EXCLUDED.happened_at
                """
            ),
            {
                "fid": family_id,
                "mid": member_id,
                "uid": int(user_id),
                "name": name,
                "url": map_url.strip(),
                "now": now,
            },
        )
    return {"ok": True, "member_id": member_id, "family_id": family_id}


def _iso(value: Any) -> Optional[str]:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return None


def list_where_phone(*, user_id: int) -> Dict[str, Any]:
    """Last signal and last point for the caller's family. One row per person."""
    ensure_tables()
    family_id = resolve_primary_family_id(int(user_id))
    if not family_id:
        return {"ok": True, "signals": [], "points": []}

    role = get_member_role(int(user_id), family_id)
    own = _member_row(int(user_id), family_id)
    own_id = str(own["id"]) if own else ""

    with engine.connect() as conn:
        signal_rows = conn.execute(
            text(
                """
                SELECT member_id, display_name, place_name, is_arrival, happened_at
                FROM family_where_phone_signal
                WHERE family_id = :fid
                ORDER BY happened_at DESC
                LIMIT 40
                """
            ),
            {"fid": family_id},
        ).mappings().all()
        point_rows = conn.execute(
            text(
                """
                SELECT member_id, display_name, map_url, happened_at
                FROM family_where_phone_point
                WHERE family_id = :fid
                ORDER BY happened_at DESC
                LIMIT 40
                """
            ),
            {"fid": family_id},
        ).mappings().all()

    signals: List[Dict[str, Any]] = []
    for row in signal_rows:
        signals.append(
            {
                "member_id": str(row["member_id"]),
                "display_name": str(row.get("display_name") or ""),
                "place_name": str(row.get("place_name") or ""),
                "is_arrival": bool(row.get("is_arrival")),
                "happened_at": _iso(row.get("happened_at")),
            }
        )
    points: List[Dict[str, Any]] = []
    for row in point_rows:
        points.append(
            {
                "member_id": str(row["member_id"]),
                "display_name": str(row.get("display_name") or ""),
                "map_url": str(row.get("map_url") or ""),
                "happened_at": _iso(row.get("happened_at")),
            }
        )

    return {
        "ok": True,
        "signals": rows_for_viewer(signals, role, own_id),
        "points": rows_for_viewer(points, role, own_id),
    }
