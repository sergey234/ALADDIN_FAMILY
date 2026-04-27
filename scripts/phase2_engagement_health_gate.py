#!/usr/bin/env python3
"""
P2-005: Engagement Health Gates scaffold.

Tracks mandatory engagement gates:
- session_depth
- d1_d7_voluntary_return
- boredom_signal
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
PROGRESS = ROOT / "Core/Content/Progress/ProgressSystems.swift"
CHILD_SCREEN = ROOT / "Screens/ChildContentScreen.swift"
ACCEPTANCE_SMOKE = DOCS / "PHASE2_CATEGORY_ACCEPTANCE_SMOKE_REPORT.json"
REPORT_JSON = DOCS / "PHASE2_ENGAGEMENT_HEALTH_GATE_REPORT.json"
REPORT_MD = DOCS / "PHASE2_ENGAGEMENT_HEALTH_GATE_REPORT.md"

REQUIRED_METRICS = ["session_depth", "d1_d7_voluntary_return", "boredom_signal"]


@dataclass
class CheckResult:
    id: str
    description: str
    status: str
    details: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 2 engagement health gate")
    parser.add_argument(
        "--enforce-signals",
        action="store_true",
        help="Fail unless all engagement metrics are explicitly wired and declared available.",
    )
    return parser.parse_args()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def run_checks(enforce_signals: bool) -> tuple[list[CheckResult], dict]:
    checks: list[CheckResult] = []

    def add(id_: str, description: str, ok: bool, details: str) -> None:
        checks.append(CheckResult(id=id_, description=description, status="PASS" if ok else "FAIL", details=details))

    add("P2E-FILE-1", "Progress systems file exists", PROGRESS.exists(), str(PROGRESS.relative_to(ROOT)))
    add("P2E-FILE-2", "Child content screen exists", CHILD_SCREEN.exists(), str(CHILD_SCREEN.relative_to(ROOT)))
    add(
        "P2E-FILE-3",
        "Acceptance smoke report exists",
        ACCEPTANCE_SMOKE.exists(),
        str(ACCEPTANCE_SMOKE.relative_to(ROOT)),
    )

    progress_text = read(PROGRESS) if PROGRESS.exists() else ""
    child_text = read(CHILD_SCREEN) if CHILD_SCREEN.exists() else ""

    add(
        "P2E-SIGNAL-BASE-1",
        "Session-depth baseline hooks exist",
        all(token in progress_text for token in ["usedSeconds", "recordOpen", "recordCompletion"]),
        "usedSeconds + opens/completions tracking",
    )
    add(
        "P2E-SIGNAL-BASE-2",
        "Child flow has loading/empty/error states for dropout observation",
        all(token in child_text for token in ["case .loading", "case .empty", "case .error"]),
        "loading/empty/error branches",
    )
    add(
        "P2E-SIGNAL-BASE-3",
        "Daily trend points available for retention proxies",
        "trendPoints" in progress_text and "ParentDashboardDayPoint" in progress_text,
        "ParentActivityDailyAggregator.trendPoints",
    )

    acceptance_payload: dict = {}
    if ACCEPTANCE_SMOKE.exists():
        acceptance_payload = json.loads(read(ACCEPTANCE_SMOKE))
    available_metrics: list[str] = acceptance_payload.get("engagement_health_metrics_available", [])
    add(
        "P2E-METRICS-DECL",
        "Engagement metrics declaration present in acceptance smoke report",
        isinstance(available_metrics, list),
        f"declared={available_metrics}",
    )

    if enforce_signals:
        missing = [m for m in REQUIRED_METRICS if m not in available_metrics]
        add(
            "P2E-METRICS-STRICT",
            "All required engagement metrics are wired",
            not missing,
            f"missing={missing}" if missing else "all required metrics declared",
        )

    return checks, acceptance_payload


def write_reports(checks: list[CheckResult], enforce_signals: bool, acceptance_payload: dict) -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    failed = [c for c in checks if c.status != "PASS"]
    available_metrics = acceptance_payload.get("engagement_health_metrics_available", [])
    payload = {
        "generated_at": generated_at,
        "enforce_signals": enforce_signals,
        "required_metrics": REQUIRED_METRICS,
        "engagement_health_metrics_available": available_metrics,
        "check_count": len(checks),
        "failed_count": len(failed),
        "checks": [asdict(c) for c in checks],
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Phase 2 Engagement Health Gate Report",
        "",
        f"- generated_at: `{generated_at}`",
        f"- enforce_signals: `{enforce_signals}`",
        f"- checks: `{len(checks)}`",
        f"- failed: `{len(failed)}`",
        f"- required_metrics: `{', '.join(REQUIRED_METRICS)}`",
        f"- available_metrics: `{', '.join(available_metrics) if available_metrics else '(none declared)'}`",
        "",
        "| ID | Status | Description | Details |",
        "|---|---|---|---|",
    ]
    for c in checks:
        lines.append(f"| {c.id} | {c.status} | {c.description} | {c.details} |")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    checks, acceptance_payload = run_checks(args.enforce_signals)
    write_reports(checks, args.enforce_signals, acceptance_payload)
    failed = [c for c in checks if c.status != "PASS"]
    if failed:
        print("❌ phase2_engagement_health_gate failed")
        for c in failed:
            print(f"- {c.id}: {c.description} ({c.details})")
        print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
        print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
        return 1
    print("✅ phase2_engagement_health_gate passed")
    print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
    print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
