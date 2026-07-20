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
    private static let pendingExerciseIdKey = "wellness_pending_exercise_id_v1"
    private static let openSleepStoriesKey = "wellness_open_sleep_stories_v1"
    private static let windDownEnabledKey = "wellness_wind_down_enabled_v1"
    private static let windDownBedtimeHourKey = "wellness_wind_down_hour_v1"
    private static let windDownBedtimeMinuteKey = "wellness_wind_down_minute_v1"

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

    // MARK: - P0.3 check-in streak (local, for Unicorn XP)

    private static let checkinDaysKey = "wellness_checkin_day_stamps_v1"
    private static let checkinStreakKey = "wellness_checkin_streak_v1"

    static func checkinStreakDays(defaults: UserDefaults = .standard) -> Int {
        defaults.integer(forKey: checkinStreakKey)
    }

    /// Records today once; returns current consecutive-day streak.
    @discardableResult
    static func recordCheckinDayAndStreak(defaults: UserDefaults = .standard, now: Date = Date()) -> Int {
        let formatter = DateFormatter()
        formatter.calendar = Calendar.current
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone.current
        formatter.dateFormat = "yyyy-MM-dd"
        let today = formatter.string(from: now)

        var days = defaults.stringArray(forKey: checkinDaysKey) ?? []
        if days.contains(today) {
            return defaults.integer(forKey: checkinStreakKey)
        }
        days.append(today)
        if days.count > 60 {
            days = Array(days.suffix(60))
        }
        defaults.set(days, forKey: checkinDaysKey)

        let cal = Calendar.current
        var streak = 1
        var cursor = cal.date(byAdding: .day, value: -1, to: now) ?? now
        while days.contains(formatter.string(from: cursor)) {
            streak += 1
            guard let prev = cal.date(byAdding: .day, value: -1, to: cursor) else { break }
            cursor = prev
        }
        defaults.set(streak, forKey: checkinStreakKey)
        return streak
    }

    /// Aggregate-only flag for parent share (teen/child privacy). Raw mood feed is never shown to parent UI.
    static var parentShareAggregatePreferred: Bool {
        get { UserDefaults.standard.object(forKey: "wellness_parent_share_aggregate_v1") as? Bool ?? true }
        set { UserDefaults.standard.set(newValue, forKey: "wellness_parent_share_aggregate_v1") }
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

    static var pendingExerciseId: String? {
        let v = UserDefaults.standard.string(forKey: pendingExerciseIdKey)?
            .trimmingCharacters(in: .whitespacesAndNewlines)
        return (v?.isEmpty == false) ? v : nil
    }

    static func setPendingExerciseId(_ id: String?) {
        if let id, !id.isEmpty {
            UserDefaults.standard.set(id, forKey: pendingExerciseIdKey)
        } else {
            UserDefaults.standard.removeObject(forKey: pendingExerciseIdKey)
        }
    }

    static func consumePendingExerciseId() -> String? {
        let id = pendingExerciseId
        setPendingExerciseId(nil)
        return id
    }

    static var shouldOpenSleepStories: Bool {
        UserDefaults.standard.bool(forKey: openSleepStoriesKey)
    }

    static func setOpenSleepStoriesOnAppear(_ enabled: Bool) {
        UserDefaults.standard.set(enabled, forKey: openSleepStoriesKey)
    }

    static func consumeOpenSleepStories() -> Bool {
        let flag = shouldOpenSleepStories
        if flag { setOpenSleepStoriesOnAppear(false) }
        return flag
    }

    static var windDownEnabled: Bool {
        UserDefaults.standard.bool(forKey: windDownEnabledKey)
    }

    static func setWindDownEnabled(_ enabled: Bool) {
        UserDefaults.standard.set(enabled, forKey: windDownEnabledKey)
    }

    static var windDownBedtime: (hour: Int, minute: Int) {
        let hour = UserDefaults.standard.object(forKey: windDownBedtimeHourKey) as? Int ?? 22
        let minute = UserDefaults.standard.object(forKey: windDownBedtimeMinuteKey) as? Int ?? 30
        return (max(0, min(23, hour)), max(0, min(59, minute)))
    }

    static func setWindDownBedtime(hour: Int, minute: Int) {
        UserDefaults.standard.set(max(0, min(23, hour)), forKey: windDownBedtimeHourKey)
        UserDefaults.standard.set(max(0, min(59, minute)), forKey: windDownBedtimeMinuteKey)
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
