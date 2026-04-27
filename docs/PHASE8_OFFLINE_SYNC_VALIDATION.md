# Phase 8.1 Validation (Offline + Sync)

Scope of this pass:

- `Track A · Phase 8` — Проверка работы оффлайн режима
- `Track A · Phase 8` — Тестирование синхронизации данных

## Smoke command

Run:

`python3 scripts/phase8_offline_sync_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

## What is validated

1. `Core/Offline/OfflineManager.swift`
   - online/offline state contract,
   - pending queue accounting,
   - enqueue/retry processing,
   - reconnect trigger that processes queued operations.
2. `Core/Content/Sync/ContentSyncManager.swift`
   - hard offline guard,
   - delta sync path,
   - fallback to full manifest when delta fails.
3. `ViewModels/FamilyViewModel.swift`
   - family fetch -> profile reconcile bridge,
   - reconcile diagnostics availability.

## Notes

- This smoke validates implementation contracts and flow wiring.
- Full device-matrix and live-network QA remains in open Phase 8 tasks.
