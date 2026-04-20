#!/usr/bin/env python3
"""
Смоук по плану ML (раздел F / smoke-contracts): 5 доменов отчётов + driving + ai-categories.

Проверяет GET /api/reports/*/stats (200, JSON, без mock-маркеров) и по одному list-эндпоинту
с курсорной формой там, где он есть.

Переменные окружения:
  ALADDIN_API_BASE  — по умолчанию http://149.154.65.180:8002

Выход: 0 = OK, 1 = ошибка.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import urllib.request

FORBIDDEN = (
    "sfm_mock",
    "sfm_fallback",
    "mock_fallback",
    "reports_compat",
)

STATS_PATHS: List[str] = [
    "/api/reports/driving/stats",
    "/api/reports/dark-web/stats",
    "/api/reports/identity-theft/stats",
    "/api/reports/privacy/tracker/stats",
    "/api/reports/privacy/location/stats",
    "/api/reports/privacy/cleanup/stats",
    "/api/reports/ai-categories/stats",
]

LIST_PATHS: List[str] = [
    "/api/reports/dark-web/leaks/list?limit=3",
    "/api/reports/identity-theft/attempts/list?limit=3",
    "/api/reports/privacy/location/requests/list?limit=3",
    "/api/reports/privacy/cleanup/records/list?limit=3",
    "/api/reports/privacy/tracker/top/list?limit=3",
]


def _get(url: str, timeout: int = 20) -> Tuple[int, str]:
    r = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        return resp.getcode(), resp.read().decode("utf-8", errors="replace")


def _bad_markers(text: str) -> List[str]:
    low = (text or "").lower()
    return [m for m in FORBIDDEN if m in low]


def _check_stats(path: str, base: str) -> Optional[str]:
    url = base + path
    try:
        code, body = _get(url)
    except Exception as e:
        return f"{path}: request failed: {e}"
    if code != 200:
        return f"{path}: http {code} body={body[:400]}"
    bad = _bad_markers(body)
    if bad:
        return f"{path}: forbidden markers {bad}"
    try:
        data: Dict[str, Any] = json.loads(body)
    except json.JSONDecodeError as e:
        return f"{path}: invalid json: {e}"
    src = str(data.get("source") or "").lower()
    if "mock" in src or src == "sfm":
        return f"{path}: suspicious source={data.get('source')!r}"
    for key in ("total", "blocked", "allowed"):
        if key not in data:
            return f"{path}: missing key {key!r}"
    return None


def _check_list(path: str, base: str) -> Optional[str]:
    url = base + path
    try:
        code, body = _get(url)
    except Exception as e:
        return f"{path}: request failed: {e}"
    if code != 200:
        return f"{path}: http {code} body={body[:400]}"
    bad = _bad_markers(body)
    if bad:
        return f"{path}: forbidden markers {bad}"
    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        return f"{path}: invalid json: {e}"
    if not isinstance(data, dict):
        return f"{path}: expected object got {type(data)}"
    if "items" not in data:
        return f"{path}: missing items (cursor list contract)"
    if not isinstance(data["items"], list):
        return f"{path}: items not a list"
    return None


def main() -> int:
    base = os.environ.get("ALADDIN_API_BASE", "http://149.154.65.180:8002").rstrip("/")
    errors: List[str] = []
    for p in STATS_PATHS:
        err = _check_stats(p, base)
        if err:
            errors.append(err)
    for p in LIST_PATHS:
        err = _check_list(p, base)
        if err:
            errors.append(err)
    if errors:
        for e in errors:
            print(f"FAIL {e}", file=sys.stderr)
        return 1
    print(f"OK reports_five_domains+driving+ai: {len(STATS_PATHS)} stats + {len(LIST_PATHS)} lists @ {base}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
