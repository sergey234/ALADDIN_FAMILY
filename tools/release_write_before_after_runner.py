#!/usr/bin/env python3
import json
import os
import shlex
import subprocess
import time
import uuid
from pathlib import Path
from typing import Optional

import requests


BASE_URL = os.environ.get("ALADDIN_API_BASE", "https://aladdin-ai.ru").rstrip("/")
SSH_HOST = os.environ.get("ALADDIN_SSH_HOST", "149.154.65.180")
SSH_USER = os.environ.get("ALADDIN_SSH_USER", "root")
SSH_PASS = os.environ.get("ALADDIN_SSH_PASS", "")
DB_NAME = os.environ.get("ALADDIN_DB_NAME", "aladdin_db")
OUT_PATH = Path(
    os.environ.get(
        "ALADDIN_WRITE_BEFORE_AFTER_REPORT",
        "docs/release/gates/write-before-after-report.json",
    )
)


def _run_sql(sql: str) -> str:
    if not SSH_PASS:
        raise RuntimeError("ALADDIN_SSH_PASS is required")
    remote = (
        f"sudo -u postgres psql -d {shlex.quote(DB_NAME)} -At -F '|' "
        f"-c {shlex.quote(sql)}"
    )
    cmd = [
        "sshpass",
        "-p",
        SSH_PASS,
        "ssh",
        "-o",
        "StrictHostKeyChecking=no",
        f"{SSH_USER}@{SSH_HOST}",
        remote,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return (res.stdout or "").strip()


def _sql_literal(value: str) -> str:
    # Dollar-quoting avoids nested shell/sql quote edge-cases during remote execution.
    return f"$${value.replace('$$', '')}$$"


def _register_token() -> str:
    device_id = f"rel09_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    resp = requests.post(
        f"{BASE_URL}/api/auth/register-device",
        json={"device_id": device_id},
        timeout=15,
    )
    resp.raise_for_status()
    payload = resp.json()
    token = (
        payload.get("access_token")
        or payload.get("token")
        or payload.get("jwt")
        or payload.get("accessToken")
    )
    if not token:
        raise RuntimeError(f"No token in auth response: {payload}")
    return token


def _post(path: str, body: dict, token: Optional[str] = None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.post(f"{BASE_URL}{path}", json=body, headers=headers, timeout=15)
    return r.status_code, (r.json() if r.text else {})


def main():
    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "base_url": BASE_URL,
        "checks": [],
        "pass": True,
    }

    token = _register_token()
    stamp = int(time.time())
    tracker_name = f"rel09-tracker-{stamp}"
    child_id = f"rel09-child-{stamp}"

    # 1) identity allow -> timestamp/action must change
    identity_id = _run_sql("SELECT id::text FROM identity.identity_attempts ORDER BY timestamp DESC LIMIT 1;")
    before = _run_sql(f"SELECT action, COALESCE(EXTRACT(EPOCH FROM timestamp)::bigint,-1) FROM identity.identity_attempts WHERE id={_sql_literal(identity_id)} LIMIT 1;")
    code, body = _post("/api/reports/identity-theft/allow", {"attemptId": identity_id})
    after = _run_sql(f"SELECT action, COALESCE(EXTRACT(EPOCH FROM timestamp)::bigint,-1) FROM identity.identity_attempts WHERE id={_sql_literal(identity_id)} LIMIT 1;")
    ok = code == 200 and "allowed" in after and before != after
    report["checks"].append({"name": "identity_allow", "pass": ok, "http_status": code, "response": body, "before": before, "after": after})

    # 1b) identity block -> timestamp/action must change again
    before = _run_sql(f"SELECT action, COALESCE(EXTRACT(EPOCH FROM timestamp)::bigint,-1) FROM identity.identity_attempts WHERE id={_sql_literal(identity_id)} LIMIT 1;")
    code, body = _post("/api/reports/identity-theft/block", {"attemptId": identity_id})
    after = _run_sql(f"SELECT action, COALESCE(EXTRACT(EPOCH FROM timestamp)::bigint,-1) FROM identity.identity_attempts WHERE id={_sql_literal(identity_id)} LIMIT 1;")
    ok = code == 200 and "blocked" in after and before != after
    report["checks"].append({"name": "identity_block", "pass": ok, "http_status": code, "response": body, "before": before, "after": after})

    # 2) location allow -> timestamp/action must change
    location_id = _run_sql("SELECT id::text FROM location.location_requests ORDER BY timestamp DESC LIMIT 1;")
    before = _run_sql(f"SELECT action, COALESCE(EXTRACT(EPOCH FROM timestamp)::bigint,-1) FROM location.location_requests WHERE id={_sql_literal(location_id)} LIMIT 1;")
    code, body = _post("/api/reports/privacy/location/allow", {"requestId": location_id})
    after = _run_sql(f"SELECT action, COALESCE(EXTRACT(EPOCH FROM timestamp)::bigint,-1) FROM location.location_requests WHERE id={_sql_literal(location_id)} LIMIT 1;")
    ok = code == 200 and "allowed" in after and before != after
    report["checks"].append({"name": "location_allow", "pass": ok, "http_status": code, "response": body, "before": before, "after": after})

    # 2b) location block -> timestamp/action must change again
    before = _run_sql(f"SELECT action, COALESCE(EXTRACT(EPOCH FROM timestamp)::bigint,-1) FROM location.location_requests WHERE id={_sql_literal(location_id)} LIMIT 1;")
    code, body = _post("/api/reports/privacy/location/block", {"requestId": location_id})
    after = _run_sql(f"SELECT action, COALESCE(EXTRACT(EPOCH FROM timestamp)::bigint,-1) FROM location.location_requests WHERE id={_sql_literal(location_id)} LIMIT 1;")
    ok = code == 200 and "blocked" in after and before != after
    report["checks"].append({"name": "location_block", "pass": ok, "http_status": code, "response": body, "before": before, "after": after})

    # 3) tracker whitelist -> row must exist/updated with blocked_count=0
    before = _run_sql(f"SELECT COUNT(*), COALESCE(MAX(blocked_count),-1), COALESCE(EXTRACT(EPOCH FROM MAX(last_blocked_at))::bigint,-1) FROM tracker.tracker_blocks WHERE tracker_name={_sql_literal(tracker_name)};")
    code, body = _post("/api/reports/privacy/tracker/whitelist", {"trackerName": tracker_name})
    after = _run_sql(f"SELECT COUNT(*), COALESCE(MAX(blocked_count),-1), COALESCE(EXTRACT(EPOCH FROM MAX(last_blocked_at))::bigint,-1) FROM tracker.tracker_blocks WHERE tracker_name={_sql_literal(tracker_name)};")
    ok = code == 200 and after.startswith("1|0|")
    report["checks"].append({"name": "tracker_whitelist", "pass": ok, "http_status": code, "response": body, "before": before, "after": after})

    # 3b) tracker whitelist idempotency -> still single row, timestamp can refresh
    before = _run_sql(f"SELECT COUNT(*), COALESCE(EXTRACT(EPOCH FROM MAX(last_blocked_at))::bigint,-1) FROM tracker.tracker_blocks WHERE tracker_name={_sql_literal(tracker_name)};")
    code, body = _post("/api/reports/privacy/tracker/whitelist", {"trackerName": tracker_name})
    after = _run_sql(f"SELECT COUNT(*), COALESCE(EXTRACT(EPOCH FROM MAX(last_blocked_at))::bigint,-1) FROM tracker.tracker_blocks WHERE tracker_name={_sql_literal(tracker_name)};")
    ok = code == 200 and after.startswith("1|")
    report["checks"].append({"name": "tracker_whitelist_idempotent", "pass": ok, "http_status": code, "response": body, "before": before, "after": after})

    # 4) cleanup start -> count/max(cleanup_date) should move
    before = _run_sql("SELECT COUNT(*), COALESCE(EXTRACT(EPOCH FROM MAX(cleanup_date))::bigint,-1) FROM cleanup.cleanup_records;")
    code, body = _post("/api/reports/privacy/cleanup/start", {"categories": ["cache", "logs"]})
    after = _run_sql("SELECT COUNT(*), COALESCE(EXTRACT(EPOCH FROM MAX(cleanup_date))::bigint,-1) FROM cleanup.cleanup_records;")
    b_count = int(before.split("|")[0] or "0")
    a_count = int(after.split("|")[0] or "0")
    ok = code == 200 and a_count >= b_count + 1
    report["checks"].append({"name": "cleanup_start", "pass": ok, "http_status": code, "response": body, "before": before, "after": after})

    # 5) darkweb scan start -> count/max(leak_date) should move
    before = _run_sql("SELECT COUNT(*), COALESCE(EXTRACT(EPOCH FROM MAX(leak_date))::bigint,-1) FROM darkweb.darkweb_leaks;")
    code, body = _post("/api/reports/dark-web/scan/start", {})
    after = _run_sql("SELECT COUNT(*), COALESCE(EXTRACT(EPOCH FROM MAX(leak_date))::bigint,-1) FROM darkweb.darkweb_leaks;")
    b_count = int(before.split("|")[0] or "0")
    a_count = int(after.split("|")[0] or "0")
    ok = code == 200 and a_count >= b_count + 1
    report["checks"].append({"name": "darkweb_scan_start", "pass": ok, "http_status": code, "response": body, "before": before, "after": after})

    # 5b) darkweb scan fast -> count/max(leak_date) should move again
    before = _run_sql("SELECT COUNT(*), COALESCE(EXTRACT(EPOCH FROM MAX(leak_date))::bigint,-1) FROM darkweb.darkweb_leaks;")
    code, body = _post("/api/reports/dark-web/scan/fast", {})
    after = _run_sql("SELECT COUNT(*), COALESCE(EXTRACT(EPOCH FROM MAX(leak_date))::bigint,-1) FROM darkweb.darkweb_leaks;")
    b_count = int(before.split("|")[0] or "0")
    a_count = int(after.split("|")[0] or "0")
    ok = code == 200 and a_count >= b_count + 1
    report["checks"].append({"name": "darkweb_scan_fast", "pass": ok, "http_status": code, "response": body, "before": before, "after": after})

    # 5c) darkweb scan secure -> count/max(leak_date) should move again
    before = _run_sql("SELECT COUNT(*), COALESCE(EXTRACT(EPOCH FROM MAX(leak_date))::bigint,-1) FROM darkweb.darkweb_leaks;")
    code, body = _post("/api/reports/dark-web/scan/secure", {})
    after = _run_sql("SELECT COUNT(*), COALESCE(EXTRACT(EPOCH FROM MAX(leak_date))::bigint,-1) FROM darkweb.darkweb_leaks;")
    b_count = int(before.split("|")[0] or "0")
    a_count = int(after.split("|")[0] or "0")
    ok = code == 200 and a_count >= b_count + 1
    report["checks"].append({"name": "darkweb_scan_secure", "pass": ok, "http_status": code, "response": body, "before": before, "after": after})

    # 6) parental bypass apply -> shadow table row should reflect payload (idempotent upsert)
    before = _run_sql(f"SELECT COALESCE(incognito,-1), COALESCE(tor,-1), COALESCE(proxy,-1) FROM parental_bypass_state_shadow WHERE target_id={_sql_literal(child_id)} LIMIT 1;")
    payload = {"childId": child_id, "incognito": True, "tor": False, "proxy": True}
    code, body = _post("/api/parental/bypass/apply", payload, token=token)
    after = _run_sql(f"SELECT COALESCE(incognito,-1), COALESCE(tor,-1), COALESCE(proxy,-1) FROM parental_bypass_state_shadow WHERE target_id={_sql_literal(child_id)} LIMIT 1;")
    ok = code == 200 and after == "1|0|1"
    report["checks"].append({"name": "parental_bypass_apply", "pass": ok, "http_status": code, "response": body, "before": before, "after": after})

    # 6b) parental bypass idempotency -> one row for target_id remains after repeated apply
    before = _run_sql(f"SELECT COUNT(*) FROM parental_bypass_state_shadow WHERE target_id={_sql_literal(child_id)};")
    code, body = _post("/api/parental/bypass/apply", payload, token=token)
    after = _run_sql(f"SELECT COUNT(*) FROM parental_bypass_state_shadow WHERE target_id={_sql_literal(child_id)};")
    ok = code == 200 and before == "1" and after == "1"
    report["checks"].append({"name": "parental_bypass_apply_idempotent", "pass": ok, "http_status": code, "response": body, "before": before, "after": after})

    # 2c) location update-accuracy -> modified action timestamp should move (write-path for freshness)
    before = _run_sql("SELECT COUNT(*), COALESCE(EXTRACT(EPOCH FROM MAX(timestamp))::bigint,-1) FROM location.location_requests WHERE action='modified';")
    code, body = _post("/api/reports/privacy/location/update-accuracy", {"accuracy": "high"})
    after = _run_sql("SELECT COUNT(*), COALESCE(EXTRACT(EPOCH FROM MAX(timestamp))::bigint,-1) FROM location.location_requests WHERE action='modified';")
    b_count = int(before.split("|")[0] or "0")
    a_count = int(after.split("|")[0] or "0")
    ok = code == 200 and a_count >= b_count + 1
    report["checks"].append({"name": "location_update_accuracy", "pass": ok, "http_status": code, "response": body, "before": before, "after": after})

    report["pass"] = all(x["pass"] for x in report["checks"])
    report["passed"] = sum(1 for x in report["checks"] if x["pass"])
    report["failed"] = sum(1 for x in report["checks"] if not x["pass"])
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"write-before-after: {'PASS' if report['pass'] else 'FAIL'}")
    print(f"passed={report['passed']} failed={report['failed']}")
    print(f"report={OUT_PATH}")
    if not report["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
