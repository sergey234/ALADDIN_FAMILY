# ADR P1-16: Companion hot path — chat / stream / voice

**Status:** Accepted (2026-05-29)  
**Scope:** ALADDIN Family iOS + `security/api/routers/ai_companion_router.py`

## Context

Companion needs low-latency dialogue (text stream + voice) with shared safety (policy, ethics, trust).  
A future **orchestrator** (P2-02) may route all AI traffic; today production uses a **direct hot path** through companion routers.

## Decision

| Path | Entry | Backend handler | Notes |
|------|--------|-----------------|-------|
| Text chat | `POST /api/ai/companion/chat` | `companion_chat` → `ai_assistant_chat` | Full turn + trust + memory |
| Text stream | `POST /api/ai/companion/stream` | `companion_stream` → `companion_chat` + token cache | Resume via `resumeFromIndex` |
| Voice | `WS /api/ai/voice/realtime` | `audio.stop` + transcript → `run_companion_voice_turn` → `companion_chat` | On-device STT; TTS on client |
| Capabilities | `GET /api/ai/companion/capabilities` | JWT + parental consent | iOS `CompanionCapabilitiesService` |

**Safety stack (unchanged):**

1. Pre-LLM: PII redact, `evaluate_request_policy`, `evaluate_companion_ethics`, age_band character filter  
2. LLM: `ai_assistant_chat` (no mock in prod)  
3. Post-LLM: `moderate_companion_assistant_text` (P1-22)

## Consequences

- **Pros:** Single code path for chat/voice/stream; easier QA and moderation.  
- **Cons:** Companion traffic not yet unified under orchestrator feature flag.  
- **Migration (P2-02):** Replace `ai_assistant_chat` call with orchestrator client behind flag; keep wire contracts stable for iOS.

## References

- `security/api/routers/ai_companion_router.py` — `@router.post("/chat")`, `@router.post("/stream")`  
- `security/services/ai_platform/companion_voice_turn.py`  
- `security/api/routers/ai_voice_ws_router.py`  
- iOS: `CompanionAPIService`, `CompanionStreamingService`, `CompanionVoiceSession`
