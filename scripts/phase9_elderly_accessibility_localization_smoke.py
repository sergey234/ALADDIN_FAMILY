#!/usr/bin/env python3
"""
Phase 9.5 smoke: elderly accessibility labels/hints localization coverage.
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
    must_contain(screen, "elderly_a11y_sos_hint", "SOS accessibility hint usage")
    must_contain(screen, "elderly_a11y_calls_family_hint", "Family call accessibility hint usage")
    must_contain(screen, "elderly_a11y_marks_medication_hint", "Medication accessibility hint usage")
    must_contain(screen, "elderly_a11y_contact_edit_hint", "Contact edit accessibility hint usage")
    must_contain(screen, "elderly_a11y_contact_delete_hint", "Contact delete accessibility hint usage")
    must_contain(screen, "accessibilityElement(children: .ignore)", "VoiceOver custom element usage")
    label_count = len(re.findall(r"accessibilityLabel\(", screen))
    hint_count = len(re.findall(r"accessibilityHint\(", screen))
    require(label_count >= 10, f"Expected >=10 accessibility labels, got {label_count}")
    require(hint_count >= 8, f"Expected >=8 accessibility hints, got {hint_count}")
    for key in [
        "elderly_contacts_edit_permission_notice",
        "elderly_a11y_opens_details_hint",
        "elderly_a11y_calls_family_hint",
        "elderly_a11y_triggers_protection_hint",
        "elderly_a11y_marks_medication_hint",
        "elderly_a11y_sos_hint",
        "elderly_a11y_contact_edit_hint",
        "elderly_a11y_contact_delete_hint",
    ]:
        must_contain(l10n, f'"{key}"', f"Localization key `{key}`")
    print("OK accessibility localization contracts")


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
        "phase9.5 accessibility build",
    )
    must_match(out, r"\*\* BUILD SUCCEEDED \*\*", "Build result")
    print("OK build")


def main() -> int:
    print("PHASE 9.5 ELDERLY ACCESSIBILITY LOCALIZATION SMOKE")
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
