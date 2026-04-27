# Phase 9 Validation (Critical 60+ Flows)

Scope:

- `9.1` — Упростить критические сценарии 60+ (экстренный звонок, лекарства, безопасность) до одного-двух действий.
- `9.5` (partial in this pass) — локализационная дисциплина для touched 60+ critical fragments.
- `9.2` (start in this pass) — базовая проверка целостности критичных 60+ данных.

## Smoke command

Run:

`python3 scripts/phase9_elderly_critical_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

## What is validated

1. **Quick critical-flow contracts**
   - `startQuickFamilyCall()`
   - `markFirstPendingMedicationAsTaken()`
   - `runQuickSecurityAction()`
   - user feedback via `criticalActionStatusMessage`
2. **Role-safe emergency contact filtering**
   - no localized-string matching for roles in emergency chooser
   - uses role enum-based filtering
3. **Localization hygiene for touched fragments**
   - no hardcoded `Время/Дата` labels in touched medication/appointment rows
   - no hardcoded icon-button strings for edit/delete in touched fragments
4. **Small-screen readiness**
   - iPhone SE (2nd generation) simulator build succeeds

## Notes

- Global localization debt still exists in the repository and is tracked separately.
- This validation file is focused on the currently implemented Phase 9 critical-flow slice.
