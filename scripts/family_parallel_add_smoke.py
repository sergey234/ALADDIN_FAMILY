#!/usr/bin/env python3
"""
Stress smoke for family roster race-safety.

Runs N parallel POST /api/family/add requests and verifies that:
- successful adds do not exceed available roster slots
- overflow attempts are rejected with 409 family_roster_full
- final server stats remain within roster max
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import sys
import time
import urllib.error
import urllib.request


def _request_json(url: str, method: str, token: str, body: dict | None = None, extra_headers: dict | None = None) -> tuple[int, str]:
    payload = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url=url, data=payload, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read().decode("utf-8", errors="replace")
            return resp.getcode(), data
    except urllib.error.HTTPError as exc:
        data = exc.read().decode("utf-8", errors="replace")
        return exc.code, data


def _get_stats(base: str, token: str, family_id: str) -> dict:
    code, body = _request_json(
        f"{base}/api/family/stats",
        "GET",
        token,
        body=None,
        extra_headers={"X-Family-Id": family_id},
    )
    if code != 200:
        raise RuntimeError(f"GET /api/family/stats failed: status={code} body={body[:400]}")
    parsed = json.loads(body)
    if not isinstance(parsed, dict):
        raise RuntimeError("Invalid stats payload: expected object")
    return parsed


def _add_member(base: str, token: str, family_id: str, idx: int) -> tuple[int, str]:
    unique_name = f"SMOKE_PAR_{int(time.time())}_{idx}"
    body = {"name": unique_name, "role": "child", "familyId": family_id}
    return _request_json(
        f"{base}/api/family/add",
        "POST",
        token,
        body=body,
        extra_headers={"Idempotency-Key": f"smoke-parallel-{unique_name}"},
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Parallel /api/family/add smoke")
    parser.add_argument("--base", required=True, help="API base URL, e.g. https://aladdin-ai.ru")
    parser.add_argument("--token", required=True, help="Bearer JWT")
    parser.add_argument("--family-id", required=True, help="Target family id")
    parser.add_argument("--attempts", type=int, default=20, help="Parallel add attempts")
    parser.add_argument("--workers", type=int, default=20, help="ThreadPool worker count")
    args = parser.parse_args()

    base = args.base.rstrip("/")
    before = _get_stats(base, args.token, args.family_id)
    before_used = int(before.get("familyRosterUsed") or before.get("totalMembers") or 0)
    before_max = int(before.get("familyRosterMax") or 0)
    if before_max <= 0:
        raise RuntimeError(f"familyRosterMax missing/invalid in stats: {before}")

    allowed_now = max(0, before_max - before_used)
    print(f"SMOKE START: used={before_used} max={before_max} available={allowed_now} attempts={args.attempts}")

    statuses: list[tuple[int, str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(_add_member, base, args.token, args.family_id, i) for i in range(args.attempts)]
        for f in concurrent.futures.as_completed(futures):
            statuses.append(f.result())

    ok_200 = 0
    deny_409 = 0
    other = 0
    for code, body in statuses:
        if code == 200:
            ok_200 += 1
        elif code == 409 and "family_roster_full" in body:
            deny_409 += 1
        else:
            other += 1

    after = _get_stats(base, args.token, args.family_id)
    after_used = int(after.get("familyRosterUsed") or after.get("totalMembers") or 0)
    after_max = int(after.get("familyRosterMax") or 0)

    print(f"RESULTS: 200={ok_200} 409_full={deny_409} other={other}")
    print(f"STATS AFTER: used={after_used} max={after_max}")

    if after_max != before_max:
        raise RuntimeError(f"Unexpected roster max drift: before={before_max} after={after_max}")
    if after_used > after_max:
        raise RuntimeError(f"Roster overflow detected: used={after_used} max={after_max}")
    if ok_200 > allowed_now:
        raise RuntimeError(
            f"Too many successful adds: ok={ok_200} available_before={allowed_now} (race protection failure)"
        )
    if other > 0:
        raise RuntimeError(f"Unexpected non-contract responses encountered: other={other}")

    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
