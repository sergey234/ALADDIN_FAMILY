import Foundation

/// P1-18 — понятные сообщения об ошибках companion (429 usage / rate limit).
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
