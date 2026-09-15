#!/usr/bin/env python3
"""Find hardcoded Cyrillic UI strings that bypass LocalizationManager.

Usage (from ALADDIN_iOS root):
  python3 scripts/find_hardcoded_ru_ui.py
  python3 scripts/find_hardcoded_ru_ui.py --top 40
  python3 scripts/find_hardcoded_ru_ui.py --path Screens/12_NotificationsScreen.swift

Excludes: LocalizationManager, BACKUP/_Old, mocks, generated mirrors, DEBUG-only comments.
"""

from __future__ import annotations

import argparse
import os
import re
from collections import Counter

ROOTS = ("Screens", "Shared", "ViewModels", "Components", "UI", "ALADDINWidgets", "Core")
SKIP_NAME = re.compile(
    r"(BACKUP|_Old|FULL_BACKUP|CURRENT_BACKUP|TestSuite|TrialFlowTest|"
    r"Mirror\.generated|MockAPI|LocalizationManager|ContentSeed)",
    re.I,
)
CYR_STR = re.compile(r'"([^"\\]*[А-Яа-яЁё][^"\\]*)"')
UI_HINTS = (
    "Text(",
    "title:",
    "subtitle:",
    "message:",
    "Button(",
    "Label(",
    "ProgressView(",
    "navigationTitle",
    "Section(",
    "alert",
    "placeholder",
    "Prompt(",
)


def iter_hits(path_filter: str | None):
    for root in ROOTS:
        if not os.path.isdir(root):
            continue
        for dp, dns, fs in os.walk(root):
            dns[:] = [d for d in dns if not SKIP_NAME.search(d)]
            for name in fs:
                if not name.endswith(".swift"):
                    continue
                if SKIP_NAME.search(name) or SKIP_NAME.search(dp):
                    continue
                path = os.path.join(dp, name)
                if path_filter and path_filter not in path:
                    continue
                with open(path, encoding="utf-8", errors="ignore") as fh:
                    for i, line in enumerate(fh, 1):
                        if "localized(" in line:
                            continue
                        stripped = line.strip()
                        if stripped.startswith("//") or stripped.startswith("*"):
                            continue
                        if not any(h in line for h in UI_HINTS):
                            continue
                        for m in CYR_STR.finditer(line):
                            yield path, i, m.group(1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=30, help="Top files by hit count")
    ap.add_argument("--path", default=None, help="Substring filter for file path")
    ap.add_argument("--limit", type=int, default=80, help="Max sample lines to print")
    args = ap.parse_args()

    hits = list(iter_hits(args.path))
    print(f"Hardcoded RU UI candidates: {len(hits)}")
    print("--- by file ---")
    for path, count in Counter(p for p, _, _ in hits).most_common(args.top):
        print(f"{count:4}  {path}")
    print("--- samples ---")
    for path, line, text in hits[: args.limit]:
        safe = text.replace("\n", " ")[:120]
        print(f"{path}:{line}: {safe}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
