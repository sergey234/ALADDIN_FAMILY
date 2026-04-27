#!/usr/bin/env python3
"""
Track B governance smoke: phase exit criteria coverage
(unit + integration + UI smoke + accessibility smoke).
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def require(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def exists(path: str) -> bool:
    return (ROOT / path).exists()


def find_any(base: str, pattern: str) -> bool:
    root = ROOT / base
    if not root.exists():
        return False
    return any(root.rglob(pattern))


def check_phase(name: str, checks: list[tuple[str, bool]]) -> None:
    missing = [label for label, ok in checks if not ok]
    require(not missing, f"{name}: missing exit-criteria evidence: {', '.join(missing)}")
    print(f"OK {name}")


def main() -> int:
    print("TRACK B PHASE EXIT CRITERIA SMOKE")

    # Phase 7
    check_phase(
        "phase7",
        [
            ("unit", find_any("Tests/UnitTests", "*PolicyTests.swift")),
            ("integration", exists("scripts/phase8_offline_sync_smoke.py")),
            ("ui_smoke", exists("scripts/phase8_ux_smoke.py")),
            ("accessibility_smoke", exists("scripts/phase9_elderly_accessibility_localization_smoke.py")),
        ],
    )

    # Phase 8
    check_phase(
        "phase8",
        [
            ("unit", find_any("Tests/UnitTests", "*.swift")),
            ("integration", exists("scripts/phase8_offline_sync_smoke.py")),
            ("ui_smoke", exists("scripts/phase8_ux_smoke.py")),
            ("accessibility_smoke", exists("scripts/phase9_elderly_accessibility_localization_smoke.py")),
        ],
    )

    # Phase 9
    check_phase(
        "phase9",
        [
            ("unit", find_any("Tests/UnitTests", "*ReconcilePolicyTests.swift")),
            ("integration", exists("scripts/phase9_family_flow_integration_smoke.py")),
            ("ui_smoke", exists("scripts/phase9_elderly_ux_ru_en_smoke.py")),
            ("accessibility_smoke", exists("scripts/phase9_elderly_accessibility_localization_smoke.py")),
        ],
    )

    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
