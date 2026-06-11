#!/usr/bin/env python3
"""B0-07: protection settings L2 round-trip smoke."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

BASE = "https://aladdin-ai.ru"
CATEGORIES = (
    "cyberThreats",
    "fraud",
    "childThreats",
    "dataLeaks",
    "deepfakes",
    "internetThreats",
    "mobileThreats",
    "familyThreats",
    "iotThreats",
)


def _post(path: str, body: dict, token: str) -> tuple[int, dict]:
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"error": raw}


def _get(path: str, token: str) -> tuple[int, dict]:
    req = urllib.request.Request(
        f"{BASE}{path}",
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status, json.loads(resp.read().decode())


def main() -> int:
    _, reg = _post("/api/auth/register-device", {"deviceId": "protection-l2-smoke"}, "")
    token = reg.get("token") or reg.get("access_token")
    if not token:
        print("FAIL: no jwt", reg)
        return 1

    enabled = {c: True for c in CATEGORIES}
    code, upd = _post(
        "/api/protection/settings",
        {"enabledCategories": enabled, "globalLevel": 95},
        token,
    )
    if code != 200 or not upd.get("success", True):
        print("FAIL post settings", code, upd)
        return 1

    code, got = _get("/api/protection/settings", token)
    cats = got.get("settings", {}).get("enabledCategories", {})
    missing = [c for c in CATEGORIES if not cats.get(c)]
    if missing:
        print("FAIL persist missing", missing, got)
        return 1

    code, en = _post("/api/protection/enable", {"categoryId": "deepfakes"}, token)
    if code != 200:
        print("FAIL enable deepfakes", code, en)
        return 1

    print("PASS protection L2", len(CATEGORIES), "categories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
