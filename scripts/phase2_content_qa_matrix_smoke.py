#!/usr/bin/env python3
"""
P2-405: Content QA matrix smoke for Phase 2 (category + item levels).

Builds a two-level QA snapshot from ContentSeedProvider and writes:
- docs/PHASE2_CONTENT_QA_MATRIX_REPORT.json
- docs/PHASE2_CONTENT_QA_MATRIX_REPORT.md
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SEED_FILE = ROOT / "Core/Content/Seed/ContentSeedProvider.swift"
REPORT_JSON = DOCS / "PHASE2_CONTENT_QA_MATRIX_REPORT.json"
REPORT_MD = DOCS / "PHASE2_CONTENT_QA_MATRIX_REPORT.md"

PHASE2_CATEGORY_IDS = [
    "child_interface_category_toys",
    "child_interface_category_drawing",
    "child_interface_category_songs",
    "child_interface_category_stories",
    "child_interface_category_games",
    "child_interface_category_study",
    "child_interface_category_safety",
    "child_interface_category_cartoons",
    "child_interface_category_programming",
    "child_interface_category_social",
    "child_interface_category_music",
    "child_interface_category_education",
]

CASE_RE = re.compile(r"case\s+([A-Za-z0-9_\.]+):")
ITEM_RE = re.compile(r'"((?:\\.|[^"\\])*)"')
PLACEHOLDER_RE = re.compile(r"(?i)(todo|tbd|placeholder|replace_me|fixme|lorem)")


@dataclass
class MatrixCheck:
    id: str
    level: str
    status: str
    description: str
    details: str


def case_to_category_id(case_token: str) -> str | None:
    mapping = {
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
    return mapping.get(case_token)


def parse_seed_titles(seed_swift: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    start_marker = "private func seedTitles(for category: String) -> [String] {"
    start_idx = seed_swift.find(start_marker)
    if start_idx == -1:
        return result

    lines = seed_swift[start_idx:].splitlines()
    idx = 0
    while idx < len(lines):
        line = lines[idx].strip()
        match = CASE_RE.search(line)
        if not match:
            idx += 1
            continue

        category_id = case_to_category_id(match.group(1))
        idx += 1
        while idx < len(lines) and "return [" not in lines[idx]:
            idx += 1
        if idx >= len(lines):
            break

        titles: list[str] = []
        return_line = lines[idx]
        titles.extend(ITEM_RE.findall(return_line))
        if "]" in return_line:
            if category_id:
                result[category_id] = titles
            idx += 1
            continue

        idx += 1
        while idx < len(lines) and "]" not in lines[idx]:
            titles.extend(ITEM_RE.findall(lines[idx]))
            idx += 1
        if category_id:
            result[category_id] = titles
        idx += 1
    return result


def run_checks() -> list[MatrixCheck]:
    checks: list[MatrixCheck] = []

    if not SEED_FILE.exists():
        return [
            MatrixCheck(
                id="P2Q-FILE-SEED",
                level="category",
                status="FAIL",
                description="Seed provider file exists",
                details=str(SEED_FILE.relative_to(ROOT)),
            )
        ]

    content = SEED_FILE.read_text(encoding="utf-8", errors="ignore")
    by_category = parse_seed_titles(content)

    checks.append(
        MatrixCheck(
            id="P2Q-CAT-COVERAGE",
            level="category",
            status="PASS" if all(c in by_category for c in PHASE2_CATEGORY_IDS) else "FAIL",
            description="All 12 Phase 2 categories have QA entries",
            details=f"covered={sum(1 for c in PHASE2_CATEGORY_IDS if c in by_category)}/12",
        )
    )

    for category_id in PHASE2_CATEGORY_IDS:
        titles = by_category.get(category_id, [])
        checks.append(
            MatrixCheck(
                id=f"P2Q-CAT-{category_id.split('_')[-1].upper()}",
                level="category",
                status="PASS" if len(titles) >= 3 else "FAIL",
                description=f"Category '{category_id}' has minimum item set",
                details=f"items={len(titles)} required>=3",
            )
        )

    all_titles: list[str] = []
    for cid in PHASE2_CATEGORY_IDS:
        all_titles.extend(by_category.get(cid, []))

    non_empty_ok = all(title.strip() for title in all_titles)
    min_len_ok = all(len(title.strip()) >= 3 for title in all_titles)
    placeholder_ok = all(not PLACEHOLDER_RE.search(title) for title in all_titles)
    unique_global_ok = len(set(all_titles)) == len(all_titles)
    unique_per_category_ok = all(
        len(set(by_category.get(cid, []))) == len(by_category.get(cid, []))
        for cid in PHASE2_CATEGORY_IDS
    )

    checks.append(
        MatrixCheck(
            id="P2Q-ITEM-NONEMPTY",
            level="item",
            status="PASS" if non_empty_ok else "FAIL",
            description="Item titles are non-empty",
            details=f"total_items={len(all_titles)}",
        )
    )
    checks.append(
        MatrixCheck(
            id="P2Q-ITEM-MINLEN",
            level="item",
            status="PASS" if min_len_ok else "FAIL",
            description="Item titles satisfy minimum length",
            details="min_length>=3",
        )
    )
    checks.append(
        MatrixCheck(
            id="P2Q-ITEM-NOPLACEHOLDER",
            level="item",
            status="PASS" if placeholder_ok else "FAIL",
            description="Item titles contain no placeholder tokens",
            details="blocked: todo/tbd/placeholder/replace_me/fixme/lorem",
        )
    )
    checks.append(
        MatrixCheck(
            id="P2Q-ITEM-UNIQUE-GLOBAL",
            level="item",
            status="PASS" if unique_global_ok else "FAIL",
            description="Item titles are globally unique across Phase 2",
            details=f"unique={len(set(all_titles))} total={len(all_titles)}",
        )
    )
    checks.append(
        MatrixCheck(
            id="P2Q-ITEM-UNIQUE-CATEGORY",
            level="item",
            status="PASS" if unique_per_category_ok else "FAIL",
            description="Item titles are unique inside each category",
            details="per-category uniqueness",
        )
    )
    checks.append(
        MatrixCheck(
            id="P2Q-ITEM-TOTAL",
            level="item",
            status="PASS" if len(all_titles) >= 36 else "FAIL",
            description="Total item count satisfies Phase 2 baseline",
            details=f"total_items={len(all_titles)} required>=36",
        )
    )

    return checks


def write_reports(checks: list[MatrixCheck]) -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    failed = [c for c in checks if c.status != "PASS"]
    category_checks = [c for c in checks if c.level == "category"]
    item_checks = [c for c in checks if c.level == "item"]
    payload = {
        "generated_at": generated_at,
        "check_count": len(checks),
        "failed_count": len(failed),
        "category_level": {
            "check_count": len(category_checks),
            "failed_count": sum(1 for c in category_checks if c.status != "PASS"),
        },
        "item_level": {
            "check_count": len(item_checks),
            "failed_count": sum(1 for c in item_checks if c.status != "PASS"),
        },
        "checks": [asdict(c) for c in checks],
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Phase 2 Content QA Matrix Report",
        "",
        f"- generated_at: `{generated_at}`",
        f"- checks: `{payload['check_count']}`",
        f"- failed: `{payload['failed_count']}`",
        f"- category_level_failed: `{payload['category_level']['failed_count']}`",
        f"- item_level_failed: `{payload['item_level']['failed_count']}`",
        "",
        "| ID | Level | Status | Description | Details |",
        "|---|---|---|---|---|",
    ]
    for c in checks:
        lines.append(f"| {c.id} | {c.level} | {c.status} | {c.description} | {c.details} |")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    checks = run_checks()
    write_reports(checks)
    failed = [c for c in checks if c.status != "PASS"]
    if failed:
        print("❌ phase2_content_qa_matrix_smoke failed")
        for c in failed:
            print(f"- {c.id}: {c.description} ({c.details})")
        print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
        print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
        return 1
    print("✅ phase2_content_qa_matrix_smoke passed")
    print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
    print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
