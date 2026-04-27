#!/usr/bin/env python3
"""
P2-004: Learning Effectiveness Gates scaffold.

Tracks mandatory gates:
- mastery_gain
- reattempt_success
- drop_off_step
- hint_dependency

This script validates that the repository has the required structural hooks and
can enforce strict readiness mode when the metrics are formally wired.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
MODELS = ROOT / "Core/Content/Models/ContentModels.swift"
VALIDATOR = ROOT / "Core/Content/Validation/ContentValidator.swift"
PROGRESS = ROOT / "Core/Content/Progress/ProgressSystems.swift"
ACCEPTANCE_SMOKE = DOCS / "PHASE2_CATEGORY_ACCEPTANCE_SMOKE_REPORT.json"
REPORT_JSON = DOCS / "PHASE2_LEARNING_EFFECTIVENESS_GATE_REPORT.json"
REPORT_MD = DOCS / "PHASE2_LEARNING_EFFECTIVENESS_GATE_REPORT.md"

REQUIRED_METRICS = ["mastery_gain", "reattempt_success", "drop_off_step", "hint_dependency"]


@dataclass
class CheckResult:
    id: str
    description: str
    status: str
    details: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 2 learning effectiveness gate")
    parser.add_argument(
        "--enforce-signals",
        action="store_true",
        help="Fail unless all four learning metrics are explicitly wired and marked available.",
    )
    return parser.parse_args()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def run_checks(enforce_signals: bool) -> tuple[list[CheckResult], dict]:
    checks: list[CheckResult] = []

    def add(id_: str, description: str, ok: bool, details: str) -> None:
        checks.append(CheckResult(id=id_, description=description, status="PASS" if ok else "FAIL", details=details))

    add("P2L-FILE-1", "Content models file exists", MODELS.exists(), str(MODELS.relative_to(ROOT)))
    add("P2L-FILE-2", "Content validator file exists", VALIDATOR.exists(), str(VALIDATOR.relative_to(ROOT)))
    add("P2L-FILE-3", "Progress systems file exists", PROGRESS.exists(), str(PROGRESS.relative_to(ROOT)))
    add(
        "P2L-FILE-4",
        "Acceptance smoke report exists",
        ACCEPTANCE_SMOKE.exists(),
        str(ACCEPTANCE_SMOKE.relative_to(ROOT)),
    )

    model_text = read(MODELS) if MODELS.exists() else ""
    validator_text = read(VALIDATOR) if VALIDATOR.exists() else ""
    progress_text = read(PROGRESS) if PROGRESS.exists() else ""

    add(
        "P2L-CONTRACT-1",
        "Learning outcome contract fields exist in model layer",
        all(token in model_text for token in ["ContentLearningOutcomeContract", "difficultyLevel", "assessmentType"]),
        "ContentLearningOutcomeContract + key fields",
    )
    add(
        "P2L-CONTRACT-2",
        "Validator checks learning contract presence/quality",
        "validateLearningOutcomeContract" in validator_text,
        "validateLearningOutcomeContract(...)",
    )
    add(
        "P2L-ANALYTICS-BASE",
        "Progress system has baseline tracking hooks",
        all(token in progress_text for token in ["recordOpen", "recordCompletion", "ParentActivityDailyAggregator"]),
        "recordOpen/recordCompletion/daily aggregator",
    )

    acceptance_payload: dict = {}
    if ACCEPTANCE_SMOKE.exists():
        acceptance_payload = json.loads(read(ACCEPTANCE_SMOKE))
    available_metrics: list[str] = acceptance_payload.get("learning_effectiveness_metrics_available", [])
    add(
        "P2L-METRICS-DECL",
        "Learning metrics declaration present in acceptance smoke report",
        isinstance(available_metrics, list),
        f"declared={available_metrics}",
    )

    if enforce_signals:
        missing = [m for m in REQUIRED_METRICS if m not in available_metrics]
        add(
            "P2L-METRICS-STRICT",
            "All required learning effectiveness metrics are wired",
            not missing,
            f"missing={missing}" if missing else "all required metrics declared",
        )

    return checks, acceptance_payload


def write_reports(checks: list[CheckResult], enforce_signals: bool, acceptance_payload: dict) -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    failed = [c for c in checks if c.status != "PASS"]
    available_metrics = acceptance_payload.get("learning_effectiveness_metrics_available", [])
    payload = {
        "generated_at": generated_at,
        "enforce_signals": enforce_signals,
        "required_metrics": REQUIRED_METRICS,
        "learning_effectiveness_metrics_available": available_metrics,
        "check_count": len(checks),
        "failed_count": len(failed),
        "checks": [asdict(c) for c in checks],
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Phase 2 Learning Effectiveness Gate Report",
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
        print("❌ phase2_learning_effectiveness_gate failed")
        for c in failed:
            print(f"- {c.id}: {c.description} ({c.details})")
        print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
        print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
        return 1
    print("✅ phase2_learning_effectiveness_gate passed")
    print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
    print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
