import Foundation

/// Локальное состояние wellness-сессии (pillar + consent + offline check-in).
enum WellnessSessionStore {
    private static let consentKey = "wellness_consent_accepted_v1"
    private static let activePillarKey = "wellness_active_pillar"
    private static let exercisePillarKey = "wellness_exercise_pillar"
    private static let assessmentKindKey = "wellness_assessment_flow_kind"
    private static let checkinKey = "wellness_last_checkin_v1"
    private static let ageBandKey = "wellness_age_band_cache"
    private static let companionBannerKey = "wellness_companion_entry_banner_v1"
    private static let highlightMicKey = "wellness_companion_highlight_mic_v1"

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

    static var companionEntryBanner: String? {
        let v = UserDefaults.standard.string(forKey: companionBannerKey)?
            .trimmingCharacters(in: .whitespacesAndNewlines)
        return (v?.isEmpty == false) ? v : nil
    }

    static func setCompanionEntryBanner(_ text: String?) {
        if let text, !text.isEmpty {
            UserDefaults.standard.set(text, forKey: companionBannerKey)
        } else {
            UserDefaults.standard.removeObject(forKey: companionBannerKey)
        }
    }

    static func requestMicHighlight() {
        UserDefaults.standard.set(true, forKey: highlightMicKey)
    }

    static func consumeMicHighlight() -> Bool {
        let flag = UserDefaults.standard.bool(forKey: highlightMicKey)
        if flag {
            UserDefaults.standard.set(false, forKey: highlightMicKey)
        }
        return flag
    }
}

/// r100-2-06 — App Group keys shared with `ALADDINWidgets/SharedDataManager`.
enum WellnessWidgetBridge {
    private static let appGroupId = "group.com.aladdin.family"
    private static let titleKey = "wellness_widget_title"
    private static let tapKey = "wellness_widget_tap"
    private static let moodKey = "wellness_last_mood"

    static func syncFromCheckin(moodId: String, localizationManager: LocalizationManager) {
        guard let defaults = UserDefaults(suiteName: appGroupId) else { return }
        defaults.set(localizationManager.localized(WellnessWidgetL10n.titleKey), forKey: titleKey)
        defaults.set(localizationManager.localized(WellnessWidgetL10n.tapKey), forKey: tapKey)
        defaults.set(moodEmoji(moodId), forKey: moodKey)
        defaults.set(Date(), forKey: "last_update")
    }

    private static func moodEmoji(_ moodId: String) -> String {
        switch moodId {
        case "great": return "😊"
        case "sad": return "😢"
        case "anxious": return "😰"
        case "tired": return "😴"
        default: return "🙂"
        }
    }
}
