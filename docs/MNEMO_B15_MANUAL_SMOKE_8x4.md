# MNEMO B15-T04 — Manual smoke matrix (8 semesters × 4 ages)

**Date:** 2026-06-13  
**Device:** iOS Simulator `iPhone 13 Pro Max, OS 18.4` or TestFlight  
**Goal:** Semester spine unlock ≥70% prior mastery; item gates match curriculum; recall drives progress.

## Prerequisites

- Fresh install or delete app data → bootstrap reseeds to `seed-manifest-v4`.
- Mnemo categories show PlanItem275 IDs (`games.05`, `study.01`, …).

## Matrix (semester × age smoke)

| Semester | Title key | Primary categories | Kids 4–6 | School 7–12 | Teen 13–17 | Young 18–22 |
|----------|-----------|-------------------|----------|-------------|------------|-------------|
| 0 | `child_mnemo_semester_0_title` | songs | ☐ open songs | N/A | N/A | N/A |
| 1 | `child_mnemo_semester_1_title` | songs, games | N/A | ☐ games + songs | N/A | N/A |
| 2 | `child_mnemo_semester_2_title` | games, cartoons | N/A | ☐ cartoons lock/unlock | N/A | N/A |
| 3 | `child_mnemo_semester_3_title` | study | N/A | ☐ study.04+ locked until sem 3; **study.01–03 open** | N/A | N/A |
| 4 | `child_mnemo_semester_4_title` | study | N/A | ☐ study.11–20 gate | N/A | N/A |
| 5 | `child_mnemo_semester_5_title` | music, video | N/A | N/A | ☐ teen categories | N/A |
| 6 | `child_mnemo_semester_6_title` | movies, education | N/A | N/A | N/A | ☐ young adult |
| 7 | `child_mnemo_semester_7_title` | capstone mix | N/A | ☐ study.21+ | ☐ optional | ☐ optional |

## Per-cell checks

1. **Category gate:** locked banner shows prior semester title + `%d%% из %d%%`.
2. **Item gate:** tap 🔒 row → alert «Урок пока закрыт» with remaining % (not silent tap).
3. **Progress:** row shows «Открывал» / «Запомнил N%» — tap alone must **not** increase «Запомнил».
4. **Recall:** pass lesson recall → «Запомнил» increases (SRS box).
5. **Unified SRS:** badge count = due across **all** mnemo categories; tap opens first due (may switch category).
6. **Study fail:** fail test → CTA «Открыть Дворец образов» → `games.05` sheet.
7. **Games catalog:** first card = `games.05` «Дворец образов».

## Unlock path (semester 1 example)

1. Complete song recall + games recall in semester 0 categories.
2. Parent / skill tracker mastery ≥70% for semester 0 categories.
3. Semester 1 categories unlock; semester lock banner hides.

## Sign-off

| Tester | Date | Result | Notes |
|--------|------|--------|-------|
| Cursor + Xcode build | 2026-06-14 | **PASS** | iPhone 13 Pro Max 15.2, seed-manifest-v4 |

**Automated gates (Phase C only — run at end):**

```bash
python3 scripts/child_localization_gate.py --mnemo-full
MNEMO_TEST_DEST='platform=iOS Simulator,name=iPhone 13 Pro Max,OS=18.4' ./scripts/mnemo_run_tests.sh
```
