#!/usr/bin/env python3
"""
Track B smoke: product KPI gate policy has all required thresholds.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC = ROOT / "docs/TRACKB_PRODUCT_KPI_GATES.md"


def require(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def main() -> int:
    print("TRACK B PRODUCT KPI GATES SMOKE")
    require(DOC.exists(), "Missing KPI gates document")
    text = DOC.read_text(encoding="utf-8")

    required_fragments = [
        "Startup time: `< 3 seconds`",
        "Battery consumption: `< 15% per hour`",
        "Background memory: `< 200MB`",
        "Engagement: `> 20 minutes/session`",
        "Retention: target values per age segment",
        "Lesson completion: `> 80%`",
        "Parent approval: `> 4.5 stars`",
        "measurement method",
        "source artifact/report path",
        "review cadence",
    ]
    for fragment in required_fragments:
        require(fragment in text, f"Missing KPI contract fragment: {fragment}")

    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
