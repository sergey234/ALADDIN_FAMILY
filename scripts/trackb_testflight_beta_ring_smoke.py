#!/usr/bin/env python3
"""
Track B smoke: TestFlight beta ring + rollback runbook completeness.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNBOOK = ROOT / "docs/TRACKB_TESTFLIGHT_BETA_RING_RUNBOOK.md"


def require(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def main() -> int:
    print("TRACK B TESTFLIGHT BETA RING SMOKE")
    require(RUNBOOK.exists(), "Runbook file is missing")
    text = RUNBOOK.read_text(encoding="utf-8")
    required_sections = [
        "Internal ring",
        "Limited external ring",
        "Rollback checklist",
        "Exit criteria",
    ]
    for section in required_sections:
        require(section in text, f"Missing required runbook section: {section}")
    required_actions = [
        "disable rollout",
        "previous stable build cohort",
        "incident card",
    ]
    lowered = text.lower()
    for action in required_actions:
        require(action in lowered, f"Missing rollback action: {action}")
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
