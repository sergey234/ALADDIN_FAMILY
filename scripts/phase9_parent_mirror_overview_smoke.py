#!/usr/bin/env python3
"""
Phase 9.4 smoke: parent mirrored overview for child/elderly visibility.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PARENT_DASHBOARD = ROOT / "Screens/ParentDashboardView.swift"
L10N = ROOT / "Core/Localization/LocalizationManager.swift"
PROJECT = "ALADDIN.xcodeproj"
SCHEME = "ALADDIN"
DEVICE_ID = "B98F9663-BB22-481C-B4C4-6D7E88F1E017"


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def require(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def run(cmd: list[str], context: str) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"{context} failed\nCMD: {' '.join(cmd)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return proc.stdout + proc.stderr


def check_contracts() -> None:
    parent = read(PARENT_DASHBOARD)
    l10n = read(L10N)
    for needle in [
        "mirrorOverviewSection",
        "buildMirrorOverview(",
        "FamilyContentSafetyBridge.resolvedElderlyCategories",
        "FamilyPermissionLayer.snapshot",
        "parent_dashboard_mirror_title",
    ]:
        require(needle in parent, f"Missing mirror overview contract: {needle}")
    for key in [
        "parent_dashboard_mirror_title",
        "parent_dashboard_mirror_subtitle",
        "parent_dashboard_mirror_child_title",
        "parent_dashboard_mirror_elderly_title",
        "parent_dashboard_mirror_permissions_title",
        "parent_dashboard_perm_contacts",
        "parent_dashboard_perm_limits",
        "parent_dashboard_perm_critical",
        "parent_dashboard_perm_allowed",
        "parent_dashboard_perm_blocked",
    ]:
        require(f'"{key}"' in l10n, f"Missing localization key: {key}")
    print("OK mirror overview contracts")


def check_build() -> None:
    out = run(
        [
            "xcodebuild",
            "-project",
            PROJECT,
            "-scheme",
            SCHEME,
            "-sdk",
            "iphonesimulator",
            "-destination",
            f"id={DEVICE_ID}",
            "build",
        ],
        "phase9.4 parent mirror build",
    )
    require("** BUILD SUCCEEDED **" in out, "Build must succeed")
    print("OK build")


def main() -> int:
    print("PHASE 9.4 PARENT MIRROR OVERVIEW SMOKE")
    check_contracts()
    check_build()
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
