#!/usr/bin/env python3
"""
Track B smoke: localization lint is configured as blocking CI gate.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CI = ROOT / ".github/workflows/ci.yml"


def require(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def main() -> int:
    print("TRACK B LOCALIZATION GATE SMOKE")
    require(CI.exists(), "CI workflow not found")
    content = CI.read_text(encoding="utf-8")

    require("localization-lint:" in content, "Missing localization-lint job")
    require(
        "python3 scripts/localization_lint.py --scope elderly60plus" in content,
        "Missing localization-lint command for enforced scope",
    )
    require(
        "needs: [localization-lint, privacy-compliance-gate]" in content,
        "Build job must depend on localization-lint gate",
    )
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
