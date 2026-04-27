#!/usr/bin/env python3
"""
W7-4 / G20: IPA size gate.
Finds latest .ipa (preferred) or .app bundle in DerivedData, validates size threshold,
and writes reports under docs/.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
REPORT_JSON = DOCS / "IPA_SIZE_GATE_REPORT_G20.json"
REPORT_MD = DOCS / "IPA_SIZE_GATE_REPORT_G20.md"


@dataclass
class TopEntry:
    path: str
    size_bytes: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate IPA/APP size against a budget.")
    parser.add_argument("--max-mb", type=float, default=500.0, help="Maximum allowed size in MB.")
    parser.add_argument(
        "--search-root",
        default=str(Path.home() / "Library/Developer/Xcode/DerivedData"),
        help="Root directory where build artifacts are searched.",
    )
    parser.add_argument("--top-n", type=int, default=20, help="Top N largest assets for report.")
    return parser.parse_args()


def latest_matching(root: Path, suffix: str) -> Path | None:
    candidates = [p for p in root.rglob(f"*{suffix}") if p.is_file() or p.is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def bytes_to_mb(size_bytes: int) -> float:
    return size_bytes / (1024 * 1024)


def top_entries_from_ipa(ipa_path: Path, top_n: int) -> list[TopEntry]:
    entries: list[TopEntry] = []
    with ZipFile(ipa_path, "r") as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            entries.append(TopEntry(path=info.filename, size_bytes=info.file_size))
    entries.sort(key=lambda x: x.size_bytes, reverse=True)
    return entries[:top_n]


def top_entries_from_app(app_path: Path, top_n: int) -> list[TopEntry]:
    entries: list[TopEntry] = []
    for path in app_path.rglob("*"):
        if not path.is_file():
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        rel = path.relative_to(app_path)
        entries.append(TopEntry(path=str(rel), size_bytes=size))
    entries.sort(key=lambda x: x.size_bytes, reverse=True)
    return entries[:top_n]


def write_report(
    artifact_type: str,
    artifact_path: Path,
    size_bytes: int,
    max_mb: float,
    top_entries: list[TopEntry],
) -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    size_mb = bytes_to_mb(size_bytes)
    payload = {
        "generated_at": generated_at,
        "artifact_type": artifact_type,
        "artifact_path": str(artifact_path),
        "size_bytes": size_bytes,
        "size_mb": round(size_mb, 2),
        "max_mb": max_mb,
        "pass": size_mb <= max_mb,
        "top_entries": [asdict(x) for x in top_entries],
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# IPA Size Gate Report (G20)",
        "",
        f"- generated_at: `{generated_at}`",
        f"- artifact_type: `{artifact_type}`",
        f"- artifact_path: `{artifact_path}`",
        f"- size_mb: `{size_mb:.2f}`",
        f"- max_mb: `{max_mb:.2f}`",
        f"- status: `{'PASS' if size_mb <= max_mb else 'FAIL'}`",
        "",
        "## Top Assets",
        "",
        "| # | Path | Size MB |",
        "|---|---|---:|",
    ]
    for idx, entry in enumerate(top_entries, start=1):
        lines.append(f"| {idx} | {entry.path} | {bytes_to_mb(entry.size_bytes):.2f} |")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = Path(args.search_root).expanduser()
    if not root.exists():
        print("❌ ipa_size_gate failed")
        print(f"- search root not found: {root}")
        return 1

    ipa = latest_matching(root, ".ipa")
    app = latest_matching(root, ".app")

    artifact_path: Path
    artifact_type: str
    size_bytes: int
    top_entries: list[TopEntry]

    if ipa is not None:
        artifact_path = ipa
        artifact_type = "ipa"
        size_bytes = ipa.stat().st_size
        top_entries = top_entries_from_ipa(ipa, args.top_n)
    elif app is not None:
        artifact_path = app
        artifact_type = "app_bundle"
        size_bytes = sum(p.stat().st_size for p in app.rglob("*") if p.is_file())
        top_entries = top_entries_from_app(app, args.top_n)
    else:
        print("❌ ipa_size_gate failed")
        print(f"- no .ipa or .app artifacts found under: {root}")
        return 1

    write_report(artifact_type, artifact_path, size_bytes, args.max_mb, top_entries)

    size_mb = bytes_to_mb(size_bytes)
    if size_mb > args.max_mb:
        print("❌ ipa_size_gate failed")
        print(f"- artifact: {artifact_path}")
        print(f"- size_mb: {size_mb:.2f} > max_mb: {args.max_mb:.2f}")
        return 1

    print("✅ ipa_size_gate passed")
    print(f"- artifact_type: {artifact_type}")
    print(f"- artifact: {artifact_path}")
    print(f"- size_mb: {size_mb:.2f}")
    print(f"- report_json: {REPORT_JSON.relative_to(ROOT)}")
    print(f"- report_md: {REPORT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
