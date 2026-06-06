# MNEMO B14-T15 — EN Native Review Checklist

**Scope:** ~400 `child_mnemo_*` + `parent_mnemo_*` EN strings in `LocalizationManager.swift`  
**Gate:** `python3 scripts/child_localization_gate.py --mnemo-full` — **389 keys PASS**  
**Project sync:** `docs/MNEMO_PROJECT_SYNC.md` (111/119)  
**Run tests/build:** Phase C only (end of project)

---

## Reviewer instructions

1. Read EN copy in context (child lesson flow, parent dashboard, lock banners).
2. Mark each section ✅ when tone is natural for ages 4–18 and parent audience.
3. Flag strings that sound machine-translated, too formal, or culturally off.
4. Do **not** change keys — only propose copy edits in a PR or appendix.

---

## Sections

| # | Prefix / area | Keys (approx) | Reviewer | Status |
|---|---------------|---------------|----------|--------|
| 1 | `child_mnemo_brand_*` | 16 | | ☐ |
| 2 | `child_mnemo_label_*` / `subtitle_*` / `catalog_greeting_*` | 24 | | ☐ |
| 3 | `child_mnemo_phase_*` / `warmup_*` / `reflect_*` | 18 | | ☐ |
| 4 | `child_mnemo_technique_*` + picker | 40 | | ☐ |
| 5 | `child_mnemo_semester_*` + lock | 32 | | ☐ |
| 6 | `child_mnemo_journey_stop_*` (01–40) | 40 | | ☐ |
| 7 | `child_mnemo_reward_*` / skill / hero | 12 | | ☐ |
| 8 | `child_mnemo_pictogram_*` | 11 | | ☐ |
| 9 | `child_mnemo_baseline_*` / MQ | 21 | | ☐ |
| 10 | `child_mnemo_capstone_*` / `championship_*` | 24 | | ☐ |
| 11 | `child_mnemo_table_*` | 14 | | ☐ |
| 12 | `child_mnemo_srs_*` / push | 6 | | ☐ |
| 13 | `child_mnemo_exam_*` / `family_*` / `companion_*` / `stories_recall_*` / `number_pegs_*` (optional B14) | 35 | | ☐ |
| 14 | `parent_mnemo_guide_*` | 30 | | ☐ |
| 15 | `parent_mnemo_brand_*` + dashboard mnemo widgets | 12 | | ☐ |
| 16 | `onboarding_mnemo_*` | 2 | | ☐ |

---

## Tone criteria (pass/fail)

- **Child (4–12):** warm, encouraging, no jargon; short sentences.
- **Teen (13–17):** respectful, not patronizing; exam framing optional (flag).
- **Parent:** clear benefit, no PII prompts, actionable tips.
- **Consistency:** «Memory Academy» brand, «image/anchor/recall» terminology aligned across study + games.

---

## Sign-off

| Role | Name | Date | Notes |
|------|------|------|-------|
| Native EN reviewer | | | |
| Product owner | | | |

When all sections are ✅, mark **MNEMO-B14-T15** complete in §Q.
