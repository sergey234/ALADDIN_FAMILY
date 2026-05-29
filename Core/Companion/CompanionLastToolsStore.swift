import Foundation

/// Sprint 5.6 — последние `tools_used` с бэкенда для родителя в «Моё».
enum CompanionLastToolsStore {
    private static let key = "companion_last_tools_used"

    static func save(_ tools: [String]?) {
        let cleaned = (tools ?? []).map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
        guard !cleaned.isEmpty else { return }
        UserDefaults.standard.set(cleaned.joined(separator: ", "), forKey: key)
    }

    static var displayLine: String {
        UserDefaults.standard.string(forKey: key) ?? ""
    }
}
