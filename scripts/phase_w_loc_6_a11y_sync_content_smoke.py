#!/usr/bin/env python3
"""
W-LOC-6 / G24: smoke checks for localized loading/error/empty + accessibility labels.
Writes JSON + markdown report under docs/.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
REPORT_JSON = DOCS / "W_LOC_6_A11Y_SYNC_CONTENT_REPORT.json"
REPORT_MD = DOCS / "W_LOC_6_A11Y_SYNC_CONTENT_REPORT.md"


@dataclass
class CheckResult:
    id: str
    description: str
    status: str
    details: str


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def has_all(content: str, tokens: list[str]) -> bool:
    return all(token in content for token in tokens)


def run_checks() -> list[CheckResult]:
    checks: list[CheckResult] = []

    child_content = ROOT / "Screens/ChildContentScreen.swift"
    parent_dashboard = ROOT / "Screens/ParentDashboardView.swift"
    ru = ROOT / "Resources/Localization/ru.lproj/Localizable.strings"
    en = ROOT / "Resources/Localization/en.lproj/Localizable.strings"

    def add(id_: str, desc: str, ok: bool, details: str) -> None:
        checks.append(
            CheckResult(
                id=id_,
                description=desc,
                status="PASS" if ok else "FAIL",
                details=details,
            )
        )

    add(
        "WLOC6-FILE-1",
        "Child content screen exists",
        child_content.exists(),
        str(child_content.relative_to(ROOT)),
    )
    add(
        "WLOC6-FILE-2",
        "Parent dashboard screen exists",
        parent_dashboard.exists(),
        str(parent_dashboard.relative_to(ROOT)),
    )

    if child_content.exists():
        content = read(child_content)
        add(
            "WLOC6-CONTENT-STATE-1",
            "Child content uses localized loading/error/empty states",
            has_all(
                content,
                [
                    'localized("child_content_loading")',
                    'localized("child_content_error_message")',
                    'localized("child_content_empty_title")',
                ],
            ),
            "child_content_loading/error_message/empty_title",
        )
        add(
            "WLOC6-CONTENT-A11Y-1",
            "Child content retry buttons use localized accessibility hints",
            has_all(
                content,
                [
                    'localized("child_content_retry_accessibility_hint")',
                    '.accessibilityIdentifier("child_content_error_retry")',
                    '.accessibilityIdentifier("child_content_empty_retry")',
                ],
            ),
            "child_content retry accessibility",
        )

    if parent_dashboard.exists():
        content = read(parent_dashboard)
        add(
            "WLOC6-DASHBOARD-A11Y-1",
            "Parent dashboard primary actions include localized accessibility hints",
            has_all(
                content,
                [
                    'localized("parent_dashboard_open_unified_limits_hint")',
                    'localized("parent_dashboard_report_export_csv_hint")',
                    'localized("parent_dashboard_report_export_pdf_hint")',
                ],
            ),
            "unified limits + export buttons hints",
        )
        add(
            "WLOC6-DASHBOARD-STATE-1",
            "Parent dashboard localized empty/error/reporting states exist",
            has_all(
                content,
                [
                    "parent_dashboard_trends_empty",
                    "parent_dashboard_report_export_failed",
                    "activity_digest_title",
                ],
            ),
            "trends_empty + report_export_failed + digest",
        )

    if ru.exists() and en.exists():
        ru_text = read(ru)
        en_text = read(en)
        keys = [
            "child_content_retry_accessibility_hint",
            "parent_dashboard_open_unified_limits_hint",
            "parent_dashboard_report_export_csv_hint",
            "parent_dashboard_report_export_pdf_hint",
            "child_content_loading",
            "child_content_error_message",
            "child_content_empty_title",
            "parent_dashboard_trends_empty",
            "parent_dashboard_report_export_failed",
        ]
        add(
            "WLOC6-I18N-KEYS-1",
            "RU/EN contain required W-LOC-6 keys",
            all(f'"{k}"' in ru_text and f'"{k}"' in en_text for k in keys),
            ", ".join(keys),
        )

    return checks


def write_reports(checks: list[CheckResult]) -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    payload = {
        "generated_at": generated_at,
        "check_count": len(checks),
        "failed_count": sum(1 for c in checks if c.status != "PASS"),
        "checks": [asdict(c) for c in checks],
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# W-LOC-6 A11y/State Smoke Report",
        "",
        f"- generated_at: `{generated_at}`",
        f"- checks: `{payload['check_count']}`",
        f"- failed: `{payload['failed_count']}`",
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
        print("❌ phase_w_loc_6_a11y_sync_content_smoke failed")
        for c in failed:
            print(f"- {c.id}: {c.description} ({c.details})")
        return 1
    print("✅ phase_w_loc_6_a11y_sync_content_smoke passed")
    print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
    print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
