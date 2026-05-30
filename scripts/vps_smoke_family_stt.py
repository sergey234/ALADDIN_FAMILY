#!/usr/bin/env python3
"""Smoke test Family P1 + Companion STT on VPS (run on server in /opt/aladdin-backend)."""
from __future__ import annotations

import io
import json
import os
import struct
import time
import uuid
import wave
import urllib.error
import urllib.request

ROOT = os.environ.get("ALADDIN_BACKEND_ROOT", "/opt/aladdin-backend")
os.chdir(ROOT)

for line in open(".env"):
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

import jwt  # noqa: E402

secret = os.environ.get("JWT_SECRET", "")
openai = os.environ.get("OPENAI_API_KEY", "")
feat = os.environ.get("FEATURE_COMPANION_SERVER_STT", "")

print("=== ENV ===")
print("JWT_SECRET:", "ok" if secret else "MISSING")
print("OPENAI_API_KEY:", f"ok len={len(openai)}" if openai else "MISSING")
print("FEATURE_COMPANION_SERVER_STT:", feat)


def mint(uid: int = 170, level: str = "premium") -> str:
    now = int(time.time())
    payload = {
        "user_id": uid,
        "sub": str(uid),
        "type": "access",
        "subscription_level": level,
        "iat": now,
        "exp": now + 3600,
    }
    return jwt.encode(payload, secret, algorithm=os.environ.get("JWT_ALGORITHM", "HS256"))


def http(
    method: str,
    path: str,
    token: str | None = None,
    body: dict | None = None,
    multipart: dict | None = None,
) -> tuple[int, dict[str, str], str]:
    url = "http://127.0.0.1:8002" + path
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = "Bearer " + token
    data: bytes | None = None
    if multipart is not None:
        boundary = uuid.uuid4().hex
        chunks: list[bytes] = []
        for name, (filename, content, ctype) in multipart.items():
            chunks.append(
                (
                    f"--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
                    f"Content-Type: {ctype}\r\n\r\n"
                ).encode()
            )
            chunks.append(content)
            chunks.append(b"\r\n")
        chunks.append(f"--{boundary}--\r\n".encode())
        data = b"".join(chunks)
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    elif body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            hdrs = {k: v for k, v in resp.headers.items()}
            return resp.status, hdrs, resp.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        hdrs = {k: v for k, v in e.headers.items()}
        return e.code, hdrs, e.read().decode(errors="replace")


def main() -> int:
    ok = True
    tok = mint(170)

    code, _, body = http("GET", "/api/ai/companion/capabilities", tok)
    print(f"\n=== CAPABILITIES: HTTP {code} ===")
    try:
        cap = json.loads(body)
        modules = cap.get("modules") or (cap.get("data") or {}).get("modules") or {}
        stt = modules.get("companion_server_stt") or {}
        print("companion_server_stt:", json.dumps(stt, ensure_ascii=False)[:400])
        if not stt.get("enabled"):
            print("WARN: server STT module not enabled in capabilities")
            ok = False
    except json.JSONDecodeError:
        print("body:", body[:300])
        ok = False

    code, hdrs, body = http("GET", "/api/family/members", tok)
    print(f"\n=== FAMILY MEMBERS (user 170): HTTP {code} ===")
    for h in (
        "X-Resolved-Family-Id",
        "X-Family-Context",
        "X-Actor-Can-Manage-Roster",
        "X-Family-Roster-Used",
        "X-Family-Roster-Max",
        "X-Family-Limit",
    ):
        print(f"  {h}: {hdrs.get(h)}")
    if code != 200:
        print("body:", body[:200])
        ok = False
    elif "X-Actor-Can-Manage-Roster" not in hdrs and hdrs.get("X-Family-Context") != "none":
        print("FAIL: missing X-Actor-Can-Manage-Roster on 200")
        ok = False

    stale = "FAM_89EC5499F331"
    code, _, body = http(
        "POST",
        "/api/family/add",
        tok,
        body={"name": "SmokeTest", "role": "child", "familyId": stale},
    )
    print(f"\n=== STALE FAMILY ADD: HTTP {code} ===")
    print("body:", body[:240])
    if code != 409 or "family_context_stale" not in body.lower():
        print("FAIL: expected 409 family_context_stale")
        ok = False
    else:
        print("OK: stale context returns 409 family_context_stale")

    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(struct.pack("<" + "h" * 16000, *([0] * 16000)))
    wav = buf.getvalue()
    code, _, body = http(
        "POST",
        "/api/ai/companion/stt",
        tok,
        multipart={"file": ("test.wav", wav, "audio/wav")},
    )
    print(f"\n=== COMPANION STT (1s silence WAV): HTTP {code} ===")
    print("body:", body[:400])
    if code not in (200, 422):
        print(f"FAIL: unexpected STT status {code}")
        ok = False
    elif code == 424:
        print("FAIL: STT disabled/unconfigured")
        ok = False
    else:
        print("OK: STT endpoint reachable (200 or 422 empty speech is fine)")

    print("\n=== OVERALL ===")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
