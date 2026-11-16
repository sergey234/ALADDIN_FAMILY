#!/usr/bin/env python3
"""Smoke: trial register → create family → stats max=3 → add to 3 → 4th 409 with roster_max."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
import uuid
from typing import Any

BASE = "http://127.0.0.1:8002"


def req(method: str, path: str, body: dict | None = None, token: str | None = None) -> tuple[int, Any]:
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=25) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"raw": raw}
        return exc.code, parsed


def main() -> int:
    device = f"ALADDIN-TRIAL-ROSTER-SMOKE-{uuid.uuid4().hex[:10]}"
    code, reg = req(
        "POST",
        "/api/auth/register-device-trial",
        {
            "device_id": device,
            "device_type": "ios",
            "trial_info": {"duration_days": 14},
        },
    )
    token = (reg or {}).get("token")
    if code != 200 or not token:
        print("FAIL register-device-trial", code, reg)
        return 1
    print("OK register-device-trial device", device)

    code, created = req(
        "POST",
        "/api/family/create",
        {"role": "parent", "age_group": "adult", "personal_letter": "T", "device_type": "ios"},
        token=token,
    )
    if code not in (200, 201):
        print("FAIL create", code, created)
        return 1
    family_id = (created or {}).get("familyId") or (created or {}).get("family_id")
    print("OK create", family_id)

    code, stats = req("GET", "/api/family/stats", token=token)
    if code != 200:
        print("FAIL stats", code, stats)
        return 1
    mx = int(stats.get("familyRosterMax") or 0)
    tier = stats.get("ownerSubscriptionTier")
    used = int(stats.get("familyRosterUsed") or stats.get("totalMembers") or 0)
    print("STATS", {"used": used, "max": mx, "tier": tier})
    if mx != 3 or str(tier).lower() != "trial":
        print("FAIL expected trial max=3 got", mx, tier)
        return 1

    # Add until 3 members total
    letters = ["A", "B", "C", "D"]
    for i, letter in enumerate(letters):
        code, body = req(
            "POST",
            "/api/family/add",
            {"name": f"CHILD {letter}", "role": "child", "familyId": family_id},
            token=token,
        )
        members_now = used + i + 1
        if members_now <= 3:
            if code not in (200, 201):
                print("FAIL add within limit", members_now, code, body)
                return 1
            print("OK add", letter, "→", members_now)
        else:
            if code != 409:
                print("FAIL expected 409 on 4th", code, body)
                return 1
            detail = body.get("detail") if isinstance(body, dict) else body
            print("OK 409 detail", detail)
            if isinstance(detail, dict):
                if detail.get("error_code") != "family_roster_full":
                    print("FAIL error_code", detail)
                    return 1
                if int(detail.get("roster_max") or 0) != 3:
                    print("FAIL roster_max", detail)
                    return 1
                if int(detail.get("roster_used") or 0) < 3:
                    print("FAIL roster_used", detail)
                    return 1
            elif "family_roster_full" not in str(detail):
                print("FAIL detail string", detail)
                return 1
            break
    else:
        print("FAIL never hit 409")
        return 1

    # Owner 1274 post-heal sanity via SQL-less stats needs their token — skip.
    print("PASS trial roster smoke")
    return 0


if __name__ == "__main__":
    sys.exit(main())
