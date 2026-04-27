#!/usr/bin/env python3
"""
Phase 9.3 smoke: unified child/elderly family roster model.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
POLICY_FILE = ROOT / "Core/Profile/FamilyAccessPolicy.swift"
ELDERLY_SCREEN = ROOT / "Screens/09_ElderlyInterfaceScreen.swift"
CHILD_SCREEN = ROOT / "Screens/08_ChildInterfaceScreen.swift"
PROJECT = "ALADDIN.xcodeproj"
SCHEME = "ALADDIN"
DEVICE_ID = "B98F9663-BB22-481C-B4C4-6D7E88F1E017"  # iPhone 16


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def require(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def must_contain(text: str, needle: str, context: str) -> None:
    require(needle in text, f"{context}: missing `{needle}`")


def must_match(text: str, pattern: str, context: str) -> None:
    require(re.search(pattern, text, flags=re.MULTILINE) is not None, f"{context}: missing pattern `{pattern}`")


def run(cmd: list[str], context: str) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"{context} failed\nCMD: {' '.join(cmd)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return proc.stdout + proc.stderr


def check_unified_model() -> None:
    body = read(POLICY_FILE)
    must_contain(body, "enum UnifiedFamilyRoster", "Unified family roster type")
    must_contain(body, "static func load(", "Unified family roster load")
    must_contain(body, "static func contactProjections(", "Unified contact projection")
    must_contain(body, "fallbackPhone(", "Unified fallback phone")
    print("OK unified family roster contracts")


def check_integrations() -> None:
    elderly = read(ELDERLY_SCREEN)
    child = read(CHILD_SCREEN)
    must_contain(elderly, "UnifiedFamilyRoster.load()", "Elderly roster load integration")
    must_contain(elderly, "UnifiedFamilyRoster.contactProjections(audience: .elderly", "Elderly contacts projection integration")
    must_contain(child, "UnifiedFamilyRoster.load()", "Child roster load integration")
    must_contain(child, "UnifiedFamilyRoster.contactProjections(audience: .child", "Child contacts projection integration")
    require('phone: "+7 (999) 000-00-00"' not in child, "Child legacy placeholder phone must be removed")
    print("OK child+elderly integrations")


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
        "phase9.3 build",
    )
    must_match(out, r"\*\* BUILD SUCCEEDED \*\*", "phase9.3 build result")
    print("OK build for phase 9.3 changes")


def main() -> int:
    print("PHASE 9.3 UNIFIED FAMILY MODEL SMOKE")
    check_unified_model()
    check_integrations()
    check_build()
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
