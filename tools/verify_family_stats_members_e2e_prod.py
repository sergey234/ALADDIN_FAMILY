#!/usr/bin/env python3
"""
Prod-only helper: pick a real family_members.user_id (prefer non-owner), mint JWT like auth_router,
compare GET /api/family/stats totalMembers vs len(GET /api/family/members).

Run on server:
  cd /opt/aladdin-backend && PYTHONPATH=/opt/aladdin-backend ./venv/bin/python3 tools/verify_family_stats_members_e2e_prod.py

Or pass BASE_URL env (default http://127.0.0.1:8002).
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import timedelta

from sqlalchemy import text

from app.database.database import SessionLocal
from app.routers.auth_router import create_access_token


def http_get_json(url: str, token: str) -> tuple[int, object]:
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            body = r.read().decode("utf-8", errors="replace")
            return r.status, json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = body
        return e.code, parsed


def main() -> int:
    base = os.environ.get("ALADDIN_VERIFY_BASE_URL", "http://127.0.0.1:8002").rstrip("/")

    db = SessionLocal()
    try:
        non_owner_count = db.execute(
            text(
                """
                SELECT COUNT(*)::int
                FROM family_members fm
                JOIN families f ON f.id = fm.family_id
                WHERE fm.user_id IS NOT NULL
                  AND fm.user_id IS DISTINCT FROM f.owner_user_id
                """
            )
        ).scalar()
        print(
            json.dumps(
                {
                    "db_non_owner_members_with_user_id": int(non_owner_count or 0),
                    "note": "E2E for non-owner requires at least one such row in PostgreSQL.",
                },
                ensure_ascii=False,
            )
        )

        row = db.execute(
            text(
                """
                SELECT fm.user_id, fm.family_id::text, f.owner_user_id
                FROM family_members fm
                JOIN families f ON f.id = fm.family_id
                WHERE fm.user_id IS NOT NULL
                  AND fm.user_id IS DISTINCT FROM f.owner_user_id
                ORDER BY fm.updated_at DESC NULLS LAST, fm.id DESC
                LIMIT 1
                """
            )
        ).fetchone()

        picked = "non_owner"
        if not row:
            picked = "fallback_any_member"
            row = db.execute(
                text(
                    """
                    SELECT fm.user_id, fm.family_id::text, f.owner_user_id
                    FROM family_members fm
                    JOIN families f ON f.id = fm.family_id
                    WHERE fm.user_id IS NOT NULL
                    ORDER BY fm.updated_at DESC NULLS LAST, fm.id DESC
                    LIMIT 1
                    """
                )
            ).fetchone()

        if not row:
            print("RESULT=no_family_members_rows")
            return 2

        uid = int(row[0])
        family_id = str(row[1]).strip()
        owner_uid = int(row[2]) if row[2] is not None else None
        is_non_owner = owner_uid is not None and uid != owner_uid

        token = create_access_token(
            {
                "user_id": uid,
                "id": uid,
                "sub": str(uid),
            },
            expires_delta=timedelta(hours=1),
        )

        qfam = urllib.parse.quote(family_id, safe="")
        st_stats, stats = http_get_json(f"{base}/api/family/stats", token)
        st_mem_q, members_q = http_get_json(f"{base}/api/family/members?familyId={qfam}", token)
        st_mem_plain, members_plain = http_get_json(f"{base}/api/family/members", token)

        print(
            json.dumps(
                {
                    "picked_row": picked,
                    "user_id": uid,
                    "family_id": family_id,
                    "owner_user_id": owner_uid,
                    "is_non_owner_member": is_non_owner,
                    "http_stats": st_stats,
                    "http_members_query": st_mem_q,
                    "http_members_plain": st_mem_plain,
                },
                ensure_ascii=False,
            )
        )

        if st_stats != 200:
            print("RESULT=stats_http_error")
            return 1
        if st_mem_q != 200:
            print("RESULT=members_http_error_query")
            return 1
        if st_mem_plain != 200:
            print("RESULT=members_http_error_plain")
            return 1
        if not isinstance(stats, dict) or not isinstance(members_q, list):
            print("RESULT=unexpected_payload_shape")
            return 1
        if not isinstance(members_plain, list):
            print("RESULT=unexpected_payload_shape_plain")
            return 1

        tm = stats.get("totalMembers")
        lm_q = len(members_q)
        lm_p = len(members_plain)
        ok_q = tm == lm_q
        ok_p = tm == lm_p
        ok = ok_q and ok_p
        print(
            json.dumps(
                {
                    "totalMembers": tm,
                    "members_len_with_familyId_query": lm_q,
                    "members_len_plain": lm_p,
                    "MATCH_query": ok_q,
                    "MATCH_plain": ok_p,
                    "MATCH": ok,
                },
                ensure_ascii=False,
            )
        )
        print("RESULT=" + ("OK" if ok else "MISMATCH"))
        return 0 if ok else 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
