#!/usr/bin/env python3
"""GATE-F family smoke — register-device (overflow-prone) → create → members → add.

Catches regressions like pseudo JWT user_id > PostgreSQL INTEGER (family_create_error).
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

BASE = os.environ.get("FAMILY_SMOKE_BASE", "http://127.0.0.1:8002").rstrip("/")
DEFAULT_DEVICE_ID = os.environ.get(
    "FAMILY_SMOKE_DEVICE_ID",
    "ALADDIN-FAMILY-SMOKE-OVERFLOW-v1",
)
SKIP_ADD = os.environ.get("FAMILY_SMOKE_SKIP_ADD", "").strip() in ("1", "true", "yes")
TIMESTAMP_FILE = os.environ.get(
    "FAMILY_SMOKE_TIMESTAMP_FILE",
    "/var/lib/aladdin/family_smoke_last_success.timestamp",
)
PG_INT_MAX = 2_147_483_647


def _legacy_pseudo_would_overflow(device_id: str) -> int:
    return int(hashlib.sha256(device_id.encode()).hexdigest()[:8], 16)


def _request(
    method: str,
    path: str,
    body: dict | None = None,
    token: str | None = None,
    extra_headers: dict | None = None,
    timeout: int = 25,
) -> tuple[int, Any, dict[str, str]]:
    headers: dict[str, str] = {"Content-Type": "application/json", "Accept": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    resp_headers: dict[str, str] = {}
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp_headers = {k: v for k, v in resp.headers.items()}
            raw = resp.read().decode()
            parsed: Any = json.loads(raw) if raw else {}
            return resp.status, parsed, resp_headers
    except urllib.error.HTTPError as exc:
        resp_headers = {k: v for k, v in exc.headers.items()} if exc.headers else {}
        raw = exc.read().decode()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"raw": raw}
        return exc.code, parsed, resp_headers


def _jwt_payload_unverified(token: str) -> dict[str, Any]:
    parts = token.split(".")
    if len(parts) < 2:
        return {}
    pad = "=" * (-len(parts[1]) % 4)
    try:
        raw = base64.urlsafe_b64decode(parts[1] + pad)
        data = json.loads(raw.decode())
        return data if isinstance(data, dict) else {}
    except (ValueError, json.JSONDecodeError):
        return {}


def _numeric_claim(payload: dict[str, Any], *keys: str) -> int | None:
    for key in keys:
        val = payload.get(key)
        if isinstance(val, int):
            return val
        if isinstance(val, str) and val.strip().isdigit():
            return int(val.strip())
    return None


def _write_success_timestamp() -> None:
    path = TIMESTAMP_FILE
    try:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"))
    except OSError as exc:
        print(f"WARN: could not write timestamp file {path}: {exc}", file=sys.stderr)


def main() -> int:
    failures: list[str] = []
    steps: dict[str, Any] = {}
    device_id = DEFAULT_DEVICE_ID

    pseudo = _legacy_pseudo_would_overflow(device_id)
    steps["device_id"] = device_id
    steps["legacy_pseudo_would_be"] = pseudo
    steps["legacy_pseudo_overflows_pg_int"] = pseudo > PG_INT_MAX
    if pseudo <= PG_INT_MAX:
        failures.append(
            f"smoke device_id must produce legacy pseudo > {PG_INT_MAX} (got {pseudo})"
        )

    code, health, _ = _request("GET", "/api/health")
    steps["health_status"] = code
    if code != 200:
        failures.append(f"S0 health expected 200 got {code}: {health}")

    code, reg, _ = _request(
        "POST",
        "/api/auth/register-device",
        {"deviceId": device_id, "deviceType": "ios"},
    )
    steps["register_device_status"] = code
    token = reg.get("access_token") if isinstance(reg, dict) else None
    if code != 200 or not token:
        failures.append(f"S1 register-device expected 200+token got {code}: {reg}")
        report = {"pass": False, "failures": failures, "steps": steps}
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 1

    payload = _jwt_payload_unverified(token)
    steps["jwt_sub"] = payload.get("sub")
    steps["jwt_device_id"] = payload.get("device_id")
    uid = _numeric_claim(payload, "user_id", "id", "sub")
    steps["jwt_resolved_numeric_id"] = uid
    if uid is None:
        failures.append(f"S1 JWT missing numeric user_id/sub: {payload}")
    elif uid > PG_INT_MAX:
        failures.append(
            f"S1 JWT user_id {uid} > PG_INT_MAX — register-device regression (pseudo id in token)"
        )

    create_body = {
        "role": "parent",
        "age_group": "24-55",
        "personal_letter": "Z",
        "device_type": "smartphone",
    }
    code, created, _ = _request("POST", "/api/family/create", create_body, token=token)
    steps["create_family_status"] = code
    family_id = created.get("family_id") if isinstance(created, dict) else None
    creator_member_id = created.get("creator_member_id") if isinstance(created, dict) else None
    steps["family_id"] = family_id
    steps["creator_member_id"] = creator_member_id

    if code != 200:
        failures.append(f"S2 family/create expected 200 got {code}: {created}")
    else:
        if not isinstance(family_id, str) or not family_id.startswith("FAM_"):
            failures.append(f"S2 family_id invalid: {family_id}")
        if not isinstance(creator_member_id, str) or not creator_member_id.startswith("MEM_"):
            failures.append(f"S2 creator_member_id invalid: {creator_member_id}")

    if family_id and token:
        code, members, mem_headers = _request(
            "GET",
            "/api/family/members",
            token=token,
            extra_headers={"X-Family-Id": family_id},
        )
        steps["members_status"] = code
        steps["x_resolved_family_id"] = mem_headers.get("X-Resolved-Family-Id")
        if code != 200:
            failures.append(f"S3 members expected 200 got {code}: {members}")
        elif isinstance(members, list):
            steps["members_count"] = len(members)
            if len(members) < 1:
                failures.append(f"S3 members expected >=1 got {len(members)}")
        else:
            failures.append(f"S3 members expected JSON array got {type(members).__name__}: {members}")

        code, stats, _ = _request(
            "GET",
            "/api/family/stats",
            token=token,
            extra_headers={"X-Family-Id": family_id},
        )
        steps["stats_status"] = code
        if code != 200:
            failures.append(f"S5 stats expected 200 got {code}: {stats}")
        elif isinstance(stats, dict):
            used = int(stats.get("familyRosterUsed") or 0)
            max_slots = int(stats.get("familyRosterMax") or 0)
            total = int(stats.get("totalMembers") or 0)
            steps["stats_totalMembers"] = total
            steps["stats_roster_used"] = used
            steps["stats_roster_max"] = max_slots
            if max_slots > 0 and used > max_slots:
                failures.append(f"S5 roster used {used} > max {max_slots}")
            if total < 1:
                failures.append(f"S5 totalMembers expected >=1 got {total}")

        if not SKIP_ADD:
            unique = f"SMOKE_FAM_{int(time.time())}"
            code, added, _ = _request(
                "POST",
                "/api/family/add",
                {"name": unique, "role": "child", "familyId": family_id},
                token=token,
                extra_headers={"Idempotency-Key": f"family-smoke-add-{unique}"},
            )
            steps["add_member_status"] = code
            if code not in (200, 409):
                failures.append(f"S4 add expected 200 or 409 got {code}: {added}")
            elif code == 409:
                detail = added.get("detail") if isinstance(added, dict) else str(added)
                if "family_roster_full" not in str(detail):
                    failures.append(f"S4 add 409 detail unexpected: {detail}")

    passed = len(failures) == 0
    if passed:
        _write_success_timestamp()

    report = {"pass": passed, "failures": failures, "steps": steps}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
