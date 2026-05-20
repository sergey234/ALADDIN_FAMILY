import Foundation

/// E1.5 — отображение и ограничения для legacy plaintext (envelope v1).
enum FamilyChatE2EULegacyPolicy {

    /// M4: не показывать текст legacy на сервере старше N дней.
    static let legacyPlaintextRedactDays: Int = 90

    static func envelopeVersion(from response: FamilyChatMessageResponse) -> Int {
        response.envelopeVersion ?? 1
    }

    static func isLegacyMessage(response: FamilyChatMessageResponse) -> Bool {
        if response.isLegacyPlaintext == true { return true }
        guard AppConfig.isFamilyChatE2EEEnabled else { return false }
        return envelopeVersion(from: response) == 1
    }

    static func isE2EEMessage(response: FamilyChatMessageResponse) -> Bool {
        envelopeVersion(from: response) == 2
    }

    static func decryptionFailed(response: FamilyChatMessageResponse, afterDecrypt text: String?) -> Bool {
        guard isE2EEMessage(response: response) else { return false }
        let hasCipher = !(response.ciphertext?.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ?? true)
        guard hasCipher else { return false }
        let t = text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        return t.isEmpty
    }

    static func parseMessageDate(_ timestamp: String) -> Date? {
        let formats = [
            "yyyy-MM-dd'T'HH:mm:ss",
            "yyyy-MM-dd'T'HH:mm:ss.SSS",
            "yyyy-MM-dd'T'HH:mm:ssZ",
            "yyyy-MM-dd'T'HH:mm:ss.SSSZ",
            "yyyy-MM-dd HH:mm:ss"
        ]
        for f in formats {
            let df = DateFormatter()
            df.locale = Locale(identifier: "en_US_POSIX")
            df.dateFormat = f
            if let d = df.date(from: timestamp) { return d }
        }
        return ISO8601DateFormatter().date(from: timestamp)
    }

    static func shouldRedactLegacyPlaintext(timestamp: String) -> Bool {
        guard let date = parseMessageDate(timestamp) else { return false }
        let cutoff = Calendar.current.date(byAdding: .day, value: -legacyPlaintextRedactDays, to: Date()) ?? Date.distantPast
        return date < cutoff
    }

    static func displayText(
        raw: String?,
        timestamp: String,
        isLegacy: Bool,
        decryptionFailed: Bool
    ) -> String? {
        if decryptionFailed { return nil }
        if isLegacy, shouldRedactLegacyPlaintext(timestamp: timestamp) { return nil }
        return raw
    }

    static func canEdit(message: FamilyChatMessage) -> Bool {
        message.isCurrentUser
            && message.messageType == .text
            && !message.isLegacyPlaintext
            && !message.isE2EEMessage
            && !message.decryptionFailed
    }
}
