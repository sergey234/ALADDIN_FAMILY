#!/usr/bin/env python3
"""E1 acceptance smoke — run ON SERVER with PYTHONPATH=/opt/aladdin-backend."""
from __future__ import annotations

import base64
import json
import os
import secrets
import sys
import uuid
import urllib.error
import urllib.request
from typing import Dict, Optional, Tuple

from sqlalchemy import text

from app.database.database import SessionLocal
from app.routers.auth_router import create_access_token


def _req(method: str, url: str, headers: Optional[Dict[str, str]] = None, body: Optional[bytes] = None) -> Tuple[int, str]:
    r = urllib.request.Request(url, data=body, method=method)
    for k, v in (headers or {}).items():
        r.add_header(k, v)
    try:
        with urllib.request.urlopen(r, timeout=25) as resp:
            return resp.getcode(), resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def main() -> int:
    base = os.environ.get("ALADDIN_API_BASE", "http://127.0.0.1:8002").rstrip("/")
    db = SessionLocal()
    row = db.execute(
        text(
            """
            SELECT fm.user_id, fm.family_id::text
            FROM family_members fm
            WHERE fm.user_id IS NOT NULL
            ORDER BY fm.updated_at DESC NULLS LAST
            LIMIT 1
            """
        )
    ).fetchone()
    if not row:
        print("FAIL no family_members row")
        return 1
    user_id, family_id = int(row[0]), str(row[1])
    token = create_access_token({"sub": str(user_id), "user_id": user_id})
    auth = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    print(f"OK user_id={user_id} family_id={family_id}")

    code, body = _req(
        "POST",
        f"{base}/api/family/chat/send",
        headers=auth,
        body=json.dumps({"message": "hello-plain", "familyId": family_id, "envelopeVersion": 1}).encode(),
    )
    if code != 400:
        print(f"FAIL test8 http={code} body={body[:300]}")
        return 1
    print("OK test8 plaintext rejected")

    e2ee_device = f"dev_{uuid.uuid4().hex[:12]}"
    identity = base64.b64encode(secrets.token_bytes(32)).decode()
    spk_pub = base64.b64encode(secrets.token_bytes(32)).decode()
    spk_sig = base64.b64encode(secrets.token_bytes(64)).decode()
    code, body = _req(
        "POST",
        f"{base}/api/family/chat/e2ee/keys/register",
        headers=auth,
        body=json.dumps(
            {
                "family_id": family_id,
                "device_id": e2ee_device,
                "registration_id": 12345,
                "identity_key_public": identity,
                "signed_prekey": {"id": 1, "public": spk_pub, "signature": spk_sig},
                "one_time_prekeys": [],
            }
        ).encode(),
    )
    if code not in (200, 201):
        print(f"FAIL e2ee register {code} {body[:400]}")
        return 1
    print("OK e2ee register")

    cipher = base64.b64encode(b"smoke-e2ee-acceptance-v2").decode()
    code, body = _req(
        "POST",
        f"{base}/api/family/chat/send",
        headers=auth,
        body=json.dumps(
            {
                "familyId": family_id,
                "messageType": "text",
                "envelopeVersion": 2,
                "senderDeviceId": e2ee_device,
                "ciphertext": cipher,
            }
        ).encode(),
    )
    if code not in (200, 201):
        print(f"FAIL v2 send {code} {body[:400]}")
        return 1
    msg_id = json.loads(body).get("messageId")
    print(f"OK v2 send id={msg_id}")

    row_db = db.execute(
        text(
            """
            SELECT envelope_version, text IS NULL, octet_length(ciphertext)
            FROM family_chat_messages WHERE id = :mid
            """
        ),
        {"mid": msg_id},
    ).fetchone()
    if not row_db or int(row_db[0]) != 2 or not row_db[1] or int(row_db[2] or 0) < 1:
        print(f"FAIL test1 DB row={row_db}")
        return 1
    print(f"OK test1 DB envelope_version=2 text=NULL cipher_len={row_db[2]}")

    code, body = _req("GET", f"{base}/api/family/chat/messages?familyId={family_id}", headers=auth)
    if code != 200:
        print(f"FAIL GET messages {code}")
        return 1
    msgs = json.loads(body)
    arr = msgs if isinstance(msgs, list) else msgs.get("messages") or []
    hit = next((m for m in arr if str(m.get("id")) == str(msg_id)), None)
    if hit and hit.get("text"):
        print("FAIL test2 API returned plaintext text")
        return 1
    if hit and not hit.get("ciphertext"):
        print("FAIL test2 API missing ciphertext")
        return 1
    print("OK test2 GET messages ciphertext only")

    print("OK smoke_family_e2ee_acceptance_prod")
    return 0


if __name__ == "__main__":
    sys.exit(main())
