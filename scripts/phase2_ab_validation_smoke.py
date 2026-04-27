#!/usr/bin/env python3
"""
P2-406: A/B validation framework smoke for task formats.

Checks framework documentation and two-level QA declarations (category + item).
Writes reports:
- docs/PHASE2_AB_VALIDATION_SMOKE_REPORT.json
- docs/PHASE2_AB_VALIDATION_SMOKE_REPORT.md
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
FRAMEWORK_DOC = DOCS / "PHASE2_AB_VALIDATION_FRAMEWORK.md"
REPORT_JSON = DOCS / "PHASE2_AB_VALIDATION_SMOKE_REPORT.json"
REPORT_MD = DOCS / "PHASE2_AB_VALIDATION_SMOKE_REPORT.md"


@dataclass
class CheckResult:
    id: str
    level: str
    description: str
    status: str
    details: str


def has_all(content: str, tokens: list[str]) -> bool:
    return all(token in content for token in tokens)


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

    add(
        "P2AB-FILE-FRAMEWORK",
        "category",
        "A/B framework document exists",
        FRAMEWORK_DOC.exists(),
        str(FRAMEWORK_DOC.relative_to(ROOT)),
    )

    if not FRAMEWORK_DOC.exists():
        return checks

    content = FRAMEWORK_DOC.read_text(encoding="utf-8", errors="ignore")

    add(
        "P2AB-VARIANTS-CORE",
        "category",
        "Core format variants are declared (short/long, text/visual)",
        has_all(content, ["short", "long", "text", "visual"]),
        "tokens: short,long,text,visual",
    )
    add(
        "P2AB-VARIANTS-GROUPS",
        "category",
        "All experiment groups A1/A2/B1/B2 are declared",
        has_all(content, ["A1", "A2", "B1", "B2"]),
        "groups: A1,A2,B1,B2",
    )
    add(
        "P2AB-ASSIGNMENT",
        "category",
        "Deterministic assignment policy is declared",
        has_all(content, ["Deterministic bucketing", "child_id", "category_id", "day_key"]),
        "deterministic assignment contract",
    )
    add(
        "P2AB-TELEMETRY",
        "item",
        "Telemetry contract fields are declared",
        has_all(
            content,
            [
                "experiment_id",
                "variant_id",
                "completion_rate",
                "first_pass_success",
                "hint_dependency",
                "time_to_complete_sec",
                "drop_off_step",
                "reattempt_success",
                "boredom_signal",
            ],
        ),
        "required telemetry fields",
    )
    add(
        "P2AB-QA-CATEGORY",
        "category",
        "Category-level QA matrix rules are present",
        has_all(content, ["Category-level", "deterministic assignment enabled"]),
        "category-level QA rules",
    )
    add(
        "P2AB-QA-ITEM",
        "item",
        "Item-level QA matrix rules are present",
        has_all(content, ["Item-level", "item has declared format", "telemetry fields"]),
        "item-level QA rules",
    )
    add(
        "P2AB-ACCEPTANCE",
        "category",
        "Acceptance rule for framework validity is defined",
        has_all(content, ["Acceptance Rule", "all 4 variants", "QA checks pass"]),
        "framework acceptance criteria",
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
        "# Phase 2 A/B Validation Smoke Report",
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
        print("❌ phase2_ab_validation_smoke failed")
        for c in failed:
            print(f"- {c.id}: {c.description} ({c.details})")
        print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
        print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
        return 1
    print("✅ phase2_ab_validation_smoke passed")
    print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
    print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
