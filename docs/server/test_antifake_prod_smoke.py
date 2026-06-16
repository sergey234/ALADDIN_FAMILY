#!/usr/bin/env python3
"""GATE-D antifake smoke — JWT, premium gate, verdict contract (af-0-08)."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from urllib.parse import quote

from smoke_env import smoke_secret

BASE = os.environ.get("ANTIFAKE_SMOKE_BASE", "http://127.0.0.1:8002")
SFM_BASE = os.environ.get("ANTIFAKE_SMOKE_SFM_BASE", "http://127.0.0.1:8003")
FORBIDDEN = ("sfm_mock", "mock-real-protection", "mock_fallback", '"status":"success"')
ALLOWED_VERDICTS = ("likely_fake", "uncertain", "likely_real", "insufficient_data")


def _request(
    method: str,
    path: str,
    body: dict | None = None,
    token: str | None = None,
    extra_headers: dict | None = None,
    timeout: int = 20,
) -> tuple[int, dict]:
    headers = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"raw": raw}


def _sfm_status() -> tuple[int, dict]:
    req = urllib.request.Request(f"{SFM_BASE}/api/sfm/status", method="GET")
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


def _multipart_upload(
    path: str,
    token: str,
    extra_headers: dict | None,
    filename: str = "smoke.wav",
) -> tuple[int, dict]:
    """Minimal WAV upload — af-11 / B-04 media path."""
    boundary = "AntifakeSmokeBoundary"
    wav_header = (
        b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
        b"\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    )
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode())
    body.extend(b"Content-Type: application/octet-stream\r\n\r\n")
    body.extend(wav_header)
    body.extend(f"\r\n--{boundary}--\r\n".encode())

    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    if extra_headers:
        headers.update(extra_headers)
    headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(
        f"{BASE}{path}",
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


def _multipart_audio(token: str, extra_headers: dict | None) -> tuple[int, dict]:
    return _multipart_upload("/api/antifake/check/audio", token, extra_headers)


def _smoke_media_job_poll(token: str, smoke_headers: dict, path: str, label: str) -> list[str]:
    failures: list[str] = []
    code, body = _multipart_upload(path, token, smoke_headers, filename=f"smoke.{label}")
    if code not in (200, 202):
        failures.append(f"check/{label} expected 200/202 got {code}: {body}")
        return failures

    status = body.get("status")
    job_id = body.get("job_id")
    if status == "completed":
        if body.get("verdict") not in ALLOWED_VERDICTS:
            failures.append(f"{label} sync invalid verdict {body}")
        return failures

    if status != "queued" or not job_id:
        failures.append(f"{label} expected queued/completed got {body}")
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
            failures.append(f"{label} jobs poll expected 200 got {poll_code}")
            return failures
        if poll_body.get("status") == "completed" or poll_body.get("verdict"):
            if poll_body.get("verdict") not in ALLOWED_VERDICTS:
                failures.append(f"{label} poll invalid verdict {poll_body}")
            return failures
        if poll_body.get("status") == "failed":
            failures.append(f"{label} job failed: {poll_body}")
            return failures
        import time

        time.sleep(1)

    failures.append(f"{label} job poll timeout")
    return failures


def main() -> int:
    failures: list[str] = []

    # OpenAPI
    _, openapi = _request("GET", "/openapi.json")
    paths = openapi.get("paths", {})
    if "/api/antifake/check/text" not in paths:
        failures.append("openapi missing /api/antifake/check/text")
    for media_path in (
        "/api/antifake/check/audio",
        "/api/antifake/check/video",
        "/api/antifake/check/document",
        "/api/antifake/call/analyze",
    ):
        if media_path not in paths:
            failures.append(f"openapi missing {media_path}")
        else:
            post = paths[media_path].get("post") or {}
            responses = post.get("responses") or {}
            if "202" not in responses and "200" not in responses:
                failures.append(f"B-03 openapi {media_path} missing 202/200 response")

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

    sfm_loaded = False
    _, sfm_body = _sfm_status()
    sfm_loaded = bool(sfm_body.get("sfm_loaded"))
    if not sfm_loaded:
        failures.append(f"B-11 sfm_loaded expected true got {sfm_body!r}")
    else:
        active = int(sfm_body.get("active_executions") or 0)
        max_c = sfm_body.get("max_concurrent_functions")
        if max_c is not None and active >= int(max_c):
            failures.append(f"B-11 active_executions {active} >= max {max_c}")

    code, body = _request(
        "POST",
        "/api/antifake/check/text",
        {"text": "шокирующая правда — переведите деньги срочно act now"},
        token,
        extra_headers=smoke_headers,
        timeout=90,
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
        if verdict not in ALLOWED_VERDICTS:
            failures.append(f"invalid verdict {verdict}")
        if source in ("sfm_mock", "mock", "sfm_stub"):
            failures.append(f"mock source {source}")
        if body.get("confidence") is None:
            failures.append("missing confidence")
        if body.get("fake_risk") is None:
            failures.append("missing fake_risk")
        # Q-06: golden scam must use AI path + strong verdict when SFM healthy or local_ml fallback
        if source not in ("real_agent", "local_ml"):
            failures.append(f"Q-06 golden scam expected real_agent|local_ml got {source!r}")
        if verdict != "likely_fake":
            failures.append(f"Q-06 golden scam expected likely_fake got {verdict!r} conf={body.get('confidence')}")
        if sfm_loaded and source != "real_agent":
            failures.append(f"Q-07 sfm_loaded true but golden scam source={source!r} expected real_agent")

    if smoke_headers:
        code, short_body = _request(
            "POST",
            "/api/antifake/check/text",
            {"text": "12+12=24", "mode": "news"},
            token,
            extra_headers=smoke_headers,
            timeout=90,
        )
        if code != 200:
            failures.append(f"Q-08 short text expected 200 got {code}: {short_body}")
        elif short_body.get("verdict") != "insufficient_data":
            failures.append(
                f"Q-08 short neutral text expected insufficient_data got {short_body.get('verdict')!r}"
            )
        elif short_body.get("fake_risk") not in (0, 0.0):
            failures.append(f"Q-08 short text expected fake_risk=0 got {short_body.get('fake_risk')}")
        elif "text_too_short" not in (short_body.get("reasons") or []):
            failures.append(f"Q-08 short text missing text_too_short reason: {short_body}")

    code, url_body = _request(
        "POST",
        "/api/antifake/check/url",
        {"url": "http://login-secure.evil-bank.ru.com/verify-account"},
        token,
        extra_headers=smoke_headers,
    )
    if code != 200:
        failures.append(f"check/url expected 200 got {code}")
    elif url_body.get("verdict") not in ALLOWED_VERDICTS:
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
    elif "funnel" not in metrics:
        failures.append(f"M-02 metrics missing funnel: {metrics}")
    elif "model_version" not in metrics or "sla_ms" not in metrics:
        failures.append(f"F-06 metrics missing model_version/sla_ms: {metrics}")

    if os.environ.get("ANTIFAKE_SMOKE_POLL_JOB") == "1" and smoke_headers:
        failures.extend(
            _smoke_media_job_poll(token, smoke_headers, "/api/antifake/check/audio", "audio")
        )
        failures.extend(
            _smoke_media_job_poll(token, smoke_headers, "/api/antifake/check/video", "video")
        )

    if smoke_headers:
        code, cd_body = _request(
            "GET",
            "/api/antifake/call-directory",
            None,
            token,
            extra_headers=smoke_headers,
        )
        if code != 200:
            failures.append(f"call-directory expected 200 got {code}: {cd_body}")
        else:
            if not isinstance(cd_body.get("identified"), list):
                failures.append(f"call-directory missing identified[]: {cd_body}")
            if not isinstance(cd_body.get("blocked"), list):
                failures.append(f"call-directory missing blocked[]: {cd_body}")
            if cd_body.get("total_count") is None:
                failures.append(f"call-directory missing total_count: {cd_body}")
            total = int(cd_body.get("total_count") or 0)
            if total < 100:
                failures.append(f"C-08 call-directory total_count {total} < 100")
            if cd_body.get("max_entries") is None:
                failures.append(f"C-10 call-directory missing max_entries: {cd_body}")
            qa_phones = {"74951234567", "78005553535", "79001234567"}
            synced_phones = {
                "".join(ch for ch in str(item.get("phone", "")) if ch.isdigit())
                for item in cd_body.get("identified", [])
                if isinstance(item, dict)
            }
            synced_phones.update(
                "".join(ch for ch in str(phone) if ch.isdigit())
                for phone in cd_body.get("blocked", [])
            )
            missing_qa = qa_phones - synced_phones
            if missing_qa:
                failures.append(f"C-11 QA numbers missing from call-directory: {sorted(missing_qa)}")
            updated_at = cd_body.get("updated_at")
            if updated_at:
                since_q = quote(str(updated_at), safe="")
                code_delta, delta_body = _request(
                    "GET",
                    f"/api/antifake/call-directory?since={since_q}",
                    None,
                    token,
                    extra_headers=smoke_headers,
                )
                if code_delta != 200:
                    failures.append(f"C-09 delta since expected 200 got {code_delta}: {delta_body}")
                elif not isinstance(delta_body.get("identified"), list):
                    failures.append(f"C-09 delta missing identified[]: {delta_body}")

    report = {"pass": len(failures) == 0, "failures": failures}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
