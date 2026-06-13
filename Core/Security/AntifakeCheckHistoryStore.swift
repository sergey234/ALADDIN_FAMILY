import Foundation

/// Local history of last antifake checks (af-6-08 / af-m3).
struct AntifakeCheckHistoryEntry: Codable, Identifiable, Equatable {
    let id: UUID
    let kind: String
    let summary: String
    let verdict: String
    let checkedAt: Date

    init(id: UUID = UUID(), kind: String, summary: String, verdict: String, checkedAt: Date = Date()) {
        self.id = id
        self.kind = kind
        self.summary = summary
        self.verdict = verdict
        self.checkedAt = checkedAt
    }
}

enum AntifakeCheckHistoryStore {
    private static let storageKey = "antifake_check_history_v1"
    private static let maxEntries = 50

    static func load() -> [AntifakeCheckHistoryEntry] {
        guard let data = UserDefaults.standard.data(forKey: storageKey),
              let list = try? JSONDecoder().decode([AntifakeCheckHistoryEntry].self, from: data)
        else { return [] }
        return list
    }

    static func append(kind: String, summary: String, verdict: String) {
        let trimmed = summary.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        var entries = load()
        entries.insert(
            AntifakeCheckHistoryEntry(kind: kind, summary: trimmed, verdict: verdict),
            at: 0
        )
        if entries.count > maxEntries {
            entries = Array(entries.prefix(maxEntries))
        }
        persist(entries)
    }

    static func clear() {
        UserDefaults.standard.removeObject(forKey: storageKey)
    }

    private static func persist(_ entries: [AntifakeCheckHistoryEntry]) {
        guard let data = try? JSONEncoder().encode(entries) else { return }
        UserDefaults.standard.set(data, forKey: storageKey)
    }
}
