import Foundation

/// Единая точка подготовки текста для облачного AI (E2.1): opt-in → XSS-sanitize → PII-redact.
enum AIOutboundTextGate {

    enum GateError: LocalizedError {
        case optInRequired

        var errorDescription: String? {
            switch self {
            case .optInRequired:
                return LocalizationManager.shared.localized("ai_error_consent_required")
            }
        }
    }

    struct PreparedMessage {
        /// Текст для пузыря в UI (без PII-redact, но после InputSanitizer).
        let displayText: String
        /// Текст для `/api/ai/*` после маскирования PII.
        let cloudText: String
        let redactionCount: Int
    }

    /// Полный пайплайн для пользовательского сообщения в AI-чат / stream.
    static func prepareUserMessage(_ raw: String) throws -> PreparedMessage {
        guard AppConfig.isAIDataSharingEnabled else {
            throw GateError.optInRequired
        }
        let sanitized = try InputSanitizer.shared.sanitizeMessage(raw)
        let redacted = AIPIIRedactor.redact(sanitized)
        return PreparedMessage(
            displayText: sanitized,
            cloudText: redacted.text,
            redactionCount: redacted.replacementCount
        )
    }

    /// Только PII-redact (без opt-in) — для feedback и прочих AI-эндпоинтов без LLM-промпта.
    static func redactOnly(_ raw: String) -> String {
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return trimmed }
        return AIPIIRedactor.redact(trimmed).text
    }

    /// Опциональная строка для API: redact + пусто → nil.
    static func redactOptional(_ raw: String?) -> String? {
        guard let raw else { return nil }
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return nil }
        return redactOnly(trimmed)
    }
}
