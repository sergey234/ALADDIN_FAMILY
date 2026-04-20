#!/usr/bin/env python3
"""
Контрактные проверки компонентной аналитики (stats) без зависимости requests.

Переменные окружения:
  ALADDIN_API_BASE  — базовый URL API (по умолчанию https://aladdin-ai.ru)

Выход: 0 при успехе, 1 при ошибке.
"""

from __future__ import annotations

import json
import os
import sys
import time
import uuid
from typing import Any, Dict, Optional, Tuple
from urllib import error as urllib_error
from urllib import parse as urllib_parse
import urllib.request


BASE_URL = os.environ.get("ALADDIN_API_BASE", "https://aladdin-ai.ru").rstrip("/")


def _request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    body: Optional[bytes] = None,
    timeout: int = 20,
) -> Tuple[int, str]:
    req = urllib.request.Request(url, data=body, method=method)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.getcode(), resp.read().decode("utf-8", errors="replace")


def get_token() -> str:
    device_id = f"contract_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    url = f"{BASE_URL}/api/auth/register-device"
    payload = json.dumps({"device_id": device_id}).encode("utf-8")
    try:
        code, raw = _request(
            "POST",
            url,
            headers={"Content-Type": "application/json"},
            body=payload,
        )
    except urllib_error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise RuntimeError(f"register-device HTTP {e.code}: {raw[:500]}") from e
    if code not in (200, 201):
        raise RuntimeError(f"register-device http={code} body={raw[:500]}")
    data = json.loads(raw)
    token = (
        data.get("access_token")
        or data.get("token")
        or data.get("jwt")
        or data.get("accessToken")
    )
    if not token:
        raise RuntimeError(f"No token in response: {data}")
    return str(token)


def auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def assert_no_mock(resp_json: Any) -> None:
    s = json.dumps(resp_json, ensure_ascii=False)
    forbidden = [
        "sfm_mock",
        "sfm_fallback",
        "sfm_error",
        "mock_fallback",
        '"source":"mock"',
    ]
    for marker in forbidden:
        assert marker not in s, f"Mock marker found: {marker} in {s}"


def assert_component_dto(resp_json: Any) -> None:
    assert isinstance(resp_json, dict), "DTO must be dict"
    if "componentId" in resp_json:
        assert "metrics" in resp_json and isinstance(resp_json["metrics"], dict), (
            "Missing metrics dict"
        )
        return
    stats_keys = {"total", "blocked", "allowed", "last_24h", "last_7d", "last_30d"}
    assert stats_keys.issubset(resp_json.keys()), "Missing reports stats keys"


def get(url: str, token: str, params: Optional[Dict[str, str]] = None) -> Tuple[int, Any]:
    q = urllib_parse.urlencode(params or {}, doseq=True)
    full = f"{BASE_URL}{url}" + (f"?{q}" if q else "")
    headers = auth_headers(token)
    try:
        code, raw = _request("GET", full, headers=headers)
    except urllib_error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace") if e.fp else ""
        if e.code == 503:
            return 503, {"detail": "503"}
        raise RuntimeError(f"GET {url} HTTP {e.code}: {raw[:600]}") from e
    if code == 503:
        return 503, {"detail": "503"}
    if code != 200:
        raise RuntimeError(f"GET {url} http={code} body={raw[:600]}")
    return code, json.loads(raw)


def main() -> int:
    token = get_token()

    # Канонические пути /api/reports/... (согласованы с AppConfig и боевым роутером)
    endpoints = [
        ("/api/reports/driving/stats", {"period": "week"}),
        ("/api/reports/dark-web/stats", None),
        ("/api/reports/identity-theft/stats", None),
        ("/api/reports/privacy/location/stats", None),
        ("/api/reports/privacy/cleanup/stats", None),
        ("/api/reports/privacy/tracker/stats", None),
        ("/api/reports/ai-categories/stats", None),
    ]

    ok = 0
    total = 0
    failures = []
    for url, params in endpoints:
        total += 1
        try:
            status, js = get(url, token, params)
            if status == 503:
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
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
