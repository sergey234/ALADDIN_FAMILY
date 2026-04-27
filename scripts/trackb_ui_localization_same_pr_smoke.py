#!/usr/bin/env python3
"""
Track B smoke: UI tasks include RU/EN localization in same PR flow.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
POLICY = ROOT / "docs/TRACKB_UI_LOCALIZATION_SAME_PR_POLICY.md"
PR_CHECKLIST = ROOT / "docs/LOCALIZATION_PR_CHECKLIST.md"
RU = ROOT / "Resources/Localization/ru.lproj/Localizable.strings"
EN = ROOT / "Resources/Localization/en.lproj/Localizable.strings"


def require(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def main() -> int:
    print("TRACK B UI LOCALIZATION SAME-PR SMOKE")
    for path in [POLICY, PR_CHECKLIST, RU, EN]:
        require(path.exists(), f"Missing required artifact: {path.relative_to(ROOT)}")

    policy = POLICY.read_text(encoding="utf-8")
    require("RU localization" in policy, "Policy must mention RU localization requirement")
    require("EN localization" in policy, "Policy must mention EN localization requirement")
    require("same PR" in policy, "Policy must enforce same PR delivery")

    checklist = PR_CHECKLIST.read_text(encoding="utf-8").lower()
    require("ru" in checklist and "en" in checklist, "PR checklist must include RU/EN checks")
    require("lint" in checklist, "PR checklist must include localization lint check")

    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
