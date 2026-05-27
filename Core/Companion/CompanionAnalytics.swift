import Foundation

/// P1-10 — Companion metrics N1–N6 (no message text / PII).
enum CompanionAnalyticsEvent: String {
    case open = "companion_open"
    case message = "companion_message"
    case voiceStart = "voice_start"
    case voiceEnd = "voice_end"
    case trustLevelUp = "trust_level_up"
    case policyBlocked = "policy_blocked"
}

enum CompanionAnalytics {
    static func track(
        _ event: CompanionAnalyticsEvent,
        characterId: String? = nil,
        sessionId: String? = nil,
        extra: [String: String] = [:]
    ) {
        var params: [String: Any] = ["event": event.rawValue]
        if let characterId, !characterId.isEmpty {
            params["character_id"] = characterId
        }
        if let sessionId, !sessionId.isEmpty {
            params["session_id"] = sessionId
        }
        for (k, v) in extra where !v.isEmpty {
            params[k] = v
        }
        AnalyticsManager.shared.trackEvent(event.rawValue, parameters: params)
        Task {
            await CompanionAPIService.shared.recordAnalyticsEvent(
                event: event.rawValue,
                characterId: characterId,
                sessionId: sessionId,
                extra: extra
            )
        }
    }
}
