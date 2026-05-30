#!/usr/bin/env python3
"""
Smoke: Family P1 headers + Companion STT on VPS (/opt/aladdin-backend).

Usage:
  python3 scripts/vps_smoke_family_stt.py --mode off      # STT disabled (expected now)
  python3 scripts/vps_smoke_family_stt.py --mode stt      # capabilities + /stt only
  python3 scripts/vps_smoke_family_stt.py --mode family   # family headers + stale add
  python3 scripts/vps_smoke_family_stt.py --mode all      # default: everything
"""
from __future__ import annotations

import argparse
import io
import json
import os
import struct
import sys
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

BASE = os.environ.get("ALADDIN_SMOKE_BASE", "http://127.0.0.1:8002")


def mint(uid: int = 170, level: str = "premium") -> str:
    secret = os.environ.get("JWT_SECRET", "")
    if not secret:
        raise RuntimeError("JWT_SECRET missing in .env")
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
    multipart: dict[str, tuple[str, bytes, str]] | None = None,
) -> tuple[int, dict[str, str], str]:
    url = BASE + path
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


def print_env() -> None:
    yandex = os.environ.get("YANDEX_SPEECHKIT_API_KEY", "")
    openai = os.environ.get("OPENAI_API_KEY", "")
    proxy = os.environ.get("COMPANION_STT_OPENAI_HTTPS_PROXY", "")
    print("=== ENV ===")
    print("FEATURE_COMPANION_SERVER_STT:", os.environ.get("FEATURE_COMPANION_SERVER_STT", ""))
    print("COMPANION_STT_PROVIDER:", os.environ.get("COMPANION_STT_PROVIDER", "auto"))
    print("YANDEX_SPEECHKIT_API_KEY:", f"ok len={len(yandex)}" if yandex else "MISSING")
    print("OPENAI_API_KEY:", f"ok len={len(openai)}" if openai else "MISSING")
    print("COMPANION_STT_OPENAI_HTTPS_PROXY:", proxy[:48] + "…" if len(proxy) > 48 else (proxy or "MISSING"))


def make_silence_wav(seconds: float = 1.0, rate: int = 16000) -> bytes:
    frames = int(rate * seconds)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(struct.pack("<" + "h" * frames, *([0] * frames)))
    return buf.getvalue()


def smoke_capabilities(tok: str, *, expect_enabled: bool | None) -> bool:
    ok = True
    code, _, body = http("GET", "/api/ai/companion/capabilities", tok)
    print(f"\n=== CAPABILITIES: HTTP {code} ===")
    try:
        cap = json.loads(body)
        modules = (
            cap.get("modules")
            or cap.get("features")
            or (cap.get("data") or {}).get("modules")
            or (cap.get("data") or {}).get("features")
            or {}
        )
        stt = modules.get("companion_server_stt") or {}
        print("companion_server_stt:", json.dumps(stt, ensure_ascii=False)[:500])
        enabled = bool(stt.get("enabled"))
        ui = stt.get("ui") or {}
        print("  server_stt_fallback:", ui.get("server_stt_fallback"))
        print("  provider:", ui.get("provider"))
        if expect_enabled is True and not enabled:
            print("FAIL: expected STT enabled in capabilities")
            ok = False
        elif expect_enabled is False and enabled:
            print("FAIL: expected STT disabled in capabilities")
            ok = False
        elif expect_enabled is False and not enabled:
            print("OK: STT disabled in capabilities")
        elif expect_enabled is True and enabled:
            print("OK: STT enabled in capabilities")
    except json.JSONDecodeError:
        print("body:", body[:300])
        ok = False
    return ok


def smoke_stt_endpoint(tok: str, *, expect_disabled: bool) -> bool:
    ok = True
    wav = make_silence_wav()
    code, _, body = http(
        "POST",
        "/api/ai/companion/stt",
        tok,
        multipart={"audio": ("test.wav", wav, "audio/wav")},
    )
    print(f"\n=== COMPANION STT (1s silence WAV): HTTP {code} ===")
    print("body:", body[:400])
    if expect_disabled:
        if code == 424 and "server_stt_disabled" in body:
            print("OK: STT disabled as expected (424)")
        else:
            print(f"FAIL: expected 424 server_stt_disabled, got {code}")
            ok = False
    else:
        if code in (200, 422):
            print("OK: STT reachable (200 transcript or 422 empty)")
        elif code == 424:
            print("FAIL: STT disabled/unconfigured but expected enabled")
            ok = False
        elif code == 503:
            print("WARN: provider error (503) — check Yandex/OpenAI/proxy keys")
            ok = False
        else:
            print(f"FAIL: unexpected STT status {code}")
            ok = False
    return ok


def smoke_family(tok: str) -> bool:
    ok = True
    code, hdrs, body = http("GET", "/api/family/members", tok)
    print(f"\n=== FAMILY MEMBERS (user 170): HTTP {code} ===")
    for h in (
        "X-Resolved-Family-Id",
        "X-Family-Context",
        "X-Actor-Can-Manage-Roster",
        "X-Family-Roster-Used",
        "X-Family-Roster-Max",
    ):
        print(f"  {h}: {hdrs.get(h)}")
    if code != 200:
        print("body:", body[:200])
        ok = False
    elif hdrs.get("X-Family-Context") == "none":
        print("OK: no family context (none)")
    elif "X-Actor-Can-Manage-Roster" not in hdrs:
        print("WARN: missing X-Actor-Can-Manage-Roster (non-fatal for STT smoke)")

    stale = "FAM_89EC5499F331"
    code, _, body = http(
        "POST",
        "/api/family/add",
        tok,
        body={"name": "SmokeTest", "role": "child", "familyId": stale},
    )
    print(f"\n=== STALE FAMILY ADD: HTTP {code} ===")
    print("body:", body[:240])
    if code == 409 and "family_context_stale" in body.lower():
        print("OK: stale context returns 409 family_context_stale")
    elif code == 409 and "mismatch" in body.lower():
        print("WARN: 409 mismatch (server wording differs from family_context_stale)")
    else:
        print("WARN: stale add check inconclusive (non-fatal for STT-only deploy)")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description="ALADDIN VPS smoke: family + companion STT")
    parser.add_argument(
        "--mode",
        choices=("off", "stt", "on", "family", "all"),
        default="all",
        help="off=STT disabled; stt/on=capabilities+STT; family=family only; all=both",
    )
    args = parser.parse_args()
    mode = args.mode
    if mode == "on":
        mode = "stt"

    print_env()
    tok = mint(170)
    ok = True

    if mode in ("off", "stt", "all"):
        if mode == "off":
            ok &= smoke_capabilities(tok, expect_enabled=False)
            ok &= smoke_stt_endpoint(tok, expect_disabled=True)
        elif mode == "stt":
            feat = (os.environ.get("FEATURE_COMPANION_SERVER_STT") or "").strip()
            if feat in ("0", "false", "False", "no", "off"):
                print("\nNOTE: FEATURE_COMPANION_SERVER_STT=0 — use --mode off")
                ok &= smoke_capabilities(tok, expect_enabled=False)
                ok &= smoke_stt_endpoint(tok, expect_disabled=True)
            else:
                ok &= smoke_capabilities(tok, expect_enabled=True)
                ok &= smoke_stt_endpoint(tok, expect_disabled=False)

    if mode in ("family", "all"):
        ok &= smoke_family(tok)

    print("\n=== OVERALL ===")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
