# ML Handoff: Plan-Fact Status and Next Work

Last verified: 2026-04-25
Scope: ALADDIN iOS, execution plan continuity

## 1) Canonical status (plan-fact)

- Total tasks: **178**
- Done: **144**
- Pending: **34**
- Phase 6: **8/8 (100%)**
- Phase 7: **6/23 (26%)**

Source of truth:
- `docs/EXECUTION_AND_LOCALIZATION_DASHBOARD.md`

Generated mirrors (must match dashboard after any checkbox change):
- `Core/Planning/ImplementationPlanProgressValues.swift`
- `Core/Planning/ImplementationPlanDashboardMirror.generated.swift`
- `docs/CURSOR_CHAT_PENDING_CHECKLIST.md`

## 2) Mandatory workflow for plan updates

If any task checkbox changes in plan/dashboard:

1. Update checklist lines in:
   - `docs/EXECUTION_AND_LOCALIZATION_DASHBOARD.md`
   - `NEXT_VERSION_IMPLEMENTATION_PLAN.md`
2. Run:
   - `python3 scripts/update_dashboard_stats.py`
3. Verify generated values changed consistently.
4. Run build check:
   - `xcodebuild -scheme ALADDIN -project ALADDIN.xcodeproj -configuration Debug -destination 'generic/platform=iOS Simulator' build`
5. Report:
   - what was implemented,
   - which checklist items were toggled,
   - final done/pending counts.

Do not mark tasks done without code + build + reflected plan-fact state.

## 3) Already implemented in current stream

### Phase 6.2 (closed)
- Quiz progress segments + micro interactions.
- Goal progress visual feedback (gradient/ticks/animated fill).
- Reward purchase burst animation (`rewardPurchase`) and trigger wiring.

### Phase 7.1 (closed)
- `Core/Profile/ChildProfile.swift`
- `Core/Profile/ProfileManager.swift`
- Validation + backup/restore.

### Phase 7.2 (partially closed)
- App-level roster -> profile sync:
  - `ProfileManager.syncChildRosterFromServer(...)`
- Policy split between app profiles and Family Sharing:
  - `Core/Profile/FamilyAccessPolicy.swift`
- Biometric gate for sensitive roster action:
  - `Core/Profile/ParentSessionGate.swift`
- Child selection flow connected to profile-backed fallback:
  - `Screens/07_ParentalControlScreen.swift`
- Active child propagation for rewards scope:
  - `Core/Storage/StorageManager.swift` (`active_child_profile_server_id` in resolver)

## 4) Remaining work focus (next iterations)

Current completion update:

1. Phase 7.2 completed: session timeout + permission hardening + deterministic cross-device reconcile.
2. Phase 7.3 completed: child-scoped personalization + recommendation scoring + progress-aware difficulty.
3. Phase 7.4 completed: parental dashboard/stats, time limits, content filters, reports, secure PIN threat model with rate limiting, mandatory challenge fallback, DSAR-style child data export/delete flows.
4. Phase 8.4 (partial) completed: parental-control and DSAR validation smoke gate added (`scripts/phase8_security_smoke.py`) with execution runbook (`docs/PHASE8_SECURITY_VALIDATION.md`).
5. Phase 8.1 (partial) completed: offline mode and sync flow validation smoke gate added (`scripts/phase8_offline_sync_smoke.py`) with execution runbook (`docs/PHASE8_OFFLINE_SYNC_VALIDATION.md`).
6. Phase 8.1 completed: content correctness + device validation smoke gate added (`scripts/phase8_content_device_smoke.py`) and executed (content contract + iPhone simulator build + iPad simulator build) with runbook (`docs/PHASE8_CONTENT_DEVICE_VALIDATION.md`).
7. Phase 8.2 completed: UX smoke gate added (`scripts/phase8_ux_smoke.py`) and executed (age coverage + accessibility baseline + reduce motion/readability + animation perf contract + multi-screen-size build matrix) with runbook (`docs/PHASE8_UX_VALIDATION.md`).
8. Phase 8.3 completed: performance smoke gate added (`scripts/phase8_performance_smoke.py`) and executed (content cache/load contracts + animation/audio optimization contracts + old-device iPhone 11 build + app bundle size budget check) with runbook (`docs/PHASE8_PERFORMANCE_VALIDATION.md`).
9. Phase 8.4 completed: compliance smoke gate added (`scripts/phase8_compliance_smoke.py`) and executed (COPPA governance contracts + personal-data storage audit contracts + Family Sharing security contracts + dependent smoke gates pass) with runbook (`docs/PHASE8_COMPLIANCE_VALIDATION.md`).
10. Phase 9.1 progressed: critical 60+ flows simplified to one-tap/two-tap actions in `Screens/09_ElderlyInterfaceScreen.swift` (quick family call, quick medication mark-as-taken, quick security action), role-safe emergency contact filtering added, and touchpoint localization hardcoded cleanup performed. Validation: `scripts/phase9_elderly_critical_smoke.py` + runbook `docs/PHASE9_CRITICAL_FLOWS_VALIDATION.md`.
16. Phase 9.1 progressed: completed elderly data-vs-placeholder audit and finalized family phone model without static placeholders by introducing unified phone directory contracts in `UnifiedFamilyRoster` (`phoneDirectoryKey`, `persistPhoneDirectory`, stable contact ID mapping) and wiring phone persistence in child+elderly contact editors. Validation: `scripts/phase9_elderly_data_audit_smoke.py` + runbook `docs/PHASE9_ELDERLY_DATA_AUDIT_VALIDATION.md`.
17. Phase 9.1 completed: added full elderly readability accessibility preset stack — explicit large read mode (`elderly_large_read_mode`) and contrast presets (`elderly_contrast_preset`) with screen-level application (`dynamicTypeSize` + contrast modifier) and settings controls in `ElderlySettingsModal`, including RU/EN localization keys. Validation: `scripts/phase9_elderly_readability_contrast_smoke.py` + runbook `docs/PHASE9_ELDERLY_READABILITY_CONTRAST_VALIDATION.md`.
18. Phase 9.4 started: linked child content categories and family safety toggles with elderly content controls by introducing `FamilyContentSafetyBridge` in `Core/Content/Seed/ContentSeedProvider.swift` and switching elderly feed loading to bridge-resolved categories in `Screens/09_ElderlyInterfaceScreen.swift`. Validation: `scripts/phase9_content_safety_alignment_smoke.py` + runbook `docs/PHASE9_CONTENT_SAFETY_ALIGNMENT_VALIDATION.md`.
19. Phase 9.4 progressed: removed category naming/logic drift across child and elderly screens by introducing a unified safety title key (`FamilyContentSafetyBridge.safetyTitleKey` -> `family_category_safety`) used in both interfaces and content seed category mapping, ensuring one canonical safety label and synchronized category semantics across age tracks.
20. Phase 9.4 progressed: locked a unified content lifecycle for child and elderly interfaces by introducing centralized lifecycle entrypoints in `ContentManager` (`runUnifiedLifecycle`, `loadUnifiedAudienceFeed`) and wiring child/elderly screens to this shared flow (`Screens/08_ChildInterfaceScreen.swift`, `Screens/09_ElderlyInterfaceScreen.swift`). Validation: `scripts/phase9_content_lifecycle_unified_smoke.py` + runbook `docs/PHASE9_CONTENT_LIFECYCLE_UNIFIED_VALIDATION.md`.
11. Phase 9.2 completed: implemented no-loss cross-device reconciliation for family/health entities via versioned sync envelope + deterministic merge policy (`ElderlyHealthSyncEnvelope`, `ElderlyHealthSyncAudit.synchronizeAcrossDevices`, `mergeWithoutLoss`), integrated persisted desync report for parent banner in `Screens/07_ParentalControlScreen.swift`, and removed legacy contact phone placeholder fallback debt in elderly contacts pipeline. Validation: `scripts/phase9_data_integrity_smoke.py` + runbook `docs/PHASE9_DATA_INTEGRITY_VALIDATION.md`.
12. Phase 9.3 progressed: unified family roster projection layer introduced in `Core/Profile/FamilyAccessPolicy.swift` (`UnifiedFamilyRoster`) and integrated into child/elderly contact pipelines (`Screens/08_ChildInterfaceScreen.swift`, `Screens/09_ElderlyInterfaceScreen.swift`) so both audiences consume a single role source (`family_members_list`) with consistent fallback phone projection and relation-key mapping. Validation: `scripts/phase9_unified_family_model_smoke.py` + runbook `docs/PHASE9_UNIFIED_FAMILY_MODEL_VALIDATION.md`.
13. Phase 9.3 progressed: synchronized access policy matrix for contacts, limits and critical settings via `FamilyAccessPolicy.Permission` (`editFamilyContacts`, `manageFamilyLimits`, `manageCriticalFamilySettings`) and applied in child/elderly contact editors plus parental limits/critical modals (`Screens/08_ChildInterfaceScreen.swift`, `Screens/09_ElderlyInterfaceScreen.swift`, `Screens/07_ParentalControlScreen.swift`). Validation: `scripts/phase9_access_rules_smoke.py` + runbook `docs/PHASE9_ACCESS_RULES_VALIDATION.md`.
14. Phase 9.3 progressed: introduced shared family permissions layer `FamilyPermissionLayer` (snapshot-based capabilities) in `Core/Profile/FamilyAccessPolicy.swift` and wired it into child + elderly interfaces as a common permission source (`Screens/08_ChildInterfaceScreen.swift`, `Screens/09_ElderlyInterfaceScreen.swift`). Validation: `scripts/phase9_shared_permission_layer_smoke.py` + runbook `docs/PHASE9_SHARED_PERMISSION_LAYER_VALIDATION.md`.
15. Phase 9.3 completed: added integration tests for child->parent->elderly family contour in `Tests/UnitTests/ChildRosterReconcilePolicyTests.swift` covering unified permission transitions (`FamilyPermissionLayer.snapshot`) and unified contact projections (`UnifiedFamilyRoster.contactProjections`) across audiences. Validation: `scripts/phase9_family_flow_integration_smoke.py` + runbook `docs/PHASE9_FAMILY_FLOW_INTEGRATION_VALIDATION.md`.

Recommended next implementation order:

1. `SessionTimeoutGate` (single service).
2. Apply gate to sensitive operations (family remove/edit, critical parental controls).
3. Permission map service for UI/API guard consistency.
4. Cross-device sync reconciliation rules + conflict strategy.
5. Update checklist + run dashboard stats script + build.

Post-plan final item (execute last):
- Fix pre-existing `ALADDINUnitTests` target compile blockers and run `ChildRosterReconcilePolicyTests` green.
- This item is intentionally deferred to the very end and does not change 178-task plan-fact counters.

## 4.1) Prioritized execution TODO (next 2 iterations, Phase 7.2 only)

Iteration 1 — Session timeout + guarded sensitive actions:
1. Extend `ParentSessionGate` with timeout-backed adult session (`sessionTimeout`, persist last successful auth timestamp).
2. Route sensitive roster operations through single guard API (`confirmSensitiveAction()`).
3. Apply guard to member removal/edit entry points in family domain (`Screens/02_FamilyScreen.swift` first).
4. Add explicit invalidation hook for forced re-auth scenarios (`invalidateSession()`), keep API ready for future integration.

Definition of done (Iteration 1):
- Sensitive roster action does not re-prompt biometrics within active session TTL.
- After TTL expires, sensitive action requires confirmation again.
- Build green: `xcodebuild ... build`.

Test checklist (Iteration 1):
- Positive path: first sensitive action -> biometric success -> action allowed.
- Warm session path: repeat action inside TTL -> no biometric prompt.
- Expired session path: wait past TTL -> biometric prompt required again.
- Failure path: biometric cancel/fail -> action blocked, no state mutation.

Iteration 2 — Permissions hardening + cross-device sync:
1. Introduce centralized permission map service for family/profile operations (single source for role capabilities).
2. Replace scattered UI checks with centralized permission calls in family + parental screens.
3. Define and implement cross-device reconciliation rules for child roster/profile deltas (server-linked precedence + conflict strategy).
4. Add reconciliation telemetry/log markers for desync diagnostics.

Progress note (current):
- Centralized permission map introduced in `Core/Profile/FamilyAccessPolicy.swift` (`Permission`, `hasPermission(...)`).
- `Screens/02_FamilyScreen.swift` moved to `hasPermission(...)` for roster/family-sharing checks.
- `Screens/07_ParentalControlScreen.swift` now gates sensitive parental modals via permission check + `ParentSessionGate.confirmSensitiveAction()`.
- `ProfileManager.syncChildRosterFromServer(...)` switched to deterministic reconcile flow (server-authoritative for server-linked fields) with diagnostics:
  - `lastChildRosterReconcileSummary`
  - log format: `serverChildren / inserted / updated / removed / conflicts`.
- `Screens/02_FamilyScreen.swift` now surfaces reconcile diagnostics in UI banner (`childRosterReconcileBanner`) after sync, not only in logs.
- Conflict strategy extracted to dedicated policy file:
  - `Core/Profile/ChildRosterReconcilePolicy.swift`
  - `ProfileManager` now delegates merge rules to this policy (single source of reconcile behavior).
- Phase 7.2.1 implemented:
  - entitlement readiness snapshot in `ParentalControlManager.assessFamilyControlsReadiness()`,
  - pipeline `AuthorizationCenter -> ManagedSettings -> DeviceActivity` in `applyFamilyControlsPipelineIfPossible()`,
  - fallback UX banner/retry entry in `Screens/07_ParentalControlScreen.swift`.
- Phase 7.3 implemented:
  - child-scoped preference analysis in `InterestAnalyzer` (storage key v2 per child),
  - explainable recommendation scoring in `ContentRecommender` (`ContentRecommendation` reasons + combined score),
  - difficulty adaptation tuning in `DifficultyAdapter` and `LearningPathGenerator`,
  - integration with progress + active child scope in `ContentManager.loadPersonalizedContent(...)` and `recordPersonalizationInteraction(...)`.

Definition of done (Iteration 2):
- Role-based critical actions are gated by one central permissions API.
- Roster/profile sync converges deterministically across device/server updates.
- Build green + plan-fact mirrors unchanged unless checklist states are toggled intentionally.

Test checklist (Iteration 2):
- Parent role can perform app-profile management actions expected by policy.
- Non-parent role is denied critical operations with clear UX fallback.
- Concurrent update simulation (local + server) resolves with stable deterministic winner.
- App restart preserves synchronized roster/profile state.

## 5) Key files for the next ML system

Plan and mirrors:
- `docs/EXECUTION_AND_LOCALIZATION_DASHBOARD.md`
- `NEXT_VERSION_IMPLEMENTATION_PLAN.md`
- `Core/Planning/ImplementationPlanProgressValues.swift`
- `Core/Planning/ImplementationPlanDashboardMirror.generated.swift`
- `docs/CURSOR_CHAT_PENDING_CHECKLIST.md`

Family/profile domain:
- `Core/Profile/ChildProfile.swift`
- `Core/Profile/ProfileManager.swift`
- `Core/Profile/FamilyAccessPolicy.swift`
- `Core/Profile/ParentSessionGate.swift`
- `Core/Managers/FamilyLocalStore.swift`
- `Screens/02_FamilyScreen.swift`
- `Screens/07_ParentalControlScreen.swift`
- `ViewModels/FamilyViewModel.swift`
- `Core/Storage/StorageManager.swift`

## 5.1) Electronic task board attachment (required)

Remaining plan TODO is attached to the in-app electronic board:
- `Screens/ImplementationPlanWorkbenchCard.swift` (renders full pending checklist from generated mirror).
- Source list for board items: `Core/Planning/ImplementationPlanDashboardMirror.generated.swift` (`pendingItems` = 34).
- Human-readable mirror for side tracking in chat sessions: `docs/CURSOR_CHAT_PENDING_CHECKLIST.md`.

After any checkbox state change, regenerate board sources with:
- `python3 scripts/update_dashboard_stats.py`

## 6) Ready-to-use prompt for next ML session

Use this as the first message to the next ML system:

"""
Continue ALADDIN iOS execution plan from current plan-fact state.
Current verified metrics: total=178, done=144, pending=34.
Use docs/EXECUTION_AND_LOCALIZATION_DASHBOARD.md as source of truth.

After any checkbox changes, run:
python3 scripts/update_dashboard_stats.py
Then verify consistency with:
- Core/Planning/ImplementationPlanProgressValues.swift
- Core/Planning/ImplementationPlanDashboardMirror.generated.swift
- docs/CURSOR_CHAT_PENDING_CHECKLIST.md

Current target: continue with next open checklist block from dashboard mirror (`pendingItems`).

Do implementation + build verification + plan-fact update in one cycle.
"""

