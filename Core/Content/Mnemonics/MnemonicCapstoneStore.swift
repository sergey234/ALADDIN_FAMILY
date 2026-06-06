import Foundation

/// study.26 capstone — preset topic + teach-back completion (B12-T05). No free-text PII.
final class MnemonicCapstoneStore {
    static let shared = MnemonicCapstoneStore()

    static let itemId = "study.26"
    static let teachBackDurationSeconds = 180
    static let minimumTeachBackSeconds = 30

    static let topicLocalizationKeys: [String] = (1...6).map {
        "child_mnemo_capstone_topic_\($0)"
    }

    struct CapstoneRecord: Codable, Equatable {
        let topicIndex: Int
        let teachBackSeconds: Int
        let completedAt: Date
    }

    private let defaults: UserDefaults
    private let storageKeyPrefix = "child.mnemo.capstone.v1"

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    func hasCompleted(childId: String? = nil) -> Bool {
        loadRecord(childId: childId) != nil
    }

    func record(childId: String? = nil) -> CapstoneRecord? {
        loadRecord(childId: childId)
    }

    @discardableResult
    func recordCompletion(
        topicIndex: Int,
        teachBackSeconds: Int,
        childId: String? = nil,
        completedAt: Date = Date()
    ) -> CapstoneRecord {
        let clampedTopic = min(max(0, topicIndex), Self.topicLocalizationKeys.count - 1)
        let record = CapstoneRecord(
            topicIndex: clampedTopic,
            teachBackSeconds: max(0, teachBackSeconds),
            completedAt: completedAt
        )
        let key = storageKey(childId: childId)
        guard let data = try? JSONEncoder().encode(record) else { return record }
        defaults.set(data, forKey: key)
        MasterLogger.shared.business(
            "MNEMO-B12 capstone completed topicIndex=\(clampedTopic) teachBackSec=\(record.teachBackSeconds)"
        )
        return record
    }

    private func storageKey(childId: String?) -> String {
        let scope = resolvedChildScope(childId)
        return "\(storageKeyPrefix).\(scope)"
    }

    private func resolvedChildScope(_ childId: String?) -> String {
        let trimmed = (childId ?? MnemonicBaselineAssessment.activeChildId())
            .trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty { return "default" }
        return trimmed
    }

    private func loadRecord(childId: String?) -> CapstoneRecord? {
        let key = storageKey(childId: childId)
        guard let data = defaults.data(forKey: key),
              let record = try? JSONDecoder().decode(CapstoneRecord.self, from: data) else {
            return nil
        }
        return record
    }
}
