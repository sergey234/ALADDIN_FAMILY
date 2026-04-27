#!/usr/bin/env python3
"""
Track B smoke: monthly log audit runbook exists and defines recurring process.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNBOOK = ROOT / "docs/TRACKB_MONTHLY_LOG_AUDIT_RUNBOOK.md"


def require(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def main() -> int:
    print("TRACK B MONTHLY LOG AUDIT SMOKE")
    require(RUNBOOK.exists(), "Missing monthly log audit runbook")
    text = RUNBOOK.read_text(encoding="utf-8")

    for required in [
        "monthly audit",
        "aladdin_latest_export_manifest.json",
        "visual-logs-*.txt",
        "startup_trace.txt",
        "app_lifecycle_trace.txt",
        "frequency: monthly",
        "SLA",
    ]:
        require(required in text, f"Missing runbook requirement: {required}")

    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
