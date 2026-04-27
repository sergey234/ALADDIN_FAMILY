# Phase 9.1 Validation (Elderly Data Audit + Contact Placeholder Removal)

Scope:

- `9.1` — audit `ElderlyInterfaceScreen` data paths vs placeholder risk.
- `9.1` — remove placeholder contact numbers and finalize unified family phone model.

## Smoke command

Run:

`python3 scripts/phase9_elderly_data_audit_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

## What it validates

1. **Data-audit contracts**
   - `runDataIntegrityAudit()` is part of elderly screen lifecycle.
   - unified roster has phone directory contracts (`phoneDirectoryKey`, `persistPhoneDirectory`, `stableContactId`).
2. **Placeholder removal**
   - no hardcoded `"+7 (999) 000-00-00"` phone placeholder in elderly screen path.
3. **Cross-audience phone consistency**
   - child and elderly contact editors persist phone edits into one shared roster phone directory.
4. **Build**
   - app build succeeds on iPhone 16 simulator.
