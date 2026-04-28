#!/usr/bin/env python3
"""Gate: child UI keys must resolve in RU+EN."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALIZATION_MANAGER = ROOT / "Core/Localization/LocalizationManager.swift"
RU_STRINGS = ROOT / "Resources/Localization/ru.lproj/Localizable.strings"
EN_STRINGS = ROOT / "Resources/Localization/en.lproj/Localizable.strings"

CHILD_CORE_SCREENS = [
    ROOT / "Screens/08_ChildInterfaceScreen.swift",
    ROOT / "Screens/ChildContentScreen.swift",
    ROOT / "Screens/ChildContentExperienceScreen.swift",
]

MANAGER_KEY_RE = re.compile(r'"([A-Za-z0-9_.:-]+)"\s*:')
LOCALIZED_CALL_RE = re.compile(r'localized\(\s*"([A-Za-z0-9_.:-]+)"')
STRINGS_LINE_RE = re.compile(r'^\s*"([^"]+)"\s*=\s*"((?:\\.|[^"\\])*)"\s*;\s*$')


def parse_strings(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = STRINGS_LINE_RE.match(line)
        if not match:
            continue
        values[match.group(1)] = match.group(2)
    return values


def parse_manager_language_block(
    content: str,
    anchor: str,
    language_pattern: str,
    next_pattern: str,
) -> set[str]:
    anchor_pos = content.find(anchor)
    if anchor_pos == -1:
        return set()
    scoped = content[anchor_pos:]
    start_match = re.search(language_pattern, scoped)
    if not start_match:
        return set()
    after_start = scoped[start_match.end():]
    next_match = re.search(next_pattern, after_start)
    if not next_match:
        return set()
    block = after_start[:next_match.start()]
    return set(MANAGER_KEY_RE.findall(block))


def collect_child_keys_from_core_screens() -> set[str]:
    keys: set[str] = set()
    for screen in CHILD_CORE_SCREENS:
        text = screen.read_text(encoding="utf-8", errors="ignore")
        keys.update(LOCALIZED_CALL_RE.findall(text))
    return {k for k in keys if k.startswith("child_")}


def main() -> int:
    manager_content = LOCALIZATION_MANAGER.read_text(encoding="utf-8")
    anchor = "var translations: [Language: [String: String]] = ["
    ru_manager_keys = parse_manager_language_block(
        manager_content,
        anchor=anchor,
        language_pattern=r"\n\s*\.russian:\s*\[",
        next_pattern=r"\n\s*\.english:\s*\[",
    )
    en_manager_keys = parse_manager_language_block(
        manager_content,
        anchor=anchor,
        language_pattern=r"\n\s*\.english:\s*\[",
        next_pattern=r"\n\s*\.arabic:\s*\[",
    )
    ru_strings = parse_strings(RU_STRINGS)
    en_strings = parse_strings(EN_STRINGS)

    child_keys = sorted(collect_child_keys_from_core_screens())

    missing_ru = [
        key for key in child_keys if key not in ru_manager_keys and key not in ru_strings
    ]
    missing_en = [
        key for key in child_keys if key not in en_manager_keys and key not in en_strings
    ]

    if missing_ru or missing_en:
        print("❌ child-localization-gate failed")
        if missing_ru:
            print(f"- Missing RU for {len(missing_ru)} keys: {missing_ru[:80]}")
        if missing_en:
            print(f"- Missing EN for {len(missing_en)} keys: {missing_en[:80]}")
        print("\nFix: add keys to LocalizationManager.swift or Localizable.strings.")
        return 1

    print("✅ child-localization-gate passed")
    print(f"- Child keys checked: {len(child_keys)}")
    print("- Coverage: RU+EN resolved via LocalizationManager and/or Localizable.strings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
