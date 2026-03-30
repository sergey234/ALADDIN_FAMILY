#!/usr/bin/env python3
import os
import sys
import json
import time
import uuid
import requests

BASE_URL = os.environ.get("ALADDIN_API_BASE", "https://aladdin-ai.ru")

def get_token():
    # Register device to get a fresh token
    device_id = f"contract_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    r = requests.post(f"{BASE_URL}/api/auth/register-device", json={"device_id": device_id}, timeout=15)
    r.raise_for_status()
    data = r.json()
    token = data.get("access_token") or data.get("token") or data.get("jwt") or data.get("accessToken")
    if not token:
        raise RuntimeError(f"No token in response: {data}")
    return token

def auth_headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def assert_no_mock(resp_json):
    s = json.dumps(resp_json, ensure_ascii=False)
    forbidden = ["sfm_mock", "sfm_fallback", "sfm_error", "mock_fallback", "\"source\":\"mock\""]
    for marker in forbidden:
        assert marker not in s, f"Mock marker found: {marker} in {s}"

def assert_component_dto(resp_json):
    assert isinstance(resp_json, dict), "DTO must be dict"
    # Accept both normalized component DTO and reports stats DTO.
    if "componentId" in resp_json:
        assert "metrics" in resp_json and isinstance(resp_json["metrics"], dict), "Missing metrics dict"
        return
    stats_keys = {"total", "blocked", "allowed", "last_24h", "last_7d", "last_30d"}
    assert stats_keys.issubset(resp_json.keys()), "Missing reports stats keys"

def get(url, token, params=None):
    r = requests.get(f"{BASE_URL}{url}", headers=auth_headers(token), params=params or {}, timeout=15)
    # Allow 200 (API) or 503 (blocked mocks). Treat 503 as acceptable for negative checks.
    if r.status_code == 503:
        return r.status_code, {"detail": "503"}
    r.raise_for_status()
    return r.status_code, r.json()

def main():
    token = get_token()

    # Component endpoints (read-only) to exercise gateway normalization
    endpoints = [
        ("/api/reports/driving/stats", {"period": "week"}),
        ("/api/darkweb/stats", None),
        ("/api/identity/stats", None),
        ("/api/location/stats", None),
        ("/api/data/cleanup/stats", None),
        ("/api/reports/tracker/stats", None),  # if exists; optional
        ("/api/ai/categories/stats", None),
    ]

    ok = 0
    total = 0
    failures = []
    for url, params in endpoints:
        total += 1
        try:
            status, js = get(url, token, params)
            if status == 503:
                # Treated as pass for "no mocks to client" contract (blocked)
                ok += 1
                continue
            assert_no_mock(js)
            assert_component_dto(js)
            ok += 1
        except Exception as e:
            failures.append((url, str(e)))

    print(f"Components contract: {ok}/{total} passed")
    if failures:
        print("Failures:")
        for url, err in failures:
            print(f"- {url}: {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()

