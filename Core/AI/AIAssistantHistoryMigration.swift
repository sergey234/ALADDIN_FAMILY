import Foundation

/// ai-ios-history-migrate: UserDefaults v2, purge demo seed / stale v1 blobs.
enum AIAssistantHistoryMigration {
    static let storageKey = "ai_assistant_messages_list_v2"
    private static let legacyKey = "ai_assistant_messages_list"
    private static let schemaKey = "ai_assistant_history_schema_version"
    static let currentSchemaVersion = 2

    private static let demoSubstrings = [
        "в разработке",
        "демо-режим",
        "ai_chat_seed",
        "47 угроз",
        "заблокировано 47",
    ]

    static func load<T: Decodable>(_ type: T.Type) -> T? {
        runMigrationIfNeeded()
        guard let data = UserDefaults.standard.data(forKey: storageKey) else { return nil }
        return try? JSONDecoder().decode(type, from: data)
    }

    static func save<T: Encodable>(_ value: T) {
        guard let encoded = try? JSONEncoder().encode(value) else { return }
        UserDefaults.standard.set(encoded, forKey: storageKey)
        UserDefaults.standard.set(currentSchemaVersion, forKey: schemaKey)
    }

    private static func runMigrationIfNeeded() {
        let version = UserDefaults.standard.integer(forKey: schemaKey)
        guard version < currentSchemaVersion else { return }

        if let legacy = UserDefaults.standard.data(forKey: legacyKey) {
            UserDefaults.standard.set(legacy, forKey: storageKey)
            UserDefaults.standard.removeObject(forKey: legacyKey)
        }

        UserDefaults.standard.set(currentSchemaVersion, forKey: schemaKey)
    }

    static func isDemoOrSeedMessage(_ text: String) -> Bool {
        let lower = text.lowercased()
        return demoSubstrings.contains { lower.contains($0) }
    }
}

// MARK: - Hermes stderr filter (user-facing replies)

enum AIAssistantResponseSanitizer {
    struct Result {
        let displayText: String
        let strippedTechnicalNoise: Bool
    }

    private static let dropSubstrings = [
        "no auxiliary llm",
        "context compression",
        "openrouter_api_key",
        "hermes setup",
        "prompt tokens limit",
        "http 402",
        "http 429",
    ]

    /// Markdown headings that are raw localization keys (e.g. `### family_chat_e2ee_decrypt_failed`).
    private static let markdownKeyHeading = try! NSRegularExpression(
        pattern: #"^#{1,6}\s*([a-z][a-z0-9_]{2,80})\s*$"#,
        options: [.anchorsMatchLines]
    )

    static func sanitize(_ raw: String) -> Result {
        var droppedNoise = false
        let L = LocalizationManager.shared
        let rawLines = raw.components(separatedBy: .newlines)
        var kept: [String] = []
        var index = 0
        while index < rawLines.count {
            let t = rawLines[index].trimmingCharacters(in: .whitespacesAndNewlines)
            index += 1
            if t.isEmpty { continue }
            if t.hasPrefix("session_id:") { droppedNoise = true; continue }
            if t.hasPrefix("⚠") || t.hasPrefix("Warning:") { droppedNoise = true; continue }
            let low = t.lowercased()
            if dropSubstrings.contains(where: { low.contains($0) }) {
                droppedNoise = true
                continue
            }
            // A `### loc_key` line is a key, not a second sentence.
            // If the handbook already has the sentence underneath, keep that once.
            if localizationKeyHeading(in: t) != nil {
                droppedNoise = true
                if nextContentLine(in: rawLines, from: index) != nil {
                    continue
                }
                if let key = localizationKeyHeading(in: t) {
                    let localized = L.localized(key)
                    if localized != key {
                        kept.append(localized)
                    }
                }
                continue
            }
            if t.range(of: #"^[a-z][a-z0-9_]{2,80}$"#, options: .regularExpression) != nil {
                let localized = L.localized(t)
                if localized != t {
                    droppedNoise = true
                    if nextContentLine(in: rawLines, from: index) == localized {
                        continue
                    }
                    kept.append(localized)
                    continue
                }
            }
            kept.append(t)
        }
        let cleaned = kept.joined(separator: "\n").trimmingCharacters(in: .whitespacesAndNewlines)
        if !cleaned.isEmpty {
            return Result(displayText: cleaned, strippedTechnicalNoise: droppedNoise)
        }
        let fallback = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        return Result(displayText: fallback, strippedTechnicalNoise: droppedNoise || !fallback.isEmpty)
    }

    static func userFacingText(from raw: String) -> String {
        sanitize(raw).displayText
    }

    private static func localizationKeyHeading(in line: String) -> String? {
        let ns = line as NSString
        let full = NSRange(location: 0, length: ns.length)
        guard let match = markdownKeyHeading.firstMatch(in: line, options: [], range: full),
              match.numberOfRanges >= 2 else {
            return nil
        }
        return ns.substring(with: match.range(at: 1))
    }

    private static func nextContentLine(in lines: [String], from index: Int) -> String? {
        var cursor = index
        while cursor < lines.count {
            let trimmed = lines[cursor].trimmingCharacters(in: .whitespacesAndNewlines)
            if !trimmed.isEmpty {
                return trimmed
            }
            cursor += 1
        }
        return nil
    }
}
