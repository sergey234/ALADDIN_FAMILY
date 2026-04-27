#!/usr/bin/env python3
"""
Phase 8.1 smoke checks for:
1) Content correctness (contract + manifest/delta shape check).
2) Validation on different devices (iPhone + iPad simulator builds).
"""

from __future__ import annotations

import re
import subprocess
import sys
import time


PROJECT = "ALADDIN.xcodeproj"
SCHEME = "ALADDIN"
IPHONE_DEST_ID = "B98F9663-BB22-481C-B4C4-6D7E88F1E017"  # iPhone 16 (OS 18.4)
IPAD_DEST_ID = "02B945E1-9B6C-4F62-8DE4-E1544ABF2783"  # iPad Air 11-inch (M3, OS 18.4)
BUILD_TIMEOUT_SEC = 420
BUILD_RETRIES = 2


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


def check_content_contract() -> None:
    output = run([sys.executable, "scripts/content_contract_smoke.py"], "content contract smoke")
    if "SMOKE RESULT: PASS" not in output:
        raise RuntimeError("content contract smoke did not report PASS")
    print("OK content correctness smoke")


def check_device_build(destination_id: str, label: str) -> None:
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
            f"id={destination_id}",
            "build",
        ],
        f"{label} build",
        timeout_sec=BUILD_TIMEOUT_SEC,
        retries=BUILD_RETRIES,
    )
    if re.search(r"\*\* BUILD SUCCEEDED \*\*", output) is None:
        raise RuntimeError(f"{label} build output missing BUILD SUCCEEDED marker")
    print(f"OK device build: {label}")


def main() -> int:
    print("PHASE 8.1 CONTENT+DEVICE SMOKE")
    check_content_contract()
    check_device_build(IPHONE_DEST_ID, "iPhone 16")
    check_device_build(IPAD_DEST_ID, "iPad Air 11-inch (M3)")
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
