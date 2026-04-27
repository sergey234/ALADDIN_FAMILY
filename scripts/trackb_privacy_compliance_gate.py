#!/usr/bin/env python3
"""
Track B gate: privacy/compliance checks before release merge.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

REQUIRED_ARTIFACTS = [
    "docs/PHASE8_COMPLIANCE_VALIDATION.md",
    "scripts/phase8_compliance_smoke.py",
    "docs/TRACKB_TESTFLIGHT_BETA_RING_RUNBOOK.md",
]


def require(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def main() -> int:
    print("TRACK B PRIVACY/COMPLIANCE GATE")
    for rel_path in REQUIRED_ARTIFACTS:
        path = ROOT / rel_path
        require(path.exists(), f"Missing required compliance artifact: {rel_path}")
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
