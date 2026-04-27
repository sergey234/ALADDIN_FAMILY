#!/usr/bin/env python3
"""
Independent acceptance gate.

Rules:
- Every required smoke must report PASS.
- Any FAIL or TIMEOUT fails the gate.
- Produces machine-readable and human-readable summary artifacts.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_MD = ROOT / "docs/INDEPENDENT_SMOKE_SUITE_REPORT.md"
REPORT_JSON = ROOT / "docs/INDEPENDENT_SMOKE_SUITE_REPORT.json"

SMOKE_TIMEOUT_SEC = 900

REQUIRED_SMOKES = [
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
    "scripts/trackb_wave2_feature_mode_smoke.py",
    "scripts/trackb_product_kpi_gates_smoke.py",
    "scripts/trackb_aes256_encryption_gate_smoke.py",
    "scripts/trackb_monthly_log_audit_smoke.py",
]


@dataclass
class SmokeResult:
    script: str
    status: str
    detail: str
    elapsed_sec: float


def run_smoke(script: str) -> SmokeResult:
    start = datetime.now(tz=timezone.utc)
    cmd = [sys.executable, script]
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=SMOKE_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        elapsed = (datetime.now(tz=timezone.utc) - start).total_seconds()
        return SmokeResult(script=script, status="TIMEOUT", detail=f"timeout>{SMOKE_TIMEOUT_SEC}s", elapsed_sec=elapsed)

    elapsed = (datetime.now(tz=timezone.utc) - start).total_seconds()
    output = (proc.stdout + "\n" + proc.stderr).strip()
    if proc.returncode == 0 and "SMOKE RESULT: PASS" in output:
        return SmokeResult(script=script, status="PASS", detail="", elapsed_sec=elapsed)

    tail = " ".join(output.splitlines()[-3:]).strip()
    if not tail:
        tail = f"returncode={proc.returncode}"
    return SmokeResult(script=script, status="FAIL", detail=tail, elapsed_sec=elapsed)


def write_reports(results: list[SmokeResult]) -> None:
    total = len(results)
    passed = sum(1 for item in results if item.status == "PASS")
    failed = total - passed
    now = datetime.now(tz=timezone.utc).isoformat()

    payload = {
        "generated_at_utc": now,
        "total": total,
        "pass": passed,
        "fail_or_timeout": failed,
        "results": [
            {
                "script": item.script,
                "status": item.status,
                "detail": item.detail,
                "elapsed_sec": round(item.elapsed_sec, 2),
            }
            for item in results
        ],
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Independent Smoke Suite Report",
        "",
        f"Generated (UTC): {now}",
        "",
        f"Total: {total}",
        f"Pass: {passed}",
        f"Fail/Timeout: {failed}",
        "",
        "## Results",
    ]
    for item in results:
        script_name = Path(item.script).name
        lines.append(f"- {item.status} `{script_name}` ({item.elapsed_sec:.1f}s)")
        if item.detail:
            lines.append(f"  - tail: {item.detail}")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    print("INDEPENDENT ACCEPTANCE GATE")
    results = [run_smoke(script) for script in REQUIRED_SMOKES]
    write_reports(results)

    failed_items = [item for item in results if item.status != "PASS"]
    for item in results:
        print(f"{item.status:7} {item.script}")

    if failed_items:
        print(f"GATE RESULT: FAIL ({len(failed_items)} checks failed)")
        return 1

    print("GATE RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
