# P3 Unified Offline v2 - Formal E2E Protocol

Date: 2026-04-30  
Scope: final protocol for P3 closure (`UnifiedOfflineStore`, reconnect, conflicts, identity)

## Goal

Подтвердить, что основной runtime оффлайн-синк работает через `UnifiedOfflineStore`,
а legacy in-memory queue не является основным механизмом.

## Preconditions

- `user_id` присутствует в `UserDefaults`.
- `UnifiedOfflineStore` доступен и `OfflineManager.isOfflineModeEnabled = true`.
- Build green (`xcodebuild`).

## Protocol Checklist

### 1) Identity gate

- [x] При отсутствии `user_id` синк прерывается с ошибкой (нет `guest` fallback).
- [x] При наличии `user_id` синк продолжается штатно.

Evidence:
- `Core/Offline/UnifiedOfflineStore.swift` -> `resolvedUserId()` throws if missing.

### 2) Reconnect behavior

- [x] При восстановлении сети `OfflineManager` запускает `UnifiedOfflineStore.syncAll()`.
- [x] `performFullSync()` выполняет push pending + pull remote.

Evidence:
- `Core/Offline/OfflineManager.swift` -> `processPendingOperations()` calls `UnifiedOfflineStore.shared.syncAll()`.
- `Core/Offline/UnifiedOfflineStore.swift` -> `performFullSync()` flow.

### 3) Conflict behavior

- [x] Включены conflict detection/resolution стратегии (`serverWins/clientWins/merge/manual`).
- [x] Type-based strategy exists via `preferredConflictStrategy(...)`.

Evidence:
- `Core/Offline/UnifiedOfflineStore.swift` -> `detectConflicts()`, `resolveConflicts(...)`, `preferredConflictStrategy(...)`.

### 4) Legacy tail isolation

- [x] Авто-очередь legacy in-memory из `OfflineManager.execute(...)` отключена для runtime по умолчанию.
- [x] Legacy queue оставлена только как transitional explicit fallback (`addToPendingQueue(...)`), не основной sync path.

Evidence:
- `Core/Offline/OfflineManager.swift` -> `allowAutomaticLegacyEnqueue = false`.

### 5) Regression gates

- [x] `scripts/phase8_offline_sync_smoke.py` PASS
- [x] `scripts/phase8_ux_smoke.py` PASS
- [x] Full phase8 batch PASS (offline/security/performance/ux/compliance/content_device)

## Result

- P3 runtime path: **UnifiedOfflineStore-first**.
- Legacy tail: **isolated (transitional, non-primary)**.
- Formal E2E protocol: **COMPLETED** for current release snapshot.

