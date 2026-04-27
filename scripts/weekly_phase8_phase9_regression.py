#!/usr/bin/env python3
"""
Weekly regression pack for Phase 8 / Phase 9 smoke suite.

Creates report with current statuses and pass/fail deltas vs previous report.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_MD = ROOT / "docs/WEEKLY_PHASE8_PHASE9_REGRESSION_REPORT.md"
REPORT_JSON = ROOT / "docs/WEEKLY_PHASE8_PHASE9_REGRESSION_REPORT.json"
TIMEOUT_SEC = 900

PHASE8_9_SUITES = [
    "scripts/phase8_content_device_smoke.py",
    "scripts/phase8_ux_smoke.py",
    "scripts/phase8_security_smoke.py",
    "scripts/phase8_compliance_smoke.py",
    "scripts/phase8_offline_sync_smoke.py",
    "scripts/phase8_performance_smoke.py",
    "scripts/phase9_access_rules_smoke.py",
    "scripts/phase9_content_lifecycle_unified_smoke.py",
    "scripts/phase9_content_safety_alignment_smoke.py",
    "scripts/phase9_data_integrity_smoke.py",
    "scripts/phase9_elderly_accessibility_localization_smoke.py",
    "scripts/phase9_elderly_critical_smoke.py",
    "scripts/phase9_elderly_data_audit_smoke.py",
    "scripts/phase9_elderly_localization_gate_smoke.py",
    "scripts/phase9_elderly_readability_contrast_smoke.py",
    "scripts/phase9_elderly_ux_ru_en_smoke.py",
    "scripts/phase9_family_flow_integration_smoke.py",
    "scripts/phase9_parent_mirror_overview_smoke.py",
    "scripts/phase9_shared_permission_layer_smoke.py",
    "scripts/phase9_unified_family_model_smoke.py",
]


def run_script(script: str) -> dict[str, str]:
    cmd = [sys.executable, script]
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=TIMEOUT_SEC)
    except subprocess.TimeoutExpired:
        return {"script": script, "status": "TIMEOUT", "tail": f"timeout>{TIMEOUT_SEC}s"}

    output = (proc.stdout + "\n" + proc.stderr).strip()
    if proc.returncode == 0 and "SMOKE RESULT: PASS" in output:
        return {"script": script, "status": "PASS", "tail": ""}
    tail = " ".join(output.splitlines()[-3:]).strip()
    return {"script": script, "status": "FAIL", "tail": tail}


def load_previous_status_map() -> dict[str, str]:
    if not REPORT_JSON.exists():
        return {}
    try:
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    status_map: dict[str, str] = {}
    for row in payload.get("results", []):
        script = row.get("script")
        status = row.get("status")
        if isinstance(script, str) and isinstance(status, str):
            status_map[script] = status
    return status_map


def build_delta(previous: dict[str, str], current: list[dict[str, str]]) -> dict[str, list[str]]:
    improved: list[str] = []
    regressed: list[str] = []
    unchanged: list[str] = []
    for row in current:
        script = row["script"]
        now = row["status"]
        before = previous.get(script)
        if before is None or before == now:
            unchanged.append(script)
        elif before != "PASS" and now == "PASS":
            improved.append(script)
        elif before == "PASS" and now != "PASS":
            regressed.append(script)
        else:
            unchanged.append(script)
    return {"improved": improved, "regressed": regressed, "unchanged": unchanged}


def write_reports(results: list[dict[str, str]], delta: dict[str, list[str]]) -> None:
    generated = datetime.now(tz=timezone.utc).isoformat()
    payload = {
        "generated_at_utc": generated,
        "total": len(results),
        "pass": sum(1 for row in results if row["status"] == "PASS"),
        "fail_or_timeout": sum(1 for row in results if row["status"] != "PASS"),
        "delta": delta,
        "results": results,
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Weekly Regression Report (Phase 8 / Phase 9)",
        "",
        f"Generated (UTC): {generated}",
        "",
        f"Total: {payload['total']}",
        f"Pass: {payload['pass']}",
        f"Fail/Timeout: {payload['fail_or_timeout']}",
        "",
        "## Pass/Fail Deltas",
        f"- Improved: {len(delta['improved'])}",
        f"- Regressed: {len(delta['regressed'])}",
        f"- Unchanged: {len(delta['unchanged'])}",
        "",
        "## Results",
    ]
    for row in results:
        name = Path(row["script"]).name
        lines.append(f"- {row['status']} `{name}`")
        if row["tail"]:
            lines.append(f"  - tail: {row['tail']}")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    previous = load_previous_status_map()
    results = [run_script(script) for script in PHASE8_9_SUITES]
    delta = build_delta(previous, results)
    write_reports(results, delta)

    failed = [row for row in results if row["status"] != "PASS"]
    print("WEEKLY PHASE8/9 REGRESSION PACK")
    print(f"pass/fail deltas: improved={len(delta['improved'])}, regressed={len(delta['regressed'])}, unchanged={len(delta['unchanged'])}")
    if failed:
        print(f"PACK RESULT: FAIL ({len(failed)} checks failed)")
        return 1
    print("PACK RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
