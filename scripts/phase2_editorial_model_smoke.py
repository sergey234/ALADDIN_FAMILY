#!/usr/bin/env python3
"""
P2-006: smoke check for content editorial model package.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
MODEL_DOC = DOCS / "PHASE2_CONTENT_EDITORIAL_MODEL.md"
REPORT_JSON = DOCS / "PHASE2_EDITORIAL_MODEL_SMOKE_REPORT.json"
REPORT_MD = DOCS / "PHASE2_EDITORIAL_MODEL_SMOKE_REPORT.md"


@dataclass
class CheckResult:
    id: str
    description: str
    status: str
    details: str


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def run_checks() -> list[CheckResult]:
    checks: list[CheckResult] = []

    def add(id_: str, description: str, ok: bool, details: str) -> None:
        checks.append(CheckResult(id=id_, description=description, status="PASS" if ok else "FAIL", details=details))

    add("P2R-FILE-1", "Editorial model doc exists", MODEL_DOC.exists(), str(MODEL_DOC.relative_to(ROOT)))

    if not MODEL_DOC.exists():
        return checks

    content = read(MODEL_DOC)
    add("P2R-RUBRIC-1", "Item quality rubric section exists", "## 1) Item Quality Rubric" in content, "rubric section")
    add("P2R-REVIEW-1", "Manifest peer review section exists", "## 2) Manifest Peer Review" in content, "peer-review section")
    add("P2R-DEPREC-1", "Deprecation policy section exists", "## 3) Deprecation Policy" in content, "deprecation section")
    add("P2R-RUBRIC-2", "Rubric has minimum acceptance score rule", "Minimum acceptance score" in content, "score threshold")
    add("P2R-REVIEW-2", "Peer review defines decision outcomes", "APPROVED_WITH_CONDITIONS" in content, "decision outcomes")
    add("P2R-DEPREC-2", "Deprecation lifecycle states defined", "DEPRECATION_CANDIDATE" in content and "HARD_DEPRECATED" in content, "lifecycle states")
    return checks


def write_reports(checks: list[CheckResult]) -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    failed = [c for c in checks if c.status != "PASS"]
    payload = {
        "generated_at": generated_at,
        "check_count": len(checks),
        "failed_count": len(failed),
        "checks": [asdict(c) for c in checks],
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Phase 2 Editorial Model Smoke Report",
        "",
        f"- generated_at: `{generated_at}`",
        f"- checks: `{len(checks)}`",
        f"- failed: `{len(failed)}`",
        "",
        "| ID | Status | Description | Details |",
        "|---|---|---|---|",
    ]
    for c in checks:
        lines.append(f"| {c.id} | {c.status} | {c.description} | {c.details} |")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    checks = run_checks()
    write_reports(checks)
    failed = [c for c in checks if c.status != "PASS"]
    if failed:
        print("❌ phase2_editorial_model_smoke failed")
        for c in failed:
            print(f"- {c.id}: {c.description} ({c.details})")
        print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
        print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
        return 1
    print("✅ phase2_editorial_model_smoke passed")
    print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
    print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
