#!/usr/bin/env python3
"""
Track B smoke: namespace-map usage and anti-duplicate key hygiene.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
NAMESPACE_MAP = ROOT / "docs/LOCALIZATION_KEY_NAMESPACE_MAP.md"
L10N = ROOT / "Core/Localization/LocalizationManager.swift"
PHASE9_FILES = [
    ROOT / "Screens/07_ParentalControlScreen.swift",
    ROOT / "Screens/08_ChildInterfaceScreen.swift",
    ROOT / "Screens/09_ElderlyInterfaceScreen.swift",
    ROOT / "Screens/ParentDashboardView.swift",
]
KEY_RE = re.compile(r'localized\(\s*"([^"]+)"')

# Legacy project currently uses underscore namespaces.
ALLOWED_PREFIXES = (
    "common_",
    "family_",
    "family_category_",
    "parental_",
    "child_",
    "elderly_",
    "parent_dashboard_",
    "a11y_",
    "component.",
    "content_",
    "content_blocker_",
    "settings_",
    "network_",
    "protection_",
)
FORBIDDEN_SUFFIXES = ("_new", "_v2", "_temp", "_final")


def require(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def collect_keys() -> set[str]:
    keys: set[str] = set()
    for path in PHASE9_FILES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        keys.update(KEY_RE.findall(text))
    return keys


def main() -> int:
    print("TRACK B NAMESPACE MAP SMOKE")
    require(NAMESPACE_MAP.exists(), "Missing namespace map document")
    require(L10N.exists(), "Missing localization manager")

    keys = collect_keys()
    require(keys, "No localized keys found in phase files")

    bad_prefix = sorted(
        key for key in keys
        if not key.startswith(ALLOWED_PREFIXES)
    )
    require(not bad_prefix, f"Keys out of allowed namespace prefixes: {bad_prefix[:15]}")

    bad_suffix = sorted(
        key for key in keys
        if key.endswith(FORBIDDEN_SUFFIXES)
    )
    require(not bad_suffix, f"Keys with unstable suffixes: {bad_suffix[:15]}")

    # Minimal anti-duplicate check for newly introduced parent dashboard mirror namespace.
    l10n_text = L10N.read_text(encoding="utf-8", errors="ignore")
    mirror_keys = [k for k in keys if k.startswith("parent_dashboard_")]
    for key in mirror_keys:
        require(f'"{key}"' in l10n_text, f"Missing mirror key in localization map: {key}")

    print(f"SMOKE RESULT: PASS ({len(keys)} phase keys checked)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
