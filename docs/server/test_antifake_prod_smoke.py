#!/usr/bin/env python3
"""GATE-D antifake smoke — JWT, premium gate, verdict contract (af-0-08)."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

from smoke_env import smoke_secret

BASE = os.environ.get("ANTIFAKE_SMOKE_BASE", "http://127.0.0.1:8002")
FORBIDDEN = ("sfm_mock", "mock-real-protection", "mock_fallback", '"status":"success"')


def _request(
    method: str,
    path: str,
    body: dict | None = None,
    token: str | None = None,
    extra_headers: dict | None = None,
) -> tuple[int, dict]:
    headers = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"raw": raw}


def _register_device(device_id: str) -> str:
    _, reg = _request("POST", "/api/auth/register-device", {"deviceId": device_id})
    token = reg.get("token") or reg.get("access_token")
    if not token:
        raise RuntimeError(f"no jwt: {reg}")
    return token


def _multipart_audio(token: str, extra_headers: dict | None) -> tuple[int, dict]:
    """Minimal WAV upload — af-11 media path (sync or queued)."""
    boundary = "AntifakeSmokeBoundary"
    wav_header = (
        b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
        b"\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    )
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(b'Content-Disposition: form-data; name="file"; filename="smoke.wav"\r\n')
    body.extend(b"Content-Type: audio/wav\r\n\r\n")
    body.extend(wav_header)
    body.extend(f"\r\n--{boundary}--\r\n".encode())

    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    if extra_headers:
        headers.update(extra_headers)
    headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(
        f"{BASE}/api/antifake/check/audio",
        data=bytes(body),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"raw": raw}


def _smoke_media_job_poll(token: str, smoke_headers: dict) -> list[str]:
    failures: list[str] = []
    code, body = _multipart_audio(token, smoke_headers)
    if code not in (200, 202):
        failures.append(f"check/audio expected 200/202 got {code}: {body}")
        return failures

    status = body.get("status")
    job_id = body.get("job_id")
    if status == "completed":
        if body.get("verdict") not in ("likely_fake", "uncertain", "likely_real"):
            failures.append(f"audio sync invalid verdict {body}")
        return failures

    if status != "queued" or not job_id:
        failures.append(f"audio expected queued/completed got {body}")
        return failures

    for _ in range(30):
        poll_code, poll_body = _request(
            "GET",
            f"/api/antifake/jobs/{job_id}",
            None,
            token,
            extra_headers=smoke_headers,
        )
        if poll_code != 200:
            failures.append(f"jobs poll expected 200 got {poll_code}")
            return failures
        if poll_body.get("status") == "completed" or poll_body.get("verdict"):
            if poll_body.get("verdict") not in ("likely_fake", "uncertain", "likely_real"):
                failures.append(f"audio poll invalid verdict {poll_body}")
            return failures
        if poll_body.get("status") == "failed":
            failures.append(f"audio job failed: {poll_body}")
            return failures
        import time

        time.sleep(1)

    failures.append("audio job poll timeout")
    return failures


def main() -> int:
    failures: list[str] = []

    # OpenAPI
    _, openapi = _request("GET", "/openapi.json")
    paths = openapi.get("paths", {})
    if "/api/antifake/check/text" not in paths:
        failures.append("openapi missing /api/antifake/check/text")

    token = _register_device("antifake-smoke-free")

    # Premium gate (free user)
    code, body = _request(
        "POST",
        "/api/antifake/check/text",
        {"text": "шокирующая правда — переведите деньги срочно"},
        token,
    )
    if code != 403:
        failures.append(f"free user expected 403 got {code}: {body}")

    smoke_key = smoke_secret("ANTIFAKE_INTERNAL_SMOKE_SECRET")
    smoke_headers = {"X-Aladdin-Smoke": smoke_key} if smoke_key else None
    if not smoke_key:
        failures.append("ANTIFAKE_INTERNAL_SMOKE_SECRET not set for premium verdict smoke")

    code, body = _request(
        "POST",
        "/api/antifake/check/text",
        {"text": "шокирующая правда — переведите деньги срочно act now"},
        token,
        extra_headers=smoke_headers,
    )
    raw = json.dumps(body, ensure_ascii=False)
    for marker in FORBIDDEN:
        if marker in raw:
            failures.append(f"forbidden marker {marker} in response")

    if code != 200:
        failures.append(f"check/text expected 200 got {code}")
    else:
        verdict = body.get("verdict")
        source = body.get("source")
        if verdict not in ("likely_fake", "uncertain", "likely_real"):
            failures.append(f"invalid verdict {verdict}")
        if source in ("sfm_mock", "mock", "sfm_stub"):
            failures.append(f"mock source {source}")
        if body.get("confidence") is None:
            failures.append("missing confidence")

    code, url_body = _request(
        "POST",
        "/api/antifake/check/url",
        {"url": "http://login-secure.evil-bank.ru.com/verify-account"},
        token,
        extra_headers=smoke_headers,
    )
    if code != 200:
        failures.append(f"check/url expected 200 got {code}")
    elif url_body.get("verdict") not in ("likely_fake", "uncertain", "likely_real"):
        failures.append(f"url invalid verdict {url_body}")

    code, metrics = _request(
        "GET",
        "/api/antifake/metrics",
        None,
        token,
        extra_headers=smoke_headers,
    )
    if code != 200:
        failures.append(f"metrics expected 200 got {code}: {metrics}")
    elif "checks_total" not in metrics:
        failures.append(f"metrics missing checks_total: {metrics}")

    if os.environ.get("ANTIFAKE_SMOKE_POLL_JOB") == "1" and smoke_headers:
        failures.extend(_smoke_media_job_poll(token, smoke_headers))

    report = {"pass": len(failures) == 0, "failures": failures}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
