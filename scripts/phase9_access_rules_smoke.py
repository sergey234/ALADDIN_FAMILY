#!/usr/bin/env python3
"""
Phase 9.3 smoke: synchronized access rules (contacts/limits/critical settings).
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
POLICY = ROOT / "Core/Profile/FamilyAccessPolicy.swift"
CHILD = ROOT / "Screens/08_ChildInterfaceScreen.swift"
ELDERLY = ROOT / "Screens/09_ElderlyInterfaceScreen.swift"
PARENTAL = ROOT / "Screens/07_ParentalControlScreen.swift"
PROJECT = "ALADDIN.xcodeproj"
SCHEME = "ALADDIN"
DEVICE_ID = "B98F9663-BB22-481C-B4C4-6D7E88F1E017"


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


def check_policy_contract() -> None:
    body = read(POLICY)
    must_contain(body, "case editFamilyContacts", "Policy contacts permission")
    must_contain(body, "case manageFamilyLimits", "Policy limits permission")
    must_contain(body, "case manageCriticalFamilySettings", "Policy critical settings permission")
    must_match(body, r"case \.editFamilyContacts:\n\s+return role == \.parent \|\| role == \.elderly", "Contacts policy role mapping")
    print("OK policy access contracts")


def check_screen_integrations() -> None:
    child = read(CHILD)
    elderly = read(ELDERLY)
    parental = read(PARENTAL)
    must_contain(child, ".editFamilyContacts", "Child contacts permission integration")
    must_contain(elderly, ".editFamilyContacts", "Elderly contacts permission integration")
    must_contain(parental, "canManageFamilyLimits", "Parental limits permission integration")
    must_contain(parental, ".manageCriticalFamilySettings", "Parental critical settings permission integration")
    print("OK screen integrations")


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
        "phase9 access rules build",
    )
    must_match(out, r"\*\* BUILD SUCCEEDED \*\*", "Build result")
    print("OK build")


def main() -> int:
    print("PHASE 9.3 ACCESS RULES SMOKE")
    check_policy_contract()
    check_screen_integrations()
    check_build()
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
