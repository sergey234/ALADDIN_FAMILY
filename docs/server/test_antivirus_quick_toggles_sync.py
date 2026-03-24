#!/usr/bin/env python3
"""
GO/STOP smoke for antivirus quick toggles server sync.

Checks component configuration contract for malware_detection_agent:
- realTimeScanning
- scanDownloads
- quarantineThreats
"""

import json
import time
import requests

BASE_URL = "https://aladdin-ai.ru"
COMPONENT_ID = "malware_detection_agent"


def register_and_get_token() -> str:
    email = f"antivirus_quick_{int(time.time())}@aladdin.local"
    payload = {"email": email, "password": "QuickToggle!123"}
    r = requests.post(f"{BASE_URL}/api/auth/register", json=payload, timeout=20)
    r.raise_for_status()
    data = r.json()
    token = data.get("access_token")
    if not token:
        raise RuntimeError(f"No access_token in register response: {data}")
    return token


def get_config(token: str) -> dict:
    r = requests.get(
        f"{BASE_URL}/api/components/configuration/{COMPONENT_ID}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=20,
    )
    r.raise_for_status()
    return r.json()


def post_config(token: str, settings: dict) -> dict:
    body = {"settings": settings}
    r = requests.post(
        f"{BASE_URL}/api/components/configuration/{COMPONENT_ID}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=body,
        timeout=20,
    )
    r.raise_for_status()
    return r.json()


def val(d: dict, key: str, default=None):
    return d.get(key, default)


def main():
    token = register_and_get_token()
    before = get_config(token)
    settings_before = val(val(before, "configuration", {}), "settings", {})

    target = {
        "realTimeScanning": False,
        "scanDownloads": False,
        "quarantineThreats": True,
    }
    merged = dict(settings_before)
    merged.update(target)

    post_config(token, merged)
    after = get_config(token)
    settings_after = val(val(after, "configuration", {}), "settings", {})

    checks = {
        "realTimeScanning": settings_after.get("realTimeScanning") is False,
        "scanDownloads": settings_after.get("scanDownloads") is False,
        "quarantineThreats": settings_after.get("quarantineThreats") is True,
    }

    failed = [k for k, ok in checks.items() if not ok]
    status = "GO" if not failed else "STOP"

    print(json.dumps({
        "status": status,
        "componentId": COMPONENT_ID,
        "checks": checks,
        "before": {
            "realTimeScanning": settings_before.get("realTimeScanning"),
            "scanDownloads": settings_before.get("scanDownloads"),
            "quarantineThreats": settings_before.get("quarantineThreats"),
        },
        "after": {
            "realTimeScanning": settings_after.get("realTimeScanning"),
            "scanDownloads": settings_after.get("scanDownloads"),
            "quarantineThreats": settings_after.get("quarantineThreats"),
        },
    }, ensure_ascii=False, indent=2))

    if status != "GO":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

