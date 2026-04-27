#!/usr/bin/env python3
"""
Track B smoke: Wave 2 feature mode policy is in place.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
POLICY = ROOT / "docs/TRACKB_WAVE2_FEATURE_MODE_POLICY.md"
PR_TEMPLATE = ROOT / ".github/pull_request_template.md"
CI = ROOT / ".github/workflows/ci.yml"


def require(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def main() -> int:
    print("TRACK B WAVE2 FEATURE MODE SMOKE")
    require(POLICY.exists(), "Missing Wave 2 feature mode policy")
    require(PR_TEMPLATE.exists(), "Missing PR template")
    require(CI.exists(), "Missing CI workflow")

    policy = POLICY.read_text(encoding="utf-8")
    pr_template = PR_TEMPLATE.read_text(encoding="utf-8")
    ci = CI.read_text(encoding="utf-8")

    require("python3 scripts/localization_lint.py" in policy, "Policy must reference global localization lint")
    require("No bypass merges" in policy, "Policy must enforce no bypass merges")
    require("localization-lint:" in ci, "CI must include localization-lint job")
    require("python3 scripts/localization_lint.py --scope elderly60plus" in ci, "CI localization gate command missing")
    require("Localization (RU/EN) - Required" in pr_template, "PR template localization section missing")
    require("no hardcoded literals" in pr_template, "PR template must enforce no hardcoded localization")

    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
