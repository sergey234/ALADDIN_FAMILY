import CryptoKit
import Foundation

/// N-02 — PII-safe phone handling on device (matches server `phone_log_hash`).
enum AntifakePhonePrivacy {
    static func phoneLogHash(_ phone: String) -> String {
        let digits = phone.filter(\.isNumber)
        guard !digits.isEmpty else { return "empty" }
        let digest = SHA256.hash(data: Data(digits.utf8))
        return String(digest.map { String(format: "%02x", $0) }.joined().prefix(16))
    }

    /// Redact phone-like substrings before persisting local history summaries.
    static func redactPhonesInText(_ text: String) -> String {
        let pattern = #"(?:(?:\+|00)\d{1,3}[\s\-()]*)?(?:\(?\d{2,4}\)?[\s\-]*)?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}"#
        guard let regex = try? NSRegularExpression(pattern: pattern) else { return text }
        let range = NSRange(text.startIndex..<text.endIndex, in: text)
        return regex.stringByReplacingMatches(in: text, range: range, withTemplate: "[phone]")
    }
}
