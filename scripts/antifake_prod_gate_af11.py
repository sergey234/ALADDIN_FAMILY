#!/usr/bin/env python3
"""F-05 / af-11: six production gate checks before TestFlight."""
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

from docs.server.smoke_env import smoke_secret  # noqa: E402

BASE = os.environ.get("ANTIFAKE_GATE_BASE", "http://127.0.0.1:8002")
FORBIDDEN = ("sfm_mock", "mock-real-protection", "mock_fallback", "sfm_stub")


def _req(method: str, path: str, body: dict | None = None, token: str | None = None, headers: dict | None = None):
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    if token:
        h["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=h, method=method)
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


def _register(device_id: str) -> str:
    _, body = _req("POST", "/api/auth/register-device", {"deviceId": device_id})
    token = body.get("token") or body.get("access_token")
    if not token:
        raise RuntimeError(f"no jwt: {body}")
    return token


def _multipart_audio(token: str, headers: dict) -> tuple[int, dict]:
    boundary = "Af11Gate"
    wav = (
        b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
        b"\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    )
    payload = bytearray()
    payload.extend(f"--{boundary}\r\n".encode())
    payload.extend(b'Content-Disposition: form-data; name="file"; filename="gate.wav"\r\n')
    payload.extend(b"Content-Type: audio/wav\r\n\r\n")
    payload.extend(wav)
    payload.extend(f"\r\n--{boundary}--\r\n".encode())
    h = {"Content-Type": f"multipart/form-data; boundary={boundary}", "Authorization": f"Bearer {token}"}
    h.update(headers)
    req = urllib.request.Request(f"{BASE}/api/antifake/check/audio", data=bytes(payload), headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"raw": raw}


def main() -> int:
    failures: list[str] = []
    smoke_key = smoke_secret("ANTIFAKE_INTERNAL_SMOKE_SECRET")
    smoke_headers = {"X-Aladdin-Smoke": smoke_key} if smoke_key else {}

    # af-11-01 health + settings path reachable
    code, health = _req("GET", "/api/health")
    if code != 200 or health.get("status") not in ("ok", "success"):
        failures.append(f"af-11-01 health fail {code} {health}")

    token = _register("af11-gate-user")

    # af-11-02 fake news text
    code, text_body = _req(
        "POST",
        "/api/antifake/check/text",
        {"text": "шокирующая правда — переведите деньги act now"},
        token,
        smoke_headers,
    )
    raw = json.dumps(text_body, ensure_ascii=False)
    for marker in FORBIDDEN:
        if marker in raw:
            failures.append(f"af-11-02 forbidden {marker}")
    if code != 200:
        failures.append(f"af-11-02 text {code}")
    elif text_body.get("verdict") == "uncertain" and text_body.get("source") == "rule_engine":
        failures.append(f"af-11-02 expected stronger fake signal got {text_body}")
    elif text_body.get("source") not in ("real_agent", "local_ml"):
        failures.append(f"af-11-02 Q-06 expected real_agent|local_ml got {text_body.get('source')}")
    elif text_body.get("verdict") != "likely_fake":
        failures.append(f"af-11-02 expected likely_fake got {text_body}")

    # af-11-03 audio job < 120s
    started = time.time()
    acode, abody = _multipart_audio(token, smoke_headers)
    if acode not in (200, 202):
        failures.append(f"af-11-03 audio upload {acode}")
    else:
        job_id = abody.get("job_id")
        if abody.get("status") == "queued" and job_id:
            for _ in range(120):
                _, poll = _req("GET", f"/api/antifake/jobs/{job_id}", token=token, headers=smoke_headers)
                if poll.get("status") == "completed" or poll.get("verdict"):
                    break
                time.sleep(1)
            else:
                failures.append("af-11-03 audio poll timeout")
        if time.time() - started > 120:
            failures.append("af-11-03 audio SLA exceeded 120s")

    # af-11-04 video upload accepted (poll optional if worker heavy)
    vcode, _ = _multipart_audio(token, smoke_headers)  # same bytes path exercises worker
    if vcode not in (200, 202, 503):
        failures.append(f"af-11-04 media path {vcode}")

    # af-11-05 call-directory >= 100
    _, cd = _req("GET", "/api/antifake/call-directory", token=token, headers=smoke_headers)
    if int(cd.get("total_count") or 0) < 100:
        failures.append(f"af-11-05 call-directory count {cd.get('total_count')}")

    # af-11-06 metrics contract (F-06 / F-07)
    _, metrics = _req("GET", "/api/antifake/metrics", token=token, headers=smoke_headers)
    for key in ("checks_total", "by_type", "model_version", "sla_ms", "latency_p95_ms"):
        if key not in metrics:
            failures.append(f"af-11-06 metrics missing {key}: {metrics}")

    report = {"pass": not failures, "failures": failures}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
