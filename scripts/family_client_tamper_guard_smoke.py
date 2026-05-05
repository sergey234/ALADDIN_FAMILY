#!/usr/bin/env python3
"""
Static contract smoke: client-side quota tampering must not affect server decision.

This verifies source contracts in code:
- Add request model has no client-provided `max/used` quota fields
- Server add/join decisions are based on server-side owner level + DB COUNT(*)
- Gate checks happen before INSERT into family_members
"""

from __future__ import annotations

import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
FAMILY_ROUTER = ROOT / "app/routers/family.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    body = FAMILY_ROUTER.read_text(encoding="utf-8")

    add_model_match = re.search(
        r"class AddFamilyMemberRequest\(BaseModel\):(?P<section>.*?)(?:\nclass |\n@router\.|\Z)",
        body,
        flags=re.S,
    )
    require(add_model_match is not None, "AddFamilyMemberRequest model not found")
    add_model = add_model_match.group("section")
    forbidden_client_quota_fields = ["max", "used", "familyRosterMax", "familyRosterUsed", "quota"]
    for fld in forbidden_client_quota_fields:
        require(fld not in add_model, f"AddFamilyMemberRequest must not accept client quota field `{fld}`")

    require("_owner_subscription_level_for_family(" in body, "Server-side owner subscription level check missing")
    require("_count_family_members(" in body, "Server-side family COUNT(*) check missing")
    require("max_family_slots_for_subscription_level(" in body, "Server-side roster max mapper missing")

    require("current_slots >= max_slots" in body, "Roster full guard condition missing")
    require('raise HTTPException(status_code=409, detail="family_roster_full")' in body, "Roster full 409 contract missing")

    require("_acquire_family_roster_write_lock(db, str(family_id))" in body, "Missing race lock in /add path")
    require("_acquire_family_roster_write_lock(db, canonical_fid)" in body, "Missing race lock in /join path")

    add_route = re.search(
        r'@router\.post\("/add".*?async def add_family_member\((?P<section>.*?)(?:\n@router\.post\("/join"|$)',
        body,
        flags=re.S,
    )
    require(add_route is not None, "/add route section not found")
    add_section = add_route.group("section")
    add_guard_idx = add_section.find("current_slots >= max_slots")
    add_insert_idx = add_section.find("INSERT INTO family_members")
    require(
        add_guard_idx != -1 and add_insert_idx != -1 and add_guard_idx < add_insert_idx,
        "Add guard must run before INSERT",
    )

    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError) as exc:
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
