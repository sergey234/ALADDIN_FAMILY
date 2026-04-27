#!/usr/bin/env python3
"""
META-3 smoke: validate sync integration policy documentation and test guard rails.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
POLICY = ROOT / "docs/SYNC_BETWEEN_DEVICES_POLICY_META3.md"
TEST_FILE = ROOT / "Tests/Integration/SyncBetweenDevicesTests.swift"
CI = ROOT / ".github/workflows/ci.yml"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def main() -> int:
    missing = [str(p.relative_to(ROOT)) for p in [POLICY, TEST_FILE, CI] if not p.exists()]
    if missing:
        print("❌ meta3_sync_policy_smoke failed")
        print(f"- missing files: {missing}")
        return 1

    policy_text = read(POLICY)
    test_text = read(TEST_FILE)
    ci_text = read(CI)

    policy_tokens = ["SYNC_INTEGRATION_MODE", "RUN_SYNC_INTEGRATION_TESTS", "XCTSkip"]
    test_tokens = ["SYNC_INTEGRATION_MODE", "RUN_SYNC_INTEGRATION_TESTS", "XCTSkip"]
    ci_tokens = ["meta3_sync_policy_smoke.py"]

    missing_policy = [t for t in policy_tokens if t not in policy_text]
    missing_test = [t for t in test_tokens if t not in test_text]
    missing_ci = [t for t in ci_tokens if t not in ci_text]

    if missing_policy or missing_test or missing_ci:
        print("❌ meta3_sync_policy_smoke failed")
        if missing_policy:
            print(f"- missing policy tokens: {missing_policy}")
        if missing_test:
            print(f"- missing test tokens: {missing_test}")
        if missing_ci:
            print(f"- missing ci tokens: {missing_ci}")
        return 1

    print("✅ meta3_sync_policy_smoke passed")
    print("- policy: docs/SYNC_BETWEEN_DEVICES_POLICY_META3.md")
    print("- test guard: Tests/Integration/SyncBetweenDevicesTests.swift")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
