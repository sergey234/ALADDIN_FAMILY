#!/usr/bin/env python3
"""
Phase 8.2 UX smoke checks.

Validates:
1) Age-segment UX coverage (child profile + seeded content age bands)
2) Accessibility baseline (VoiceOver + Dynamic Type hooks)
3) Reduce Motion and readability hooks
4) Animation performance coverage contract
5) Screen-size validation through multi-device simulator builds
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import time


ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJECT = "ALADDIN.xcodeproj"
SCHEME = "ALADDIN"

# Screen-size matrix: small phone, large phone, tablet.
DEVICE_MATRIX: list[tuple[str, str]] = [
    ("iPhone SE (2nd generation)", "AE4850FB-CDAB-4B5B-B765-92CC04F4781B"),
    ("iPhone 16 Pro Max", "39BB07B2-0793-462E-8F21-AB12CA9525D1"),
    ("iPad Air 11-inch (M3)", "02B945E1-9B6C-4F62-8DE4-E1544ABF2783"),
]
BUILD_TIMEOUT_SEC = 420
BUILD_RETRIES = 2


def read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def must_contain(text: str, needle: str, context: str) -> None:
    require(needle in text, f"{context}: missing `{needle}`")


def must_match(text: str, pattern: str, context: str) -> None:
    require(re.search(pattern, text, flags=re.MULTILINE) is not None, f"{context}: missing pattern `{pattern}`")


def run(cmd: list[str], context: str) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"{context} failed\n"
            f"CMD: {' '.join(cmd)}\n"
            f"STDOUT:\n{proc.stdout}\n"
            f"STDERR:\n{proc.stderr}"
        )
    return proc.stdout + proc.stderr


def diagnose_failure(output: str) -> str:
    if "Unable to find a device matching the provided destination specifier" in output:
        return "simulator_destination_unavailable"
    if "timed out waiting for all destinations" in output:
        return "simulator_boot_timeout"
    if "** BUILD FAILED **" in output:
        return "build_failed"
    if "xcodebuild: error:" in output:
        return "xcodebuild_error"
    return "unknown"


def run_with_retry(cmd: list[str], context: str, timeout_sec: int, retries: int) -> str:
    errors: list[str] = []
    for attempt in range(1, retries + 1):
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec)
            output = proc.stdout + proc.stderr
            if proc.returncode == 0:
                return output
            cause = diagnose_failure(output)
            errors.append(f"attempt={attempt} returncode={proc.returncode} cause={cause}")
        except subprocess.TimeoutExpired:
            errors.append(f"attempt={attempt} timeout={timeout_sec}s cause=command_timeout")
        if attempt < retries:
            time.sleep(2)
    raise RuntimeError(
        f"{context} failed after {retries} attempts\n"
        f"CMD: {' '.join(cmd)}\n"
        f"ROOT_CAUSE_TRACE: {'; '.join(errors)}"
    )


def check_age_coverage() -> None:
    child_profile = read("Core/Profile/ChildProfile.swift")
    for case_name in ("preschool4to6", "school7to10", "tween11to13", "teen14plus"):
        must_contain(child_profile, f"case {case_name}", "ChildProfile age groups")

    seed = read("Core/Content/Seed/ContentSeedProvider.swift")
    for age_band in ("kids_1_6", "school_7_12", "teen_13_17", "youngAdult_18_22"):
        must_contain(seed, f".{age_band}", "Content seed age-band coverage")
    print("OK age-segment UX coverage")


def check_accessibility_baseline() -> None:
    accessibility_manager = read("Core/Accessibility/AccessibilityManager.swift")
    must_contain(accessibility_manager, "UIAccessibility.isVoiceOverRunning", "Accessibility manager voiceover hook")
    must_contain(accessibility_manager, "UIContentSizeCategory.didChangeNotification", "Accessibility manager dynamic type hook")
    must_contain(accessibility_manager, "reduceMotionStatusDidChangeNotification", "Accessibility manager reduce motion hook")

    parental = read("Screens/07_ParentalControlScreen.swift")
    family = read("Screens/02_FamilyScreen.swift")
    must_contain(parental, ".accessibilityLabel(", "Parental screen accessibility labels")
    must_contain(family, ".accessibilityLabel(", "Family screen accessibility labels")
    must_contain(parental, ".minimumScaleFactor(", "Parental screen dynamic text readability")
    must_contain(family, ".minimumScaleFactor(", "Family screen dynamic text readability")
    print("OK accessibility baseline (VoiceOver + large text)")


def check_reduce_motion_and_readability() -> None:
    files = [
        "Screens/ChildRewardsScreen.swift",
        "Screens/YoungDefenderView.swift",
        "Screens/ChildContentScreen.swift",
        "Core/Animation/AnimatedButton.swift",
        "Core/Animation/TransitionManager.swift",
    ]
    count = 0
    for rel in files:
        body = read(rel)
        if "@Environment(\\.accessibilityReduceMotion)" in body:
            count += 1
    require(count >= 3, "Reduce Motion adoption is insufficient across animation-heavy surfaces")
    print("OK reduce-motion readability coverage")


def check_animation_performance_contract() -> None:
    perf_tests = read("Tests/UnitTests/PerformanceBenchmarkTests.swift")
    must_contain(perf_tests, "testUIRenderingPerformance", "Animation performance test coverage")
    must_contain(perf_tests, "testPerformanceStability", "Animation performance stability coverage")
    must_contain(perf_tests, "testHighLoadPerformance", "Animation/perf load coverage")
    print("OK animation performance contract coverage")


def check_screen_size_matrix_build() -> None:
    for label, device_id in DEVICE_MATRIX:
        output = run_with_retry(
            [
                "xcodebuild",
                "-project",
                PROJECT,
                "-scheme",
                SCHEME,
                "-sdk",
                "iphonesimulator",
                "-destination",
                f"id={device_id}",
                "build",
            ],
            f"{label} build",
            timeout_sec=BUILD_TIMEOUT_SEC,
            retries=BUILD_RETRIES,
        )
        must_match(output, r"\*\* BUILD SUCCEEDED \*\*", f"{label} build")
        print(f"OK screen-size build: {label}")


def main() -> int:
    print("PHASE 8.2 UX SMOKE")
    check_age_coverage()
    check_accessibility_baseline()
    check_reduce_motion_and_readability()
    check_animation_performance_contract()
    check_screen_size_matrix_build()
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
