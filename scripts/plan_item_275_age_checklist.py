#!/usr/bin/env python3
"""Generate docs/PLAN_ITEM_275_BY_AGE_READABLE.md from PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md.

Task-style lines (GFM-compatible):
  - [x]  — DONE
  - [ ] **PARTIAL:** … — PARTIAL
  - [ ]  — TODO

Canonical source of truth remains the matrix file.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md"
OUT_MD = ROOT / "docs" / "PLAN_ITEM_275_BY_AGE_READABLE.md"
ROW_RE = re.compile(r"^- (.+)$")


def parse_row_body(body: str) -> list[str] | None:
    parts = [p.strip() for p in body.split("|")]
    if len(parts) != 8:
        return None
    return parts


def task_line(parts: list[str]) -> str:
    plan, _cat, iid, st = parts[0], parts[1], parts[2], parts[3]
    ref = f"`{iid}`"
    if st == "DONE":
        return f"- [x] {plan} ({ref})"
    if st == "PARTIAL":
        return f"- [ ] **PARTIAL:** {plan} ({ref})"
    if st == "TODO":
        return f"- [ ] {plan} ({ref})"
    return f"- [ ] **{st}:** {plan} ({ref})"


def is_age_band_heading(title: str) -> bool:
    t = title.strip()
    if t.casefold() == "notes":
        return False
    # Sections: "1-6 лет", "7-12 лет", "13-17 лет", "18-22 лет"
    return "лет" in t and re.match(r"^\d+-\d+", t) is not None


def main() -> int:
    if not MATRIX.exists():
        print("FAIL: matrix missing", file=sys.stderr)
        return 1

    text = MATRIX.read_text(encoding="utf-8")
    lines_out: list[str] = []
    lines_out.append("# PLAN_ITEM 275 — чеклист по возрастам")
    lines_out.append("")
    lines_out.append(
        "**Источник правды:** `docs/PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md` "
        "(строки `PLAN_ITEM | category_id | item_id | status | …`)."
    )
    lines_out.append("")
    lines_out.append("Этот файл **генерируется** — не править вручную; изменения вносить в матрицу, затем:")
    lines_out.append("")
    lines_out.append("```bash")
    lines_out.append("python3 scripts/plan_item_275_age_checklist.py")
    lines_out.append("```")
    lines_out.append("")
    lines_out.append("## Легенда")
    lines_out.append("")
    lines_out.append("- `[x]` — статус **DONE** в матрице")
    lines_out.append("- `[ ]` **PARTIAL:** — статус **PARTIAL**")
    lines_out.append("- `[ ]` без метки — статус **TODO**")
    lines_out.append("- В скобках — `item_id` для трассировки в коде и аудите")
    lines_out.append("")

    row_count = 0
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("## ") and not line.startswith("###"):
            title = line[3:].strip()
            if title.casefold() == "notes":
                break
            if not is_age_band_heading(title):
                continue
            lines_out.append("")
            lines_out.append(f"## {title}")
            continue

        if line.startswith("### "):
            lines_out.append("")
            lines_out.append(f"### {line[4:].strip()}")
            continue

        m = ROW_RE.match(line)
        if not m:
            continue
        parts = parse_row_body(m.group(1))
        if parts is None:
            continue
        lines_out.append(task_line(parts))
        row_count += 1

    lines_out.append("")

    OUT_MD.write_text("\n".join(lines_out), encoding="utf-8")
    print(f"Wrote {OUT_MD.relative_to(ROOT)} ({row_count} rows)")
    if row_count != 275:
        print(f"WARN: expected 275 task rows, got {row_count}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
