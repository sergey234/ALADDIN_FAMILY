#!/usr/bin/env python3
"""
Phase 9.1 smoke: elderly data audit + placeholder contacts removal.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
POLICY = ROOT / "Core/Profile/FamilyAccessPolicy.swift"
ELDERLY = ROOT / "Screens/09_ElderlyInterfaceScreen.swift"
CHILD = ROOT / "Screens/08_ChildInterfaceScreen.swift"
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


def check_contracts() -> None:
    policy = read(POLICY)
    elderly = read(ELDERLY)
    child = read(CHILD)
    must_contain(policy, "phoneDirectoryKey", "Unified roster phone directory")
    must_contain(policy, "persistPhoneDirectory(", "Unified roster phone persistence")
    must_contain(policy, "stableContactId(", "Stable contact ID mapping")
    must_contain(elderly, "runDataIntegrityAudit()", "Elderly audit on screen appear")
    must_contain(elderly, "persistPhoneDirectory(", "Elderly contacts persist in unified directory")
    must_contain(child, "persistPhoneDirectory(", "Child contacts persist in unified directory")
    require('phone: "+7 (999) 000-00-00"' not in elderly, "Hardcoded elderly placeholder phone still present")
    print("OK phase 9.1 data-audit contracts")


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
        "phase9.1 data audit build",
    )
    must_match(out, r"\*\* BUILD SUCCEEDED \*\*", "Build result")
    print("OK build")


def main() -> int:
    print("PHASE 9.1 ELDERLY DATA AUDIT SMOKE")
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
