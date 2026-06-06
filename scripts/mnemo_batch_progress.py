#!/usr/bin/env python3
"""Print Memory Academy batch progress from MNEMONICS_CHILD_IMPLEMENTATION_PLAN.md §Q."""

from __future__ import annotations

import re
from pathlib import Path

PLAN = Path(__file__).resolve().parent.parent / "docs/MNEMONICS_CHILD_IMPLEMENTATION_PLAN.md"

BATCH_ORDER = [
    "B0", "B1C", "B1", "B2", "B3", "B4A", "B4B", "B4C", "B4D",
    "B5", "B6", "B7", "B8", "B9", "B10", "B11", "B12", "B13", "B14", "B15",
]

V2_PREFIXES = ("B0", "B1C", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8")
V3_PREFIXES = ("B9", "B10", "B11", "B12", "B13", "B14", "B15")


def batch_id(task_id: str) -> str:
    m = re.match(r"MNEMO-(B\d+[A-Z]?)", task_id)
    return m.group(1) if m else "?"


def main() -> int:
    text = PLAN.read_text(encoding="utf-8")
    tasks = re.findall(r"- \[([ x])\] (MNEMO-[^\n]+)", text)
    done = sum(1 for s, _ in tasks if s == "x")
    total = len(tasks)
    print(f"Memory Academy: {done}/{total} ({100 * done // max(total, 1)}%)")
    print()
    for part, prefixes in [("v2 MVP", V2_PREFIXES), ("v3 Course", V3_PREFIXES)]:
        part_tasks = [(s, i) for s, i in tasks if batch_id(i).startswith(prefixes) or any(i.startswith(f"MNEMO-{p}") for p in prefixes if len(p) <= 3)]
        # simpler filter
        filtered = []
        for s, tid in tasks:
            bid = batch_id(tid)
            if part == "v2 MVP" and (bid in V2_PREFIXES or bid.startswith("B4")):
                filtered.append((s, tid))
            elif part == "v3 Course" and bid in V3_PREFIXES:
                filtered.append((s, tid))
        d = sum(1 for s, _ in filtered if s == "x")
        print(f"{part}: {d}/{len(filtered)} done")
    print()
    grouped: dict[str, list[tuple[str, str]]] = {}
    for s, tid in tasks:
        grouped.setdefault(batch_id(tid), []).append((s, tid))
    for bid in BATCH_ORDER:
        rows = grouped.get(bid, [])
        if not rows:
            continue
        d = sum(1 for s, _ in rows if s == "x")
        mark = "✅" if d == len(rows) else ("🔄" if d else "⏳")
        print(f"{mark} {bid}: {d}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
