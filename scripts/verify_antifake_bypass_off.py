#!/usr/bin/env python3
"""Q-01 / G-03 — assert iOS QA bypass is OFF before App Store submit."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "Core/Security/AntifakeAccessPolicy.swift"


def main() -> int:
    text = POLICY.read_text(encoding="utf-8")
    m = re.search(r"bypassPremiumGate:\s*Bool\s*=\s*(true|false)", text)
    if not m:
        print("FAIL bypassPremiumGate declaration not found")
        return 1
    value = m.group(1)
    if value == "true":
        print("FAIL G-03/Q-01: bypassPremiumGate is still true — set false before submit")
        print(json.dumps({"pass": False, "bypassPremiumGate": True}))
        return 1
    if "UITestAntifakeHubSmoke" not in text:
        print("WARN UITestAntifakeHubSmoke hook not found — Q-02 UITest may need Premium on sim")
    print("OK  G-03/Q-01 bypassPremiumGate=false")
    print(json.dumps({"pass": True, "bypassPremiumGate": False, "gate": "antifake_bypass_off"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
