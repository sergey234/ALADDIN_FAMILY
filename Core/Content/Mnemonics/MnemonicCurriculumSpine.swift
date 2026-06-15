import Foundation

/// Longitudinal Memory Academy course: 8 semesters (ages 4→22), unlock ≥70% prior semester.
final class MnemonicCurriculumSpine {
    static let shared = MnemonicCurriculumSpine()

    static let semesterCount = 8
    static let weeksPerSemester = 12
    static let unlockThreshold = 0.70

    struct Semester: Identifiable {
        let index: Int
        let titleKey: String
        let subtitleKey: String
        let primaryCategories: [String]
        let featuredTechniques: [MnemonicTechnique]
        let kpiSummaryKey: String

        var id: Int { index }
    }

    let semesters: [Semester] = [
        Semester(
            index: 0,
            titleKey: "child_mnemo_semester_0_title",
            subtitleKey: "child_mnemo_semester_0_subtitle",
            primaryCategories: [ChildCategoryKey.songs],
            featuredTechniques: [.rhymePeg, .linkChain, .rhythmCode],
            kpiSummaryKey: "child_mnemo_semester_0_kpi"
        ),
        Semester(
            index: 1,
            titleKey: "child_mnemo_semester_1_title",
            subtitleKey: "child_mnemo_semester_1_subtitle",
            primaryCategories: [ChildCategoryKey.songs, ChildCategoryKey.games],
            featuredTechniques: [.memoryPalace, .rhymePeg],
            kpiSummaryKey: "child_mnemo_semester_1_kpi"
        ),
        Semester(
            index: 2,
            titleKey: "child_mnemo_semester_2_title",
            subtitleKey: "child_mnemo_semester_2_subtitle",
            primaryCategories: [ChildCategoryKey.games, ChildCategoryKey.cartoons],
            featuredTechniques: [.memoryPalace, .storyLink, .keyword],
            kpiSummaryKey: "child_mnemo_semester_2_kpi"
        ),
        Semester(
            index: 3,
            titleKey: "child_mnemo_semester_3_title",
            subtitleKey: "child_mnemo_semester_3_subtitle",
            primaryCategories: [ChildCategoryKey.study],
            featuredTechniques: [.acronym, .chunking, .memoryPalace],
            kpiSummaryKey: "child_mnemo_semester_3_kpi"
        ),
        Semester(
            index: 4,
            titleKey: "child_mnemo_semester_4_title",
            subtitleKey: "child_mnemo_semester_4_subtitle",
            primaryCategories: [ChildCategoryKey.study],
            featuredTechniques: [.framePeg, .storyLink, .spacedReview],
            kpiSummaryKey: "child_mnemo_semester_4_kpi"
        ),
        Semester(
            index: 5,
            titleKey: "child_mnemo_semester_5_title",
            subtitleKey: "child_mnemo_semester_5_subtitle",
            primaryCategories: [ChildCategoryKey.music, ChildCategoryKey.video],
            featuredTechniques: [.rhythmCode, .framePeg],
            kpiSummaryKey: "child_mnemo_semester_5_kpi"
        ),
        Semester(
            index: 6,
            titleKey: "child_mnemo_semester_6_title",
            subtitleKey: "child_mnemo_semester_6_subtitle",
            primaryCategories: [ChildCategoryKey.movies, ChildCategoryKey.education],
            featuredTechniques: [.storyLink, .acronym, .memoryPalace],
            kpiSummaryKey: "child_mnemo_semester_6_kpi"
        ),
        Semester(
            index: 7,
            titleKey: "child_mnemo_semester_7_title",
            subtitleKey: "child_mnemo_semester_7_subtitle",
            primaryCategories: [
                ChildCategoryKey.education,
                ChildCategoryKey.study,
                ChildCategoryKey.games
            ],
            featuredTechniques: MnemonicTechnique.allCases,
            kpiSummaryKey: "child_mnemo_semester_7_kpi"
        )
    ]

    private let defaults: UserDefaults
    private let progressKey = "child.mnemo.spine.progress.v1"

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    func semester(at index: Int) -> Semester? {
        semesters.first { $0.index == index }
    }

    /// Mastery 0…1 for a semester (derived from recalls + SRS success in its categories).
    func masteryFraction(for semesterIndex: Int, childId: String? = nil, now: Date = Date()) -> Double {
        guard let semester = semester(at: semesterIndex) else { return 0 }
        let tracker = MnemonicSkillTracker.shared
        let base = Double(tracker.masteryPercent(childId: childId)) / 100.0
        let categoryDue = semester.primaryCategories.map {
            MnemonicSRSStore.shared.dueToday(category: $0, now: now)
        }.reduce(0, +)
        let categoryBoost = semester.primaryCategories.isEmpty
            ? 0
            : Double(max(0, 10 - categoryDue)) / 10.0 * 0.25
        let semesterWeight = 0.75 + Double(semesterIndex) * 0.03
        return min(1.0, max(0, (base * semesterWeight) + categoryBoost))
    }

    struct SemesterGate {
        let requiredSemesterIndex: Int
        let isAccessible: Bool
        /// Prior semester mastery 0…100 (for unlock hint).
        let priorMasteryPercent: Int
        let unlockThresholdPercent: Int

        var remainingPercent: Int {
            max(0, unlockThresholdPercent - priorMasteryPercent)
        }
    }

    #if DEBUG
    static var uiTestForceSemesterLocked: Bool {
        ProcessInfo.processInfo.arguments.contains("-UITestMnemoSemesterLocked")
    }
    #else
    static let uiTestForceSemesterLocked = false
    #endif

    /// All semester indices where `category` appears in `primaryCategories`.
    func semesterIndices(containing category: String) -> [Int] {
        semesters
            .filter { $0.primaryCategories.contains(category) }
            .map(\.index)
            .sorted()
    }

    /// Earliest semester that gates this category (multi-semester categories use the minimum index).
    func minimumSemesterIndex(for category: String) -> Int? {
        semesterIndices(containing: category).first
    }

    /// Item-level semester for study.* — intro 01–03 open without semester 3; 04–10 → sem 3; 11–20 → sem 4; 21+ → sem 7.
    func requiredSemesterIndex(forItemId itemId: String, category: String) -> Int {
        if category == ChildCategoryKey.study,
           itemId.hasPrefix("study."),
           let num = Int(itemId.replacingOccurrences(of: "study.", with: "")) {
            if num <= 3 { return 0 }
            if num <= 10 { return 3 }
            if num <= 20 { return 4 }
            return 7
        }
        return minimumSemesterIndex(for: category) ?? 0
    }

    func isUnlocked(_ semesterIndex: Int, childId: String? = nil, now: Date = Date()) -> Bool {
        guard semesterIndex >= 0, semesterIndex < Self.semesterCount else { return false }
        if semesterIndex == 0 { return true }
        if Self.uiTestForceSemesterLocked { return false }
        return masteryFraction(for: semesterIndex - 1, childId: childId, now: now) >= Self.unlockThreshold
    }

    func gate(for category: String, childId: String? = nil, now: Date = Date()) -> SemesterGate {
        let required = minimumSemesterIndex(for: category) ?? 0
        let accessible = isUnlocked(required, childId: childId, now: now)
        let priorPercent = required == 0
            ? 100
            : Int((masteryFraction(for: required - 1, childId: childId, now: now) * 100).rounded())
        return SemesterGate(
            requiredSemesterIndex: required,
            isAccessible: accessible,
            priorMasteryPercent: min(100, priorPercent),
            unlockThresholdPercent: Int(Self.unlockThreshold * 100)
        )
    }

    func itemGate(forItemId itemId: String, category: String, childId: String? = nil, now: Date = Date()) -> SemesterGate {
        let required = requiredSemesterIndex(forItemId: itemId, category: category)
        let accessible = isUnlocked(required, childId: childId, now: now)
        let priorPercent = required == 0
            ? 100
            : Int((masteryFraction(for: required - 1, childId: childId, now: now) * 100).rounded())
        return SemesterGate(
            requiredSemesterIndex: required,
            isAccessible: accessible,
            priorMasteryPercent: min(100, priorPercent),
            unlockThresholdPercent: Int(Self.unlockThreshold * 100)
        )
    }

    func activeSemesterIndex(childId: String? = nil, now: Date = Date()) -> Int {
        var highest = 0
        for index in 0..<Self.semesterCount where isUnlocked(index, childId: childId, now: now) {
            highest = index
        }
        return highest
    }

    /// Parent dashboard — progress toward unlocking the next semester (B14-T16).
    struct NextSemesterUnlockProgress {
        let activeSemesterIndex: Int
        let nextSemesterIndex: Int
        let gate: SemesterGate
        let allSemestersUnlocked: Bool
    }

    func nextSemesterUnlockProgress(childId: String? = nil, now: Date = Date()) -> NextSemesterUnlockProgress {
        let active = activeSemesterIndex(childId: childId, now: now)
        let next = active + 1
        guard next < Self.semesterCount else {
            return NextSemesterUnlockProgress(
                activeSemesterIndex: active,
                nextSemesterIndex: active,
                gate: SemesterGate(
                    requiredSemesterIndex: active,
                    isAccessible: true,
                    priorMasteryPercent: 100,
                    unlockThresholdPercent: Int(Self.unlockThreshold * 100)
                ),
                allSemestersUnlocked: true
            )
        }
        let priorPercent = Int((masteryFraction(for: active, childId: childId, now: now) * 100).rounded())
        return NextSemesterUnlockProgress(
            activeSemesterIndex: active,
            nextSemesterIndex: next,
            gate: SemesterGate(
                requiredSemesterIndex: next,
                isAccessible: isUnlocked(next, childId: childId, now: now),
                priorMasteryPercent: min(100, priorPercent),
                unlockThresholdPercent: Int(Self.unlockThreshold * 100)
            ),
            allSemestersUnlocked: false
        )
    }

    func currentWeek(in semesterIndex: Int) -> Int {
        let stored = defaults.integer(forKey: "\(progressKey).week.\(semesterIndex)")
        if stored > 0 { return min(stored, Self.weeksPerSemester) }
        return 1
    }

    func advanceWeek(in semesterIndex: Int) {
        let next = min(Self.weeksPerSemester, currentWeek(in: semesterIndex) + 1)
        defaults.set(next, forKey: "\(progressKey).week.\(semesterIndex)")
    }

    /// Progressive journey stop for non-study mnemo items (games/songs/…).
    func nextAvailableStop(for itemId: String, childId: String? = nil) -> Int {
        let semester = activeSemesterIndex(childId: childId)
        let week = currentWeek(in: semester)
        let cap = min(MnemonicJourneyPath.stopCount, 2 + semester * 2 + week / 3)
        if itemId.hasPrefix("games.") {
            if let num = Int(itemId.replacingOccurrences(of: "games.", with: "")) {
                return min(cap, max(1, num))
            }
        }
        if itemId.hasPrefix("songs.") {
            if let num = Int(itemId.replacingOccurrences(of: "songs.", with: "")) {
                return min(4, max(1, num))
            }
        }
        return min(cap, max(1, abs(itemId.hashValue) % cap + 1))
    }
}
