import Foundation

/// afhub-p0-01 — pick API `mode` for text antifake checks (sms unlocks scam floors).
enum AntifakeTextCheckModeResolver {
    /// Short chat / scam-like → sms; long article-like → news.
    static func apiMode(forText text: String, inputMode: AntifakeTextInputMode) -> String {
        switch inputMode {
        case .url:
            return "news" // unused for URL path
        case .contact:
            return "sms"
        case .text:
            return prefersSms(text) ? "sms" : "news"
        }
    }

    static func prefersSms(_ text: String) -> Bool {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.count <= 280 { return true }
        let lower = trimmed.lowercased()
        let scamHints = [
            "перевед", "срочно", "на карту", "скамер", "мошен", "сбп",
            "send money", "urgently", "to my card", "scammer", "otp", "transfer",
        ]
        return scamHints.contains { lower.contains($0) }
    }
}
