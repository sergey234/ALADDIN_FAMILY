#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
POLICY = DOCS / "PHASE2_CONTENT_HEALTH_DASHBOARD_ALERTING.md"
REPORT_JSON = DOCS / "PHASE2_CONTENT_HEALTH_DASHBOARD_REPORT.json"
REPORT_MD = DOCS / "PHASE2_CONTENT_HEALTH_DASHBOARD_REPORT.md"


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
        checks.append(Check("P2H-FILE", "FAIL", "Health dashboard policy exists", str(POLICY.relative_to(ROOT))))
    else:
        txt = POLICY.read_text(encoding="utf-8", errors="ignore")
        checks.extend(
            [
                Check("P2H-FILE", "PASS", "Health dashboard policy exists", str(POLICY.relative_to(ROOT))),
                Check("P2H-PANELS", "PASS" if has_all(txt, ["Gate status timeline", "Category readiness distribution", "KPI trend"]) else "FAIL", "Dashboard panels declared", "core panels"),
                Check("P2H-ALERTS", "PASS" if has_all(txt, ["alert_gate_failure", "alert_readiness_regression", "alert_freshness_sla_breach"]) else "FAIL", "Alert rules declared", "alert rules"),
                Check("P2H-ROUTING", "PASS" if has_all(txt, ["warning", "critical", "on-call"]) else "FAIL", "Alert routing declared", "warning/critical"),
            ]
        )

    failed = [c for c in checks if c.status != "PASS"]
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_count": len(checks),
        "failed_count": len(failed),
        "checks": [asdict(c) for c in checks],
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Phase 2 Content Health Dashboard Report",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- checks: `{payload['check_count']}`",
        f"- failed: `{payload['failed_count']}`",
        "",
        "| ID | Status | Description | Details |",
        "|---|---|---|---|",
    ] + [f"| {c.id} | {c.status} | {c.description} | {c.details} |" for c in checks]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if failed:
        print("❌ phase2_content_health_dashboard_smoke failed")
        for c in failed:
            print(f"- {c.id}: {c.description} ({c.details})")
        return 1
    print("✅ phase2_content_health_dashboard_smoke passed")
    print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
    print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
