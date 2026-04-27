#!/usr/bin/env python3
"""
P2-003: category acceptance smoke scaffold for Phase 2.

Builds acceptance summary from:
- category status doc
- count gate report
- localization files parity presence
- core content screens/routes existence

Outputs JSON + markdown reports under docs/.
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
STATUS_DOC = DOCS / "PHASE2_CATEGORY_ACCEPTANCE_STATUS_ALL.md"
COUNT_GATE_JSON = DOCS / "PHASE2_CATEGORY_COUNT_GATE_REPORT.json"
REPORT_JSON = DOCS / "PHASE2_CATEGORY_ACCEPTANCE_SMOKE_REPORT.json"
REPORT_MD = DOCS / "PHASE2_CATEGORY_ACCEPTANCE_SMOKE_REPORT.md"
RU_LOC = ROOT / "Resources/Localization/ru.lproj/Localizable.strings"
EN_LOC = ROOT / "Resources/Localization/en.lproj/Localizable.strings"
CHILD_SCREEN = ROOT / "Screens/ChildContentScreen.swift"
EXPERIENCE_SCREEN = ROOT / "Screens/ChildContentExperienceScreen.swift"

CATEGORY_ORDER = [
    "toys",
    "drawing",
    "songs",
    "stories",
    "games",
    "study",
    "safety",
    "cartoons",
    "programming",
    "social",
    "music",
    "education",
]

STATUS_RE = re.compile(r"###\s+([a-z0-9_]+)\s*\n- Status:\s*`([^`]+)`", re.MULTILINE)


@dataclass
class CheckResult:
    id: str
    description: str
    status: str
    details: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 2 category acceptance smoke")
    parser.add_argument(
        "--enforce-ready",
        action="store_true",
        help="Fail unless all categories are READY and strict count gate has zero fails.",
    )
    return parser.parse_args()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_category_statuses(markdown: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for category, status in STATUS_RE.findall(markdown):
        parsed[category] = status.strip()
    return parsed


def run_checks(enforce_ready: bool) -> tuple[list[CheckResult], dict[str, str], dict]:
    checks: list[CheckResult] = []

    def add(id_: str, desc: str, ok: bool, details: str) -> None:
        checks.append(CheckResult(id=id_, description=desc, status="PASS" if ok else "FAIL", details=details))

    add("P2A-FILE-STATUS", "Category status doc exists", STATUS_DOC.exists(), str(STATUS_DOC.relative_to(ROOT)))
    add("P2A-FILE-COUNT-GATE", "Count gate report exists", COUNT_GATE_JSON.exists(), str(COUNT_GATE_JSON.relative_to(ROOT)))
    add("P2A-FILE-CHILD-SCREEN", "Child content screen exists", CHILD_SCREEN.exists(), str(CHILD_SCREEN.relative_to(ROOT)))
    add(
        "P2A-FILE-EXPERIENCE-SCREEN",
        "Child experience screen exists",
        EXPERIENCE_SCREEN.exists(),
        str(EXPERIENCE_SCREEN.relative_to(ROOT)),
    )
    add("P2A-FILE-RU", "RU localization file exists", RU_LOC.exists(), str(RU_LOC.relative_to(ROOT)))
    add("P2A-FILE-EN", "EN localization file exists", EN_LOC.exists(), str(EN_LOC.relative_to(ROOT)))

    statuses: dict[str, str] = {}
    count_gate_payload: dict = {}
    if STATUS_DOC.exists():
        statuses = parse_category_statuses(read(STATUS_DOC))
        missing = [c for c in CATEGORY_ORDER if c not in statuses]
        add(
            "P2A-STATUS-COVERAGE",
            "All 12 Phase 2 categories have status entries",
            not missing and len(statuses) >= 12,
            f"missing={missing}" if missing else "12/12 categories mapped",
        )
    else:
        add("P2A-STATUS-COVERAGE", "All 12 Phase 2 categories have status entries", False, "status doc missing")

    if COUNT_GATE_JSON.exists():
        count_gate_payload = json.loads(read(COUNT_GATE_JSON))
        check_count = int(count_gate_payload.get("check_count", 0))
        add("P2A-COUNT-COVERAGE", "Count gate contains 12 category checks", check_count == 12, f"check_count={check_count}")
    else:
        add("P2A-COUNT-COVERAGE", "Count gate contains 12 category checks", False, "count gate report missing")

    if RU_LOC.exists() and EN_LOC.exists():
        ru_text = read(RU_LOC)
        en_text = read(EN_LOC)
        required_keys = ["child_content_loading", "child_content_error_message", "child_content_empty_title"]
        ok = all(f'"{k}"' in ru_text and f'"{k}"' in en_text for k in required_keys)
        add("P2A-I18N-BASE", "RU/EN include baseline child content acceptance keys", ok, ", ".join(required_keys))

    if enforce_ready:
        all_ready = all(statuses.get(c) == "READY" for c in CATEGORY_ORDER)
        strict_ok = count_gate_payload.get("profile") == "phase2_strict" and int(count_gate_payload.get("failed_count", 1)) == 0
        add("P2A-READY-ENFORCED", "All categories are READY", all_ready, f"ready_count={sum(1 for c in CATEGORY_ORDER if statuses.get(c) == 'READY')}/12")
        add("P2A-COUNT-STRICT", "Strict count gate has no failures", strict_ok, f"profile={count_gate_payload.get('profile')} failed={count_gate_payload.get('failed_count')}")

    return checks, statuses, count_gate_payload


def write_reports(checks: list[CheckResult], statuses: dict[str, str], count_gate_payload: dict, enforce_ready: bool) -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    ready = sum(1 for c in CATEGORY_ORDER if statuses.get(c) == "READY")
    ready_with_conditions = sum(1 for c in CATEGORY_ORDER if statuses.get(c) == "READY WITH CONDITIONS")
    not_ready = sum(1 for c in CATEGORY_ORDER if statuses.get(c) == "NOT READY")
    failed = [c for c in checks if c.status != "PASS"]

    payload = {
        "generated_at": generated_at,
        "enforce_ready": enforce_ready,
        "check_count": len(checks),
        "failed_count": len(failed),
        "category_summary": {
            "ready": ready,
            "ready_with_conditions": ready_with_conditions,
            "not_ready": not_ready,
        },
        "count_gate_profile": count_gate_payload.get("profile"),
        "count_gate_failed_count": count_gate_payload.get("failed_count"),
        "checks": [asdict(c) for c in checks],
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Phase 2 Category Acceptance Smoke Report",
        "",
        f"- generated_at: `{generated_at}`",
        f"- enforce_ready: `{enforce_ready}`",
        f"- checks: `{len(checks)}`",
        f"- failed: `{len(failed)}`",
        f"- summary: `READY={ready}`, `READY WITH CONDITIONS={ready_with_conditions}`, `NOT READY={not_ready}`",
        f"- count_gate_profile: `{count_gate_payload.get('profile')}`",
        f"- count_gate_failed: `{count_gate_payload.get('failed_count')}`",
        "",
        "| ID | Status | Description | Details |",
        "|---|---|---|---|",
    ]
    for c in checks:
        lines.append(f"| {c.id} | {c.status} | {c.description} | {c.details} |")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    checks, statuses, count_gate_payload = run_checks(args.enforce_ready)
    write_reports(checks, statuses, count_gate_payload, args.enforce_ready)
    failed = [c for c in checks if c.status != "PASS"]
    if failed:
        print("❌ phase2_category_acceptance_smoke failed")
        for c in failed:
            print(f"- {c.id}: {c.description} ({c.details})")
        print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
        print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
        return 1
    print("✅ phase2_category_acceptance_smoke passed")
    print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
    print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
