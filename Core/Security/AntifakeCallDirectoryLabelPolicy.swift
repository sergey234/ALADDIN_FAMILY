import Foundation

/// fws-06 — D-10 relocalize server/default scam labels when user changes device locale.
enum AntifakeCallDirectoryLabelPolicy {
    static let voiceFraudSentinel = "__voice_fraud__"

    private static let knownDefaultLabels: Set<String> = [
        "Возможный мошенник?",
        "Possible scam?"
    ]

    private static let knownVoiceLabels: Set<String> = [
        voiceFraudSentinel,
        "Подозрение на ИИ-голос?",
        "Possible AI voice scam?"
    ]

    static func relocalizeIfKnownDefault(_ label: String, currentDefault: String) -> String {
        let trimmed = label.trimmingCharacters(in: .whitespacesAndNewlines)
        guard knownDefaultLabels.contains(trimmed) else { return label }
        return currentDefault
    }

    static func resolvedLabel(
        _ raw: String?,
        defaultLabel: String,
        voiceLabel: String
    ) -> String {
        let trimmed = (raw ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty { return defaultLabel }
        if knownVoiceLabels.contains(trimmed) { return voiceLabel }
        return relocalizeIfKnownDefault(trimmed, currentDefault: defaultLabel)
    }
}
