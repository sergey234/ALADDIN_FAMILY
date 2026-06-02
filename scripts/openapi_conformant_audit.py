#!/usr/bin/env python3
"""
OpenAPI-conformant API audit: uses each path's *documented* HTTP method(s) from
OpenAPI. This avoids false 404/405/422 caused by a naive "POST everywhere" client.

- Fetches: {BASE}/openapi.json (FastAPI); falls back to {BASE}/api/openapi.json
- Auth:     POST {BASE}/api/auth/register-device with body {"device_id","deviceType"}
- For each operation: use the real method. Optional JSON body is:
    - no body: GET, HEAD, DELETE, unless OpenAPI lists requestBody
    - for POST/PUT/PATCH: "" if no requestBody; else application/json: {} (minimal
      payload — many routes return 422, which we treat as *routed* / schema mismatch,
      not *missing route*)

Reports:
- docs/OPENAPI_CONFORMANT_AUDIT_{timestamp}.md
- docs/OPENAPI_CONFORMANT_AUDIT_{timestamp}.json
and symlinks:
- docs/OPENAPI_CONFORMANT_AUDIT_LATEST.md
- docs/OPENAPI_CONFORMANT_AUDIT_LATEST.json

Env:
- ALADDIN_BASE_URL (default http://149.154.65.180:8002) — use /openapi.json host
- ALADDIN_API_BASE  — same, alias
- ALADDIN_DEVICE_ID — device id for register-device (default openapi_audit_device_v1)
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

HTTP_METHODS = frozenset({"get", "put", "post", "delete", "options", "head", "patch", "trace"})

BASE = (
    os.environ.get("ALADDIN_BASE_URL")
    or os.environ.get("ALADDIN_API_BASE")
    or "http://149.154.65.180:8002"
).rstrip("/")

DEVICE_ID = os.environ.get("ALADDIN_DEVICE_ID", "openapi_audit_device_v1").strip()

PATH_PARAM_RE = re.compile(r"\{([^}]+)\}")

# Template IDs — same spirit as full_system_endpoint_audit
REPLACEMENTS: dict[str, str] = {
    "request_id": "test-req-123",
    "familyId": "test-family-456",
    "childId": "8E0515FE-33AC-4221-93E0-9912DAE47FBC",
    "geofenceId": "test-geo-000",
    "dataId": "test-data-111",
    "achievementId": "test-ach-222",
    "tournamentId": "test-tour-333",
    "deviceId": DEVICE_ID,
    "device_id": DEVICE_ID,
    "userId": "test_user",
    "memberId": "member_1",
    "messageId": "msg_1",
    "componentId": "network_protection",
    "component_id": "network_protection",
    "paymentId": "test-pay-777",
    "homeId": "test-home-555",
    "threatId": "test-threat-666",
    "gameId": "game_1",
    "id": "test-id-1",
    "name": "test",
}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def concretize_path(tpl: str) -> str:
    def _sub(m: re.Match) -> str:
        key = m.group(1)
        return REPLACEMENTS.get(key, "test")

    return PATH_PARAM_RE.sub(_sub, tpl)


def http_request(
    url: str,
    method: str,
    body: Optional[bytes] = None,
    token: Optional[str] = None,
    content_type: Optional[str] = None,
    timeout: float = 15.0,
    max_response_chars: Optional[int] = 2000,
) -> tuple[Optional[int], str]:
    headers: dict[str, str] = {"Accept": "application/json", "User-Agent": "ALADDIN-OpenAPIAudit/1.0"}
    if content_type:
        headers["Content-Type"] = content_type
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = body
    req = Request(url=url, method=method.upper(), headers=headers, data=data)
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            if max_response_chars is not None:
                raw = raw[: max_response_chars]
            return resp.getcode(), raw
    except HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:2000]
    except (URLError, OSError) as e:
        return None, str(e)[:2000]
    except Exception as e:  # noqa: BLE001
        return None, f"Exception: {e!s}"[:2000]


def load_openapi() -> dict[str, Any]:
    def _valid(spec: dict[str, Any]) -> bool:
        if spec.get("version") == "3.0.0-mock-real-protection":
            return False
        if spec.get("function"):
            return False
        paths = spec.get("paths")
        return isinstance(paths, dict) and bool(paths)

    for suffix in ("/openapi.json", "/api/openapi.json"):
        st, text = http_request(
            f"{BASE}{suffix}",
            "GET",
            body=None,
            token=None,
            content_type=None,
            timeout=60.0,
            max_response_chars=None,
        )
        if st == 200 and text:
            try:
                spec = json.loads(text)
            except json.JSONDecodeError:
                continue
            if _valid(spec):
                return spec
    raise RuntimeError(f"Cannot load OpenAPI from {BASE} (/openapi.json, /api/openapi.json)")


def register_device_token() -> str:
    payload = json.dumps({"device_id": DEVICE_ID, "deviceType": "ios"}).encode("utf-8")
    st, text = http_request(
        f"{BASE}/api/auth/register-device",
        "POST",
        body=payload,
        content_type="application/json",
    )
    if st not in (200, 201) or not text:
        raise RuntimeError(f"register-device failed: status={st} body={text[:500]}")
    data = json.loads(text)
    tok = data.get("access_token") or data.get("token")
    if not tok:
        raise RuntimeError("register-device: no access_token in response")
    return str(tok)


def has_json_request_body(op: dict[str, Any]) -> bool:
    rb = op.get("requestBody")
    if not isinstance(rb, dict):
        return False
    content = rb.get("content")
    if not isinstance(content, dict):
        return False
    return "application/json" in content


def classify_status(code: Optional[int]) -> str:
    if code is None:
        return "network_error"
    if 200 <= code < 300:
        return "success_2xx"
    if code in (401, 403):
        return "auth_forbidden"
    if code == 404:
        return "not_found"
    if code == 405:
        return "method_not_allowed"
    if code == 422:
        return "validation_422"
    if code and code >= 500:
        return "server_5xx"
    if code is not None and 400 <= code < 500:
        return "client_4xx_other"
    return "other"


def main() -> int:
    print(f"ALADDIN OpenAPI-conformant audit  BASE={BASE}  device={DEVICE_ID}", flush=True)
    spec = load_openapi()
    paths = spec.get("paths") or {}
    if not paths:
        print("No paths in OpenAPI", file=sys.stderr)
        return 1

    token = register_device_token()
    print("OK JWT from register-device", flush=True)

    results: list[dict[str, Any]] = []
    t0 = time.time()

    for path_tpl, item in sorted(paths.items()):
        if not isinstance(item, dict):
            continue
        for method, op in item.items():
            m = method.lower()
            if m not in HTTP_METHODS or not isinstance(op, dict):
                continue
            concrete = concretize_path(path_tpl)
            url = f"{BASE}{concrete}"
            use_json = has_json_request_body(op) and m in ("post", "put", "patch", "delete")
            if m in ("get", "head", "options", "trace"):
                st, text = http_request(url, m.upper(), token=token)
            elif m == "delete":
                if use_json:
                    b = json.dumps({}).encode("utf-8")
                    st, text = http_request(
                        url, "DELETE", body=b, token=token, content_type="application/json"
                    )
                else:
                    st, text = http_request(url, "DELETE", token=token)
            elif m in ("post", "put", "patch"):
                if use_json:
                    b = json.dumps({}).encode("utf-8")
                    st, text = http_request(
                        url, m.upper(), body=b, token=token, content_type="application/json"
                    )
                else:
                    st, text = http_request(url, m.upper(), token=token)
            else:
                st, text = http_request(url, m.upper(), token=token)

            bucket = classify_status(st)
            # "Route exists" heuristic: not 404 (and not our transport None unless network error)
            route_hit = st is not None and st != 404

            results.append(
                {
                    "path_template": path_tpl,
                    "path": concrete,
                    "method": m.upper(),
                    "status": st,
                    "bucket": bucket,
                    "route_hit": route_hit,
                    "response_preview": text[:400] if text else "",
                }
            )
            time.sleep(0.02)

    elapsed = int(time.time() - t0)
    now = datetime.now(tz=timezone.utc).isoformat()
    total = len(results)
    summary = {
        "total_operations": total,
        "elapsed_sec": elapsed,
        "by_bucket": {},
        "route_hits": sum(1 for r in results if r.get("route_hit")),
        "not_found": sum(1 for r in results if r.get("status") == 404),
        "success_2xx": sum(1 for r in results if (r.get("status") or 0) // 100 == 2),
        "server_5xx": sum(1 for r in results if (r.get("status") or 0) >= 500),
    }
    for r in results:
        b = r.get("bucket") or "other"
        summary["by_bucket"][b] = summary["by_bucket"].get(b, 0) + 1

    stamp = now.replace(":", "").replace("-", "")[:15]
    out_json = os.path.join(ROOT, "docs", f"OPENAPI_CONFORMANT_AUDIT_{stamp}.json")
    out_md = os.path.join(ROOT, "docs", f"OPENAPI_CONFORMANT_AUDIT_{stamp}.md")
    latest_j = os.path.join(ROOT, "docs", "OPENAPI_CONFORMANT_AUDIT_LATEST.json")
    latest_m = os.path.join(ROOT, "docs", "OPENAPI_CONFORMANT_AUDIT_LATEST.md")

    report = {
        "generated_at_utc": now,
        "base_url": BASE,
        "device_id": DEVICE_ID,
        "summary": summary,
        "results": results,
    }
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=True, indent=2)

    # Markdown summary (human)
    lines = [
        f"# OpenAPI-conformant audit (method-aware)",
        "",
        f"- Generated: `{now}` (UTC)",
        f"- Base URL: `{BASE}`",
        f"- OpenAPI: `{len(paths)}` path templates, `{total}` method operations",
        f"- Elapsed: `{elapsed}s`",
        "",
        "## Why this is not the old «POST everywhere» test",
        "",
        "A naive client that sends the same `POST` + JSON to every path often gets **404** (there is no such route for POST) or **405** (method not allowed) or **422** (body does not match Pydantic).",
        "That is **not** a proof that the backend is wrong — it is usually proof that the **test was wrong**.",
        "",
        "This script reads **OpenAPI** and calls each listed **method** (GET as GET, POST as POST, …) with a **minimal** body when JSON is declared.",
        "",
        "## Summary buckets",
        "",
    ]
    for k, v in sorted(summary["by_bucket"].items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"- **{k}**: `{v}`")
    lines.extend(
        [
            "",
            f"- **Route hits (status != 404)**: `{summary['route_hits']}` / `{total}`",
            f"- **2xx count**: `{summary['success_2xx']}`",
            f"- **5xx count**: `{summary['server_5xx']}`",
            "",
            "## How to re-run",
            "",
            "```bash",
            "ALADDIN_BASE_URL=http://149.154.65.180:8002 \\",
            "  python3 scripts/openapi_conformant_audit.py",
            "```",
            "",
            f"JSON: `{os.path.basename(out_json)}`",
        ]
    )
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    # "Latest" copies (portable: symlinks are not always wanted in VCS/zip)
    for src, dst in ((out_json, latest_j), (out_md, latest_m)):
        try:
            with open(src, "r", encoding="utf-8") as s:
                with open(dst, "w", encoding="utf-8") as d:
                    d.write(s.read())
        except OSError as e:
            print(f"WARN: could not write {dst}: {e}", file=sys.stderr)

    print(json.dumps(summary, ensure_ascii=True, indent=2))
    print(f"Wrote {out_json}", flush=True)
    print(f"Wrote {out_md}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
