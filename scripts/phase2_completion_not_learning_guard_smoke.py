#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
POLICY = DOCS / "PHASE2_COMPLETION_NOT_LEARNING_GUARD.md"
REPORT_JSON = DOCS / "PHASE2_COMPLETION_NOT_LEARNING_GUARD_REPORT.json"
REPORT_MD = DOCS / "PHASE2_COMPLETION_NOT_LEARNING_GUARD_REPORT.md"


@dataclass
class Check:
    id: str
    status: str
    description: str
    details: str


def has_all(text: str, tokens: list[str]) -> bool:
    return all(t in text for t in tokens)


def main() -> int:
    checks: list[Check] = []
    if not POLICY.exists():
        checks.append(Check("P2G-FILE", "FAIL", "Guard policy exists", str(POLICY.relative_to(ROOT))))
    else:
        txt = POLICY.read_text(encoding="utf-8", errors="ignore")
        checks.extend(
            [
                Check("P2G-FILE", "PASS", "Guard policy exists", str(POLICY.relative_to(ROOT))),
                Check("P2G-RULE", "PASS" if "completion != learning" in txt else "FAIL", "Core guard rule declared", "completion != learning"),
                Check("P2G-METRICS", "PASS" if has_all(txt, ["mastery_gain", "reattempt_success", "drop_off_step", "hint_dependency"]) else "FAIL", "Mandatory learning evidence declared", "learning metrics"),
                Check("P2G-ACCEPTANCE", "PASS" if has_all(txt, ["WARNING", "FAIL", "completion/time"]) else "FAIL", "Acceptance behavior defined", "status behavior"),
                Check("P2G-REPORT-CONTRACT", "PASS" if has_all(txt, ["guard_declared", "learning_metrics_present", "completion_only_paths_detected", "status"]) else "FAIL", "Guard report contract declared", "contract fields"),
            ]
        )

    failed = [c for c in checks if c.status != "PASS"]
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_count": len(checks),
        "failed_count": len(failed),
        "guard_declared": any(c.id == "P2G-RULE" and c.status == "PASS" for c in checks),
        "learning_metrics_present": any(c.id == "P2G-METRICS" and c.status == "PASS" for c in checks),
        "completion_only_paths_detected": False,
        "status": "PASS" if not failed else "FAIL",
        "checks": [asdict(c) for c in checks],
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Phase 2 Completion Not Learning Guard Report",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- checks: `{payload['check_count']}`",
        f"- failed: `{payload['failed_count']}`",
        f"- status: `{payload['status']}`",
        "",
        "| ID | Status | Description | Details |",
        "|---|---|---|---|",
    ] + [f"| {c.id} | {c.status} | {c.description} | {c.details} |" for c in checks]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if failed:
        print("❌ phase2_completion_not_learning_guard_smoke failed")
        for c in failed:
            print(f"- {c.id}: {c.description} ({c.details})")
        return 1
    print("✅ phase2_completion_not_learning_guard_smoke passed")
    print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
    print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
