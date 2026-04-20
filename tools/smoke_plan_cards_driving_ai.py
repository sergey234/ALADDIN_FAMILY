#!/usr/bin/env python3
"""
План §2.2 п.3–4: смоук карточек Driving и AI Categories (stats), stdlib only.

Переменная окружения: ALADDIN_API_BASE (по умолчанию https://aladdin-ai.ru)

Проверяет:
  - 200 или 503 (политика шлюза);
  - отсутствие mock‑маркеров в теле;
  - при 200 для stats с полем source — предпочтительно source=api_db (боевой путь из БД).

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


BASE = os.environ.get("ALADDIN_API_BASE", "https://aladdin-ai.ru").rstrip("/")

FORBIDDEN = (
    "sfm_mock",
    "sfm_fallback",
    "sfm_error",
    "mock_fallback",
    '"source":"mock"',
)


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
    device_id = f"smoke_driving_ai_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    url = f"{BASE}/api/auth/register-device"
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
        raise RuntimeError(f"register-device HTTP {e.code}: {raw[:400]}") from e
    if code not in (200, 201):
        raise RuntimeError(f"register-device http={code} body={raw[:400]}")
    data = json.loads(raw)
    token = data.get("access_token") or data.get("token") or data.get("jwt")
    if not token:
        raise RuntimeError(f"No token in response keys={list(data.keys())}")
    return str(token)


def get_json(url: str, token: str) -> Tuple[int, Any]:
    try:
        code, raw = _request("GET", url, headers={"Authorization": f"Bearer {token}"})
    except urllib_error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace") if e.fp else ""
        if e.code == 503:
            return 503, {"detail": "503"}
        raise RuntimeError(f"GET {url} HTTP {e.code}: {raw[:500]}") from e
    if code == 503:
        return 503, {"detail": "503"}
    if code != 200:
        raise RuntimeError(f"GET {url} http={code} body={raw[:500]}")
    return code, json.loads(raw)


def assert_no_mock(js: Any) -> None:
    s = json.dumps(js, ensure_ascii=False)
    for m in FORBIDDEN:
        assert m not in s, f"Forbidden marker {m!r} in response"


def check_card(name: str, path: str, token: str, params: Optional[Dict[str, str]] = None) -> None:
    q = urllib_parse.urlencode(params or {}, doseq=True)
    url = f"{BASE}{path}" + (f"?{q}" if q else "")
    status, js = get_json(url, token)
    if status == 503:
        print(f"  {name}: 503 (pass)")
        return
    assert_no_mock(js)
    if isinstance(js, dict) and "source" in js:
        src = str(js.get("source", "")).lower()
        assert src not in ("sfm_mock", "mock", "reports_compat"), f"{name}: unexpected source={js.get('source')}"
        if src != "api_db":
            print(f"  {name}: WARN source={js.get('source')!r} (expected api_db when DB path active)")
    print(f"  {name}: OK (200)")


def main() -> int:
    print(f"smoke_plan_cards_driving_ai: BASE={BASE}")
    try:
        token = get_token()
    except Exception as e:
        print(f"FAIL auth: {e}")
        return 1
    try:
        check_card("Driving", "/api/reports/driving/stats", token, {"period": "week"})
        check_card("AI Categories", "/api/reports/ai-categories/stats", token, None)
    except Exception as e:
        print(f"FAIL: {e}")
        return 1
    print("smoke_plan_cards_driving_ai: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
