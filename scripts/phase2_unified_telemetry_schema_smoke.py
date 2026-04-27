#!/usr/bin/env python3
"""
P2-601: Unified telemetry schema smoke.

Validates Learning + Engagement + Freshness unified schema document.
Writes:
- docs/PHASE2_UNIFIED_TELEMETRY_SCHEMA_REPORT.json
- docs/PHASE2_UNIFIED_TELEMETRY_SCHEMA_REPORT.md
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SCHEMA_DOC = DOCS / "PHASE2_UNIFIED_TELEMETRY_SCHEMA.md"
REPORT_JSON = DOCS / "PHASE2_UNIFIED_TELEMETRY_SCHEMA_REPORT.json"
REPORT_MD = DOCS / "PHASE2_UNIFIED_TELEMETRY_SCHEMA_REPORT.md"


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
        "P2T-FILE-SCHEMA",
        "category",
        "Unified telemetry schema document exists",
        SCHEMA_DOC.exists(),
        str(SCHEMA_DOC.relative_to(ROOT)),
    )
    if not SCHEMA_DOC.exists():
        return checks

    content = SCHEMA_DOC.read_text(encoding="utf-8", errors="ignore")

    add(
        "P2T-BLOCKS",
        "category",
        "Learning/Engagement/Freshness blocks are declared",
        has_all(content, ["## Learning Block", "## Engagement Block", "## Freshness Block"]),
        "three mandatory blocks",
    )
    add(
        "P2T-CORE-ENVELOPE",
        "item",
        "Core envelope fields are declared",
        has_all(content, ["event_id", "event_name", "ts_utc", "child_id", "category_id", "item_id", "session_id"]),
        "core envelope",
    )
    add(
        "P2T-LEARNING-FIELDS",
        "item",
        "Learning metrics fields are declared",
        has_all(content, ["mastery_gain", "reattempt_success", "drop_off_step", "hint_dependency", "first_pass_success"]),
        "learning fields",
    )
    add(
        "P2T-ENGAGEMENT-FIELDS",
        "item",
        "Engagement metrics fields are declared",
        has_all(content, ["session_depth", "used_seconds", "completion_rate", "boredom_signal", "d1_d7_voluntary_return"]),
        "engagement fields",
    )
    add(
        "P2T-FRESHNESS-FIELDS",
        "item",
        "Freshness metrics fields are declared",
        has_all(content, ["content_last_refresh_at", "content_refresh_due_at", "freshness_sla_status", "staleness_seconds"]),
        "freshness fields",
    )
    add(
        "P2T-EVENT-FAMILIES",
        "category",
        "Event families are declared",
        has_all(
            content,
            [
                "learning_outcome_updated",
                "engagement_checkpoint",
                "freshness_window_evaluated",
                "parent_dashboard_digest_generated",
            ],
        ),
        "event families",
    )
    add(
        "P2T-VALIDATION-RULES",
        "category",
        "Validation rules section is present",
        has_all(content, ["## Validation Rules", "freshness status must be enum-like"]),
        "validation rules",
    )
    add(
        "P2T-ACCEPTANCE",
        "category",
        "Acceptance rule is declared",
        has_all(content, ["## Acceptance Rule", "smoke report passes", "report artifacts"]),
        "acceptance criteria",
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
        "# Phase 2 Unified Telemetry Schema Report",
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
        print("❌ phase2_unified_telemetry_schema_smoke failed")
        for c in failed:
            print(f"- {c.id}: {c.description} ({c.details})")
        print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
        print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
        return 1
    print("✅ phase2_unified_telemetry_schema_smoke passed")
    print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
    print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
