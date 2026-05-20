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
