#!/usr/bin/env python3
"""
W7-2 / G18: verifies device matrix process documentation and CI wiring.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs/DEVICE_MATRIX_PROCESS_G18.md"
CI = ROOT / ".github/workflows/ci.yml"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def main() -> int:
    if not DOC.exists():
        print("❌ phase7_device_matrix_process_smoke failed")
        print("- missing docs/DEVICE_MATRIX_PROCESS_G18.md")
        return 1
    if not CI.exists():
        print("❌ phase7_device_matrix_process_smoke failed")
        print("- missing .github/workflows/ci.yml")
        return 1

    doc = read(DOC)
    ci = read(CI)

    required_doc_tokens = [
        "Owner:",
        "Cadence:",
        "Required Device Matrix",
        "Simulator | iPhone 13",
        "Simulator | iPhone 15 Pro",
        "Physical | iPhone 14/15 class",
        "Mandatory Flows",
        "Evidence And Sign-Off",
    ]
    missing_doc = [t for t in required_doc_tokens if t not in doc]

    required_ci_tokens = [
        "phase7_device_matrix_process_smoke.py",
        "platform=iOS Simulator,name=iPhone 13",
    ]
    missing_ci = [t for t in required_ci_tokens if t not in ci]

    if missing_doc or missing_ci:
        print("❌ phase7_device_matrix_process_smoke failed")
        if missing_doc:
            print(f"- missing in doc: {missing_doc}")
        if missing_ci:
            print(f"- missing in ci: {missing_ci}")
        return 1

    print("✅ phase7_device_matrix_process_smoke passed")
    print("- doc: docs/DEVICE_MATRIX_PROCESS_G18.md")
    print("- ci: .github/workflows/ci.yml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
