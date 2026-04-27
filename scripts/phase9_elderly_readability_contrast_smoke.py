#!/usr/bin/env python3
"""
Phase 9.1 smoke: large read mode + contrast presets for elderly interface.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCREEN = ROOT / "Screens/09_ElderlyInterfaceScreen.swift"
L10N = ROOT / "Core/Localization/LocalizationManager.swift"
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
    screen = read(SCREEN)
    l10n = read(L10N)
    must_contain(screen, '@AppStorage("elderly_large_read_mode")', "Large read mode storage")
    must_contain(screen, '@AppStorage("elderly_contrast_preset")', "Contrast preset storage")
    must_contain(screen, ".dynamicTypeSize(elderlyDynamicType)", "Large read mode application")
    must_contain(screen, ".contrast(elderlyContrastValue)", "Contrast preset application")
    must_contain(screen, "elderly_settings_large_read_mode", "Settings toggle key usage")
    must_contain(screen, "elderly_settings_contrast_title", "Settings contrast picker key usage")
    must_contain(l10n, '"elderly_settings_large_read_mode"', "Localization key large read mode")
    must_contain(l10n, '"elderly_settings_contrast_high"', "Localization key high contrast")
    print("OK readability+contrast contracts")


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
        "phase9.1 readability build",
    )
    must_match(out, r"\*\* BUILD SUCCEEDED \*\*", "Build result")
    print("OK build")


def main() -> int:
    print("PHASE 9.1 READABILITY + CONTRAST SMOKE")
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
