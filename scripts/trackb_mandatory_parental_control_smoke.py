#!/usr/bin/env python3
"""
Track B gate: mandatory in-app parental confirmation on sensitive surfaces.

Static checks only (no simulator): verifies ParentSessionGate wiring in Swift sources.
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
    print("TRACK B MANDATORY PARENTAL CONTROL (static wiring smoke)")
    gate = ROOT / "Core/Profile/ParentSessionGate.swift"
    require(gate.exists(), f"Missing {gate}")
    require(
        file_contains(gate, "confirmSensitiveAction", "hasConfiguredParentalPIN", "verifyParentalPIN"),
        "ParentSessionGate must expose confirmSensitiveAction and PIN APIs",
    )

    checks: list[tuple[str, pathlib.Path, tuple[str, ...]]] = [
        (
            "Rewards modal (parent actions)",
            ROOT / "Screens/RewardsModalView.swift",
            ("ParentSessionGate", "confirmSensitiveAction", "runWithParentConfirmation"),
        ),
        (
            "Rewards quick modal",
            ROOT / "Screens/RewardsQuickModal.swift",
            ("ParentSessionGate", "confirmSensitiveAction"),
        ),
        (
            "Child rewards screen",
            ROOT / "Screens/ChildRewardsScreen.swift",
            ("ParentSessionGate", "confirmSensitiveAction"),
        ),
        (
            "Parental control screen",
            ROOT / "Screens/07_ParentalControlScreen.swift",
            ("ParentSessionGate", "requireSensitiveParentSession"),
        ),
        (
            "Games parental screen",
            ROOT / "Screens/GamesParentalControlScreen.swift",
            ("ParentSessionGate", "confirmSensitiveAction"),
        ),
        (
            "Family roster sensitive branch",
            ROOT / "Screens/02_FamilyScreen.swift",
            ("ParentSessionGate", "confirmSensitiveAction"),
        ),
        (
            "Parent dashboard",
            ROOT / "Screens/ParentDashboardView.swift",
            ("ParentSessionGate", "confirmSensitiveAction"),
        ),
    ]
    for label, path, needles in checks:
        require(path.exists(), f"Missing {path.relative_to(ROOT)}")
        require(file_contains(path, *needles), f"{label}: expected substrings in {path.name}: {needles}")

    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
