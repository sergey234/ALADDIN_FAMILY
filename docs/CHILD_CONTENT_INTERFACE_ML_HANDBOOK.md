# Child content and child interface — ML handbook (full picture)

**Purpose:** one narrative for a future ML system: how work was organized, what was built, where it lives, how to verify it, and how the **275-item catalog matrix** relates to code.

**Canonical catalog matrix (275 rows):** `docs/PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md`  
**Open rows only (PARTIAL + TODO):** `docs/PLAN_ITEM_OPEN_TASKS.md`  
**Matrix structure smoke:** `scripts/plan_item_traceability_smoke.py`  
**Full 275-row audit (per item, duplicates, per-category counts):** `docs/PLAN_ITEM_275_AUDIT_REPORT.md` (regenerate: `python3 scripts/plan_item_275_audit.py`)  
**Readable age-band checklist (GFM task list from matrix statuses):** `docs/PLAN_ITEM_275_BY_AGE_READABLE.md` (`python3 scripts/plan_item_275_age_checklist.py`)  
**Prod API check + roadmap for 100% alignment (manifest/delta, not Telegram bot):** `docs/CHILD_CONTENT_PROD_CHECK_AND_ROADMAP.md`

---

## 1) How the three “plan sizes” fit together

| Track | What it is | Primary documents | Relation to child UI |
| --- | --- | --- | --- |
| **178** | Client-wide execution and localization dashboard (total tasks in that plan) | `docs/EXECUTION_AND_LOCALIZATION_DASHBOARD.md`, `docs/PLAN_174_ML_HANDOFF_FRONTEND.md` | Sets **global** rules: localization, CI, screens list, handoff narrative. Child screens are listed there as product surfaces. |
| **38** | Not a separate numbered file in-repo; if your “38” referred to a sprint slice or chat batch, map it to **`docs/PHASE2_LIVE_TODO_TRACKER.md`** sprint sections or **`docs/CURSOR_CHAT_PENDING_CHECKLIST.md`**. | Use Phase 2 trackers below | Phase 2 **implementation** tasks are grouped as P2-001…P2-604 (43) + category readiness (12) + exit/strategy (13) = **68** in the chat checklist. |
| **68** | Phase 2 child-content closure checklist (child depth + gates + parent outcome + strategy) | `docs/CURSOR_CHAT_PENDING_CHECKLIST.md`, `docs/PHASE2_LIVE_TODO_TRACKER.md`, `docs/TASK_56_DONE.md` … `docs/TASK_68_DONE.md` | Delivers **engines**, **journeys**, **gates**, **parent mirror**, **telemetry docs**. |
| **275** | Item-level **product catalog** you specified (by age and category), traced to `category_id` / `item_id` | `docs/PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md` | This is **volume and theme** roadmap; many rows are still `TODO` / `PARTIAL` while **modules** exist. |

**Short truth:** 68 closes **Phase 2 engineering and governance** for the child stack; 275 tracks **per-item content completeness** against your full wish list.

---

## 2) Read order for the next ML system (30 minutes → deep dive)

1. **This file** (`docs/CHILD_CONTENT_INTERFACE_ML_HANDBOOK.md`) — orientation.
2. **Plan vs fact (child):** `docs/CHILD_CONTENT_INTERFACE_PLAN_FACT.md`
3. **Phase 2 product plan:** `docs/PHASE2_CHILD_CONTENT_100_PERCENT_PLAN.md`
4. **Transfer package (canonical index):** `docs/ML_SYSTEM_TRANSFER_PACKAGE_PHASE2.md`
5. **Gap closure context:** `docs/GAP_CLOSURE_PLAN_PHASES_1_8_ML_HANDOFF.md`
6. **275 matrix:** `docs/PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md` + `docs/PLAN_ITEM_OPEN_TASKS.md` + **`docs/PLAN_ITEM_275_OPERATING_RHYTHM.md`** (ритм сверки и волн)
7. **Category truth:** `docs/PHASE2_CATEGORY_ACCEPTANCE_STATUS_ALL.md`
8. **Evidence and sign-off:** `docs/PHASE2_EVIDENCE_PACK_REPORT.md`, `docs/PHASE2_FINAL_SIGNOFF.md`
9. **Last full gate run:** `docs/PHASE2_FINAL_VERIFICATION_RUN.md`
10. **275 audit:** `docs/PLAN_ITEM_275_AUDIT_REPORT.md` (includes §1a **localization vs 275**; regenerate: `python3 scripts/plan_item_275_audit.py`)
11. **275 age checklist (generated):** `docs/PLAN_ITEM_275_BY_AGE_READABLE.md` (`python3 scripts/plan_item_275_age_checklist.py`)
12. **Prod content API + plan gaps:** `docs/CHILD_CONTENT_PROD_CHECK_AND_ROADMAP.md`
13. **Content endpoint contract + smoke:** `docs/ENDPOINT_CONTRACT_AND_SERVER_ACCESS.md`
14. **Wave-1 slice (optional):** `docs/PLAN_ITEM_WAVE_1.md`

---

## 2a) Completeness: can we promise “nothing to add ever”?

**No.** Any living product will eventually need new rows or documents when:

- regulators, App Store rules, or school partnerships change;
- you add categories, locales, or server-only content packs;
- Apple ships new OS APIs or deprecations (SwiftUI, SceneKit, PencilKit);
- telemetry or KPI definitions evolve.

What **is** complete today:

- **Traceability:** 275 unique `(PLAN_ITEM, category_id)` pairs, unique `item_id`, validated by `plan_item_traceability_smoke.py` and `plan_item_275_audit.py`.
- **Narrative + map:** this handbook + `ML_SYSTEM_TRANSFER_PACKAGE_PHASE2.md` + matrix header link back here.
- **Operational proof:** Phase 2 gates and `PHASE2_FINAL_VERIFICATION_RUN.md`.

**Process rule:** when the product changes, update the matrix row and rerun the two scripts above; update handbook section 8 if new doc families appear.

---

## 2b) Child UI density, performance, and crashes

**Where 275 items “live” in the app**

- **Hub:** `Screens/08_ChildInterfaceScreen.swift` → `Screens/ChildContentScreen.swift` (categories, journeys, cards). Users do **not** open 275 modules on one screen; they pick **one category**, then **one item** from a list.
- **Experience:** `Screens/ChildContentExperienceScreen.swift` hosts the heavy module (3D, drawing, karaoke, drills, …) **one at a time** in navigation flow.
- **Data:** `Core/Content/*` loads manifest/items; scale comes from **list virtualization** (SwiftUI `List` / lazy stacks) and **incremental sync**, not from rendering 275 bespoke views at once.

**Will the page be overloaded?**

- Risk is **UX clutter** on `ChildContentScreen` if too many *persistent* cards (journey, adaptive, rewards, etc.) stack without hierarchy — mitigated by design: collapse secondary cards into a single “Today” section, sheets, or tabs; keep one primary CTA per age band.
- **275 items** are **data rows**, not 275 simultaneous views.

**Architecture fit**

- Modular routing (`ContentExperienceResolver` + experience screen) is the right pattern for large catalogs.
- **Stability:** avoid blocking `main` with heavy work; load assets lazily; test SceneKit / PencilKit on older devices; use Instruments (Time Profiler, Allocations) when adding many new experiences.
- **Crashes:** follow existing gates (`localization_lint`, a11y smoke, `xcodebuild`); add unit/UI tests for new branches; keep `ContentValidator` fail-closed on bad manifest data.

---

## 3) Runtime architecture (where child content “lives”)

### 3.1 Data and lifecycle

| Concern | Location |
| --- | --- |
| Models (items, categories, progress, learning contract) | `Core/Content/Models/ContentModels.swift` |
| Seed manifest (baseline items per category) | `Core/Content/Seed/ContentSeedProvider.swift` |
| Load / sync / personalize | `Core/Content/ContentManager.swift` |
| Sync, manifest, delta | `Core/Content/Sync/ContentSyncManager.swift`, `Core/Content/Sync/NetworkContentAPIClient.swift`, `Core/Content/Sync/DefaultContentAPIClient.swift` |
| Validation / signing | `Core/Content/Validation/ContentValidator.swift`, `Core/Content/Validation/ContentManifestSigning.swift` |
| Routing experience by type | `Core/Content/Experiences/ContentExperienceResolver.swift`, `Core/Content/Experiences/ContentExperienceRoute.swift` |
| Storage / cache / versioning | `Core/Content/Storage/ContentDatabase.swift`, `Core/Content/Cache/*`, `Core/Content/Versioning/ContentVersionManager.swift` |

### 3.2 UI (child + parent mirror)

| Surface | Location |
| --- | --- |
| Child shell | `Screens/08_ChildInterfaceScreen.swift` |
| Category feed, journeys, adaptive loop, rewards, creative output | `Screens/ChildContentScreen.swift` |
| Per-item experiences (toys 3D, drawing, karaoke, stories, games, study, safety, cartoons, programming, social, music, education, …) | `Screens/ChildContentExperienceScreen.swift` |
| Parent outcome layer (learned panel, digest, mastery, ROI) | `Screens/ParentDashboardView.swift` |
| Related gamification / rewards surfaces | `Screens/ChildRewardsScreen.swift`, `Screens/RewardsModalView.swift`, `Screens/RewardsQuickModal.swift`, `Screens/GamesParentalControlScreen.swift` |

### 3.3 Localization (mandatory dual language)

| Resource | Path |
| --- | --- |
| Russian | `Resources/Localization/ru.lproj/Localizable.strings` |
| English | `Resources/Localization/en.lproj/Localizable.strings` |
| Lint gate | `scripts/localization_lint.py` |
| Standards | `docs/LOCALIZATION_IMPLEMENTATION_STANDARD.md`, `docs/LOCALIZATION_KEY_NAMESPACE_MAP.md`, `docs/LOCALIZATION_PR_CHECKLIST.md` |

---

## 4) Governance, gates, and reports (what “PASS” means)

### 4.1 Phase 2 Python gates (child content program)

| Script | Role |
| --- | --- |
| `scripts/phase2_category_count_gate.py` | Minimum seed counts per category (baseline profile). |
| `scripts/phase2_category_acceptance_smoke.py` | Files exist, 12 categories mapped, count gate report present. |
| `scripts/phase2_learning_effectiveness_gate.py` | Learning effectiveness contract in docs/repo rules. |
| `scripts/phase2_engagement_health_gate.py` | Engagement health contract. |
| `scripts/phase2_editorial_model_smoke.py` | Editorial model document valid. |
| `scripts/phase2_content_qa_matrix_smoke.py` | QA matrix on category + item level. |
| `scripts/phase2_content_freshness_sla_smoke.py` | Freshness SLA policy. |
| `scripts/phase2_ab_validation_smoke.py` | A/B framework doc. |
| `scripts/phase2_stimulus_budget_smoke.py` | Stimulus budget 1–6 policy. |
| `scripts/phase2_unified_telemetry_schema_smoke.py` | Telemetry schema doc. |
| `scripts/phase2_weekly_improvement_loop_smoke.py` | Weekly improvement loop doc. |
| `scripts/phase2_content_health_dashboard_smoke.py` | Health dashboard doc. |
| `scripts/phase2_completion_not_learning_guard_smoke.py` | “Completion ≠ learning” guard doc. |
| `scripts/plan_item_traceability_smoke.py` | Parses `PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md` rows. |

### 4.2 Cross-cutting smokes (still part of release discipline)

| Script | Role |
| --- | --- |
| `scripts/phase_w_loc_6_a11y_sync_content_smoke.py` | Localization + accessibility sync for content flows. |
| `scripts/phase7_content_qa_matrix_smoke.py` | Legacy name / Phase 7 lineage; keep in CI where referenced. |
| `scripts/ipa_size_gate.py` | Binary size cap (e.g. `--max-mb 500`). |

### 4.3 Generated / committed reports (`docs/`)

All `docs/PHASE2_*_REPORT.md` (+ `.json` where present) are the **machine-readable proof** for gates. Consolidated summary: `docs/PHASE2_EVIDENCE_PACK_REPORT.md` / `.json`. Final human sign-off: `docs/PHASE2_FINAL_SIGNOFF.md`.

### 4.4 Per-task closure memos (68 tail: 56–68)

| Task | Evidence file |
| --- | --- |
| 56 | `docs/TASK_56_DONE.md` |
| 57 | `docs/TASK_57_DONE.md` |
| 58 | `docs/TASK_58_DONE.md` |
| 59 | `docs/TASK_59_DONE.md` |
| 60 | `docs/TASK_60_DONE.md` |
| 61 | `docs/TASK_61_DONE.md` |
| 62 | `docs/TASK_62_DONE.md` |
| 63 | `docs/TASK_63_DONE.md` |
| 64 | `docs/TASK_64_DONE.md` |
| 65 | `docs/TASK_65_DONE.md` |
| 66 | `docs/TASK_66_DONE.md` |
| 67 | `docs/TASK_67_DONE.md` |
| 68 | `docs/TASK_68_DONE.md` |

### 4.5 Policy documents (design intent, not executable)

Examples: `docs/PHASE2_CONTENT_EDITORIAL_MODEL.md`, `docs/PHASE2_CONTENT_FRESHNESS_SLA.md`, `docs/PHASE2_STIMULUS_BUDGET_POLICY_1_6.md`, `docs/PHASE2_UNIFIED_TELEMETRY_SCHEMA.md`, `docs/PHASE2_WEEKLY_IMPROVEMENT_LOOP.md`, `docs/PHASE2_CONTENT_HEALTH_DASHBOARD_ALERTING.md`, `docs/PHASE2_COMPLETION_NOT_LEARNING_GUARD.md`, `docs/PHASE2_AB_VALIDATION_FRAMEWORK.md`.

---

## 5) Waves on top of the 275 matrix

| Artifact | Purpose |
| --- | --- |
| `docs/PLAN_ITEM_WAVE_1.md` | First 10 open items from `PLAN_ITEM_OPEN_TASKS.md` with owners and gates. |
| `docs/PLAN_ITEM_OPEN_TASKS.md` | Filtered backlog (`PARTIAL` + `TODO`). |

**Rule:** each wave closes with: `plan_item_traceability_smoke.py` + `phase2_content_qa_matrix_smoke.py` + `localization_lint.py` + `xcodebuild` (as already written in Wave-1).

---

## 6) What is *not* fully covered by “68 done”

- **275 catalog**: many `TODO` / `PARTIAL` rows — need content design + seed/API expansion + UX per theme.
- **Strict item counts** (e.g. 15 toys, 30 study topics): growth targets; see “Missing” lines in `PHASE2_CATEGORY_ACCEPTANCE_STATUS_ALL.md`.

---

## 7) Quick “start coding” checklist for ML

1. Pick a row in `PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md` (or `PLAN_ITEM_OPEN_TASKS.md`).
2. Map `category_id` → `ContentSeedProvider` / server manifest → `ChildContentExperienceScreen` branch.
3. Add RU+EN keys; run `python3 scripts/localization_lint.py`.
4. Run `python3 scripts/phase2_content_qa_matrix_smoke.py` and `xcodebuild` on the ALADDIN scheme.
5. Update the matrix row from `TODO`/`PARTIAL` to `DONE` with owner/due/wave.

---

## 8) Document map (everything tied to child content interface)

| Layer | Files |
| --- | --- |
| Global execution (178) | `docs/EXECUTION_AND_LOCALIZATION_DASHBOARD.md`, `docs/PLAN_174_ML_HANDOFF_FRONTEND.md`, `docs/INDEPENDENT_PLAN_FACT_AUDIT_174.md` |
| Phase 2 plan | `docs/PHASE2_CHILD_CONTENT_100_PERCENT_PLAN.md`, `docs/PHASE2_100_IMPLEMENTATION_BACKLOG_FOR_ML.md` |
| Phase 2 trackers | `docs/PHASE2_LIVE_TODO_TRACKER.md`, `docs/CURSOR_CHAT_PENDING_CHECKLIST.md` |
| Acceptance | `docs/PHASE2_CATEGORY_ACCEPTANCE_CHECKLIST_TEMPLATE.md`, `docs/PHASE2_CATEGORY_ACCEPTANCE_STATUS_ALL.md` |
| 275 matrix | `docs/PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md`, `docs/PLAN_ITEM_OPEN_TASKS.md`, `docs/PLAN_ITEM_WAVE_1.md`, `docs/PLAN_ITEM_275_AUDIT_REPORT.md` |
| Proof | `docs/PHASE2_EVIDENCE_PACK_REPORT.md`, `docs/PHASE2_FINAL_SIGNOFF.md`, `docs/PHASE2_FINAL_VERIFICATION_RUN.md` |
| Plan vs fact | `docs/CHILD_CONTENT_INTERFACE_PLAN_FACT.md` |

**Entry point for another ML system:** `docs/ML_SYSTEM_TRANSFER_PACKAGE_PHASE2.md` **and** this handbook.
