#!/usr/bin/env python3
"""Runtime-oriented localization integrity checks for child interface."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RU_STRINGS = ROOT / "Resources/Localization/ru.lproj/Localizable.strings"
EN_STRINGS = ROOT / "Resources/Localization/en.lproj/Localizable.strings"
CHILD_SCREENS = [
    ROOT / "Screens/08_ChildInterfaceScreen.swift",
    ROOT / "Screens/ChildContentScreen.swift",
    ROOT / "Screens/ChildContentExperienceScreen.swift",
]

STRINGS_LINE_RE = re.compile(r'^\s*"([^"]+)"\s*=\s*"((?:\\.|[^"\\])*)"\s*;\s*$')
RAW_CHILD_KEY_UI_RE = re.compile(r'\b(?:Text|Label|Button)\(\s*"child_[^"]+"')

REQUIRED_KEYS = [
    "child_daily_journey_title",
    "child_daily_journey_subtitle",
    "child_daily_journey_step_discover",
    "child_daily_journey_step_practice",
    "child_daily_journey_step_reflect",
    "child_daily_journey_v2_title",
    "child_daily_journey_v2_pacing_fast",
    "child_daily_journey_v2_pacing_steady",
    "child_daily_journey_v2_pacing_support",
    "child_daily_journey_v3_title",
    "child_daily_journey_v3_focus_explore",
    "child_daily_journey_v3_focus_build",
    "child_daily_journey_v3_focus_lead",
]


def parse_strings(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = STRINGS_LINE_RE.match(line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def main() -> int:
    ru = parse_strings(RU_STRINGS)
    en = parse_strings(EN_STRINGS)

    missing_ru = [k for k in REQUIRED_KEYS if k not in ru or not ru[k].strip()]
    missing_en = [k for k in REQUIRED_KEYS if k not in en or not en[k].strip()]

    raw_key_leaks: list[str] = []
    for screen in CHILD_SCREENS:
        text = screen.read_text(encoding="utf-8", errors="ignore")
        for m in RAW_CHILD_KEY_UI_RE.finditer(text):
            raw_key_leaks.append(f"{screen.relative_to(ROOT)}:{m.group(0)}")

    if missing_ru or missing_en or raw_key_leaks:
        print("❌ child-runtime-localization-integrity failed")
        if missing_ru:
            print(f"- Missing RU required keys: {missing_ru}")
        if missing_en:
            print(f"- Missing EN required keys: {missing_en}")
        if raw_key_leaks:
            print(f"- Raw child_* key render patterns found: {len(raw_key_leaks)}")
            for row in raw_key_leaks[:20]:
                print(f"  - {row}")
        return 1

    print("✅ child-runtime-localization-integrity passed")
    print(f"- Required journey keys in RU+EN: {len(REQUIRED_KEYS)}")
    print("- Raw UI child_* key render patterns: none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
