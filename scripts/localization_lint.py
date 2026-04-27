#!/usr/bin/env python3
"""Localization lint for RU/EN key parity and hardcoded UI text."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RU_FILE = ROOT / "Resources/Localization/ru.lproj/Localizable.strings"
EN_FILE = ROOT / "Resources/Localization/en.lproj/Localizable.strings"

SWIFT_DIRS = [
    ROOT / "Screens",
    ROOT / "Shared",
    ROOT / "ViewModels",
    ROOT / "Core",
]

ELDERLY_SCOPE_SWIFT_FILES = [
    ROOT / "Screens/09_ElderlyInterfaceScreen.swift",
]

SKIP_PATH_PARTS = {
    ".build",
    ".git",
    "CLEAN_EXPORT2_",
    "ARCHIVE_ONLY_DO_NOT_EDIT_",
    "backup",
    "Family_Registration_Removal_Files",
    "ML_SYSTEM_PACKAGE",
    "LocalizedVersions",
    "Tests",
}

SKIP_HARDCODED_FILE_NAMES = {
    "ImplementationPlanWorkbenchCard.swift",
    "SettingsScreenFallback.swift",
    "SettingsTestSuiteView.swift",
    "SettingsScreenMinimal.swift",
    "SimpleTestScreen.swift",
    "UIKitNavigationController.swift",
    "TrialFlowTestView.swift",
    "27_ProtectionStatsScreen.swift",
    "FamilyAnalyticsView.swift",
    "FamilyTournamentView.swift",
    "FamilyChatView.swift",
}

KEY_VALUE_RE = re.compile(r'^\s*"([^"]+)"\s*=\s*"((?:\\.|[^"\\])*)"\s*;\s*$')
PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[@dDuUxXfFeEgGcCsSpaA]")
LOCALIZED_KEY_RE = re.compile(r'localized\(\s*"([^"]+)"')
UNRESOLVED_VALUE_RE = re.compile(
    r"(?i)\b(todo|tbd|fixme|wip|replace_me|stub)\b|<#|{{|}}|__+[A-Z0-9_]+__+"
)

# P2-401: hard-gate for recently added Phase 2 modules.
REQUIRED_PHASE2_KEY_PREFIXES = [
    "child_music_drill_",
    "child_education_pathways_",
    "child_education_milestone_",
    "child_daily_journey_v3_",
    "child_creative_output_v2_",
]

REQUIRED_PHASE2_EXACT_KEYS = [
    "child_music_drill_title",
    "child_music_drill_metric_accuracy",
    "child_education_pathways_title",
    "child_education_milestone_title_1",
    "child_daily_journey_v3_title",
    "child_daily_journey_v3_reflection_prompt",
    "child_creative_output_v2_title",
    "child_creative_output_v2_done",
]

# Common hardcoded UI patterns. We only flag when text likely contains user-facing words.
HARDCODED_PATTERNS = [
    re.compile(r'Text\(\s*"([^"\n]*[A-Za-zА-Яа-яЁё][^"\n]*)"\s*\)'),
    re.compile(r'UILabel\(\s*.*text:\s*"([^"\n]*[A-Za-zА-Яа-яЁё][^"\n]*)"\s*'),
    re.compile(r'\.navigationTitle\(\s*"([^"\n]*[A-Za-zА-Яа-яЁё][^"\n]*)"\s*\)'),
    re.compile(r'UIAlertAction\(\s*title:\s*"([^"\n]*[A-Za-zА-Яа-яЁё][^"\n]*)"\s*'),
    re.compile(r'\.alert\(\s*"([^"\n]*[A-Za-zА-Яа-яЁё][^"\n]*)"\s*'),
    re.compile(r'\.sheet\(\s*.*\)\s*\{\s*.*Text\(\s*"([^"\n]*[A-Za-zА-Яа-яЁё][^"\n]*)"\s*\)', re.S),
]


@dataclass
class ParseResult:
    values: dict[str, str]
    duplicates: list[str]
    malformed_lines: list[int]


def should_skip(path: Path) -> bool:
    path_s = str(path)
    filename = path.name.lower()
    if "backup" in filename or "_old" in filename:
        return True
    return any(part in path_s for part in SKIP_PATH_PARTS)


def parse_strings_file(path: Path) -> ParseResult:
    values: dict[str, str] = {}
    duplicates: list[str] = []
    malformed_lines: list[int] = []

    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("//") or line.startswith("/*") or line.startswith("*"):
            continue
        match = KEY_VALUE_RE.match(line)
        if not match:
            # Ignore multiline comment closing.
            if line == "*/":
                continue
            malformed_lines.append(i)
            continue
        key, value = match.group(1), match.group(2)
        if key in values:
            duplicates.append(key)
        values[key] = value

    return ParseResult(values=values, duplicates=duplicates, malformed_lines=malformed_lines)


def placeholder_signature(value: str) -> tuple[str, ...]:
    return tuple(PLACEHOLDER_RE.findall(value))


def collect_swift_files() -> list[Path]:
    files: list[Path] = []
    for base in SWIFT_DIRS:
        if not base.exists():
            continue
        for path in base.rglob("*.swift"):
            if should_skip(path):
                continue
            files.append(path)
    return files


def likely_localization_key(text: str) -> bool:
    # Keys are dot/underscore separated and never contain spaces.
    return ("." in text or "_" in text) and " " not in text and text.lower() == text


def ignore_dynamic_or_nontext(text: str) -> bool:
    t = text.strip()
    if not t:
        return True
    if "\\(" in t:
        return True
    if t.startswith("\\(") and t.endswith(")"):
        return True
    if re.fullmatch(r"[\d\W_]+", t):
        return True
    return False


def scan_hardcoded_strings(paths: list[Path]) -> list[str]:
    violations: list[str] = []
    for path in paths:
        if path.name in SKIP_HARDCODED_FILE_NAMES:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        # Ignore debug-only preview/test literals.
        content = re.sub(r"#if\s+DEBUG[\s\S]*?#endif", "", content)
        lines = content.splitlines()
        for pattern in HARDCODED_PATTERNS:
            for match in pattern.finditer(content):
                text = match.group(1).strip()
                if not text:
                    continue
                if ignore_dynamic_or_nontext(text):
                    continue
                if likely_localization_key(text):
                    continue
                if text.startswith("http://") or text.startswith("https://"):
                    continue
                # Best-effort line number.
                line_no = content.count("\n", 0, match.start()) + 1
                violations.append(f"{path.relative_to(ROOT)}:{line_no}: hardcoded '{text}'")
        # Heuristic: direct NSLocalizedString with phrase instead of key.
        for idx, line in enumerate(lines, start=1):
            m = re.search(r'NSLocalizedString\(\s*"([^"]+)"\s*,', line)
            if m:
                key = m.group(1).strip()
                if likely_localization_key(key):
                    continue
                if re.search(r"[A-Za-zА-Яа-яЁё]{3,}", key):
                    violations.append(
                        f"{path.relative_to(ROOT)}:{idx}: NSLocalizedString uses non-key '{key}'"
                    )
    return violations


def collect_used_localization_keys(paths: list[Path]) -> set[str]:
    keys: set[str] = set()
    for path in paths:
        content = path.read_text(encoding="utf-8", errors="ignore")
        for match in LOCALIZED_KEY_RE.finditer(content):
            keys.add(match.group(1))
    return keys


def find_keys_by_prefix(keys: set[str], prefix: str) -> list[str]:
    return sorted([key for key in keys if key.startswith(prefix)])


def unresolved_value(value: str) -> bool:
    return bool(UNRESOLVED_VALUE_RE.search(value))


def collect_swift_files_for_scope(scope: str) -> list[Path]:
    if scope == "all":
        return collect_swift_files()
    if scope == "elderly60plus":
        return [path for path in ELDERLY_SCOPE_SWIFT_FILES if path.exists()]
    raise ValueError(f"Unknown scope: {scope}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Localization lint for RU/EN parity and hardcoded UI text."
    )
    parser.add_argument(
        "--scope",
        choices=["all", "elderly60plus"],
        default="all",
        help="Lint scope. Use elderly60plus for Phase 9.5 merge gate.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    errors: list[str] = []

    if not RU_FILE.exists() or not EN_FILE.exists():
        print("❌ Missing RU/EN localization files.")
        return 1

    ru = parse_strings_file(RU_FILE)
    en = parse_strings_file(EN_FILE)

    if ru.malformed_lines:
        errors.append(f"Malformed lines in RU file: {ru.malformed_lines[:20]}")
    if en.malformed_lines:
        errors.append(f"Malformed lines in EN file: {en.malformed_lines[:20]}")

    if ru.duplicates:
        errors.append(f"Duplicate RU keys: {sorted(set(ru.duplicates))[:30]}")
    if en.duplicates:
        errors.append(f"Duplicate EN keys: {sorted(set(en.duplicates))[:30]}")

    ru_keys = set(ru.values.keys())
    en_keys = set(en.values.keys())
    swift_files = collect_swift_files_for_scope(args.scope)
    if not swift_files:
        errors.append(f"No Swift files found for scope '{args.scope}'")

    parity_keys = ru_keys
    if args.scope != "all":
        parity_keys = collect_used_localization_keys(swift_files)

    if args.scope == "all":
        missing_in_en = sorted(parity_keys - en_keys)
        missing_in_ru = sorted(parity_keys - ru_keys)

        if missing_in_en:
            errors.append(f"Keys missing in EN: {missing_in_en[:40]}")
        if missing_in_ru:
            errors.append(f"Keys missing in RU: {missing_in_ru[:40]}")

        for key in sorted(parity_keys & ru_keys & en_keys):
            ru_sig = placeholder_signature(ru.values[key])
            en_sig = placeholder_signature(en.values[key])
            if ru_sig != en_sig:
                errors.append(
                    f"Placeholder mismatch for '{key}': RU={ru_sig} EN={en_sig}"
                )

        for prefix in REQUIRED_PHASE2_KEY_PREFIXES:
            ru_prefixed = find_keys_by_prefix(ru_keys, prefix)
            en_prefixed = find_keys_by_prefix(en_keys, prefix)
            if not ru_prefixed:
                errors.append(f"Missing RU keys for required Phase2 prefix '{prefix}'")
            if not en_prefixed:
                errors.append(f"Missing EN keys for required Phase2 prefix '{prefix}'")

        for key in REQUIRED_PHASE2_EXACT_KEYS:
            if key not in ru.values:
                errors.append(f"Missing required RU key '{key}'")
                continue
            if key not in en.values:
                errors.append(f"Missing required EN key '{key}'")
                continue
            if not ru.values[key].strip():
                errors.append(f"Empty RU value for required key '{key}'")
            if not en.values[key].strip():
                errors.append(f"Empty EN value for required key '{key}'")
            if unresolved_value(ru.values[key]):
                errors.append(f"Unresolved RU value for required key '{key}'")
            if unresolved_value(en.values[key]):
                errors.append(f"Unresolved EN value for required key '{key}'")

    hardcoded = scan_hardcoded_strings(swift_files)
    if hardcoded:
        errors.append("Hardcoded UI strings found:")
        errors.extend(hardcoded[:120])

    if errors:
        print("❌ localization-lint failed")
        for err in errors:
            print(f"- {err}")
        print("\nFix issues and run: python3 scripts/localization_lint.py")
        return 1

    print("✅ localization-lint passed")
    print(f"- Scope: {args.scope}")
    print(f"- RU keys: {len(ru_keys)}")
    print(f"- EN keys: {len(en_keys)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

