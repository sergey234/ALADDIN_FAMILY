#!/usr/bin/env python3
"""Auto-update dashboard progress stats from markdown checkboxes."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path


DASHBOARD = Path("docs/EXECUTION_AND_LOCALIZATION_DASHBOARD.md")
CHAT_SNAPSHOT = Path("docs/CURSOR_CHAT_PENDING_CHECKLIST.md")
SWIFT_VALUES_OUT = Path("Core/Planning/ImplementationPlanProgressValues.swift")
SWIFT_MIRROR_OUT = Path("Core/Planning/ImplementationPlanDashboardMirror.generated.swift")

FILE_BACKTICK_RE = re.compile(r"^- `([^`]+)`\s*$")

PHASE_RE = re.compile(r"^## 📅 ФАЗА (\d+):")
TRACK_RE = re.compile(r"^## TRACK ([AB]):")
CHECK_RE = re.compile(r"^- \[( |x|X)\] ")
SUMMARY_TOTAL_RE = re.compile(r"^- Всего задач в плане: \*\*\d+\*\*$")
SUMMARY_DONE_RE = re.compile(r"^- Выполнено: \*\*\d+\*\*$")
SUMMARY_INPROGRESS_RE = re.compile(r"^- В работе: \*\*\d+\*\*$")
SUMMARY_PENDING_RE = re.compile(r"^- Ожидают: \*\*\d+\*\*$")

TABLE_START = "<!-- PHASE_STATS:START -->"
TABLE_END = "<!-- PHASE_STATS:END -->"


def parse_counts(lines: list[str]) -> tuple[dict[str, tuple[int, int]], dict[str, tuple[int, int]], int, int]:
    phase = "General"
    track = "Track A"
    counts: dict[str, list[int]] = {}
    track_counts: dict[str, list[int]] = {"Track A": [0, 0], "Track B": [0, 0]}
    total = 0
    done = 0

    for line in lines:
        track_match = TRACK_RE.match(line)
        if track_match:
            track = f"Track {track_match.group(1)}"
            track_counts.setdefault(track, [0, 0])
            continue

        phase_match = PHASE_RE.match(line)
        if phase_match:
            phase = f"Phase {phase_match.group(1)}"
            counts.setdefault(phase, [0, 0])
            continue

        check_match = CHECK_RE.match(line)
        if not check_match:
            continue

        counts.setdefault(phase, [0, 0])
        counts[phase][0] += 1
        track_counts.setdefault(track, [0, 0])
        track_counts[track][0] += 1
        total += 1
        if check_match.group(1).lower() == "x":
            counts[phase][1] += 1
            track_counts[track][1] += 1
            done += 1

    out = {k: (v[0], v[1]) for k, v in counts.items() if v[0] > 0}
    tracks_out = {k: (v[0], v[1]) for k, v in track_counts.items() if v[0] > 0}
    return out, tracks_out, total, done


def build_tables(phase_counts: dict[str, tuple[int, int]], track_counts: dict[str, tuple[int, int]]) -> list[str]:
    lines = [
        TABLE_START,
        "### Прогресс по трекам (авто)",
        "",
        "| Трек | Выполнено | Всего | Прогресс |",
        "|---|---:|---:|---:|",
    ]
    for track in ["Track A", "Track B"]:
        if track not in track_counts:
            continue
        total, done = track_counts[track]
        progress = 0 if total == 0 else int((done / total) * 100)
        lines.append(f"| {track} | {done} | {total} | {progress}% |")

    lines.extend([
        "",
        "### Прогресс по фазам (авто)",
        "",
        "| Фаза | Выполнено | Всего | Прогресс |",
        "|---|---:|---:|---:|",
    ])
    for phase in sorted(phase_counts.keys(), key=lambda x: (x != "General", x)):
        total, done = phase_counts[phase]
        progress = 0 if total == 0 else int((done / total) * 100)
        lines.append(f"| {phase} | {done} | {total} | {progress}% |")
    lines.extend(["", TABLE_END])
    return lines


def replace_summary(lines: list[str], total: int, done: int) -> list[str]:
    pending = total - done
    in_progress = 0  # kept manual in dashboard scope; set to zero by default
    replaced: list[str] = []
    for line in lines:
        if SUMMARY_TOTAL_RE.match(line):
            replaced.append(f"- Всего задач в плане: **{total}**")
        elif SUMMARY_DONE_RE.match(line):
            replaced.append(f"- Выполнено: **{done}**")
        elif SUMMARY_INPROGRESS_RE.match(line):
            replaced.append(f"- В работе: **{in_progress}**")
        elif SUMMARY_PENDING_RE.match(line):
            replaced.append(f"- Ожидают: **{pending}**")
        else:
            replaced.append(line)
    return replaced


def upsert_phase_table(lines: list[str], table_lines: list[str]) -> list[str]:
    if TABLE_START in lines and TABLE_END in lines:
        start = lines.index(TABLE_START)
        end = lines.index(TABLE_END)
        return lines[:start] + table_lines + lines[end + 1 :]

    insert_idx = 0
    for i, line in enumerate(lines):
        if line.strip() == "---" and i > 30:
            insert_idx = i
            break
    if insert_idx == 0:
        insert_idx = len(lines)
    return lines[:insert_idx] + [""] + table_lines + [""] + lines[insert_idx:]


def _pct(done: int, total: int) -> int:
    if total == 0:
        return 0
    return int((done / total) * 100)


def write_swift_progress_values(
    phase_counts: dict[str, tuple[int, int]],
    track_counts: dict[str, tuple[int, int]],
    total: int,
    done: int,
) -> None:
    """Emit numeric progress for in-app UI (Settings). Keep in sync with dashboard tables."""
    pending = total - done
    in_progress = 0
    ta = track_counts.get("Track A", (0, 0))
    tb = track_counts.get("Track B", (0, 0))
    iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lines: list[str] = [
        "// AUTO-GENERATED by scripts/update_dashboard_stats.py — do not edit by hand.",
        "// Re-run: python3 scripts/update_dashboard_stats.py",
        f"// Source: {DASHBOARD.as_posix()} (checkbox parse)",
        f"// Generated at (UTC): {iso}",
        "",
        "import Foundation",
        "",
        "enum ImplementationPlanProgressValues {",
        f"    static let generatedAtUTC: String = \"{iso}\"",
        f"    static let totalTasks: Int = {total}",
        f"    static let doneTasks: Int = {done}",
        f"    static let pendingTasks: Int = {pending}",
        f"    static let inProgressTasks: Int = {in_progress}",
        "",
        f"    static let trackATotal: Int = {ta[0]}",
        f"    static let trackADone: Int = {ta[1]}",
        f"    static let trackAProgressPercent: Int = {_pct(ta[1], ta[0])}",
        "",
        f"    static let trackBTotal: Int = {tb[0]}",
        f"    static let trackBDone: Int = {tb[1]}",
        f"    static let trackBProgressPercent: Int = {_pct(tb[1], tb[0])}",
        "",
    ]
    for i in range(10):
        key = f"Phase {i}"
        pt, pd = phase_counts.get(key, (0, 0))
        lines.append(f"    static let phase{i}Total: Int = {pt}")
        lines.append(f"    static let phase{i}Done: Int = {pd}")
        lines.append(f"    static let phase{i}ProgressPercent: Int = {_pct(pd, pt)}")
        if pt > 0:
            lines.append(f"    static let phase{i}Pending: Int = {pt - pd}")
        else:
            lines.append(f"    static let phase{i}Pending: Int = 0")
        lines.append("")

    lines.append("}")
    lines.append("")

    SWIFT_VALUES_OUT.parent.mkdir(parents=True, exist_ok=True)
    SWIFT_VALUES_OUT.write_text("\n".join(lines), encoding="utf-8")


def _swift_string_literal(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("\"", "\\\"")
    return f"\"{escaped}\""


def parse_key_working_files(lines: list[str]) -> list[str]:
    """Paths from `## Основные рабочие файлы` until the first standalone `---`."""
    paths: list[str] = []
    in_block = False
    for raw in lines:
        s = raw.strip()
        if s == "## Основные рабочие файлы":
            in_block = True
            continue
        if not in_block:
            continue
        if s == "---":
            break
        m = FILE_BACKTICK_RE.match(raw.strip())
        if m:
            paths.append(m.group(1))
    return paths


def parse_checklist_done_and_pending(lines: list[str]) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Return (done, pending) (context, title) for every `- [ ]` / `- [x]` checklist line under TRACK/PHASE."""
    track = "Track A"
    phase_token = ""
    done_items: list[tuple[str, str]] = []
    pending_items: list[tuple[str, str]] = []
    for raw in lines:
        line = raw.rstrip("\n")

        track_match = TRACK_RE.match(line)
        if track_match:
            track = f"Track {track_match.group(1)}"
            phase_token = ""
            continue

        phase_match = PHASE_RE.match(line)
        if phase_match:
            phase_token = f"Phase {phase_match.group(1)}"
            continue

        check_match = CHECK_RE.match(line)
        if not check_match:
            continue

        title = line[check_match.end() :].strip()
        if not title:
            continue
        parts = [track]
        if phase_token:
            parts.append(phase_token)
        context = " · ".join(parts)
        if check_match.group(1).lower() == "x":
            done_items.append((context, title))
        else:
            pending_items.append((context, title))
    return done_items, pending_items


def write_swift_dashboard_mirror(
    key_paths: list[str],
    done_items: list[tuple[str, str]],
    pending_items: list[tuple[str, str]],
    iso: str,
) -> None:
    """Emit key file paths + full done/pending checklist for in-app mirror of the dashboard."""
    out: list[str] = [
        "// AUTO-GENERATED by scripts/update_dashboard_stats.py — do not edit by hand.",
        "// Re-run: python3 scripts/update_dashboard_stats.py",
        f"// Source: {DASHBOARD.as_posix()} (key files + checklist)",
        f"// Generated at (UTC): {iso}",
        "",
        "import Foundation",
        "",
        "struct ImplementationPlanDashboardChecklistLine: Identifiable, Hashable {",
        "    let id: String",
        "    let context: String",
        "    let title: String",
        "}",
        "",
        "enum ImplementationPlanDashboardMirror {",
        f"    static let generatedAtUTC: String = {_swift_string_literal(iso)}",
        "    static let keyWorkingFilePaths: [String] = [",
    ]
    for p in key_paths:
        out.append("        " + _swift_string_literal(p) + ",")
    out.extend(
        [
            "    ]",
            "",
            "    static let completedItems: [ImplementationPlanDashboardChecklistLine] = [",
        ]
    )
    for i, (ctx, title) in enumerate(done_items):
        out.append(
            "        .init(id: "
            + _swift_string_literal(f"d{i}")
            + ", context: "
            + _swift_string_literal(ctx)
            + ", title: "
            + _swift_string_literal(title)
            + "),"
        )
    out.extend(
        [
            "    ]",
            "",
            "    static let pendingItems: [ImplementationPlanDashboardChecklistLine] = [",
        ]
    )
    for i, (ctx, title) in enumerate(pending_items):
        out.append(
            "        .init(id: "
            + _swift_string_literal(f"p{i}")
            + ", context: "
            + _swift_string_literal(ctx)
            + ", title: "
            + _swift_string_literal(title)
            + "),"
        )
    out.extend(
        [
            "    ]",
            "}",
            "",
        ]
    )
    SWIFT_MIRROR_OUT.parent.mkdir(parents=True, exist_ok=True)
    SWIFT_MIRROR_OUT.write_text("\n".join(out), encoding="utf-8")


def write_chat_pending_snapshot(
    pending: list[tuple[str, str]],
    iso: str,
    total: int,
    done: int,
) -> None:
    """Numbered open tasks for keeping next to Cursor chat while executing the plan."""
    n_open = len(pending)
    lines: list[str] = [
        "# Open tasks snapshot (next to Cursor chat)",
        "",
        f"_Generated at {iso} (UTC). Canonical checklist: `{DASHBOARD.as_posix()}`. "
        "Refresh: `python3 scripts/update_dashboard_stats.py`._",
        "",
        f"**Progress:** {done} done / {total} total — **{n_open} open tasks** below.",
        "",
        "Keep this file open beside the agent chat while executing the plan.",
        "",
        "## All open tasks (numbered)",
        "",
    ]
    for i, (ctx, title) in enumerate(pending, start=1):
        lines.append(f"{i}. **{ctx}** — {title}")
    lines.append("")
    CHAT_SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    CHAT_SNAPSHOT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not DASHBOARD.exists():
        raise FileNotFoundError(f"Dashboard not found: {DASHBOARD}")

    raw_lines = DASHBOARD.read_text(encoding="utf-8").splitlines()
    phase_counts, track_counts, total, done = parse_counts(raw_lines)
    lines = replace_summary(raw_lines, total, done)
    table_lines = build_tables(phase_counts, track_counts)
    lines = upsert_phase_table(lines, table_lines)
    DASHBOARD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_swift_progress_values(phase_counts, track_counts, total, done)
    iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    key_paths = parse_key_working_files(lines)
    done_lines, pending_lines = parse_checklist_done_and_pending(lines)
    write_swift_dashboard_mirror(key_paths, done_lines, pending_lines, iso)
    write_chat_pending_snapshot(pending_lines, iso, total, done)
    print(f"Updated dashboard: total={total}, done={done}, pending={total-done}")
    print(f"Wrote {SWIFT_VALUES_OUT.as_posix()}")
    print(
        f"Wrote {SWIFT_MIRROR_OUT.as_posix()} "
        f"({len(key_paths)} key paths, {len(done_lines)} done, {len(pending_lines)} pending checklist lines)"
    )
    print(f"Wrote {CHAT_SNAPSHOT.as_posix()} ({len(pending_lines)} numbered open tasks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

