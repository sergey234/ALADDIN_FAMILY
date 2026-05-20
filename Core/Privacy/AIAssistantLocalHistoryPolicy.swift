import Foundation

/// E2.4 hybrid D — полная история AI только на устройстве, 90 дней.
enum AIAssistantLocalHistoryPolicy {
    static let retentionDays = 90

    static func purgeIfNeeded(storedAt: Date) -> Bool {
        guard let cutoff = Calendar.current.date(byAdding: .day, value: -retentionDays, to: Date()) else {
            return true
        }
        return storedAt >= cutoff
    }
}
