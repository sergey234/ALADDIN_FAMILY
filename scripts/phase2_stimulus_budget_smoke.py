#!/usr/bin/env python3
"""
P2-408: Stimulus budget policy smoke for ages 1-6.

Validates policy structure and required limits/mappings.
Writes:
- docs/PHASE2_STIMULUS_BUDGET_REPORT.json
- docs/PHASE2_STIMULUS_BUDGET_REPORT.md
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
POLICY_DOC = DOCS / "PHASE2_STIMULUS_BUDGET_POLICY_1_6.md"
REPORT_JSON = DOCS / "PHASE2_STIMULUS_BUDGET_REPORT.json"
REPORT_MD = DOCS / "PHASE2_STIMULUS_BUDGET_REPORT.md"

KIDS_CATEGORIES = [
    "child_interface_category_toys",
    "child_interface_category_drawing",
    "child_interface_category_songs",
    "child_interface_category_stories",
]


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
        "P2S-FILE-POLICY",
        "category",
        "Stimulus budget policy document exists",
        POLICY_DOC.exists(),
        str(POLICY_DOC.relative_to(ROOT)),
    )
    if not POLICY_DOC.exists():
        return checks

    content = POLICY_DOC.read_text(encoding="utf-8", errors="ignore")

    add(
        "P2S-LIMITS",
        "category",
        "Numeric budget limits are declared",
        has_all(content, ["effects_per_minute_max", "rewards_per_minute_max", "high_intensity_burst_max"]),
        "effects/rewards/burst limits",
    )
    add(
        "P2S-SCOPE",
        "category",
        "All 1-6 categories are in scope",
        all(c in content for c in KIDS_CATEGORIES),
        f"scope_count={sum(1 for c in KIDS_CATEGORIES if c in content)}/{len(KIDS_CATEGORIES)}",
    )
    add(
        "P2S-MAP-EFFECTS",
        "item",
        "Effects event mapping is declared",
        has_all(content, ["Effects events", "mascot emotion/activity", "surprise visual event", "animated transition"]),
        "effects mapping",
    )
    add(
        "P2S-MAP-REWARDS",
        "item",
        "Rewards event mapping is declared",
        has_all(content, ["Rewards events", "skill progress reward", "completion reward", "surprise reward"]),
        "rewards mapping",
    )
    add(
        "P2S-GUARDRAIL-EFFECTS",
        "item",
        "Effects threshold fallback is declared",
        has_all(content, ["If `effects/min` exceeds threshold", "reduced animation preset"]),
        "effects fallback",
    )
    add(
        "P2S-GUARDRAIL-REWARDS",
        "item",
        "Rewards threshold fallback is declared",
        has_all(content, ["If `rewards/min` exceeds threshold", "summary reward"]),
        "rewards fallback",
    )
    add(
        "P2S-GUARDRAIL-CALM",
        "item",
        "Calm mode escalation is declared",
        has_all(content, ["calm mode", "suppress non-critical effects", "milestone rewards"]),
        "calm mode",
    )
    add(
        "P2S-ACCEPTANCE",
        "category",
        "Acceptance rule for policy validity is defined",
        has_all(content, ["Acceptance Rule", "smoke report passes", "report artifacts"]),
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
        "# Phase 2 Stimulus Budget Report",
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
        print("❌ phase2_stimulus_budget_smoke failed")
        for c in failed:
            print(f"- {c.id}: {c.description} ({c.details})")
        print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
        print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
        return 1
    print("✅ phase2_stimulus_budget_smoke passed")
    print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
    print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
