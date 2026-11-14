#!/usr/bin/env python3
"""Static mirror of NetworkManager.normalizeDrivingReportsListPayload (no xcodebuild)."""
from __future__ import annotations

import json
import sys


def normalize(path: str, raw: bytes) -> bytes | None:
    is_list = "/api/reports/driving" in path and not any(
        x in path for x in ("/stats", "/export", "/start", "/end", "/events")
    )
    if not is_list:
        return None
    root = json.loads(raw)
    if isinstance(root, list):
        return raw
    if isinstance(root, dict):
        data = root.get("data")
        if isinstance(data, list):
            return json.dumps(data).encode()
        if isinstance(data, bool) or "success" in root:
            return b"[]"
    return b"[]"


def main() -> int:
    stub = b'{"success":true,"data":true,"message":"Driving reports available"}'
    assert normalize("/api/reports/driving?period=week", stub) == b"[]"
    assert normalize("/api/reports/driving/stats", stub) is None
    assert normalize("/api/reports/driving", b'[{"id":"1"}]') == b'[{"id":"1"}]'
    env = b'{"success":true,"data":[{"id":"t1"}]}'
    out = normalize("/api/reports/driving", env)
    assert out is not None and json.loads(out)[0]["id"] == "t1"
    print("OK verify_driving_reports_decode_normalize")
    return 0


if __name__ == "__main__":
    sys.exit(main())
