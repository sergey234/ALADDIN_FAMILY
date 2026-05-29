#!/usr/bin/env python3
"""
Generate folder-level LOC CSV for ALADDIN mobile codebase map.
Usage:
  python3 scripts/mobile_codebase_loc_report.py --root /path/to/ALADDIN_iOS --out docs/data/mobile_loc_local.csv
  python3 scripts/mobile_codebase_loc_report.py --root /opt/aladdin-backend --out /tmp/mobile_loc_vps.csv
"""
from __future__ import annotations

import argparse
import csv
import os
from collections import defaultdict
from pathlib import Path

SKIP_DIR_NAMES = {
    "venv",
    ".git",
    "__pycache__",
    "node_modules",
    "DerivedData",
    "build",
    ".build",
    "Pods",
    "Carthage",
    ".swiftpm",
    "xcuserdata",
    "dist",
    "egg-info",
    ".pytest_cache",
}

JUNK_DIR_MARKERS = (
    "backup",
    "archive",
    "clean_export",
    "gateway_archive",
    "_backup",
    "tmp_push",
    "aladdin_ios_clean",
    "aladdin_ios_final",
    "ml_system_package",
    "new_backup_aladdin",
    "wireframe_analysis",
)

CODE_EXTS = {
    ".py": "Python",
    ".swift": "Swift",
    ".m": "Objective-C",
    ".mm": "Objective-C",
    ".h": "Header",
    ".sh": "Shell",
    ".sql": "SQL",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".kt": "Kotlin",
    ".java": "Java",
}


def is_junk_dir(path: Path) -> bool:
    if path.name in SKIP_DIR_NAMES:
        return True
    name = path.name.lower()
    full = str(path).lower()
    return any(m in name or m in full for m in JUNK_DIR_MARKERS)


def count_lines(fp: Path) -> int:
    with open(fp, "rb") as f:
        data = f.read()
    if not data or b"\x00" in data[:4096]:
        return 0
    return data.count(b"\n") + (0 if data.endswith(b"\n") else 1)


def scan_root(root: Path) -> tuple[list[dict], dict[str, int]]:
    root = root.resolve()
    rows: list[dict] = []
    totals = defaultdict(int)

    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        if is_junk_dir(current):
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if not is_junk_dir(current / d)]

        rel_dir = "." if current == root else str(current.relative_to(root))
        by_ext: dict[str, dict[str, int]] = defaultdict(lambda: {"files": 0, "lines": 0})

        for fn in filenames:
            if fn.endswith((".bak", ".backup", ".orig", ".tmp")):
                continue
            fp = current / fn
            ext = fp.suffix.lower()
            if ext not in CODE_EXTS:
                continue
            try:
                lines = count_lines(fp)
            except OSError:
                continue
            if lines == 0:
                continue
            lang = CODE_EXTS[ext]
            by_ext[lang]["files"] += 1
            by_ext[lang]["lines"] += lines

        if not by_ext:
            continue

        total_files = sum(v["files"] for v in by_ext.values())
        total_lines = sum(v["lines"] for v in by_ext.values())
        py = by_ext.get("Python", {"files": 0, "lines": 0})
        sw = by_ext.get("Swift", {"files": 0, "lines": 0})
        rows.append(
            {
                "path": rel_dir,
                "files_total": total_files,
                "lines_total": total_lines,
                "python_files": py["files"],
                "python_lines": py["lines"],
                "swift_files": sw["files"],
                "swift_lines": sw["lines"],
                "shell_files": by_ext.get("Shell", {"files": 0})["files"],
                "shell_lines": by_ext.get("Shell", {"files": 0, "lines": 0})["lines"],
                "other_files": total_files - py["files"] - sw["files"] - by_ext.get("Shell", {"files": 0})["files"],
                "other_lines": total_lines - py["lines"] - sw["lines"] - by_ext.get("Shell", {"files": 0, "lines": 0})["lines"],
            }
        )
        totals["files"] += total_files
        totals["lines"] += total_lines
        totals["python_lines"] += py["lines"]
        totals["swift_lines"] += sw["lines"]

    rows.sort(key=lambda r: (-r["lines_total"], r["path"]))
    return rows, totals


def write_csv(rows: list[dict], out: Path, root: Path, totals: dict[str, int]) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "path",
                "files_total",
                "lines_total",
                "python_files",
                "python_lines",
                "swift_files",
                "swift_lines",
                "shell_files",
                "shell_lines",
                "other_files",
                "other_lines",
            ],
        )
        w.writeheader()
        w.writerows(rows)
        w.writerow(
            {
                "path": "__TOTAL__",
                "files_total": totals["files"],
                "lines_total": totals["lines"],
                "python_files": "",
                "python_lines": totals["python_lines"],
                "swift_files": "",
                "swift_lines": totals["swift_lines"],
                "shell_files": "",
                "shell_lines": "",
                "other_files": "",
                "other_lines": "",
            }
        )
    print(f"Wrote {out} ({len(rows)} dirs, {totals['lines']:,} code lines) root={root}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="Scan root directory")
    parser.add_argument("--out", required=True, help="Output CSV path")
    args = parser.parse_args()
    root = Path(args.root)
    out = Path(args.out)
    if not root.exists():
        raise SystemExit(f"Root not found: {root}")
    rows, totals = scan_root(root)
    write_csv(rows, out, root, totals)


if __name__ == "__main__":
    main()
