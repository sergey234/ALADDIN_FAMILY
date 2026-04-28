# ML System Transfer Package — Child Content (Phase 2)

Use this file as the single entry point for another ML system.

**Governance (metrics + release scope + P0–P3, non-code track):** read **`docs/PLAN_GOVERNANCE_ONEPAGER.md`** immediately after this section if you need one page on «what number means what» and release table **R0–R3**.

## 1) Read In This Order

1. **`docs/PLAN_GOVERNANCE_ONEPAGER.md`** — **178 / 68 / 275 / G** disambiguation, release scope rows **R0–R3**, non-code G19/G21+ table.
1a. **`docs/CHILD_CONTENT_FINAL_SYSTEM_HANDOFF.md`** — **ML-ready end-state:** layers 178 + 68 + 275, architecture map, localization policy, mandatory validation commands, operational notes (read this if you only open one child-content doc).
2. **`docs/CHILD_CONTENT_INTERFACE_ML_HANDBOOK.md`** — full picture: 178 vs 68 vs **275** matrix, code map, gates, waves, document index.
3. **`docs/PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md`** — canonical **275-row** `PLAN_ITEM -> category_id -> item_id -> status` catalog (baseline gates include **`localization_lint`** per matrix header).
3a. **`docs/PLAN_ITEM_275_OPERATING_RHYTHM.md`** — **постоянный порядок:** сверка с каноном, волны, DoD, таблица соответствия возраст/категория, скрипты после правок.
4. `docs/PLAN_ITEM_OPEN_TASKS.md` — only `PARTIAL` + `TODO` rows from the matrix.
4a. **`docs/PLAN_ITEM_275_BY_AGE_READABLE.md`** — human checklist by age (regenerate: `python3 scripts/plan_item_275_age_checklist.py`).
4b. **`docs/PLAN_ITEM_275_AUDIT_REPORT.md`** — duplicates, per-category counts, Xcode Sources heuristic, **localization vs 275** (§1a), `linked_module` hints (regenerate: `python3 scripts/plan_item_275_audit.py`).
4c. **`docs/CHILD_CONTENT_PROD_CHECK_AND_ROADMAP.md`** — prod `/api/content/*` facts, API need/nice, plan additions for full delivery.
4d. **`docs/ENDPOINT_CONTRACT_AND_SERVER_ACCESS.md`** — content contract + `content_contract_smoke.py`.
5. `docs/EXECUTION_AND_LOCALIZATION_DASHBOARD.md` — global client plan (**178** tasks) and localization discipline.
5a. **Localization policy (apply to every new 275-facing UI string):** `docs/LOCALIZATION_IMPLEMENTATION_STANDARD.md`, `docs/LOCALIZATION_PR_CHECKLIST.md`, `docs/LOCALIZATION_KEY_NAMESPACE_MAP.md` (optional backlog context: `docs/LOCALIZATION_BASELINE_BACKLOG.md`; gamification key matrix: `docs/GAMIFICATION_LOCALIZATION_SYNC_MATRIX.md`).
6. `docs/PLAN_174_ML_HANDOFF_FRONTEND.md` — ML handoff for the **174 closed** items inside the 178-task dashboard (terminology).
7. `docs/GAP_CLOSURE_PLAN_PHASES_1_8_ML_HANDOFF.md`
8. `docs/PHASE2_CHILD_CONTENT_100_PERCENT_PLAN.md`
9. `docs/CHILD_CONTENT_INTERFACE_PLAN_FACT.md` — plan vs fact for child UI and content pipeline.
10. `docs/PHASE2_CATEGORY_ACCEPTANCE_CHECKLIST_TEMPLATE.md`
11. `docs/PHASE2_CATEGORY_ACCEPTANCE_STATUS_ALL.md`
12. `docs/PHASE2_100_IMPLEMENTATION_BACKLOG_FOR_ML.md`
13. `docs/PHASE2_LIVE_TODO_TRACKER.md` and `docs/CURSOR_CHAT_PENDING_CHECKLIST.md` — **68-task** Phase 2 closure (includes hard exit 56–65 and SF 66–68).
14. `docs/PHASE2_EVIDENCE_PACK_REPORT.md`, `docs/PHASE2_FINAL_SIGNOFF.md`, `docs/PHASE2_FINAL_VERIFICATION_RUN.md`
15. Per-exit-task memos: `docs/TASK_56_DONE.md` … `docs/TASK_68_DONE.md` (as applicable)

## 2) Core Code Areas

- `Core/Content/Models/ContentModels.swift`
- `Core/Content/Seed/ContentSeedProvider.swift`
- `Core/Content/ContentManager.swift`
- `Core/Content/Sync/ContentSyncManager.swift`
- `Core/Content/Sync/NetworkContentAPIClient.swift`
- `Core/Content/Validation/ContentValidator.swift`
- `Core/Content/Experiences/ContentExperienceResolver.swift`
- `Screens/ChildContentScreen.swift`
- `Screens/ChildContentExperienceScreen.swift`
- `Screens/ParentDashboardView.swift` (parent outcome mirror: learned panel, digest, mastery, ROI)
- `Resources/Localization/ru.lproj/Localizable.strings`
- `Resources/Localization/en.lproj/Localizable.strings`

## 3) Mandatory Commands Before/After Changes

- `python3 scripts/localization_lint.py`
- `python3 scripts/phase2_content_qa_matrix_smoke.py` (primary Phase 2 QA matrix gate)
- `python3 scripts/phase7_content_qa_matrix_smoke.py` (legacy / CI where still referenced)
- `python3 scripts/phase_w_loc_6_a11y_sync_content_smoke.py`
- `python3 scripts/ipa_size_gate.py --max-mb 500`

## 4) Current Truth Snapshot

- System architecture and governance: mature.
- Phase 2 **68-task** program: closed per `docs/CURSOR_CHAT_PENDING_CHECKLIST.md` with evidence in `docs/TASK_*_DONE.md` and `docs/PHASE2_FINAL_VERIFICATION_RUN.md`.
- **275-item** catalog matrix: **DONE 275 / PARTIAL 0 / TODO 0** as of **2026-04-28** (canonical: `docs/PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md`; open-row drill-down should be empty: `docs/PLAN_ITEM_OPEN_TASKS.md`).
- Category-level readiness baseline captured in:
  - `docs/PHASE2_CATEGORY_ACCEPTANCE_STATUS_ALL.md`

## 5) Non-Negotiable Delivery Policy

- No category can be marked done without:
  - learning outcome contract
  - interaction depth proof
  - educational evidence
  - RU/EN localization + a11y completeness
- No user-facing literal text in new modules.
- No duplicate localization keys.
- No noisy quotes/brackets in localized values.

## 6) First Execution Steps For Next ML System

**If you are continuing from the current repo baseline:** P2-001..P2-604 and exit criteria 56–68 are already delivered; the **275 matrix** is closed at the product row level — use **`docs/CHILD_CONTENT_FINAL_SYSTEM_HANDOFF.md`** § “Next ML system” for the recommended verification order, then maintain parity via `docs/PLAN_ITEM_275_OPERATING_RHYTHM.md` whenever the catalog changes.

**If you are bootstrapping from an older snapshot:**

1. Implement `P2-001..P2-003` from backlog first (contracts + gates).
2. Deliver 1-6 deep modules (P2-101..P2-104).
3. Deliver 7-12 depth (P2-201..P2-204).
4. Deliver 13-22 tracks (P2-301..P2-304).
5. Complete hardening and sign-off tasks (P2-401..P2-408) and parent/telemetry packs (P2-501..P2-604).

## 7) Completion Definition

- **Phase 2 engineering transfer:** all **12** child categories `READY`, hard gates and evidence pack pass — see `docs/PHASE2_CATEGORY_ACCEPTANCE_STATUS_ALL.md` and `docs/PHASE2_FINAL_VERIFICATION_RUN.md`.
- **275 catalog completeness:** **met** for the current matrix revision — all rows `DONE` in `docs/PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md`. Future product changes should add/retire rows explicitly and rerun `scripts/plan_item_traceability_smoke.py` + `scripts/plan_item_275_audit.py`.

## 8) Phase 2 gate scripts (reference)

All under `scripts/`: `phase2_category_count_gate.py`, `phase2_category_acceptance_smoke.py`, `phase2_learning_effectiveness_gate.py`, `phase2_engagement_health_gate.py`, `phase2_editorial_model_smoke.py`, `phase2_content_qa_matrix_smoke.py`, `phase2_content_freshness_sla_smoke.py`, `phase2_ab_validation_smoke.py`, `phase2_stimulus_budget_smoke.py`, `phase2_unified_telemetry_schema_smoke.py`, `phase2_weekly_improvement_loop_smoke.py`, `phase2_content_health_dashboard_smoke.py`, `phase2_completion_not_learning_guard_smoke.py`, plus `plan_item_traceability_smoke.py` (matrix row shape), **`plan_item_275_audit.py`** (duplicate detection + per-row register → `docs/PLAN_ITEM_275_AUDIT_REPORT.md`), and **`plan_item_275_age_checklist.py`** → `docs/PLAN_ITEM_275_BY_AGE_READABLE.md`.
