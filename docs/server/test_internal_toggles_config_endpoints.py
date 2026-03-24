#!/usr/bin/env python3
"""
Smoke-check for internal (gear) toggles configuration endpoints.

What it validates:
1) GET /api/components/configuration/{component_id} returns non-mock response.
2) POST /api/components/configuration/{component_id} accepts canonical payload.
3) Follow-up GET still returns non-mock response.
"""

import json
import subprocess
import time
from typing import Dict, Optional, Tuple

BASE_URL = "https://aladdin-ai.ru"

COMPONENT_SETTINGS = {
    "phishing_protection_agent": {
        "blockSuspiciousLinks": True,
        "warnBeforeOpening": True,
        "checkEmailLinks": True,
        "checkSMSLinks": True,
        "blockKnownPhishingDomains": True,
        "sensitivityLevel": "high",
    },
    "malware_detection_agent": {
        "realTimeScanning": True,
        "scanDownloads": True,
        "scanInstalledApps": True,
        "quarantineThreats": True,
        "autoRemoveThreats": False,
        "scanFrequency": "daily",
    },
    "mobile_security_agent": {
        "deviceEncryption": True,
        "appLock": True,
        "screenLock": True,
        "biometricAuth": True,
        "remoteWipe": False,
        "trackDevice": True,
    },
    "network_security_agent": {
        "blockUnsafeNetworks": True,
        "warnOnPublicWiFi": True,
        "autoConnectVPN": False,
        "blockTracking": True,
        "encryptTraffic": True,
        "firewallEnabled": True,
    },
    "incident_response_agent": {
        "escalationThresholds": {"low": "30", "medium": "15", "high": "5", "critical": "1"},
        "slaTime": "30",
        "contactRoles": ["admin", "security"],
        "autoActions": {"block": False, "notify": True, "escalate": True},
    },
    "password_security_agent": {
        "passwordLength": 16,
        "includeUppercase": True,
        "includeLowercase": True,
        "includeNumbers": True,
        "includeSpecial": True,
    },
}

MOCK_MARKERS = ("sfm_mock", "sfm_fallback", "sfm_error", "mock_fallback")


def run(cmd: str) -> str:
    return subprocess.check_output(cmd, shell=True, text=True).strip()


def curl_json(method: str, url: str, token: str, body: Optional[Dict] = None) -> Tuple[int, str]:
    body_part = ""
    if body is not None:
        payload = json.dumps(body, ensure_ascii=False).replace("'", "'\\''")
        body_part = f" -H 'Content-Type: application/json' -d '{payload}'"

    cmd = (
        f"curl -sS -m 25 -w '\\nHTTP_STATUS:%{{http_code}}' -X {method} "
        f"-H 'Authorization: Bearer {token}' '{url}'{body_part}"
    )
    raw = run(cmd)
    if "\nHTTP_STATUS:" not in raw:
        return 0, raw
    body_text, status_text = raw.rsplit("\nHTTP_STATUS:", 1)
    return int(status_text.strip()), body_text.strip()


def has_mock_markers(payload: str) -> bool:
    text = payload.lower()
    return any(marker in text for marker in MOCK_MARKERS)


def main() -> None:
    email = f"internal_cfg_{int(time.time())}@aladdin.local"
    password = "Gate!Pass123"

    reg_cmd = (
        "curl -sS -m 25 -X POST "
        f"'{BASE_URL}/api/auth/register' "
        "-H 'Content-Type: application/json' "
        f"-d '{{\"email\":\"{email}\",\"password\":\"{password}\"}}'"
    )
    reg_raw = run(reg_cmd)
    reg = json.loads(reg_raw)
    token = reg.get("access_token", "")
    if not token:
        print("TOKEN_FAIL")
        print(reg_raw)
        return

    all_ok = True
    for component_id, settings in COMPONENT_SETTINGS.items():
        get_url = f"{BASE_URL}/api/components/configuration/{component_id}"
        post_url = get_url

        st_get_1, body_get_1 = curl_json("GET", get_url, token)
        post_payload = {"settings": settings}
        st_post, body_post = curl_json("POST", post_url, token, post_payload)
        st_get_2, body_get_2 = curl_json("GET", get_url, token)

        bad = (
            st_post >= 400
            or st_get_2 >= 400
            or has_mock_markers(body_get_1 + body_post + body_get_2)
        )
        all_ok = all_ok and (not bad)
        print(
            f"{component_id} "
            f"GET1={st_get_1} POST={st_post} GET2={st_get_2} "
            f"{'OK' if not bad else 'BAD'}"
        )
        if bad:
            print("  GET1:", body_get_1[:180])
            print("  POST:", body_post[:180])
            print("  GET2:", body_get_2[:180])

    print("INTERNAL_CONFIG_ALL_OK", all_ok)


if __name__ == "__main__":
    main()

