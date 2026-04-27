# Phase 9.3 Validation (Access Rules Synchronization)

Scope:

- `9.3` — synchronized access rules for contacts, limits and critical family settings.

## Smoke command

Run:

`python3 scripts/phase9_access_rules_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

## What it validates

1. **Policy layer**
   - `FamilyAccessPolicy.Permission` has:
     - `editFamilyContacts`
     - `manageFamilyLimits`
     - `manageCriticalFamilySettings`
2. **UI integrations**
   - child contacts edit flow is gated by `editFamilyContacts`.
   - elderly contacts edit flow is gated by `editFamilyContacts`.
   - parental limits cards use limits permission gate.
   - parental critical cards/session use critical-settings permission gate.
3. **Build verification**
   - app build succeeds on iPhone 16 simulator.
