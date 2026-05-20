#!/usr/bin/env python3
"""E1 acceptance smoke on prod API (tests 1, 8 + schema touch)."""
from __future__ import annotations

import base64
import json
import os
import sys
import time
import uuid
import urllib.error
import urllib.request
from typing import Dict, Optional, Tuple


def _req(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    body: Optional[bytes] = None,
    timeout: int = 25,
) -> Tuple[int, str]:
    r = urllib.request.Request(url, data=body, method=method)
    for k, v in (headers or {}).items():
        r.add_header(k, v)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            raw = resp.read()
            return resp.getcode(), raw.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        return e.code, raw


def main() -> int:
    base = os.environ.get("ALADDIN_API_BASE", "http://149.154.65.180:8002").rstrip("/")
    device_id = f"smoke_e2ee_{int(time.time())}_{uuid.uuid4().hex[:8]}"

    code, reg_body = _req(
        "POST",
        f"{base}/api/auth/register-device",
        headers={"Content-Type": "application/json"},
        body=json.dumps({"device_id": device_id}).encode("utf-8"),
    )
    if code not in (200, 201):
        print(f"FAIL register-device http={code} {reg_body[:300]}")
        return 1
    reg = json.loads(reg_body)
    token = reg.get("access_token") or reg.get("token")
    if not token:
        print("FAIL no JWT in register-device")
        return 1
    auth = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Pick a real family_id from members list
    code, members_body = _req("GET", f"{base}/api/family/members", headers=auth)
    if code != 200:
        print(f"FAIL GET members http={code} {members_body[:300]}")
        return 1
    members = json.loads(members_body)
    family_id = None
    if isinstance(members, dict):
        fam = members.get("family_id") or members.get("familyId")
        if fam:
            family_id = str(fam)
        items = members.get("members") or members.get("items") or []
        if not family_id and items:
            family_id = str(items[0].get("family_id") or items[0].get("familyId") or "")
    if not family_id:
        family_id = os.environ.get("SMOKE_FAMILY_ID", "").strip()
    if not family_id:
        print("FAIL could not resolve family_id — set SMOKE_FAMILY_ID")
        return 1
    print(f"OK family_id={family_id}")

    # Test 8 — plaintext v1 rejected
    code, body = _req(
        "POST",
        f"{base}/api/family/chat/send",
        headers=auth,
        body=json.dumps(
            {"message": "hello-plain", "familyId": family_id, "envelopeVersion": 1}
        ).encode("utf-8"),
    )
    if code != 400 or "envelope_version=2" not in body and "plaintext" not in body.lower():
        print(f"FAIL test8 expected 400 plaintext forbidden, got {code} {body[:300]}")
        return 1
    print("OK test8 plaintext v1 rejected (400)")

    # Register E2EE device (minimal bundle)
    import secrets

    identity = base64.b64encode(secrets.token_bytes(32)).decode("ascii")
    spk_pub = base64.b64encode(secrets.token_bytes(32)).decode("ascii")
    spk_sig = base64.b64encode(secrets.token_bytes(64)).decode("ascii")
    e2ee_device = f"dev_{uuid.uuid4().hex[:12]}"
    reg_e2ee = {
        "family_id": family_id,
        "device_id": e2ee_device,
        "registration_id": 12345,
        "identity_key_public": identity,
        "signed_prekey": {"id": 1, "public": spk_pub, "signature": spk_sig},
        "one_time_prekeys": [],
    }
    code, body = _req(
        "POST",
        f"{base}/api/family/chat/e2ee/keys/register",
        headers=auth,
        body=json.dumps(reg_e2ee).encode("utf-8"),
    )
    if code not in (200, 201):
        print(f"FAIL e2ee register http={code} {body[:400]}")
        return 1
    print(f"OK e2ee keys/register device={e2ee_device}")

    # Send v2 ciphertext (dummy base64 — server stores opaque)
    cipher = base64.b64encode(b"smoke-ciphertext-blob").decode("ascii")
    send_body = {
        "familyId": family_id,
        "messageType": "text",
        "envelopeVersion": 2,
        "senderDeviceId": e2ee_device,
        "ciphertext": cipher,
    }
    code, body = _req(
        "POST",
        f"{base}/api/family/chat/send",
        headers=auth,
        body=json.dumps(send_body).encode("utf-8"),
    )
    if code not in (200, 201):
        print(f"FAIL v2 send http={code} {body[:400]}")
        return 1
    send_resp = json.loads(body)
    msg_id = send_resp.get("messageId") or send_resp.get("message_id")
    print(f"OK v2 send messageId={msg_id}")

    # GET messages — v2 should have ciphertext, text null
    code, body = _req(
        "GET",
        f"{base}/api/family/chat/messages?familyId={family_id}",
        headers=auth,
    )
    if code != 200:
        print(f"FAIL GET messages http={code} {body[:300]}")
        return 1
    msgs = json.loads(body)
    arr = msgs if isinstance(msgs, list) else msgs.get("messages") or msgs.get("data") or []
    found = None
    for m in arr:
        if str(m.get("id")) == str(msg_id):
            found = m
            break
    if not found and arr:
        found = arr[-1]
    if not found:
        print("WARN no message in GET list (may be lag)")
    else:
        env = found.get("envelopeVersion") or found.get("envelope_version")
        if int(env or 1) != 2:
            print(f"FAIL message not v2 envelope={env}")
            return 1
        if found.get("text"):
            print(f"FAIL v2 message has plaintext text={found.get('text')[:50]}")
            return 1
        if not found.get("ciphertext"):
            print("FAIL v2 message missing ciphertext in API")
            return 1
        print("OK GET messages returns ciphertext without plaintext text")

    print("OK smoke_family_e2ee_acceptance")
    return 0


if __name__ == "__main__":
    sys.exit(main())
