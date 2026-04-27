# Phase 9.3 Validation (Unified Child x Elderly Family Model)

Scope:

- `9.3` — unified `family roster` as single source of roles for child/parent/elderly.
- `9.3` — integration of unified roster projection into child and elderly contact pipelines.

## Smoke command

Run:

`python3 scripts/phase9_unified_family_model_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

## What it validates

1. **Unified family model contracts**
   - `Core/Profile/UnifiedFamilyRoster.swift` exists.
   - `load/contactProjections/fallbackPhone` contracts are present.
2. **Screen integrations**
   - `Screens/08_ChildInterfaceScreen.swift` uses unified roster projections.
   - `Screens/09_ElderlyInterfaceScreen.swift` uses unified roster projections.
   - legacy child placeholder phone is removed from roster projection path.
3. **Build verification**
   - app build succeeds on iPhone 16 simulator.
