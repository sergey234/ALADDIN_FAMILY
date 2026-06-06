import Foundation

/// Ten mnemo techniques × four mastery stages (awareness → practice → fluent → master).
final class MnemonicTechniqueMastery {
    static let shared = MnemonicTechniqueMastery()

    enum Stage: Int, CaseIterable, Codable {
        case awareness = 0
        case practice = 1
        case fluent = 2
        case master = 3

        var localizationKey: String {
            switch self {
            case .awareness: return "child_mnemo_technique_stage_awareness"
            case .practice: return "child_mnemo_technique_stage_practice"
            case .fluent: return "child_mnemo_technique_stage_fluent"
            case .master: return "child_mnemo_technique_stage_master"
            }
        }
    }

    private static let stageThresholds = [1, 5, 15, 30]

    private let defaults: UserDefaults
    private let storageKey = "child.mnemo.technique.mastery.v1"

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    func successCount(for technique: MnemonicTechnique, childId: String? = nil) -> Int {
        loadCounts(childId: childId)[technique.rawValue] ?? 0
    }

    func stage(for technique: MnemonicTechnique, childId: String? = nil) -> Stage {
        let count = successCount(for: technique, childId: childId)
        if count >= Self.stageThresholds[3] { return .master }
        if count >= Self.stageThresholds[2] { return .fluent }
        if count >= Self.stageThresholds[1] { return .practice }
        if count >= Self.stageThresholds[0] { return .awareness }
        return .awareness
    }

    func recordSuccess(technique: MnemonicTechnique, childId: String? = nil) {
        var counts = loadCounts(childId: childId)
        counts[technique.rawValue] = (counts[technique.rawValue] ?? 0) + 1
        persist(counts, childId: childId)
    }

    func masterySummary(childId: String? = nil) -> [(technique: MnemonicTechnique, stage: Stage, count: Int)] {
        MnemonicTechnique.allCases.map { technique in
            (
                technique: technique,
                stage: stage(for: technique, childId: childId),
                count: successCount(for: technique, childId: childId)
            )
        }
    }

    private func loadCounts(childId: String?) -> [String: Int] {
        let key = resolvedKey(childId: childId)
        guard let data = defaults.data(forKey: key),
              let decoded = try? JSONDecoder().decode([String: Int].self, from: data)
        else { return [:] }
        return decoded
    }

    private func persist(_ counts: [String: Int], childId: String?) {
        let key = resolvedKey(childId: childId)
        if let data = try? JSONEncoder().encode(counts) {
            defaults.set(data, forKey: key)
        }
    }

    private func resolvedKey(childId: String?) -> String {
        let sid = (childId ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        guard !sid.isEmpty else { return "\(storageKey).global" }
        return "\(storageKey).\(sid)"
    }
}
