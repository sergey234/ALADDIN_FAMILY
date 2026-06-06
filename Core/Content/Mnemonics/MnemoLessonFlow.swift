import Foundation

/// Lesson flow helpers — WARMUP/REFLECT age gates + active age persistence (B14-T05/T06).
enum MnemoLessonFlow {
    static let activeAgeGroupStorageKey = "child.mnemo.active_age_group.v1"
    static let warmupDurationSeconds = 30

    static func persistActiveAgeGroup(_ ageGroup: ChildInterfaceScreen.AgeGroup) {
        UserDefaults.standard.set(ageGroup.mnemoStorageValue, forKey: activeAgeGroupStorageKey)
    }

    static func activeAgeGroup() -> ChildInterfaceScreen.AgeGroup {
        guard let raw = UserDefaults.standard.string(forKey: activeAgeGroupStorageKey) else {
            return .school
        }
        return ChildInterfaceScreen.AgeGroup.fromMnemoStorage(raw) ?? .school
    }

    static func supportsWarmup(for ageGroup: ChildInterfaceScreen.AgeGroup? = nil) -> Bool {
        switch ageGroup ?? activeAgeGroup() {
        case .kids:
            return false
        case .school, .teen, .youngAdult:
            return true
        }
    }

    /// Technique picker before lesson — teen + young adult only (B14-T07).
    static func supportsTechniquePicker(for ageGroup: ChildInterfaceScreen.AgeGroup? = nil) -> Bool {
        switch ageGroup ?? activeAgeGroup() {
        case .kids, .school:
            return false
        case .teen, .youngAdult:
            return true
        }
    }

    /// REFLECT metacognition — teen (13–17) and young adult (18–22) only (B14-T06).
    static func supportsReflect(for ageGroup: ChildInterfaceScreen.AgeGroup? = nil) -> Bool {
        switch ageGroup ?? activeAgeGroup() {
        case .kids, .school:
            return false
        case .teen, .youngAdult:
            return true
        }
    }

    static func initialLessonPhase() -> MnemoAcademyPhase {
        if supportsTechniquePicker() { return .techniquePick }
        return supportsWarmup() ? .warmup : .encode
    }

    static func lessonPhaseIndicators(for ageGroup: ChildInterfaceScreen.AgeGroup? = nil) -> [MnemoAcademyPhase] {
        let age = ageGroup ?? activeAgeGroup()
        var phases: [MnemoAcademyPhase] = []
        if supportsTechniquePicker(for: age) {
            phases.append(.techniquePick)
        }
        if supportsWarmup(for: age) {
            phases.append(.warmup)
        }
        phases.append(contentsOf: MnemoAcademyPhase.catalogPhases)
        if supportsReflect(for: age) {
            phases.append(.reflect)
        }
        return phases
    }
}

extension ChildInterfaceScreen.AgeGroup {
    var mnemoStorageValue: String {
        switch self {
        case .kids: return "kids"
        case .school: return "school"
        case .teen: return "teen"
        case .youngAdult: return "young_adult"
        }
    }

    static func fromMnemoStorage(_ raw: String) -> ChildInterfaceScreen.AgeGroup? {
        switch raw {
        case "kids": return .kids
        case "school": return .school
        case "teen": return .teen
        case "young_adult": return .youngAdult
        default: return nil
        }
    }
}
