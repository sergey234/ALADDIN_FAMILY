#!/usr/bin/env python3
"""
Phase 9.4 smoke: child content + family safety settings linked to elderly controls.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEED = ROOT / "Core/Content/Seed/ContentSeedProvider.swift"
ELDERLY = ROOT / "Screens/09_ElderlyInterfaceScreen.swift"
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
    seed = read(SEED)
    elderly = read(ELDERLY)
    child = read(ROOT / "Screens/08_ChildInterfaceScreen.swift")
    l10n = read(ROOT / "Core/Localization/LocalizationManager.swift")
    must_contain(seed, "enum FamilyContentSafetyBridge", "Family content/safety bridge")
    must_contain(seed, "childSafetyMirrorCategories", "Child safety mirror categories")
    must_contain(seed, "safetyTitleKey", "Unified safety title key")
    must_contain(seed, "resolvedElderlyCategories", "Resolved elderly categories API")
    must_contain(seed, "family_content_block_enabled", "Content filter toggle linkage")
    must_contain(seed, "family_bypass_protection_enabled", "Bypass protection toggle linkage")
    must_contain(elderly, "FamilyContentSafetyBridge.resolvedElderlyCategories()", "Elderly feed linked to family safety bridge")
    must_contain(elderly, "localized(FamilyContentSafetyBridge.safetyTitleKey)", "Elderly screen uses unified safety title")
    must_contain(child, "localized(FamilyContentSafetyBridge.safetyTitleKey)", "Child screen uses unified safety title")
    must_contain(l10n, '"family_category_safety"', "Localization key for unified safety category")
    print("OK phase 9.4 contracts")


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
        "phase9.4 content safety build",
    )
    must_match(out, r"\*\* BUILD SUCCEEDED \*\*", "Build result")
    print("OK build")


def main() -> int:
    print("PHASE 9.4 CONTENT SAFETY ALIGNMENT SMOKE")
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
