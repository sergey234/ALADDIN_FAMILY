#!/usr/bin/env python3
"""
Advanced Settings smoke test (GO/STOP) for:
1) Safari settings (browser_security_bot)
2) Parental monitoring toggles (parental_control_bot)
3) Time management payloads (parental_control_bot)

Usage:
  export BASE_URL="https://aladdin-ai.ru"
  export TOKEN="<jwt>"
  python3 docs/server/test_advanced_settings_smoke.py
"""

import json
import os
import sys
from typing import Any, Dict, Optional, Tuple

import requests


BASE_URL = os.getenv("BASE_URL", "https://aladdin-ai.ru").rstrip("/")
TOKEN = os.getenv("TOKEN", "")
TIMEOUT = 20


def fail(msg: str) -> None:
    print(f"[STOP] {msg}")
    sys.exit(1)


def req(method: str, path: str, body: Optional[Dict[str, Any]] = None) -> requests.Response:
    if not TOKEN:
        fail("TOKEN is empty. Export TOKEN before running.")
    url = f"{BASE_URL}{path}"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    return requests.request(method, url, headers=headers, json=body, timeout=TIMEOUT)


def get_config(component_id: str) -> Dict[str, Any]:
    r = req("GET", f"/api/components/configuration/{component_id}")
    if r.status_code != 200:
        fail(f"GET config failed for {component_id}: {r.status_code} {r.text[:200]}")
    data = r.json()
    cfg = data.get("configuration") or {}
    return cfg.get("settings") or {}


def post_settings(component_id: str, settings: Dict[str, Any]) -> None:
    r = req("POST", f"/api/components/configuration/{component_id}", {"settings": settings})
    if r.status_code != 200:
        fail(f"POST config failed for {component_id}: {r.status_code} {r.text[:200]}")
    payload = r.json()
    if payload.get("success") is False:
        fail(f"POST returned success=false for {component_id}: {payload}")


def check_keys(settings: Dict[str, Any], expected: Dict[str, Any]) -> Tuple[bool, str]:
    for k, v in expected.items():
        if settings.get(k) != v:
            return False, f"{k}: expected={v}, got={settings.get(k)}"
    return True, "ok"


def main() -> None:
    print(f"[INFO] BASE_URL={BASE_URL}")

    # --- 1) Safari settings ---
    safari_payload = {
        "selectedCategories": ["adult", "violence", "gambling", "forums"],
        "safariSitesEnabled": True,
        "safariSocialEnabled": True
    }
    post_settings("browser_security_bot", safari_payload)
    safari_settings = get_config("browser_security_bot")
    ok, reason = check_keys(
        safari_settings,
        {
            "safariSitesEnabled": True,
            "safariSocialEnabled": True
        },
    )
    if not ok:
        fail(f"Safari verify failed: {reason}")
    print("[PASS] Safari settings write/read verified")

    # --- 2) Parental monitoring toggles ---
    parental_payload = {
        "messagesMonitoringEnabled": True,
        "screenshotsEnabled": True,
        "parental_messages_monitoring": True,
        "parental_screenshots_enabled": True
    }
    post_settings("parental_control_bot", parental_payload)
    parental_settings = get_config("parental_control_bot")
    ok, reason = check_keys(
        parental_settings,
        {
            "messagesMonitoringEnabled": True,
            "screenshotsEnabled": True
        },
    )
    if not ok:
        fail(f"Parental monitoring verify failed: {reason}")
    print("[PASS] Parental monitoring write/read verified")

    # --- 3) Time management block ---
    tm_payload = {
        "scheduleWeekdayStart": 1.0,
        "scheduleWeekdayEnd": 2.0,
        "scheduleWeekendStart": 3.0,
        "scheduleWeekendEnd": 4.0,
        "scheduleIsWeekdaySelected": True,
        "sleepBedtimeStart": 5.0,
        "sleepBedtimeEnd": 6.0,
        "sleepEmergencyCallsEnabled": True,
        "appLimits": [
            {"app": "Instagram", "limit": 30.0},
            {"app": "TikTok", "limit": 20.0}
        ]
    }
    post_settings("parental_control_bot", tm_payload)
    tm_settings = get_config("parental_control_bot")
    ok, reason = check_keys(
        tm_settings,
        {
            "scheduleWeekdayStart": 1.0,
            "scheduleWeekdayEnd": 2.0,
            "sleepEmergencyCallsEnabled": True
        },
    )
    if not ok:
        fail(f"Time management verify failed: {reason}")
    if not isinstance(tm_settings.get("appLimits"), list) or len(tm_settings.get("appLimits", [])) < 2:
        fail("Time management verify failed: appLimits missing/invalid")
    print("[PASS] Time management write/read verified")

    print("[GO] Advanced Settings smoke passed")
    print(json.dumps({"result": "GO", "checks": ["safari", "parental", "time_management"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
