#!/usr/bin/env python3
"""
P2-002: category count gate for Phase 2 content.

Reads `Core/Content/Seed/ContentSeedProvider.swift`, calculates item count per category
from `seedTitles(...)` arrays, and validates against configured thresholds.
Writes JSON + markdown reports under docs/.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SEED_FILE = ROOT / "Core/Content/Seed/ContentSeedProvider.swift"
REPORT_JSON = DOCS / "PHASE2_CATEGORY_COUNT_GATE_REPORT.json"
REPORT_MD = DOCS / "PHASE2_CATEGORY_COUNT_GATE_REPORT.md"

# Baseline profile: fits current repository seed density.
BASELINE_THRESHOLDS: dict[str, int] = {
    "child_interface_category_toys": 3,
    "child_interface_category_drawing": 3,
    "child_interface_category_songs": 3,
    "child_interface_category_stories": 3,
    "child_interface_category_games": 3,
    "child_interface_category_study": 3,
    "child_interface_category_safety": 3,
    "child_interface_category_cartoons": 3,
    "child_interface_category_programming": 3,
    "child_interface_category_social": 3,
    "child_interface_category_music": 3,
    "child_interface_category_education": 3,
}

# Strict profile: original Phase 2 target wording.
PHASE2_STRICT_THRESHOLDS: dict[str, int] = {
    "child_interface_category_toys": 15,
    "child_interface_category_drawing": 10,
    "child_interface_category_songs": 15,
    "child_interface_category_stories": 10,
    "child_interface_category_games": 20,
    "child_interface_category_study": 30,
    "child_interface_category_safety": 15,
    "child_interface_category_cartoons": 15,
    "child_interface_category_programming": 15,
    "child_interface_category_social": 15,
    "child_interface_category_music": 15,
    "child_interface_category_education": 15,
}

CASE_RE = re.compile(r"case\s+([A-Za-z0-9_\.]+):")
ITEM_RE = re.compile(r'"([^"\\]|\\.)*"')


@dataclass
class CountCheck:
    category_id: str
    actual: int
    required: int
    status: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 2 category count gate")
    parser.add_argument(
        "--profile",
        choices=["baseline", "phase2_strict"],
        default="baseline",
        help="Threshold profile to validate.",
    )
    return parser.parse_args()


def count_seed_titles(seed_swift: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    start_marker = "private func seedTitles(for category: String) -> [String] {"
    start_idx = seed_swift.find(start_marker)
    if start_idx == -1:
        return counts
    seed_scope = seed_swift[start_idx:]
    lines = seed_scope.splitlines()
    idx = 0
    while idx < len(lines):
        line = lines[idx].strip()
        match = CASE_RE.search(line)
        if not match:
            idx += 1
            continue
        case_token = match.group(1)
        idx += 1
        # Find `return [ ... ]` block for this case.
        while idx < len(lines) and "return [" not in lines[idx]:
            idx += 1
        if idx >= len(lines):
            break
        item_count = 0
        return_line = lines[idx]
        item_count += len(ITEM_RE.findall(return_line))
        # Inline array case: `return ["a", "b"]`
        if "]" in return_line:
            category_id = case_to_category_id(case_token)
            if category_id:
                counts[category_id] = item_count
            idx += 1
            continue
        idx += 1
        while idx < len(lines) and "]" not in lines[idx]:
            item_count += len(ITEM_RE.findall(lines[idx]))
            idx += 1
        category_id = case_to_category_id(case_token)
        if category_id:
            counts[category_id] = item_count
        idx += 1
    return counts


def case_to_category_id(case_token: str) -> str | None:
    known: dict[str, str] = {
        "ChildCategoryKey.toys": "child_interface_category_toys",
        "ChildCategoryKey.drawing": "child_interface_category_drawing",
        "ChildCategoryKey.songs": "child_interface_category_songs",
        "ChildCategoryKey.stories": "child_interface_category_stories",
        "ChildCategoryKey.games": "child_interface_category_games",
        "ChildCategoryKey.study": "child_interface_category_study",
        "ChildCategoryKey.safety": "child_interface_category_safety",
        "ChildCategoryKey.cartoons": "child_interface_category_cartoons",
        "ChildCategoryKey.programming": "child_interface_category_programming",
        "ChildCategoryKey.social": "child_interface_category_social",
        "ChildCategoryKey.music": "child_interface_category_music",
        "ChildCategoryKey.education": "child_interface_category_education",
    }
    return known.get(case_token)


def run_gate(profile: str) -> list[CountCheck]:
    thresholds = BASELINE_THRESHOLDS if profile == "baseline" else PHASE2_STRICT_THRESHOLDS
    content = SEED_FILE.read_text(encoding="utf-8", errors="ignore")
    counts = count_seed_titles(content)
    checks: list[CountCheck] = []
    for category_id, required in thresholds.items():
        actual = counts.get(category_id, 0)
        checks.append(
            CountCheck(
                category_id=category_id,
                actual=actual,
                required=required,
                status="PASS" if actual >= required else "FAIL",
            )
        )
    return checks


def write_reports(profile: str, checks: list[CountCheck]) -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    failed = [c for c in checks if c.status != "PASS"]
    payload = {
        "generated_at": generated_at,
        "profile": profile,
        "check_count": len(checks),
        "failed_count": len(failed),
        "checks": [asdict(c) for c in checks],
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Phase 2 Category Count Gate Report",
        "",
        f"- generated_at: `{generated_at}`",
        f"- profile: `{profile}`",
        f"- checks: `{len(checks)}`",
        f"- failed: `{len(failed)}`",
        "",
        "| Category | Actual | Required | Status |",
        "|---|---:|---:|---|",
    ]
    for c in checks:
        lines.append(f"| {c.category_id} | {c.actual} | {c.required} | {c.status} |")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    checks = run_gate(args.profile)
    write_reports(args.profile, checks)
    failed = [c for c in checks if c.status != "PASS"]
    if failed:
        print("❌ phase2_category_count_gate failed")
        print(f"- profile: {args.profile}")
        for c in failed:
            print(f"- {c.category_id}: actual={c.actual} required={c.required}")
        print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
        print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
        return 1
    print("✅ phase2_category_count_gate passed")
    print(f"- profile: {args.profile}")
    print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
    print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
