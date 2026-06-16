#!/usr/bin/env python3
"""Static guard: device JWT must map to users.id before family PG writes."""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
AUTH_ROUTER = ROOT / "app/routers/auth_router.py"
FAMILY_ROUTER = ROOT / "app/routers/family.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_auth_router(body: str) -> None:
    require("_ensure_db_user_for_device" in body, "auth_router: _ensure_db_user_for_device missing")
    require("_PG_INT_MAX" in body, "auth_router: _PG_INT_MAX constant missing")
    require(
        "db_user_id = _ensure_db_user_for_device" in body
        or "_ensure_db_user_for_device(db" in body,
        "register_device must call _ensure_db_user_for_device",
    )
    require(
        not re.search(
            r"pseudo_user_id\s*=\s*int\(hashlib\.sha256",
            body,
        ),
        "auth_router: legacy pseudo_user_id from SHA256 must not be used in register_device",
    )


def check_family_router(body: str) -> None:
    require("_PG_INT_MAX" in body, "family.py: _PG_INT_MAX constant missing")
    require(
        "_lookup_or_create_user_id_for_device" in body
        or "claim_device_id" in body,
        "family.py: device_id → users.id resolution missing",
    )
    require(
        "parsed > _PG_INT_MAX" in body or "uid > _PG_INT_MAX" in body,
        "family.py: guard for oversized numeric JWT sub missing",
    )
    require("INSERT INTO families" in body and "owner_user_id" in body, "family create persist missing")


def main() -> int:
    auth_body = AUTH_ROUTER.read_text(encoding="utf-8")
    family_body = FAMILY_ROUTER.read_text(encoding="utf-8")
    check_auth_router(auth_body)
    check_family_router(family_body)
    print("family_auth_static_guard: OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
