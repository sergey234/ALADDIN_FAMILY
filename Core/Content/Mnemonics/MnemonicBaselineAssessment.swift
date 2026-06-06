import Foundation

/// AMAkids-style baseline: memorize 5 words within 2 minutes, then ordered recall (B12-T01).
final class MnemonicBaselineAssessment {
    static let shared = MnemonicBaselineAssessment()

    static let wordCount = 5
    static let timeLimitSeconds = 120
    static let baselineSemesterIndex = 1
    static let baselineWeekThreshold = 10
    static let retestIntervalDays = 90

    enum OfferKind: Equatable {
        case initialBaseline
        case quarterlyRetest
    }

    static let wordLocalizationKeys: [String] = (1...wordCount).map {
        "child_mnemo_baseline_word_\($0)"
    }

    struct SessionResult: Codable, Equatable {
        let correctCount: Int
        let wordCount: Int
        let rawScorePercent: Int
        let memoryQuotient: Int
        let elapsedStudySeconds: Int
        let completedAt: Date

        enum CodingKeys: String, CodingKey {
            case correctCount
            case wordCount
            case rawScorePercent
            case memoryQuotient
            case elapsedStudySeconds
            case completedAt
        }

        init(
            correctCount: Int,
            wordCount: Int,
            rawScorePercent: Int,
            memoryQuotient: Int,
            elapsedStudySeconds: Int,
            completedAt: Date
        ) {
            self.correctCount = correctCount
            self.wordCount = wordCount
            self.rawScorePercent = rawScorePercent
            self.memoryQuotient = memoryQuotient
            self.elapsedStudySeconds = elapsedStudySeconds
            self.completedAt = completedAt
        }

        init(from decoder: Decoder) throws {
            let container = try decoder.container(keyedBy: CodingKeys.self)
            correctCount = try container.decode(Int.self, forKey: .correctCount)
            wordCount = try container.decode(Int.self, forKey: .wordCount)
            rawScorePercent = try container.decode(Int.self, forKey: .rawScorePercent)
            elapsedStudySeconds = try container.decode(Int.self, forKey: .elapsedStudySeconds)
            completedAt = try container.decode(Date.self, forKey: .completedAt)
            if let storedMQ = try container.decodeIfPresent(Int.self, forKey: .memoryQuotient) {
                memoryQuotient = storedMQ
            } else {
                memoryQuotient = MnemonicBaselineAssessment.memoryQuotient(
                    correctCount: correctCount,
                    elapsedStudySeconds: elapsedStudySeconds,
                    wordCount: wordCount
                )
            }
        }

        func encode(to encoder: Encoder) throws {
            var container = encoder.container(keyedBy: CodingKeys.self)
            try container.encode(correctCount, forKey: .correctCount)
            try container.encode(wordCount, forKey: .wordCount)
            try container.encode(rawScorePercent, forKey: .rawScorePercent)
            try container.encode(memoryQuotient, forKey: .memoryQuotient)
            try container.encode(elapsedStudySeconds, forKey: .elapsedStudySeconds)
            try container.encode(completedAt, forKey: .completedAt)
        }
    }

    private struct PersistedRecord: Codable, Equatable {
        var sessions: [SessionResult]
        var latestMemoryQuotient: Int?
    }

    private let defaults: UserDefaults
    private let storageKeyPrefix = "child.mnemo.baseline.v1"
    private let latestMQKeyPrefix = "child.mnemo.mq.latest.v1"

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    #if DEBUG
    static var uiTestForceOffer: Bool {
        ProcessInfo.processInfo.arguments.contains("-UITestMnemoBaseline")
    }

    static var uiTestForceRetestOffer: Bool {
        ProcessInfo.processInfo.arguments.contains("-UITestMnemoBaselineRetest")
    }
    #else
    static let uiTestForceOffer = false
    static let uiTestForceRetestOffer = false
    #endif

    func shouldOffer(childId: String? = nil, now: Date = Date()) -> Bool {
        offerKind(childId: childId, now: now) != nil
    }

    func offerKind(childId: String? = nil, now: Date = Date()) -> OfferKind? {
        if Self.uiTestForceOffer {
            return latestResult(childId: childId) == nil ? .initialBaseline : .quarterlyRetest
        }
        if Self.uiTestForceRetestOffer, latestResult(childId: childId) != nil {
            return .quarterlyRetest
        }
        if latestResult(childId: childId) == nil {
            return meetsInitialSpineGate(childId: childId, now: now) ? .initialBaseline : nil
        }
        return isQuarterlyRetestDue(childId: childId, now: now) ? .quarterlyRetest : nil
    }

    func daysUntilRetest(childId: String? = nil, now: Date = Date()) -> Int? {
        guard let last = latestResult(childId: childId) else { return nil }
        let elapsed = Self.calendarDays(from: last.completedAt, to: now)
        return max(0, Self.retestIntervalDays - elapsed)
    }

    func nextRetestDate(childId: String? = nil, now: Date = Date()) -> Date? {
        guard let last = latestResult(childId: childId) else { return nil }
        let calendar = Calendar.current
        let intervalReady = calendar.date(byAdding: .day, value: Self.retestIntervalDays, to: last.completedAt) ?? last.completedAt
        if hasSession(inCalendarQuarterOf: now, childId: childId) {
            guard let nextQuarterStart = startOfNextCalendarQuarter(from: now) else { return intervalReady }
            return max(intervalReady, nextQuarterStart)
        }
        return intervalReady
    }

    func isQuarterlyRetestDue(childId: String? = nil, now: Date = Date()) -> Bool {
        guard let last = latestResult(childId: childId) else { return false }
        let elapsed = Self.calendarDays(from: last.completedAt, to: now)
        guard elapsed >= Self.retestIntervalDays else { return false }
        return !hasSession(inCalendarQuarterOf: now, childId: childId)
    }

    func hasSession(inCalendarQuarterOf date: Date, childId: String? = nil) -> Bool {
        let calendar = Calendar.current
        let year = calendar.component(.year, from: date)
        let quarter = calendar.component(.quarter, from: date)
        return allResults(childId: childId).contains { session in
            calendar.component(.year, from: session.completedAt) == year
                && calendar.component(.quarter, from: session.completedAt) == quarter
        }
    }

    private func meetsInitialSpineGate(childId: String? = nil, now: Date = Date()) -> Bool {
        let spine = MnemonicCurriculumSpine.shared
        let active = spine.activeSemesterIndex(childId: childId, now: now)
        guard active >= Self.baselineSemesterIndex else { return false }
        let week = spine.currentWeek(in: Self.baselineSemesterIndex)
        return week >= Self.baselineWeekThreshold
    }

    private static func calendarDays(from start: Date, to end: Date) -> Int {
        let calendar = Calendar.current
        let startDay = calendar.startOfDay(for: start)
        let endDay = calendar.startOfDay(for: end)
        return calendar.dateComponents([.day], from: startDay, to: endDay).day ?? 0
    }

    private func startOfNextCalendarQuarter(from date: Date) -> Date? {
        let calendar = Calendar.current
        let year = calendar.component(.year, from: date)
        let quarter = calendar.component(.quarter, from: date)
        let nextQuarter = quarter == 4 ? 1 : quarter + 1
        let nextYear = quarter == 4 ? year + 1 : year
        let month = (nextQuarter - 1) * 3 + 1
        var components = DateComponents(year: nextYear, month: month, day: 1)
        return calendar.date(from: components)
    }

    func latestResult(childId: String? = nil) -> SessionResult? {
        loadRecord(childId: childId).sessions.last
    }

    func allResults(childId: String? = nil) -> [SessionResult] {
        loadRecord(childId: childId).sessions
    }

    /// Parent trend point — MQ + quarter label only (no words / no PII).
    struct MQTrendPoint: Identifiable, Equatable {
        let index: Int
        let memoryQuotient: Int
        let quarterLabel: String

        var id: Int { index }
    }

    func trendPoints(childId: String? = nil, calendar: Calendar = .current) -> [MQTrendPoint] {
        allResults(childId: childId).enumerated().map { index, session in
            MQTrendPoint(
                index: index,
                memoryQuotient: session.memoryQuotient,
                quarterLabel: Self.quarterLabel(for: session.completedAt, calendar: calendar)
            )
        }
    }

    func memoryQuotientDelta(childId: String? = nil) -> Int? {
        let sessions = allResults(childId: childId)
        guard sessions.count >= 2 else { return nil }
        return sessions[sessions.count - 1].memoryQuotient - sessions[sessions.count - 2].memoryQuotient
    }

    static func quarterLabel(for date: Date, calendar: Calendar = .current) -> String {
        let year = calendar.component(.year, from: date) % 100
        let quarter = calendar.component(.quarter, from: date)
        return String(format: "Q%d '%02d", quarter, year)
    }

    /// Latest Memory Quotient (0–100) for parent trend hooks (B12-T04).
    func latestMemoryQuotient(childId: String? = nil) -> Int? {
        let record = loadRecord(childId: childId)
        if let cached = record.latestMemoryQuotient {
            return cached
        }
        if let sessionMQ = latestResult(childId: childId)?.memoryQuotient {
            return sessionMQ
        }
        let quickKey = latestMQKey(childId: childId)
        guard defaults.object(forKey: quickKey) != nil else { return nil }
        return defaults.integer(forKey: quickKey)
    }

    /// MQ v1 — игровой индекс: 85% точность recall + до 15 бонус за скорость изучения.
    static func memoryQuotient(
        correctCount: Int,
        elapsedStudySeconds: Int,
        wordCount: Int = MnemonicBaselineAssessment.wordCount
    ) -> Int {
        guard wordCount > 0 else { return 0 }
        let clamped = min(max(0, correctCount), wordCount)
        let raw = Int((Double(clamped) / Double(wordCount) * 100).rounded())
        guard raw > 0 else { return 0 }
        let elapsed = min(max(0, elapsedStudySeconds), timeLimitSeconds)
        let speedBonus = Int(
            (Double(timeLimitSeconds - elapsed) / Double(timeLimitSeconds) * 15).rounded()
        )
        return min(100, max(0, raw + speedBonus))
    }

    func rawScorePercent(correctCount: Int, wordCount: Int = MnemonicBaselineAssessment.wordCount) -> Int {
        guard wordCount > 0 else { return 0 }
        let clamped = min(max(0, correctCount), wordCount)
        return Int((Double(clamped) / Double(wordCount) * 100).rounded())
    }

    @discardableResult
    func recordResult(
        correctCount: Int,
        elapsedStudySeconds: Int,
        childId: String? = nil,
        completedAt: Date = Date()
    ) -> SessionResult {
        let clampedCorrect = min(max(0, correctCount), Self.wordCount)
        let clampedElapsed = max(0, elapsedStudySeconds)
        let raw = rawScorePercent(correctCount: clampedCorrect)
        let mq = Self.memoryQuotient(
            correctCount: clampedCorrect,
            elapsedStudySeconds: clampedElapsed
        )
        let result = SessionResult(
            correctCount: clampedCorrect,
            wordCount: Self.wordCount,
            rawScorePercent: raw,
            memoryQuotient: mq,
            elapsedStudySeconds: clampedElapsed,
            completedAt: completedAt
        )
        var record = loadRecord(childId: childId)
        record.sessions.append(result)
        record.latestMemoryQuotient = mq
        persist(record, childId: childId)
        persistLatestMQ(mq, childId: childId)
        MasterLogger.shared.business(
            "MNEMO-B12 baseline recorded correct=\(result.correctCount)/\(result.wordCount) raw=\(result.rawScorePercent)% mq=\(result.memoryQuotient)"
        )
        return result
    }

    // MARK: - Persistence

    private func storageKey(childId: String?) -> String {
        let scope = resolvedChildScope(childId)
        return "\(storageKeyPrefix).\(scope)"
    }

    private func resolvedChildScope(_ childId: String?) -> String {
        let trimmed = (childId ?? Self.activeChildId()).trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty { return "default" }
        return trimmed
    }

    static func activeChildId() -> String {
        MnemonicPictogramStore.activeChildId()
    }

    private func loadRecord(childId: String?) -> PersistedRecord {
        let key = storageKey(childId: childId)
        guard let data = defaults.data(forKey: key),
              let record = try? JSONDecoder().decode(PersistedRecord.self, from: data) else {
            return PersistedRecord(sessions: [], latestMemoryQuotient: nil)
        }
        return record
    }

    private func persist(_ record: PersistedRecord, childId: String?) {
        let key = storageKey(childId: childId)
        guard let data = try? JSONEncoder().encode(record) else { return }
        defaults.set(data, forKey: key)
    }

    private func latestMQKey(childId: String?) -> String {
        "\(latestMQKeyPrefix).\(resolvedChildScope(childId))"
    }

    private func persistLatestMQ(_ mq: Int, childId: String?) {
        defaults.set(min(100, max(0, mq)), forKey: latestMQKey(childId: childId))
    }
}
