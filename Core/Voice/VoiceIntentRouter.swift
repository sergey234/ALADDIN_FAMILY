import Foundation

/// VSL-C P0 — deterministic voice intent from **leading** tokens only (no mid-sentence).
/// Full transcript is always preserved by callers; `remainder` is body after prefix.
enum VoiceIntentRouter {

    enum Intent: String, Equatable {
        case antifakeURL
        case securityCheck
        case incident
        case status
        case idea
        case remind
        case breakSegment
        case note
    }

    struct Result: Equatable {
        let intent: Intent
        /// Original user text (trimmed). Callers persist this as transcript.
        let fullTranscript: String
        /// Text after matched prefix (may be empty).
        let remainder: String
        /// Stable tag merged into VoiceNote.tags (never overwritten wholesale).
        var intentTag: String {
            switch intent {
            case .antifakeURL: return "intent_antifake_url"
            case .securityCheck: return "intent_security_check"
            case .incident: return "intent_incident"
            case .status: return "intent_status"
            case .idea: return "intent_idea"
            case .remind: return "intent_remind"
            case .breakSegment: return "intent_break"
            case .note: return "intent_note"
            }
        }

        var shouldOpenAntifake: Bool {
            intent == .antifakeURL || intent == .securityCheck
        }

        /// Body after prefix only (may be empty). Callers may fall back to clipboard.
        var antifakePrefill: String {
            remainder.trimmingCharacters(in: .whitespacesAndNewlines)
        }
    }

    /// Longest-match-first multi-word then single-word aliases (RU STT + EN).
    private static let multiWordPrefixes: [(tokens: [String], intent: Intent)] = [
        (["не", "забыть"], .remind),
        (["dont", "forget"], .remind),
        (["don't", "forget"], .remind),
        (["проверь", "ссылку"], .antifakeURL),
        (["проверка", "ссылки"], .antifakeURL),
        (["проверь", "ссылка"], .antifakeURL),
        (["check", "link"], .antifakeURL),
        (["check", "the", "link"], .antifakeURL),
    ]

    private static let singleWordAliases: [String: Intent] = [
        // antifake URL
        "ссылка": .antifakeURL,
        "сылка": .antifakeURL, // STT typo
        "линк": .antifakeURL,
        "link": .antifakeURL,
        "url": .antifakeURL,
        // security check
        "проверка": .securityCheck,
        "проверь": .securityCheck,
        "провери": .securityCheck, // STT
        "check": .securityCheck,
        // incident
        "тревога": .incident,
        "срочно": .incident,
        "alert": .incident,
        // status
        "статус": .status,
        "status": .status,
        // idea
        "идея": .idea,
        "idea": .idea,
        // remind (single)
        "напомни": .remind,
        "remind": .remind,
        "reminder": .remind,
        // break
        "перерыв": .breakSegment,
        "break": .breakSegment,
    ]

    static func parse(_ raw: String) -> Result {
        let full = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !full.isEmpty else {
            return Result(intent: .note, fullTranscript: "", remainder: "")
        }

        let tokens = tokenize(full)
        guard !tokens.isEmpty else {
            return Result(intent: .note, fullTranscript: full, remainder: full)
        }

        // Multi-word first (longest)
        for entry in multiWordPrefixes {
            let n = entry.tokens.count
            guard tokens.count >= n else { continue }
            let head = Array(tokens.prefix(n))
            if head == entry.tokens {
                let remainder = remainderAfter(tokenCount: n, original: full, tokens: tokens)
                return Result(intent: entry.intent, fullTranscript: full, remainder: remainder)
            }
        }

        let first = tokens[0]
        if let intent = singleWordAliases[first] {
            let remainder = remainderAfter(tokenCount: 1, original: full, tokens: tokens)
            return Result(intent: intent, fullTranscript: full, remainder: remainder)
        }

        return Result(intent: .note, fullTranscript: full, remainder: full)
    }

    // MARK: - Helpers

    private static func tokenize(_ text: String) -> [String] {
        let lowered = text.lowercased()
        let scalars = lowered.unicodeScalars.map { scalar -> Character in
            if CharacterSet.alphanumerics.contains(scalar) || scalar == "'" || scalar == "ё" || scalar == "’" {
                return Character(scalar)
            }
            // Keep letters; map punctuation/separators to space
            if CharacterSet.letters.contains(scalar) {
                return Character(scalar)
            }
            return " "
        }
        let normalized = String(scalars)
            .replacingOccurrences(of: "ё", with: "е")
            .replacingOccurrences(of: "’", with: "'")
        return normalized
            .split(whereSeparator: { $0.isWhitespace })
            .map(String.init)
            .filter { !$0.isEmpty }
    }

    /// Rebuild remainder from original string after skipping `tokenCount` leading tokens (best-effort).
    private static func remainderAfter(tokenCount: Int, original: String, tokens: [String]) -> String {
        guard tokenCount > 0, tokenCount < tokens.count else {
            return tokenCount >= tokens.count ? "" : original
        }
        // Walk original lowercase to find end of Nth token
        var searchFrom = original.startIndex
        let lowerOriginal = original.lowercased()
        for i in 0..<tokenCount {
            let needle = tokens[i]
            if let range = lowerOriginal.range(of: needle, range: searchFrom..<lowerOriginal.endIndex) {
                searchFrom = range.upperBound
            } else {
                // Fallback: join remaining tokens
                return tokens.dropFirst(tokenCount).joined(separator: " ")
            }
        }
        let sliced = String(original[searchFrom...])
        return sliced.trimmingCharacters(in: .whitespacesAndNewlines.union(.punctuationCharacters))
            .trimmingCharacters(in: .whitespacesAndNewlines)
    }
}
