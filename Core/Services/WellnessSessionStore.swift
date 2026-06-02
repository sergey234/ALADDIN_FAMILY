import Foundation

/// Локальное состояние wellness-сессии (pillar + consent + offline check-in).
enum WellnessSessionStore {
    private static let consentKey = "wellness_consent_accepted_v1"
    private static let activePillarKey = "wellness_active_pillar"
    private static let exercisePillarKey = "wellness_exercise_pillar"
    private static let assessmentKindKey = "wellness_assessment_flow_kind"
    private static let checkinKey = "wellness_last_checkin_v1"
    private static let ageBandKey = "wellness_age_band_cache"

    static var cachedAgeBand: String? {
        UserDefaults.standard.string(forKey: ageBandKey)
    }

    static func setCachedAgeBand(_ band: String?) {
        if let band, !band.isEmpty {
            UserDefaults.standard.set(band, forKey: ageBandKey)
        } else {
            UserDefaults.standard.removeObject(forKey: ageBandKey)
        }
    }

    static var hasAcceptedConsent: Bool {
        UserDefaults.standard.bool(forKey: consentKey)
    }

    static func acceptConsent() {
        UserDefaults.standard.set(true, forKey: consentKey)
    }

    static var activePillar: String? {
        let v = UserDefaults.standard.string(forKey: activePillarKey)?
            .trimmingCharacters(in: .whitespacesAndNewlines)
        return (v?.isEmpty == false) ? v : nil
    }

    static func setActivePillar(_ pillar: String?) {
        if let pillar, !pillar.isEmpty {
            UserDefaults.standard.set(pillar, forKey: activePillarKey)
        } else {
            UserDefaults.standard.removeObject(forKey: activePillarKey)
        }
    }

    /// Столп для экрана упражнений (Phase 2).
    static var exercisePillar: String? {
        let v = UserDefaults.standard.string(forKey: exercisePillarKey)?
            .trimmingCharacters(in: .whitespacesAndNewlines)
        return (v?.isEmpty == false) ? v : activePillar
    }

    static func setExercisePillar(_ pillar: String?) {
        if let pillar, !pillar.isEmpty {
            UserDefaults.standard.set(pillar, forKey: exercisePillarKey)
        } else {
            UserDefaults.standard.removeObject(forKey: exercisePillarKey)
        }
    }

    static var assessmentFlowKind: String {
        UserDefaults.standard.string(forKey: assessmentKindKey) ?? "phqLite"
    }

    static func setAssessmentFlowKind(_ kind: WellnessAssessmentFlowScreen.Kind) {
        UserDefaults.standard.set(kind.rawValue, forKey: assessmentKindKey)
    }

    static func saveCheckin(_ draft: WellnessCheckinDraft) {
        let enc = JSONEncoder()
        enc.dateEncodingStrategy = .iso8601
        if let data = try? enc.encode(draft) {
            UserDefaults.standard.set(data, forKey: checkinKey)
        }
    }

    static func loadCheckin() -> WellnessCheckinDraft? {
        guard let data = UserDefaults.standard.data(forKey: checkinKey) else { return nil }
        let dec = JSONDecoder()
        dec.dateDecodingStrategy = .iso8601
        return try? dec.decode(WellnessCheckinDraft.self, from: data)
    }
}
