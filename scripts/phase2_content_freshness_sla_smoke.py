#!/usr/bin/env python3
"""
P2-407: Content freshness SLA smoke.

Validates SLA policy doc + category/item-level freshness guards.
Writes:
- docs/PHASE2_CONTENT_FRESHNESS_SLA_REPORT.json
- docs/PHASE2_CONTENT_FRESHNESS_SLA_REPORT.md
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SLA_DOC = DOCS / "PHASE2_CONTENT_FRESHNESS_SLA.md"
SEED_FILE = ROOT / "Core/Content/Seed/ContentSeedProvider.swift"
REPORT_JSON = DOCS / "PHASE2_CONTENT_FRESHNESS_SLA_REPORT.json"
REPORT_MD = DOCS / "PHASE2_CONTENT_FRESHNESS_SLA_REPORT.md"

TOP_CATEGORIES = [
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
class CheckResult:
    id: str
    level: str
    description: str
    status: str
    details: str


def has_all(content: str, tokens: list[str]) -> bool:
    return all(token in content for token in tokens)


def case_to_category_id(case_token: str) -> str | None:
    mapping = {
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
    marker = "private func seedTitles(for category: String) -> [String] {"
    start_idx = seed_swift.find(marker)
    if start_idx == -1:
        return result
    lines = seed_swift[start_idx:].splitlines()
    idx = 0
    while idx < len(lines):
        m = CASE_RE.search(lines[idx].strip())
        if not m:
            idx += 1
            continue
        category_id = case_to_category_id(m.group(1))
        idx += 1
        while idx < len(lines) and "return [" not in lines[idx]:
            idx += 1
        if idx >= len(lines):
            break
        titles: list[str] = ITEM_RE.findall(lines[idx])
        if "]" not in lines[idx]:
            idx += 1
            while idx < len(lines) and "]" not in lines[idx]:
                titles.extend(ITEM_RE.findall(lines[idx]))
                idx += 1
        if category_id:
            result[category_id] = titles
        idx += 1
    return result


def run_checks() -> list[CheckResult]:
    checks: list[CheckResult] = []

    def add(id_: str, level: str, desc: str, ok: bool, details: str) -> None:
        checks.append(
            CheckResult(
                id=id_,
                level=level,
                description=desc,
                status="PASS" if ok else "FAIL",
                details=details,
            )
        )

    add("P2F-FILE-SLA", "category", "SLA policy document exists", SLA_DOC.exists(), str(SLA_DOC.relative_to(ROOT)))
    add("P2F-FILE-SEED", "item", "Seed provider exists", SEED_FILE.exists(), str(SEED_FILE.relative_to(ROOT)))

    if not (SLA_DOC.exists() and SEED_FILE.exists()):
        return checks

    sla = SLA_DOC.read_text(encoding="utf-8", errors="ignore")
    seed = SEED_FILE.read_text(encoding="utf-8", errors="ignore")
    by_category = parse_seed_titles(seed)

    add(
        "P2F-POLICY-CORE",
        "category",
        "SLA policy includes cadence and thresholds",
        has_all(sla, ["Refresh cadence", "Hard warning threshold", "Hard fail threshold"]),
        "cadence + warning/fail thresholds",
    )
    add(
        "P2F-POLICY-FALLBACK",
        "category",
        "SLA includes emergency fallback window",
        has_all(sla, ["Emergency fallback", "24h"]),
        "fallback <=24h",
    )
    add(
        "P2F-SCOPE-TOP",
        "category",
        "All top categories are included in SLA scope",
        all(category in sla for category in TOP_CATEGORIES),
        f"scope_count={sum(1 for c in TOP_CATEGORIES if c in sla)}/{len(TOP_CATEGORIES)}",
    )
    add(
        "P2F-CONTRACT-META",
        "category",
        "Metadata contract fields are declared",
        has_all(sla, ["category_id", "freshness_tier", "last_refresh_at", "refresh_due_at", "owner"]),
        "metadata contract",
    )

    top_titles = []
    min_items_ok = True
    for category in TOP_CATEGORIES:
        titles = by_category.get(category, [])
        top_titles.extend(titles)
        if len(titles) < 3:
            min_items_ok = False
    add(
        "P2F-ITEM-MIN",
        "item",
        "Top categories satisfy minimum item baseline",
        min_items_ok,
        "required>=3 each top category",
    )

    non_empty_ok = all(t.strip() for t in top_titles)
    placeholder_ok = all(not PLACEHOLDER_RE.search(t) for t in top_titles)
    add("P2F-ITEM-NONEMPTY", "item", "Top-category items are non-empty", non_empty_ok, f"items={len(top_titles)}")
    add(
        "P2F-ITEM-NOPLACEHOLDER",
        "item",
        "Top-category items have no placeholder tokens",
        placeholder_ok,
        "blocked: todo/tbd/placeholder/replace_me/fixme/lorem",
    )

    return checks


def write_reports(checks: list[CheckResult]) -> None:
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
        "# Phase 2 Content Freshness SLA Report",
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
        print("❌ phase2_content_freshness_sla_smoke failed")
        for c in failed:
            print(f"- {c.id}: {c.description} ({c.details})")
        print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
        print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
        return 1
    print("✅ phase2_content_freshness_sla_smoke passed")
    print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
    print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
