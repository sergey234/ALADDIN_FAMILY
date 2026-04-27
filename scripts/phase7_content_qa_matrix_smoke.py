#!/usr/bin/env python3
"""
W7-1 / G17: structural smoke for content QA matrix.
Generates JSON + markdown report under docs/.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
REPORT_JSON = DOCS / "PHASE7_CONTENT_QA_MATRIX_REPORT.json"
REPORT_MD = DOCS / "PHASE7_CONTENT_QA_MATRIX_REPORT.md"


@dataclass
class CheckResult:
    id: str
    description: str
    status: str
    details: str


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def has_all(content: str, tokens: List[str]) -> bool:
    return all(token in content for token in tokens)


def run_checks() -> List[CheckResult]:
    checks: List[CheckResult] = []

    child_content = ROOT / "Screens/ChildContentScreen.swift"
    offline = ROOT / "Core/Content/Sync/ContentSyncManager.swift"
    progress_systems = ROOT / "Core/Content/Progress/ProgressSystems.swift"
    ui_test = ROOT / "Tests/UITests/ChildContentProgressUITests.swift"
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
        "G17-FILE-1",
        "Child content screen exists",
        child_content.exists(),
        str(child_content.relative_to(ROOT)),
    )
    add(
        "G17-FILE-2",
        "Content sync manager exists",
        offline.exists(),
        str(offline.relative_to(ROOT)),
    )
    add(
        "G17-FILE-3",
        "Progress systems module exists",
        progress_systems.exists(),
        str(progress_systems.relative_to(ROOT)),
    )
    add(
        "G17-TEST-1",
        "UI progress test exists",
        ui_test.exists(),
        str(ui_test.relative_to(ROOT)),
    )

    if child_content.exists():
        content = read(child_content)
        add(
            "G17-STATE-OPEN",
            "Child content open/progress hooks present",
            has_all(content, ["progress", "ChildCategoryKey", "contentItem"]),
            "tokens: progress, ChildCategoryKey, contentItem",
        )
        add(
            "G17-STATE-EMPTY-ERROR",
            "Child content has empty/error/loading handling",
            has_all(content, ["empty", "error", "loading"]),
            "tokens: empty, error, loading",
        )

    if ru.exists() and en.exists():
        ru_text = read(ru)
        en_text = read(en)
        keys = [
            "child_content_loading",
            "child_content_error_message",
            "child_content_empty_title",
            "child_content_overall_progress",
        ]
        add(
            "G17-I18N-1",
            "RU/EN include baseline child content keys",
            all(k in ru_text and k in en_text for k in keys),
            "prefix/key fragments: " + ", ".join(keys),
        )

    return checks


def write_reports(checks: List[CheckResult]) -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    payload = {
        "generated_at": generated_at,
        "check_count": len(checks),
        "failed_count": sum(1 for c in checks if c.status != "PASS"),
        "checks": [asdict(c) for c in checks],
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Phase 7 Content QA Matrix Report",
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
        print("❌ phase7_content_qa_matrix_smoke failed")
        for c in failed:
            print(f"- {c.id}: {c.description} ({c.details})")
        return 1
    print("✅ phase7_content_qa_matrix_smoke passed")
    print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
    print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

