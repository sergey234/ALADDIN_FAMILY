import Foundation

/// Classifies clipboard / pasted strings for Antifake Hub text tab routing.
enum AntifakeTextInputClassifier {

    enum PasteKind: Equatable {
        case url(String)
        case phone(String)
        case text(String)
    }

    static func classify(_ raw: String) -> PasteKind {
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return .text("") }

        if let url = extractURL(from: trimmed) {
            return .url(url)
        }
        if isLikelyPhone(trimmed) {
            return .phone(trimmed)
        }
        return .text(trimmed)
    }

    static func looksLikeURL(_ string: String) -> Bool {
        let lower = string.lowercased()
        if lower.hasPrefix("http://") || lower.hasPrefix("https://") { return true }
        if lower.hasPrefix("www.") { return true }
        if string.contains("://") { return true }
        // Common video / article hosts without scheme
        let hostPrefixes = ["youtube.com", "youtu.be", "vk.com", "t.me", "telegram.me", "instagram.com", "facebook.com", "fb.watch"]
        return hostPrefixes.contains { lower.contains($0) }
    }

    static func extractURL(from string: String) -> String? {
        let lines = string
            .components(separatedBy: .newlines)
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }

        if lines.count == 1, let single = lines.first, looksLikeURL(single) {
            return normalizeURL(single)
        }

        if let detector = try? NSDataDetector(types: NSTextCheckingResult.CheckingType.link.rawValue) {
            let range = NSRange(string.startIndex..<string.endIndex, in: string)
            let matches = detector.matches(in: string, options: [], range: range)
            if matches.count == 1, let match = matches.first, let url = match.url?.absoluteString {
                return url
            }
        }

        return nil
    }

    static func normalizeURL(_ string: String) -> String {
        let trimmed = string.trimmingCharacters(in: .whitespacesAndNewlines)
        let lower = trimmed.lowercased()
        if lower.hasPrefix("http://") || lower.hasPrefix("https://") {
            return trimmed
        }
        if lower.hasPrefix("www.") {
            return "https://\(trimmed)"
        }
        if looksLikeURL(trimmed) {
            return "https://\(trimmed)"
        }
        return trimmed
    }

    static func isLikelyPhone(_ string: String) -> Bool {
        let digitChars = string.filter { $0.isNumber }
        guard digitChars.count >= 7, digitChars.count <= 15 else { return false }
        let allowed = CharacterSet(charactersIn: "+-() .")
        let digitScalars = CharacterSet.decimalDigits
        let stripped = string.unicodeScalars.filter {
            $0.isASCII && (digitScalars.contains($0) || allowed.contains($0))
        }
        return stripped.count >= string.unicodeScalars.count - 2
    }

    static func composeContactCheckText(callerId: String, displayName: String, localizationManager: LocalizationManager) -> String {
        let callerLabel = localizationManager.localized("antifake_contact_caller_label")
        let nameLabel = localizationManager.localized("antifake_contact_name_label")
        var lines: [String] = []
        let cid = callerId.trimmingCharacters(in: .whitespacesAndNewlines)
        let name = displayName.trimmingCharacters(in: .whitespacesAndNewlines)
        if !cid.isEmpty { lines.append("\(callerLabel): \(cid)") }
        if !name.isEmpty { lines.append("\(nameLabel): \(name)") }
        return lines.joined(separator: "\n")
    }
}
