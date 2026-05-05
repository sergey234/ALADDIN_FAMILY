#!/usr/bin/env python3
"""
Track B gate: simplified no-PIN parental flows on sensitive surfaces.

Static checks only (no simulator): verifies runtime no longer depends on ParentSessionGate.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def require(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def file_contains(path: pathlib.Path, *needles: str) -> bool:
    text = path.read_text(encoding="utf-8")
    return all(n in text for n in needles)


def main() -> int:
    print("TRACK B SIMPLIFIED PARENTAL CONTROL (static wiring smoke)")

    checks: list[tuple[str, pathlib.Path, tuple[str, ...]]] = [
        (
            "Rewards modal (parent actions)",
            ROOT / "Screens/RewardsModalView.swift",
            ("runWithParentConfirmation",),
        ),
        (
            "Rewards quick modal",
            ROOT / "Screens/RewardsQuickModal.swift",
            ("rewardChild()", "punishChild()"),
        ),
        (
            "Child rewards screen",
            ROOT / "Screens/ChildRewardsScreen.swift",
            ("showRewardInput = true", "showPunishInput = true"),
        ),
        (
            "Parental control screen",
            ROOT / "Screens/07_ParentalControlScreen.swift",
            ("requireSensitiveParentSession",),
        ),
        (
            "Games parental screen",
            ROOT / "Screens/GamesParentalControlScreen.swift",
            ("requestParentSessionForSettingChange",),
        ),
        (
            "Family roster sensitive branch",
            ROOT / "Screens/02_FamilyScreen.swift",
            ("removeFamilyMember(target)",),
        ),
        (
            "Parent dashboard",
            ROOT / "Screens/ParentDashboardView.swift",
            ("runSensitiveAction",),
        ),
    ]
    for label, path, needles in checks:
        require(path.exists(), f"Missing {path.relative_to(ROOT)}")
        require(file_contains(path, *needles), f"{label}: expected substrings in {path.name}: {needles}")
        body = path.read_text(encoding="utf-8")
        require(
            "ParentSessionGate.confirmSensitiveAction(" not in body,
            f"{label}: ParentSessionGate runtime challenge must be removed",
        )

    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
