#!/usr/bin/env python3
"""GATE-D antifake smoke — JWT, premium gate, verdict contract (af-0-08)."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import quote

from smoke_env import smoke_secret

BASE = os.environ.get("ANTIFAKE_SMOKE_BASE", "http://127.0.0.1:8002")
SFM_BASE = os.environ.get("ANTIFAKE_SMOKE_SFM_BASE", "http://127.0.0.1:8003")
FORBIDDEN = ("sfm_mock", "mock-real-protection", "mock_fallback", '"status":"success"')
ALLOWED_VERDICTS = ("likely_fake", "uncertain", "likely_real", "insufficient_data")
# Same SLA as iOS AntifakeMediaCheckViewModel.slaSeconds — a shorter poll gives false FAIL on slow video ONNX.
MEDIA_POLL_SLA_SECONDS = {"audio": 120, "video": 300, "document": 120, "call": 180}


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


def _register_device(device_id: str, extra_headers: dict | None = None) -> str:
    _, reg = _request("POST", "/api/auth/register-device", {"deviceId": device_id}, extra_headers=extra_headers)
    token = reg.get("token") or reg.get("access_token")
    if not token:
        raise RuntimeError(f"no jwt: {reg}")
    return token


def _multipart_upload(
    path: str,
    token: str,
    extra_headers: dict | None,
    filename: str = "smoke.wav",
    form_fields: dict[str, str] | None = None,
    file_bytes: bytes | None = None,
) -> tuple[int, dict]:
    """Minimal WAV upload — af-11 / B-04 media path."""
    boundary = "AntifakeSmokeBoundary"
    wav_header = (
        b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
        b"\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    )
    payload = file_bytes if file_bytes is not None else wav_header
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode())
    body.extend(b"Content-Type: application/octet-stream\r\n\r\n")
    body.extend(payload)
    body.extend(b"\r\n")
    for key, value in (form_fields or {}).items():
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode())
        body.extend(f"{value}\r\n".encode())
    body.extend(f"--{boundary}--\r\n".encode())

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


def _smoke_media_job_poll(
    token: str,
    smoke_headers: dict,
    path: str,
    label: str,
    form_fields: dict[str, str] | None = None,
    filename: str | None = None,
    file_bytes: bytes | None = None,
) -> list[str]:
    failures: list[str] = []
    code, body = _multipart_upload(
        path,
        token,
        smoke_headers,
        filename=filename or f"smoke.{label}",
        form_fields=form_fields,
        file_bytes=file_bytes,
    )
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

    import time

    deadline = time.monotonic() + MEDIA_POLL_SLA_SECONDS.get(label, 120)
    while time.monotonic() < deadline:
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
        time.sleep(2)

    failures.append(f"{label} job poll timeout ({MEDIA_POLL_SLA_SECONDS.get(label, 120)}s SLA)")
    return failures


def _smoke_web_trial_path(failures: list[str]) -> None:
    """T1-03: web trial API contract + text check when trial/premium active."""
    web_headers = {"X-Aladdin-Client": "web"}
    token = _register_device("antifake-smoke-web-trial", web_headers)

    code, access = _request("GET", "/api/antifake/web/access", None, token, extra_headers=web_headers)
    if code != 200:
        failures.append(f"web/access expected 200 got {code}: {access}")
        return
    for key in ("access", "premium_required", "paid"):
        if key not in access:
            failures.append(f"web/access missing {key}: {access}")

    code, trial_body = _request("POST", "/api/antifake/web/start-trial", None, token, extra_headers=web_headers)
    if code == 200:
        if not trial_body.get("started") and trial_body.get("reason") not in (
            "trial_already_active",
            "already_premium",
        ):
            failures.append(f"web/start-trial unexpected 200 body: {trial_body}")
    elif code == 403:
        detail = trial_body.get("detail")
        if detail not in ("trial_already_used", "web_trial_disabled", "web_client_required"):
            failures.append(f"web/start-trial unexpected 403 detail: {trial_body}")
    elif code == 429:
        detail = trial_body.get("detail")
        if not isinstance(detail, dict) or detail.get("error") != "trial_ip_limit":
            failures.append(f"web/start-trial unexpected 429: {trial_body}")
    else:
        failures.append(f"web/start-trial expected 200/403/429 got {code}: {trial_body}")

    code, access_after = _request("GET", "/api/antifake/web/access", None, token, extra_headers=web_headers)
    if code != 200:
        failures.append(f"web/access after trial expected 200 got {code}")
        return

    if access_after.get("access"):
        code, txt = _request(
            "POST",
            "/api/antifake/check/text",
            {"text": "проверка trial smoke — нейтральный текст без триггеров"},
            token,
            extra_headers=web_headers,
            timeout=90,
        )
        if code != 200:
            failures.append(f"web trial text check expected 200 got {code}: {txt}")
        elif txt.get("verdict") not in ALLOWED_VERDICTS:
            failures.append(f"web trial text invalid verdict {txt}")


def _smoke_slo_thresholds(failures: list[str], metrics: dict) -> None:
    """T1-05: SLO text p95 < 8s, media p95 < 120s (when metrics populated)."""
    sla = metrics.get("sla_ms") or {}
    text_sla = int(sla.get("text") or 8000)
    media_sla = int(sla.get("media") or 120000)
    p95 = int(metrics.get("latency_p95_ms") or 0)
    checks = int(metrics.get("checks_total") or 0)
    if checks <= 0:
        return
    if p95 > 0 and p95 > media_sla:
        failures.append(f"T1-05 latency_p95_ms {p95} > media sla {media_sla}")
    if text_sla != 8000 or media_sla != 120000:
        failures.append(f"T1-05 unexpected sla_ms defaults text={text_sla} media={media_sla}")


def main() -> int:
    failures: list[str] = []

    # OpenAPI — must list antifake routes (fixed via AntifakeSettingsUpdateRequest)
    code_oa, openapi = _request("GET", "/openapi.json")
    paths = openapi.get("paths", {}) if isinstance(openapi, dict) else {}
    if code_oa != 200:
        failures.append(f"openapi expected 200 got {code_oa}: {openapi}")
    else:
        if "/api/antifake/check/text" not in paths:
            failures.append("openapi missing /api/antifake/check/text")
        for media_path in (
            "/api/antifake/check/audio",
            "/api/antifake/check/video",
            "/api/antifake/check/document",
            "/api/antifake/call/analyze",
            "/api/antifake/settings",
        ):
            if media_path not in paths:
                failures.append(f"openapi missing {media_path}")
            elif media_path.startswith("/api/antifake/check/") or media_path.endswith(
                "/analyze"
            ):
                post = (paths[media_path].get("post") or {})
                responses = post.get("responses") or {}
                if "202" not in responses and "200" not in responses:
                    failures.append(f"B-03 openapi {media_path} missing 202/200 response")

    # Media quota is 10/h per device; one wrapper run (1 try + 2 retries) needs 12 media checks.
    smoke_device_id = os.environ.get("ANTIFAKE_SMOKE_DEVICE_ID") or (
        "antifake-smoke-free-" + time.strftime("%Y%m%d%H%M%S", time.gmtime())
    )
    token = _register_device(smoke_device_id)

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
        # Q-06 RH-B05: golden scam — verdict correctness (not source=real_agent)
        if verdict != "likely_fake":
            failures.append(
                f"Q-06 golden scam expected likely_fake got {verdict!r} conf={body.get('confidence')}"
            )
        if source in ("sfm_mock", "mock", "sfm_stub"):
            failures.append(f"Q-06 mock source {source}")
        # RH-A06: stub must never masquerade
        reasons = body.get("reasons") or []
        if reasons == ["sfm_agent"] or "sfm_executed_stub" in reasons:
            failures.append(f"Q-A06 stub reasons in golden text: {reasons}")
        if '"status": "executed"' in raw or '"status":"executed"' in raw:
            failures.append("Q-A06 status executed leaked into client response")

        # Q-07 RH-B05: SMS mode scam — rules primary
        code_sms, sms_body = _request(
            "POST",
            "/api/antifake/check/text",
            {
                "text": "Служба безопасности: ваш счёт заблокирован, сообщите код подтверждения",
                "mode": "sms",
            },
            token,
            extra_headers=smoke_headers,
            timeout=90,
        )
        if code_sms != 200:
            failures.append(f"Q-07 sms check expected 200 got {code_sms}")
        elif sms_body.get("verdict") == "likely_real":
            failures.append(
                f"Q-07 sms scam must not be likely_real got {sms_body.get('verdict')!r}"
            )
        elif sms_body.get("verdict") != "likely_fake":
            failures.append(
                f"Q-07 sms scam expected likely_fake got {sms_body.get('verdict')!r}"
            )

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
        elif not any(
            "text_too_short" in str(r) for r in (short_body.get("reasons") or [])
        ):
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
    else:
        # RH-C03: lookalike / phishing path golden
        if url_body.get("verdict") != "likely_fake":
            failures.append(
                f"C03 lookalike URL expected likely_fake got {url_body.get('verdict')!r}"
            )
        if (url_body.get("reasons") or []) == ["sfm_agent"]:
            failures.append("C03/A06 URL stub reasons sfm_agent")
        if url_body.get("source") in ("sfm_mock", "mock", "sfm_stub"):
            failures.append(f"C03 forbidden url source {url_body.get('source')}")

    code, bank_body = _request(
        "POST",
        "/api/antifake/check/url",
        {"url": "https://www.sberbank.ru/"},
        token,
        extra_headers=smoke_headers,
    )
    if code != 200:
        failures.append(f"C03 bank allowlist url expected 200 got {code}")
    elif bank_body.get("verdict") == "likely_fake":
        failures.append(
            f"C03 allowlisted bank must not be likely_fake got {bank_body}"
        )

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
    else:
        # RH-H04
        if "stub_rate" not in metrics:
            failures.append(f"H04 metrics missing stub_rate: {metrics}")
        elif float(metrics.get("stub_rate") or 0) > 0:
            failures.append(f"H04 stub_rate must be 0 got {metrics.get('stub_rate')}")
        if "verdict_distribution" not in metrics:
            failures.append(f"H04 metrics missing verdict_distribution: {metrics}")
        if "latency_by_type_ms" not in metrics:
            failures.append(f"H04 metrics missing latency_by_type_ms: {metrics}")
        _smoke_slo_thresholds(failures, metrics)

    _smoke_web_trial_path(failures)

    if smoke_headers:
        failures.extend(
            _smoke_media_job_poll(token, smoke_headers, "/api/antifake/check/audio", "audio")
        )
        failures.extend(
            _smoke_media_job_poll(token, smoke_headers, "/api/antifake/check/video", "video")
        )
        failures.extend(
            _smoke_media_job_poll(
                token,
                smoke_headers,
                "/api/antifake/check/document",
                "document",
                filename="smoke.jpg",
                file_bytes=b"\xff\xd8\xff\xe0" + b"\x00" * 512,
            )
        )
        failures.extend(
            _smoke_media_job_poll(
                token,
                smoke_headers,
                "/api/antifake/call/analyze",
                "call",
                form_fields={"caller_id": "74951234567"},
            )
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
