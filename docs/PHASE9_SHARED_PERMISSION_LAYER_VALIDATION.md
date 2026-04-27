# Phase 9.3 Validation (Shared Family Permission Layer)

Scope:

- `9.3` — shared family permissions layer reused by child and elderly interfaces.

## Smoke command

Run:

`python3 scripts/phase9_shared_permission_layer_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

## What it validates

1. **Layer contracts**
   - `FamilyPermissionLayer` exists in `Core/Profile/FamilyAccessPolicy.swift`.
   - snapshot API and capabilities are present:
     - `canEditContacts`
     - `canManageFamilyLimits`
     - `canManageCriticalFamilySettings`
2. **Screen integration**
   - child interface uses `FamilyPermissionLayer.snapshot`.
   - elderly interface uses `FamilyPermissionLayer.snapshot`.
3. **Build**
   - app build succeeds on iPhone 16 simulator.
