# Phase 8.4 Security Validation (Parental Control + DSAR)

Scope of this validation pass:

- `Track A · Phase 8` — Валидация родительского контроля
- `Track A · Phase 8` — Проверка DSAR процессов (экспорт/удаление данных) и журналирования согласий

## Automated smoke gate

Run:

`python3 scripts/phase8_security_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

What it verifies:

1. `Core/Profile/ParentSessionGate.swift`
   - Secure PIN API exists (`setParentalPIN`, `verifyParentalPIN`)
   - PIN is not stored plaintext (SHA-256 + secure storage)
   - Rate limiting and lockout exist (max attempts + blocked window)
2. `Core/Profile/ProfileManager.swift`
   - DSAR export contract exists (`ChildDataRightsPackage`, `exportChildDataRightsPackage`)
   - DSAR delete contract exists (`deleteChildData`)
   - Diagnostic summary for audit flow exists
3. `Screens/ParentDashboardView.swift`
   - Parent-only data-rights actions exist in UI (`Export child data`, `Delete active child data`)
   - Sensitive flow is challenge-gated via `ParentSessionGate.confirmSensitiveAction()`

## Notes

- This is a deterministic contract smoke and does not replace full end-to-end legal/compliance audit.
- Existing `ALADDINUnitTests` compile blockers remain explicitly deferred as the post-plan final item.
