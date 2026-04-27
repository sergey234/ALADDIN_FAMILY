#!/usr/bin/env python3
"""
W7-5 / G21-G23: build evidence pack archive and validate required artifacts.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
REPORT_JSON = DOCS / "EVIDENCE_PACK_G21_G23_REPORT.json"
REPORT_MD = DOCS / "EVIDENCE_PACK_G21_G23_REPORT.md"
PACK_ZIP = DOCS / "EVIDENCE_PACK_G21_G23.zip"


@dataclass
class Entry:
    path: str
    exists: bool


REQUIRED_FILES = [
    "docs/PHASE8_SECURITY_VALIDATION.md",
    "docs/TRACKB_PRIVACY_COMPLIANCE_GATE.md",
    "docs/W_LOC_6_A11Y_SYNC_CONTENT_REPORT.md",
    "docs/THREAT_MODEL_DELTA_G21_G23.md",
    "docs/DATA_MAP_G21_G23.md",
    "docs/DSAR_SCREENSHOTS_LOG_G21_G23.md",
]


def build_entries() -> list[Entry]:
    entries: list[Entry] = []
    for rel in REQUIRED_FILES:
        p = ROOT / rel
        entries.append(Entry(path=rel, exists=p.exists()))
    return entries


def write_reports(entries: list[Entry]) -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    payload = {
        "generated_at": generated_at,
        "required_count": len(entries),
        "missing_count": sum(1 for x in entries if not x.exists),
        "entries": [asdict(x) for x in entries],
        "zip_path": str(PACK_ZIP.relative_to(ROOT)),
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Evidence Pack Report (G21-G23)",
        "",
        f"- generated_at: `{generated_at}`",
        f"- required_count: `{payload['required_count']}`",
        f"- missing_count: `{payload['missing_count']}`",
        f"- archive: `{PACK_ZIP.relative_to(ROOT)}`",
        "",
        "| Path | Exists |",
        "|---|---|",
    ]
    for x in entries:
        lines.append(f"| {x.path} | {'YES' if x.exists else 'NO'} |")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_zip(entries: list[Entry]) -> None:
    with ZipFile(PACK_ZIP, "w", compression=ZIP_DEFLATED) as zf:
        for x in entries:
            if not x.exists:
                continue
            p = ROOT / x.path
            zf.write(p, arcname=x.path)
        if REPORT_JSON.exists():
            zf.write(REPORT_JSON, arcname=str(REPORT_JSON.relative_to(ROOT)))
        if REPORT_MD.exists():
            zf.write(REPORT_MD, arcname=str(REPORT_MD.relative_to(ROOT)))


def main() -> int:
    entries = build_entries()
    write_reports(entries)
    missing = [x.path for x in entries if not x.exists]
    if missing:
        print("❌ phase7_evidence_pack_g21_g23 failed")
        print(f"- missing artifacts: {missing}")
        return 1

    write_zip(entries)
    print("✅ phase7_evidence_pack_g21_g23 passed")
    print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
    print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
    print(f"- evidence_zip: {PACK_ZIP.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
