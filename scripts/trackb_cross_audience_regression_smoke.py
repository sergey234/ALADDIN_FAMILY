#!/usr/bin/env python3
"""
Track B smoke: mandatory cross-audience regression for phases 2, 7, 9.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    # Phase 2 / shared content lifecycle evidence
    "Core/Content/ContentManager.swift",
    "Core/Content/Seed/ContentSeedProvider.swift",
    # Phase 7 family/parent controls evidence
    "Screens/07_ParentalControlScreen.swift",
    "Core/Profile/FamilyAccessPolicy.swift",
    # Phase 9 child + elderly interfaces and integration smoke
    "Screens/08_ChildInterfaceScreen.swift",
    "Screens/09_ElderlyInterfaceScreen.swift",
    "scripts/phase9_family_flow_integration_smoke.py",
]


def require(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def main() -> int:
    print("TRACK B CROSS-AUDIENCE REGRESSION SMOKE")
    for rel in REQUIRED_FILES:
        require((ROOT / rel).exists(), f"Missing required artifact: {rel}")

    content_manager = (ROOT / "Core/Content/ContentManager.swift").read_text(encoding="utf-8")
    require("runUnifiedLifecycle" in content_manager, "Missing unified lifecycle entrypoint")
    require("loadUnifiedAudienceFeed" in content_manager, "Missing unified audience feed API")

    phase9_script = (ROOT / "scripts/phase9_family_flow_integration_smoke.py").read_text(encoding="utf-8")
    require("FamilyPermissionLayer.snapshot" in phase9_script, "Missing family permission integration evidence")
    require("UnifiedFamilyRoster.contactProjections" in phase9_script, "Missing unified roster integration evidence")

    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
