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

    static func sanitize(_ raw: String) -> Result {
        var droppedNoise = false
        let lines = raw.components(separatedBy: .newlines).filter { line in
            let t = line.trimmingCharacters(in: .whitespacesAndNewlines)
            if t.isEmpty { return false }
            if t.hasPrefix("session_id:") { droppedNoise = true; return false }
            if t.hasPrefix("⚠") || t.hasPrefix("Warning:") { droppedNoise = true; return false }
            let low = t.lowercased()
            if dropSubstrings.contains(where: { low.contains($0) }) {
                droppedNoise = true
                return false
            }
            return true
        }
        let cleaned = lines.joined(separator: "\n").trimmingCharacters(in: .whitespacesAndNewlines)
        if !cleaned.isEmpty {
            return Result(displayText: cleaned, strippedTechnicalNoise: droppedNoise)
        }
        let fallback = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        return Result(displayText: fallback, strippedTechnicalNoise: droppedNoise || !fallback.isEmpty)
    }

    static func userFacingText(from raw: String) -> String {
        sanitize(raw).displayText
    }
}
