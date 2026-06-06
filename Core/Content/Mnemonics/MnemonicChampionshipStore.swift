import Foundation

/// Junior Memory Championship-style drill: 20 journey pegs / 5 min study → ordered recall (B12-T06).
/// Personal best only — no leaderboard (ALADDIN safety).
final class MnemonicChampionshipStore {
    static let shared = MnemonicChampionshipStore()

    static let itemId = "games.05"
    static let itemCount = 20
    static let timeLimitSeconds = 300
    static let unlockSemesterIndex = 6

    static let journeyPegEmojis: [String] = [
        "🐱", "🌟", "🎈", "🚗", "🦄", "📚", "🎵", "⚽", "🌙", "🍎",
        "🦋", "🚀", "🌈", "🎁", "🔑", "🌊", "🎨", "🍀", "🦊", "🎪"
    ]

    struct SessionResult: Codable, Equatable {
        let correctCount: Int
        let itemCount: Int
        let elapsedStudySeconds: Int
        let completedAt: Date
        let isPersonalBest: Bool
    }

    private struct PersistedRecord: Codable, Equatable {
        var personalBestCount: Int
        var sessions: [SessionResult]
    }

    private let defaults: UserDefaults
    private let storageKeyPrefix = "child.mnemo.championship.v1"

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    #if DEBUG
    static var uiTestForceUnlock: Bool {
        ProcessInfo.processInfo.arguments.contains("-UITestMnemoChampionship")
    }
    #else
    static let uiTestForceUnlock = false
    #endif

    func isUnlocked(childId: String? = nil, now: Date = Date()) -> Bool {
        if Self.uiTestForceUnlock { return true }
        let tracker = MnemonicSkillTracker(defaults: defaults)
        if tracker.hasCompletedCapstone(childId: childId) { return true }
        if tracker.currentLevel(childId: childId) == .champion { return true }
        let spine = MnemonicCurriculumSpine(defaults: defaults)
        return spine.activeSemesterIndex(childId: childId, now: now) >= Self.unlockSemesterIndex
    }

    func personalBest(childId: String? = nil) -> Int {
        loadRecord(childId: childId)?.personalBestCount ?? 0
    }

    func latestResult(childId: String? = nil) -> SessionResult? {
        loadRecord(childId: childId)?.sessions.last
    }

    func makeSequence(seed: UInt64? = nil) -> [Int] {
        var indices = Array(0..<Self.itemCount)
        var generator: SeededRandomNumberGenerator
        if let seed {
            generator = SeededRandomNumberGenerator(seed: seed)
        } else {
            generator = SeededRandomNumberGenerator(seed: UInt64(Date().timeIntervalSince1970 * 1000))
        }
        indices.shuffle(using: &generator)
        return indices
    }

    @discardableResult
    func recordResult(
        correctCount: Int,
        elapsedStudySeconds: Int,
        childId: String? = nil,
        completedAt: Date = Date()
    ) -> SessionResult {
        let clampedCorrect = min(max(0, correctCount), Self.itemCount)
        var record = loadRecord(childId: childId) ?? PersistedRecord(personalBestCount: 0, sessions: [])
        let isBest = clampedCorrect > record.personalBestCount
        if isBest {
            record.personalBestCount = clampedCorrect
        }
        let session = SessionResult(
            correctCount: clampedCorrect,
            itemCount: Self.itemCount,
            elapsedStudySeconds: max(0, elapsedStudySeconds),
            completedAt: completedAt,
            isPersonalBest: isBest
        )
        record.sessions.append(session)
        if record.sessions.count > 20 {
            record.sessions = Array(record.sessions.suffix(20))
        }
        persist(record, childId: childId)
        MasterLogger.shared.business(
            "MNEMO-B12 championship correct=\(clampedCorrect)/\(Self.itemCount) personalBest=\(record.personalBestCount) isNewBest=\(isBest)"
        )
        return session
    }

    private func storageKey(childId: String?) -> String {
        "\(storageKeyPrefix).\(resolvedChildScope(childId))"
    }

    private func resolvedChildScope(_ childId: String?) -> String {
        let trimmed = (childId ?? MnemonicBaselineAssessment.activeChildId())
            .trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty { return "default" }
        return trimmed
    }

    private func loadRecord(childId: String?) -> PersistedRecord? {
        let key = storageKey(childId: childId)
        guard let data = defaults.data(forKey: key),
              let record = try? JSONDecoder().decode(PersistedRecord.self, from: data) else {
            return nil
        }
        return record
    }

    private func persist(_ record: PersistedRecord, childId: String?) {
        let key = storageKey(childId: childId)
        guard let data = try? JSONEncoder().encode(record) else { return }
        defaults.set(data, forKey: key)
    }
}

/// Deterministic shuffle for championship sequences (tests + reproducible drills).
struct SeededRandomNumberGenerator: RandomNumberGenerator {
    private var state: UInt64

    init(seed: UInt64) {
        state = seed == 0 ? 0xDEAD_BEEF_CAFE_BABE : seed
    }

    mutating func next() -> UInt64 {
        state &+= 0x9E37_79B9_7F4A_7C15
        var z = state
        z = (z ^ (z >> 30)) &* 0xBF58_476D_1CE4_E5B9
        z = (z ^ (z >> 27)) &* 0x94D0_49BB_1331_11EB
        return z ^ (z >> 31)
    }
}
