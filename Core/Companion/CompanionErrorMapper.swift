import Foundation

/// P1-18 — понятные сообщения об ошибках companion (429 usage / rate limit / 409).
enum CompanionErrorMapper {
    static func message(for error: Error, localizationManager: LocalizationManager) -> String {
        if let gate = error as? AIOutboundTextGate.GateError {
            return gate.errorDescription ?? localizationManager.localized("companion_conversation_send_failed")
        }

        let stream = error as NSError
        if stream.domain == "CompanionStream", stream.code == 404 {
            return localizationManager.localized("companion_conversation_send_failed")
        }

        let networkError = NetworkError.from(error)
        if case .tooManyRequests(let detail) = networkError {
            return rateLimitMessage(detail: detail, localizationManager: localizationManager)
        }
        if case .httpError(429) = networkError {
            return localizationManager.localized("companion_error_rate_limit")
        }
        if case .conflict = networkError {
            return localizationManager.localized("companion_error_conflict")
        }
        if case .httpError(409) = networkError {
            return localizationManager.localized("companion_error_conflict")
        }
        // W4: never show raw HTTP 504 / gateway codes in companion UI.
        if case .httpError(let code) = networkError, [502, 503, 504].contains(code) {
            return localizationManager.localized("companion_error_hero_unavailable")
        }
        if case .timeout = networkError {
            return localizationManager.localized("companion_error_hero_unavailable")
        }
        let raw = (networkError.localizedDescription ?? error.localizedDescription).lowercased()
        if raw.contains("409") || raw.contains("conflict") {
            return localizationManager.localized("companion_error_conflict")
        }
        if raw.contains("504") || raw.contains("502") || raw.contains("503")
            || raw.contains("gateway") || raw.contains("timed out") || raw.contains("timeout") {
            return localizationManager.localized("companion_error_hero_unavailable")
        }
        if raw.contains("http ") || raw.contains("status code") {
            return localizationManager.localized("companion_error_hero_unavailable")
        }

        return networkError.localizedDescription ?? error.localizedDescription
    }

    private static func rateLimitMessage(detail: String?, localizationManager: LocalizationManager) -> String {
        let lowered = (detail ?? "").lowercased()
        if lowered.contains("usage") || (lowered.contains("message") && lowered.contains("limit")) {
            return localizationManager.localized("companion_error_usage_limit")
        }
        if lowered.contains("voice") && lowered.contains("limit") {
            return localizationManager.localized("companion_error_voice_limit")
        }
        if lowered.contains("rate limit") || lowered.contains("rate_limit") {
            return localizationManager.localized("companion_error_rate_limit")
        }
        return localizationManager.localized("ai_error_rate_limit")
    }
}
