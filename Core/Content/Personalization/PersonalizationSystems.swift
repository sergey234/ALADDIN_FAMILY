import Foundation

enum DifficultyLevel: String, Codable {
    case easy
    case medium
    case hard
}

struct ContentRecommendation: Identifiable, Hashable, Sendable {
    let id: String
    let item: ContentItem
    let interestScore: Int
    let progressScore: Int
    let difficulty: DifficultyLevel
    let reasons: [String]
}

final class InterestAnalyzer {
    static let shared = InterestAnalyzer()

    private let defaults = UserDefaults.standard
    private let keyPrefix = "content.personalization.interests.v2"

    private init() {}

    func recordInteraction(item: ContentItem, childId: String? = nil) {
        var weights = readWeights(childId: childId)
        weights["type.\(item.type.rawValue)", default: 0] += 1
        for tag in item.metadata.tags {
            weights["tag.\(tag)", default: 0] += 1
        }
        writeWeights(weights, childId: childId)
    }

    func score(item: ContentItem, childId: String? = nil) -> Int {
        let weights = readWeights(childId: childId)
        var result = weights["type.\(item.type.rawValue)", default: 0]
        for tag in item.metadata.tags {
            result += weights["tag.\(tag)", default: 0]
        }
        return result
    }

    private func resolvedKey(childId: String?) -> String {
        let sid = (childId ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        guard !sid.isEmpty else { return "\(keyPrefix).global" }
        return "\(keyPrefix).\(sid)"
    }

    private func readWeights(childId: String?) -> [String: Int] {
        let key = resolvedKey(childId: childId)
        guard let data = defaults.data(forKey: key),
              let decoded = try? JSONDecoder().decode([String: Int].self, from: data) else {
            return [:]
        }
        return decoded
    }

    private func writeWeights(_ weights: [String: Int], childId: String?) {
        let key = resolvedKey(childId: childId)
        guard let encoded = try? JSONEncoder().encode(weights) else { return }
        defaults.set(encoded, forKey: key)
    }
}

final class DifficultyAdapter {
    static let shared = DifficultyAdapter()

    private init() {}

    func difficulty(for item: ContentItem, progress: ContentProgress?) -> DifficultyLevel {
        guard let progress else { return .easy }
        if progress.completionPercent >= 100 && progress.attempts <= 2 {
            return .hard
        }
        if progress.completionPercent >= 65 || progress.attempts >= 3 {
            return .medium
        }
        return .easy
    }

    func progressScore(for progress: ContentProgress?) -> Int {
        guard let progress else { return 15 }
        let completion = Int(progress.completionPercent.rounded())
        if completion >= 100 { return -20 } // prefer not-yet-completed content
        if completion >= 70 { return 12 }
        if completion >= 30 { return 20 }
        return 28 // prioritize starting unfinished items
    }
}

final class LearningPathGenerator {
    static let shared = LearningPathGenerator()

    private init() {}

    func orderedPath(items: [ContentItem], progressById: [String: ContentProgress]) -> [ContentItem] {
        items.sorted { lhs, rhs in
            let ld = DifficultyAdapter.shared.difficulty(for: lhs, progress: progressById[lhs.id])
            let rd = DifficultyAdapter.shared.difficulty(for: rhs, progress: progressById[rhs.id])
            if ld == rd {
                // In same difficulty bucket, unfinished first.
                let lp = progressById[lhs.id]?.completionPercent ?? 0
                let rp = progressById[rhs.id]?.completionPercent ?? 0
                if lp == rp {
                    return lhs.metadata.title < rhs.metadata.title
                }
                return lp < rp
            }
            return weight(ld) < weight(rd)
        }
    }

    private func weight(_ level: DifficultyLevel) -> Int {
        switch level {
        case .easy: return 0
        case .medium: return 1
        case .hard: return 2
        }
    }
}

final class ContentRecommender {
    static let shared = ContentRecommender()

    private init() {}

    func rank(items: [ContentItem], progressById: [String: ContentProgress], childId: String? = nil) -> [ContentItem] {
        recommendations(items: items, progressById: progressById, childId: childId).map(\.item)
    }

    func recommendations(items: [ContentItem], progressById: [String: ContentProgress], childId: String? = nil) -> [ContentRecommendation] {
        let learningPath = LearningPathGenerator.shared.orderedPath(items: items, progressById: progressById)
        var mapped: [ContentRecommendation] = learningPath.map { item in
            let progress = progressById[item.id]
            let interest = InterestAnalyzer.shared.score(item: item, childId: childId)
            let progressScore = DifficultyAdapter.shared.progressScore(for: progress)
            let difficulty = DifficultyAdapter.shared.difficulty(for: item, progress: progress)
            var reasons: [String] = []
            if interest > 0 { reasons.append("interest_match") }
            if (progress?.completionPercent ?? 0) < 100 { reasons.append("unfinished_content") }
            reasons.append("difficulty_\(difficulty.rawValue)")
            return ContentRecommendation(
                id: item.id,
                item: item,
                interestScore: interest,
                progressScore: progressScore,
                difficulty: difficulty,
                reasons: reasons
            )
        }
        mapped.sort { lhs, rhs in
            let lTotal = lhs.interestScore + lhs.progressScore
            let rTotal = rhs.interestScore + rhs.progressScore
            if lTotal == rTotal {
                return lhs.item.metadata.title < rhs.item.metadata.title
            }
            return lTotal > rTotal
        }
        return mapped
    }
}

