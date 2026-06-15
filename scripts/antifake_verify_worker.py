#!/usr/bin/env python3
"""B-04: verify worker processes audio/video jobs end-to-end (local smoke)."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

sys.path.insert(0, str(ROOT / "docs" / "server"))
from smoke_env import smoke_secret

BASE = os.environ.get("ANTIFAKE_GATE_BASE", "http://127.0.0.1:8002")


def _post_multipart(
    path: str,
    token: str,
    filename: str,
    body: bytes,
    content_type: str,
    extra_headers: dict | None = None,
) -> tuple[int, dict]:
    boundary = "AntifakeWorkerVerify"
    payload = bytearray()
    payload.extend(f"--{boundary}\r\n".encode())
    payload.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode())
    payload.extend(f"Content-Type: {content_type}\r\n\r\n".encode())
    payload.extend(body)
    payload.extend(f"\r\n--{boundary}--\r\n".encode())
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Authorization": f"Bearer {token}",
    }
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=bytes(payload),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"raw": raw}


def _register() -> str:
    req = urllib.request.Request(
        f"{BASE}/api/auth/register-device",
        data=json.dumps({"deviceId": "antifake-worker-verify"}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = json.loads(resp.read().decode())
    token = body.get("token") or body.get("access_token")
    if not token:
        raise RuntimeError(f"no jwt: {body}")
    return token


def _poll_job(token: str, job_id: str, extra_headers: dict | None = None) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    if extra_headers:
        headers.update(extra_headers)
    for _ in range(45):
        req = urllib.request.Request(
            f"{BASE}/api/antifake/jobs/{job_id}",
            headers=headers,
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode())
        if body.get("status") in ("completed", "failed") or body.get("verdict"):
            return body
        time.sleep(1)
    raise TimeoutError(f"job poll timeout {job_id}")


def main() -> int:
    smoke_key = smoke_secret("ANTIFAKE_INTERNAL_SMOKE_SECRET")
    if not smoke_key:
        print(json.dumps({"pass": False, "failures": ["ANTIFAKE_INTERNAL_SMOKE_SECRET not set"]}))
        return 1
    smoke_headers = {"X-Aladdin-Smoke": smoke_key}

    token = _register()
    wav = (
        b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
        b"\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    )
    failures: list[str] = []
    for path, label in (
        ("/api/antifake/check/audio", "audio"),
        ("/api/antifake/check/video", "video"),
    ):
        code, body = _post_multipart(
            path, token, f"verify.{label}", wav, "application/octet-stream", smoke_headers
        )
        if code not in (200, 202):
            failures.append(f"{label} upload {code}: {body}")
            continue
        if body.get("status") == "completed":
            if body.get("verdict") not in ("likely_fake", "uncertain", "likely_real"):
                failures.append(f"{label} sync bad verdict {body}")
            continue
        job_id = body.get("job_id")
        if not job_id:
            failures.append(f"{label} missing job_id {body}")
            continue
        polled = _poll_job(token, job_id, smoke_headers)
        if polled.get("verdict") not in ("likely_fake", "uncertain", "likely_real"):
            failures.append(f"{label} poll bad verdict {polled}")

    print(json.dumps({"pass": not failures, "failures": failures}, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
