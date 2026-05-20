import Foundation

/// E2.1 — локальное маскирование PII перед отправкой текста в облачный AI-канал.
/// Не используется для Family Chat E2EE (там ciphertext на устройстве).
enum AIPIIRedactor {

    struct Result {
        let text: String
        let replacementCount: Int
    }

    /// Маскирует известные классы PII. Порядок правил важен (длинные токены раньше коротких цифр).
    static func redact(_ input: String) -> Result {
        let capped = input.count > 16_000 ? String(input.prefix(16_000)) : input
        var text = capped
        var count = 0

        func apply(_ pattern: String, options: NSRegularExpression.Options = [], placeholder: String) {
            guard let regex = try? NSRegularExpression(pattern: pattern, options: options) else { return }
            let matches = regex.matches(in: text, range: NSRange(text.startIndex..., in: text))
            guard !matches.isEmpty else { return }
            count += matches.count
            for match in matches.reversed() {
                guard let range = Range(match.range, in: text) else { continue }
                text.replaceSubrange(range, with: placeholder)
            }
        }

        // JWT / session-like tokens
        apply(#"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"#, placeholder: "[REDACTED_JWT]")

        // Bearer / API keys in free text
        apply(#"(?i)\b(?:bearer|api[_-]?key|client[_-]?secret|access[_-]?token)\s*[:=]\s*[A-Za-z0-9._\-]{8,}\b"#, placeholder: "[REDACTED_SECRET]")

        // Email
        apply(#"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"#, placeholder: "[REDACTED_EMAIL]")

        // Credit cards (Visa/MC/Amex/Discover) with optional separators
        apply(#"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b"#, placeholder: "[REDACTED_CARD]")
        apply(#"\b(?:\d{4}[\s\-]?){3}\d{4}\b"#, placeholder: "[REDACTED_CARD]")

        // RU SNILS (только с разделителями)
        apply(#"\b\d{3}-\d{3}-\d{3}[\s-]\d{2}\b"#, placeholder: "[REDACTED_SNILS]")

        // RU passport: 4 цифры серии + 6 цифр номера
        apply(#"\b\d{4}[\s-]\d{6}\b"#, placeholder: "[REDACTED_PASSPORT]")

        // INN с явной меткой
        apply(#"(?i)\b(?:инн|inn)\s*[:#]?\s*\d{10}(?:\d{2})?\b"#, placeholder: "[REDACTED_INN]")

        // Phones: +7 / 8 RU and international E.164-ish
        apply(#"(?:\+7|8)[\s\-\(]?(?:\d[\s\-\(]?){10}"#, placeholder: "[REDACTED_PHONE]")
        apply(#"\+\d{1,3}[\s\-\(]?(?:\d[\s\-\(]?){7,14}\d"#, placeholder: "[REDACTED_PHONE]")

        // IPv4
        apply(#"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\b"#, placeholder: "[REDACTED_IP]")

        // Password / PIN hints in key=value form
        apply(#"(?i)\b(?:password|passwd|pwd|pin|cvv|secret)\s*[:=]\s*\S+"#, placeholder: "[REDACTED_PASSWORD]")

        // Long hex blobs (likely keys)
        apply(#"\b[a-fA-F0-9]{32,}\b"#, placeholder: "[REDACTED_KEY]")

        return Result(text: text, replacementCount: count)
    }
}
