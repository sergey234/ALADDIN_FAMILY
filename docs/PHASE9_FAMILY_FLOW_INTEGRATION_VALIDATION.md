# Phase 9.3 Validation (Child -> Parent -> Elderly Integration Tests)

Scope:

- `9.3` — integration test coverage for child/parent/elderly family flow in one unified family contour.

## Smoke command

Run:

`python3 scripts/phase9_family_flow_integration_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

## What it validates

1. **Integration tests present**
   - `testUnifiedFamilyPermissionsChildParentElderlyScenario`
   - `testUnifiedFamilyRosterProjectsConsistentContactsForChildAndElderly`
2. **Coverage intent**
   - tests assert `FamilyPermissionLayer` role-based capabilities across child -> parent -> elderly actors.
   - tests assert `UnifiedFamilyRoster` projections are consistent across child/elderly audiences.
3. **Build**
   - app build succeeds on iPhone 16 simulator.
