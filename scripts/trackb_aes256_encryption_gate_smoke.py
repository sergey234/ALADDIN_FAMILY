#!/usr/bin/env python3
"""
Track B smoke: AES-256 gate artifact exists with security anchors.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC = ROOT / "docs/TRACKB_AES256_ENCRYPTION_GATE.md"


def require(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def main() -> int:
    print("TRACK B AES256 ENCRYPTION GATE SMOKE")
    require(DOC.exists(), "Missing AES-256 gate document")
    text = DOC.read_text(encoding="utf-8")
    require("AES-256" in text, "AES-256 marker missing in gate document")
    for anchor in [
        "Core/Security/KeychainManager.swift",
        "Core/Managers/TokenManager.swift",
        "Core/Network/NetworkManager.swift",
    ]:
        require(anchor in text, f"Missing evidence anchor: {anchor}")

    # best-effort static evidence across codebase
    code_matches = []
    for path in [ROOT / "Core"]:
        for swift in path.rglob("*.swift"):
            content = swift.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"AES|CryptoKit|Keychain|SecItem", content):
                code_matches.append(swift)
                if len(code_matches) >= 3:
                    break
        if len(code_matches) >= 3:
            break
    require(len(code_matches) >= 1, "No security/encryption evidence found in Core/*.swift")

    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
