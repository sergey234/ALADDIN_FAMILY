#!/usr/bin/env python3
"""Audit PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md: duplicates, coverage, per-row summary for ML."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md"
OUT_MD = ROOT / "docs" / "PLAN_ITEM_275_AUDIT_REPORT.md"
PBXPROJ = ROOT / "ALADDIN.xcodeproj/project.pbxproj"
ROW_RE = re.compile(r"^- (.+)$")

# PBXBuildFile entries: file name must appear in `… in Sources` for main app compilation.
XCODE_CHILD_CONTENT_SOURCES = (
    "08_ChildInterfaceScreen.swift in Sources",
    "ChildContentScreen.swift in Sources",
    "ChildContentExperienceScreen.swift in Sources",
    "ParentDashboardView.swift in Sources",
    "ContentSeedProvider.swift in Sources",
    "ContentManager.swift in Sources",
    "ContentExperienceResolver.swift in Sources",
)


def parse_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        m = ROW_RE.match(line.strip())
        if not m:
            continue
        body = m.group(1)
        if "|" not in body:
            continue
        parts = [p.strip() for p in body.split("|")]
        if len(parts) != 8:
            continue
        rows.append(parts)
    return rows


def implementation_hint(category_id: str, item_id: str, status: str) -> str:
    """Short hint where work lands; not a legal guarantee."""
    if status == "TODO":
        return "seed + experience branch + localization (to add)"
    base = "ChildContentExperienceScreen + ContentSeedProvider"
    if "teen_safety" in item_id:
        return f"{base}; same safety category as 7-12, distinct item prefix"
    return base


# Heuristic: primary Swift UI surface for `category_id` in ChildContentExperienceScreen (+ same file private views).
# Some categories still resolve to generic `contentCard` until a dedicated branch exists (see value suffix).
CATEGORY_LINKED_MODULE: dict[str, str] = {
    "child_interface_category_toys": "ChildContentExperienceScreen → Toys3DSceneHostView",
    "child_interface_category_games": "ChildContentExperienceScreen → GamesChallengeEngineView (fallback: UnicornUniverseView)",
    "child_interface_category_drawing": "ChildContentExperienceScreen → DrawingExperienceHostView",
    "child_interface_category_creativity": "ChildContentExperienceScreen → DrawingExperienceHostView",
    "child_interface_category_songs": "ChildContentExperienceScreen → KaraokeExperienceHostView",
    "child_interface_category_stories": "ChildContentExperienceScreen → StoryExperienceHostView",
    "child_interface_category_study": "ChildContentExperienceScreen → StudyLessonTestExperienceView",
    "child_interface_category_safety": "ChildContentExperienceScreen → SafetyScenarioEngineView (fallback: YoungDefenderView)",
    "child_interface_category_cartoons": "ChildContentExperienceScreen → CartoonsActiveWatchExperienceView",
    "child_interface_category_programming": "ChildContentExperienceScreen → ProgrammingTaskProgressionView",
    "child_interface_category_social": "ChildContentExperienceScreen → SocialLiteracyDrillsView",
    "child_interface_category_music": "ChildContentExperienceScreen → MusicDrillsProgressionView",
    "child_interface_category_education": "ChildContentExperienceScreen → EducationPathwaysMilestonesView (route .career + education)",
    "child_interface_category_career": "ChildContentExperienceScreen → contentCard / actionCard (no dedicated career view yet)",
    "child_interface_category_video": "ChildContentExperienceScreen → contentCard (video route; no non-cartoons branch yet)",
    "child_interface_category_movies": "ChildContentExperienceScreen → contentCard (video route; no movies-specific view yet)",
    "child_interface_category_internet": "ChildContentExperienceScreen → contentCard (lesson route default)",
}


def linked_module_heuristic(category_id: str, status: str) -> str:
    """Swift surface hint for ML; only filled for DONE/PARTIAL."""
    if status == "TODO":
        return "—"
    return CATEGORY_LINKED_MODULE.get(
        category_id,
        "ChildContentExperienceScreen → contentCard (unknown category_id)",
    )


def xcode_membership_lines() -> tuple[list[str], bool]:
    """Return markdown lines for section 0; ok=False if project file or entries missing."""
    if not PBXPROJ.exists():
        return (["- **project.pbxproj** not found** — cannot verify target membership.", ""], False)
    text = PBXPROJ.read_text(encoding="utf-8", errors="replace")
    missing = [s for s in XCODE_CHILD_CONTENT_SOURCES if s not in text]
    lines: list[str] = []
    lines.append(
        "Checked that each file name appears in a **`… in Sources`** build phase entry "
        f"in `{PBXPROJ.relative_to(ROOT)}` (heuristic: compiled into *some* target; "
        "normally the main ALADDIN app target)."
    )
    lines.append("")
    if missing:
        lines.append("- **MISSING from Sources list:**")
        for m in missing:
            lines.append(f"  - `{m}`")
        lines.append("")
        return (lines, False)
    lines.append("- **All listed child-content / Core Content files present in Sources:** OK")
    for s in XCODE_CHILD_CONTENT_SOURCES:
        lines.append(f"  - `{s}`")
    lines.append("")
    return (lines, True)


def main() -> int:
    if not MATRIX.exists():
        print("FAIL: matrix missing")
        return 1
    rows = parse_rows(MATRIX.read_text(encoding="utf-8"))
    if len(rows) != 275:
        print(f"WARN: expected 275 rows, got {len(rows)}")

    item_ids = [r[2] for r in rows]
    id_dupes = {k: v for k, v in Counter(item_ids).items() if v > 1}

    plan_cat = [(r[0], r[1]) for r in rows]
    pc_dupes = {k: v for k, v in Counter(plan_cat).items() if v > 1}

    plan_only = [r[0] for r in rows]
    # Same Russian title in different categories is OK; flag if same (plan, cat) duped above
    same_title_many_cats = {
        t: len({r[1] for r in rows if r[0] == t})
        for t in set(plan_only)
        if len({r[1] for r in rows if r[0] == t}) > 1
    }

    by_cat: dict[str, list[list[str]]] = defaultdict(list)
    for r in rows:
        by_cat[r[1]].append(r)

    lines: list[str] = []
    lines.append("# PLAN_ITEM 275 — audit report")
    lines.append("")
    lines.append("Generated by `scripts/plan_item_275_audit.py`.")
    lines.append("")
    lines.append("## 0) Xcode — child content surfaces in Sources")
    lines.append("")
    xcode_lines, xcode_ok = xcode_membership_lines()
    lines.extend(xcode_lines)
    lines.append("## 1) Summary")
    lines.append("")
    sc = Counter(r[3] for r in rows)
    lines.append(f"- Total rows parsed: **{len(rows)}**")
    lines.append(f"- DONE: **{sc['DONE']}** | PARTIAL: **{sc['PARTIAL']}** | TODO: **{sc['TODO']}**")
    lines.append(f"- Distinct `category_id`: **{len(by_cat)}**")
    lines.append("")

    lines.append("## 1a) Localization vs 275 items (child content)")
    lines.append("")
    lines.append(
        "- **Matrix `PLAN_ITEM` text** lives in `PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md` in Russian; "
        "it is **not** automatically wired to `Localizable.strings`. Treat it as product copy / backlog, not runtime keys."
    )
    lines.append(
        "- **Category hub** (`ChildContentScreen`, child shell): uses **`child_interface_*`** keys in "
        "`Resources/Localization/*/Localizable.strings` (category titles, chrome). Keep EN/RU in sync when adding categories."
    )
    lines.append(
        "- **Per-item titles in the hub today** often come from **`ContentSeedProvider`** metadata as **Russian string literals** "
        "in Swift (and `.navigationTitle(item.metadata.title)` in `ChildContentExperienceScreen`). "
        "That is **not** the same as 275 separate l10n keys: for full EN (or other locales) you either add keys per seed row, "
        "or move titles into manifest/i18n — see project localization standard docs."
    )
    lines.append(
        "- **DONE / PARTIAL experiences**: drill labels and flows inside `ChildContentExperienceScreen` (private views) "
        "already use **`LocalizationManager`** keys where implemented; gaps = missing keys for new copy in that branch."
    )
    lines.append(
        "- **TODO rows (275)**: when implemented, expect **new keys** for any user-visible strings introduced in that branch "
        "(same-PR policy if your gate requires it), plus seed/manifest strings if the item title/description is shown."
    )
    lines.append(
        "- **What was «not translated» before:** the matrix column itself; any **hardcoded RU** in seed stubs; "
        "and **stub English** in generic cards (e.g. `Offline ready`, `Open source` in `ChildContentExperienceScreen` if still literal)."
    )
    lines.append("")

    lines.append("## 2) Duplicate checks")
    lines.append("")
    if id_dupes:
        lines.append("### Duplicate `item_id` (must be empty)")
        for k, v in sorted(id_dupes.items()):
            lines.append(f"- `{k}` appears **{v}** times")
        lines.append("")
    else:
        lines.append("- **Duplicate `item_id`:** none (all unique).")
        lines.append("")

    if pc_dupes:
        lines.append("### Duplicate (`PLAN_ITEM`, `category_id`) (must be empty)")
        for (plan, cat), v in sorted(pc_dupes.items(), key=lambda x: -x[1]):
            lines.append(f"- {v}x: `{plan}` | `{cat}`")
        lines.append("")
    else:
        lines.append("- **Duplicate (`PLAN_ITEM`, `category_id`):** none.")
        lines.append("")

    lines.append("### Same title in multiple categories (informational, not an error)")
    lines.append("")
    lines.append(
        "These titles appear under more than one `category_id` (often intentional: "
        "e.g. safety vs internet vs social)."
    )
    lines.append("")
    for t in sorted(same_title_many_cats, key=lambda x: -same_title_many_cats[x])[:25]:
        cats = sorted({r[1] for r in rows if r[0] == t})
        lines.append(f"- **{t}** → {len(cats)} categories: {', '.join(cats)}")
    if len(same_title_many_cats) > 25:
        lines.append(f"- … and {len(same_title_many_cats) - 25} more titles with multi-category use")
    lines.append("")

    lines.append("## 3) Per `category_id` breakdown")
    lines.append("")
    lines.append("| category_id | total | DONE | PARTIAL | TODO |")
    lines.append("|---|---:|---:|---:|---:|")
    for cat in sorted(by_cat.keys()):
        rs = by_cat[cat]
        c = Counter(x[3] for x in rs)
        lines.append(
            f"| `{cat}` | {len(rs)} | {c['DONE']} | {c['PARTIAL']} | {c['TODO']} |"
        )
    lines.append("")

    lines.append("## 4) Per-row register (all 275)")
    lines.append("")
    lines.append(
        "Columns: `item_id` | status | **linked_module** (heuristic by `category_id`, only DONE/PARTIAL) | "
        "`PLAN_ITEM` | `category_id` → implementation hint."
    )
    lines.append("")
    for r in rows:
        plan, cat, iid, st = r[0], r[1], r[2], r[3]
        hint = implementation_hint(cat, iid, st)
        mod = linked_module_heuristic(cat, st)
        lines.append(f"- `{iid}` | **{st}** | {mod} | {plan} | `{cat}` → {hint}")
    lines.append("")

    lines.append("## 5) Recommendations (engineering)")
    lines.append("")
    lines.append(
        "1. **Do not put 275 experiences on one scroll:** keep `ChildContentScreen` as "
        "category hub + optional compact journey cards; each item opens "
        "`ChildContentExperienceScreen` (navigation stack)."
    )
    lines.append(
        "2. **Content scale:** grow `ContentSeedProvider` / server manifest; avoid loading "
        "all payloads at once — use existing `ContentManager` + pagination patterns."
    )
    lines.append(
        "3. **Heavy modules (SceneKit, PencilKit):** one active experience at a time; "
        "release resources on dismiss; profile with Instruments if adding many 3D scenes."
    )
    lines.append(
        "4. **Matrix maintenance:** when product adds a new theme, add a row here — "
        "the matrix is a living registry, not a frozen law."
    )
    lines.append("")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    if id_dupes or pc_dupes:
        print("FAIL: duplicates found")
        return 1
    if not xcode_ok:
        print("WARN: Xcode Sources heuristic failed (see report section 0)")
    print("PASS: no duplicate item_id or (plan, category) pairs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
