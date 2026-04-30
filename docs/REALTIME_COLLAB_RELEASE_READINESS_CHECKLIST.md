# Realtime/Collab Release Readiness (Items 1-7 snapshot)

Date: 2026-04-30
Scope: `docs/TODO_REALTIME_COLLABORATION_PLAN.md` items 1..7 (with P6 deferred)

## What Tested

- `xcodebuild -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 16' build` -> **BUILD SUCCEEDED**
- `python3 scripts/localization_lint.py` -> **PASS**
- `python3 scripts/phase8_offline_sync_smoke.py` -> **PASS**
- `python3 scripts/phase8_ux_smoke.py` -> **PASS**

### Full Phase8 batch (single-run summary)

- `scripts/phase8_offline_sync_smoke.py` -> **PASS** (0.34s)
- `scripts/phase8_security_smoke.py` -> **PASS** (0.34s)
- `scripts/phase8_performance_smoke.py` -> **PASS** (272.49s)
- `scripts/phase8_ux_smoke.py` -> **PASS** (74.49s)
- `scripts/phase8_compliance_smoke.py` -> **PASS** (14.22s)
- `scripts/phase8_content_device_smoke.py` -> **PASS** (46.5s)

### Functional checks completed in code

- **Item 1: AI streaming + resume**
  - `AIStreamingService` uses absolute endpoint URL (`AppConfig.apiBaseURL + aiAssistantStream`).
  - Transport switched to SSE line streaming (`URLSession.bytes` + `bytes.lines`), not buffered full-response parsing.
  - Retry for transient network errors (bounded attempts), cancellation path preserved.
  - Stream checkpoint persisted (`UserDefaults` + `UnifiedOfflineStore` `.aiInteraction`).

- **Item 2: uploadMedia + family chat media**
  - Voice/image send path includes upload + server send + offline pending fallback.
  - `mediaThumbnailUrl` preserved through message remaps/updates in `23_FamilyChatScreen`.
  - WS message decoding hardened (`message`/`payload`, snake/camel tolerance in `FamilyChatWebSocket`).

- **Item 3: Unified offline layer v2**
  - Runtime sync path moved to `UnifiedOfflineStore` (push pending + pull remote).
  - Conflict detection/resolution implemented (`serverWins/clientWins/merge/manual` behavior).
  - Legacy `OfflineStorageManager` runtime methods delegated to unified store.
  - Sync identity policy hardened: no `guest` fallback; missing `user_id` aborts sync with error state.

- **Item 4: Presence (hardening + UI final partial)**
- **Item 4: Presence (hardening + UI final)**
  - `FamilyChatWebSocket` handles `typing` + `presence` payload variants and emits connection status callbacks.
  - `FamilyChatScreen` now reflects connection badge state (online/reconnecting/offline) in UI.
  - Typing indicators are deduplicated, stale entries are pruned by TTL timer, and reconnect/disconnect clears stale state.
  - Online participants chips are rendered in chat header area when presence is known.

- **Item 5: Sign in with Apple + Magic Links**
  - Apple Sign-In endpoint/model/UI flow implemented (`AppConfig`, `APIModels`, `APIService`, `MainScreenWithRegistration`).
  - Magic-link request/consume API methods implemented and wired with deep-link parser in `ALADDINApp`.
  - Session persistence normalized for Apple/Magic-link login path (token/refresh/user_id).

- **Item 7: Thin Reactive Layer (SyncEngine)**
  - `SyncEngine` domain/state/event bus integrated in core offline/chat/ai pipelines.
  - Unified sync-state coverage added to heavy screens and non-heavy screens/views/modals.
  - Contract used across UI: `pending / syncing / synced / error / local / idle`.

## Risks / Residual Gaps

- **Backend contract risk (SSE):** true end-to-end behavior depends on production `/api/ai/assistant/stream` SSE conformance.
- **Conflict semantics:** merge is generic JSON merge; domain-specific merge rules per data type may still be needed.
- **Identity readiness:** strict `user_id` requirement is safer, but flows where `user_id` is not initialized must be validated in QA.
- **No full manual regression sweep:** automated gates are green, but full device/simulator user-journey smoke is still recommended.
- **Presence backend contract risk:** if backend sends non-standard presence user identifiers, some users may flicker in online chips.
- **P3 legacy tail:** isolated as transitional fallback; automatic legacy enqueue from `OfflineManager.execute(...)` is disabled.
- **P6 policy layer:** currently deferred; must remain explicitly marked deferred in roadmap until dedicated implementation cycle.

## Rollback Notes

- **Item 1 rollback:** revert `Core/Network/AIStreamingService.swift` to previous transport implementation if SSE backend incompatibility is detected.
- **Item 2 rollback:** revert `Screens/23_FamilyChatScreen.swift` media remap updates and `Core/Models/APIModels.swift` thumbnail propagation if message rendering regressions appear.
- **Item 3 rollback:** revert `Core/Offline/UnifiedOfflineStore.swift` + `Core/Offline/OfflineStorageManager.swift` delegation changes to legacy behavior only as last resort (may reintroduce duplication/inconsistency).

## Release Decision (snapshot for items 1-7)

- **Engineering readiness:** ✅ ready (build + lint + offline smoke pass)
- **QA readiness:** ⚠️ requires focused manual smoke on:
  - AI streaming interruptions/resume (network toggle/background/foreground)
  - Family chat media send/receive/edit/reaction with thumbnails
  - Offline sync with valid `user_id` across reconnect cycles

## Manual Reconnect Checklist (Item 4 Presence)

- Open family chat on two devices/simulators with same family; confirm status badge shows `В сети` on active connection.
- Start typing on device A; confirm typing indicator appears on device B and disappears within ~6s when typing stops.
- Turn off network on device A for 10-15s; confirm device B no longer shows stale typing/online chips for A.
- Restore network on device A; confirm reconnect badge appears then returns to `В сети`.
- Send a message immediately after reconnect; confirm message delivery and no duplicate typing indicators remain.

## P3 residual checklist (done/not done)

- [x] `UnifiedOfflineStore` full sync flow (`push pending + pull remote`) exists and runs in runtime.
- [x] Strict sync identity (`user_id`) enforced; no `guest` fallback.
- [x] Conflict detection/resolution strategy present (`serverWins/clientWins/merge/manual`).
- [x] Legacy in-memory queue path formally removed/disabled as primary sync path.
- [x] Final documented P3 e2e regression protocol (reconnect + conflict + identity) marked complete.
  - Reference: `docs/P3_UNIFIED_OFFLINE_E2E_PROTOCOL.md`

## Manual QA critical flows (done/not done)

Status (2026-04-30): требуется ручной прогон на 2 сессиях/устройствах, автотестами не закрывается.
Update (2026-04-30): QA временно blocked на family chat send/upload до ретеста после client fallback fix (`APIService`) и проверки explicit backend chat router contract.

- [ ] Presence reconnect manual test on two devices/simulators.
- [ ] AI streaming resume manual test (background/foreground + network toggle).
- [ ] Magic-link full journey manual test (request email -> deep link consume -> session persisted).
- [ ] Sign in with Apple manual test (happy-path + canceled auth).
- [ ] Settings sync manual cross-screen consistency check (same account, multi-screen changes).

## P7 formal DoD (done/not done)

- [x] SyncEngine publishing contract documented and fixed as team rule.
  - Reference: `docs/P7_SYNCENGINE_PUBLISHING_RULES.md`
- [x] Domain mapping (`offline/familyChat/aiStreaming/family/settings/networkProtection`) unified in app runtime.
- [x] Review rule defined: new sync/API flow without `SyncEngine.publish(...)` is a blocker.
