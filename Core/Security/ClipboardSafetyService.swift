import Foundation

/// VSL-C P0 — on-demand clipboard sanitize + secret gate (no history, no background observer).
enum ClipboardSafetyService {

    enum SecretKind: String, Equatable {
        case otp
        case authToken
        case apiKey
        case paymentCard
        case seedPhrase
    }

    enum Outcome: Equatable {
        case ok(String)
        case blockedSecret(SecretKind)
    }

    private static let trackingQueryKeys: Set<String> = [
        "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id",
        "fbclid", "gclid", "mc_cid", "mc_eid", "igshid", "si", "feature"
    ]

    static func process(_ raw: String) -> Outcome {
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return .ok("") }

        if let secret = detectSecret(trimmed) {
            return .blockedSecret(secret)
        }

        // C-2: never pass raw `trimmed` into normalizeURL when extractURL fails
        // (looksLikeURL alone is not enough — that path leaked unsanitized text).
        if let extracted = AntifakeTextInputClassifier.extractURL(from: trimmed) {
            let normalized = AntifakeTextInputClassifier.normalizeURL(extracted)
            return .ok(stripTrackingParams(from: normalized))
        }

        return .ok(trimmed)
    }

    // MARK: - Sanitize

    static func stripTrackingParams(from urlString: String) -> String {
        guard var components = URLComponents(string: urlString) else { return urlString }
        guard let items = components.queryItems, !items.isEmpty else { return urlString }
        let filtered = items.filter { item in
            !trackingQueryKeys.contains(item.name.lowercased())
        }
        components.queryItems = filtered.isEmpty ? nil : filtered
        return components.string ?? urlString
    }

    // MARK: - Secrets

    static func detectSecret(_ text: String) -> SecretKind? {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        let lower = trimmed.lowercased()

        if lower.hasPrefix("bearer ") || lower.contains("bearer eyj") {
            return .authToken
        }
        if lower.hasPrefix("sk-") && trimmed.count >= 20 {
            return .apiKey
        }
        if lower.hasPrefix("eyj"), trimmed.split(separator: ".").count >= 3 {
            return .authToken
        }

        // Phone numbers are valid Antifake input — never treat as OTP.
        if AntifakeTextInputClassifier.isLikelyPhone(trimmed) {
            return nil
        }

        let digitsOnly = trimmed.filter(\.isNumber)
        if digitsOnly.count == trimmed.count,
           digitsOnly.count >= 4,
           digitsOnly.count <= 8 {
            return .otp
        }

        if looksLikePaymentCard(trimmed) {
            return .paymentCard
        }

        let words = trimmed.split(whereSeparator: { $0.isWhitespace }).map(String.init)
        if words.count == 12 || words.count == 24 {
            let alpha = words.allSatisfy { w in
                w.count >= 3 && w.unicodeScalars.allSatisfy { CharacterSet.letters.contains($0) }
            }
            if alpha { return .seedPhrase }
        }

        return nil
    }

    private static func looksLikePaymentCard(_ text: String) -> Bool {
        let digits = text.filter(\.isNumber)
        guard digits.count >= 13, digits.count <= 19 else { return false }
        // Reject if looks like phone with separators already handled above
        return luhnValid(digits)
    }

    private static func luhnValid(_ digits: String) -> Bool {
        var sum = 0
        let reversed = digits.reversed().map { Int(String($0)) ?? 0 }
        for (idx, d) in reversed.enumerated() {
            if idx % 2 == 1 {
                let doubled = d * 2
                sum += doubled > 9 ? doubled - 9 : doubled
            } else {
                sum += d
            }
        }
        return sum % 10 == 0
    }
}
